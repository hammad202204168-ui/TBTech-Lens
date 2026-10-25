# Will this work in my setting?

**Honest answer: it is a reasonable starting design, but it is only as good as its check in your own population.** Any screening model drops in accuracy when the people, the lab methods or the X-ray equipment differ from the training data. TB-Screen was trained on adults in South Africa and Zambia (open TREATS CRP dataset) and has been checked on a country it had not seen, which is the best test available without local data.

What transfers well
- The inputs (cough, fever, night sweats, weight loss, age, sex, TB history, CRP, chest X-ray score or image) are available in most clinics. Computer-aided chest X-ray reading is an accepted screening approach.
- The model does not use HIV status, so it can be used where HIV is common or rare, but HIV prevalence in the training data is high and shifts the baseline risk.
- English and Urdu are built in; all wording is in `tbscreen/i18n.py` and can be translated.

What may not transfer
- Different TB patterns (diabetes, malnutrition, extra-pulmonary TB), different CRP and X-ray practice, and a different mix of people who get tested.
- Only 117 TB cases in the symptom/CRP training data, so the accuracy interval is wide.
- ESR, HIV, diabetes and blood counts are not used because the open data lacks them.

What to do before real use
1. Run 100 or more people with known Xpert/culture results through *Clinic tools -> Check against Xpert/culture* (at least 20 TB and 20 non-TB).
2. If the AUC is much lower than in the README table, or too much TB falls into *Lower*, do not use it for triage; retrain with `scripts/add_tier.py` on local data.
3. Get ethics, clinical and (for patient use) regulatory review.

Suggested pilot: run the app in parallel to the normal pathway (no change to patient care) and compare its groups with Xpert results.
