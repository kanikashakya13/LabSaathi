"""Deterministic Rule-Based Result Classification Engine for LabSaathi.

IMPORTANT: This module uses strictly deterministic Python logic to compare verified
laboratory results against laboratory-provided reference ranges. The AI explanation
engine is NEVER permitted to compute, modify, or override these statuses.
"""

from __future__ import annotations

import re
from backend.schemas import (
    ClassifiedParameter,
    ClassificationStatus,
    ExtractedParameter,
)

# Canonical unit equivalence map (harmless typographical synonyms)
UNIT_SYNONYMS: dict[str, str] = {
    "g/dl": "g/dl",
    "gm/dl": "g/dl",
    "gm%": "g/dl",
    "g%": "g/dl",
    "g/l": "g/l",
    "gm/l": "g/l",
    "mg/dl": "mg/dl",
    "mg%": "mg/dl",
    "mg/l": "mg/l",
    "ug/dl": "ug/dl",
    "µg/dl": "ug/dl",
    "mcg/dl": "ug/dl",
    "mmol/l": "mmol/l",
    "umol/l": "umol/l",
    "µmol/l": "umol/l",
    "mcmol/l": "umol/l",
    "uiu/ml": "uiu/ml",
    "µiu/ml": "uiu/ml",
    "miu/l": "uiu/ml",
    "miu/ml": "uiu/ml",
    "ng/ml": "ng/ml",
    "ug/l": "ng/ml",
    "µg/l": "ng/ml",
    "mcg/l": "ng/ml",
    "pg/ml": "pg/ml",
    "ng/l": "pg/ml",
    "ng/dl": "ng/dl",
    "u/l": "u/l",
    "iu/l": "u/l",
    "meq/l": "meq/l",
    "%": "%",
    "fl": "fl",
    "pg": "pg",
    "mm/hr": "mm/hr",
    "mm/1sthr": "mm/hr",
    "10^3/ul": "10^3/ul",
    "10^3/µl": "10^3/ul",
    "10^3/mcl": "10^3/ul",
    "x10^3/ul": "10^3/ul",
    "thou/ul": "10^3/ul",
    "10^9/l": "10^3/ul",
    "lakhs/cumm": "lakhs/cumm",
    "lakh/cumm": "lakhs/cumm",
    "lakhs/ul": "lakhs/cumm",
    "cells/cumm": "cells/cumm",
    "/cumm": "cells/cumm",
    "cells/ul": "cells/cumm",
    "cells/mcl": "cells/cumm",
    "/mm3": "cells/cumm",
    "10^6/ul": "10^6/ul",
    "10^6/µl": "10^6/ul",
    "10^12/l": "10^6/ul",
    "mill/cumm": "10^6/ul",
    "million/cumm": "10^6/ul",
    "ml/min/1.73m2": "ml/min/1.73m2",
}

# Validated exact metric / SI scaling conversions: (from_canonical_unit, to_canonical_unit) -> multiplier
VALIDATED_UNIT_CONVERSIONS: dict[tuple[str, str], float] = {
    ("g/l", "g/dl"): 0.1,
    ("g/dl", "g/l"): 10.0,
    ("mg/l", "mg/dl"): 0.1,
    ("mg/dl", "mg/l"): 10.0,
    ("ng/ml", "ng/dl"): 100.0,
    ("ng/dl", "ng/ml"): 0.01,
    ("lakhs/cumm", "10^3/ul"): 100.0,
    ("10^3/ul", "lakhs/cumm"): 0.01,
    ("lakhs/cumm", "cells/cumm"): 100000.0,
    ("cells/cumm", "lakhs/cumm"): 0.00001,
    ("cells/cumm", "10^3/ul"): 0.001,
    ("10^3/ul", "cells/cumm"): 1000.0,
}

QUALITATIVE_NORMALS = {
    "negative",
    "non-reactive",
    "non reactive",
    "nonreactive",
    "absent",
    "nil",
    "normal",
    "clear",
    "not detected",
    "none seen",
}

CRITICAL_KEYWORDS = (
    "critical",
    "panic",
    "urgent alert",
    "alert value",
    "life threatening",
)


def normalize_unit(unit_str: str) -> str:
    """Normalize unit string for compatibility checking."""
    cleaned = (unit_str or "").strip().lower().replace(" ", "")
    return UNIT_SYNONYMS.get(cleaned, cleaned)


