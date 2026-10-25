"""Train the TB-Screen risk models on the open TREATS CRP dataset (LSHTM Data Compass, CC BY 4.0).

Four models, depending on which inputs the user has:
  A        symptoms + sex + age group + TB history
  A+CRP    + point-of-care CRP
  A+CAD    + chest X-ray CAD score (CAD4TB)
  A+CRP+CAD
Sign-constrained logistic regression: symptoms, cough duration, TB history, CRP and CAD cannot lower the risk (scripts/constrained.py).
A deep network and gradient boosting were tested and were not better; see model/benchmark.csv (also the unconstrained fit).
Validation = train on one country, test on the other (Zambia <-> South Africa). Risk bands are set from
cross-validated (out-of-fold) predictions, never from the fit on the training rows.
"""
import json, sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from constrained import ConLR
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "CRP_dataset_open.csv"
SYMP = ["cough", "fever", "chestpain", "nightsweats", "weightlost"]
DUR = {s: s + "_dur" for s in SYMP}


def build(df):
    """Feature table. Duration codes 0-5 as in the codebook (0 none, 1 <1wk, 2 7-13d, 3 14-27d, 4 >=4wk<3mo, 5 >=3mo)."""
    F = pd.DataFrame(index=df.index)
    for s in SYMP:
        F[s] = (df["symp_" + s] == 1).astype(int)
    F["cough_dur"] = df["symp_cough_weeks"].where(F.cough == 1, 0).clip(0, 5)
    F["n_symptoms"] = F[SYMP].sum(1)
    F["male"] = (df.sex == "M").astype(int)
    F["age_group"] = df.age_group.clip(1, 5)                       # 1=15-24 ... 5=55+
    F["prior_tb"] = (df.tb_history == "history of tb treatment").astype(int)
    crp = df.crp_value.where(df.crp_value.between(0, 900))
    F["crp_log2"] = np.log2(crp.clip(lower=4))                     # 4 is the device floor
    cad = df.CAD_score.where(df.CAD_score >= 0)
    F["cad"] = cad / 10.0                                          # per 10 points
    return F

A = ["cough", "fever", "chestpain", "nightsweats", "weightlost", "cough_dur", "male", "age_group", "prior_tb"]
TIERS = {"A": A, "A+CRP": A + ["crp_log2"], "A+CAD": A + ["cad"], "A+CRP+CAD": A + ["crp_log2", "cad"]}


def fit_lr(X, y, C, cols=None, constrain=True): return ConLR(cols, C, constrain).fit(X, y)


def pick_C(X, y, cols, seed=0, constrain=True):
    """Choose the regularisation by repeated CV inside the training data only."""
    best, bc = -1, 0.3
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=seed)
    for C in [0.03, 0.1, 0.3, 1.0]:
        a = []
        for tr, te in cv.split(X, y):
            a.append(roc_auc_score(y[te], fit_lr(X[tr], y[tr], C, cols, constrain).predict_proba(X[te])[:, 1]))
        if np.mean(a) > best: best, bc = np.mean(a), C
    return bc


def boot_ci(y, p, n=1000, seed=0):
    r = np.random.RandomState(seed); a = []
    for _ in range(n):
        i = r.randint(0, len(y), len(y))
        if len(np.unique(y[i])) > 1: a.append(roc_auc_score(y[i], p[i]))
    return np.percentile(a, [2.5, 97.5])


