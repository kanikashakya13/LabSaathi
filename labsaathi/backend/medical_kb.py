"""Curated Educational Medical Reference Knowledge Base (English & Hinglish) for LabSaathi.

Provides vetted, non-diagnostic educational explanations, non-clinical factors affecting test
values, and neutral doctor discussion prompts. Used both to ground LLM explanations and as a
reliable, transparent fallback when external AI credentials (GEMINI_API_KEY) are not configured.
"""

from __future__ import annotations

from typing import Any
from backend.schemas import ClassifiedParameter, ParameterExplanationCard


CURATED_TESTS: dict[str, dict[str, Any]] = {
    "hemoglobin": {
        "aliases": ["hemoglobin", "haemoglobin", "hb", "hgb", "hemoglobin (hb)"],
        "what_en": (
            "Hemoglobin is an iron-rich protein inside red blood cells that carries oxygen "
            "from your lungs to tissues and organs throughout your body."
        ),
        "what_hi": (
            "Hemoglobin aapke red blood cells (laal rakt koshikaon) mein paaya jaane wala ek "
            "iron-rich protein hai, jo lungs se poore sharir ke angon tak oxygen pahunchata hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your reported hemoglobin value is within the laboratory's reference range. "
                    "While this generally indicates typical oxygen-carrying protein levels at the time of testing, "
                    "a single value cannot rule out nutritional deficiencies (such as early iron or vitamin changes) "
                    "without considering your symptoms and full blood count."
                ),
                "hi": (
                    "Aapka hemoglobin level lab ki di gayi reference range ke andar hai. Yeh aam taur par "
                    "normal oxygen-carrying capacity darshata hai, lekin sirf ek test se shuruati iron ya "
                    "vitamin ki kami ka poora pata nahi chalta — doctor aapke baaki CBC values ke saath ise dekhenge."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your reported hemoglobin value is below the laboratory's reference range. Lower hemoglobin "
                    "can be seen with nutritional factors, recent blood loss, increased fluid volume, or chronic "
                    "health conditions, but this number alone cannot identify the underlying reason."
                ),
                "hi": (
                    "Aapka hemoglobin lab ki reference range se kam hai. Kam hemoglobin khan-pan mein poshan ki kami, "
                    "hydration level, ya anya kaaranon se ho sakta hai, par sirf is number se asli wajah tay nahi hoti. "
                    "Kripya bina doctor ki salah ke koi iron ya dawa shuru na karein."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your reported hemoglobin value is above the laboratory's reference range. Higher values can "
                    "occur with dehydration (concentrated blood), living at high altitude, smoking, or other "
                    "physiological factors. It does not by itself confirm a medical condition."
                ),
                "hi": (
                    "Aapka hemoglobin lab ki reference range se upar hai. Pani kam peene (dehydration), "
                    "oonchai wale ilake mein rehne, ya smoking jaise kaaranon se bhi value badh sakti hai. "
                    "Iska sahi matlab samajhne ke liye doctor se charcha karein."
                ),
            },
            "Unable to Classify": {
                "en": (
                    "Hemoglobin measures oxygen-carrying protein in red blood cells, but this specific value "
                    "could not be automatically classified against a single reference range (for example, due to "
                    "missing demographic range details or missing lab limits)."
                ),
                "hi": (
                    "Hemoglobin sharir mein oxygen le jaane wala protein hai, lekin reference range ya "
                    "demographic jankari adhuri hone ke kaaran is value ko automatically classify nahi kiya ja saka."
                ),
            },
        },
        "factors_en": [
            "Hydration status (dehydration can temporarily concentrate hemoglobin; high fluid intake can dilute it)",
            "Age, biological sex, and pregnancy status",
            "Living at higher altitude where oxygen levels are lower",
            "Recent nutritional intake or recent blood donation/loss",
        ],
        "factors_hi": [
            "Sharir mein pani ki matra (dehydration se value thodi zyada aur zyada taral se kam dikh sakti hai)",
            "Umra (age), biological sex, aur pregnancy ki sthiti",
            "Pahadi ya oonchai wale ilake mein rehna",
            "Haal hi mein blood donation ya poshan (diet) mein badlaav",
        ],
        "question_en": "How should I interpret this hemoglobin level alongside my red blood cell indices (MCV, MCH) and daily energy levels?",
        "question_hi": "Meri baaki CBC report (jaise MCV, MCH) aur meri sehat ke hisaab se is hemoglobin value ka kya matlab hai?",
        "source": "MedlinePlus (U.S. National Library of Medicine) — Hemoglobin Test Educational Overview",
    },
    "wbc": {
        "aliases": [
            "wbc count",
            "total wbc",
            "total leucocyte count",
            "tlc",
            "white blood cell count",
            "leukocytes",
            "wbc",
        ],
        "what_en": (
            "White Blood Cells (WBCs / Leukocytes) are part of your body's immune system. They help "
            "respond to infections, inflammation, and tissue stress."
        ),
        "what_hi": (
            "White Blood Cells (WBC / Safed Rakt Koshikayein) aapke immune system ka hissa hain, "
            "jo sharir ko infection aur sujan (inflammation) se ladne mein madad karte hain."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your total white blood cell count is within the laboratory's reference range. "
                    "While reassuring, doctors also look at individual WBC types (differential count) "
                    "and how you feel physically."
                ),
                "hi": (
                    "Aapka total WBC count lab ki reference range ke andar hai. Yeh ek achha sanket hai, "
                    "halanki doctor zaroorat padne par alag-alag WBC types (differential count) aur aapke lakshano ko bhi dekhte hain."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your WBC count is below the laboratory's reference range. Temporary dips can happen "
                    "after viral illnesses, with certain medications, or due to nutritional factors. "
                    "A low number by itself does not pinpoint a specific condition."
                ),
                "hi": (
                    "Aapka WBC count lab ki reference range se kam hai. Kai baar viral infection ke baad, "
                    "kuch dawaiyon ke asar se, ya vitamin ki kami se WBC aasthaayi roop se kam ho sakta hai."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your WBC count is above the laboratory's reference range. Elevated counts commonly "
                    "reflect a normal immune response to a minor infection, inflammation, physical stress, "
                    "or recent exercise, and do not automatically indicate a serious illness."
                ),
                "hi": (
                    "Aapka WBC count reference range se upar hai. Aam taur par halka infection, sujan, "
                    "physical stress, ya kasrat ke baad sharir ki immune pratikriya ke kaaran WBC badh sakta hai."
                ),
            },
            "Unable to Classify": {
                "en": (
                    "WBC count measures immune cells in the blood, but this value could not be automatically "
                    "classified against the provided reference range."
                ),
                "hi": (
                    "WBC count khoon mein immune cells ki sankhya batata hai, par di gayi reference range "
                    "se iska automatic classification nahi ho saka."
                ),
            },
        },
        "factors_en": [
            "Recent viral or bacterial infections or recovery from a cold",
            "Intense physical exercise, emotional stress, or lack of sleep before blood draw",
            "Certain prescription medications (such as corticosteroids)",
            "Time of day when the blood sample was collected",
        ],
        "factors_hi": [
            "Haal hi mein hua sardi-zukham, viral infection, ya halka bukhar",
            "Test se pehle bhari kasrat (exercise) ya mental stress",
            "Kuch dawaiyan (jaise steroids ya painkillers)",
            "Sample dene ka samay aur pregnancy ki sthiti",
        ],
        "question_en": "Could a recent minor illness, stress, or medication explain my white blood cell count, and should we check the differential count?",
        "question_hi": "Kya haal ki kisi tabiyat kharabi, stress, ya dawa ki wajah se mera WBC count aisa hai, aur kya mujhe dubara test karana chahiye?",
        "source": "MedlinePlus (U.S. National Library of Medicine) — White Blood Count (WBC)",
    },
    "platelets": {
        "aliases": ["platelet count", "platelets", "plt", "thrombocyte count"],
        "what_en": (
            "Platelets (thrombocytes) are tiny cell fragments in your blood that stick together "
            "to help form clots and stop bleeding when a blood vessel is injured."
        ),
        "what_hi": (
            "Platelets khoon mein maujood chhote cell hisse hote hain jo chot lagne par khoon "
            "jamane (clotting) aur bleeding rokne mein madad karte hain."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your platelet count falls within the laboratory's reference range, suggesting a typical "
                    "number of clotting cells in the sample tested."
                ),
                "hi": (
                    "Aapka platelet count lab ki reference range ke andar hai, jo khoon mein platelets ki "
                    "aam sankhya darshata hai."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your platelet count is below the laboratory's reference range. Platelets can temporarily "
                    "drop during or after viral fevers, due to certain medicines, or sometimes appear falsely "
                    "low if platelets clump together in the collection tube."
                ),
                "hi": (
                    "Aapka platelet count reference range se kam hai. Viral bukhar ke dauran ya baad mein, "
                    "kuch dawaiyon se, ya kabhi-kabhi test tube mein platelets chipak jaane (clumping) se bhi "
                    "machine mein count kam dikh sakta hai."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your platelet count is above the laboratory's reference range. Mild elevations often "
                    "happen as a reactive response to inflammation, infection, or iron deficiency."
                ),
                "hi": (
                    "Aapka platelet count reference range se upar hai. Sharir mein sujan, halka infection, "
                    "ya iron ki kami hone par aksar reactive taur par platelets badh jaate hain."
                ),
            },
            "Unable to Classify": {
                "en": (
                    "Platelets help blood clot properly, but this result could not be automatically "
                    "compared against a verified numeric reference range."
                ),
                "hi": (
                    "Platelets khoon ke thakke banane mein madad karte hain, lekin is value ko di gayi "
                    "range ke saath automatically classify nahi kiya ja saka."
                ),
            },
        },
        "factors_en": [
            "Recent viral fever or seasonal infection",
            "Platelet clumping in the EDTA blood tube (which can cause a falsely low machine reading)",
            "Iron levels and general inflammatory state",
            "High altitude or strenuous physical exertion before sampling",
        ],
        "factors_hi": [
            "Haal hi mein hua viral bukhar ya infection",
            "Blood sample tube mein platelets ka aapas mein judna (platelet clumping)",
            "Sharir mein iron ka level ya halka inflammation",
            "Sample lene se pehle bhari sharirik mehnat",
        ],
        "question_en": "Is this platelet level clinically meaningful for me, or could it be related to a recent viral illness or sample clumping?",
        "question_hi": "Kya yeh platelet count mere liye dhyan dene yogya hai, ya yeh haal ke bukhar ya sample clumping ki wajah se ho sakta hai?",
        "source": "Testing.com / AACC Lab Tests Online — Platelet Count Educational Guide",
    },
    "fasting_glucose": {
        "aliases": [
            "fasting blood glucose",
            "fasting blood sugar",
            "fbs",
            "glucose fasting",
            "glucose (fasting)",
            "blood glucose fasting",
            "plasma glucose fasting",
        ],
        "what_en": (
            "Fasting Blood Glucose measures the amount of sugar (glucose) circulating in your blood "
            "after an overnight fast (typically 8 to 12 hours without food or caloric drinks)."
        ),
        "what_hi": (
            "Fasting Blood Glucose (FBS) raat bhar (8 se 12 ghante) bina khaye-piye rehne ke baad "
            "aapke khoon mein maujood sugar (glucose) ki matra ko maapta hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your fasting blood glucose is within the laboratory's reference range. However, a single "
                    "fasting reading only captures a one-moment snapshot and does not reflect long-term average "
                    "blood sugar (which is typically evaluated using tests like HbA1c)."
                ),
                "hi": (
                    "Aapka fasting blood sugar lab ki reference range ke andar hai. Dhyan rahe ki yeh sirf "
                    "sample dete waqt ka level batata hai; pichhle kuch mahino ka aam level janne ke liye doctor HbA1c jaise test dekhte hain."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your fasting blood glucose is below the laboratory's reference range. Prolonged fasting "
                    "beyond 12–14 hours, delayed sample processing, or blood-sugar-lowering medications can "
                    "contribute to lower readings."
                ),
                "hi": (
                    "Aapka fasting sugar reference range se kam hai. Bahut lambe samay tak bhookhe rehna, "
                    "zyada kasrat, ya sugar ki dawaiyon ke asar se value kam aa sakti hai."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your fasting blood glucose is above the laboratory's reference range. While elevated fasting "
                    "glucose warrants discussion with your doctor, a single reading cannot diagnose a condition "
                    "on its own — incomplete fasting, stress, poor sleep, or recent illness can also raise blood sugar temporarily."
                ),
                "hi": (
                    "Aapka fasting blood sugar lab ki reference range se upar hai. Ek baar sugar upar aane "
                    "ka matlab seedhe bimari ki pushti nahi hai — poori tarah 8-10 ghante fasting na hona, "
                    "tanaav (stress), neend ki kami, ya dawaiyon se bhi sugar badh sakta hai."
                ),
            },
            "Unable to Classify": {
                "en": (
                    "Fasting blood glucose measures blood sugar after fasting, but this result could not be "
                    "automatically classified due to missing or incompatible reference range details."
                ),
                "hi": (
                    "Fasting blood glucose khali pet khoon mein sugar maapta hai, par reference range ya unit "
                    "match na hone ke kaaran ise classify nahi kiya ja saka."
                ),
            },
        },
        "factors_en": [
            "Duration of fasting (having tea, coffee with milk/sugar, or late snacks within 8 hours affects results)",
            "Acute stress, poor sleep the night before, or recent fever/infection",
            "Medications such as steroids, diuretics, or cold decongestants",
            "Time elapsed between blood collection and laboratory separation",
        ],
        "factors_hi": [
            "Fasting ka sahi samay (test se 8-10 ghante pehle chai, doodh, ya nashta lene se value badal jaati hai)",
            "Raat ko neend poori na hona, mental stress, ya bukhar",
            "Kuch dawaiyan jaise steroids ya khansi-zukham ke syrup",
            "Test se pehle ki gayi sharirik gatividhi",
        ],
        "question_en": "Given how long I fasted before this test, should we repeat the fasting glucose or compare it with an HbA1c test?",
        "question_hi": "Mere fasting ke samay aur is report ko dekhte hue, kya mujhe yeh test dubara karana chahiye ya HbA1c ke saath milakar dekhna chahiye?",
        "source": "MedlinePlus (NLM) & American Diabetes Association — Blood Glucose Testing Education",
    },
    "hba1c": {
        "aliases": [
            "hba1c",
            "glycated hemoglobin",
            "glycosylated hemoglobin",
            "hemoglobin a1c",
            "hb a1c",
        ],
        "what_en": (
            "HbA1c (Glycated Hemoglobin) estimates your average blood sugar levels over the past "
            "2 to 3 months by measuring the percentage of hemoglobin coated with sugar."
        ),
        "what_hi": (
            "HbA1c test pichhle 2 se 3 mahino mein aapke khoon mein rahe average blood sugar level "
            "ka andaza deta hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your HbA1c is within the laboratory's reference interval, reflecting typical average "
                    "blood glucose attachment over the lifespan of red blood cells."
                ),
                "hi": (
                    "Aapka HbA1c lab ki reference range ke andar hai, jo pichhle 2-3 mahino mein aam "
                    "average blood sugar darshata hai."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your HbA1c is below the laboratory's reference interval. Factors that shorten red blood "
                    "cell lifespan or alter hemoglobin turnover can sometimes cause lower HbA1c readings."
                ),
                "hi": (
                    "Aapka HbA1c lab ki reference range se kam hai. Red blood cells ki umra ya hemoglobin "
                    "mein badlaav ke kaaran bhi HbA1c kam dikh sakta hai."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your HbA1c is above the laboratory's reference interval, indicating that average blood "
                    "sugar over recent months has been higher than the reference baseline. Your doctor will "
                    "interpret this alongside fasting glucose, hemoglobin levels, and your health history."
                ),
                "hi": (
                    "Aapka HbA1c lab ki reference range se upar hai, jiska matlab hai ki pichhle kuch mahino "
                    "mein average blood sugar aam range se zyada raha hai. Doctor aapki fasting report aur "
                    "health history ke saath iska sahi matlab samjhayenge."
                ),
            },
            "Unable to Classify": {
                "en": (
                    "HbA1c reflects 2–3 month average blood glucose, but this value could not be automatically "
                    "classified against a single numeric interval."
                ),
                "hi": (
                    "HbA1c 2-3 mahine ka average sugar batata hai, lekin di gayi range ke hisaab se "
                    "automatic classification nahi ho paya."
                ),
            },
        },
        "factors_en": [
            "Iron deficiency, vitamin B12 deficiency, or anemia (which can alter red blood cell turnover and skew HbA1c)",
            "Hemoglobin variants (such as thalassemia trait)",
            "Recent blood loss, transfusion, or pregnancy",
        ],
        "factors_hi": [
            "Sharir mein iron ya Vitamin B12 ki kami / anemia (isse HbA1c ki reading par asar pad sakta hai)",
            "Hemoglobin variants ya thalassemia trait",
            "Pregnancy ya haal hi mein hua blood loss",
        ],
        "question_en": "How does this HbA1c result align with my fasting blood sugar, and could my hemoglobin level affect the HbA1c reading?",
        "question_hi": "Mera HbA1c aur fasting sugar aapas mein kaise mel khaate hain, aur kya mere hemoglobin level ka HbA1c par koi asar pad sakta hai?",
        "source": "National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK) — A1C Test Guide",
    },
    "cholesterol": {
        "aliases": [
            "total cholesterol",
            "cholesterol total",
            "serum cholesterol",
            "cholesterol",
        ],
        "what_en": (
            "Total Cholesterol measures the combined amount of cholesterol (including HDL, LDL, and VLDL) "
            "circulating in your blood. Cholesterol is a waxy fat-like substance used to build cells and hormones."
        ),
        "what_hi": (
            "Total Cholesterol aapke khoon mein maujood kul cholesterol (HDL, LDL aur VLDL milakar) "
            "ki matra maapta hai. Sharir ko cells aur hormones banane ke liye thode cholesterol ki zaroorat hoti hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your total cholesterol is within the laboratory's reference threshold. Because total "
                    "cholesterol combines both 'protective' HDL and LDL particles, doctors usually review "
                    "the full lipid breakdown rather than total cholesterol alone."
                ),
                "hi": (
                    "Aapka total cholesterol lab ki reference limit ke andar hai. Kyunki ismein HDL aur LDL "
                    "dono shamil hote hain, isliye doctor poori lipid profile ko ek saath dekhte hain."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your total cholesterol is below the laboratory's lower reference limit. Your doctor "
                    "can evaluate this in the context of your overall nutrition and health."
                ),
                "hi": (
                    "Aapka total cholesterol di gayi reference range se kam hai. Doctor aapke khan-pan "
                    "aur sehat ke hisaab se iski samiksha karenge."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your total cholesterol is above the laboratory's reference threshold. A single lipid "
                    "value is not a disease diagnosis; clinicians consider age, HDL/LDL ratios, diet, "
                    "thyroid function, and overall cardiovascular profile."
                ),
                "hi": (
                    "Aapka total cholesterol lab ki reference threshold se upar hai. Sirf total cholesterol "
                    "badhne se koi bimari tay nahi hoti — doctor HDL, LDL, triglycerides, khan-pan aur lifestyle ke saath ise dekhte hain."
                ),
            },
            "Unable to Classify": {
                "en": (
                    "Total cholesterol measures blood lipids, but this value could not be automatically classified."
                ),
                "hi": (
                    "Total cholesterol khoon mein lipids ki matra batata hai, par is value ko automatically classify nahi kiya ja saka."
                ),
            },
        },
        "factors_en": [
            "Recent dietary fat intake and whether the sample was fasting or non-fasting",
            "Thyroid hormone levels (underactive thyroid can raise cholesterol)",
            "Recent weight changes, pregnancy, or acute illness",
        ],
        "factors_hi": [
            "Haal ke dino ka khan-pan aur test khali pet (fasting) hua ya nahi",
            "Thyroid hormone ka level (thyroid kam kaam karne par bhi cholesterol badh sakta hai)",
            "Vajan mein badlaav ya sharirik gatividhi",
        ],
        "question_en": "How should I look at my total cholesterol in relation to my HDL, LDL, and triglyceride numbers?",
        "question_hi": "Mere HDL, LDL aur triglycerides ke mukable is total cholesterol value ko kaise samjha jaana chahiye?",
        "source": "MedlinePlus (NLM) — Cholesterol Levels: What You Need to Know",
    },
    "triglycerides": {
        "aliases": ["triglycerides", "serum triglycerides", "tg", "triglyceride"],
        "what_en": (
            "Triglycerides are the most common type of fat in the body, storing unused calories "
            "from food to provide energy between meals."
        ),
        "what_hi": (
            "Triglycerides khoon mein paaya jaane wala ek prakar ka fat (charbi) hai. Khane se milne "
            "wali extra calories ko sharir triglycerides ke roop mein jama karta hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your triglyceride value is within the laboratory's reference threshold."
                ),
                "hi": (
                    "Aapka triglyceride level lab ki reference range ke andar hai."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your triglyceride value is below the laboratory's lower reference boundary."
                ),
                "hi": (
                    "Aapka triglyceride level reference range ki nichli seema se kam hai."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your triglyceride value is above the laboratory's reference threshold. Triglycerides "
                    "are especially sensitive to recent meals, sugary drinks, and fasting duration."
                ),
                "hi": (
                    "Aapka triglyceride level reference limit se upar hai. Triglycerides par pichhle 10-12 "
                    "ghante ke khane, meethi cheezon, aur fasting ke samay ka bahut jaldi asar padta hai."
                ),
            },
            "Unable to Classify": {
                "en": "Triglycerides measure blood fats, but this result could not be automatically classified.",
                "hi": "Triglycerides khoon mein fat ki matra batate hain, par is value ko classify nahi kiya ja saka.",
            },
        },
        "factors_en": [
            "Eating or drinking anything other than water within 10–12 hours before the test",
            "High-carbohydrate meals or alcohol intake in the days preceding the test",
            "Blood sugar control and thyroid function",
        ],
        "factors_hi": [
            "Test se 10-12 ghante pehle kuch khana ya chai/meetha peena (non-fasting sample)",
            "Test se ek-do din pehle tel-masale, meetha, ya alcohol ka sevan",
            "Blood sugar aur thyroid ka balance",
        ],
        "question_en": "Could my fasting duration or recent diet explain this triglyceride level, and what lifestyle steps are helpful?",
        "question_hi": "Kya mere khan-pan ya fasting ke samay ka is triglyceride value par asar pada hai, aur mujhe kin baaton ka dhyan rakhna chahiye?",
        "source": "MedlinePlus (NLM) — Triglycerides Test Educational Reference",
    },
    "creatinine": {
        "aliases": ["serum creatinine", "creatinine", "creatinine, serum", "creat"],
        "what_en": (
            "Serum Creatinine measures a normal waste product created by daily muscle activity. "
            "Healthy kidneys filter creatinine out of the blood into urine."
        ),
        "what_hi": (
            "Serum Creatinine muscles (maanspeshiyon) ke rozana kaam se banne wala ek natural waste "
            "hai, jise kidneys khoon se chhaan kar urine (peshab) ke zariye bahar nikalti hain."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your serum creatinine is within the laboratory's reference range. Because creatinine "
                    "depends heavily on muscle mass and age, doctors often evaluate it alongside estimated "
                    "GFR (eGFR) and hydration status."
                ),
                "hi": (
                    "Aapka serum creatinine lab ki reference range ke andar hai. Creatinine vyakti ke muscle "
                    "mass aur umra par bhi nirbhar karta hai, isliye doctor ise eGFR ke saath dekhte hain."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your serum creatinine is below the laboratory's reference range. This is frequently "
                    "related to lower muscle mass, older age, pregnancy, or high fluid intake rather than kidney trouble."
                ),
                "hi": (
                    "Aapka serum creatinine reference range se kam hai. Aksar kam muscle mass, dubla sharir, "
                    "ya pregnancy mein creatinine aam range se thoda kam dikhta hai."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your serum creatinine is above the laboratory's reference range. Higher values can "
                    "reflect temporary dehydration, high protein/meat intake, heavy weightlifting, certain "
                    "medications, or changes in how quickly the kidneys filter fluid."
                ),
                "hi": (
                    "Aapka serum creatinine reference range se upar hai. Pani kam peene (dehydration), "
                    "heavy gym/exercise, high-protein diet, kuch painkillers, ya kidney filtration mein "
                    "badlaav se creatinine badh sakta hai."
                ),
            },
            "Unable to Classify": {
                "en": "Serum creatinine helps evaluate kidney filtration, but this value could not be automatically classified.",
                "hi": "Serum creatinine kidney ke chhanne ki kshamta samajhne mein madad karta hai, par is value ko classify nahi kiya ja saka.",
            },
        },
        "factors_en": [
            "Hydration levels (dehydration before the blood draw can temporarily raise creatinine)",
            "Body muscle mass, heavy exercise, or creatine supplements",
            "High-protein or cooked meat meals before testing",
            "Certain medications (such as NSAID pain relievers or blood pressure medicines)",
        ],
        "factors_hi": [
            "Sharir mein pani ki kami (dehydration se creatinine temporary taur par badh sakta hai)",
            "Muscle mass, bhari gym workout, ya protein/creatine supplements",
            "Dard ki dawaiyan (painkillers) ya kuch BP ki dawaiyan",
        ],
        "question_en": "How should I interpret this creatinine result given my age, hydration, and estimated GFR (eGFR)?",
        "question_hi": "Meri umra, pani peene ki aadat, aur eGFR ke hisaab se is creatinine value ka kya matlab hai?",
        "source": "National Kidney Foundation & MedlinePlus — Creatinine Test Overview",
    },
    "tsh": {
        "aliases": [
            "tsh",
            "thyroid stimulating hormone",
            "tsh (ultrasensitive)",
            "ultrasensitive tsh",
            "serum tsh",
        ],
        "what_en": (
            "Thyroid Stimulating Hormone (TSH) is a messenger hormone produced by the pituitary gland "
            "that tells your thyroid gland how much thyroid hormone (T3 and T4) to make."
        ),
        "what_hi": (
            "TSH (Thyroid Stimulating Hormone) dimag ki pituitary gland se nikalne wala ek messenger "
            "hormone hai, jo thyroid gland ko batata hai ki sharir ke liye kitna thyroid hormone (T3, T4) banana hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": (
                    "Your TSH value falls within the laboratory's reference interval, suggesting balanced "
                    "signaling between the pituitary and thyroid gland at the time of testing."
                ),
                "hi": (
                    "Aapka TSH level lab ki reference range ke andar hai, jo pituitary aur thyroid gland "
                    "ke beech santulit sanket darshata hai."
                ),
            },
            "Below Reference Range": {
                "en": (
                    "Your TSH value is below the laboratory's reference interval. When thyroid hormone "
                    "levels in the blood are already high (or thyroid medication dose is high), the pituitary "
                    "releases less TSH. Pregnancy and certain non-thyroid illnesses can also lower TSH."
                ),
                "hi": (
                    "Aapka TSH reference range se kam hai. Jab khoon mein thyroid hormone zyada hota hai "
                    "(ya thyroid ki goli ki dose zyada ho), tab TSH kam ho jaata hai. Doctor ise Free T3 aur Free T4 ke saath milakar dekhte hain."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your TSH value is above the laboratory's reference interval. When the thyroid gland "
                    "produces less hormone, the pituitary releases extra TSH to encourage it. Mild TSH "
                    "fluctuations can also happen with time of day, recovery from illness, or biotin supplements."
                ),
                "hi": (
                    "Aapka TSH lab ki reference range se upar hai. Jab thyroid gland thoda dhima kaam karti "
                    "hai, to dimag ki granthi zyada TSH bhejti hai. Halanki subah-shaam ke samay, haal ki bimari, "
                    "ya hair/nail supplements (biotin) se bhi TSH badal sakta hai."
                ),
            },
            "Unable to Classify": {
                "en": "TSH evaluates thyroid signaling, but this value could not be automatically classified.",
                "hi": "TSH thyroid granthi ke kaam ko samajhne ke liye hota hai, par is value ko classify nahi kiya ja saka.",
            },
        },
        "factors_en": [
            "Time of day (TSH naturally peaks late at night / early morning and drops in the afternoon)",
            "Biotin (Vitamin B7) hair/skin supplements taken within 48 hours of blood draw",
            "Pregnancy trimesters (which have distinct TSH reference ranges)",
            "Timing of existing thyroid hormone tablet before the blood sample",
        ],
        "factors_hi": [
            "Sample dene ka samay (subah khali pet TSH aur dopahar ke TSH mein natural antar hota hai)",
            "Baalon ya skin ke Biotin (Vitamin B7) supplements (jo test report ko prabhavit kar sakte hain)",
            "Pregnancy ki alag-alag trimesters",
            "Agar aap thyroid ki dawa lete hain, to test se pehle goli li thi ya nahi",
        ],
        "question_en": "Should we review my TSH alongside Free T4/Free T3 levels and symptoms before deciding if any follow-up is needed?",
        "question_hi": "Kya is TSH value ko Free T3, Free T4 aur mere lakshano ke saath milakar dekhne ki zaroorat hai?",
        "source": "American Thyroid Association & MedlinePlus — TSH Test Patient Guide",
    },
    "alt": {
        "aliases": ["sgpt", "alt", "sgpt (alt)", "alt (sgpt)", "alanine aminotransferase", "alanine transaminase"],
        "what_en": (
            "ALT (Alanine Aminotransferase, also called SGPT) is an enzyme found mainly inside liver cells "
            "that helps process proteins. Small amounts are normally present in the blood."
        ),
        "what_hi": (
            "SGPT (ALT) mukhya roop se liver cells ke andar paaya jaane wala ek enzyme hai. Jab liver "
            "cells par kisi tarah ka dabav ya irritation hota hai, to khoon mein iski matra badh sakti hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": "Your ALT (SGPT) level is within the laboratory's reference range.",
                "hi": "Aapka SGPT (ALT) level lab ki reference range ke andar hai.",
            },
            "Below Reference Range": {
                "en": "Your ALT (SGPT) level is below the laboratory's lower reference boundary, which is generally not a cause for concern.",
                "hi": "Aapka SGPT (ALT) reference range ki nichli seema se kam hai, jo aam taur par chinta ki baat nahi hoti.",
            },
            "Above Reference Range": {
                "en": (
                    "Your ALT (SGPT) level is above the laboratory's reference range. Mild-to-moderate elevations "
                    "are very common and can occur after taking common pain/fever medications, viral infections, "
                    "fatty liver changes, alcohol intake, or even strenuous muscle exercise."
                ),
                "hi": (
                    "Aapka SGPT (ALT) lab ki reference range se upar hai. Bukhar ya dard ki dawaiyon, "
                    "viral infection, fatty liver, khan-pan, ya bhari exercise ke baad bhi SGPT aasthaayi "
                    "roop se badh sakta hai."
                ),
            },
            "Unable to Classify": {
                "en": "ALT (SGPT) measures a liver enzyme, but this value could not be automatically classified.",
                "hi": "SGPT (ALT) ek liver enzyme hai, par is value ko automatically classify nahi kiya ja saka.",
            },
        },
        "factors_en": [
            "Recent use of over-the-counter pain relievers (like paracetamol/acetaminophen), antibiotics, or herbal supplements",
            "Strenuous muscle workouts or intramuscular injections",
            "Recent viral fever, dietary habits, or alcohol consumption",
        ],
        "factors_hi": [
            "Haal hi mein li gayi bukhar/dard ki dawaiyan (jaise paracetamol), antibiotics, ya herbal kadha/supplements",
            "Bhari gym/kasrat ya muscle injury",
            "Viral bukhar, khan-pan, ya alcohol ka sevan",
        ],
        "question_en": "Could any recent medicines, supplements, or lifestyle factors explain this SGPT (ALT) level, and when should it be rechecked?",
        "question_hi": "Kya haal ki kisi dawa, khan-pan, ya viral ke kaaran mera SGPT (ALT) badha hai, aur ise kab dubara check karana chahiye?",
        "source": "MedlinePlus (NLM) — ALT Blood Test Educational Reference",
    },
    "vitamin_d": {
        "aliases": [
            "vitamin d",
            "25-oh vitamin d",
            "25-hydroxy vitamin d",
            "vitamin d total",
            "25(oh)d",
            "vit d",
        ],
        "what_en": (
            "25-Hydroxy Vitamin D measures your body's stored supply of Vitamin D, which helps "
            "absorb calcium for bone strength, muscle function, and immune support."
        ),
        "what_hi": (
            "Vitamin D (25-OH) aapke sharir mein Vitamin D ke bhandar ko maapta hai, jo haddiyon ki "
            "mazbooti, calcium sokhne, aur muscles ke kaam ke liye zaroori hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": "Your Vitamin D level is within the laboratory's sufficiency reference range.",
                "hi": "Aapka Vitamin D level lab ki sufficiency reference range ke andar hai.",
            },
            "Below Reference Range": {
                "en": (
                    "Your Vitamin D level is below the laboratory's sufficiency range. Low Vitamin D is "
                    "very widespread among people who spend most daytime hours indoors or use sun protection. "
                    "Your doctor can advise on safe dietary or supplementation options — avoid high-dose self-medication."
                ),
                "hi": (
                    "Aapka Vitamin D level lab ki sufficiency range se kam hai. Ghar ya office ke andar "
                    "zyada samay bitane aur dhoop kam milne se Vitamin D kam hona bahut aam hai. Sahi matra "
                    "ke liye doctor se salah lein; bina puche high-dose supplements na lein."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your Vitamin D level is above the laboratory's reference range, which most often "
                    "occurs after high-dose Vitamin D supplementation."
                ),
                "hi": (
                    "Aapka Vitamin D level reference range se upar hai, jo aksar Vitamin D ke supplements "
                    "zyada matra mein lene se hota hai."
                ),
            },
            "Unable to Classify": {
                "en": "Vitamin D supports bone and calcium health, but this value could not be automatically classified.",
                "hi": "Vitamin D haddiyon aur calcium ke liye zaroori hai, par is value ko classify nahi kiya ja saka.",
            },
        },
        "factors_en": [
            "Daily sunlight exposure, season of the year, and skin pigmentation",
            "Dietary intake (fortified milk, fish, egg yolks) and recent supplement use",
        ],
        "factors_hi": [
            "Rozana dhoop mein rehne ka samay aur mausam",
            "Khan-pan (doodh, dahi, dhoop) aur haal mein liye gaye supplements",
        ],
        "question_en": "Based on this Vitamin D result, what diet, sunlight, or guided supplementation approach is appropriate for me?",
        "question_hi": "Is Vitamin D report ke aadhar par mere liye khan-pan aur dhoop ke saath kya salah sahi rahegi?",
        "source": "NIH Office of Dietary Supplements & MedlinePlus — Vitamin D Fact Sheet",
    },
    "potassium": {
        "aliases": ["serum potassium", "potassium", "potassium (k+)", "k+"],
        "what_en": (
            "Potassium is an essential mineral and electrolyte that helps nerves send signals "
            "and muscles (including the heart muscle) contract smoothly."
        ),
        "what_hi": (
            "Potassium sharir ka ek mahatvapurna electrolyte mineral hai, jo nerves (naso) ke "
            "sanket aur heart samet sabhi muscles ke sahi kaam mein madad karta hai."
        ),
        "context": {
            "Within Reference Range": {
                "en": "Your serum potassium is within the laboratory's reference interval.",
                "hi": "Aapka serum potassium lab ki reference range ke andar hai.",
            },
            "Below Reference Range": {
                "en": (
                    "Your serum potassium is below the laboratory's reference interval. Fluid loss from "
                    "sweating, vomiting, loose motions, or certain blood-pressure water pills (diuretics) "
                    "can lower blood potassium."
                ),
                "hi": (
                    "Aapka potassium level reference range se kam hai. Zyada pasina, ulti-dast, ya kuch "
                    "BP ki dawaiyon (diuretics) ke kaaran potassium kam ho sakta hai."
                ),
            },
            "Above Reference Range": {
                "en": (
                    "Your serum potassium is above the laboratory's reference interval. Notably, a common "
                    "laboratory artifact called 'hemolysis' (or tightly clenching your fist during the blood draw) "
                    "can leak potassium out of blood cells into the tube, causing a falsely elevated reading, "
                    "though kidney function and medications are also reviewed by doctors."
                ),
                "hi": (
                    "Aapka potassium level reference range se upar hai. Kai baar khoon nikalte waqt mutthi "
                    "zor se band karne ya sample tube mein cells tootne (hemolysis) se bhi potassium badha hua "
                    "aa sakta hai. Agar report par CRITICAL ALERT likha ho, to turant doctor ya lab se sampark karein."
                ),
            },
            "Unable to Classify": {
                "en": "Potassium measures blood electrolyte balance, but this value could not be automatically classified.",
                "hi": "Potassium khoon mein electrolyte balance batata hai, par is value ko classify nahi kiya ja saka.",
            },
        },
        "factors_en": [
            "Fist clenching during blood collection or sample hemolysis (which can falsely raise tube potassium)",
            "Hydration status, recent vomiting, diarrhea, or heavy sweating",
            "Blood pressure medications or potassium-containing salt substitutes",
        ],
        "factors_hi": [
            "Blood sample dete samay mutthi zor se bheenchana ya sample hemolysis",
            "Dehydration, ulti-dast, ya zyada pasina aana",
            "BP ki dawaiyan ya low-sodium salt substitutes",
        ],
        "question_en": "Should this potassium reading be rechecked on a fresh blood sample, and could any of my current medicines or diet affect it?",
        "question_hi": "Kya is potassium reading ko confirm karne ke liye dubara fresh sample dena chahiye, aur kya meri kisi dawa ka ispar asar hai?",
        "source": "MedlinePlus (NLM) — Potassium Blood Test Educational Guide",
    },
}


