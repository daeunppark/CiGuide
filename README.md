# CiGuide
NYU CS6903/4783 Project 1.3 — private-key encryption configuration selection.

## Open the UI
Double-click **web/index.html**. No server, installation or network is needed. Upload this file to a static host if desired. Tabs: **Find My Scheme | Comparison Table | Decision Tree | Evaluation | Sources**.

## Python commands
From this folder, with Python 3.9+ (standard library only):
```sh
python3 run.py
python3 run.py tree
python3 run.py evaluate
python3 run.py build
python3 -m unittest discover -s tests -v
```
Optional browser-script checks (Node.js required): `node tests/test_web.cjs`.
`run.py` uses standard input/output. `tree` exports the filtering tree with ranking policy at leaves. `evaluate` writes the current experiment to reports/evaluation_results.json. **build** regenerates the report, exported tree, standalone HTML, comparison table, slide notes, presentation outline and source list together. After changing data or Python logic, use build to synchronize the deliverables. Web layout/text is edited in src/templates/index.html, then built.

## Behavior
Adaptive filtering selects maximum expected candidate reduction under equal Yes/No probabilities. No means a capability is optional. IDK shows an easy example and asks once more; a second IDK preserves candidates. Q4 storage is inactive without a numeric budget. Follow-up preferences rank multiple remaining candidates: one point per matching Yes, zero for No/IDK, shared ranks for ties. Ranking never removes candidates. Unknown/unasked requirements remain unconfirmed; Storage is omitted from the displayed unassessed list.

## Evaluation
The chosen success rule is **target inclusion anywhere in the final ranked list**, regardless of rank or other candidates. Current default: **100.00%**, 10,000 trials, seed 6903. The Evaluation tab shows the primary metric and Expected/Actual cases. Secondary diagnostics remain in the raw JSON only. High inclusion does not prove unique identification or real-user suitability. No user uncertainty is simulated in the base experiment; IDK has separate tests.

## Source files
- data/schemes.csv — canonical comparison table
- data/questions.json — requirement questions and examples
- data/ranking_questions.json — ranking preferences and examples
- src/ — Python logic, builder and UI template
- web/index.html — generated standalone application
- reports/ — current evaluation and tree
- docs/ — current table, slide notes, presentation outline and sources
- tests/ — automated checks

The application recommends schemes; it does not perform encryption. The finished slide deck and recorded 10–15 minute presentation remain to be created. See docs/sources.md for course page references and standards.
