# Changelog

## 3.0.0
- New name: TBTech Lens (set another with the APP_NAME environment variable).
- Every saved visit gets a report number (TBL-year-id-check letter) printed on the PDF; typing it in Records, or uploading the PDF again, finds the saved record.
- Patient records: visits saved under a reference code (age, sex, symptoms, results; never names, phone or ID numbers, never the X-ray picture); trend against the last visit (improving / similar / worsening score), follow-up date, laboratory outcome entry, delete and CSV export, optional PIN (TBSCREEN_PIN).
- Baby-lungs mascot that changes with the result, in the page and in the PDF; brighter theme, animated header and result motion.
- PDF report in English, Urdu or both; cause and spread of TB, patient-specific points, SHAP chart in plain language, trend chart, follow-up.
- Upload a lab or clinic report (PDF, photo, text): values are read, filled into the form and shown with the line they came from; nothing is stored.
- More inputs as transparent rules (not model-trained): extra symptoms, HIV, diabetes, contact, smoking, BMI, ESR, WBC, Hb, Xpert, smear, culture, IGRA, skin test. They can raise the level, never lower it.
- Clinical model retrained with sign constraints (symptoms, CRP, CAD cannot lower risk).
## 1.0.0
- Four model tiers (symptoms; +CRP; +CAD; +CRP+CAD), exact linear SHAP explanations, FastAPI backend, SQLite log, local validation, English/Urdu Streamlit app, X-ray module slot, `add_tier.py` retraining.
- Break-it test round (see docs/BREAK_REPORT.md): strict yes/no parsing, input clipping, CAD-scale warning, model-file validation, API field/size limits, CSV formula neutralisation, age in years for batch files.

## 1.1.0
- New web page (brown/gold theme, animated 3D result dial, English/Urdu) with three modes: clinical, chest X-ray, both.
- Result-specific impression, suggested tests and precautions; PDF report with SHAP chart, X-ray map and advice.
- X-ray module: occlusion map, picture-quality check, gauge position. `train_xray.py`: activation sweep, ResNet-18, held-out sources/clusters.
- Symptom-free people with only demographics are reported as Lower (no symptom, nothing to screen on).
- Neutral wording: no country or training-data statements on screen. Streamlit UI retired.
