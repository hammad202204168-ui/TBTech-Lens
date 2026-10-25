"""Result-specific impression, suggested tests and precautions.
Not one fixed script: every item is switched on by the patient's own result (overall level, symptoms, TB history, X-ray finding and picture quality, CRP).
Texts exist in English and Urdu; `compose(a, lang)` returns plain strings ready for the screen or the PDF."""

TX = {
"en": {
 "head_Higher": "The findings point to a higher likelihood of pulmonary TB. A confirmatory laboratory test is advised without delay.",
 "head_Intermediate": "The findings are indeterminate for pulmonary TB. Further assessment and a confirmatory test are advised.",
 "head_Lower": "The findings point to a lower likelihood of pulmonary TB on this screening. This does not exclude TB.",
 "basis_clin": "Clinical screening: {band}.", "basis_xray": "Chest X-ray: {band}.", "basis_both_same": "Clinical screening and chest X-ray give the same level.",
 "basis_both_diff": "Clinical screening and chest X-ray differ; the higher level sets the overall result and a confirmatory test settles it.",
 "contrib": "Main contributors: {f}.", "crp_high": "CRP is raised ({v} mg/L), a non-specific sign of inflammation.",
 "region": "The X-ray score was driven mainly by the {v} {h} part of the picture (as displayed). This shows where the model looked; it is not a diagnosis of a lesion.",
 "v_upper": "upper", "v_mid": "middle", "v_lower": "lower", "h_left": "left", "h_centre": "central", "h_right": "right",
 "q_small": "The X-ray picture is small, so the reading may be less reliable.", "q_dark": "The X-ray picture is very dark.", "q_bright": "The X-ray picture is very bright.", "q_flat": "The X-ray picture has very low contrast.",
 "t_xpert": ("Sputum Xpert MTB/RIF (Ultra)", "Detects TB bacteria and rifampicin resistance within hours; the main test to confirm or exclude TB."),
 "t_culture": ("Sputum culture with drug-susceptibility testing", "Needed after earlier TB treatment or if Xpert is positive or unclear; shows which medicines will work."),
 "t_cxr": ("Chest X-ray, with computer-aided reading where available", "Looks for lung changes; this result was based on symptoms and tests only."),
 "t_radiologist": ("Radiologist review of the chest X-ray", "Confirms the finding and looks for other lung conditions."),
 "t_retake": ("Repeat the X-ray with a clearer picture", "The picture quality limits how reliable the reading is."),
 "t_hiv": ("HIV test", "HIV changes TB risk and treatment and is a standard part of a TB work-up."),
 "t_glucose": ("Blood glucose or HbA1c", "Diabetes raises TB risk and needs managing; weight loss can be a sign of either."),
 "t_review": ("Clinical review in about 2 weeks", "If the cough, fever, night sweats or weight loss continue, a test is needed even with a lower score."),
 "p_cough": "Cover the mouth and nose when coughing, use tissues and dispose of them safely, and wash hands afterwards.",
 "p_vent": "Keep windows open and rooms ventilated; avoid sleeping in a shared closed room until TB is excluded.",
 "p_mask": "Wear a mask near other people and in health facilities until TB is excluded.",
 "p_crowd": "Avoid crowded, closed places and long shared transport until the test result is known.",
 "p_nutri": "Eat energy- and protein-rich food and weigh yourself weekly; report further weight loss.",
 "p_smoke": "Avoid smoking and smoke exposure; they worsen cough and lung health.",
 "p_selftreat": "Do not start TB or antibiotic medicines on your own. Incomplete or unsupervised treatment can cause drug-resistant TB.",
 "p_prior": "Tell the doctor about the earlier TB treatment: when, how long and which medicines. Drug-resistance testing matters more after earlier treatment.",
 "p_contacts": "People living with you, especially children under 5, older adults, and people with HIV or diabetes, should be assessed for TB.",
 "p_lower_symp": "A lower score does not rule out TB. Keep the symptoms in mind and return if they continue or worsen.",
 "p_none": "No action is needed now. Seek a check if cough lasts 2 weeks or more, or fever, night sweats or weight loss appear.",
 "p_cadvice": "A confirmatory test is the next step, not treatment. Treatment starts only after a doctor confirms TB.",
 "urgent": "Seek urgent care for coughing blood, severe breathlessness, chest pain that is getting worse, or confusion.",
},
"ur": {
 "head_Higher": "نتائج پھیپھڑوں کی ٹی بی کے زیادہ امکان کی طرف اشارہ کرتے ہیں۔ تصدیقی لیبارٹری ٹیسٹ بلا تاخیر کروائیں۔",
 "head_Intermediate": "نتائج پھیپھڑوں کی ٹی بی کے بارے میں واضح نہیں۔ مزید معائنہ اور تصدیقی ٹیسٹ کروائیں۔",
 "head_Lower": "اس جانچ کے مطابق پھیپھڑوں کی ٹی بی کا امکان کم ہے۔ اس کا مطلب یہ نہیں کہ ٹی بی ہے ہی نہیں۔",
 "basis_clin": "کلینیکل جانچ: {band}۔", "basis_xray": "سینے کا ایکسرے: {band}۔", "basis_both_same": "کلینیکل جانچ اور ایکسرے کا درجہ ایک ہی ہے۔",
 "basis_both_diff": "کلینیکل جانچ اور ایکسرے کا درجہ مختلف ہے؛ زیادہ درجہ مجموعی نتیجہ طے کرتا ہے اور فیصلہ تصدیقی ٹیسٹ سے ہوگا۔",
 "contrib": "اہم عوامل: {f}۔", "crp_high": "سی آر پی بڑھا ہوا ہے ({v} mg/L)، جو سوزش کی غیر مخصوص علامت ہے۔",
 "region": "ایکسرے کا اسکور زیادہ تر تصویر کے {v} {h} حصے سے طے ہوا (جیسا تصویر میں دکھایا گیا)۔ یہ دکھاتا ہے کہ ماڈل نے کہاں دیکھا؛ یہ کسی گھاؤ کی تشخیص نہیں۔",
 "v_upper": "اوپری", "v_mid": "درمیانی", "v_lower": "نچلے", "h_left": "بائیں", "h_centre": "مرکزی", "h_right": "دائیں",
 "q_small": "ایکسرے کی تصویر چھوٹی ہے، اس لیے پڑھائی کم قابل اعتماد ہو سکتی ہے۔", "q_dark": "ایکسرے کی تصویر بہت تاریک ہے۔", "q_bright": "ایکسرے کی تصویر بہت روشن ہے۔", "q_flat": "ایکسرے کی تصویر میں تضاد بہت کم ہے۔",
 "t_xpert": ("بلغم کا ایکسپرٹ MTB/RIF (الٹرا)", "چند گھنٹوں میں ٹی بی کے جراثیم اور رفیمپسن مزاحمت پکڑتا ہے؛ ٹی بی کی تصدیق یا تردید کا بنیادی ٹیسٹ۔"),
 "t_culture": ("بلغم کا کلچر اور دوائی کی حساسیت کا ٹیسٹ", "پہلے ٹی بی علاج ہو چکا ہو یا ایکسپرٹ مثبت یا غیر واضح ہو تو ضروری ہے؛ بتاتا ہے کون سی دوائیں کام کریں گی۔"),
 "t_cxr": ("سینے کا ایکسرے (جہاں دستیاب ہو کمپیوٹر کی مدد سے پڑھائی کے ساتھ)", "پھیپھڑوں کی تبدیلیاں دیکھتا ہے؛ یہ نتیجہ صرف علامات اور ٹیسٹوں پر مبنی ہے۔"),
 "t_radiologist": ("ریڈیالوجسٹ سے ایکسرے کا معائنہ", "نتیجے کی تصدیق کرتا ہے اور پھیپھڑوں کے دوسرے مسائل بھی دیکھتا ہے۔"),
 "t_retake": ("زیادہ واضح تصویر کے ساتھ ایکسرے دوبارہ کروائیں", "تصویر کا معیار پڑھائی کی قابل اعتمادی کو محدود کرتا ہے۔"),
 "t_hiv": ("ایچ آئی وی ٹیسٹ", "ایچ آئی وی ٹی بی کے خطرے اور علاج کو بدلتا ہے اور ٹی بی کی جانچ کا معیاری حصہ ہے۔"),
 "t_glucose": ("بلڈ گلوکوز یا HbA1c", "ذیابیطس ٹی بی کا خطرہ بڑھاتی ہے اور اس کا انتظام ضروری ہے؛ وزن میں کمی دونوں کی علامت ہو سکتی ہے۔"),
 "t_review": ("تقریباً 2 ہفتے بعد ڈاکٹر سے دوبارہ معائنہ", "اگر کھانسی، بخار، رات کا پسینہ یا وزن میں کمی جاری رہے تو کم اسکور کے باوجود ٹیسٹ ضروری ہے۔"),
 "p_cough": "کھانستے وقت منہ اور ناک ڈھانپیں، ٹشو استعمال کر کے محفوظ طریقے سے پھینکیں اور بعد میں ہاتھ دھوئیں۔",
 "p_vent": "کھڑکیاں کھلی اور کمرے ہوادار رکھیں؛ ٹی بی خارج ہونے تک مشترکہ بند کمرے میں سونے سے پرہیز کریں۔",
 "p_mask": "ٹی بی خارج ہونے تک دوسروں کے قریب اور صحت مراکز میں ماسک پہنیں۔",
 "p_crowd": "ٹیسٹ کا نتیجہ آنے تک بھیڑ والی بند جگہوں اور طویل مشترکہ سفر سے بچیں۔",
 "p_nutri": "توانائی اور پروٹین والی غذا کھائیں اور ہفتہ وار وزن کریں؛ مزید کمی ہو تو بتائیں۔",
 "p_smoke": "تمباکو نوشی اور دھوئیں سے بچیں؛ یہ کھانسی اور پھیپھڑوں کو بگاڑتے ہیں۔",
 "p_selftreat": "خود سے ٹی بی یا اینٹی بایوٹک دوائیں شروع نہ کریں۔ ادھورا یا بغیر نگرانی علاج ادویات کے خلاف مزاحم ٹی بی بنا سکتا ہے۔",
 "p_prior": "ڈاکٹر کو پہلے ٹی بی علاج کے بارے میں بتائیں: کب، کتنا عرصہ اور کون سی دوائیں۔ پہلے علاج کے بعد دوائی کی مزاحمت کا ٹیسٹ زیادہ اہم ہے۔",
 "p_contacts": "ساتھ رہنے والے افراد، خاص طور پر 5 سال سے کم بچے، بزرگ اور ایچ آئی وی یا ذیابیطس والے، کی ٹی بی کے لیے جانچ ہونی چاہیے۔",
 "p_lower_symp": "کم اسکور ٹی بی کو خارج نہیں کرتا۔ علامات کا دھیان رکھیں اور اگر جاری رہیں یا بڑھیں تو دوبارہ رجوع کریں۔",
 "p_none": "ابھی کسی کارروائی کی ضرورت نہیں۔ اگر کھانسی 2 ہفتے یا زیادہ رہے، یا بخار، رات کا پسینہ یا وزن میں کمی ہو تو معائنہ کروائیں۔",
 "p_cadvice": "اگلا قدم تصدیقی ٹیسٹ ہے، علاج نہیں۔ علاج صرف ڈاکٹر کی تصدیق کے بعد شروع ہوتا ہے۔",
 "urgent": "خون کی کھانسی، شدید سانس پھولنا، بڑھتا ہوا سینے کا درد یا الجھن ہو تو فوراً ایمرجنسی میں جائیں۔",
},
}
LV = {"Lower": 0, "Intermediate": 1, "Higher": 2}


