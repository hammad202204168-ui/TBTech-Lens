"""Local validation: how well do the scores agree with the clinic's own Xpert/culture results?"""
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from . import engine as E


def bootstrap_auc(y, p, n=1000, seed=0):
    r = np.random.RandomState(seed); a = []
    for _ in range(n):
        i = r.randint(0, len(y), len(y))
        if len(np.unique(y[i])) > 1: a.append(roc_auc_score(y[i], p[i]))
    return (float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))) if a else (float("nan"), float("nan"))


def evaluate(df, prob_col="probability", band_col="band", y_col="outcome_tb"):
    """df needs a 0/1 TB outcome column and the model probability and band. Returns a dict of results and a per-band table."""
    d = df[df[y_col].isin([0, 1])].copy(); y = d[y_col].astype(int).values; p = d[prob_col].astype(float).values
    n, tb = len(d), int(y.sum()); out = dict(n=n, tb=tb, prevalence=tb / n if n else float("nan"), enough=bool(tb >= 20 and n - tb >= 20))
    if len(np.unique(y)) < 2: out.update(auc=None, auc_ci=None); return out, pd.DataFrame()
    out["auc"] = float(roc_auc_score(y, p)); out["auc_ci"] = bootstrap_auc(y, p)
    low = d[band_col].eq("Lower").values
    out["sens_not_lower"] = float((~low)[y == 1].mean()); out["spec_not_lower"] = float(low[y == 0].mean())      # 'Lower' = screen-negative
    out["missed_tb_in_lower"] = int((low & (y == 1)).sum())
    t = d.groupby(band_col).agg(people=(y_col, "size"), tb=(y_col, "sum")).reindex(["Lower", "Intermediate", "Higher"]).fillna(0)
    t["tb_per_100"] = (100 * t.tb / t.people.replace(0, np.nan)).round(1); t = t.reset_index().rename(columns={band_col: "band"})
    return out, t


def from_upload(df):
    """A clinic file = template columns + `tb` (1/0 or yes/no from Xpert/culture). Scores every row and evaluates."""
    d = df.copy(); yes = lambda v: 1 if str(v).strip().lower() in ("1", "1.0", "yes", "y", "true", "tb", "positive") else (0 if str(v).strip().lower() in ("0", "0.0", "no", "n", "false", "not_tb", "negative") else np.nan)
    d["outcome_tb"] = d["tb"].map(yes)
    sc = E.score_table(d.drop(columns=["tb", "outcome_tb"])); sc["outcome_tb"] = d["outcome_tb"].values
    sc["probability"] = sc.risk_percent / 100.0
    ok = sc[sc.row_status == "ok"]
    return sc, *evaluate(ok)
