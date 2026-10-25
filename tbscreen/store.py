"""Optional, anonymous screening log (SQLite). No names, phone numbers or IDs are stored unless the clinic types them into `ref`."""
import json, sqlite3, datetime as dt, os
from pathlib import Path

DB = Path(os.environ.get("TBSCREEN_DB", Path(__file__).resolve().parent.parent / "data" / "screenings.db"))


def _c():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB, timeout=30); c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("""CREATE TABLE IF NOT EXISTS screenings(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, site TEXT, ref TEXT, tier TEXT, band TEXT,
                 probability REAL, who_positive INTEGER, inputs TEXT, outcome TEXT)""")
    return c


def save(result, inputs, site="", ref=""):
    with _c() as c:
        cur = c.execute("INSERT INTO screenings(ts,site,ref,tier,band,probability,who_positive,inputs,outcome) VALUES(?,?,?,?,?,?,?,?,NULL)",
                        (dt.datetime.now().isoformat(timespec="seconds"), site, ref, result["tier"], result["band"], result["probability"], int(result["who_positive"]), json.dumps(inputs, default=str)))
        return cur.lastrowid


def set_outcome(id_, outcome):
    """outcome: 'tb' (Xpert/culture positive) or 'not_tb' (negative)."""
    if outcome not in ("tb", "not_tb"): raise ValueError("outcome must be 'tb' or 'not_tb'")
    with _c() as c:
        n = c.execute("UPDATE screenings SET outcome=? WHERE id=?", (outcome, id_)).rowcount
    if not n: raise KeyError(id_)


def rows(site=None, limit=5000):
    q, a = "SELECT * FROM screenings", []
    if site: q += " WHERE site=?"; a.append(site)
    q += " ORDER BY id DESC LIMIT ?"; a.append(limit)
    with _c() as c: return [dict(r) for r in c.execute(q, a)]


def delete_all():
    with _c() as c: c.execute("DELETE FROM screenings")


def safe_csv(df):
    """CSV text that spreadsheets will not run as formulas: any text cell starting with = + - @ (or tab/CR) gets a leading apostrophe."""
    d = df.copy()
    for c in d.columns:
        if d[c].dtype == object or str(d[c].dtype).startswith(("str", "string")):
            d[c] = d[c].map(lambda v: "'" + v if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r") else v)
    return d.to_csv(index=False)
