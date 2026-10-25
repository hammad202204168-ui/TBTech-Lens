# Contributing
1. Test first: write the test that shows the problem (`tests/test_break.py` is for break-it cases), watch it fail, then fix.
2. `pip install -r requirements-dev.txt && python -m pytest tests -q`
3. Never commit patient data or identifiers. Never claim performance that `model/benchmark.csv` does not show.
4. Model changes need a regenerated benchmark and an updated `docs/MODEL_CARD.md`.
