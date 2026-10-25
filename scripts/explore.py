"""Model/feature search. Selection uses the mean of the two leave-one-country-out AUCs (SA<->Zambia); each fit is repeated for stability."""
import sys, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "scripts")
import numpy as np, pandas as pd
from train import build, CSV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import roc_auc_score

c = pd.read_csv(CSV, low_memory=False); d = c[c.Xpertculture.notna()].copy(); y_all = d.Xpertculture.astype(int).values; g_all = d.country.values
F = build(d)
# extra engineered features
for s in ["fever", "chestpain", "nightsweats", "weightlost"]: F[s + "_dur"] = d["symp_" + s + "_weeks"].where(F[s] == 1, 0).clip(0, 5)
F["cough2w"] = ((F.cough == 1) & (F.cough_dur >= 3)).astype(int)
F["who4"] = ((F.cough + F.fever + F.nightsweats + F.weightlost) > 0).astype(int)
F["max_dur"] = F[["cough_dur", "fever_dur", "chestpain_dur", "nightsweats_dur", "weightlost_dur"]].max(1)
F["sex_age"] = F.male * F.age_group
F["constitutional"] = F.fever + F.nightsweats + F.weightlost
F["crp_hi"] = (np.exp2(F.crp_log2) >= 10).astype(float).where(F.crp_log2.notna())
F["cad2"] = F.cad ** 2 / 10
F["cad_hi"] = (F.cad >= 4.0).astype(float).where(F.cad.notna())
BASE = ["cough", "fever", "chestpain", "nightsweats", "weightlost", "cough_dur", "male", "age_group", "prior_tb"]
sets = {
 "base": BASE,
 "base+nsym": BASE + ["n_symptoms"],
 "base+durs": BASE + ["fever_dur", "chestpain_dur", "nightsweats_dur", "weightlost_dur"],
 "base+cough2w+constit": BASE + ["cough2w", "constitutional", "who4"],
 "base+sexage": BASE + ["sex_age"],
 "compact": ["nightsweats", "weightlost", "fever", "cough_dur", "male", "age_group", "prior_tb", "constitutional"],
}
def lr(C, pen="l2"): return lambda: make_pipeline(StandardScaler(), LogisticRegression(C=C, penalty=pen, solver="liblinear" if pen == "l1" else "lbfgs", max_iter=3000))
def gb(): return HistGradientBoostingClassifier(max_depth=2, learning_rate=.04, max_iter=200, min_samples_leaf=30, l2_regularization=5.0, random_state=0)
class Blend:
    def __init__(s, w=.5, C=.1): s.w, s.C = w, C
    def fit(s, X, y): s.a = lr(s.C)().fit(X, y); s.b = gb().fit(X, y); return s
    def predict_proba(s, X): p = s.w * s.a.predict_proba(X)[:, 1] + (1 - s.w) * s.b.predict_proba(X)[:, 1]; return np.c_[1 - p, p]
models = {"LR C.03": lr(.03), "LR C.1": lr(.1), "LR C.3": lr(.3), "LR C1": lr(1.0), "L1 C.1": lr(.1, "l1"), "L1 C.3": lr(.3, "l1"), "GB": gb, "Blend": lambda: Blend()}
def loco(mk, cols):
    ok = F[cols].notna().all(1).values; X = F.loc[ok, cols].values.astype(float); y = y_all[ok]; g = g_all[ok]; out = []
    for t in ["SA", "Zambia"]:
        tr = g != t; out.append(roc_auc_score(y[~tr], mk().fit(X[tr], y[tr]).predict_proba(X[~tr])[:, 1]))
    return out
rows = []
for tier, extra in [("A", []), ("A+CRP", ["crp_log2"]), ("A+CAD", ["cad"]), ("A+CRP+CAD", ["crp_log2", "cad"])]:
    for sn, cs in sets.items():
        for mn, mk in models.items():
            a = loco(mk, cs + extra); rows.append(dict(tier=tier, feats=sn, model=mn, SA=a[0], Zam=a[1], mean=np.mean(a)))
    for sn, cs, ex in [("base+cad2", BASE, extra + (["cad2"] if "cad" in extra else [])), ("base+cadhi", BASE, extra + (["cad_hi"] if "cad" in extra else [])), ("base+crphi", BASE, extra + (["crp_hi"] if "crp_log2" in extra else []))]:
        if ex != extra:
            for mn in ["LR C.1", "LR C.3", "GB", "Blend"]:
                a = loco(models[mn], cs + ex); rows.append(dict(tier=tier, feats=sn, model=mn, SA=a[0], Zam=a[1], mean=np.mean(a)))
R = pd.DataFrame(rows).round(3); R.to_csv("model/explore.csv", index=False)
for t, g in R.groupby("tier"): print(t); print(g.sort_values("mean", ascending=False).head(6).to_string(index=False))
print("baseline base LR C.1:"); print(R[(R.feats == "base") & (R.model == "LR C.1")].to_string(index=False))
