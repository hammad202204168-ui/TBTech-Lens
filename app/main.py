"""One-command entrypoint (API + clinical web page):   python -m uvicorn app.main:app --port 8000
Open http://localhost:8000  (API docs: /docs)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.main import app

STATIC = Path(__file__).resolve().parent / "static"


@app.middleware("http")
async def headers(request, call_next):
    r = await call_next(request)
    r.headers.setdefault("X-Content-Type-Options", "nosniff"); r.headers.setdefault("X-Frame-Options", "DENY"); r.headers.setdefault("Referrer-Policy", "no-referrer")
    r.headers.setdefault("Cache-Control", "no-store")
    return r


@app.get("/", include_in_schema=False)
def home(): return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
app.mount("/assets", StaticFiles(directory=Path(__file__).resolve().parent.parent / "assets"), name="assets")
