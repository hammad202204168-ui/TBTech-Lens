"""English and Urdu texts. Every user-facing string lives here so a clinic can edit wording without touching code."""
T = {
"en": {
 "x_title": "Chest X-ray", "x_hint": "Optional. Upload the chest X-ray as a PNG or JPG picture.", "x_missing": "The X-ray reader is not installed on this server, so the picture cannot be read. Enter the clinical data only.",
 "x_Lower": "X-ray: no suspicious finding", "x_Intermediate": "X-ray: unclear, may be abnormal", "x_Higher": "X-ray: looks suspicious for TB",
 "x_adv_high": "The X-ray looks suspicious for TB. Send sputum for Xpert or culture now; do not wait.", "x_bad": "The X-ray could not be used: {e}",
 "overall": "Overall result", "clin": "Clinical result", "xr": "X-ray result", "new_check": "New patient", "print": "Print", "age_years": "Age (years)", "age_bad": "Enter an age between 15 and 110.",
 "choose_sex": "Choose sex", "wait": "Checking...", "rule": "The overall result is the higher of the clinical result and the X-ray result.", "err": "Something went wrong. Check the entries and try again.",
 "pid": "Patient reference (optional, no name or phone number)", "why_short": "Main reasons", "raises": "raises", "lowers": "lowers",
 "dir": "ltr", "title": "TB-Screen", "tagline": "TB risk screening for adults (15 years and older)",
 "disclaimer": "Screening, not diagnosis. Only a laboratory test (Xpert or culture) and a doctor can confirm or exclude TB. Research software, not a medical device.",
 "tab_screen": "Screen a person", "tab_clinic": "Clinic tools", "tab_about": "About and limits",
 "sec_person": "About the person", "age": "Age", "age_under15": "Under 15 (not supported)", "sex": "Sex", "female": "Female", "male": "Male",
 "tbtx": "TB treatment", "tbtx0": "Never treated for TB", "tbtx1": "Treated for TB in the past", "tbtx2": "On TB treatment now",
 "sec_symp": "Symptoms", "cough": "Cough", "fever": "Fever", "nightsweats": "Night sweats", "weightlost": "Weight loss", "chestpain": "Chest pain",
 "cough_dur": "If coughing: for how long?", "d1": "Less than 1 week", "d2": "1 to 2 weeks", "d3": "2 to 4 weeks", "d4": "4 weeks to 3 months", "d5": "3 months or more", "d0": "No cough",
 "sec_tests": "Optional test results (each one makes the result more reliable)", "has_crp": "I have a point-of-care CRP result",
 "crp": "CRP value (unit of your device; the study cut-off was 4)", "has_cad": "I have a chest X-ray CAD score (for example CAD4TB, 0 to 100)", "cad": "CAD score",
 "xray_up": "Upload chest X-ray image", "go": "Check TB risk", "result": "Result",
 "band_Lower": "Lower likelihood", "band_Intermediate": "Intermediate likelihood", "band_Higher": "Higher likelihood",
 "bt_Lower": "TB is less likely than in most people sent for TB testing.", "bt_Intermediate": "TB is about as likely as in the average person sent for TB testing.", "bt_Higher": "TB is more likely than in most people sent for TB testing.",
 "in_study": "In the study, about {n} in 100 people in this group, all sent for TB testing, had TB. Model estimate for this person: about {p}% (rough).",
 "adv_symptom_test": "There is at least one TB symptom. Ask a health worker for a TB test (sputum Xpert or culture) whatever this result says.",
 "adv_high": "Go to a clinic soon and ask for a TB test. Cover your mouth when you cough.",
 "adv_mid": "Visit a clinic for an assessment, and for a TB test if symptoms continue or the doctor advises it.",
 "adv_low": "A lower result does not rule out TB. If cough lasts 2 weeks or more, or there is weight loss, night sweats or blood in the sputum, see a doctor.",
 "adv_none": "No TB symptom was reported. Keep watching: if cough lasts 2 weeks or more, or there is fever, night sweats or weight loss, see a doctor.",
 "adv_lab_only": "Only a laboratory test and a doctor can confirm or exclude TB.",
 "need_dur": "Please choose how long the cough has lasted.", "choose": "Choose...",
 "cad_scale": "The CAD score looks like a fraction (below 1). CAD scores are usually 0 to 100, for example 72 and not 0.72. Please check the value; a wrong scale makes the result too low.",
 "adv_pk": "National TB programme clinics usually provide TB testing and treatment free of charge. Ask your local health service.",
 "next": "What to do next", "conf": "How reliable is this result?", "conf_limited": "Limited. Based on symptoms only. Adding a CRP result or a chest X-ray score makes it clearly better.",
 "conf_moderate": "Moderate. A CRP result was included. A chest X-ray CAD score would improve it further.", "conf_good": "Good for a screening tool. A chest X-ray CAD score was included.",
 "conf_note": "On people from a country the tool had not seen, it ranked TB above non-TB correctly {a}% of the time (0.50 would be a coin flip).",
 "oor": "{x} is outside the range the tool was built on, so the result is less reliable.", "why": "What pushed the result up or down", "why_axis": "Right = higher risk, left = lower",
 "pdf": "Download PDF report", "under15": "This tool was built on adults aged 15 and over. Please take children to a doctor.", "ontx": "The person is already on TB treatment, so a screening result does not apply. Continue treatment and follow the clinic's advice.",
 "save_log": "Save to this clinic's anonymous log", "site": "Clinic or site name", "ref": "Reference code (no names or phone numbers)", "saved": "Saved. Record number {i}.",
 "f_age_group": "Age group", "f_male": "Male sex", "f_prior_tb": "Earlier TB treatment", "f_cough": "Cough", "f_fever": "Fever", "f_chestpain": "Chest pain", "f_nightsweats": "Night sweats", "f_weightlost": "Weight loss",
 "f_cough_dur": "How long the cough has lasted", "f_crp_log2": "CRP level", "f_cad": "Chest X-ray CAD score", "f_xray_prob": "Chest X-ray image model",
 "c_batch": "Score a file", "c_records": "Records and outcomes", "c_validate": "Check against Xpert/culture",
 "pin": "Staff PIN", "pin_wrong": "Wrong PIN.", "batch_help": "One row per person. `age` in years (15 or older). Yes/no columns accept 1/0 or yes/no. `prior_tb`: no, history, or 'on treatment' (those rows are skipped). Leave crp and cad empty if not done. cough_dur: 0 none, 1 <1 week, 2 1-2 weeks, 3 2-4 weeks, 4 4 weeks-3 months, 5 3+ months. Up to 5,000 rows.",
 "tpl": "Download template (CSV)", "upload": "Upload filled CSV", "dl_scored": "Download scored CSV", "inmem": "Files are processed in memory and are not stored.",
 "no_records": "No records saved yet.", "set_outcome": "Record the laboratory result", "rec_id": "Record number", "out_tb": "TB confirmed (Xpert or culture positive)", "out_not": "TB not found (negative)", "save_outcome": "Save result",
 "val_help": "Upload a CSV with the template columns plus a column `tb` (yes/no from Xpert or culture). The tool checks how well its scores agree with your own results. At least 20 TB and 20 non-TB people are needed for a stable answer.",
 "val_enough": "Too few people for a stable answer (need at least 20 TB and 20 non-TB).", "val_auc": "AUC", "val_missed": "TB cases in the 'Lower' group", "val_sens": "TB found outside the 'Lower' group", "val_spec": "Non-TB placed in the 'Lower' group",
 "lang": "Language",
},
"ur": {
 "x_title": "سینے کا ایکسرے", "x_hint": "اختیاری۔ سینے کے ایکسرے کی تصویر PNG یا JPG میں اپ لوڈ کریں۔", "x_missing": "اس سرور پر ایکسرے پڑھنے والا ماڈیول نصب نہیں، اس لیے تصویر نہیں پڑھی جا سکتی۔ صرف کلینیکل ڈیٹا درج کریں۔",
 "x_Lower": "ایکسرے: کوئی مشتبہ علامت نہیں", "x_Intermediate": "ایکسرے: واضح نہیں، غیر معمولی ہو سکتا ہے", "x_Higher": "ایکسرے: ٹی بی کا شبہ ہے",
 "x_adv_high": "ایکسرے میں ٹی بی کا شبہ ہے۔ بلغم کا ایکسپرٹ یا کلچر ٹیسٹ فوراً بھیجیں، انتظار نہ کریں۔", "x_bad": "ایکسرے استعمال نہیں ہو سکا: {e}",
 "overall": "مجموعی نتیجہ", "clin": "کلینیکل نتیجہ", "xr": "ایکسرے کا نتیجہ", "new_check": "نیا مریض", "print": "پرنٹ", "age_years": "عمر (سال)", "age_bad": "15 سے 110 کے درمیان عمر درج کریں۔",
 "choose_sex": "جنس منتخب کریں", "wait": "جانچ ہو رہی ہے...", "rule": "مجموعی نتیجہ کلینیکل اور ایکسرے میں سے زیادہ خطرے والا نتیجہ ہے۔", "err": "کچھ خرابی ہوئی۔ اندراجات دیکھ کر دوبارہ کوشش کریں۔",
 "pid": "مریض کا حوالہ (اختیاری، نام یا فون نمبر نہ لکھیں)", "why_short": "اہم وجوہات", "raises": "بڑھاتا ہے", "lowers": "کم کرتا ہے",
 "dir": "rtl", "title": "TB-Screen", "tagline": "ٹی بی کے خطرے کی جانچ (بالغ افراد، 15 سال اور اس سے زیادہ)",
 "disclaimer": "یہ ابتدائی جانچ ہے، تشخیص نہیں۔ ٹی بی کی تصدیق یا تردید صرف لیبارٹری ٹیسٹ (ایکسپرٹ یا کلچر) اور ڈاکٹر ہی کر سکتے ہیں۔ یہ ریسرچ سافٹ ویئر ہے، طبی آلہ نہیں۔",
 "tab_screen": "فرد کی جانچ", "tab_clinic": "کلینک کے اوزار", "tab_about": "معلومات اور حدود",
 "sec_person": "فرد کے بارے میں", "age": "عمر", "age_under15": "15 سال سے کم (اس ٹول میں شامل نہیں)", "sex": "جنس", "female": "عورت", "male": "مرد",
 "tbtx": "ٹی بی کا علاج", "tbtx0": "کبھی ٹی بی کا علاج نہیں ہوا", "tbtx1": "ماضی میں ٹی بی کا علاج ہوا", "tbtx2": "اس وقت ٹی بی کا علاج جاری ہے",
 "sec_symp": "علامات", "cough": "کھانسی", "fever": "بخار", "nightsweats": "رات کو پسینہ", "weightlost": "وزن میں کمی", "chestpain": "سینے میں درد",
 "cough_dur": "اگر کھانسی ہے تو کتنے عرصے سے؟", "d1": "ایک ہفتے سے کم", "d2": "1 سے 2 ہفتے", "d3": "2 سے 4 ہفتے", "d4": "4 ہفتے سے 3 ماہ", "d5": "3 ماہ یا اس سے زیادہ", "d0": "کھانسی نہیں",
 "sec_tests": "اختیاری ٹیسٹ کے نتائج (جتنے زیادہ ہوں، نتیجہ اتنا زیادہ قابل اعتماد)", "has_crp": "میرے پاس سی آر پی (CRP) کا نتیجہ ہے",
 "crp": "سی آر پی کی قدر (اپنی مشین کی اکائی میں؛ تحقیق میں حد 4 تھی)", "has_cad": "میرے پاس سینے کے ایکسرے کا CAD اسکور ہے (مثلاً CAD4TB، 0 سے 100)", "cad": "CAD اسکور",
 "xray_up": "سینے کے ایکسرے کی تصویر اپ لوڈ کریں", "go": "ٹی بی کا خطرہ جانچیں", "result": "نتیجہ",
 "band_Lower": "کم امکان", "band_Intermediate": "درمیانی امکان", "band_Higher": "زیادہ امکان",
 "bt_Lower": "ٹی بی ٹیسٹ کے لیے بھیجے گئے زیادہ تر لوگوں کے مقابلے میں ٹی بی کا امکان کم ہے۔", "bt_Intermediate": "ٹی بی ٹیسٹ کے لیے بھیجے گئے عام شخص جتنا ٹی بی کا امکان ہے۔", "bt_Higher": "ٹی بی ٹیسٹ کے لیے بھیجے گئے زیادہ تر لوگوں کے مقابلے میں ٹی بی کا امکان زیادہ ہے۔",
 "in_study": "تحقیق میں اس گروپ کے ہر 100 افراد میں سے تقریباً {n} کو ٹی بی تھی (سب کا ٹی بی ٹیسٹ ہوا تھا)۔ اس فرد کے لیے ماڈل کا اندازہ: تقریباً {p}٪ (موٹا اندازہ)۔",
 "adv_symptom_test": "ٹی بی کی کم از کم ایک علامت موجود ہے۔ اس نتیجے سے قطع نظر، صحت کارکن سے ٹی بی ٹیسٹ (بلغم کا ایکسپرٹ یا کلچر) کروائیں۔",
 "adv_high": "جلد کلینک جائیں اور ٹی بی ٹیسٹ کروائیں۔ کھانستے وقت منہ ڈھانپیں۔",
 "adv_mid": "معائنے کے لیے کلینک جائیں؛ علامات برقرار رہیں یا ڈاکٹر مشورہ دے تو ٹی بی ٹیسٹ کروائیں۔",
 "adv_low": "کم امکان کا مطلب یہ نہیں کہ ٹی بی نہیں ہے۔ اگر کھانسی 2 ہفتے یا زیادہ رہے، وزن گھٹے، رات کو پسینہ آئے یا بلغم میں خون آئے تو ڈاکٹر کو دکھائیں۔",
 "adv_none": "ٹی بی کی کوئی علامت نہیں بتائی گئی۔ نگرانی رکھیں: اگر کھانسی 2 ہفتے یا زیادہ رہے، یا بخار، رات کو پسینہ یا وزن میں کمی ہو تو ڈاکٹر کو دکھائیں۔",
 "adv_lab_only": "ٹی بی کی تصدیق یا تردید صرف لیبارٹری ٹیسٹ اور ڈاکٹر ہی کر سکتے ہیں۔",
 "need_dur": "براہ کرم بتائیں کہ کھانسی کتنے عرصے سے ہے۔", "choose": "منتخب کریں...",
 "cad_scale": "CAD اسکور ایک سے کم (کسر) لگ رہا ہے۔ CAD اسکور عموماً 0 سے 100 کے درمیان ہوتا ہے، مثلاً 72 نہ کہ 0.72۔ براہ کرم قدر چیک کریں؛ غلط پیمانے سے نتیجہ ضرورت سے کم آتا ہے۔",
 "adv_pk": "قومی ٹی بی پروگرام کے کلینک عموماً ٹی بی کی جانچ اور علاج مفت فراہم کرتے ہیں۔ اپنی مقامی صحت سروس سے پوچھیں۔",
 "next": "اب کیا کریں", "conf": "یہ نتیجہ کتنا قابل اعتماد ہے؟", "conf_limited": "محدود۔ صرف علامات کی بنیاد پر ہے۔ سی آر پی یا ایکسرے کا اسکور شامل کرنے سے نتیجہ واضح طور پر بہتر ہوتا ہے۔",
 "conf_moderate": "درمیانہ۔ سی آر پی کا نتیجہ شامل ہے۔ ایکسرے کا CAD اسکور شامل کرنے سے مزید بہتری آئے گی۔", "conf_good": "جانچ کے ٹول کے لیے اچھا۔ ایکسرے کا CAD اسکور شامل ہے۔",
 "conf_note": "کسی ایسے ملک کے لوگوں پر جنہیں ٹول نے پہلے نہیں دیکھا تھا، اس نے {a}٪ مرتبہ ٹی بی والے کو بغیر ٹی بی والے سے اوپر رکھا (0.50 سکہ اچھالنے کے برابر ہے)۔",
 "oor": "{x} اس حد سے باہر ہے جس پر ٹول بنایا گیا تھا، اس لیے نتیجہ کم قابل اعتماد ہے۔", "why": "نتیجہ کس وجہ سے اوپر یا نیچے گیا", "why_axis": "دائیں = زیادہ خطرہ، بائیں = کم",
 "pdf": "پی ڈی ایف رپورٹ ڈاؤن لوڈ کریں", "under15": "یہ ٹول 15 سال اور اس سے زیادہ عمر کے بالغ افراد پر بنایا گیا ہے۔ براہ کرم بچوں کو ڈاکٹر کو دکھائیں۔", "ontx": "فرد پہلے ہی ٹی بی کا علاج کروا رہا ہے، اس لیے جانچ کا نتیجہ لاگو نہیں ہوتا۔ علاج جاری رکھیں اور کلینک کی ہدایات پر عمل کریں۔",
 "save_log": "اس کلینک کے گمنام ریکارڈ میں محفوظ کریں", "site": "کلینک یا جگہ کا نام", "ref": "حوالہ کوڈ (نام یا فون نمبر نہ لکھیں)", "saved": "محفوظ ہو گیا۔ ریکارڈ نمبر {i}۔",
 "f_age_group": "عمر کا گروپ", "f_male": "مرد ہونا", "f_prior_tb": "پہلے ٹی بی کا علاج", "f_cough": "کھانسی", "f_fever": "بخار", "f_chestpain": "سینے میں درد", "f_nightsweats": "رات کو پسینہ", "f_weightlost": "وزن میں کمی",
 "f_cough_dur": "کھانسی کا دورانیہ", "f_crp_log2": "سی آر پی کی سطح", "f_cad": "ایکسرے کا CAD اسکور", "f_xray_prob": "ایکسرے تصویر کا ماڈل",
 "c_batch": "فائل سے جانچ", "c_records": "ریکارڈ اور نتائج", "c_validate": "ایکسپرٹ/کلچر سے موازنہ",
 "pin": "اسٹاف پن", "pin_wrong": "پن غلط ہے۔", "batch_help": "ہر فرد کی ایک قطار۔ `age` سالوں میں (15 یا زیادہ)۔ ہاں/نہیں والے کالم میں 1/0 یا yes/no لکھیں۔ `prior_tb`: no، history، یا 'on treatment' (ایسی قطاریں چھوڑ دی جاتی ہیں)۔ اگر سی آر پی یا cad نہیں ہوا تو خالی چھوڑیں۔ زیادہ سے زیادہ 5,000 قطاریں۔ cough_dur: 0 نہیں، 1 ایک ہفتے سے کم، 2 1-2 ہفتے، 3 2-4 ہفتے، 4 4 ہفتے سے 3 ماہ، 5 3 ماہ سے زیادہ۔",
 "tpl": "ٹیمپلیٹ ڈاؤن لوڈ کریں (CSV)", "upload": "بھری ہوئی CSV اپ لوڈ کریں", "dl_scored": "نتائج کے ساتھ CSV ڈاؤن لوڈ کریں", "inmem": "فائلیں صرف میموری میں پروسیس ہوتی ہیں اور محفوظ نہیں کی جاتیں۔",
 "no_records": "ابھی کوئی ریکارڈ محفوظ نہیں ہوا۔", "set_outcome": "لیبارٹری کا نتیجہ درج کریں", "rec_id": "ریکارڈ نمبر", "out_tb": "ٹی بی کی تصدیق ہوئی (ایکسپرٹ یا کلچر مثبت)", "out_not": "ٹی بی نہیں ملی (منفی)", "save_outcome": "نتیجہ محفوظ کریں",
 "val_help": "ٹیمپلیٹ کے کالم کے ساتھ ایک کالم `tb` (ایکسپرٹ یا کلچر کا yes/no) والی CSV اپ لوڈ کریں۔ ٹول دیکھے گا کہ اس کے اسکور آپ کے اپنے نتائج سے کتنا ملتے ہیں۔ مستحکم جواب کے لیے کم از کم 20 ٹی بی اور 20 غیر ٹی بی افراد چاہئیں۔",
 "val_enough": "مستحکم جواب کے لیے افراد کم ہیں (کم از کم 20 ٹی بی اور 20 غیر ٹی بی چاہئیں)۔", "val_auc": "AUC", "val_missed": "'کم' گروپ میں ٹی بی کے کیس", "val_sens": "'کم' گروپ سے باہر ملنے والی ٹی بی", "val_spec": "'کم' گروپ میں رکھے گئے غیر ٹی بی افراد",
 "lang": "زبان",
}}
DUR = {0: "d0", 1: "d1", 2: "d2", 3: "d3", 4: "d4", 5: "d5"}


