"""Train a new tier (or retrain a tier) from YOUR OWN labelled data and add it to the model file.

Input CSV columns: the template columns (age_group, male, prior_tb, cough, cough_dur, fever, chestpain, nightsweats, weightlost),
`tb` (yes/no from Xpert or culture), optional extra inputs `crp`, `cad`, `xray_prob`, and optional `site` (clinic or city).
Example (local clinic data + the X-ray model's output):
    python scripts/add_tier.py my_data.csv --name A+CRP+CAD+XRAY --out model/tb_screen_model_pk.json
If `site` has 2+ values the script also reports leave-one-site-out AUC. Use at least ~50 TB cases per tier; the script refuses fewer.
Point the app to the new file with  TBSCREEN_MODEL=model/tb_screen_model_pk.json
"""
import argparse, json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from tbscreen import engine as E
from train import fit_lr, pick_C, boot_ci
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score
EXTRA = ["crp", "cad", "xray_prob"]


def main(a=None):
    ap = argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--name", required=True); ap.add_argument("--model", default=str(E.MODEL_PATH)); ap.add_argument("--out"); ap.add_argument("--min-tb", type=int, default=50)
    a = ap.parse_args(a); df = pd.read_csv(a.csv)
    yes = lambda v: 1 if str(v).strip().lower() in ("1", "1.0", "yes", "y", "true", "tb", "positive") else (0 if str(v).strip().lower() in ("0", "0.0", "no", "n", "false", "negative", "not_tb") else np.nan)
    y = df["tb"].map(yes); df = df[y.notna()].copy(); y = y[y.notna()].astype(int).values
    use = [c for c in EXTRA if c in df.columns and df[c].notna().all()]
    rows = []
    for _, r in df.iterrows():
        x = {k: (str(r[k]).strip().lower() in ("1", "1.0", "yes", "y", "true", "m", "male") if k in E.SYMPTOMS + ["male", "prior_tb"] else r[k]) for k in E.BASE_FEATURES if k in r}
        for k in use: x[k] = r[k]
        rows.append(E.features(x))
    feats = E.BASE_FEATURES + [{"crp": "crp_log2", "cad": "cad", "xray_prob": "xray_prob"}[k] for k in use]
    X = pd.DataFrame(rows)[feats].values.astype(float)
    if y.sum() < a.min_tb: sys.exit(f"Only {int(y.sum())} TB cases; at least {a.min_tb} are needed for a stable tier.")
    res = dict(n=len(y), tb=int(y.sum()), extra=use)
    if "site" in df.columns and df["site"].nunique() > 1:
        g = df["site"].values; pa, py = [], []
        for s in np.unique(g):
            te = g == s
            if len(np.unique(y[te])) < 2 or len(np.unique(y[~te])) < 2: continue
            C = pick_C(X[~te], y[~te], feats); pa.append(fit_lr(X[~te], y[~te], C, feats).predict_proba(X[te])[:, 1]); py.append(y[te]); print(f"  held-out site {s}: AUC {roc_auc_score(y[te], pa[-1]):.3f} (n={te.sum()}, TB={y[te].sum()})")
        if pa: pp, yy = np.concatenate(pa), np.concatenate(py); lo, hi = boot_ci(yy, pp); res.update(auc=roc_auc_score(yy, pp), lo=lo, hi=hi)
    C = pick_C(X, y, feats, seed=1); oof = np.zeros(len(y)); cnt = np.zeros(len(y))
    for tr, te in RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=3).split(X, y):
        oof[te] += fit_lr(X[tr], y[tr], C, feats).predict_proba(X[te])[:, 1]; cnt[te] += 1
    oof /= cnt
    if "auc" not in res: lo, hi = boot_ci(y, oof); res.update(auc=roc_auc_score(y, oof), lo=lo, hi=hi, note="cross-validated within one site only; not an unseen-site estimate")
    pos = np.sort(oof[y == 1]); tl = float(pos[int(np.floor(.10 * len(pos)))]); neg = np.sort(oof[y == 0]); th = max(float(neg[int(np.floor(.80 * len(neg)))]), tl)
    band = np.where(oof < tl, 0, np.where(oof < th, 1, 2)); bands = [dict(band=n, n=int((band == i).sum()), share=float((band == i).mean()), tb_rate=float(y[band == i].mean()) if (band == i).any() else 0.0) for i, n in enumerate(["Lower", "Intermediate", "Higher"])]
    m = fit_lr(X, y, C, feats); coef = m.coef_ / m.scale_; icpt = float(m.intercept_ - np.sum(m.coef_ * m.mean_ / m.scale_)); call = oof >= tl
    tier = dict(features=feats, coef=[float(v) for v in coef], intercept=icpt, C=C, n_train=int(len(y)), n_tb=int(y.sum()), threshold_low=tl, threshold_high=th, bands=bands,
                oof_performance_at_low=dict(sens=float(call[y == 1].mean()), spec=float((~call)[y == 0].mean()), ppv=float(y[call].mean()), npv=float(1 - y[~call].mean()), prevalence=float(y.mean())),
                feature_mean=[float(v) for v in X.mean(0)], feature_min=[float(v) for v in X.min(0)], feature_max=[float(v) for v in X.max(0)],
                auc_unseen_country_pooled=float(res["auc"]), auc_ci=[float(res["lo"]), float(res["hi"])], source=str(Path(a.csv).name))
    M = json.load(open(a.model)); M["models"][a.name] = tier; out = a.out or a.model; json.dump(M, open(out, "w"), indent=1)
    print(f"Tier '{a.name}' saved to {out}: n={len(y)}, TB={int(y.sum())}, AUC {res['auc']:.3f} ({res['lo']:.3f}-{res['hi']:.3f}) {res.get('note', '')}")
    return tier

if __name__ == "__main__": main()
