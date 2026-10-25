"""Scoring engine for TB-Screen. Pure Python + a JSON model (no pickle, no ML library at run time).

The model file holds several tiers. A tier is a logistic model that needs the base inputs plus some optional results
(CRP, X-ray CAD score, later an X-ray model probability). The richest tier whose inputs are all present is used, so a new tier
trained later (for example with an X-ray model output) works without changing any code.
"""
import json, math, os
from pathlib import Path

MODEL_PATH = Path(os.environ.get("TBSCREEN_MODEL") or Path(__file__).resolve().parent.parent / "model" / "tb_screen_model.json")
SYMPTOMS = ["cough", "fever", "chestpain", "nightsweats", "weightlost"]
BASE_FEATURES = SYMPTOMS + ["cough_dur", "male", "age_group", "prior_tb"]
OPTIONAL = {"crp_log2": "crp", "cad": "cad", "xray_prob": "xray_prob"}      # model feature -> input key
DUR_CODES = {0: "none", 1: "lt1w", 2: "1to2w", 3: "2to4w", 4: "4w3m", 5: "gt3m"}
AGE_CODES = {1: "15-24", 2: "25-34", 3: "35-44", 4: "45-54", 5: "55+"}
TEMPLATE_COLUMNS = ["id", "age", "male", "prior_tb", "cough", "cough_dur", "fever", "chestpain", "nightsweats", "weightlost", "crp", "cad"]
_CACHE = {}


def validate_model(M):
    """Refuse a model file that is incomplete or internally inconsistent (a wrong file must fail loudly, not score silently)."""
    try:
        for name, m in M["models"].items():
            n = len(m["features"])
            if not (len(m["coef"]) == len(m["feature_mean"]) == len(m["feature_min"]) == len(m["feature_max"]) == n):
                raise ValueError(f"tier {name}: coefficient and feature lists differ in length")
            if not all(f in BASE_FEATURES or f in OPTIONAL for f in m["features"]): raise ValueError(f"tier {name}: unknown feature")
            if not (0 < m["threshold_low"] <= m["threshold_high"] < 1): raise ValueError(f"tier {name}: bad thresholds")
            if {b["band"] for b in m["bands"]} != {"Lower", "Intermediate", "Higher"}: raise ValueError(f"tier {name}: bands incomplete")
        if not M["models"]: raise ValueError("no tiers")
    except KeyError as e:
        raise ValueError(f"model file is missing {e}") from None
    return M


def load_model(path=None):
    p = str(path or MODEL_PATH)
    if p not in _CACHE:
        try: M = json.load(open(p))
        except (OSError, json.JSONDecodeError) as e: raise ValueError(f"cannot read model file {p}: {e}") from None
        _CACHE[p] = validate_model(M)
    return _CACHE[p]


def _num(v):
    """A finite number, or None when the value is missing, blank, text or infinite."""
    if v is None or isinstance(v, (bool, list, dict, tuple)): return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


YES = {"1", "1.0", "yes", "y", "true", "t", "positive", "m", "male"}
NO = {"0", "0.0", "no", "n", "false", "f", "negative", "female", ""}


def flag(v):
    """Yes/no from a bool, number or text. Unclear text raises ValueError (never silently 'yes' or 'no')."""
    if isinstance(v, (bool, int, float)) and not (isinstance(v, float) and math.isnan(v)): return bool(v)
    if v is None or (isinstance(v, float) and math.isnan(v)): return False
    t = str(v).strip().lower()
    if t in YES: return True
    if t in NO: return False
    raise ValueError(f"unclear yes/no value: {v!r}")


def age_to_group(age):
    a = _num(age)
    if a is None or a < 15: raise ValueError("age must be 15 or older")
    return 1 if a < 25 else 2 if a < 35 else 3 if a < 45 else 4 if a < 55 else 5


def _int(v, lo, hi, default):
    v = _num(v)
    return default if v is None else min(max(int(v), lo), hi)


def features(x):
    """x: dict. cough,fever,chestpain,nightsweats,weightlost,male,prior_tb are yes/no (bool, 0/1 or text); cough_dur 0-5; age_group 1-5;
    optional crp (device units), cad (0-100), xray_prob (0-1). Values that are blank, text or infinite count as 'not entered'."""
    f = {s: int(flag(x.get(s))) for s in SYMPTOMS}
    f["cough_dur"] = _int(x.get("cough_dur"), 0, 5, 0) if f["cough"] else 0
    f["male"] = int(flag(x.get("male"))); f["prior_tb"] = int(flag(x.get("prior_tb")))
    f["age_group"] = _int(x.get("age_group"), 1, 5, 1)
    crp, cad, xr = _num(x.get("crp")), _num(x.get("cad")), _num(x.get("xray_prob"))
    if crp is not None: f["crp_log2"] = math.log2(min(max(crp, 4.0), 900.0))
    if cad is not None: f["cad"] = min(max(cad, 0.0), 100.0) / 10.0
    if xr is not None: f["xray_prob"] = min(max(xr, 0.0), 1.0)
    return f


def pick_tier(f, M):
    best, bn = None, -1
    for name, m in M["models"].items():
        if all(n in f for n in m["features"]):
            extra = len(m["features"]) - len(BASE_FEATURES)
            if extra > bn: best, bn = name, extra
    return best


def who_screen(f):
    """WHO four-symptom screen: any of cough, fever, night sweats, weight loss."""
    return bool(f["cough"] or f["fever"] or f["nightsweats"] or f["weightlost"])