def tr(lang, key, **kw):
    s = T.get(lang, T["en"]).get(key) or T["en"].get(key, key)
    return s.format(**kw) if kw else s


def confidence_key(auc):
    return "conf_limited" if auc < 0.62 else "conf_moderate" if auc < 0.72 else "conf_good"


# ---- v2 web page: neutral wording, three modes, report labels (overrides earlier keys of the same name)
T["en"].update({
 "tagline": "Clinical and chest X-ray screening for tuberculosis",
 "disclaimer": "Screening support, not a diagnosis. Only a laboratory test and a doctor can confirm or exclude TB. Results can differ between people and settings.",
 "bt_Lower": "TB is less likely on this screening.", "bt_Intermediate": "This screening is indeterminate. More assessment is needed.", "bt_Higher": "TB is more likely on this screening. Confirm with a laboratory test.",
 "crp": "CRP (mg/L), optional", "cad": "CAD score (0 to 100), optional", "go": "Run screening",
 "mode_clinical": "Clinical data", "mode_xray": "Chest X-ray", "mode_both": "Clinical + X-ray", "mode_hint": "Choose what is available for this patient.",
 "sec_xray": "Chest X-ray picture", "xray_drop": "Choose a PNG or JPG picture of the chest X-ray", "xray_none": "No chest X-ray? Use the Clinical data option.",
 "res_overall": "Overall result", "res_clin": "Clinical result", "res_xray": "X-ray result", "res_imp": "Impression", "res_tests": "Suggested tests", "res_prec": "Precautions", "res_why": "What shaped the clinical result",
 "res_heat": "Where the X-ray reading looked", "res_urgent": "Seek urgent care", "dl_pdf": "Download PDF report", "print": "Print", "new_check": "New patient", "wait": "Analysing...",
 "heat_note": "Brighter areas changed the score most. This shows where the model looked; it is not a diagnosis of a lesion.", "need_one": "Enter the clinical data, add a chest X-ray, or both.",
 "xray_na": "The X-ray reader is not installed on this server. Use the Clinical data option.", "xray_failed": "The X-ray could not be used: {e}", "not_done": "not done",
 "raises": "raises", "lowers": "lowers", "ref": "Patient reference (optional; no name or phone number)", "pdf_fail": "The report could not be created. Check the entries and try again.",
 "why_note": "Bars compare this patient with the average person in the reference group. Some entries can look counter-intuitive; use them to understand the score, not to decide treatment.", "legend_lo": "Lower", "legend_mid": "Indeterminate", "legend_hi": "Higher", "sex_pick": "Choose sex", "age_bad": "Enter an age between 15 and 110.", "err": "Something went wrong. Check the entries and try again.",
})
T["ur"].update({
 "tagline": "ٹی بی کے لیے کلینیکل اور سینے کے ایکسرے کی جانچ",
 "disclaimer": "یہ جانچ میں معاونت ہے، تشخیص نہیں۔ ٹی بی کی تصدیق یا تردید صرف لیبارٹری ٹیسٹ اور ڈاکٹر ہی کر سکتے ہیں۔ نتائج افراد اور مقامات کے لحاظ سے مختلف ہو سکتے ہیں۔",
 "bt_Lower": "اس جانچ میں ٹی بی کا امکان کم ہے۔", "bt_Intermediate": "یہ جانچ واضح نہیں۔ مزید معائنہ ضروری ہے۔", "bt_Higher": "اس جانچ میں ٹی بی کا امکان زیادہ ہے۔ لیبارٹری ٹیسٹ سے تصدیق کروائیں۔",
 "crp": "سی آر پی (mg/L)، اختیاری", "cad": "CAD اسکور (0 سے 100)، اختیاری", "go": "جانچ شروع کریں",
 "mode_clinical": "کلینیکل ڈیٹا", "mode_xray": "سینے کا ایکسرے", "mode_both": "کلینیکل + ایکسرے", "mode_hint": "جو اس مریض کے لیے دستیاب ہے وہ منتخب کریں۔",
 "sec_xray": "سینے کے ایکسرے کی تصویر", "xray_drop": "سینے کے ایکسرے کی PNG یا JPG تصویر منتخب کریں", "xray_none": "ایکسرے نہیں ہے؟ کلینیکل ڈیٹا والا آپشن استعمال کریں۔",
 "res_overall": "مجموعی نتیجہ", "res_clin": "کلینیکل نتیجہ", "res_xray": "ایکسرے کا نتیجہ", "res_imp": "تاثر", "res_tests": "تجویز کردہ ٹیسٹ", "res_prec": "احتیاطی تدابیر", "res_why": "کلینیکل نتیجہ کن باتوں سے بنا",
 "res_heat": "ایکسرے کی پڑھائی نے کہاں دیکھا", "res_urgent": "فوری طبی مدد لیں", "dl_pdf": "پی ڈی ایف رپورٹ ڈاؤن لوڈ کریں", "print": "پرنٹ", "new_check": "نیا مریض", "wait": "جانچ ہو رہی ہے...",
 "heat_note": "زیادہ روشن حصوں نے اسکور کو سب سے زیادہ بدلا۔ یہ دکھاتا ہے کہ ماڈل نے کہاں دیکھا؛ یہ کسی گھاؤ کی تشخیص نہیں۔", "need_one": "کلینیکل ڈیٹا درج کریں، سینے کا ایکسرے شامل کریں، یا دونوں۔",
 "xray_na": "اس سرور پر ایکسرے پڑھنے والا ماڈیول نصب نہیں۔ کلینیکل ڈیٹا والا آپشن استعمال کریں۔", "xray_failed": "ایکسرے استعمال نہیں ہو سکا: {e}", "not_done": "نہیں ہوا",
 "raises": "بڑھاتا ہے", "lowers": "کم کرتا ہے", "ref": "مریض کا حوالہ (اختیاری؛ نام یا فون نمبر نہ لکھیں)", "pdf_fail": "رپورٹ نہیں بن سکی۔ اندراجات دیکھ کر دوبارہ کوشش کریں۔",
 "why_note": "بارز اس مریض کا موازنہ حوالہ گروپ کے اوسط فرد سے کرتے ہیں۔ کچھ اندراجات الٹے لگ سکتے ہیں؛ انہیں اسکور سمجھنے کے لیے دیکھیں، علاج کے فیصلے کے لیے نہیں۔", "legend_lo": "کم", "legend_mid": "غیر واضح", "legend_hi": "زیادہ", "sex_pick": "جنس منتخب کریں", "age_bad": "15 سے 110 کے درمیان عمر درج کریں۔", "err": "کچھ خرابی ہوئی۔ اندراجات دیکھ کر دوبارہ کوشش کریں۔",
})
for _L in ("en", "ur"):
    for _k in ("in_study", "conf", "conf_limited", "conf_moderate", "conf_good", "conf_note", "adv_pk"): T[_L].pop(_k, None)


