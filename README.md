# CiGuide

NYU CS6903/4783 Project 1.3 — an interactive guide to choosing symmetric encryption configurations.

## Demo

[Open CiGuide](https://daeunppark.github.io/CiGuide/)

For offline use, open `index.html` in a browser. No installation or server is required.

## Run

Run commands from the repository root. Python 3.9+ and Node.js are required for the automated checks; no additional packages are needed.

```sh
# Python logic, ranking, evaluation and data consistency
python3 -m unittest discover -s tests -v

# JavaScript interactions and Python/HTML result parity
node tests/test_web.cjs

# Reproduce the evaluation (10,000 trials, seed 6903)
python3 run.py evaluate
```

Evaluation results are saved to `reports/evaluation_results.json`. Success means the target scheme appears anywhere in the returned list; it does not require a unique or first-ranked match.

For a manual check, open the demo or `index.html`:

1. Answer questions in **Find My Scheme** and confirm results appear.
2. Select **I don’t know** twice: the first selection shows an example; the second advances.
3. Try **Back** and **Restart**, then open the other four tabs.
4. In **Decision Tree**, expand nodes and try zoom and reset.
