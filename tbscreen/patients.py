"""Patient records: every saved screening is a visit under a clinic reference code, so a later visit can be compared with the earlier ones.
Stored: reference code, date, age, sex, TB history, symptoms, CRP, CAD, X-ray level, result levels and positions, and the laboratory outcome when entered.
Never stored: names, phone numbers, ID numbers (the reference code is checked) and the X-ray picture itself."""
import json, re, sqlite3, datetime as dt
from . import store

REF_OK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/\-]{0,39}$")
LV = {"Lower": 0, "Intermediate": 1, "Higher": 2}


def valid_ref(ref):
    ref = (ref or "").strip()
    if not ref: raise ValueError("ref_required")
    if not REF_OK.match(ref): raise ValueError("ref_format")
    if re.search(r"\d{9,}", ref.replace("-", "").replace("/", "")) or re.search(r"\d{5}-\d{7}-\d", ref): raise ValueError("ref_looks_like_id")
    return ref


def _c():
    c = store._c()
    c.execute("""CREATE TABLE IF NOT EXISTS visits(id INTEGER PRIMARY KEY AUTOINCREMENT, ref TEXT NOT NULL, ts TEXT NOT NULL, age REAL, male INTEGER, tb_history TEXT,
                 symptoms TEXT, crp REAL, cad REAL, mode TEXT, tier TEXT, clinical_band TEXT, clinical_pos REAL, xray_band TEXT, xray_pos REAL,
                 overall TEXT, position REAL, outcome TEXT, version TEXT)""")
    c.execute("CREATE INDEX IF NOT EXISTS visits_ref ON visits(ref, ts)")
    return c


def save_visit(ref, res, clinical_input, version):
    ref = valid_ref(ref); c_in = clinical_input or {}; cl = res.get("clinical") or {}; xr = res.get("xray") or {}
    syms = {k: bool(c_in.get(k)) for k in ("cough", "fever", "nightsweats", "weightlost", "chestpain")}
    if c_in.get("cough"): syms["cough_dur"] = c_in.get("cough_dur")
    with _c() as c:
        cur = c.execute("INSERT INTO visits(ref,ts,age,male,tb_history,symptoms,crp,cad,mode,tier,clinical_band,clinical_pos,xray_band,xray_pos,overall,position,outcome,version) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL,?)",
                        (ref, dt.datetime.now().isoformat(timespec="seconds"), c_in.get("age"), None if not c_in else int(bool(c_in.get("male"))), c_in.get("tb_history"), json.dumps(syms),
                         c_in.get("crp"), c_in.get("cad"), res["mode"], cl.get("tier"), cl.get("band"), cl.get("position"), xr.get("band"), xr.get("position"), res["overall"], res["position"], version))
        return cur.lastrowid


def _row(r):
    d = dict(r); d["symptoms"] = json.loads(d["symptoms"] or "{}"); d["report_no"] = report_no(d); return d


def history(ref, limit=50):
    ref = (ref or "").strip()
    if not REF_OK.match(ref): return []
    with _c() as c: return [_row(r) for r in c.execute("SELECT * FROM visits WHERE ref=? ORDER BY ts DESC, id DESC LIMIT ?", (ref, limit))][::-1]


def last_visit(ref):
    h = history(ref, 1000); return h[-1] if h else None


def n_symptoms(s): return sum(bool(s.get(k)) for k in ("cough", "fever", "nightsweats", "weightlost", "chestpain"))


def trend(prev, cur):
    """Compare this result with the previous visit. cur: dict(position, overall, mode, tier, symptoms, ts). A screening score is not a measure of disease course:
    the answer is 'improving / similar / worsening score' and a prompt to confirm with the clinician and laboratory."""
    if not prev: return None
    d = round(cur["position"] - prev["position"], 3)
    label = "improving" if d <= -0.10 else "worsening" if d >= 0.10 else "similar"
    if LV[cur["overall"]] < LV[prev["overall"]]: label = "improving" if d < 0 else label
    if LV[cur["overall"]] > LV[prev["overall"]]: label = "worsening" if d > 0 else label
    days = None
    try: days = (dt.datetime.fromisoformat(cur["ts"]) - dt.datetime.fromisoformat(prev["ts"])).days
    except Exception: pass
    return dict(label=label, delta=d, prev_overall=prev["overall"], prev_ts=prev["ts"], prev_position=prev["position"], days=days,
                comparable=bool(prev.get("mode") == cur.get("mode") and prev.get("tier") == cur.get("tier")),
                symptoms_prev=n_symptoms(prev["symptoms"]), symptoms_now=n_symptoms(cur["symptoms"]), prev_outcome=prev.get("outcome"), visits=None)


def set_outcome(visit_id, outcome):
    if outcome not in ("tb", "not_tb"): raise ValueError("outcome")
    with _c() as c:
        if not c.execute("UPDATE visits SET outcome=? WHERE id=?", (outcome, visit_id)).rowcount: raise KeyError(visit_id)


def list_patients(q="", limit=200):
    q = (q or "").strip()
    with _c() as c:
        rows = c.execute("""SELECT v.ref, COUNT(*) AS visits, MAX(v.ts) AS last_ts,
                            (SELECT overall FROM visits w WHERE w.ref=v.ref ORDER BY ts DESC, id DESC LIMIT 1) AS last_overall,
                            (SELECT position FROM visits w WHERE w.ref=v.ref ORDER BY ts DESC, id DESC LIMIT 1) AS last_position
                            FROM visits v WHERE v.ref LIKE ? ESCAPE '\\' GROUP BY v.ref ORDER BY last_ts DESC LIMIT ?""", ("%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%", limit)).fetchall()
    return [dict(r) for r in rows]


def delete_patient(ref):
    with _c() as c: return c.execute("DELETE FROM visits WHERE ref=?", ((ref or "").strip(),)).rowcount


def export_rows():
    with _c() as c: return [dict(dict(r), report_no=report_no(dict(r))) for r in c.execute("SELECT * FROM visits ORDER BY ref, ts")]


def delete_all():
    with _c() as c: c.execute("DELETE FROM visits")


# ---- report numbers: TBL-<year>-<visit id, 6 digits>-<check letter>. Derived from the saved visit, so the number and the backend record always match.
RN = re.compile(r"\bTBL-(\d{4})-(\d{6})-([A-Z])\b")


def _chk(year, vid): return chr(65 + (int(year) * 7 + int(vid) * 13) % 26)


def report_no(visit):
    y = str(visit["ts"])[:4]; return f"TBL-{y}-{int(visit['id']):06d}-{_chk(y, visit['id'])}"


def find_report_no(text):
    """First valid report number inside any text (a typed number or the text of an uploaded report), or None. A number with a wrong check letter is not accepted."""
    for m in RN.finditer((text or "").upper()):
        if _chk(m.group(1), m.group(2)) == m.group(3): return m.group(0)
    return None


def get_visit(vid):
    with _c() as c:
        r = c.execute("SELECT * FROM visits WHERE id=?", (int(vid),)).fetchone()
    return _row(r) if r else None


def by_report_no(no):
    no = find_report_no(no)
    if not no: return None
    v = get_visit(int(RN.match(no).group(2)))
    return v if v and report_no(v) == no else None