def compose(a, lang="en", band_name=None, feat_name=None):
    """a: dict(overall, clinical (band or None), xray (dict with band/quality/peak or None), f (features), who_positive, cough_2w, reasons [(feature, effect)], crp).
    band_name(b) and feat_name(f) translate labels. Returns dict(impression=[...], tests=[(name, why)], precautions=[...], urgent=str)."""
    T = TX[lang]; bn = band_name or (lambda b: b); fn = feat_name or (lambda f: f)
    o = a["overall"]; clin = a.get("clinical"); xr = a.get("xray") or {}; xb = xr.get("band"); f = a.get("f") or {}
    sym = bool(a.get("who_positive") or a.get("cough_2w") or f.get("chestpain")); prior = bool(f.get("prior_tb")); weight = bool(f.get("weightlost")); cough = bool(f.get("cough"))
    imp = [T["head_" + o]]
    if clin: imp.append(T["basis_clin"].format(band=bn(clin)))
    if xb: imp.append(T["basis_xray"].format(band=bn(xb)))
    if clin and xb: imp.append(T["basis_both_same"] if clin == xb else T["basis_both_diff"])
    pos = [fn(n) for n, v in a.get("reasons", []) if v > 0][:3]
    if clin and pos and clin != "Lower": imp.append(T["contrib"].format(f="، ".join(pos) if lang == "ur" else ", ".join(pos)))
    crp = a.get("crp")
    if crp is not None and crp >= 10: imp.append(T["crp_high"].format(v=round(crp, 1)))
    pk = xr.get("peak")
    if xb and xb != "Lower" and pk:
        g = xr.get("grid", 8); r, c = pk; v = "v_upper" if r < g / 3 else "v_mid" if r < 2 * g / 3 else "v_lower"; h = "h_left" if c < g / 3 else "h_centre" if c < 2 * g / 3 else "h_right"
        imp.append(T["region"].format(v=T[v], h=T[h]))
    for q in xr.get("quality", []): imp.append(T[q])
    tests = []
    add = lambda k: tests.append(T[k])
    if o != "Lower" or sym: add("t_xpert")
    if o == "Higher" or (prior and o != "Lower"): add("t_culture")
    if clin and not xb and (o != "Lower" or sym): add("t_cxr")
    if xb in ("Intermediate", "Higher"): add("t_radiologist")
    if xr.get("quality"): add("t_retake")
    if o != "Lower": add("t_hiv")
    if o == "Higher" or (o == "Intermediate" and weight): add("t_glucose")
    if o == "Lower" and sym: add("t_review")
    pr = []
    P = lambda k: pr.append(T[k])
    if o == "Higher": P("p_cadvice")
    if cough or o == "Higher": P("p_cough")
    if o != "Lower" and cough: P("p_vent")
    if o == "Higher" and (cough or xb == "Higher"): P("p_mask")
    if o == "Higher": P("p_crowd")
    if weight: P("p_nutri")
    if cough: P("p_smoke")
    if o != "Lower": P("p_selftreat")
    if prior: P("p_prior")
    if o == "Higher": P("p_contacts")
    if o == "Lower": P("p_lower_symp" if sym else "p_none")
    return dict(impression=imp, tests=tests, precautions=pr, urgent=T["urgent"] if (o != "Lower" or f.get("chestpain") or cough) else "")