def score(x, model=None):
    M = model or load_model(); f = features(x); tier = pick_tier(f, M); m = M["models"][tier]
    z = m["intercept"] + sum(c * f[n] for n, c in zip(m["features"], m["coef"]))
    p = 1.0 / (1.0 + math.exp(-z))
    band = "Lower" if p < m["threshold_low"] else "Intermediate" if p < m["threshold_high"] else "Higher"
    no_symp = tier == "A" and not any(f[k] for k in SYMPTOMS)
    presumptive = bool(f["cough"] and f["cough_dur"] >= 3)        # cough for 2 weeks or more = presumptive TB (WHO): never reported as Lower
    if presumptive and band == "Lower": band = "Intermediate"
    if no_symp: band = "Lower"            # the symptom-only tier has nothing to go on without a symptom (age and sex alone are not a screen)
    base_z = m["intercept"] + sum(c * mu for c, mu in zip(m["coef"], m["feature_mean"]))
    shap = [(n, c * (f[n] - mu)) for n, c, mu in zip(m["features"], m["coef"], m["feature_mean"])]   # exact linear SHAP (independent features)
    shap.sort(key=lambda t: -abs(t[1]))
    warns = []
    for n, lo, hi in zip(m["features"], m["feature_min"], m["feature_max"]):
        if n in OPTIONAL and not (lo - 1e-9 <= f[n] <= hi + 1e-9): warns.append(n)
    cad_in = _num(x.get("cad"))
    if cad_in is not None and 0 < cad_in < 1: warns.append("cad_scale")      # looks like a fraction, not a 0-100 score
    br = next(b for b in m["bands"] if b["band"] == band)
    lo_, hi_ = m["threshold_low"], max(m["threshold_high"], m["threshold_low"] + 1e-9)
    pos = 0.33 * p / lo_ if p < lo_ else 0.33 + 0.34 * (p - lo_) / (hi_ - lo_) if p < hi_ else min(1.0, 0.67 + 0.33 * (p - hi_) / max(1 - hi_, 1e-9))
    pos = min(pos, 0.3) if no_symp else max(pos, 0.34) if (presumptive and pos < 0.34) else pos
    return dict(no_symptoms=no_symp, position=round(pos, 3), tier=tier, probability=p, base_probability=1 / (1 + math.exp(-base_z)), band=band, tb_rate_in_band=br["tb_rate"], shap=shap,
                warnings=warns, who_positive=who_screen(f), cough_2w=bool(f["cough"] and f["cough_dur"] >= 3),
                auc=m["auc_unseen_country_pooled"], auc_ci=m["auc_ci"], features=f, inputs_used=[k for k in ("crp", "cad", "xray_prob") if OPTIONAL_KEY_IN(f, k)])


def OPTIONAL_KEY_IN(f, k):
    inv = {v: n for n, v in OPTIONAL.items()}
    return inv[k] in f


def next_steps(r):
    """Keys for the plain-language advice (translated by i18n). A lower score is never reported as 'no TB'."""
    a = []
    symptomatic = r["who_positive"] or r["cough_2w"]
    if symptomatic: a.append("adv_symptom_test")
    if not symptomatic and (r["band"] != "Higher" or r["tier"] == "A"): a.append("adv_none")        # nobody without a symptom is sent to "assessment" by a middling score
    else: a.append({"Higher": "adv_high", "Intermediate": "adv_mid", "Lower": "adv_low"}[r["band"]])
    a.append("adv_lab_only")
    return a


def score_table(df, model=None):
    """Batch scoring of a DataFrame. Needs `age` (years) or `age_group` (1-5) and the yes/no columns; `crp`, `cad` optional.
    Adds model, risk_percent, band, who_screen_positive, row_status ('ok', 'skipped: ...' or 'error: ...'). A bad row never stops the others."""
    import pandas as pd
    M = model or load_model(); rows = []
    for _, r in df.iterrows():
        try:
            tbv = str(r.get("prior_tb", "")).strip().lower()
            if tbv in ("on treatment", "current", "currently on tb treatment", "on tb treatment"):
                rows.append(dict(model="", risk_percent=None, band="", who_screen_positive="", row_status="skipped: on TB treatment")); continue
            x = {k: flag(r.get(k)) for k in SYMPTOMS + ["male"]}
            x["prior_tb"] = True if tbv in ("history", "history of tb treatment", "past", "treated") else flag(tbv)
            if _num(r.get("age")) is not None: x["age_group"] = age_to_group(r.get("age"))
            elif "age_group" in df.columns and _num(r.get("age_group")) is not None:
                ag = int(_num(r.get("age_group")))
                if not 1 <= ag <= 5: raise ValueError("age_group must be 1 to 5 (or give `age` in years)")
                x["age_group"] = ag
            else: raise ValueError("age is missing")
            if x["cough"]:
                cd = _num(r.get("cough_dur"))
                if cd is None or not 0 <= cd <= 5: raise ValueError("cough_dur (0-5) is needed when cough is yes")
                x["cough_dur"] = int(cd)
            x["crp"], x["cad"] = _num(r.get("crp")), _num(r.get("cad"))
            s = score(x, M)
            rows.append(dict(model=s["tier"], risk_percent=round(100 * s["probability"], 1), band=s["band"], who_screen_positive="yes" if s["who_positive"] else "no", row_status="ok" + ("; check CAD scale" if "cad_scale" in s["warnings"] else "")))
        except Exception as e:
            rows.append(dict(model="", risk_percent=None, band="", who_screen_positive="", row_status=f"error: {e}"))
    return pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)

