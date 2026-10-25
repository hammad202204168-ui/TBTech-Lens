# 1,200 simulated users

**These are simulated people, not real users.** Covariates (age group, sex, symptoms, CRP, CAD) were resampled from the real 9,588-person training data; extra personas were added that make typical mistakes. They test the software under load and bad input. They cannot tell you whether a nurse in your clinic understands the screen. Reproduce: `python scripts/simulate_users.py` (results in `docs/simulation_results.json`).

| Persona | n | What happened | Difficulty found |
|---|---|---|---|
| Typical (symptoms only) | 700 | 104 Lower / 427 Intermediate / 169 Higher | 61% land in "Intermediate": the symptom-only tier (AUC 0.58) separates poorly, so most people get a middle answer that does not help decisions |
| With CRP | 100 | all scored with the CRP tier | none |
| CRP + CAD | 100 | all scored with the richest tier | none |
| CAD typed as a fraction (0.72) | 100 | all 100 flagged with a warning; all 100 came out "Lower" | Risk under-estimated by 6.3 percentage points on average. The warning works, but a hurried user may ignore it |
| CRP typed in mg/dL | 60 | scored normally, no warning | **Undetectable**: a mg/dL value looks like a valid low mg/L value. Needs a unit label on the field |
| No symptoms at all | 60 | 60 of 60 Lower, none told to get assessed | Earlier version labelled 50 of 60 as not Lower (12 Higher) from age and sex alone; fixed by reporting symptom-free people on the symptom-only tier as Lower with a 'no action needed, return if symptoms appear' message |
| Wrong type ("N/A", "12,5", "1e999") | 40 | all rejected with HTTP 422 | Error text is technical; the app should show a plain sentence next to the field |
| Impossible age (0, 6, -1, 99) | 40 | all rejected with HTTP 422 | Same |
| Load | 1,200 requests, 16 at once | 0 server errors, all 1,120 valid requests saved, 227 requests/s, p50 55 ms, p95 140 ms, p99 365 ms | In-process test; a real network, phone and hosting will be slower |

## Difficulties users will face (ranked)
1. **Most answers are "Intermediate"** with the symptom-only tier. The app is honest, but it is not very useful until CRP or CAD is added.
2. **Unit and scale mistakes** (CAD 0.72 vs 72, CRP mg/dL vs mg/L). Only the CAD one is caught.
3. ~~Symptom-free people saw a risk band~~ fixed in 1.1.0.
4. **Technical error messages.**
5. Not tested at all: slow phones, patchy internet, low literacy, Urdu wording, screen readers, shared devices, power cuts.

## What a real test needs
10 to 20 real users (nurses, lady health workers, a doctor) doing 5 realistic cases each while someone watches and takes notes, in Urdu and English, on their own phones.
