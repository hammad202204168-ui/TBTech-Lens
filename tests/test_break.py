"""Break-it tests, written BEFORE the fixes (test-driven). Each test states the behaviour a careful user or a hostile caller should get.
A failing test here is a bug in the app, not in the test. See docs/BREAK_REPORT.md for what failed on the first run and how it was fixed."""
import io, os, sys, math, threading, json
from pathlib import Path
import numpy as np, pandas as pd, pytest
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["TBSCREEN_DB"] = str(ROOT / "tests" / "_break.db")
from tbscreen import engine as E, store, validate

BASE = dict(cough=1, cough_dur=3, fever=0, nightsweats=1, weightlost=0, male=1, age_group=3, prior_tb=0)


# ----------------------------------------------------------------- engine: wrong types and wild numbers
@pytest.mark.parametrize("no", ["no", "No", "false", "0", "n", "NO"])
def test_text_no_means_no(no):
    a = E.score({**BASE, "fever": no}); b = E.score({**BASE, "fever": 0}); assert a["probability"] == pytest.approx(b["probability"])


@pytest.mark.parametrize("yes", ["yes", "Yes", "true", "1", "y", True, 1])
def test_text_yes_means_yes(yes):
    assert E.score({**BASE, "fever": yes})["probability"] == pytest.approx(E.score({**BASE, "fever": 1})["probability"])


@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan"), "abc", "", None, [], {}])
def test_unusable_numbers_are_treated_as_not_entered(bad):
    r = E.score({**BASE, "crp": bad, "cad": bad}); assert r["tier"] == "A" and math.isfinite(r["probability"]) and all(math.isfinite(v) for _, v in r["shap"])


def test_extreme_numbers_are_clipped_not_exploded():
    r = E.score({**BASE, "crp": 1e300, "cad": 1e300}); assert math.isfinite(r["probability"]) and r["features"]["cad"] <= 10.0 and r["features"]["crp_log2"] <= math.log2(900) + 1e-9
    r = E.score({**BASE, "crp": -50, "cad": -50}); assert r["features"]["crp_log2"] == 2.0 and r["features"]["cad"] == 0.0


def test_cad_entered_as_fraction_is_flagged():
    """Users often type the CAD probability (0.72) instead of the 0-100 score; that would silently look like a very low score."""
    assert "cad_scale" in E.score({**BASE, "cad": 0.72})["warnings"]
    assert "cad_scale" not in E.score({**BASE, "cad": 72})["warnings"]


@pytest.mark.parametrize("age", [-5, 0, 99, 2.7, "3", None])
def test_odd_ages_do_not_crash(age):
    assert math.isfinite(E.score({**BASE, "age_group": age})["probability"])


def test_cough_duration_ignored_without_cough():
    a = E.score({**BASE, "cough": 0, "cough_dur": 5}); b = E.score({**BASE, "cough": 0, "cough_dur": 0}); assert a["probability"] == pytest.approx(b["probability"])


def test_person_with_no_symptoms_is_not_told_to_visit_a_clinic_for_assessment():
    r = E.score(dict(age_group=3, male=0)); assert not r["who_positive"]
    assert "adv_mid" not in E.next_steps(r) and "adv_high" not in E.next_steps(r) and "adv_none" in E.next_steps(r)


def test_model_file_is_validated(tmp_path):
    m = json.load(open(E.MODEL_PATH)); m["models"]["A"]["coef"] = m["models"]["A"]["coef"][:-1]
    p = tmp_path / "bad.json"; json.dump(m, open(p, "w"))
    with pytest.raises(ValueError): E.load_model(p)
    (tmp_path / "junk.json").write_text("{not json")
    with pytest.raises(ValueError): E.load_model(tmp_path / "junk.json")


# ----------------------------------------------------------------- batch scoring
def test_batch_accepts_age_in_years():
    df = pd.DataFrame(dict(id=["a"], age=[41], male=["M"], prior_tb=[0], cough=[1], cough_dur=[3], fever=[0], chestpain=[0], nightsweats=[1], weightlost=[0]))
    out = E.score_table(df); assert out.loc[0, "row_status"] == "ok"
    df2 = df.drop(columns="age").assign(age_group=[3]); assert E.score_table(df2).loc[0, "risk_percent"] == out.loc[0, "risk_percent"]


def test_batch_under_15_row_is_rejected_not_scored():
    df = pd.DataFrame(dict(age=[9], male=[0], prior_tb=[0], cough=[1], cough_dur=[3], fever=[0], chestpain=[0], nightsweats=[0], weightlost=[0]))
    assert E.score_table(df).loc[0, "row_status"].startswith("error")


def test_batch_row_on_tb_treatment_is_not_scored():
    df = pd.DataFrame(dict(age=[30], male=[0], prior_tb=["on treatment"], cough=[1], cough_dur=[3], fever=[0], chestpain=[0], nightsweats=[0], weightlost=[0]))
    assert E.score_table(df).loc[0, "row_status"].startswith("skipped")