# ---- trend, follow-up date, cause of TB, patient factors
X = {
"en": {
 "tr_improving": "Compared with the visit on {d} ({prev}), the screening score is lower. This is encouraging but does not confirm recovery; continue the clinician's plan.",
 "tr_similar": "Compared with the visit on {d} ({prev}), the screening score is about the same.",
 "tr_worsening": "Compared with the visit on {d} ({prev}), the screening score is higher. Please see a clinician soon.",
 "tr_sym": "Symptoms entered: {a} at the earlier visit, {b} now.", "tr_nocomp": "The two visits used different inputs (for example an X-ray or CRP was added), so the comparison is approximate.",
 "tr_tb": "Laboratory result recorded at the earlier visit: TB confirmed.", "tr_not": "Laboratory result recorded at the earlier visit: TB not found.",
 "tr_caveat": "A screening score is not a measure of how the disease is progressing; confirm with the clinician and laboratory tests.",
 "fu_Higher": "Next check: within 3 days (by {d}), together with the confirmatory test.", "fu_Intermediate": "Next check: within 1 week (by {d}), or sooner if symptoms worsen.",
 "fu_Lower_sym": "Next check: in about 2 weeks (by {d}) if symptoms continue.", "fu_Lower": "No scheduled check is needed. Return if symptoms appear.",
 "about_title": "About TB: cause and spread",
 "about": ["TB is caused by a bacterium, Mycobacterium tuberculosis, which usually infects the lungs.",
           "It spreads through the air when a person with TB of the lungs coughs, sneezes or speaks. It does not spread by touch, food, shared plates or bedding.",
           "Many people who breathe in the bacteria never become ill because the immune system keeps them in check (latent infection). TB disease develops when the body can no longer contain the bacteria.",
           "Things that raise the chance of TB disease: close contact with an infectious person, HIV infection, diabetes, undernutrition or low body weight, smoking, heavy alcohol use, crowded or poorly ventilated places, earlier TB, and medicines that weaken the immune system.",
           "TB is curable. Treatment usually takes 6 months and every dose matters; stopping early can cause drug-resistant TB."],
 "rf_title": "Points noted for this patient", "rf_none": "None of the entered items is a known extra risk factor for TB disease.",
 "rf_prior": "Earlier TB treatment: a person who had TB before has a higher chance of TB coming back or of drug resistance.", "rf_weight": "Weight loss can be a sign of TB and also of undernutrition or diabetes; both are worth checking.",
 "rf_cough": "Cough for 2 weeks or more is the main reason to test for TB.", "rf_crp": "Raised CRP shows inflammation; it is not specific to TB.", "rf_sweats": "Night sweats are a common TB symptom.",
 "rf_caveat": "This tool cannot tell how or when this person was infected.",
},
"ur": {
 "tr_improving": "{d} کی وزٹ ({prev}) کے مقابلے میں جانچ کا اسکور کم ہے۔ یہ حوصلہ افزا ہے مگر صحت یابی کی تصدیق نہیں؛ ڈاکٹر کے منصوبے پر عمل جاری رکھیں۔",
 "tr_similar": "{d} کی وزٹ ({prev}) کے مقابلے میں جانچ کا اسکور تقریباً وہی ہے۔",
 "tr_worsening": "{d} کی وزٹ ({prev}) کے مقابلے میں جانچ کا اسکور زیادہ ہے۔ براہ کرم جلد ڈاکٹر کو دکھائیں۔",
 "tr_sym": "درج علامات: پچھلی وزٹ پر {a}، اب {b}۔", "tr_nocomp": "دونوں وزٹ میں مختلف معلومات استعمال ہوئیں (مثلاً ایکسرے یا سی آر پی شامل ہوا)، اس لیے موازنہ تقریبی ہے۔",
 "tr_tb": "پچھلی وزٹ پر درج لیبارٹری نتیجہ: ٹی بی کی تصدیق ہوئی۔", "tr_not": "پچھلی وزٹ پر درج لیبارٹری نتیجہ: ٹی بی نہیں ملی۔",
 "tr_caveat": "جانچ کا اسکور بیماری کی پیش رفت کا پیمانہ نہیں؛ ڈاکٹر اور لیبارٹری ٹیسٹ سے تصدیق کریں۔",
 "fu_Higher": "اگلا معائنہ: 3 دن کے اندر ({d} تک)، تصدیقی ٹیسٹ کے ساتھ۔", "fu_Intermediate": "اگلا معائنہ: 1 ہفتے کے اندر ({d} تک)، علامات بڑھیں تو جلد۔",
 "fu_Lower_sym": "اگلا معائنہ: تقریباً 2 ہفتے بعد ({d} تک) اگر علامات جاری رہیں۔", "fu_Lower": "کسی مقررہ معائنے کی ضرورت نہیں۔ علامات ظاہر ہوں تو رجوع کریں۔",
 "about_title": "ٹی بی کے بارے میں: وجہ اور پھیلاؤ",
 "about": ["ٹی بی ایک جرثومے مائیکوبیکٹیریم ٹیوبرکلوسس سے ہوتی ہے جو عموماً پھیپھڑوں کو متاثر کرتا ہے۔",
           "یہ ہوا کے ذریعے پھیلتی ہے جب پھیپھڑوں کی ٹی بی والا شخص کھانستا، چھینکتا یا بولتا ہے۔ یہ چھونے، کھانے، مشترکہ برتن یا بستر سے نہیں پھیلتی۔",
           "بہت سے لوگ جو یہ جرثومے سانس میں لیتے ہیں بیمار نہیں ہوتے کیونکہ مدافعتی نظام انہیں قابو میں رکھتا ہے (خفیہ انفیکشن)۔ ٹی بی کی بیماری تب بنتی ہے جب جسم انہیں قابو میں نہ رکھ سکے۔",
           "ٹی بی کی بیماری کا امکان بڑھانے والی باتیں: متعدی شخص سے قریبی رابطہ، ایچ آئی وی، ذیابیطس، غذائی کمی یا کم وزن، تمباکو نوشی، زیادہ شراب نوشی، بھیڑ والی یا کم ہوادار جگہیں، پہلے ٹی بی ہونا، اور مدافعت کم کرنے والی دوائیں۔",
           "ٹی بی قابل علاج ہے۔ علاج عموماً 6 ماہ کا ہوتا ہے اور ہر خوراک اہم ہے؛ جلدی چھوڑنے سے دوائی کے خلاف مزاحم ٹی بی بن سکتی ہے۔"],
 "rf_title": "اس مریض کے بارے میں قابل ذکر نکات", "rf_none": "درج کردہ معلومات میں ٹی بی کی بیماری کا کوئی معروف اضافی خطرہ نہیں۔",
 "rf_prior": "پہلے ٹی بی کا علاج: جسے پہلے ٹی بی ہو چکی ہو اس میں دوبارہ ہونے یا دوائی کے خلاف مزاحمت کا امکان زیادہ ہوتا ہے۔", "rf_weight": "وزن میں کمی ٹی بی کی علامت بھی ہو سکتی ہے اور غذائی کمی یا ذیابیطس کی بھی؛ دونوں کی جانچ مفید ہے۔",
 "rf_cough": "2 ہفتے یا زیادہ کھانسی ٹی بی کے ٹیسٹ کی اہم ترین وجہ ہے۔", "rf_crp": "سی آر پی کا بڑھنا سوزش ظاہر کرتا ہے؛ یہ ٹی بی کے لیے مخصوص نہیں۔", "rf_sweats": "رات کا پسینہ ٹی بی کی عام علامت ہے۔",
 "rf_caveat": "یہ ٹول نہیں بتا سکتا کہ اس شخص کو انفیکشن کیسے یا کب ہوا۔",
},
}


