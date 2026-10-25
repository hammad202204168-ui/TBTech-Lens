"""PDF report in English, Urdu or both (one language after the other). Urdu text is shaped (arabic_reshaper) and reordered (bidi) and wrapped by a small RTL flowable."""
import io, datetime as dt, os
from pathlib import Path
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, Flowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from . import __version__, mascot
from .i18n import tr, DUR, APP_NAME

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
UR, URB = "NaskhR", "NaskhB"
for nm, fn in ((UR, "NotoNaskhArabic_400Regular.ttf"), (URB, "NotoNaskhArabic_700Bold.ttf")):
    try: pdfmetrics.getFont(nm)
    except KeyError: pdfmetrics.registerFont(TTFont(nm, str(FONTS / fn)))

INK, CAR, AMB, GOLD, CREAM = "#3B2A1F", "#C9782B", "#F5A524", "#FFC83D", "#FFF8EC"
BAND = {"Lower": "#2FA37A", "Intermediate": "#F29D1F", "Higher": "#E5484D"}
BANDBG = {"Lower": "#E6F7EE", "Intermediate": "#FFF3DC", "Higher": "#FFE6E3"}

RP = {  # report-only labels
 "en": dict(title="Screening report", date="Date", ref="Reference", ver="Version", rno="Report no.", unsaved="not saved", none="not given", clin="Clinical result", xr="X-ray result", nd="not done", bad="could not be used", yes="Yes", no="No",
            info="Information entered", age="Age", years="years", sex="Sex", tbh="Earlier TB treatment", crp="CRP", cad="CAD score", dur="Cough duration", sup="Additional findings", notes="Notes on these findings",
            hist="Visit history", date_c="Date", res_c="Result", sc_c="Score", lab_c="Lab result", lab_tb="TB confirmed", lab_not="TB not found", pg="page", hiv="HIV", pos="Positive", neg="Negative", unk="not given",
            hemoptysis="Coughing up blood", breathless="Breathlessness", fatigue="Tiredness", appetite_loss="Loss of appetite", diabetes="Diabetes", contact="Contact with a TB patient", smoker="Smoker", bmi="BMI", esr="ESR (mm/h)",
            wbc="White cells (x10^9/L)", hb="Haemoglobin (g/dL)", xpert="Xpert", afb="Sputum smear (AFB)", culture="Culture", igra="IGRA", mantoux="Skin test (mm)", xdet="MTB detected", xnot="MTB not detected", xrif="MTB detected, rifampicin resistance",
            shapt="SHAP: what moved the clinical score", xt="Chest X-ray reading", xa="Chest X-ray as submitted", xb="Where the reading looked", prev="Earlier visits", sc_note="Score 0-100 (not a probability)", lbl_low="Lower", lbl_mid="Indeterminate", lbl_hi="Higher"),
 "ur": dict(title="جانچ کی رپورٹ", date="تاریخ", ref="حوالہ", ver="ورژن", rno="رپورٹ نمبر", unsaved="محفوظ نہیں", none="درج نہیں", clin="کلینیکل نتیجہ", xr="ایکسرے کا نتیجہ", nd="نہیں ہوا", bad="استعمال نہیں ہو سکا", yes="ہاں", no="نہیں",
            info="درج کردہ معلومات", age="عمر", years="سال", sex="جنس", tbh="پہلے ٹی بی کا علاج", crp="سی آر پی", cad="CAD اسکور", dur="کھانسی کا دورانیہ", sup="اضافی معلومات", notes="ان معلومات پر نوٹس",
            hist="وزٹس کی تاریخ", date_c="تاریخ", res_c="نتیجہ", sc_c="اسکور", lab_c="لیبارٹری نتیجہ", lab_tb="ٹی بی کی تصدیق", lab_not="ٹی بی نہیں ملی", pg="صفحہ", hiv="ایچ آئی وی", pos="مثبت", neg="منفی", unk="درج نہیں",
            hemoptysis="کھانسی میں خون", breathless="سانس پھولنا", fatigue="تھکاوٹ", appetite_loss="بھوک کی کمی", diabetes="ذیابیطس", contact="ٹی بی مریض سے رابطہ", smoker="تمباکو نوشی", bmi="بی ایم آئی", esr="ای ایس آر (mm/h)",
            wbc="سفید خلیات (x10^9/L)", hb="ہیموگلوبن (g/dL)", xpert="ایکسپرٹ", afb="بلغم کی سمیئر (AFB)", culture="کلچر", igra="آئی جی آر اے", mantoux="جلد کا ٹیسٹ (mm)", xdet="ٹی بی کے جراثیم ملے", xnot="جراثیم نہیں ملے", xrif="جراثیم ملے، رائفیمپیسن مزاحمت",
            shapt="SHAP: کلینیکل اسکور کو کس نے بدلا", xt="سینے کے ایکسرے کی پڑھائی", xa="جمع کرایا گیا ایکسرے", xb="پڑھائی نے کہاں دیکھا", prev="پچھلی وزٹس", sc_note="اسکور 0-100 (امکان نہیں)", lbl_low="کم", lbl_mid="غیر واضح", lbl_hi="زیادہ"),
}