def find_curated_entry(test_name: str) -> dict[str, Any] | None:
    """Lookup a laboratory test in the curated medical reference database."""
    norm = (test_name or "").strip().lower()
    # Strip trailing parenthetical abbreviations for fallback matching
    norm_simple = norm.split("(")[0].strip()

    for entry in CURATED_TESTS.values():
        aliases = entry["aliases"]
        if norm in aliases or norm_simple in aliases:
            return entry
        for alias in aliases:
            if len(alias) >= 4 and (alias in norm or norm in alias):
                return entry
    return None


def build_curated_explanation_card(classified: ClassifiedParameter) -> ParameterExplanationCard:
    """Build a complete bilingual ParameterExplanationCard using deterministic status and curated medical reference."""
    entry = find_curated_entry(classified.test_name)
    status = classified.rule_based_status

    if entry:
        ctx = entry["context"].get(status, entry["context"]["Unable to Classify"])
        what_en = entry["what_en"]
        what_hi = entry["what_hi"]
        context_en = ctx["en"]
        context_hi = ctx["hi"]
        factors_en = list(entry["factors_en"])
        factors_hi = list(entry["factors_hi"])
        q_en = entry["question_en"]
        q_hi = entry["question_hi"]
        source = entry["source"]
    else:
        # Generic safe educational template for any other lab test
        what_en = (
            f"{classified.test_name} is a laboratory parameter measured in your sample to help your "
            f"healthcare provider evaluate specific physiological or biochemical processes in your body."
        )
        what_hi = (
            f"{classified.test_name} ek laboratory test parameter hai jo aapke doctor ko sharir ki "
            f"andaruni prakriyaon aur health status ko samajhne mein madad karta hai."
        )
        if status == "Within Reference Range":
            context_en = (
                f"Your reported result ({classified.original_result} {classified.unit}) is within the "
                f"laboratory's stated reference range ({classified.reference_range}). Remember that "
                f"an in-range result is one piece of information and does not replace a full clinical review."
            )
            context_hi = (
                f"Aapki report ki value ({classified.original_result} {classified.unit}) lab ki di gayi "
                f"reference range ({classified.reference_range}) ke andar hai. Phir bhi poori jankari ke liye "
                f"doctor aapke lakshano ke saath ise dekhenge."
            )
        elif status in ("Below Reference Range", "Above Reference Range"):
            direction_en = "below" if status == "Below Reference Range" else "above"
            direction_hi = "kam (below)" if status == "Below Reference Range" else "upar (above)"
            context_en = (
                f"Your reported result ({classified.original_result} {classified.unit}) is {direction_en} "
                f"the laboratory's reference range ({classified.reference_range}). An out-of-range value "
                f"does not automatically mean a disease is present; temporary physiological changes, "
                f"hydration, test preparation, or individual baselines often play a role."
            )
            context_hi = (
                f"Aapki report ki value ({classified.original_result} {classified.unit}) lab ki reference range "
                f"({classified.reference_range}) se {direction_hi} hai. Range se bahar aane ka matlab hamesha "
                f"bimari nahi hota — hydration, fasting, ya aasthaayi badlaav se bhi aisa ho sakta hai."
            )
        else:
            context_en = (
                f"Your reported result is {classified.original_result} {classified.unit}. Because a single "
                f"compatible numeric reference range could not be verified ({classified.classification_reason}), "
                f"LabSaathi has left this status as 'Unable to Classify' for your doctor to review directly."
            )
            context_hi = (
                f"Aapki report ki value {classified.original_result} {classified.unit} hai. Sahi numeric "
                f"reference range ya unit verify na hone ke kaaran ({classified.classification_reason}) "
                f"ise 'Unable to Classify' rakha gaya hai taaki doctor seedhe iski jaanch karein."
            )

        factors_en = [
            "Hydration status and whether the sample was collected fasting or after a meal",
            "Time of day, recent physical activity, and normal biological variation",
            "Differences in laboratory equipment and assay reagents across diagnostic centers",
        ]
        factors_hi = [
            "Sample dete samay sharir mein pani ki matra aur fasting ki sthiti",
            "Din ka samay, haal ki sharirik mehnat, aur har vyakti ka natural variation",
            "Alag-alag pathology labs ki machine aur testing method ka antar",
        ]
        q_en = f"How should I interpret this {classified.test_name} result ({classified.original_result} {classified.unit}) in the context of my overall health?"
        q_hi = f"Meri sehat aur lakshano ke hisaab se {classified.test_name} ({classified.original_result} {classified.unit}) ki is value ka kya matlab hai?"
        source = "MedlinePlus (U.S. National Library of Medicine) — Understanding Medical Tests Educational Guide"

    if classified.is_critical_alert:
        crit_note_en = (
            " IMPORTANT: Your laboratory report explicitly flagged this parameter with a critical/urgent alert. "
            "Please contact the ordering clinician or laboratory promptly as instructed on your report."
        )
        crit_note_hi = (
            " ZAROORI SOOCHNA: Aapki lab report mein is value par CRITICAL ALERT darj hai. "
            "Kripya bina deri kiye apne doctor ya lab se sampark karein."
        )
        context_en = context_en + crit_note_en
        context_hi = context_hi + crit_note_hi

    return ParameterExplanationCard(
        id=classified.id,
        test_name=classified.test_name,
        original_result=classified.original_result,
        unit=classified.unit,
        reference_range=classified.reference_range,
        lab_interpretation=classified.lab_interpretation,
        rule_based_status=status,
        classification_reason=classified.classification_reason,
        what_it_measures_en=what_en,
        what_it_measures_hi=what_hi,
        result_context_en=context_en,
        result_context_hi=context_hi,
        factors_affecting_en=factors_en,
        factors_affecting_hi=factors_hi,
        doctor_question_en=q_en,
        doctor_question_hi=q_hi,
        source_attribution=source,
        original_extracted_result=classified.original_extracted_result,
        user_edited=classified.user_edited,
        is_critical_alert=classified.is_critical_alert,
        page_number=classified.page_number,
    )