def _date(days):
    import datetime as dt
    return (dt.date.today() + dt.timedelta(days=days)).isoformat()


def followup(overall, symptomatic, lang="en"):
    T = X[lang]
    if overall == "Higher": return T["fu_Higher"].format(d=_date(3))
    if overall == "Intermediate": return T["fu_Intermediate"].format(d=_date(7))
    return T["fu_Lower_sym"].format(d=_date(14)) if symptomatic else T["fu_Lower"]


def about(lang="en"): return dict(title=X[lang]["about_title"], paragraphs=X[lang]["about"])


def trend_lines(tr, lang="en", band_name=None):
    if not tr: return []
    T = X[lang]; bn = band_name or (lambda b: b); out = [T["tr_" + tr["label"]].format(d=tr["prev_ts"][:10], prev=bn(tr["prev_overall"]))]
    out.append(T["tr_sym"].format(a=tr["symptoms_prev"], b=tr["symptoms_now"]))
    if not tr["comparable"]: out.append(T["tr_nocomp"])
    if tr.get("prev_outcome") == "tb": out.append(T["tr_tb"])
    if tr.get("prev_outcome") == "not_tb": out.append(T["tr_not"])
    out.append(T["tr_caveat"]); return out


def patient_factors(a, lang="en"):
    T = X[lang]; f = a.get("f") or {}; out = []
    if f.get("prior_tb"): out.append(T["rf_prior"])
    if f.get("cough") and f.get("cough_dur", 0) >= 3: out.append(T["rf_cough"])
    if f.get("weightlost"): out.append(T["rf_weight"])
    if f.get("nightsweats"): out.append(T["rf_sweats"])
    if a.get("crp") is not None and a["crp"] >= 10: out.append(T["rf_crp"])
    return (out or [T["rf_none"]]) + [T["rf_caveat"]]