def shape(s):
    import arabic_reshaper
    from bidi.algorithm import get_display
    return get_display(arabic_reshaper.reshape(str(s)), base_dir="R")


class UrPara(Flowable):
    """Right-to-left paragraph: wraps logical words, then shapes and reorders each line."""
    def __init__(self, text, size=10.5, font=UR, color=INK, leading=None, bullet=False, align="R"):
        super().__init__(); self.text, self.size, self.font, self.color = ("• " if bullet else "") + str(text), size, font, color; self.leading = leading or size * 1.9; self.align = align
    def wrap(self, aw, ah):
        self.aw = aw; words, lines, cur = self.text.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if cur and stringWidth(shape(t), self.font, self.size) > aw: lines.append(cur); cur = w
            else: cur = t
        lines.append(cur); self.lines = lines; self.height = self.leading * len(lines); return aw, self.height
    def split(self, aw, ah): return []
    def draw(self):
        c = self.canv; c.setFont(self.font, self.size); c.setFillColor(colors.HexColor(self.color)); y = self.height - self.leading * 0.72
        for ln in self.lines:
            s = shape(ln)
            (c.drawRightString(self.aw, y, s) if self.align == "R" else c.drawCentredString(self.aw / 2, y, s)); y -= self.leading


def _png(fig, face="white"):
    import matplotlib.pyplot as plt
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=200, bbox_inches="tight", facecolor=face); plt.close(fig); b.seek(0); return b


def _mpl_text(L):
    import matplotlib; matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    fp = fm.FontProperties(fname=str(FONTS / "NotoNaskhArabic_400Regular.ttf")) if L == "ur" else None
    return (lambda s: shape(s)) if L == "ur" else (lambda s: s), fp


def shap_chart(shap, L):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    f, fp = _mpl_text(L); rows = [(tr(L, "f_" + n), v) for n, v in shap if abs(v) > 0.005][:8][::-1]
    if not rows: return None
    fig, ax = plt.subplots(figsize=(6.2, 0.45 * len(rows) + 0.9)); vals = [v for _, v in rows]
    ax.barh(range(len(rows)), vals, color=[BAND["Higher"] if v > 0 else "#2F8FBF" for v in vals], height=0.6)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([f(r[0]) for r in rows], fontproperties=fp, fontsize=9)
    for i, v in enumerate(vals): ax.text(v + (0.02 if v >= 0 else -0.02), i, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=8, color=INK)
    ax.axvline(0, color=INK, linewidth=0.8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=8, colors=INK); lim = max(abs(min(vals)), abs(max(vals)), 0.1) * 1.4; ax.set_xlim(-lim, lim)
    ax.set_xlabel(f(tr(L, "lowers") + "   |   " + tr(L, "raises")) if L == "ur" else "lowers  <  0  >  raises", fontproperties=fp, fontsize=9, color=INK)
    return _png(fig)


