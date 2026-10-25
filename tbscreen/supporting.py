"""Supporting findings: extra symptoms, risk factors and laboratory results that the statistical model was NOT trained on.
They are applied as transparent rules (never hidden in a score) and are shown to the user as notes. They can raise the overall level; a negative result never lowers it,
because a negative smear or a single negative Xpert does not exclude TB."""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

LV = {"Lower": 0, "Intermediate": 1, "Higher": 2}


class Support(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hemoptysis: bool = False
    breathless: bool = False
    fatigue: bool = False
    appetite_loss: bool = False
    hiv: str = Field("", pattern="^(|pos|neg)$")
    diabetes: bool = False
    contact: bool = False
    smoker: bool = False
    bmi: Optional[float] = Field(None, ge=8, le=70)
    esr: Optional[float] = Field(None, ge=0, le=200)
    wbc: Optional[float] = Field(None, ge=0, le=500)
    hb: Optional[float] = Field(None, ge=2, le=25)
    xpert: str = Field("", pattern="^(|not_detected|detected|rif_resistant)$")
    afb: str = Field("", pattern="^(|neg|pos)$")
    culture: str = Field("", pattern="^(|neg|pos)$")
    igra: str = Field("", pattern="^(|neg|pos)$")
    mantoux_mm: Optional[float] = Field(None, ge=0, le=40)

    def any(self): return any(v not in (False, "", None) for v in self.model_dump().values())


def assess(s, symptomatic):
    """Returns dict(min_level 0-2, notes [(key, kind)], urgent [keys]). kind: raise | info | caution."""
    if s is None: return dict(min_level=0, notes=[], urgent=[])
    lvl, notes, urgent = 0, [], []
    def up(n, key, kind="raise"):
        nonlocal lvl; lvl = max(lvl, n); notes.append((key, kind))
    if s.xpert in ("detected", "rif_resistant"): up(2, "xpert_pos")
    if s.xpert == "rif_resistant": urgent.append("rif_res")
    if s.afb == "pos": up(2, "afb_pos")
    if s.culture == "pos": up(2, "culture_pos")
    if s.hemoptysis: up(1, "hemoptysis"); urgent.append("hemoptysis")
    if s.igra == "pos" or (s.mantoux_mm is not None and s.mantoux_mm >= (5 if s.hiv == "pos" else 10)): up(1, "infection_test", "info")
    if s.hiv == "pos" and (symptomatic or s.breathless or s.fatigue or s.appetite_loss): up(1, "hiv_symptoms")
    rf = [s.hiv == "pos", s.diabetes, s.contact, s.smoker, s.bmi is not None and s.bmi < 18.5, s.esr is not None and s.esr >= 40, s.hb is not None and s.hb < 10]
    extra_sym = s.breathless or s.fatigue or s.appetite_loss
    if sum(rf) >= 2 and (symptomatic or extra_sym): up(1, "multi_risk")
    if s.contact and symptomatic: up(1, "contact_symptoms")
    if s.xpert == "not_detected": notes.append(("xpert_neg", "caution"))
    if s.afb == "neg": notes.append(("afb_neg", "caution"))
    if s.culture == "neg": notes.append(("culture_neg", "caution"))
    if s.esr is not None and s.esr >= 40: notes.append(("esr_high", "info"))
    if s.hb is not None and s.hb < 10: notes.append(("hb_low", "info"))
    if s.wbc is not None and s.wbc > 11: notes.append(("wbc_high", "info"))
    if s.bmi is not None and s.bmi < 18.5: notes.append(("bmi_low", "info"))
    if s.diabetes: notes.append(("diabetes", "info"))
    if s.smoker: notes.append(("smoker", "info"))
    if s.contact: notes.append(("contact", "info"))
    if s.hiv == "pos": notes.append(("hiv", "info"))
    seen, out = set(), []
    for n in notes:
        if n[0] not in seen: seen.add(n[0]); out.append(n)
    return dict(min_level=lvl, notes=out, urgent=urgent)