def generate_general_doctor_questions(
    classified_list: list[ClassifiedParameter],
) -> tuple[list[str], list[str]]:
    """Generate relevant, neutral, non-alarming doctor discussion questions based on verified results."""
    has_out_of_range = any(
        c.rule_based_status in ("Below Reference Range", "Above Reference Range")
        for c in classified_list
    )
    has_unclassified = any(
        c.rule_based_status == "Unable to Classify" for c in classified_list
    )

    questions_en = [
        "How should I understand these results in the context of my personal health history and how I feel?",
        "Could any routine medicines, supplements, recent minor illness, or fasting/hydration before the test have affected these numbers?",
    ]
    questions_hi = [
        "Meri pichhli health history aur rozana ki tabiyat ke hisaab se in lab results ko kaise samjha jaana chahiye?",
        "Kya kisi rozana ki dawa, vitamin supplement, haal ke bukhar, ya fasting/pani ki matra ka in values par asar pada ho sakta hai?",
    ]

    if has_out_of_range:
        out_names = [
            c.test_name
            for c in classified_list
            if c.rule_based_status in ("Below Reference Range", "Above Reference Range")
        ][:3]
        joined = ", ".join(out_names)
        questions_en.append(
            f"For the parameter(s) outside the reference range ({joined}), is this a mild variation for me or do I need a repeat/follow-up test?"
        )
        questions_hi.append(
            f"Jo parameters reference range se bahar hain ({joined}), kya woh mere liye mamooli badlaav hain ya kuch samay baad dubara test karana chahiye?"
        )

    if has_unclassified:
        questions_en.append(
            "What is the appropriate reference range for the unclassified parameter(s) on my report given my age and sex?"
        )
        questions_hi.append(
            "Jin parameters ki reference range report mein saaf nahi thi, meri umra aur sehat ke hisaab se unki sahi range kya honi chahiye?"
        )

    questions_en.extend(
        [
            "Are there any dietary, hydration, or lifestyle habits you recommend focusing on before my next checkup?",
            "When would you recommend scheduling my next routine follow-up?",
        ]
    )
    questions_hi.extend(
        [
            "Agle checkup se pehle khan-pan, pani peene, ya dincharya mein kin aam baaton ka dhyan rakhna achha rahega?",
            "Mujhe agla follow-up ya routine checkup kab karana chahiye?",
        ]
    )

    return questions_en, questions_hi