def trend_chart(hist, L):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    f, fp = _mpl_text(L); fig, ax = plt.subplots(figsize=(6.2, 2.2)); n = len(hist); xs = list(range(n))
    for a, b, c in ((0, 1 / 3, BANDBG["Lower"]), (1 / 3, 2 / 3, BANDBG["Intermediate"]), (2 / 3, 1, BANDBG["Higher"])): ax.axhspan(a, b, color=c)
    ys = [h["position"] for h in hist]; ax.plot(xs, ys, color="#7C4A1D", linewidth=2)
    for x, h in zip(xs, hist): ax.scatter([x], [h["position"]], s=70, color=BAND[h["overall"]], edgecolor="white", zorder=3)
    ax.set_ylim(0, 1); ax.set_xlim(-0.4, max(n - 1, 1) + 0.4); ax.set_xticks(xs); ax.set_xticklabels([h["ts"][5:10] for h in hist], fontsize=8)
    ax.set_yticks([1 / 6, 0.5, 5 / 6]); ax.set_yticklabels([f(RP[L]["lbl_low"]), f(RP[L]["lbl_mid"]), f(RP[L]["lbl_hi"])], fontproperties=fp, fontsize=8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    return _png(fig)


def xray_overlay(raw, heat, L):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from PIL import Image
    f, fp = _mpl_text(L); im = Image.open(io.BytesIO(raw)).convert("L"); im.thumbnail((700, 700)); h = np.array(heat, dtype="float32")
    hm = np.asarray(Image.fromarray((h * 255).astype("uint8")).resize(im.size, Image.BICUBIC), dtype="float32") / 255
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.4))
    axs[0].imshow(im, cmap="gray"); axs[0].set_title(f(RP[L]["xa"]), fontsize=9, color=INK, fontproperties=fp)
    axs[1].imshow(im, cmap="gray"); axs[1].imshow(hm, cmap="YlOrBr", alpha=0.55 * (hm > 0.05), vmin=0, vmax=1); axs[1].set_title(f(RP[L]["xb"]), fontsize=9, color=INK, fontproperties=fp)
    for a in axs: a.axis("off")
    return _png(fig)


def mascot_flow(level, cm_size=4.2):
    from svglib.svglib import svg2rlg
    d = svg2rlg(io.BytesIO(mascot.svg(level, 200).encode())); s = cm_size * cm / d.width; d.scale(s, s); d.width *= s; d.height *= s; return d


