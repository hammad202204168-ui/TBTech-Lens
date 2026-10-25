"""Train a chest X-ray TB classifier on your own computer and export it for the TB-Screen X-ray module.

  python scripts/train_xray.py --data x-ray --epochs 12
  (default = automatic: sweeps 4 activation functions on a residual CNN, also tries a pretrained ResNet-18 if torchvision is installed, keeps the best on VALIDATION)

Class comes from folder or file names anywhere under --data (Tuberculosis / TB = positive, Normal = negative). Exact duplicate files are used once.
Writes model/xray/xray_model.onnx, xray_config.json (cut-offs included) and xray_report.json.

What makes the test honest ("unseen data")
  * train / validation / test split. The epoch, the activation function and the cut-offs are chosen on validation; the reported AUC is on the untouched test part.
  * the test part is made of images from SOURCES the model never saw: sources are read from *.metadata.xlsx (URL column) when present; otherwise images are
    clustered by appearance and whole clusters are held out, so near-duplicates never sit on both sides. Plain random split is only the last resort and is flagged.
  * a shortcut probe: overall brightness/contrast alone predicting the label is reported; per-image standardisation (on by default) removes that shortcut.
This is NOT a clinical validation. Test on images from your own hospital before any use.
Activation functions: --activation relu|leaky|gelu|silu, or --sweep to try all four briefly and keep the best on validation.
"""
import argparse, json, random, re, sys, hashlib
from pathlib import Path
from urllib.parse import urlparse
import numpy as np
from PIL import Image
import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import GroupShuffleSplit, StratifiedShuffleSplit
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
POS_WORDS = ("tuberculosis", "tb"); NEG_WORDS = ("normal", "healthy", "nontb", "non-tb")
ACT = {"relu": nn.ReLU, "leaky": lambda: nn.LeakyReLU(0.1), "gelu": nn.GELU, "silu": nn.SiLU}


# ------------------------------------------------------------------ data
def label_of(path, root, pos, neg):
    parts = [x.lower() for x in path.relative_to(root).parts[:-1]] + [re.split(r"[_\-\s]", path.stem)[0].lower()]
    P = set(POS_WORDS) | {pos.lower()}; N = set(NEG_WORDS) | {neg.lower()}
    is_p = any(x in P for x in parts); is_n = any(x in N for x in parts)
    return 1 if is_p and not is_n else 0 if is_n and not is_p else None


def read_sources(root, extra):
    """file stem (lower) -> source, from *.metadata.xlsx files (needs openpyxl). Returns {} if none or unreadable."""
    import pandas as pd
    out = {}
    for f in list(Path(root).rglob("*.metadata.xlsx")) + [Path(x) for x in extra]:
        try:
            d = pd.read_excel(f); cols = {str(c).lower().strip(): c for c in d.columns}
            fc = next((c for k, c in cols.items() if "file" in k or "name" in k), None); uc = next((c for k, c in cols.items() if "url" in k or "source" in k), None)
            if fc is None or uc is None: print("metadata", f.name, "has no file/url columns, ignored:", list(d.columns)); continue
            for fn, u in zip(d[fc], d[uc]):
                host = urlparse(str(u)).netloc or str(u)[:40]; out[Path(str(fn)).stem.lower()] = host.lower()
        except Exception as e: print("could not read", f.name, "-", type(e).__name__, "(pip install openpyxl)")
    return out


def collect(data, pos, neg, sources):
    root = Path(data); items = []; seen = {}; dup = 0; unknown = 0; per = {}
    for f in sorted(root.rglob("*")):
        if f.suffix.lower() not in EXT or not f.is_file(): continue
        y = label_of(f, root, pos, neg)
        if y is None: unknown += 1; continue
        h = hashlib.md5(f.read_bytes()).hexdigest()
        if h in seen:
            dup += 1
            if seen[h] != y: print("WARNING: same image under both classes, dropped:", f.name)
            continue
        seen[h] = y; top = f.relative_to(root).parts[0]; per[(top, y)] = per.get((top, y), 0) + 1
        items.append((f, y, sources.get(f.stem.lower())))
    print("images per top folder and class (0=normal, 1=TB):", dict(sorted(per.items())), flush=True)
    print(f"duplicates removed: {dup}; files with unknown class skipped: {unknown}", flush=True)
    if not items or len({y for _, y, _ in items}) < 2: sys.exit("need images of both classes")
    return items


def load(f, size): return np.asarray(Image.open(f).convert("L").resize((size, size)), dtype="float32") / 255.0


