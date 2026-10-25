"""Simulate 1,200 users through the real API (in-process). SIMULATED people, not real usability data.
Real covariates are resampled from the training dataset; extra personas make typical mistakes."""
import sys, os, time, json, random, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
os.environ["TBSCREEN_DB"] = str(ROOT / "tests" / "_sim.db")
import numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
import api.main as m; import train
from tbscreen import store
m.KEY = None; store.delete_all(); c = TestClient(m.app)
df = pd.read_csv(ROOT / "data" / "CRP_dataset_open.csv"); X = train.build(df); X = X.sample(frac=1, random_state=1).reset_index(drop=True)
rng = random.Random(7); users = []
def base(r):
    return dict(age_group=int(r.age_group), male=bool(r.male), cough=bool(r.cough), cough_dur=int(r.cough_dur) if r.cough else 0, fever=bool(r.fever), chestpain=bool(r.chestpain),
                nightsweats=bool(r.nightsweats), weightlost=bool(r.weightlost), prior_tb=bool(r.prior_tb))
rows = [r for r in X.itertuples()]
has_crp = [r for r in rows if np.isfinite(r.crp_log2)]; has_both = [r for r in has_crp if np.isfinite(r.cad)]
# persona mix (1,200): 700 typical, 100 with CRP, 100 with CRP+CAD, 100 CAD fraction typed, 60 CRP wrong unit, 60 no symptoms, 40 wrong-type input, 40 under 15/edge
for i in range(700): users.append(("typical", base(rows[i])))
for r in has_crp[:100]: d = base(r); d["crp"] = float(np.exp2(r.crp_log2)); users.append(("with_crp", d))
for r in has_both[:100]: d = base(r); d["crp"] = float(np.exp2(r.crp_log2)); d["cad"] = float(min(100, max(0, r.cad * 10))); users.append(("crp_cad", d))
for i in range(100): d = base(rows[900 + i]); d["cad"] = round(rng.uniform(0.05, 0.95), 2); d["_truth_cad"] = round(d["cad"] * 100); users.append(("cad_fraction", d))
for i in range(60): d = base(rows[1000 + i]); d["crp"] = round(rng.uniform(0.5, 90) / 10, 2); users.append(("crp_mg_dl_unit", d))
for i in range(60): d = dict(age_group=rng.randint(1, 5), male=rng.random() < .5, prior_tb=False, cough=False, fever=False, chestpain=False, nightsweats=False, weightlost=False); users.append(("no_symptoms", d))
for i in range(40): d = base(rows[1100 + i]); d[rng.choice(["crp", "cad", "age_group"])] = rng.choice(["high", "N/A", "", "12,5", "1e999"]); users.append(("wrong_type", d))
for i in range(40): d = base(rows[1140 + i]); d["age_group"] = rng.choice([0, 6, -1, 99]); users.append(("bad_age", d))
def run(u):
    kind, d = u; d = {k: v for k, v in d.items() if not k.startswith("_")}; t = time.perf_counter()
    r = c.post("/predict", json={**d, "save": True, "site": f"clinic{rng.randint(1,5)}"}); return kind, d, r.status_code, (time.perf_counter() - t) * 1000, (r.json() if r.status_code == 200 else r.text[:120])
t0 = time.perf_counter()
with ThreadPoolExecutor(16) as ex: res = list(ex.map(run, users))
wall = time.perf_counter() - t0
out = []; summ = collections.defaultdict(lambda: collections.Counter()); lat = [x[3] for x in res]
for kind, d, code, ms, j in res:
    if code == 200: summ[kind][j["band"]] += 1; summ[kind]["warn:" + ",".join(j["out_of_range"])] += bool(j["out_of_range"]); summ[kind]["tier:" + j["tier"]] += 1
    else: summ[kind]["HTTP %d" % code] += 1
ns = [x for x in res if x[0] == "no_symptoms" and x[2] == 200]
alarm = sum(1 for x in ns if x[4]["band"] != "Lower"); told_assess = sum(1 for x in ns if any(k in x[4]["next_steps"] for k in ("adv_high", "adv_mid")))
rep = dict(n=len(res), wall_s=round(wall, 1), throughput_per_s=round(len(res) / wall, 1), p50_ms=round(float(np.percentile(lat, 50)), 1), p95_ms=round(float(np.percentile(lat, 95)), 1), p99_ms=round(float(np.percentile(lat, 99)), 1),
           http=dict(collections.Counter(x[2] for x in res)), saved=len(store.rows(None, 5000)), no_symptom_not_lower=alarm, no_symptom_n=len(ns), no_symptom_told_to_get_assessed=told_assess,
           by_persona={k: dict(v) for k, v in summ.items()})
# effect of mistakes: CAD fraction vs true; CRP unit
def prob(d): return c.post("/predict", json=d).json()["probability"]
cf = [u for u in users if u[0] == "cad_fraction"][:100]; drop = []
for _, d in cf:
    tcad = d["_truth_cad"]; dd = {k: v for k, v in d.items() if not k.startswith("_")}; a = prob(dd); b = prob({**dd, "cad": tcad}); drop.append((b - a) * 100)
rep["cad_fraction_mean_underestimate_pp"] = round(float(np.mean(drop)), 1)
json.dump(rep, open(ROOT / "docs" / "simulation_results.json", "w"), indent=1); print(json.dumps(rep, indent=1))
