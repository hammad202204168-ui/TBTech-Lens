"""Screening endpoints for the web page. Three ways in: clinical data only, chest X-ray only, or both (the higher level sets the overall result)."""
import json, os, datetime as dt
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from tbscreen import engine as E, advice, patients, supporting, extract, __version__
from tbscreen.i18n import T, tr, APP_NAME
from tbscreen.modules import xray

router = APIRouter()
LV = {"Lower": 0, "Intermediate": 1, "Higher": 2}; NAME = {v: k for k, v in LV.items()}


class Clinical(BaseModel):
    model_config = ConfigDict(extra="forbid")
    age: float = Field(..., ge=15, le=110)
    male: bool
    tb_history: str = Field("never", pattern="^(never|past|current)$")
    cough: bool = False
    cough_dur: int = Field(0, ge=0, le=5)
    fever: bool = False
    chestpain: bool = False
    nightsweats: bool = False
    weightlost: bool = False
    crp: Optional[float] = Field(None, ge=0, le=900)
    cad: Optional[float] = Field(None, ge=0, le=100)


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clinical: Optional[Clinical] = None
    ref: str = Field("", max_length=100)
    save: bool = False
    visit_id: Optional[int] = Field(None, ge=1)
    support: Optional[supporting.Support] = None
    lang: str = Field("en", pattern="^(en|ur|both)$")


@router.get("/api/i18n")
def i18n(): return T


@router.get("/api/info")
def info(): return dict(xray_available=xray.available(), name=APP_NAME, pin_required=bool(os.environ.get("TBSCREEN_PIN")))


@router.get("/api/mascot/{level}", include_in_schema=False)
def mascot_svg(level: str, bg: int = 1):
    from tbscreen import mascot
    if level not in ("Lower", "Intermediate", "Higher"): raise HTTPException(404, "not_found")
    return Response(mascot.svg(level, 240, bool(bg)), media_type="image/svg+xml")


def parse(data):
    try: return Request(**json.loads(data))
    except (ValueError, TypeError, ValidationError) as e:
        raise HTTPException(422, "invalid data: " + ("; ".join(f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors())[:300] if isinstance(e, ValidationError) else "unreadable"))


def analyze(req, raw):
    """Returns (result for the screen, internals for the PDF)."""
    c = req.clinical; clin = None; xr = dict(provided=False, available=xray.available()); inner = dict(ref=req.ref)
    if c is None and not raw: raise HTTPException(422, "nothing_to_check")
    if c is not None:
        if c.tb_history == "current": raise HTTPException(422, "on_tb_treatment")
        if c.cough and c.cough_dur == 0: raise HTTPException(422, "cough_dur")
        x = c.model_dump(); x["age_group"] = E.age_to_group(c.age); x["prior_tb"] = c.tb_history == "past"; x["cough_dur"] = c.cough_dur if c.cough else 0
        r = E.score(x); clin = dict(band=r["band"], position=r["position"], tier=r["tier"], reasons=[dict(feature=n, effect=round(v, 3)) for n, v in r["shap"][:6] if abs(v) > 0.01])
        inner.update(clinical_input=c.model_dump(), shap=r["shap"], features=r["features"], who_positive=r["who_positive"], cough_2w=r["cough_2w"], warnings=r["warnings"], tier=r["tier"])
    if raw:
        if not xray.available():
            if c is None: raise HTTPException(422, "xray_not_installed")
            xr["error"] = "not_installed"
        else:
            try:
                xray.check_image(raw); q = xray.quality(raw); oc = xray.occlusion(raw); pr = oc["prob"]
                xr.update(provided=True, band=xray.finding(pr), position=xray.position(pr), heat=oc["heat"], grid=oc["grid"], peak=oc["peak"], quality=q["issues"]); inner["image"] = raw
            except ValueError as e:
                if c is None: raise HTTPException(422, "x-ray: " + str(e))
                xr["error"] = str(e)
    levels = [LV[b] for b in (clin and clin["band"], xr.get("band")) if b]; overall = NAME[max(levels)]
    pos = max([p for p in (clin and clin["position"], xr.get("position")) if p is not None])
    sym_any = bool(c and (c.cough or c.fever or c.nightsweats or c.weightlost or c.chestpain))
    sa = supporting.assess(req.support, sym_any)
    if sa["min_level"] > LV[overall]:
        overall = NAME[sa["min_level"]]; pos = max(pos, 0.67 if sa["min_level"] == 2 else 0.34)
    elif sa["min_level"] == 2: pos = max(pos, 0.67)
    inner["support"] = req.support.model_dump() if req.support else None
    a = dict(overall=overall, clinical=clin and clin["band"], xray=xr if xr.get("band") else None, f=inner.get("features"), who_positive=inner.get("who_positive"), cough_2w=inner.get("cough_2w"),
             reasons=inner.get("shap", []), crp=c.crp if c else None, support_urgent=sa["urgent"])
    text = {L: advice.compose(a, L, lambda b, L=L: tr(L, "band_" + b), lambda n, L=L: tr(L, "f_" + n)) for L in ("en", "ur")}
    mode = "both" if (clin and xr.get("band")) else "clinical" if clin else "xray"
    sym = sym_any
    extra = {L: dict(followup=advice.followup(overall, sym, L), about=advice.about(L), factors=advice.patient_factors(a, L)) for L in ("en", "ur")}
    res = dict(mode=mode, overall=overall, position=pos, clinical=clin, xray=xr, text=text, extra=extra, warnings=inner.get("warnings", []))
    # comparison with the previous saved visit of the same reference code
    ref = (req.ref or "").strip(); res["ref"] = ref; res["trend"] = None; res["history"] = []
    if ref:
        try: patients.valid_ref(ref)
        except ValueError as e: raise HTTPException(422, str(e))
        h = patients.history(ref); res["history"] = [dict(id=v["id"], ts=v["ts"], overall=v["overall"], position=v["position"], mode=v["mode"], outcome=v["outcome"]) for v in h]
        if h:
            cs = {k: bool(getattr(c, k)) for k in ("cough", "fever", "nightsweats", "weightlost", "chestpain")} if c else {}
            tr_ = patients.trend(h[-1], dict(position=pos, overall=overall, mode=mode, tier=clin and clin["tier"], symptoms=cs, ts=dt.datetime.now().isoformat(timespec="seconds")))
            if tr_: tr_["visits"] = len(h); res["trend"] = tr_
    res["support_notes"] = {L: dict(zip(("notes", "urgent"), advice.support_notes(sa, L))) for L in ("en", "ur")}
    res["trend_text"] = {L: advice.trend_lines(res["trend"], L, lambda b, L=L: tr(L, "band_" + b)) for L in ("en", "ur")}
    res["report_no"] = None
    if req.visit_id:
        v = patients.get_visit(req.visit_id)
        if not v or v["ref"] != ref: raise HTTPException(422, "visit_not_found")
        res["report_no"] = patients.report_no(v)
    inner["report_no"] = res["report_no"]
    inner.update(support_notes=res["support_notes"], overall=overall, a=a, text=text, mode=mode, xray=xr, extra=extra, trend=res["trend"], trend_text=res["trend_text"], history=res["history"], lang=req.lang)
    return res, inner


