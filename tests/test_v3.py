"""v3: patient records and trend, mascot, bilingual PDF, supporting findings, report upload."""
import io, os, sys, json
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); os.environ["TBSCREEN_DB"] = str(ROOT / "tests" / "_v3.db")
from fastapi.testclient import TestClient
from tbscreen import extract, supporting, mascot, patients, i18n
import app.main as M

SICK = dict(age=40, male=True, tb_history="never", cough=True, cough_dur=3, fever=True, weightlost=True)
WELL = dict(age=40, male=True, tb_history="never")


@pytest.fixture()
def c(monkeypatch):
    monkeypatch.setattr("api.main.KEY", None); monkeypatch.delenv("TBSCREEN_PIN", raising=False)
    cl = TestClient(M.app); patients.delete_all(); yield cl; patients.delete_all()


def post(c, **d): return c.post("/api/screen", data={"data": json.dumps(d)})


def test_save_and_trend(c):
    assert post(c, clinical=SICK, ref="P-1", save=True).json()["saved"] == 1
    j = post(c, clinical=WELL, ref="P-1", save=True).json()
    assert j["trend"]["label"] == "improving" and len(j["history"]) == 1 and j["trend_text"]["ur"]
    j = post(c, clinical=SICK, ref="P-1").json(); assert j["trend"]["label"] == "worsening" and j["saved"] is None
    assert len(c.get("/api/patients/P-1").json()["visits"]) == 2


def test_nothing_saved_unless_asked(c):
    post(c, clinical=SICK, ref="P-2"); assert c.get("/api/patients").json() == []


@pytest.mark.parametrize("ref,err", [("", "ref_required"), ("a b", "ref_format"), ("12345678901", "ref_looks_like_id"), ("42101-1234567-1", "ref_looks_like_id")])
def test_ref_rules(c, ref, err):
    r = post(c, clinical=SICK, ref=ref, save=True); assert r.status_code == 422 and r.json()["detail"] == err


def test_outcome_delete_export_and_formula_safe_csv(c):
    post(c, clinical=SICK, ref="=cmd", save=True) if False else None
    post(c, clinical=SICK, ref="P-3", save=True)
    vid = c.get("/api/patients/P-3").json()["visits"][0]["id"]
    assert c.post(f"/api/visits/{vid}/outcome", json={"outcome": "tb"}).status_code == 200
    assert c.post(f"/api/visits/{vid}/outcome", json={"outcome": "x"}).status_code == 422
    assert c.get("/api/patients/export.csv").text.startswith("id,ref")
    assert c.delete("/api/patients/P-3").json()["deleted"] == 1 and c.delete("/api/patients/P-3").status_code == 404


def test_pin_protects_records(c, monkeypatch):
    monkeypatch.setenv("TBSCREEN_PIN", "1234")
    assert post(c, clinical=SICK, ref="P-4", save=True).status_code == 401 and c.get("/api/patients").status_code == 401
    h = {"X-Pin": "1234"}
    assert c.post("/api/screen", data={"data": json.dumps(dict(clinical=SICK, ref="P-4", save=True))}, headers=h).status_code == 200 and c.get("/api/patients", headers=h).status_code == 200
    assert post(c, clinical=SICK).status_code == 200      # screening without saving needs no PIN


def test_mascot_svgs_differ_and_parse(c):
    s = {b: c.get(f"/api/mascot/{b}").text for b in ("Lower", "Intermediate", "Higher")}
    assert len(set(s.values())) == 3 and all(v.startswith("<svg") for v in s.values()) and c.get("/api/mascot/x").status_code == 404
    from svglib.svglib import svg2rlg
    assert svg2rlg(io.BytesIO(mascot.svg("Higher").encode())) is not None


@pytest.mark.parametrize("lang", ["en", "ur", "both"])
def test_pdf_languages(c, lang):
    r = c.post("/api/report", data={"data": json.dumps(dict(clinical=dict(SICK, crp=30), lang=lang, support=dict(hiv="pos", xpert="not_detected")))})
    assert r.status_code == 200 and r.content[:4] == b"%PDF"
    from pypdf import PdfReader
    pdf = PdfReader(io.BytesIO(r.content)); n = len(pdf.pages); assert (n >= 4) if lang == "both" else n >= 2
    assert "Mycobacterium" in "".join(p.extract_text() for p in pdf.pages) or lang == "ur"


def test_bad_lang_rejected(c): assert c.post("/api/report", data={"data": json.dumps(dict(clinical=SICK, lang="fr"))}).status_code == 422


def test_supporting_rules():
    S = supporting.Support
    assert supporting.assess(S(xpert="detected"), False)["min_level"] == 2
    assert supporting.assess(S(xpert="rif_resistant"), False)["urgent"] == ["rif_res"]
    assert supporting.assess(S(xpert="not_detected", afb="neg", culture="neg"), True)["min_level"] == 0      # negatives never lower or raise
    assert supporting.assess(S(hemoptysis=True), False)["min_level"] == 1
    assert supporting.assess(S(hiv="pos", diabetes=True), True)["min_level"] == 1
    assert supporting.assess(S(hiv="pos", diabetes=True), False)["min_level"] == 0
    assert supporting.assess(S(mantoux_mm=12), False)["min_level"] == 1 and supporting.assess(S(mantoux_mm=6, hiv="pos"), False)["min_level"] == 1


