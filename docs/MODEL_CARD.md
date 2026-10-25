# Model card: TB-Screen v1.0.0

- **Purpose:** rank adults (15+) who are being considered for TB testing by likelihood of TB. Not a diagnosis.
- **Model:** logistic regression, four tiers (symptoms; + CRP; + chest X-ray CAD score; + both). Coefficients are in `model/tb_screen_model.json`.
- **Training data:** TREATS community survey open data (Zambia, South Africa), 1,777 adults with Xpert/culture results, 117 TB. CC BY 4.0.
- **Reference standard:** Xpert Ultra or culture positive.
- **Validation:** trained on one country, tested on the other; bootstrap 95% CI. See the README table.
- **Risk groups:** from cross-validated predictions (90% sensitivity cut-off; 80% specificity cut-off). In the best tier: Lower 1.3 TB per 100, Intermediate 3.9, Higher 17.5.
- **Known limits:** 117 cases; two African countries; selected population (people sent for sputum testing); no HIV, CBC, ESR, diabetes; not validated outside the two training countries; coefficients for some symptoms (for example cough) look unusual because everyone in the labelled set was selected for TB-like symptoms or an abnormal X-ray.
- **Not for:** children, people on TB treatment, diagnosis, deciding to withhold testing.
