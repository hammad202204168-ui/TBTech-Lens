"""Read a laboratory or clinic report (PDF, picture or text) and pull out the values this app can use.
Nothing is stored. The person must check the filled values before running the screening. Reports in English; units are converted where unambiguous."""
import io, re, shutil, subprocess

MAX_BYTES = 8 * 1024 * 1024
NUM = r"([0-9]+(?:[.,][0-9]+)?)"


def text_of(raw, name=""):
    n = (name or "").lower()
    if raw[:4] == b"%PDF":
        txt = ""
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw)) as pdf: txt = "\n".join((p.extract_text() or "") for p in pdf.pages[:6])
        except Exception: txt = ""
        if len(txt.strip()) < 20: txt = _ocr_pdf(raw)
        return txt
    if raw[:8] == b"\x89PNG\r\n\x1a\n" or raw[:3] == b"\xff\xd8\xff": return _ocr(raw)
    try: return raw.decode("utf-8")[:200000]
    except UnicodeDecodeError: raise ValueError("unsupported_file")


def _ocr(raw):
    if not shutil.which("tesseract"): raise ValueError("ocr_missing")
    from PIL import Image
    import pytesseract
    im = Image.open(io.BytesIO(raw)); im.load()
    if im.width * im.height > 40_000_000: raise ValueError("image_too_big")
    return pytesseract.image_to_string(im.convert("L"))


def _ocr_pdf(raw):
    if not shutil.which("pdftoppm") or not shutil.which("tesseract"): raise ValueError("ocr_missing")
    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "a.pdf"), "wb").write(raw)
        subprocess.run(["pdftoppm", "-r", "150", "-l", "3", "-png", os.path.join(d, "a.pdf"), os.path.join(d, "p")], check=True, timeout=60, capture_output=True)
        out = []
        for f in sorted(os.listdir(d)):
            if f.endswith(".png"): out.append(_ocr(open(os.path.join(d, f), "rb").read()))
        return "\n".join(out)


def _f(s): return float(s.replace(",", "."))


def _line_value(lines, names, lo, hi):
    """First line mentioning a name followed by a number inside the plausible range. Returns (value, line, unit_text)."""
    for ln in lines:
        low = ln.lower()
        for nm in names:
            m = re.search(nm, low)
            if not m: continue
            tail = low[m.end():]
            for g in re.finditer(NUM, tail):
                v = _f(g.group(1))
                if lo <= v <= hi: return v, ln.strip(), tail[g.end():g.end() + 14]
    return None


def _result(lines, names, pos_words, neg_words):
    for ln in lines:
        low = ln.lower()
        if any(re.search(n, low) for n in names):
            # decide on negative first: "not detected", "negative" contain the positive stems
            if any(re.search(w, low) for w in neg_words): return "neg", ln.strip()
            if any(re.search(w, low) for w in pos_words): return "pos", ln.strip()
    return None


def parse(text):
    lines = [l for l in (text or "").replace("\r", "").split("\n") if l.strip()]
    out, src = {}, {}
    v = _line_value(lines, [r"c[\s\-]*reactive protein", r"\bcrp\b", r"hs[\s\-]?crp"], 0, 900)
    if v:
        val = v[0] * 10 if re.match(r"\s*mg\s*/\s*d", v[2]) else v[0]      # mg/dL -> mg/L
        out["crp"] = round(val, 1); src["crp"] = v[1]
    for key, names, lo, hi in (("esr", [r"\besr\b", r"erythrocyte sedimentation"], 0, 150), ("wbc", [r"\bwbc\b", r"white blood cell", r"total leu[ck]ocyte", r"\btlc\b"], 0.5, 100000),
                               ("hb", [r"h[a]?emoglobin", r"\bhb\b", r"\bhgb\b"], 3, 20)):
        v = _line_value(lines, names, lo, hi)
        if v:
            val = v[0]
            if key == "wbc": val = val / 1000 if val > 100 else val        # 8500 /uL -> 8.5 x10^9/L
            out[key] = round(val, 1); src[key] = v[1]
    v = _line_value(lines, [r"mantoux", r"tuberculin skin", r"\btst\b", r"\bpPD\b".lower()], 0, 40)
    if v: out["mantoux_mm"] = v[0]; src["mantoux_mm"] = v[1]
    for ln in lines:
        low = re.sub(r"mtb\s*[/\-]\s*rif\w*", "mtb", ln.lower())
        if not re.search(r"xpert|genexpert|gene\s?xpert|\bmtb\b", low): continue
        mt = re.search(r"rif\w*", low); mtb, rif = (low[:mt.start()], low[mt.end():]) if mt else (low, "")
        if re.search(r"not detected|negative|undetected|trace", mtb): out["xpert"] = "not_detected"
        elif re.search(r"detected|positive", mtb):
            out["xpert"] = "rif_resistant" if re.search(r"resistan\w*\s*(detected|present|positive)|(detected|positive)\s*resistan|rif\w*\s*(resistant|detected)", low) and not re.search(r"not detected|indeterminate|sensitive|susceptible", rif) else "detected"
        else: continue
        src["xpert"] = ln.strip(); break
    for key, names in (("afb", [r"\bafb\b", r"acid[\s\-]*fast", r"ziehl", r"sputum smear", r"\bz[\s\-]?n\b"]), ("culture", [r"mycobacter\w* culture", r"\bafb culture", r"\btb culture", r"\blj culture", r"\bmgit"]),
                       ("igra", [r"igra", r"quantiferon", r"t[\s\-]?spot", r"interferon"]), ("hiv", [r"\bhiv\b", r"anti[\s\-]?hiv"])):
        r = _result(lines, names, [r"positive", r"reactive", r"\bseen\b", r"grown", r"growth"], [r"negative", r"non[\s\-]?reactive", r"not seen", r"no growth", r"not detected", r"nil", r"absent"])
        if r: out[key] = r[0]; src[key] = r[1]
    m = re.search(r"\bage\s*[:/\-]?\s*(\d{1,3})", (text or "").lower())
    if m and 15 <= int(m.group(1)) <= 110: out["age"] = int(m.group(1)); src["age"] = m.group(0)
    m = re.search(r"\b(?:sex|gender)\s*[:/\-]?\s*(male|female|m|f)\b", (text or "").lower())
    if m: out["male"] = m.group(1).startswith("m") and not m.group(1).startswith("f"); src["male"] = m.group(0)
    if re.search(r"\bhaemoptysis|hemoptysis|blood[\s\-]*stained sputum|coughing (up )?blood", (text or "").lower()): out["hemoptysis"] = True; src["hemoptysis"] = "haemoptysis"
    return dict(values=out, source={k: s[:140] for k, s in src.items()}, chars=len(text or ""))


def extract(raw, name=""):
    if len(raw) > MAX_BYTES: raise ValueError("file_too_big")
    if not raw: raise ValueError("empty_file")
    txt = text_of(raw, name); out = parse(txt); out["text"] = txt[:200000]; return out
