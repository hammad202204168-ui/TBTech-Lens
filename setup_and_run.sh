#!/usr/bin/env bash
# One-command setup and start (Ubuntu/WSL).   bash setup_and_run.sh            -> install + start the app on http://localhost:8000
#                                              bash setup_and_run.sh train     -> also train the X-ray model on ./x-ray (Normal/ and Tuberculosis/ folders) first
set -e
cd "$(dirname "$0")"
sudo -n true 2>/dev/null && sudo apt-get install -y python3-venv tesseract-ocr poppler-utils >/dev/null 2>&1 || echo "(tip: sudo apt install python3-venv tesseract-ocr poppler-utils  - needed to read photos/scanned reports)"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q --upgrade pip && pip install -q -r requirements.txt
if [ "$1" = "train" ]; then
  pip install -q torch torchvision onnx --index-url https://download.pytorch.org/whl/cpu || pip install -q torch torchvision onnx
  python scripts/train_xray.py --data x-ray --out model/xray
fi
[ -f model/xray/xray_model.onnx ] || echo "(X-ray model not found in model/xray - clinical mode works; run: bash setup_and_run.sh train)"
echo "Open http://localhost:8000"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