def probe(items):
    X = []
    for f, _, _ in items:
        im = Image.open(f); w, h = im.size; a = np.asarray(im.convert("L").resize((32, 32)), dtype="float32") / 255
        X.append([w, h, w / h, a.mean(), a.std(), a[:4].mean(), a[-4:].mean()])
    return np.array(X)


def make_groups(items, IM, seed):
    """source groups from metadata when usable, else appearance clusters. Returns (groups, description)."""
    src = [s for _, _, s in items]
    if sum(s is not None for s in src) >= 0.6 * len(src) and len({s for s in src if s}) >= 4:
        return np.array([s or "unknown" for s in src]), "held-out sources (from metadata URLs)"
    from sklearn.cluster import MiniBatchKMeans
    th = torch.nn.functional.adaptive_avg_pool2d(torch.tensor(IM[:, None].astype("float32") / 255), 16).reshape(len(IM), -1).numpy()
    th = (th - th.mean(1, keepdims=True)) / (th.std(1, keepdims=True) + 1e-6)
    k = int(min(150, max(20, len(IM) // 25))); lab = MiniBatchKMeans(k, random_state=seed, n_init=3).fit_predict(th)
    return np.array([f"c{v}" for v in lab]), f"held-out look-alike clusters ({k} clusters of similar-looking images)"


def split3(y, g, seed, how):
    idx = np.arange(len(y))
    if len(set(g)) >= 4:
        for s in range(seed, seed + 25):
            a, te = next(GroupShuffleSplit(1, test_size=.2, random_state=s).split(idx, y, g)); b, va = next(GroupShuffleSplit(1, test_size=.2, random_state=s).split(a, y[a], g[a]))
            tr, va = a[b], a[va]
            if all(len(set(y[i])) == 2 and (y[i] == 1).sum() >= 10 for i in (tr, va, te)): return tr, va, te, how
        print("group split could not keep both classes in every part; falling back", flush=True)
    a, te = next(StratifiedShuffleSplit(1, test_size=.2, random_state=seed).split(idx, y)); b, va = next(StratifiedShuffleSplit(1, test_size=.2, random_state=seed).split(a, y[a]))
    return a[b], a[va], te, "random (last resort: near-identical images may sit on both sides, AUC can be optimistic)"


# ------------------------------------------------------------------ model
class Block(nn.Module):
    def __init__(self, i, o, act, stride):
        super().__init__(); self.c1 = nn.Conv2d(i, o, 3, stride, 1, bias=False); self.b1 = nn.BatchNorm2d(o); self.c2 = nn.Conv2d(o, o, 3, 1, 1, bias=False); self.b2 = nn.BatchNorm2d(o)
        self.sk = nn.Sequential(nn.Conv2d(i, o, 1, stride, bias=False), nn.BatchNorm2d(o)) if (i != o or stride != 1) else nn.Identity(); self.act = ACT[act]()
    def forward(self, x): return self.act(self.b2(self.c2(self.act(self.b1(self.c1(x))))) + self.sk(x))


def make_net(arch, act):
    if arch in ("resnet18", "efficientnet_b0"):
        try:
            import torchvision
            if arch == "resnet18": m = torchvision.models.resnet18(weights="DEFAULT"); m.fc = nn.Sequential(nn.Dropout(.3), nn.Linear(512, 1))
            else: m = torchvision.models.efficientnet_b0(weights="DEFAULT"); m.classifier = nn.Sequential(nn.Dropout(.3), nn.Linear(1280, 1))
            return m, 3
        except Exception as e: print(f"{arch} unavailable ({type(e).__name__}); using the residual CNN", flush=True)
    A = ACT[act]; chans = (32, 64, 128, 192, 256); L = [nn.Conv2d(1, 24, 3, 2, 1, bias=False), nn.BatchNorm2d(24), A()]; c = 24
    for o in chans: L += [Block(c, o, act, 2), Block(o, o, act, 1)]; c = o
    return nn.Sequential(*L, nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(.3), nn.Linear(c, 1)), 1


def augment(x):
    n = x.shape[0]; ang = (torch.rand(n) - .5) * 2 * np.deg2rad(7); sc = 1 + (torch.rand(n) - .5) * .16; tx, ty = (torch.rand(n) - .5) * .1, (torch.rand(n) - .5) * .1
    th = torch.stack([torch.stack([sc * torch.cos(ang), -sc * torch.sin(ang), tx], 1), torch.stack([sc * torch.sin(ang), sc * torch.cos(ang), ty], 1)], 1)
    x = F.grid_sample(x, F.affine_grid(th, x.shape, align_corners=False), padding_mode="border", align_corners=False)
    return x * (1 + (torch.rand(n, 1, 1, 1) - .5) * .2) + (torch.rand(n, 1, 1, 1) - .5) * .2


def boot_ci(y, p, n=1000, seed=0):
    r = np.random.default_rng(seed); v = []
    for _ in range(n):
        i = r.integers(0, len(y), len(y))
        if len(set(y[i])) == 2: v.append(roc_auc_score(y[i], p[i]))
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--pos", default="Tuberculosis"); ap.add_argument("--neg", default="Normal")
    ap.add_argument("--size", type=int, default=224); ap.add_argument("--epochs", type=int, default=12); ap.add_argument("--batch", type=int, default=32); ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--arch", default="auto", choices=["auto", "cnn", "resnet18", "efficientnet_b0"]); ap.add_argument("--activation", default="silu", choices=list(ACT))
    ap.add_argument("--no-sweep", action="store_true", help="skip the activation-function sweep (default: sweep ReLU/LeakyReLU/GELU/SiLU and keep the best on validation)"); ap.add_argument("--sweep-epochs", type=int, default=3)
    ap.add_argument("--no-per-image-norm", action="store_true", help="default is to standardise every image by its own mean/std (removes brightness/contrast shortcuts)"); ap.add_argument("--metadata", nargs="*", default=[]); ap.add_argument("--max-images", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", default=str(ROOT / "model" / "xray"))
    ap.add_argument("--per-image-norm", action="store_true", help="(on by default; kept so old commands still work)"); ap.add_argument("--sweep", action="store_true", help="(on by default)")
    a = ap.parse_args(); a.per_image_norm = not a.no_per_image_norm; a.sweep = not a.no_sweep; random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    items = collect(a.data, a.pos, a.neg, read_sources(a.data, a.metadata))
    if a.max_images: random.shuffle(items); items = items[:a.max_images]
    y = np.array([i[1] for i in items]); print(f"{len(items)} images, {int(y.sum())} TB", flush=True)
    print("loading images into memory once ...", flush=True)
    IM = np.stack([(load(f, a.size) * 255).astype("uint8") for f, _, _ in items]); print("loaded", IM.shape, flush=True)
    g, how = make_groups(items, IM, a.seed); tr, va, te, how = split3(y, g, a.seed, how)
    print(f"split: {how}; train {len(tr)}, validation {len(va)}, test {len(te)} (TB: {int(y[tr].sum())}/{int(y[va].sum())}/{int(y[te].sum())})", flush=True)
    M = probe(items); mu, sd = M[tr].mean(0), M[tr].std(0) + 1e-6
    shortcut_auc = float(roc_auc_score(y[te], LogisticRegression(max_iter=2000).fit((M[tr] - mu) / sd, y[tr]).predict_proba((M[te] - mu) / sd)[:, 1]))
    mean, std = 0.5, 0.25; dev = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("device:", dev, flush=True)

    def prep(idx, ch, train=False):
        x = IM[idx].astype("float32") / 255
        x = (x - x.mean((1, 2), keepdims=True)) / (x.std((1, 2), keepdims=True) + 1e-6) if a.per_image_norm else (x - mean) / std
        x = torch.tensor(x)[:, None]; x = augment(x) if train else x
        return (x.repeat(1, 3, 1, 1) if ch == 3 else x).to(dev)

    def predict(net, ch, idx):
        net.eval(); out = []
        with torch.no_grad():
            for k in range(0, len(idx), 64): out += torch.sigmoid(net(prep(idx[k:k + 64], ch)).squeeze(1)).cpu().tolist()
        return np.array(out)

    def fit(arch, act, epochs, tag):
        torch.manual_seed(a.seed); net, ch = make_net(arch, act); net.to(dev); w = torch.tensor((len(tr) - y[tr].sum()) / max(1, y[tr].sum())); lossf = nn.BCEWithLogitsLoss(pos_weight=w.to(dev))
        opt = torch.optim.AdamW(net.parameters(), a.lr, weight_decay=1e-4); steps = max(1, -(-len(tr) // a.batch))
        sch = torch.optim.lr_scheduler.OneCycleLR(opt, a.lr, total_steps=max(20, epochs * steps), pct_start=.25); best = (-1, None, 0)
        for ep in range(epochs):
            net.train(); order = np.random.permutation(tr); tot = 0
            for k in range(0, len(order), a.batch):
                idx = order[k:k + a.batch]; x = prep(idx, ch, True); t = torch.tensor(y[idx], dtype=torch.float32).to(dev)
                opt.zero_grad(); l = lossf(net(x).squeeze(1), t); l.backward(); nn.utils.clip_grad_norm_(net.parameters(), 2.0); opt.step(); sch.step(); tot += l.item() * len(idx)
            v = float(roc_auc_score(y[va], predict(net, ch, va))); print(f"[{tag}] epoch {ep + 1}/{epochs}: train loss {tot / len(tr):.3f}  validation AUC {v:.3f}", flush=True)
            if v > best[0]: best = (v, {k: t.clone() for k, t in net.state_dict().items()}, ep + 1)
        net.load_state_dict(best[1]); return net, ch, best

    sweep = {}; act = a.activation; cands = []
    archs = ["cnn", "resnet18"] if a.arch == "auto" else [a.arch]
    for arch in archs:
        if arch == "resnet18":
            try: import torchvision; torchvision.models.resnet18(weights="DEFAULT")
            except Exception as e: print("resnet18 (pretrained) skipped:", type(e).__name__, "- pip install torchvision and allow internet to enable it", flush=True); continue
        ac = act
        if arch == "cnn" and a.sweep:
            sw = {n: fit("cnn", n, a.sweep_epochs, "sweep " + n)[2][0] for n in ACT}; sweep = sw; ac = max(sw, key=sw.get)
            print("activation sweep (validation AUC):", {k: round(v, 3) for k, v in sw.items()}, "-> using", ac, flush=True)
        n_, c_, b_ = fit(arch, ac, a.epochs, arch + ("/" + ac if arch == "cnn" else "")); cands.append((b_[0], arch, ac if arch == "cnn" else "pretrained", n_, c_, b_))
    cands.sort(key=lambda t: -t[0]); print("candidates (validation AUC):", {f"{c[1]}/{c[2]}": round(c[0], 4) for c in cands}, "-> chosen", cands[0][1], flush=True)
    _, arch_used, act, net, ch, best = cands[0]
    pv, p = predict(net, ch, va), predict(net, ch, te); auc = float(roc_auc_score(y[te], p)); ci = boot_ci(y[te], p)
    fpr, tpr, thr = roc_curve(y[va], pv)       # cut-offs from VALIDATION images only
    thr_low = float(thr[np.argmax(tpr >= 0.90)]) if (tpr >= 0.90).any() else 0.3
    thr_high = float(thr[np.where(fpr <= 0.10)[0][-1]]) if (fpr <= 0.10).any() else 0.7
    thr_low, thr_high = min(thr_low, thr_high), max(thr_low, thr_high)
    sens_low = float((p[y[te] == 1] >= thr_low).mean()); spec_high = float((p[y[te] == 0] < thr_high).mean())
    per_src = {}
    if "sources" in how:
        for s in sorted(set(g[te])):
            m = g[te] == s
            if len(set(y[te][m])) == 2: per_src[s] = round(float(roc_auc_score(y[te][m], p[m])), 3)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); net.cpu().eval()
    torch.onnx.export(net, torch.zeros(1, ch, a.size, a.size), str(out / "xray_model.onnx"), input_names=["image"], output_names=["logit"], opset_version=17, dynamo=False)
    json.dump(dict(size=a.size, channels=ch, mean=mean, std=std, per_image_norm=bool(a.per_image_norm), logits=True, thr_low=thr_low, thr_high=thr_high), open(out / "xray_config.json", "w"), indent=1)
    warn = []
    if shortcut_auc > .75 and not a.per_image_norm: warn.append(f"Brightness/contrast alone predict the label (AUC {shortcut_auc:.2f}). Per-image standardisation is switched off; leave it on.")
    if shortcut_auc > .75 and a.per_image_norm: warn.append(f"Brightness/contrast alone would predict the label (AUC {shortcut_auc:.2f}); per-image standardisation was used to remove it, but other source cues (borders, text marks, scanner texture) may remain.")
    if auc > .97: warn.append("AUC above 0.97 on public X-ray sets is a classic sign of source shortcuts. Test on images from another hospital before trusting it.")
    if how.startswith("random"): warn.append("The split is random, so the AUC can be optimistic.")
    rep = dict(arch=arch_used, candidates_val_auc={f"{c[1]}/{c[2]}": round(c[0], 4) for c in cands}, activation=act, activation_sweep_val_auc=sweep, per_image_norm=bool(a.per_image_norm), n_images=len(items), n_tb=int(y.sum()), split=how, n_train=len(tr), n_val=len(va), n_test=len(te),
               best_epoch=best[2], validation_auc=best[0], test_auc=auc, test_auc_ci95=ci, test_sensitivity_at_low_cutoff=sens_low, test_specificity_at_high_cutoff=spec_high,
               test_auc_per_unseen_source=per_src, shortcut_probe_auc=shortcut_auc, warnings=warn, note="Not a clinical validation. Test on images from your own hospital before use.")
    json.dump(rep, open(out / "xray_report.json", "w"), indent=1); print(json.dumps(rep, indent=1))


if __name__ == "__main__": main()