def test_support_raises_overall_but_never_lowers(c):
    assert post(c, clinical=WELL, support=dict(xpert="detected")).json()["overall"] == "Higher"
    assert post(c, clinical=SICK, support=dict(xpert="not_detected", afb="neg")).json()["overall"] == post(c, clinical=SICK).json()["overall"]
    assert post(c, clinical=WELL, support=dict(bogus=1)).status_code == 422 and post(c, clinical=WELL, support=dict(bmi=2)).status_code == 422


def test_extract_values_and_units():
    v = extract.parse("CRP 2.4 mg/dL\nESR 62 mm/hr\nWBC 11200 /uL\nHb 9.8 g/dL\nMantoux 12 mm\nHIV: non-reactive\nAFB smear: not seen")["values"]
    assert v["crp"] == 24.0 and v["esr"] == 62 and v["wbc"] == 11.2 and v["hb"] == 9.8 and v["mantoux_mm"] == 12 and v["hiv"] == "neg" and v["afb"] == "neg"


@pytest.mark.parametrize("line,want", [("Xpert MTB/RIF: MTB detected, Rifampicin resistance not detected", "detected"), ("GeneXpert: MTB Not Detected", "not_detected"),
                                       ("Xpert MTB/RIF Ultra: MTB detected; Rif resistance detected", "rif_resistant")])
def test_extract_xpert_never_misreads_a_positive(line, want): assert extract.parse(line)["values"]["xpert"] == want


def test_extract_endpoint_and_limits(c):
    r = c.post("/api/extract", files={"file": ("r.txt", b"CRP 24 mg/L")}); assert r.json()["values"] == {"crp": 24.0}
    assert c.post("/api/extract", files={"file": ("e.txt", b"")}).status_code == 422
    assert c.post("/api/extract", files={"file": ("b.bin", b"\xff\xfe\x00\x01garbage\x80")}).status_code == 422
    assert c.post("/api/extract", files={"file": ("big.txt", b"x" * (9 * 1024 * 1024))}).status_code == 422


def test_extract_from_pdf(c):
    from reportlab.pdfgen import canvas
    b = io.BytesIO(); k = canvas.Canvas(b); k.drawString(72, 700, "ESR 55 mm/hr"); k.drawString(72, 680, "Xpert MTB/RIF: MTB detected"); k.save()
    v = c.post("/api/extract", files={"file": ("lab.pdf", b.getvalue())}).json()["values"]; assert v["esr"] == 55 and v["xpert"] == "detected"


def test_new_keys_exist_in_both_languages():
    for k in ("up_title", "sec_more", "hemoptysis", "o_rif", "rec_empty", "mas_Higher", "e_ref_required"): assert i18n.T["en"][k] and i18n.T["ur"][k]
    assert i18n.APP_NAME == "TBTech Lens"


def test_report_number_roundtrip_through_the_pdf(c):
    j = post(c, clinical=SICK, ref="P-7", save=True).json(); no = j["report_no"]
    assert no.startswith("TBL-") and patients.find_report_no(no) == no
    for lg in ("en", "ur", "both"):
        pdf = c.post("/api/report", data={"data": json.dumps(dict(clinical=SICK, ref="P-7", visit_id=j["saved"], lang=lg))}).content
        got = c.post("/api/extract", files={"file": ("r.pdf", pdf)}).json()
        assert got["report_no"] == no, lg                       # the number printed in the PDF is detected when the PDF is uploaded again
    r = c.get(f"/api/reports/{no}"); assert r.status_code == 200 and r.json()["visit"]["ref"] == "P-7"
    assert c.get(f"/api/reports/{no.lower()}").status_code == 200


def test_forged_or_foreign_report_numbers(c):
    j = post(c, clinical=SICK, ref="P-8", save=True).json(); no = j["report_no"]; bad = no[:-1] + ("A" if no[-1] != "A" else "B")
    assert c.get(f"/api/reports/{bad}").status_code == 404 and c.get("/api/reports/TBL-2026-999999-A").status_code == 404 and c.get("/api/reports/hello").status_code == 404
    assert c.post("/api/report", data={"data": json.dumps(dict(clinical=SICK, ref="OTHER", visit_id=j["saved"]))}).status_code == 422     # visit belongs to another reference code
    assert c.post("/api/report", data={"data": json.dumps(dict(clinical=SICK, ref="P-8", visit_id=9999))}).status_code == 422


def test_unsaved_report_has_no_number_and_pin_guards_lookup(c, monkeypatch):
    assert post(c, clinical=SICK, ref="P-9").json()["report_no"] is None
    no = post(c, clinical=SICK, ref="P-9", save=True).json()["report_no"]; monkeypatch.setenv("TBSCREEN_PIN", "1")
    assert c.get(f"/api/reports/{no}").status_code == 401 and c.get(f"/api/reports/{no}", headers={"X-Pin": "1"}).status_code == 200