@router.post("/api/extract")
async def extract_report(file: UploadFile = File(...)):
    raw = await file.read(extract.MAX_BYTES + 1)
    try:
        out = extract.extract(raw, file.filename or ""); out["report_no"] = patients.find_report_no(out.pop("text", ""))
        return out
    except ValueError as e: raise HTTPException(422, str(e))
    except Exception: raise HTTPException(422, "unreadable_file")


def pin_ok(x_pin: Optional[str] = Header(default=None)):
    want = os.environ.get("TBSCREEN_PIN", "")
    if want:
        import hmac
        if not hmac.compare_digest(want, x_pin or ""): raise HTTPException(401, "pin_required")


def build(auth):
    @router.post("/api/screen", dependencies=[Depends(auth)])
    async def screen(data: str = Form(...), image: Optional[UploadFile] = File(None), x_pin: Optional[str] = Header(default=None)):
        raw = await image.read() if image is not None and image.filename else b""
        req = parse(data)
        if req.save: pin_ok(x_pin)
        res, inner = analyze(req, raw)
        res["saved"] = None
        if req.save:
            try: res["saved"] = patients.save_visit(req.ref, res, inner.get("clinical_input"), __version__)
            except ValueError as e: raise HTTPException(422, str(e))
            res["report_no"] = patients.report_no(patients.get_visit(res["saved"]))
        return res

    @router.post("/api/report", dependencies=[Depends(auth)])
    async def report(data: str = Form(...), image: Optional[UploadFile] = File(None)):
        from tbscreen.clinical_report import make_report
        raw = await image.read() if image is not None and image.filename else b""
        req = parse(data); res, inner = analyze(req, raw)
        return Response(make_report(res, inner, req.lang), media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="report_%s.pdf"' % req.lang})

    @router.get("/api/patients", dependencies=[Depends(auth), Depends(pin_ok)])
    def plist(q: str = ""): return patients.list_patients(q)

    @router.get("/api/patients/export.csv", dependencies=[Depends(auth), Depends(pin_ok)])
    def pexport():
        from tbscreen import store
        import pandas as pd
        rows = patients.export_rows()
        return Response(store.safe_csv(pd.DataFrame(rows or [{"ref": ""}])), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="visits.csv"'})

    @router.get("/api/reports/{no}", dependencies=[Depends(auth), Depends(pin_ok)])
    def report_lookup(no: str):
        v = patients.by_report_no(no)
        if not v: raise HTTPException(404, "not_found")
        return dict(report_no=patients.report_no(v), visit=v, visits=patients.history(v["ref"]))

    @router.get("/api/patients/{ref:path}", dependencies=[Depends(auth), Depends(pin_ok)])
    def pget(ref: str):
        try: patients.valid_ref(ref)
        except ValueError as e: raise HTTPException(422, str(e))
        h = patients.history(ref)
        if not h: raise HTTPException(404, "not_found")
        return dict(ref=ref, visits=h)

    @router.delete("/api/patients/{ref:path}", dependencies=[Depends(auth), Depends(pin_ok)])
    def pdel(ref: str):
        n = patients.delete_patient(ref)
        if not n: raise HTTPException(404, "not_found")
        return dict(deleted=n)

    class Outcome(BaseModel):
        model_config = ConfigDict(extra="forbid")
        outcome: str = Field(..., pattern="^(tb|not_tb)$")

    @router.post("/api/visits/{vid}/outcome", dependencies=[Depends(auth), Depends(pin_ok)])
    def vout(vid: int, o: Outcome):
        try: patients.set_outcome(vid, o.outcome)
        except KeyError: raise HTTPException(404, "not_found")
        return dict(ok=True)
    return router
