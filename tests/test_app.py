"""Web app: three modes (clinical / X-ray / both), result-specific advice, PDF report, page content."""
import io, os, sys, json, re
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); os.environ["TBSCREEN_DB"] = str(ROOT / "tests" / "_app.db")
from PIL import Image
from fastapi.testclient import TestClient
from tbscreen import advice, i18n
from tbscreen.modules import xray
import app.main as M

CLIN = dict(age=41, male=True, tb_history="never", cough=True, cough_dur=4, nightsweats=True, weightlost=True, crp=40)
ORDER = ["Lower", "Intermediate", "Higher"]


@pytest.fixture()
def c(monkeypatch, tmp_path):
    monkeypatch.setattr("api.main.KEY", None); monkeypatch.setattr(xray, "DIR", tmp_path / "none"); return TestClient(M.app)


def png(w=300, h=300, v=120):
    b = io.BytesIO(); Image.new("L", (w, h), v).save(b, "PNG"); return b.getvalue()


@pytest.fixture()
def cx(tmp_path, monkeypatch, c):
    torch = pytest.importorskip("torch"); pytest.importorskip("onnx"); pytest.importorskip("onnxruntime")
    net = torch.nn.Sequential(torch.nn.AdaptiveAvgPool2d(4), torch.nn.Flatten(), torch.nn.Linear(16, 1)); net.eval()
    torch.onnx.export(net, torch.zeros(1, 1, 64, 64), str(tmp_path / "xray_model.onnx"), input_names=["image"], output_names=["logit"], dynamo=False)
    (tmp_path / "xray_config.json").write_text(json.dumps(dict(size=64, channels=1, mean=.5, std=.25, logits=True, thr_low=.4, thr_high=.6)))
    monkeypatch.setattr(xray, "DIR", tmp_path); return c


def post(c, clinical=None, img=None, url="/api/screen", ref=""):
    files = {"image": ("x.png", img, "image/png")} if img is not None else None
    return c.post(url, data={"data": json.dumps({"clinical": clinical, "ref": ref})}, files=files)


# ---- page and language
def test_page_and_static_files(c):
    r = c.get("/"); assert r.status_code == 200 and "TBTech Lens" in r.text and r.headers["x-content-type-options"] == "nosniff"
    assert c.get("/static/style.css").status_code == 200 and c.get("/assets/molecunova_logo_small.png").status_code == 200


def test_no_country_or_study_wording_in_app_texts():
    bad = re.compile(r"zambia|south africa|pakistan|trained on|study|training countr|research software|DOTS", re.I)
    for lg in ("en", "ur"):
        assert not [k for k, v in i18n.T[lg].items() if bad.search(v)], lg
    html = (ROOT / "app" / "static" / "index.html").read_text(); assert not bad.search(html)
    for lg in ("en", "ur"): assert not bad.search(json.dumps(advice.TX[lg], ensure_ascii=False))


def test_advice_texts_exist_in_both_languages():
    assert set(advice.TX["en"]) == set(advice.TX["ur"])
    assert set(i18n.T["en"]) == set(i18n.T["ur"])


# ---- modes
def test_clinical_only(c):
    j = post(c, CLIN).json(); assert j["mode"] == "clinical" and j["overall"] in ORDER and 0 <= j["position"] <= 1 and j["xray"]["provided"] is False


def test_xray_only(cx):
    j = post(cx, None, png()).json(); assert j["mode"] == "xray" and j["clinical"] is None and j["xray"]["band"] in ORDER and len(j["xray"]["heat"]) == 8


def test_both_overall_is_the_higher_level(cx):
    j = post(cx, CLIN, png()).json(); assert j["mode"] == "both"
    assert ORDER.index(j["overall"]) == max(ORDER.index(j["clinical"]["band"]), ORDER.index(j["xray"]["band"]))


def test_nothing_entered_is_refused(c):
    assert post(c).status_code == 422


def test_xray_only_without_module_is_refused(c):
    assert post(c, None, png()).status_code == 422


def test_xray_failure_does_not_block_clinical(c):
    j = post(c, CLIN, png()).json(); assert j["xray"]["error"] == "not_installed" and j["overall"]


