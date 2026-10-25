# What to improve next (in priority order)

## Must do before any real use
1. **Validate in your own population.** The model was trained on South Africa and Zambia. Collect 300 to 500 locally tested people (Xpert result as the label) and run Clinic tools > Local validation. If AUC is below about 0.65, retrain with `scripts/add_tier.py`.
2. **Ethics approval and clinical sign-off** before patients see it; add a clinician-reviewed Urdu translation.
3. **Hosting and privacy:** HTTPS, set `TBSCREEN_API_KEY` and `TBSCREEN_STAFF_PIN`, backups, no names or phone numbers (only reference codes).

## Model
4. Only 117 TB cases: confidence intervals are wide. More local data is the single biggest gain.
5. Add a cohort with real-world labels for symptom-free people; today the model cannot say much about them.
6. Add X-ray: train with `scripts/train_xray.py` on your local data, check the shortcut warning, then retrain a tier with `xray_prob`.
7. Calibrate again on local data (risk bands are from South Africa and Zambia).

## App
8. Unit label and range hint on CRP (mg/L) and CAD (0 to 100); plain-language error messages.
9. Hide the band for symptom-free people in tier A, or show "no symptoms reported" instead.
10. Urdu PDF (needs a text-shaping library), WhatsApp share, offline mode.
11. User accounts with roles instead of one staff PIN; audit log.
12. Move SQLite to PostgreSQL when more than one clinic writes at once.

## Engineering
13. Run Playwright UI tests in CI; add load tests against a deployed server; dependency scanning.
14. Third-party security review.