def extract_unit_from_range(range_str: str) -> str:
    """Check if the reference range string explicitly embeds a trailing measurement unit."""
    cleaned = (range_str or "").strip()
    match = re.search(
        r"(?:\d+(?:\.\d+)?)\s*(10\^\d+\/[uµ]l|10\^\d+\/l|lakhs\/cumm|lakh\/cumm|cells\/cumm|\/cumm|mg\/dl|mmol\/l|g\/dl|gm\/dl|g\/l|mg\/l|umol\/l|µmol\/l|ng\/ml|pg\/ml|ng\/dl|uiu\/ml|µiu\/ml|miu\/l|meq\/l|u\/l|iu\/l)\s*$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1)
    return ""


def has_demographic_subrange(range_str: str) -> tuple[bool, bool]:
    """Return (has_sex_subrange, has_age_subrange) if the printed range is stratified by sex or age."""
    text = (range_str or "").strip()
    has_sex = bool(
        re.search(r"\b(?:male|men|m)\s*[:\-]", text, flags=re.IGNORECASE)
        and re.search(r"\b(?:female|women|f)\s*[:\-]", text, flags=re.IGNORECASE)
    )
    has_age = bool(
        re.search(r"\b(?:adult|adults)\s*[:\-]", text, flags=re.IGNORECASE)
        and re.search(r"\b(?:child|children|pediatric|newborn|infant)\s*[:\-]", text, flags=re.IGNORECASE)
    )
    return has_sex, has_age


def _select_demographic_subrange(
    range_str: str,
    patient_sex: str = "unspecified",
    patient_age_group: str = "unspecified",
) -> tuple[str | None, list[str], str]:
    """Parse sex-specific or age-specific subranges if present in the laboratory reference range."""
    text = (range_str or "").strip()
    sex = (patient_sex or "unspecified").lower()
    age = (patient_age_group or "unspecified").lower()

    male_match = re.search(
        r"\b(?:male|men|m)\s*[:\-]?\s*([<>≤≥=]?\s*\d+(?:\.\d+)?(?:\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?)?)",
        text,
        flags=re.IGNORECASE,
    )
    female_match = re.search(
        r"\b(?:female|women|f)\s*[:\-]?\s*([<>≤≥=]?\s*\d+(?:\.\d+)?(?:\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?)?)",
        text,
        flags=re.IGNORECASE,
    )
    if male_match and female_match:
        m_range = male_match.group(1).strip()
        f_range = female_match.group(1).strip()
        if sex == "male":
            return m_range, [m_range, f_range], "Classified using Male laboratory reference range."
        if sex == "female":
            return f_range, [m_range, f_range], "Classified using Female laboratory reference range."
        return (
            None,
            [m_range, f_range],
            "Reference range is sex-specific (Male vs Female) and biological sex was not specified on the report.",
        )

    adult_match = re.search(
        r"\b(?:adult|adults)\s*[:\-]?\s*([<>≤≥=]?\s*\d+(?:\.\d+)?(?:\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?)?)",
        text,
        flags=re.IGNORECASE,
    )
    child_match = re.search(
        r"\b(?:child|children|pediatric)\s*[:\-]?\s*([<>≤≥=]?\s*\d+(?:\.\d+)?(?:\s*(?:-|–|—|to)\s*\d+(?:\.\d+)?)?)",
        text,
        flags=re.IGNORECASE,
    )
    if adult_match and child_match:
        a_range = adult_match.group(1).strip()
        c_range = child_match.group(1).strip()
        if age in ("adult", "senior"):
            return a_range, [a_range, c_range], "Classified using Adult laboratory reference range."
        if age == "child":
            return c_range, [a_range, c_range], "Classified using Child laboratory reference range."
        return (
            None,
            [a_range, c_range],
            "Reference range is age-specific (Adult vs Child) and patient age was not specified on the report.",
        )

    return text, [], ""


def _parse_single_range(
    range_str: str,
) -> dict[str, float | bool | str | None]:
    """Parse a single reference range expression into structured bounds."""
    s = (range_str or "").strip().replace(",", "")
    if not s or s.lower() in ("-", "n/a", "na", "none", "unable to verify", "not provided"):
        return {"kind": "empty"}

    # 1. Interval: low - high (handles '4-6', '12.0 - 15.5', '70 – 99', '150 to 410')
    interval_match = re.search(
        r"^\s*([+-]?\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*([+-]?\d+(?:\.\d+)?)",
        s,
        flags=re.IGNORECASE,
    )
    if interval_match:
        low = float(interval_match.group(1))
        high = float(interval_match.group(2))
        if low <= high:
            return {
                "kind": "interval",
                "low": low,
                "high": high,
                "low_inclusive": True,
                "high_inclusive": True,
            }

    # 2. Upper bound inclusive: <=, ≤, Up to
    upper_inc_match = re.search(
        r"^\s*(?:<=|≤|up\s+to|less\s+than\s+or\s+equal\s+to)\s*([+-]?\d+(?:\.\d+)?)",
        s,
        flags=re.IGNORECASE,
    )
    if upper_inc_match:
        return {
            "kind": "upper",
            "low": None,
            "high": float(upper_inc_match.group(1)),
            "high_inclusive": True,
        }

    # 3. Upper bound exclusive: <, Less than, Below
    upper_exc_match = re.search(
        r"^\s*(?:<|less\s+than|below)\s*([+-]?\d+(?:\.\d+)?)",
        s,
        flags=re.IGNORECASE,
    )
    if upper_exc_match:
        return {
            "kind": "upper",
            "low": None,
            "high": float(upper_exc_match.group(1)),
            "high_inclusive": False,
        }

    # 4. Lower bound inclusive: >=, ≥
    lower_inc_match = re.search(
        r"^\s*(?:>=|≥|at\s+least|greater\s+than\s+or\s+equal\s+to)\s*([+-]?\d+(?:\.\d+)?)",
        s,
        flags=re.IGNORECASE,
    )
    if lower_inc_match:
        return {
            "kind": "lower",
            "low": float(lower_inc_match.group(1)),
            "high": None,
            "low_inclusive": True,
        }

    # 5. Lower bound exclusive: >, Greater than, Above
    lower_exc_match = re.search(
        r"^\s*(?:>|greater\s+than|above)\s*([+-]?\d+(?:\.\d+)?)",
        s,
        flags=re.IGNORECASE,
    )
    if lower_exc_match:
        return {
            "kind": "lower",
            "low": float(lower_exc_match.group(1)),
            "high": None,
            "low_inclusive": False,
        }

    return {"kind": "unparsed", "raw": s}


def _parse_result_value(result_str: str) -> dict[str, float | str | None]:
    """Parse original result string into plain number, inequality, or qualitative text."""
    s = (result_str or "").strip().replace(",", "")
    if not s or s.lower() in ("-", "n/a", "unable to verify"):
        return {"kind": "empty"}

    num_match = re.match(r"^([+-]?\d+(?:\.\d+)?)$", s)
    if num_match:
        return {"kind": "numeric", "value": float(num_match.group(1))}

    ineq_match = re.match(r"^(<=|>=|≤|≥|<|>)\s*([+-]?\d+(?:\.\d+)?)$", s)
    if ineq_match:
        op = ineq_match.group(1).replace("≤", "<=").replace("≥", ">=")
        return {"kind": "inequality", "operator": op, "value": float(ineq_match.group(2))}

    return {"kind": "qualitative", "raw": s}


def _compare_value_to_parsed_range(
    res_parsed: dict,
    rng_parsed: dict,
) -> tuple[ClassificationStatus, str]:
    """Deterministically compare parsed result against parsed single range."""
    rng_kind = rng_parsed.get("kind")
    res_kind = res_parsed.get("kind")

    if rng_kind == "empty" or res_kind == "empty":
        return (
            "Unable to Classify",
            "Essential value or laboratory reference range is missing.",
        )

    if res_kind == "qualitative" or rng_kind == "unparsed":
        res_raw = str(res_parsed.get("raw", "")).strip().lower()
        rng_raw = str(rng_parsed.get("raw", "")).strip().lower()
        if res_raw and rng_raw and res_raw == rng_raw:
            return (
                "Within Reference Range",
                f"Qualitative result ('{res_parsed.get('raw')}') matches laboratory reference ('{rng_parsed.get('raw')}').",
            )
        if res_raw in QUALITATIVE_NORMALS and rng_raw in QUALITATIVE_NORMALS:
            return (
                "Within Reference Range",
                "Qualitative result is within standard negative/non-reactive reference expectation.",
            )
        return (
            "Unable to Classify",
            "Result or reference range is qualitative/non-numeric and cannot be assigned a numeric high/low status.",
        )

    if res_kind == "numeric":
        val = float(res_parsed["value"])
        if rng_kind == "interval":
            low = float(rng_parsed["low"])
            high = float(rng_parsed["high"])
            if val < low:
                return (
                    "Below Reference Range",
                    f"Reported value ({val:g}) is below the laboratory lower limit ({low:g}).",
                )
            if val > high:
                return (
                    "Above Reference Range",
                    f"Reported value ({val:g}) is above the laboratory upper limit ({high:g}).",
                )
            return (
                "Within Reference Range",
                f"Reported value ({val:g}) is within the laboratory reference range ({low:g} – {high:g}).",
            )

        if rng_kind == "upper":
            high = float(rng_parsed["high"])
            inc = bool(rng_parsed.get("high_inclusive", True))
            if (val <= high) if inc else (val < high):
                op_sym = "≤" if inc else "<"
                return (
                    "Within Reference Range",
                    f"Reported value ({val:g}) satisfies the laboratory reference threshold ({op_sym} {high:g}).",
                )
            op_sym = "≤" if inc else "<"
            return (
                "Above Reference Range",
                f"Reported value ({val:g}) exceeds the laboratory reference threshold ({op_sym} {high:g}).",
            )

        if rng_kind == "lower":
            low = float(rng_parsed["low"])
            inc = bool(rng_parsed.get("low_inclusive", True))
            if (val >= low) if inc else (val > low):
                op_sym = "≥" if inc else ">"
                return (
                    "Within Reference Range",
                    f"Reported value ({val:g}) satisfies the laboratory reference threshold ({op_sym} {low:g}).",
                )
            op_sym = "≥" if inc else ">"
            return (
                "Below Reference Range",
                f"Reported value ({val:g}) is below the laboratory reference threshold ({op_sym} {low:g}).",
            )

    if res_kind == "inequality":
        op = str(res_parsed["operator"])
        val = float(res_parsed["value"])

        if op in ("<", "<="):
            if rng_kind == "interval":
                low = float(rng_parsed["low"])
                high = float(rng_parsed["high"])
                if val <= low and low > 0:
                    return (
                        "Below Reference Range",
                        f"Inequality result ({op} {val:g}) is strictly below the reference lower limit ({low:g}).",
                    )
                if low == 0.0 and val <= high:
                    return (
                        "Within Reference Range",
                        f"Inequality result ({op} {val:g}) falls within the reference interval (0 – {high:g}).",
                    )
            elif rng_kind == "upper":
                high = float(rng_parsed["high"])
                if val <= high:
                    return (
                        "Within Reference Range",
                        f"Inequality result ({op} {val:g}) is within the upper reference limit ({high:g}).",
                    )
            return (
                "Unable to Classify",
                f"Inequality result ({op} {val:g}) spans multiple possible range outcomes and cannot be deterministically classified.",
            )

        if op in (">", ">="):
            if rng_kind == "interval":
                high = float(rng_parsed["high"])
                if val >= high:
                    return (
                        "Above Reference Range",
                        f"Inequality result ({op} {val:g}) exceeds the reference upper limit ({high:g}).",
                    )
            elif rng_kind == "lower":
                low = float(rng_parsed["low"])
                if val >= low:
                    return (
                        "Within Reference Range",
                        f"Inequality result ({op} {val:g}) satisfies the lower reference limit ({low:g}).",
                    )
            elif rng_kind == "upper":
                high = float(rng_parsed["high"])
                if val >= high:
                    return (
                        "Above Reference Range",
                        f"Inequality result ({op} {val:g}) exceeds the upper reference limit ({high:g}).",
                    )
            return (
                "Unable to Classify",
                f"Inequality result ({op} {val:g}) is ambiguous relative to the reference range.",
            )

    return ("Unable to Classify", "Result format could not be deterministically classified.")


def classify_parameter(
    param: ExtractedParameter,
    patient_sex: str = "unspecified",
    patient_age_group: str = "unspecified",
) -> ClassifiedParameter:
    """Deterministically classify a single extracted & verified laboratory parameter."""
    res_str = (param.original_result or "").strip()
    unit_str = (param.unit or "").strip()
    rng_str = (param.reference_range or "").strip()
    interp_str = (param.lab_interpretation or "").strip()

    is_critical = any(
        kw in interp_str.lower() or kw in res_str.lower()
        for kw in CRITICAL_KEYWORDS
    )

    if param.verification_status == "Unable to verify" or not res_str:
        return ClassifiedParameter(
            id=param.id,
            test_name=param.test_name,
            original_result=res_str or "Unable to verify",
            unit=unit_str,
            reference_range=rng_str or "Not provided",
            lab_interpretation=interp_str,
            rule_based_status="Unable to Classify",
            classification_reason="Result value could not be verified from the report.",
            original_extracted_result=param.original_extracted_result or res_str,
            user_edited=param.user_edited,
            is_critical_alert=is_critical,
            page_number=param.page_number,
        )

    if not rng_str or rng_str.lower() in ("-", "n/a", "na", "none", "unable to verify", "not provided"):
        return ClassifiedParameter(
            id=param.id,
            test_name=param.test_name,
            original_result=res_str,
            unit=unit_str,
            reference_range="Not provided on report",
            lab_interpretation=interp_str,
            rule_based_status="Unable to Classify",
            classification_reason=(
                "No laboratory reference range was provided for this test. "
                "LabSaathi does not invent reference ranges because ranges vary across laboratories."
            ),
            original_extracted_result=param.original_extracted_result or res_str,
            user_edited=param.user_edited,
            is_critical_alert=is_critical,
            page_number=param.page_number,
        )

    res_parsed = _parse_result_value(res_str)
    conversion_note = ""

    # Check for unit compatibility or validated SI scaling conversion when range embeds a unit
    range_unit = extract_unit_from_range(rng_str)
    if range_unit and unit_str:
        norm_res_unit = normalize_unit(unit_str)
        norm_rng_unit = normalize_unit(range_unit)
        if norm_res_unit and norm_rng_unit and norm_res_unit != norm_rng_unit:
            conv_factor = VALIDATED_UNIT_CONVERSIONS.get((norm_res_unit, norm_rng_unit))
            if conv_factor is not None and res_parsed.get("kind") == "numeric":
                converted_val = round(float(res_parsed["value"]) * conv_factor, 4)
                res_parsed = {"kind": "numeric", "value": converted_val}
                conversion_note = (
                    f"Converted {res_str} {unit_str} to {converted_val:g} {range_unit} "
                    f"using validated SI scaling factor ({conv_factor:g})."
                )
            else:
                return ClassifiedParameter(
                    id=param.id,
                    test_name=param.test_name,
                    original_result=res_str,
                    unit=unit_str,
                    reference_range=rng_str,
                    lab_interpretation=interp_str,
                    rule_based_status="Unable to Classify",
                    classification_reason=(
                        f"Unit mismatch detected between reported value unit ('{unit_str}') "
                        f"and reference range unit ('{range_unit}'). Incompatible units are not compared without a validated conversion."
                    ),
                    original_extracted_result=param.original_extracted_result or res_str,
                    user_edited=param.user_edited,
                    is_critical_alert=is_critical,
                    page_number=param.page_number,
                )

    selected_rng, candidate_rngs, demo_note = _select_demographic_subrange(
        rng_str, patient_sex=patient_sex, patient_age_group=patient_age_group
    )
    numeric_val = float(res_parsed["value"]) if res_parsed.get("kind") == "numeric" else None

    if selected_rng is None and candidate_rngs:
        outcomes = [
            _compare_value_to_parsed_range(res_parsed, _parse_single_range(c_rng))[0]
            for c_rng in candidate_rngs
        ]
        if len(set(outcomes)) == 1 and outcomes[0] != "Unable to Classify":
            status = outcomes[0]
            reason = f"Result is {status.lower()} across all listed demographic sub-ranges ({rng_str})."
            if conversion_note:
                reason = f"{reason} {conversion_note}"
            return ClassifiedParameter(
                id=param.id,
                test_name=param.test_name,
                original_result=res_str,
                unit=unit_str,
                reference_range=rng_str,
                lab_interpretation=interp_str,
                rule_based_status=status,
                classification_reason=reason,
                parsed_numeric_value=numeric_val,
                original_extracted_result=param.original_extracted_result or res_str,
                user_edited=param.user_edited,
                is_critical_alert=is_critical,
                page_number=param.page_number,
            )
        return ClassifiedParameter(
            id=param.id,
            test_name=param.test_name,
            original_result=res_str,
            unit=unit_str,
            reference_range=rng_str,
            lab_interpretation=interp_str,
            rule_based_status="Unable to Classify",
            classification_reason=demo_note,
            parsed_numeric_value=numeric_val,
            original_extracted_result=param.original_extracted_result or res_str,
            user_edited=param.user_edited,
            is_critical_alert=is_critical,
            page_number=param.page_number,
        )

    rng_parsed = _parse_single_range(selected_rng or rng_str)
    status, reason = _compare_value_to_parsed_range(res_parsed, rng_parsed)
    if demo_note:
        reason = f"{reason} ({demo_note})"
    if conversion_note:
        reason = f"{reason} {conversion_note}"

    return ClassifiedParameter(
        id=param.id,
        test_name=param.test_name,
        original_result=res_str,
        unit=unit_str,
        reference_range=rng_str,
        lab_interpretation=interp_str,
        rule_based_status=status,
        classification_reason=reason,
        parsed_numeric_value=numeric_val,
        parsed_range_low=rng_parsed.get("low") if isinstance(rng_parsed.get("low"), float) else None,
        parsed_range_high=rng_parsed.get("high") if isinstance(rng_parsed.get("high"), float) else None,
        original_extracted_result=param.original_extracted_result or res_str,
        user_edited=param.user_edited,
        is_critical_alert=is_critical,
        page_number=param.page_number,
    )
