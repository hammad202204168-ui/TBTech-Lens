import io, os, sys, math, json
from pathlib import Path
import pytest, numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["TBSCREEN_DB"] = str(ROOT / "tests" / "_test.db")
from tbscreen import engine as E, store, validate, i18n
from tbscreen.modules import xray

P = dict(cough=1, cough_dur=4, fever=1, nightsweats=1, weightlost=1, male=1, age_group=2, prior_tb=0)


def test_tier_selection():
    assert E.score(dict(age_group=3))["tier"] == "A"
    assert E.score({**P, "crp": 10})["tier"] == "A+CRP"
    assert E.score({**P, "cad": 50})["tier"] == "A+CAD"
    assert E.score({**P, "crp": 10, "cad": 50})["tier"] == "A+CRP+CAD"


def test_more_symptoms_means_higher_risk():
    lo = E.score(dict(age_group=3, male=0))["probability"]; hi = E.score({**P, "male": 0, "age_group": 3})["probability"]
    assert hi > lo
    assert E.score({**P, "cad": 90})["probability"] > E.score({**P, "cad": 10})["probability"]


def test_probability_bounds_and_bands():
    for cad in (0, 40, 100):
        r = E.score({**P, "cad": cad}); assert 0 < r["probability"] < 1 and r["band"] in ("Lower", "Intermediate", "Higher")


def test_shap_adds_up():
    r = E.score({**P, "crp": 40, "cad": 70}); M = E.load_model(); m = M["models"][r["tier"]]
    base_z = math.log(r["base_probability"] / (1 - r["base_probability"])); z = math.log(r["probability"] / (1 - r["probability"]))
    assert abs(base_z + sum(v for _, v in r["shap"]) - z) < 1e-9


def test_shap_matches_shap_library():
    shap = pytest.importorskip("shap")
    r = E.score({**P, "crp": 40, "cad": 70}); m = E.load_model()["models"][r["tier"]]; f = r["features"]
    x = np.array([[f[n] for n in m["features"]]]); ex = shap.LinearExplainer((np.array(m["coef"]), m["intercept"]), np.array(m["feature_mean"]).reshape(1, -1))
    mine = np.array([dict(r["shap"])[n] for n in m["features"]]); assert np.abs(ex.shap_values(x)[0] - mine).max() < 1e-9


def test_who_screen_and_advice():
    r = E.score({**P}); assert r["who_positive"] and "adv_symptom_test" in E.next_steps(r)
    r0 = E.score(dict(age_group=3)); assert not r0["who_positive"] and "adv_symptom_test" not in E.next_steps(r0)
    assert "adv_lab_only" in E.next_steps(r0)


def test_out_of_range_warning_and_clipping():
    r = E.score({**P, "crp": 5000}); assert r["features"]["crp_log2"] <= math.log2(5000)
    r = E.score({**P, "crp": 1}); assert r["features"]["crp_log2"] == 2.0            # floor at the device limit 4


def test_garbage_inputs_do_not_crash():
    r = E.score(dict(age_group=99, cough=1, cough_dur=99, crp="abc", cad=float("nan"))); assert r["tier"] == "A"


def test_batch_scoring_and_errors():
    df = pd.DataFrame([["a", 41, "yes", 0, 1, 4, 1, 0, 1, 1, 40, 70], ["b", 9, 0, 0, 0, 0, 0, 0, 0, 0, "", ""]], columns=E.TEMPLATE_COLUMNS)
    out = E.score_table(df); assert out.loc[0, "row_status"] == "ok" and out.loc[0, "band"] in ("Lower", "Intermediate", "Higher"); assert out.loc[1, "row_status"].startswith("error")


def test_translations_complete_and_formattable():
    assert set(i18n.T["en"]) == set(i18n.T["ur"])
    for lg in ("en", "ur"):
        i18n.tr(lg, "oor", x="x"); i18n.tr(lg, "saved", i=3); i18n.tr(lg, "xray_failed", e="x")
    for k in ("adv_symptom_test", "adv_high", "adv_mid", "adv_low", "adv_lab_only"): assert k in i18n.T["ur"]


def test_store_and_validation_roundtrip():
    store.delete_all(); ids = []
    rng = np.random.RandomState(0)
    for i in range(60):
        x = {**P, "cad": float(rng.randint(0, 100))}; r = E.score(x); ids.append(store.save(r, x, "T", f"r{i}"))
        store.set_outcome(ids[-1], "tb" if rng.rand() < r["probability"] * 3 else "not_tb")
    d = pd.DataFrame(store.rows()); d["outcome_tb"] = (d.outcome == "tb").astype(int)
    res, tab = validate.evaluate(d); assert res["n"] == 60 and res["auc"] is not None and set(tab.band) == {"Lower", "Intermediate", "Higher"}
    with pytest.raises(ValueError): store.set_outcome(ids[0], "maybe")
    with pytest.raises(KeyError): store.set_outcome(99999, "tb")
    store.delete_all()


