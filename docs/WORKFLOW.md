# Workflow: from data to app

1. **Data.** The open TREATS dataset (`data/CRP_dataset_open.csv`, 9,588 adults, Zambia and South Africa). Only people with a reference result (Xpert Ultra or culture) can be used: 1,777, of whom 117 have TB. The rest were never sent for a sputum test, so their TB status is unknown. They are **not** treated as negatives, because that would inflate the accuracy.
2. **Inputs (features).** Taken from what a clinic can really ask or measure: five symptoms (cough, fever, chest pain, night sweats, weight loss), how long the cough has lasted, sex, age group, earlier TB treatment, point-of-care CRP (log2, floor 4) and the chest X-ray CAD score (per 10 points). HIV and blood counts are not in the open file, so they are not used.
3. **Four models (tiers)** are trained, one for each combination of optional inputs, so that nobody has to enter a value they do not have. The app picks the richest tier whose inputs are all present.
4. **Honest test.** For each tier: train on one country, test on the other (Zambia <-> South Africa), and pool. The regularisation strength is chosen by cross-validation inside the training country only. AUC confidence intervals come from 1,000 bootstrap resamples.
5. **Other models and features were tried** (`scripts/explore.py`, results in `model/model_search.csv`): logistic with L1 or L2, gradient boosting, a blend, small neural networks, spline-like terms, symptom counts, durations, interactions. None beat the plain logistic by more than 0.005 AUC, which is noise. So the simple model is used: it is also exact for SHAP, easy to audit and runs on a phone.
6. **Risk groups.** From cross-validated predictions, never from the training fit: *Lower* = below the cut-off that catches 90% of TB; *Higher* = above the cut-off that keeps 80% of non-TB below it; *Intermediate* in between. The app also shows how many of 100 people in the group had TB in the study.
7. **Explanation.** For a linear model, SHAP values are `coefficient x (value - average value)`. This was checked against the `shap` library (identical to 1e-9) in the tests. The chart shows what moved the result.
8. **Safety rules.** A person with any WHO symptom is always told to get a laboratory test, whatever the group. A lower group is never described as "no TB". People under 15 or already on TB treatment get no score.
9. **Backend.** `api/main.py` exposes the same engine over REST. Screenings can be saved anonymously (no names) and Xpert/culture results added later, which feeds the *local validation* page.
10. **Local validation and retraining.** `Clinic tools -> Check against Xpert/culture` compares scores with your own results. `scripts/add_tier.py` trains a new tier from your own data.

## Re-run everything
```bash
python scripts/train.py            # trains the 4 tiers, writes model/tb_screen_model.json and model/benchmark.csv
python scripts/explore.py          # the model/feature search (about a minute)
pytest
```