@pytest.mark.parametrize("bad", [dict(CLIN, age=9), dict(CLIN, age=200), dict(CLIN, cough_dur=0), dict(CLIN, tb_history="current"), dict(CLIN, nightsweat=True), dict(CLIN, crp="high"), dict(CLIN, cad=500)])
def test_bad_clinical_input_is_refused(c, bad):
    assert post(c, bad).status_code == 422


def test_garbage_and_unknown_fields_are_refused(c):
    assert c.post("/api/screen", data={"data": "{oops"}).status_code == 422
    assert c.post("/api/screen", data={"data": json.dumps({"clinical": CLIN, "bogus": 1})}).status_code == 422


def test_unreadable_images_are_reported_politely(cx):
    for img in (b"not an image", png(20, 20), png(300, 300) + b"0" * 11_000_000):
        assert post(cx, CLIN, img).json()["xray"]["error"]; assert post(cx, None, img).status_code == 422


def test_symptom_free_person_is_lower_and_told_no_action(c):
    j = post(c, dict(age=30, male=False)).json(); assert j["overall"] == "Lower" and j["position"] <= 0.3
    assert advice_has(j, "No action is needed now") and not j["text"]["en"]["tests"]


def advice_has(j, s): return any(s in p for p in j["text"]["en"]["precautions"])


# ---- advice depends on the result
def test_precautions_change_with_the_result(c):
    hi = post(c, CLIN).json()["text"]["en"]; lo_sym = post(c, dict(age=50, male=False, fever=True)).json()["text"]["en"]
    assert hi["precautions"] != lo_sym["precautions"] and hi["tests"] != lo_sym["tests"]
    names = lambda t: [n for n, _ in t["tests"]]
    assert "Sputum Xpert MTB/RIF (Ultra)" in names(hi) and "Clinical review in about 2 weeks" in names(lo_sym)


def test_prior_tb_triggers_resistance_advice(c):
    j = post(c, dict(CLIN, tb_history="past")).json()["text"]["en"]; assert any("earlier TB treatment" in p for p in j["precautions"]) and any("culture" in n.lower() for n, _ in j["tests"])


def test_weight_loss_triggers_nutrition_advice(c):
    assert any("weigh yourself" in p for p in post(c, CLIN).json()["text"]["en"]["precautions"])
    assert not any("weigh yourself" in p for p in post(c, dict(CLIN, weightlost=False)).json()["text"]["en"]["precautions"])


def test_xray_quality_issue_is_reported(cx):
    j = post(cx, CLIN, png(300, 300, 5)).json(); assert "q_dark" in j["xray"]["quality"] and any("dark" in s for s in j["text"]["en"]["impression"]) and any("Repeat the X-ray" in n for n, _ in j["text"]["en"]["tests"])


def test_both_languages_returned(c):
    j = post(c, CLIN).json(); assert set(j["text"]) == {"en", "ur"} and j["text"]["ur"]["impression"] != j["text"]["en"]["impression"]


# ---- PDF
def test_pdf_clinical_only(c):
    r = post(c, CLIN, url="/api/report", ref="CLN-1"); assert r.status_code == 200 and r.content[:4] == b"%PDF" and r.headers["content-type"] == "application/pdf"


def test_pdf_with_xray_contains_text(cx):
    r = post(cx, CLIN, png(), url="/api/report"); assert r.content[:4] == b"%PDF" and len(r.content) > 20000


def test_pdf_xray_only(cx):
    assert post(cx, None, png(), url="/api/report").content[:4] == b"%PDF"


def test_pdf_refuses_empty(c):
    assert post(c, None, url="/api/report").status_code == 422


# ---- X-ray module pieces
def test_finding_and_position_thresholds(tmp_path, monkeypatch):
    (tmp_path / "xray_config.json").write_text(json.dumps(dict(thr_low=.2, thr_high=.8))); monkeypatch.setattr(xray, "DIR", tmp_path)
    assert [xray.finding(p) for p in (.1, .5, .9)] == ["Lower", "Intermediate", "Higher"]
    ps = [xray.position(p) for p in (0, .1, .2, .5, .8, .9, 1)]; assert ps == sorted(ps) and ps[0] == 0 and ps[-1] == 1


def test_env_override_for_model_folder():
    assert "TBSCREEN_XRAY_DIR" in (ROOT / "tbscreen" / "modules" / "xray.py").read_text()