def section(res, inner, L):
    """All flowables for one language."""
    R = RP[L]; rtl = L == "ur"; O = res["overall"]; txt = res["text"][L]; ex = res["extra"][L]; x = res["xray"]; el = []
    ss = getSampleStyleSheet(); fn, fb = ("Helvetica", "Helvetica-Bold") if not rtl else (UR, URB)
    body = ParagraphStyle("b", parent=ss["Normal"], fontName=fn, fontSize=9.6, leading=14, textColor=colors.HexColor(INK))
    small = ParagraphStyle("s", parent=body, fontSize=8, leading=11)
    P = lambda s, st=None, bullet=False: (UrPara(s, size=10 if st is not small else 8.5, bullet=bullet) if rtl else Paragraph(("• " if bullet else "") + str(s).replace("&", "&amp;").replace("<", "&lt;"), st or body))
    def H(s):
        return UrPara(s, size=13, font=URB, color=CAR) if rtl else Paragraph(str(s), ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor(CAR), spaceBefore=10, spaceAfter=4))
    def row2(a, b): return [P(b), P(a)] if rtl else [P(a), P(b)]
    def tbl(rows, w1=6 * cm, w2=10.4 * cm, grid=True):
        rr = [row2(a, b) for a, b in rows]; t = Table(rr, colWidths=[w2, w1] if rtl else [w1, w2])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#F0E1CC")), ("BACKGROUND", (1 if rtl else 0, 0), (1 if rtl else 0, -1), colors.HexColor(CREAM)), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)])); return t
    # banner
    ttl = ParagraphStyle("t", parent=body, fontName="Helvetica-Bold", fontSize=22, textColor=colors.white, leading=26)
    meta = [f"{R['date']}: {dt.date.today().isoformat()}", f"{R['ref']}: {inner.get('ref') or R['none']}", f"{R['rno']}: {inner.get('report_no') or R['unsaved']}", f"{R['ver']} {__version__}"]
    if rtl: left, right = UrPara("  |  ".join(meta[::-1]), 8.5, color="#FFFFFF", align="R"), UrPara(APP_NAME + " — " + R["title"], 16, font=URB, color="#FFFFFF")
    else: left, right = Paragraph(f"{APP_NAME}<br/><font size=10>{R['title']}</font>", ttl), Paragraph("<br/>".join(meta), ParagraphStyle("r", parent=body, textColor=colors.white, alignment=2))
    head = Table([[left, right] if not rtl else [left, right]], colWidths=[11 * cm, 5.4 * cm] if not rtl else [8 * cm, 8.4 * cm])
    head.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(AMB)), ("LINEBELOW", (0, 0), (-1, -1), 4, colors.HexColor(CAR)), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 14), ("BOTTOMPADDING", (0, 0), (-1, -1), 14), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12)]))
    el += [head, Spacer(1, 10)]
    # verdict with mascot
    vtxt = [UrPara(tr(L, "band_" + O), 18, font=URB, color=BAND[O]), Spacer(1, 4), UrPara(tr(L, "bt_" + O), 10)] if rtl else [Paragraph(f"<font color='{BAND[O]}' size=18><b>{tr(L, 'band_' + O)}</b></font>", ParagraphStyle("v", parent=body, leading=24)), Spacer(1, 3), Paragraph(tr(L, "bt_" + O), body)]
    cells = [mascot_flow(O), vtxt]; cw = [4.6 * cm, 11.8 * cm]
    if rtl: cells, cw = cells[::-1], cw[::-1]
    ov = Table([cells], colWidths=cw); ov.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.HexColor(BAND[O])), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(BANDBG[O])), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    el += [ov, Spacer(1, 6)]
    parts = []
    if res["clinical"]: parts.append((R["clin"], tr(L, "band_" + res["clinical"]["band"])))
    parts.append((R["xr"], tr(L, "x_" + x["band"]) if x.get("band") else R["nd"] + (f" ({R['bad']})" if x.get("error") else "")))
    el += [tbl(parts, 4.2 * cm, 12.2 * cm), H(tr(L, "res_imp"))] + [P(s, bullet=True) for s in txt["impression"]]
    # trend
    if res.get("trend"):
        el += [H(tr(L, "res_trend"))] + [P(s) for s in res["trend_text"][L]]
        hist = res["history"] + [dict(ts=dt.date.today().isoformat(), position=res["position"], overall=O)]
        el += [RLImage(trend_chart(hist, L), width=14 * cm, height=14 * cm * 0.36, kind="proportional")]
    c = inner.get("clinical_input")
    if c:
        yn = lambda v: R["yes"] if v else R["no"]; f = inner["features"]
        rows = [(R["age"], f"{c['age']:.0f} {R['years']}"), (R["sex"], tr(L, "male") if c["male"] else tr(L, "female")), (R["tbh"], yn(c["tb_history"] == "past"))]
        rows += [(tr(L, "f_" + s), yn(c[s])) for s in ("cough", "fever", "nightsweats", "weightlost", "chestpain")]
        if c["cough"]: rows.append((R["dur"], tr(L, DUR[f["cough_dur"]])))
        rows += [(R["crp"], f"{c['crp']} mg/L" if c.get("crp") is not None else R["nd"]), (R["cad"], str(c["cad"]) if c.get("cad") is not None else R["nd"])]
        el += [H(R["info"]), tbl(rows)]
    sp = inner.get("support")
    if sp:
        rows = []
        for k in ("hemoptysis", "breathless", "fatigue", "appetite_loss", "diabetes", "contact", "smoker"):
            if sp.get(k): rows.append((R[k], R["yes"]))
        if sp.get("hiv"): rows.append((R["hiv"], R["pos"] if sp["hiv"] == "pos" else R["neg"]))
        for k in ("bmi", "esr", "wbc", "hb"):
            if sp.get(k) is not None: rows.append((R[k], str(sp[k])))
        if sp.get("mantoux_mm") is not None: rows.append((R["mantoux"], str(sp["mantoux_mm"])))
        if sp.get("xpert"): rows.append((R["xpert"], R[{"detected": "xdet", "not_detected": "xnot", "rif_resistant": "xrif"}[sp["xpert"]]]))
        for k in ("afb", "culture", "igra"):
            if sp.get(k): rows.append((R[k], R["pos"] if sp[k] == "pos" else R["neg"]))
        if rows: el += [H(R["sup"]), tbl(rows)]
        sn = (inner.get("support_notes") or {}).get(L, {}).get("notes", [])
        if sn: el += [H(R["notes"])] + [P(n["text"], bullet=True) for n in sn]
    if c:
        ch = shap_chart(inner["shap"], L)
        if ch: el += [KeepTogether([H(R["shapt"]), P(tr(L, "why_plain")), RLImage(ch, width=15 * cm, height=7.5 * cm, kind="proportional"), P(tr(L, "why_note"), small)])]
    if x.get("heat") and inner.get("image"):
        el += [KeepTogether([H(R["xt"]), RLImage(xray_overlay(inner["image"], x["heat"], L), width=15 * cm, height=8 * cm, kind="proportional"), P(tr(L, "heat_note"), small)])]
    if txt["tests"]:
        t = Table([row2(f"{n}", w) if not rtl else [P(w), UrPara(n, 10, font=URB)] for n, w in txt["tests"]], colWidths=[10.2 * cm, 6.2 * cm] if rtl else [6.2 * cm, 10.2 * cm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), .3, colors.HexColor("#F0E1CC")), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        el += [KeepTogether([H(tr(L, "res_tests")), t])]
    if txt["precautions"]: el += [KeepTogether([H(tr(L, "res_prec"))] + [P(s, bullet=True) for s in txt["precautions"]])]
    urg = ([txt["urgent"]] if txt["urgent"] else []) + (res.get("support_notes", {}).get(L, {}).get("urgent", []))
    if urg:
        u = Table([[ [P(s) for s in urg] ]], colWidths=[16.4 * cm]); u.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(BANDBG["Higher"])), ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(BAND["Higher"])), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        el += [Spacer(1, 8), u]
    fu = Table([[P(f"{tr(L, 'res_follow')}: {ex['followup']}")]], colWidths=[16.4 * cm]); fu.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF6FF")), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    el += [Spacer(1, 8), fu, H(tr(L, "res_factors"))] + [P(s, bullet=True) for s in ex["factors"]]
    el += [KeepTogether([H(ex["about"]["title"])] + [P(s) for s in ex["about"]["paragraphs"]])]
    el += [Spacer(1, 12), P(tr(L, "disclaimer"), small)]
    return el


def make_report(res, inner, lang="en"):
    buf = io.BytesIO(); doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.4 * cm, bottomMargin=1.6 * cm, title=f"{APP_NAME} report", author=APP_NAME)
    langs = ["en", "ur"] if lang == "both" else [lang if lang in ("en", "ur") else "en"]; el = []
    for i, L in enumerate(langs):
        if i: el.append(PageBreak())
        el += section(res, inner, L)

    def foot(c_, d):
        c_.saveState(); c_.setFillColor(colors.HexColor(GOLD)); c_.rect(0, 0, A4[0], 0.35 * cm, stroke=0, fill=1); c_.setFont("Helvetica", 7.5); c_.setFillColor(colors.HexColor(CAR))
        c_.drawString(1.8 * cm, 0.7 * cm, f"{APP_NAME} {__version__} · MolecuNova · {d.page}"); c_.restoreState()
    doc.build(el, onFirstPage=foot, onLaterPages=foot); return buf.getvalue()