def test_batch_survives_blank_and_messy_cells():
    df = pd.DataFrame(dict(id=["a", "b"], age=[35, ""], male=["m", "?"], prior_tb=[None, 0], cough=["Yes", "yes "], cough_dur=["", 3], fever=[0, 0], chestpain=[0, 0], nightsweats=[0, 0], weightlost=[0, 0]))
    out = E.score_table(df); assert len(out) == 2 and out.row_status.str.startswith(("ok", "error")).all()


def test_csv_export_neutralises_formulas():
    df = pd.DataFrame(dict(ref=["=HYPERLINK(\"http://x\")", "+1+1", "-2", "@SUM(A1)", "normal"], n=[1, 2, 3, 4, 5]))
    csv = store.safe_csv(df); lines = csv.splitlines()[1:]
    assert all(not l.startswith(("=", "+", "-", "@")) for l in lines) and "normal" in csv and "'=HYPERLINK" in csv


# ----------------------------------------------------------------- API
@pytest.fixture()
def client(monkeypatch):
    from fastapi.testclient import TestClient
    import api.main as m
    monkeypatch.setattr(m, "KEY", None); store.delete_all(); yield TestClient(m.app); store.delete_all()


PERSON = dict(age_group=3, male=True, cough=True, cough_dur=3)


def test_api_rejects_misspelled_fields(client):
    assert client.post("/predict", json={**PERSON, "nightsweat": True}).status_code == 422


def test_api_text_fields_are_length_limited(client):
    assert client.post("/predict", json={**PERSON, "save": True, "ref": "x" * 10000}).status_code == 422
    assert client.post("/predict", json={**PERSON, "save": True, "site": "s" * 10000}).status_code == 422


def test_api_sql_and_html_in_text_fields_are_stored_as_plain_text(client):
    evil = "x'); DROP TABLE screenings;--<script>alert(1)</script>"
    r = client.post("/predict", json={**PERSON, "save": True, "ref": evil[:100], "site": "S"}); assert r.status_code == 200
    rows = client.get("/screenings").json(); assert rows and rows[0]["ref"] == evil[:100]


def test_api_limit_is_bounded(client):
    assert client.get("/screenings", params=dict(limit=-1)).status_code == 422
    assert client.get("/screenings", params=dict(limit=10 ** 9)).status_code == 422


def test_api_rejects_non_numeric_json_values(client):
    assert client.post("/predict", json={**PERSON, "crp": "very high"}).status_code == 422
    assert client.post("/predict", json={**PERSON, "cad": 500}).status_code == 422


def test_api_batch_rejects_binary_and_huge_files(client):
    assert client.post("/predict/batch", files={"file": ("a.csv", bytes(range(256)) * 50, "text/csv")}).status_code in (400, 422)
    big = "age,male,prior_tb,cough,cough_dur,fever,chestpain,nightsweats,weightlost\n" + "30,1,0,1,3,0,0,0,0\n" * 6000
    assert client.post("/predict/batch", files={"file": ("a.csv", big, "text/csv")}).status_code == 413


def test_api_batch_accepts_age_in_years(client):
    csv = "id,age,male,prior_tb,cough,cough_dur,fever,chestpain,nightsweats,weightlost\nP1,41,M,0,1,3,0,0,1,0\n"
    r = client.post("/predict/batch", files={"file": ("a.csv", csv, "text/csv")}); assert r.status_code == 200 and r.json()[0]["row_status"] == "ok"


def test_api_concurrent_saves_do_not_lock_the_database(client):
    errs = []
    def work():
        for _ in range(15):
            r = client.post("/predict", json={**PERSON, "save": True, "site": "T"})
            if r.status_code != 200: errs.append(r.status_code)
    th = [threading.Thread(target=work) for _ in range(8)]; [t.start() for t in th]; [t.join() for t in th]
    assert not errs and len(client.get("/screenings", params=dict(limit=1000)).json()) == 120


def test_api_validation_endpoint_handles_empty_and_single_class(client):
    assert "message" in client.get("/validation").json()
    for _ in range(3):
        i = client.post("/predict", json={**PERSON, "save": True}).json()["id"]; client.post(f"/screenings/{i}/outcome", params=dict(outcome="not_tb"))
    j = client.get("/validation").json(); assert "summary" in j and j["summary"]["auc"] is None


def test_api_errors_do_not_leak_internals(client):
    r = client.post("/predict", content=b"{broken", headers={"content-type": "application/json"}); assert r.status_code == 422 and "Traceback" not in r.text


def test_api_key_check_is_constant_time(monkeypatch):
    import inspect, api.main as m
    assert "compare_digest" in inspect.getsource(m.auth)