# ---- v3: patient records, mascot, bilingual report
import os as _os
APP_NAME = _os.environ.get("APP_NAME", "PulmoSight")
T["en"].update({
 "title": APP_NAME, "tagline": "Clinical and chest X-ray screening for tuberculosis, with follow-up tracking",
 "tab_new": "New screening", "tab_rec": "Patient records", "save_visit": "Save this visit to the patient's record",
 "ref": "Patient reference code (no name or phone number)", "ref_hint": "Needed to save a visit or compare with earlier visits.",
 "rep_lang": "Report language", "rep_en": "English", "rep_ur": "اردو", "rep_both": "English + اردو",
 "res_trend": "Compared with the last visit", "res_follow": "Follow-up", "res_about": "About TB: cause and spread", "res_factors": "Points noted for this patient",
 "saved_ok": "Visit saved to record {r}.", "hist": "Earlier visits", "visits_n": "{n} visits",
 "rec_search": "Search reference code", "rec_empty": "No patient records yet. Run a screening and tick 'Save this visit'.", "rec_open": "Open", "rec_delete": "Delete record",
 "rec_del_confirm": "Delete all visits for this reference code? This cannot be undone.", "rec_export": "Export all (CSV)", "rec_back": "Back to list", "rec_last": "Last visit",
 "col_date": "Date", "col_result": "Result", "col_score": "Score", "col_lab": "Laboratory result", "lab_tb": "TB confirmed", "lab_not": "TB not found", "lab_none": "Not entered",
 "lab_set": "Record laboratory result", "lab_saved": "Laboratory result saved.", "follow_prefill": "Screen again", "chart_title": "Screening score over visits (lower is better)",
 "pin_label": "Clinic PIN", "pin_ask": "Enter the clinic PIN to continue.", "mas_Lower": "Lungs look comfortable on this screening", "mas_Intermediate": "Lungs need a closer look", "mas_Higher": "Lungs need urgent testing",
 "tr_improving": "Score lower", "tr_similar": "About the same", "tr_worsening": "Score higher", "why_title": "Why this result", "why_plain": "Each bar shows how much one entry moved the score up (right) or down (left) compared with an average person.",
 "e_ref_required": "Enter a reference code to save the visit.", "e_ref_format": "Use letters, numbers, dot, dash or slash only (up to 40 characters).", "e_ref_looks_like_id": "That looks like an ID or phone number. Use a clinic code instead.",
 "e_pin_required": "The clinic PIN is missing or wrong.", "e_not_found": "Nothing found.",
})
T["ur"].update({
 "title": APP_NAME, "tagline": "ٹی بی کے لیے کلینیکل اور سینے کے ایکسرے کی جانچ، فالو اپ کے ساتھ",
 "tab_new": "نئی جانچ", "tab_rec": "مریضوں کا ریکارڈ", "save_visit": "اس وزٹ کو مریض کے ریکارڈ میں محفوظ کریں",
 "ref": "مریض کا حوالہ کوڈ (نام یا فون نمبر نہ لکھیں)", "ref_hint": "وزٹ محفوظ کرنے یا پچھلی وزٹ سے موازنہ کے لیے ضروری ہے۔",
 "rep_lang": "رپورٹ کی زبان", "rep_en": "English", "rep_ur": "اردو", "rep_both": "English + اردو",
 "res_trend": "پچھلی وزٹ سے موازنہ", "res_follow": "فالو اپ", "res_about": "ٹی بی کے بارے میں: وجہ اور پھیلاؤ", "res_factors": "اس مریض کے بارے میں قابل ذکر نکات",
 "saved_ok": "وزٹ ریکارڈ {r} میں محفوظ ہو گئی۔", "hist": "پچھلی وزٹس", "visits_n": "{n} وزٹس",
 "rec_search": "حوالہ کوڈ تلاش کریں", "rec_empty": "ابھی کوئی ریکارڈ نہیں۔ جانچ کریں اور 'اس وزٹ کو محفوظ کریں' پر نشان لگائیں۔", "rec_open": "کھولیں", "rec_delete": "ریکارڈ مٹائیں",
 "rec_del_confirm": "اس حوالہ کوڈ کی تمام وزٹس مٹا دی جائیں؟ یہ واپس نہیں ہو سکتا۔", "rec_export": "سب برآمد کریں (CSV)", "rec_back": "فہرست پر واپس", "rec_last": "آخری وزٹ",
 "col_date": "تاریخ", "col_result": "نتیجہ", "col_score": "اسکور", "col_lab": "لیبارٹری نتیجہ", "lab_tb": "ٹی بی کی تصدیق", "lab_not": "ٹی بی نہیں ملی", "lab_none": "درج نہیں",
 "lab_set": "لیبارٹری نتیجہ درج کریں", "lab_saved": "لیبارٹری نتیجہ محفوظ ہو گیا۔", "follow_prefill": "دوبارہ جانچ", "chart_title": "وزٹس میں جانچ کا اسکور (کم بہتر ہے)",
 "pin_label": "کلینک پن", "pin_ask": "جاری رکھنے کے لیے کلینک کا پن درج کریں۔", "mas_Lower": "اس جانچ میں پھیپھڑے ٹھیک لگتے ہیں", "mas_Intermediate": "پھیپھڑوں کو قریب سے دیکھنے کی ضرورت ہے", "mas_Higher": "پھیپھڑوں کا فوری ٹیسٹ ضروری ہے",
 "tr_improving": "اسکور کم", "tr_similar": "تقریباً وہی", "tr_worsening": "اسکور زیادہ", "why_title": "یہ نتیجہ کیوں", "why_plain": "ہر بار دکھاتی ہے کہ ایک اندراج نے اوسط شخص کے مقابلے میں اسکور کتنا اوپر (دائیں) یا نیچے (بائیں) کیا۔",
 "e_ref_required": "وزٹ محفوظ کرنے کے لیے حوالہ کوڈ لکھیں۔", "e_ref_format": "صرف حروف، اعداد، نقطہ، ڈیش یا سلیش استعمال کریں (زیادہ سے زیادہ 40)۔", "e_ref_looks_like_id": "یہ شناختی نمبر یا فون نمبر لگتا ہے۔ کلینک کا کوڈ استعمال کریں۔",
 "e_pin_required": "کلینک کا پن غائب یا غلط ہے۔", "e_not_found": "کچھ نہیں ملا۔",
})