def main():
    c = pd.read_csv(CSV, low_memory=False)
    d = c[c.Xpertculture.notna()].copy(); F = build(d); y_all = d.Xpertculture.astype(int).values; ctry = d.country.values
    bench, card, models = [], {}, {}
    for tier, cols in TIERS.items():
        ok = F[cols].notna().all(1).values
        X, y, g = F.loc[ok, cols].values.astype(float), y_all[ok], ctry[ok]
        row = dict(tier=tier, n=int(ok.sum()), tb=int(y.sum()))
        # ---- validation on an unseen country (model + C chosen inside the training country only)
        pooled_p, pooled_y, free_p = [], [], []
        for test in ["SA", "Zambia"]:
            tr, te = g != test, g == test
            C = pick_C(X[tr], y[tr], cols); m = fit_lr(X[tr], y[tr], C, cols); p = m.predict_proba(X[te])[:, 1]
            Cf = pick_C(X[tr], y[tr], cols, constrain=False); free_p.append(fit_lr(X[tr], y[tr], Cf, cols, False).predict_proba(X[te])[:, 1])
            row["auc_" + test] = roc_auc_score(y[te], p); pooled_p.append(p); pooled_y.append(y[te])
            for nm, mk in [("MLP", lambda: make_pipeline(StandardScaler(), MLPClassifier((32, 16), alpha=1e-2, max_iter=600, early_stopping=True, random_state=0))),
                           ("GradBoost", lambda: HistGradientBoostingClassifier(max_depth=3, learning_rate=.05, max_iter=150))]:
                row[f"{nm}_auc_{test}"] = roc_auc_score(y[te], mk().fit(X[tr], y[tr]).predict_proba(X[te])[:, 1])
        py, pp = np.concatenate(pooled_y), np.concatenate(pooled_p)
        lo, hi = boot_ci(py, pp); row.update(auc_pooled=roc_auc_score(py, pp), auc_lo=lo, auc_hi=hi, unconstrained_auc_pooled=roc_auc_score(py, np.concatenate(free_p)))
        bench.append(row)
        # ---- final model on both countries; bands from out-of-fold predictions
        C = pick_C(X, y, cols, seed=1); oof = np.zeros(len(y)); cnt = np.zeros(len(y))
        for tr, te in RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=3).split(X, y):
            oof[te] += fit_lr(X[tr], y[tr], C, cols).predict_proba(X[te])[:, 1]; cnt[te] += 1
        oof /= cnt
        pos = np.sort(oof[y == 1]); t_low = float(pos[int(np.floor(0.10 * len(pos)))])        # 90% sensitivity
        neg = np.sort(oof[y == 0]); t_high = float(neg[int(np.floor(0.80 * len(neg)))])       # 80% specificity
        t_high = max(t_high, t_low)
        band = np.where(oof < t_low, 0, np.where(oof < t_high, 1, 2))
        bands = []
        for b, nm in enumerate(["Lower", "Intermediate", "Higher"]):
            s = band == b; bands.append(dict(band=nm, n=int(s.sum()), share=float(s.mean()), tb_rate=float(y[s].mean()) if s.sum() else None))
        call = oof >= t_low
        perf = dict(sens=float(call[y == 1].mean()), spec=float((~call)[y == 0].mean()), ppv=float(y[call].mean()), npv=float(1 - y[~call].mean()), prevalence=float(y.mean()))
        m = fit_lr(X, y, C, cols); coef = m.coef_ / m.scale_; intercept = float(m.intercept_ - np.sum(m.coef_ * m.mean_ / m.scale_))
        models[tier] = dict(features=cols, coef=[float(v) for v in coef], intercept=intercept, C=C, n_train=int(len(y)), n_tb=int(y.sum()),
                            threshold_low=t_low, threshold_high=t_high, bands=bands, oof_performance_at_low=perf,
                            feature_mean=[float(v) for v in X.mean(0)], feature_min=[float(v) for v in X.min(0)], feature_max=[float(v) for v in X.max(0)],
                            auc_unseen_country_pooled=float(row["auc_pooled"]), auc_ci=[float(lo), float(hi)], auc_SA=float(row["auc_SA"]), auc_Zambia=float(row["auc_Zambia"]))
        print(tier, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    out = dict(version="1.1.0", constraint="symptoms, cough duration, TB history, CRP and CAD cannot lower the risk (sign-constrained logistic regression)", dataset="TREATS community TB survey, open data (Zambia + South Africa), LSHTM Data Compass, doi:10.17037/DATA.00005150, CC BY 4.0",
               population="Adults 15+ who were eligible for sputum testing (TB-suggestive symptoms or chest X-ray CAD score >= 40). Reference standard: Xpert Ultra or culture.",
               symptoms_scale="cough_dur: 0 none, 1 <1 week, 2 7-13 days, 3 14-27 days, 4 >=4 weeks and <3 months, 5 >=3 months",
               age_groups={"1": "15-24", "2": "25-34", "3": "35-44", "4": "45-54", "5": "55+"}, crp_note="Point-of-care CRP in the study's own units (cut-off 4 in the open data; the codebook gives no unit for crp_value). Values below 4 are treated as 4.",
               models=models)
    (ROOT / "model" / "tb_screen_model.json").write_text(json.dumps(out, indent=1))
    pd.DataFrame(bench).round(3).to_csv(ROOT / "model" / "benchmark.csv", index=False)
    print("saved")

if __name__ == "__main__": main()