def test_validation_flags_small_samples():
    d = pd.DataFrame(dict(probability=[.1, .2, .3, .4], band=["Lower", "Lower", "Higher", "Higher"], outcome_tb=[0, 0, 1, 1])); res, _ = validate.evaluate(d); assert res["enough"] is False


def test_xray_module_is_off_without_model(tmp_path, monkeypatch):
    monkeypatch.setattr(xray, "DIR", tmp_path); assert not xray.available()
    with pytest.raises(RuntimeError): xray.probability(b"x")


def test_model_json_is_consistent():
    M = E.load_model()
    for name, m in M["models"].items():
        n = len(m["features"]); assert len(m["coef"]) == n == len(m["feature_mean"]) == len(m["feature_min"]) == len(m["feature_max"])
        assert 0 < m["threshold_low"] <= m["threshold_high"] < 1 and m["n_tb"] >= 50 and all(b["tb_rate"] is not None for b in m["bands"])


# ---------------------------------------------------------------- API
def test_api():
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app); store.delete_all()
    assert c.get("/health").json()["status"] == "ok"
    body = dict(age_group=2, male=True, cough=True, cough_dur=4, fever=True, nightsweats=True, weightlost=True, crp=40, cad=70, save=True, site="T")
    r = c.post("/predict", json=body); assert r.status_code == 200; j = r.json(); assert j["band"] in ("Lower", "Intermediate", "Higher") and j["id"] and j["shap_log_odds"]
    assert c.post("/predict", json={**body, "age_group": 9}).status_code == 422
    assert c.post("/predict", json={**body, "on_tb_treatment": True}).status_code == 422
    assert c.post(f"/screenings/{j['id']}/outcome", params=dict(outcome="tb")).status_code == 200
    assert c.post(f"/screenings/{j['id']}/outcome", params=dict(outcome="x")).status_code == 422
    assert c.post("/screenings/999999/outcome", params=dict(outcome="tb")).status_code == 404
    assert len(c.get("/screenings").json()) == 1
    assert "summary" in c.get("/validation").json()
    csv = pd.DataFrame([["P1", 41, 1, 0, 1, 4, 1, 0, 1, 1, 40, 70]], columns=E.TEMPLATE_COLUMNS).to_csv(index=False)
    r = c.post("/predict/batch", files={"file": ("a.csv", csv, "text/csv")}); assert r.status_code == 200 and r.json()[0]["row_status"] == "ok"
    assert c.post("/predict/batch", files={"file": ("a.csv", "x\n1", "text/csv")}).status_code == 422
    store.delete_all()


def test_api_key(monkeypatch):
    from fastapi.testclient import TestClient
    import api.main as m
    monkeypatch.setattr(m, "KEY", "secret"); c = TestClient(m.app)
    assert c.post("/predict", json=dict(age_group=2, male=True)).status_code == 401
    assert c.post("/predict", json=dict(age_group=2, male=True), headers={"X-API-Key": "secret"}).status_code == 200
    assert c.get("/health").status_code == 200


# ---------------------------------------------------------------- UI
def test_add_tier_reproduces_training(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import train, add_tier
    c = pd.read_csv(train.CSV, low_memory=False); d = c[c.Xpertculture.notna()].copy(); F = train.build(d)
    t = pd.DataFrame(dict(age_group=F.age_group, male=F.male, prior_tb=F.prior_tb, cough=F.cough, cough_dur=F.cough_dur, fever=F.fever, chestpain=F.chestpain,
                          nightsweats=F.nightsweats, weightlost=F.weightlost, cad=(F.cad * 10), tb=d.Xpertculture.map({1.0: "yes", 0.0: "no"}), site=d.country)).dropna(subset=["cad"])
    f = tmp_path / "d.csv"; t.to_csv(f, index=False); out = tmp_path / "m.json"
    tier = add_tier.main([str(f), "--name", "TEST", "--out", str(out)])
    ref = E.load_model()["models"]["A+CAD"]
    assert np.allclose(tier["coef"], ref["coef"], atol=1e-6) and abs(tier["auc_unseen_country_pooled"] - ref["auc_unseen_country_pooled"]) < 1e-6
    M = json.load(open(out)); assert "TEST" in M["models"] and "A" in M["models"]
    with pytest.raises(SystemExit): add_tier.main([str(f), "--name", "X", "--out", str(out), "--min-tb", "500"])
