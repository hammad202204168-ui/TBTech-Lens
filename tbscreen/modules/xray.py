"""Chest X-ray module. Switches itself on when model/xray/xray_model.onnx and xray_config.json exist (written by scripts/train_xray.py).
Provides: probability, finding (Lower/Intermediate/Higher), position (0-1 for the gauge), occlusion map (which part of the picture drives the score) and a picture-quality check."""
import io, json, os
from pathlib import Path
import numpy as np

DIR = Path(os.environ.get("TBSCREEN_XRAY_DIR") or Path(__file__).resolve().parent.parent.parent / "model" / "xray")   # TBSCREEN_XRAY_DIR=model/xray_v2 to use another folder
_SESS = {}


def available():
    return (DIR / "xray_model.onnx").exists() and (DIR / "xray_config.json").exists()


def _cfg():
    return json.load(open(DIR / "xray_config.json"))


def check_image(image_bytes, max_mb=10):
    """Reject files that are not a usable chest X-ray picture. Raises ValueError with a short reason."""
    from PIL import Image
    if len(image_bytes) > max_mb * 1_000_000: raise ValueError(f"image larger than {max_mb} MB")
    try:
        im = Image.open(io.BytesIO(image_bytes)); im.verify()
    except Exception: raise ValueError("not a readable PNG or JPG image (DICOM must be exported to PNG/JPG first)")
    w, h = Image.open(io.BytesIO(image_bytes)).size
    if min(w, h) < 128 or max(w, h) > 12000: raise ValueError("image size looks wrong (needs at least 128 pixels on the short side)")
    return w, h


def quality(image_bytes):
    """Simple picture-quality screen. Returns dict(ok, issues) with issue keys q_small / q_dark / q_bright / q_flat."""
    from PIL import Image
    im = Image.open(io.BytesIO(image_bytes)); w, h = im.size; a = np.asarray(im.convert("L").resize((256, 256)), dtype="float32") / 255
    issues = []
    if min(w, h) < 256: issues.append("q_small")
    if a.mean() < 0.12: issues.append("q_dark")
    if a.mean() > 0.85: issues.append("q_bright")
    if a.std() < 0.06: issues.append("q_flat")
    return dict(ok=not issues, issues=issues)


def _session():
    import onnxruntime as ort
    key = str(DIR / "xray_model.onnx"); mt = (DIR / "xray_model.onnx").stat().st_mtime
    if _SESS.get("key") != (key, mt): _SESS.update(key=(key, mt), s=ort.InferenceSession(key))
    return _SESS["s"]


def _gray(image_bytes, size):
    from PIL import Image
    return np.asarray(Image.open(io.BytesIO(image_bytes)).convert("L").resize((size, size)), dtype="float32") / 255.0


def _norm(a, cfg):
    return (a - a.mean()) / (a.std() + 1e-6) if cfg.get("per_image_norm") else (a - cfg.get("mean", 0.5)) / cfg.get("std", 0.25)


def _run(norm2d, cfg):
    ch = int(cfg.get("channels", 1)); x = np.repeat(norm2d[None, None], ch, axis=1) if ch > 1 else norm2d[None, None]
    s = _session(); v = float(s.run(None, {s.get_inputs()[0].name: x.astype("float32")})[0].ravel()[-1])
    return 1 / (1 + np.exp(-v)) if cfg.get("logits", False) else v


def probability(image_bytes):
    """P(TB) from one chest X-ray picture (PNG/JPG). Raises RuntimeError when the module is not installed."""
    if not available(): raise RuntimeError("X-ray model not installed. See docs/XRAY_MODULE.md")
    cfg = _cfg(); return _run(_norm(_gray(image_bytes, int(cfg.get("size", 224))), cfg), cfg)


def finding(prob):
    """Lower = below the 90%-sensitivity cut-off, Higher = above the 90%-specificity cut-off (both chosen on validation images)."""
    c = _cfg(); lo = c.get("thr_low", 0.3); hi = c.get("thr_high", 0.7)
    return "Lower" if prob < lo else "Intermediate" if prob < hi else "Higher"


def position(prob):
    """0..1 position for the gauge: thirds are Lower / Intermediate / Higher."""
    c = _cfg(); lo = c.get("thr_low", 0.3); hi = max(c.get("thr_high", 0.7), lo + 1e-6)
    if prob < lo: return round(0.33 * prob / max(lo, 1e-6), 3)
    if prob < hi: return round(0.33 + 0.34 * (prob - lo) / (hi - lo), 3)
    return round(min(1.0, 0.67 + 0.33 * (prob - hi) / max(1 - hi, 1e-6)), 3)


def occlusion(image_bytes, grid=8):
    """Which part of the picture drives the score: grey out one cell at a time and see how much the score drops.
    Returns dict(prob, heat (grid x grid, 0..1), peak=(row, col)). It shows where the model looked; it is not a diagnosis of a lesion."""
    cfg = _cfg(); size = int(cfg.get("size", 224)); n = _norm(_gray(image_bytes, size), cfg); base = _run(n, cfg); fill = float(n.mean()); step = size // grid
    drop = np.zeros((grid, grid))
    for r in range(grid):
        for c in range(grid):
            m = n.copy(); m[r * step:(r + 1) * step if r < grid - 1 else size, c * step:(c + 1) * step if c < grid - 1 else size] = fill
            drop[r, c] = base - _run(m, cfg)
    pos = np.clip(drop, 0, None); heat = pos / pos.max() if pos.max() > 1e-9 else pos
    pk = np.unravel_index(int(np.argmax(pos)), pos.shape) if pos.max() > 1e-9 else None
    return dict(prob=base, heat=np.round(heat, 3).tolist(), peak=None if pk is None else (int(pk[0]), int(pk[1])), grid=grid)
