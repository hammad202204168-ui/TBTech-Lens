# Break report (test-first round)

Method: the 52 tests in `tests/test_break.py` were written **before** any fix and run against the working app. First run: **23 failed, 29 passed**. Then each failure was fixed. Final: **71 passed** (19 original + 52 break-it).

| # | What broke | Why it matters | Fix |
|---|---|---|---|
| 1 | Text "no", "false", "n" was read as YES (any non-empty text was truthy) | A clinician uploading a CSV with "no" would get the risk of someone who has the symptom | Strict yes/no parser; unknown text is an error, not a guess |
| 2 | `inf` / `-inf` CRP or CAD gave NaN or crashed | One bad cell stops a batch | Only finite numbers accepted; others treated as "not entered" |
| 3 | CRP 1e300 or negative values flowed into the model | Absurd scores | Values clipped to a plausible range |
| 4 | CAD typed as 0.72 (fraction) silently looked like a very low score | Real TB under-called | Warning in app, API and batch ("check CAD scale") |
| 5 | A person with no symptoms was told to go to the clinic for assessment | Alarm, wasted visits | New "keep watching" advice unless the band is Higher |
| 6 | A damaged or edited model file was loaded without checks | Silent wrong scores | Model validated on load (lengths, features, thresholds, bands) |
| 7 | Batch file only accepted `age_group` codes | Nobody knows the codes | Batch takes `age` in years; under 15 rejected row-by-row |
| 8 | Rows "on TB treatment" were scored | Screening someone already treated is meaningless | Row skipped with a reason |
| 9 | CSV download could carry `=HYPERLINK(...)` cells | Formula injection when opened in Excel | Cells starting `= + - @` get an apostrophe |
| 10 | API ignored misspelt fields (`nightsweat`) | Symptom silently counted as "no" | Unknown fields return 422 |
| 11 | No length limit on `site` / `ref` | Database bloat, abuse | 100 characters max |
| 12 | `limit` unbounded or negative | Memory/time abuse | 1 to 5000 |
| 13 | Binary or huge batch upload was accepted or crashed | Server stalls | 400 for unreadable files; 413 over 5000 rows or 3 MB |
| 14 | API key compared with `!=` | Timing leak | `hmac.compare_digest` |
| 15 | Cough with no duration chosen silently used 2 to 4 weeks | A made-up answer entered as fact | Duration has no default; asks the user |

Also found while fixing: a stale duplicate copy of the engine code overrode the new batch function (caught only because the tests still failed). Lesson: tests found it, not eyes.

Not covered by these tests (be honest): real phones and slow networks, long-running load, screen readers, Urdu wording checked by a native clinician, security testing by a third party.
