<p align="center"><img src="assets/molecunova_logo.png" width="260" alt="MolecuNova"></p>

# TBTech Lens

Clinical and chest X-ray screening for tuberculosis, with explanations and a printable report. English and Urdu.
Maintainer: Hammad Anwar, Ali Murtasim.


## What it does
| You give | You get |
|---|---|
| **Clinical data** (age, sex, TB history, symptoms, optional CRP and CAD score) | a result (Lower / Indeterminate / Higher) shown on an animated dial, an impression, SHAP explanation |
| **Chest X-ray** picture (PNG/JPG) | an X-ray result, a map of where the reading looked, a picture-quality check |
| **Both** | the higher of the two levels as the overall result |

Every result comes with **suggested tests and precautions that depend on that patient's result** (level, symptoms, TB history, X-ray finding and picture quality), and a **PDF report** with the SHAP chart and the X-ray map.

## Run
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000        # open http://localhost:8000   (or ./run.sh, or docker compose up --build)
```
Use `app.main:app` (not `app:app`). Interactive API docs: `/docs`. Set `TBSCREEN_API_KEY` to require an `X-API-Key` header on the API.

## Add your X-ray model (train on your own computer)
```bash
pip install torch torchvision pillow scikit-learn onnx onnxscript openpyxl
python scripts/train_xray.py --data /path/to/xray_folder --epochs 12 --out model/xray
```
Class comes from folder or file names (Tuberculosis / TB, Normal). The script tries four activation functions (ReLU, LeakyReLU, GELU, SiLU) on a residual CNN and a pretrained ResNet-18, keeps the best on a validation split, tests on held-out sources or look-alike clusters, and writes `model/xray/xray_model.onnx`, `xray_config.json` and `xray_report.json`. Restart the app: X-ray upload switches on by itself. To use another folder: `TBSCREEN_XRAY_DIR=model/xray_v2`. Read the warnings in `xray_report.json`; details in [docs/XRAY_MODULE.md](docs/XRAY_MODULE.md).

## Repository
`app/` page and entry point · `api/` endpoints · `tbscreen/` engine, advice rules, report, X-ray module · `model/` clinical model (JSON coefficients) · `scripts/` training, retraining on your own data, X-ray training, simulation · `tests/` unit, integration, API and break-it tests · `docs/` model card, break report, simulation, improvements.

## Tests
`pip install -r requirements-dev.txt && python -m pytest tests -q`

## Data and licences
See [DATA_LICENSES.md](DATA_LICENSES.md) and [docs/MODEL_CARD.md](docs/MODEL_CARD.md). Code: MIT.


## Version 3 quick start (Ubuntu / WSL)
```
bash setup_and_run.sh          # installs, starts on http://localhost:8000
bash setup_and_run.sh train    # also trains the X-ray model from ./x-ray first
```
Optional environment: `APP_NAME`, `TBSCREEN_PIN` (protects saving and the records tab), `TBSCREEN_DB`, `TBSCREEN_XRAY_DIR`, `TBSCREEN_API_KEY`.

**Limits to know.** The clinical model was fitted on 117 TB cases; the X-ray accuracy on a public mixed-source set is probably optimistic. The extra findings (HIV, Xpert, ESR ...) are fixed clinical rules, not learned from data. Report reading uses text search and OCR and can misread: always check the filled values. Test on your own hospital's data before relying on any result. Saved records contain health data: use a PIN, HTTPS and your local data-protection rules.