# ---- supporting findings (rule-based notes)
SX = {
"en": {"xpert_pos": "Xpert detected TB bacteria. This confirms bacteria in the sample: start the TB service pathway today.", "afb_pos": "The sputum smear shows acid-fast bacilli. Refer for TB treatment assessment now.",
 "culture_pos": "The culture grew mycobacteria. Refer for TB treatment assessment now.", "hemoptysis": "Coughing up blood needs a doctor's assessment soon.",
 "infection_test": "A positive skin or blood infection test shows past exposure; it cannot tell active disease from latent infection.", "hiv_symptoms": "HIV with symptoms: TB testing is a priority.",
 "multi_risk": "Several TB risk factors together with symptoms raise the level of concern.", "contact_symptoms": "Symptoms after contact with a person with TB: get tested.",
 "xpert_neg": "A negative Xpert does not completely rule out TB, especially if symptoms continue.", "afb_neg": "A negative smear does not rule out TB; many people with TB have a negative smear.", "culture_neg": "A negative culture lowers but does not remove the chance of TB, particularly if the culture was early.",
 "esr_high": "ESR is raised (inflammation, not specific to TB).", "hb_low": "Haemoglobin is low (anaemia is common in long illness).", "wbc_high": "White cell count is raised.", "bmi_low": "Low body weight raises the chance of TB disease.",
 "diabetes": "Diabetes raises the chance of TB disease; keep sugar controlled.", "smoker": "Smoking raises the chance of TB and slows recovery.", "contact": "Close contact with a person with TB raises the chance of infection.", "hiv": "HIV infection raises the chance of TB disease.",
 "u_rif_res": "Rifampicin resistance was found. Specialist drug-resistant TB care is needed.", "u_hemoptysis": "Coughing up blood: go to a health facility today if it is more than a streak."},
"ur": {"xpert_pos": "ایکسپرٹ میں ٹی بی کے جراثیم ملے۔ نمونے میں جراثیم کی تصدیق ہوئی: آج ہی ٹی بی سروس سے رجوع کریں۔", "afb_pos": "بلغم کی سمیئر میں تیزاب مزاحم جراثیم ملے۔ علاج کے جائزے کے لیے فوری رجوع کریں۔",
 "culture_pos": "کلچر میں مائیکوبیکٹیریا اگے۔ علاج کے جائزے کے لیے فوری رجوع کریں۔", "hemoptysis": "کھانسی میں خون آنے پر جلد ڈاکٹر سے معائنہ کرائیں۔",
 "infection_test": "جلد یا خون کا مثبت انفیکشن ٹیسٹ پچھلے رابطے کو ظاہر کرتا ہے؛ یہ فعال بیماری اور خفیہ انفیکشن میں فرق نہیں بتا سکتا۔", "hiv_symptoms": "ایچ آئی وی کے ساتھ علامات: ٹی بی ٹیسٹ ترجیح ہے۔",
 "multi_risk": "کئی خطرے کے عوامل علامات کے ساتھ تشویش کی سطح بڑھاتے ہیں۔", "contact_symptoms": "ٹی بی کے مریض سے رابطے کے بعد علامات: ٹیسٹ کرائیں۔",
 "xpert_neg": "منفی ایکسپرٹ ٹی بی کو مکمل طور پر رد نہیں کرتا، خاص طور پر اگر علامات جاری ہوں۔", "afb_neg": "منفی سمیئر ٹی بی کو رد نہیں کرتی؛ ٹی بی کے بہت سے مریضوں کی سمیئر منفی ہوتی ہے۔", "culture_neg": "منفی کلچر امکان کم کرتا ہے مگر ختم نہیں کرتا، خاص طور پر اگر کلچر جلدی کیا گیا ہو۔",
 "esr_high": "ای ایس آر بڑھا ہوا ہے (سوزش، ٹی بی کے لیے مخصوص نہیں)۔", "hb_low": "ہیموگلوبن کم ہے (طویل بیماری میں خون کی کمی عام ہے)۔", "wbc_high": "سفید خلیات کی تعداد بڑھی ہوئی ہے۔", "bmi_low": "کم وزن ٹی بی کی بیماری کا امکان بڑھاتا ہے۔",
 "diabetes": "ذیابیطس ٹی بی کا امکان بڑھاتی ہے؛ شوگر قابو میں رکھیں۔", "smoker": "تمباکو نوشی ٹی بی کا امکان بڑھاتی اور صحت یابی سست کرتی ہے۔", "contact": "ٹی بی کے مریض سے قریبی رابطہ انفیکشن کا امکان بڑھاتا ہے۔", "hiv": "ایچ آئی وی انفیکشن ٹی بی کی بیماری کا امکان بڑھاتا ہے۔",
 "u_rif_res": "رائفیمپیسن کے خلاف مزاحمت ملی۔ دوائی مزاحم ٹی بی کی ماہرانہ دیکھ بھال ضروری ہے۔", "u_hemoptysis": "کھانسی میں خون: اگر صرف لکیر سے زیادہ ہو تو آج ہی صحت مرکز جائیں۔"},
}


def support_notes(assessment, lang="en"):
    return [dict(kind=k, text=SX[lang][n]) for n, k in assessment["notes"]], [SX[lang]["u_" + u] for u in assessment["urgent"]]