# ---- v3.1: extra findings and report upload
APP_NAME = _os.environ.get("APP_NAME", "TBTech Lens"); T["en"]["title"] = T["ur"]["title"] = APP_NAME
T["en"].update({
 "sec_more": "More symptoms and risk factors (optional)", "sec_labs": "More laboratory results (optional)", "up_title": "Upload a lab or clinic report", "up_hint": "PDF, photo or text file. Values are read on this server, filled in below and not stored. Check every value before screening.",
 "up_btn": "Choose report", "up_found": "Filled {n} values from the report. Please check them.", "up_none": "No known values were found in this file. Type them in below.", "up_fail": "The file could not be read.", "up_ocr": "Reading text from pictures is not available on this server. Upload a PDF with text.",
 "up_src": "Read from", "hemoptysis": "Coughing up blood", "breathless": "Shortness of breath", "fatigue": "Unusual tiredness", "appetite_loss": "Loss of appetite", "diabetes": "Diabetes", "contact": "Lives with or has been close to someone with TB", "smoker": "Smoker",
 "hiv": "HIV test", "hiv_u": "Not known", "hiv_p": "Positive", "hiv_n": "Negative", "bmi": "BMI (kg/m²)", "esr": "ESR (mm/h)", "wbc": "White cells (×10⁹/L)", "hb": "Haemoglobin (g/dL)", "xpert": "Sputum Xpert", "afb": "Sputum smear (AFB)", "culture": "TB culture", "igra": "IGRA blood test", "mantoux": "Skin test (Mantoux) in mm",
 "o_none": "Not done", "o_pos": "Positive", "o_neg": "Negative", "o_det": "MTB detected", "o_nd": "MTB not detected", "o_rif": "MTB detected, rifampicin resistant", "res_support": "Notes on the additional findings", "analysing": "Analysing…",
 "e_file_too_big": "The file is larger than 8 MB.", "e_empty_file": "The file is empty.", "e_unsupported_file": "Unsupported file. Use PDF, PNG, JPG or text.", "e_ocr_missing": "Reading text from pictures is not available on this server.", "e_unreadable_file": "The file could not be read.",
})
T["ur"].update({
 "sec_more": "مزید علامات اور خطرے کے عوامل (اختیاری)", "sec_labs": "مزید لیبارٹری نتائج (اختیاری)", "up_title": "لیب یا کلینک کی رپورٹ اپ لوڈ کریں", "up_hint": "PDF، تصویر یا ٹیکسٹ فائل۔ اقدار اس سرور پر پڑھی جاتی ہیں، نیچے بھر دی جاتی ہیں اور محفوظ نہیں ہوتیں۔ جانچ سے پہلے ہر قدر دیکھ لیں۔",
 "up_btn": "رپورٹ منتخب کریں", "up_found": "رپورٹ سے {n} اقدار بھر دی گئیں۔ براہ کرم انہیں دیکھ لیں۔", "up_none": "اس فائل میں کوئی معروف قدر نہیں ملی۔ نیچے خود لکھیں۔", "up_fail": "فائل پڑھی نہیں جا سکی۔", "up_ocr": "اس سرور پر تصویر سے متن پڑھنا دستیاب نہیں۔ متن والی PDF اپ لوڈ کریں۔",
 "up_src": "یہاں سے پڑھا", "hemoptysis": "کھانسی میں خون", "breathless": "سانس پھولنا", "fatigue": "غیر معمولی تھکاوٹ", "appetite_loss": "بھوک کی کمی", "diabetes": "ذیابیطس", "contact": "ٹی بی کے مریض کے ساتھ رہتے ہیں یا قریبی رابطہ رہا", "smoker": "تمباکو نوشی",
 "hiv": "ایچ آئی وی ٹیسٹ", "hiv_u": "معلوم نہیں", "hiv_p": "مثبت", "hiv_n": "منفی", "bmi": "بی ایم آئی (kg/m²)", "esr": "ای ایس آر (mm/h)", "wbc": "سفید خلیات (×10⁹/L)", "hb": "ہیموگلوبن (g/dL)", "xpert": "بلغم کا ایکسپرٹ", "afb": "بلغم کی سمیئر (AFB)", "culture": "ٹی بی کلچر", "igra": "آئی جی آر اے خون ٹیسٹ", "mantoux": "جلد کا ٹیسٹ (مانٹو) ملی میٹر",
 "o_none": "نہیں ہوا", "o_pos": "مثبت", "o_neg": "منفی", "o_det": "ٹی بی کے جراثیم ملے", "o_nd": "جراثیم نہیں ملے", "o_rif": "جراثیم ملے، رائفیمپیسن مزاحم", "res_support": "اضافی معلومات پر نوٹس", "analysing": "تجزیہ جاری ہے…",
 "e_file_too_big": "فائل 8 MB سے بڑی ہے۔", "e_empty_file": "فائل خالی ہے۔", "e_unsupported_file": "فائل کی قسم قابل قبول نہیں۔ PDF، PNG، JPG یا ٹیکسٹ استعمال کریں۔", "e_ocr_missing": "اس سرور پر تصویر سے متن پڑھنا دستیاب نہیں۔", "e_unreadable_file": "فائل پڑھی نہیں جا سکی۔",
})

T["en"].update({"rep_no": "Report number", "rep_find": "Find by report number", "rep_find_ph": "TBL-2026-000001-X", "rep_nf": "No saved report has this number.", "rep_unsaved": "Tick 'Save this visit' and enter a reference code to get a report number.",
 "up_known": "This report was issued by this app: {n}. Open its saved record.", "copy": "Copy", "e_visit_not_found": "The saved visit does not match this reference code."})
T["ur"].update({"rep_no": "رپورٹ نمبر", "rep_find": "رپورٹ نمبر سے تلاش کریں", "rep_find_ph": "TBL-2026-000001-X", "rep_nf": "اس نمبر کی کوئی محفوظ رپورٹ نہیں ملی۔", "rep_unsaved": "رپورٹ نمبر کے لیے 'اس وزٹ کو محفوظ کریں' پر نشان لگائیں اور حوالہ کوڈ لکھیں۔",
 "up_known": "یہ رپورٹ اسی ایپ نے جاری کی تھی: {n}۔ اس کا محفوظ ریکارڈ کھولیں۔", "copy": "کاپی", "e_visit_not_found": "محفوظ وزٹ اس حوالہ کوڈ سے میل نہیں کھاتی۔"})
