"""TB-Screen backend (FastAPI). Run:  uvicorn api.main:app --port 8000   Docs: http://localhost:8000/docs
Set TBSCREEN_API_KEY to require the header `X-API-Key` on every request except /health."""
import os, io, sys, hmac
from pathlib import Path
from typing import Optional
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from tbscreen import engine as E, store, validate, __version__
from tbscreen.modules import xray

app = FastAPI(title="TB-Screen API", version=__version__, description="TB risk screening for adults 15+. Research software, not a medical device.")
KEY = os.environ.get("TBSCREEN_API_KEY")


def auth(x_api_key: Optional[str] = Header(default=None)):
    if KEY and not hmac.compare_digest((x_api_key or "").encode(), KEY.encode()): raise HTTPException(401, "invalid or missing X-API-Key")


from api.screen import build as _build_screen
app.include_router(_build_screen(auth))


class Person(BaseModel):
    model_config = ConfigDict(extra="forbid")          # a misspelt field (e.g. "nightsweat") must be an error, not silently ignored
    age_group: int = Field(..., ge=1, le=5, description="1=15-24, 2=25-34, 3=35-44, 4=45-54, 5=55+")
    male: bool
    prior_tb: bool = False
    on_tb_treatment: bool = False
    cough: bool = False
    cough_dur: int = Field(0, ge=0, le=5, description="0 none,1 <1wk,2 1-2wk,3 2-4wk,4 4wk-3mo,5 3mo+")
    fever: bool = False
    chestpain: bool = False
    nightsweats: bool = False
    weightlost: bool = False
    crp: Optional[float] = Field(None, ge=0, le=900, description="point-of-care CRP, device units (study cut-off 4)")
    cad: Optional[float] = Field(None, ge=0, le=100, description="chest X-ray CAD score 0-100 (e.g. CAD4TB)")
    xray_prob: Optional[float] = Field(None, ge=0, le=1)
    save: bool = False
    site: str = Field("", max_length=100)
    ref: str = Field("", max_length=100, description="clinic reference code; no names or phone numbers")


def pack(r):
    return dict(tier=r["tier"], band=r["band"], probability=round(r["probability"], 4), average_probability=round(r["base_probability"], 4),
                tb_per_100_in_band=round(100 * r["tb_rate_in_band"], 1), who_symptom_screen_positive=r["who_positive"], next_steps=E.next_steps(r),
                inputs_used=r["inputs_used"], out_of_range=r["warnings"], auc_unseen_country=round(r["auc"], 3), auc_ci=[round(v, 3) for v in r["auc_ci"]],
                shap_log_odds=[dict(feature=n, value=round(v, 4)) for n, v in r["shap"]])


@app.get("/health")
def health(): return dict(status="ok", version=__version__, xray_module=xray.available())


@app.post("/predict", dependencies=[Depends(auth)])
def predict(p: Person):
    if p.on_tb_treatment: raise HTTPException(422, "Person is already on TB treatment; screening does not apply.")
    x = p.model_dump(); r = E.score(x); out = pack(r)
    if p.save: out["id"] = store.save(r, {k: v for k, v in x.items() if k not in ("save", "site", "ref")}, p.site, p.ref)
    return out


MAX_BATCH_ROWS, MAX_BATCH_BYTES = 5000, 3_000_000


@app.post("/predict/batch", dependencies=[Depends(auth)])
async def batch(file: UploadFile = File(...)):
    raw = await file.read()
    if len(raw) > MAX_BATCH_BYTES: raise HTTPException(413, f"file too large (limit {MAX_BATCH_BYTES // 1_000_000} MB)")
    try: df = pd.read_csv(io.BytesIO(raw))
    except Exception as e: raise HTTPException(400, f"cannot read CSV: {type(e).__name__}")
    if len(df) > MAX_BATCH_ROWS: raise HTTPException(413, f"too many rows (limit {MAX_BATCH_ROWS})")
    need = [c for c in E.TEMPLATE_COLUMNS if c not in ("id", "crp", "cad", "age")]
    miss = need + (["age or age_group"] if "age" not in df.columns and "age_group" not in df.columns else [])
    miss = [c for c in miss if c in need and c not in df.columns or c == "age or age_group"]
    if miss: raise HTTPException(422, "missing columns: " + ", ".join(miss))
    for c in ("crp", "cad"):
        if c not in df.columns: df[c] = None
    return E.score_table(df).astype(object).where(lambda d: d.notna(), "").to_dict(orient="records")


@app.post("/screenings/{id}/outcome", dependencies=[Depends(auth)])
def outcome(id: int, outcome: str):
    try: store.set_outcome(id, outcome)
    except ValueError as e: raise HTTPException(422, str(e))
    except KeyError: raise HTTPException(404, "unknown id")
    return dict(id=id, outcome=outcome)


@app.get("/screenings", dependencies=[Depends(auth)])
def screenings(site: Optional[str] = Query(None, max_length=100), limit: int = Query(1000, ge=1, le=5000)): return store.rows(site, limit)


@app.get("/validation", dependencies=[Depends(auth)])
def validation(site: Optional[str] = None):
    d = pd.DataFrame(store.rows(site)); 
    if d.empty or d.outcome.notna().sum() == 0: return dict(message="No screenings with a recorded outcome yet.")
    d = d[d.outcome.notna()].copy(); d["outcome_tb"] = (d.outcome == "tb").astype(int)
    res, tab = validate.evaluate(d); return dict(summary=res, bands=tab.to_dict(orient="records"))
