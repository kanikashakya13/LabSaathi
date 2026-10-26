"""Windows Native WinRT Optical Character Recognition (Windows.Media.Ocr) Bridge for LabSaathi.

Provides local, zero-dependency OCR on Windows 10/11 when Tesseract is not installed,
extracting word-level bounding boxes and reconstructing horizontal table rows accurately.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
import cv2
import numpy as np

POWERSHELL_OCR_SCRIPT_TEMPLATE = r"""
$ErrorActionPreference = "Stop"
$imgPath = "__IMAGE_PATH__"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]

function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($imgPath)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if ($null -eq $engine) {
    $lang = New-Object Windows.Globalization.Language("en-US")
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
}
$result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])

$words = @()
foreach ($line in $result.Lines) {
    foreach ($w in $line.Words) {
        $words += [PSCustomObject]@{
            t = $w.Text
            x = [math]::Round($w.BoundingRect.X, 1)
            y = [math]::Round($w.BoundingRect.Y, 1)
            w = [math]::Round($w.BoundingRect.Width, 1)
            h = [math]::Round($w.BoundingRect.Height, 1)
        }
    }
}
$stream.Dispose()
ConvertTo-Json -InputObject @($words) -Compress
"""


def group_words_into_table_rows(
    words: list[dict],
    y_tolerance_factor: float = 0.65,
) -> list[tuple[str, float]]:
    """Group OCR words with (x, y, w, h) coordinates into horizontal table rows.

    Preserves multi-column separation by inserting '   ' (3 spaces) when the horizontal
    gap between consecutive words exceeds 1.8x average character height, and ' ' (1 space)
    within phrases like 'Hemoglobin (Hb)' or '12.0 - 15.5'.
    """
    if not words:
        return []

    # Sort primarily by vertical center, then horizontal X
    enriched = []
    for item in words:
        txt = str(item.get("t", "")).strip()
        if not txt:
            continue
        x = float(item.get("x", 0.0))
        y = float(item.get("y", 0.0))
        w = float(item.get("w", 10.0))
        h = float(item.get("h", 14.0))
        y_center = y + h * 0.5
        enriched.append({"t": txt, "x": x, "y": y, "w": w, "h": h, "yc": y_center, "conf": float(item.get("conf", 0.92))})

    if not enriched:
        return []

    enriched.sort(key=lambda w: (w["yc"], w["x"]))

    rows: list[list[dict]] = []
    for word in enriched:
        placed = False
        for row in rows:
            # Compare against median y_center and median height of current row
            avg_yc = sum(r["yc"] for r in row) / len(row)
            avg_h = max(10.0, sum(r["h"] for r in row) / len(row))
            if abs(word["yc"] - avg_yc) <= max(10.0, avg_h * y_tolerance_factor):
                row.append(word)
                placed = True
                break
        if not placed:
            rows.append([word])

    # Sort rows top-to-bottom
    rows.sort(key=lambda r: sum(w["yc"] for w in r) / len(r))

    lines_out: list[tuple[str, float]] = []
    for row in rows:
        row.sort(key=lambda w: w["x"])
        avg_h = max(12.0, sum(w["h"] for w in row) / len(row))
        parts: list[str] = []
        prev_right: float | None = None
        for w in row:
            if prev_right is not None:
                gap = w["x"] - prev_right
                if gap > max(18.0, avg_h * 1.35):
                    parts.append("   ")
                else:
                    parts.append(" ")
            parts.append(w["t"])
            prev_right = w["x"] + w["w"]

        line_str = "".join(parts).strip()
        avg_conf = sum(w["conf"] for w in row) / len(row)
        if line_str:
            lines_out.append((line_str, round(avg_conf, 3)))

    return lines_out


def run_windows_native_ocr(img_gray_or_bgr: np.ndarray) -> list[tuple[str, float]]:
    """Run Windows native WinRT OcrEngine on an OpenCV image array and return reconstructed lines."""
    if os.name != "nt":
        return []

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="labsaathi_ocr_") as tmp:
            tmp_path = tmp.name

        cv2.imwrite(tmp_path, img_gray_or_bgr)
        ps_code = POWERSHELL_OCR_SCRIPT_TEMPLATE.replace("__IMAGE_PATH__", tmp_path)
        encoded = base64.b64encode(ps_code.encode("utf-16le")).decode("ascii")

        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return []

        raw_out = proc.stdout.strip()
        parsed = json.loads(raw_out)
        if isinstance(parsed, dict):
            parsed = [parsed]
        if not isinstance(parsed, list):
            return []

        return group_words_into_table_rows(parsed)
    except Exception:
        return []
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
