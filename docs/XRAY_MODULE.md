# Adding the chest X-ray module

Today the app takes a **CAD score typed in** from a CAD program (for example CAD4TB). That tier is already trained.
To let the app read the **image itself**, follow these steps. Until the two files below exist, no image upload is shown and no placeholder score is produced.

1. **Train an image model** outside this app (for example a small CNN or a pretrained network fine-tuned on labelled chest X-rays from at least two sources). Check it on a source it never saw.
2. **Export to ONNX** and save `model/xray/xray_model.onnx` plus `model/xray/xray_config.json`:
   ```json
   {"size": 224, "channels": 1, "mean": 0.5, "std": 0.25, "logits": true}
   ```
   `logits: true` means the network outputs a raw score, which the module turns into a probability.
3. **Collect scored clinical data.** Run the model over X-rays of people whose clinical inputs and Xpert/culture result you have, and save a CSV with the template columns, `tb` (yes/no) and `xray_prob`.
4. **Train the new tier:**
   ```bash
   python scripts/add_tier.py scored_data.csv --name A+XRAY --out model/tb_screen_model.json
   ```
   The engine automatically uses the richest tier whose inputs are present, so the new tier is used whenever an X-ray image is uploaded. Add `crp` to the CSV to train an `A+CRP+XRAY` tier the same way.
5. Restart the app. `/health` shows `"xray_module": true` and the *Screen a person* tab shows an image upload.

Why step 3 matters: the number from your own image model is on a different scale from CAD4TB, so it cannot be dropped into the CAD tier. It needs its own tier trained on its own output.
Do not upload identifiable patient images to any cloud service; run the app inside the clinic network.


## Training on your own X-ray folder (no upload needed)
```
pip install torch pillow scikit-learn onnx onnxscript
python scripts/train_xray.py --data /path/to/xray_folder --pos Tuberculosis --neg Normal --epochs 8
```
It writes `model/xray/xray_model.onnx`, `xray_config.json` and `xray_report.json`. **Read the report warnings first**: public X-ray sets mix hospitals, and a model can learn the hospital instead of TB. The script splits by source group and probes for size/brightness shortcuts. Tested on synthetic images only; not yet run on real X-rays.


The app also uses the model for an occlusion map (grey out one cell at a time and see how much the score drops) and a picture-quality check. Set `TBSCREEN_XRAY_DIR` to load a model from another folder.
