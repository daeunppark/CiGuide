"""Rebuild browser data, current reports and docs from canonical inputs."""
import csv
import html
import json
import re
import random
from html.parser import HTMLParser
from pathlib import Path
from decision_engine import ROOT, load, approved_tree
from local_server import filter_state
from ranking import QUESTIONS as RANKING
from evaluate import experiment

FIELDS = [('no','No.'),('scheme','Symmetric Encryption Scheme'),('runtime_efficiency','Runtime Efficiency'),('security','Security'),('freshness_check','Freshness Check (ADDED)'),('storage_complexity','Storage Complexity — Output (ADDED)'),('time_complexity','Time Complexity (ADDED)'),('message_length_required_in_advance','Message Length Required in Advance (ADDED)'),('integrated_authentication','Integrated Authentication (ADDED)'),('parallel_encryption','Parallel Encryption (ADDED)')]

def escaped(value):return html.escape(str(value))
def script_json(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

def comparison(rows):
    text='<thead><tr>'+''.join('<th'+(' class="added-cell"' if '(ADDED)' in label else '')+'>'+label+'</th>' for _,label in FIELDS)+'</tr></thead><tbody>'
    for row in rows:
        text+='<tr>'+''.join(('<th scope="row">' if key=='scheme' else '<td>')+escaped(row[key])+('</th>' if key=='scheme' else '</td>') for key,_ in FIELDS)+'</tr>'
    return text+'</tbody>'

def evaluation(report):
    rate=report['metrics']['choice_correctness_success_probability']
    text='<section id="evaluationView" hidden><div class="card"><div class="step">Project step 4</div><h2>Evaluation: Expected vs. Actual</h2><p>Randomly select a target scheme, answer both requirement and follow-up preference questions consistently with its table properties, then compare Expected with the returned ranked list.</p>'
    text+=f'<div class="tablewrap"><table style="min-width:650px"><thead><tr><th>Metric</th><th>Actual — {report["trials"]:,} trials; seed {report["seed"]}</th></tr></thead><tbody><tr><th>Choice correctness — target included</th><td>{rate:.2%}</td></tr></tbody></table></div>'
    text+='<h3>Expected–Actual Cases</h3><div class="tablewrap"><table><thead><tr><th>Expected</th><th>Answers</th><th>Actual — ranks and scores</th><th>Result: target included?</th></tr></thead><tbody>'
    for case in report['expected_actual_cases']:
        answers='<br>'.join(escaped(x['id'])+' = '+({'yes':'Yes','no':'No',None:'I don’t know'}[x['answer']]) for x in case['path'])
        actual='<br>'.join(str(x['rank'])+'. '+escaped(x['scheme'])+' ('+str(x['score'])+' points)' for x in case['actual'])
        hit=case['expected'] in [x['scheme'] for x in case['actual']]
        text+=f'<tr><th>{escaped(case["expected"])}</th><td>{answers}</td><td>{actual}</td><td>{"PASS" if hit else "FAIL"}</td></tr>'
    text+='</tbody></table></div><h3>Ranking rules</h3><p>After requirement filtering, a matching Yes preference earns one point. No and I don’t know earn none. Follow-ups compare combined protection, skipping optional timestamp checks, and parallel encryption. Only preferences that differ among eligible candidates are asked. Ties share a rank; order within a tie has no meaning. Ranking never removes eligible candidates. It is not a security-strength or measured-speed ranking.</p>'
    text+='<h3>Reproduce and interpret</h3><p>Run <code>python3 run.py evaluate</code>. Results: <code>reports/evaluation_results.json</code>. Run <code>python3 run.py build</code> to refresh all reports, documentation and browser data together. The default experiment uniformly samples targets with seed 6903 and does not simulate IDK; IDK handling is tested separately.</p><p>Returning multiple candidates can make inclusion high. This score is not unique identification and is not directly comparable to choosing one scheme randomly. Preferences are generated from target properties, not measured from real users. Storage suitability is not assessed.</p></div></section>'
    return text

class Markdown(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('h2','h3'):self.parts.append('\n\n'+('## ' if tag=='h3' else '# '))
        elif tag=='li':self.parts.append('\n- ')
        elif tag in ('p','div','ul','ol'):self.parts.append('\n')
        elif tag=='br':self.parts.append('\n')
        elif tag=='strong':self.parts.append('**')
        elif tag=='a':self.parts.append('[');self.links.append(attrs.get('href',''))
    def handle_endtag(self,tag):
        if tag in ('h2','h3','p'):self.parts.append('\n\n')
        elif tag=='strong':self.parts.append('**')
        elif tag=='a':self.parts.append(']('+self.links.pop()+')')
    def handle_data(self,text):self.parts.append(text)
    def result(self):return re.sub(r'\n{3,}','\n\n',''.join(self.parts)).strip()+'\n'

def build():
    rows,_=load(ROOT/'data/schemes.csv')
    questions=json.loads((ROOT/'data/questions.json').read_text())
    states={}
    def walk(history):
        current=filter_state(history);states[json.dumps(history,separators=(',',':'))]=current
        if current['question']:
            for answer in ('yes','no',None):walk(history+[{'id':current['question']['id'],'answer':answer}])
    walk([])
    # Refresh Python/HTML parity fixtures from canonical state logic.
    from local_server import state
    rng=random.Random(6903);samples=[]
    for _ in range(80):
        history=[]
        while True:
            current=state(history)
            samples.append({'history':history[:],'question':current['question']['id'] if current['question'] else None,'candidates':[(r['scheme'],r.get('rank'),r.get('score')) for r in current['candidates']]})
            if current['done']:break
            history.append({'id':current['question']['id'],'answer':rng.choice(['yes','no',None])})
    fixture=ROOT/'tests/fixtures/recommendation_cases.json'
    fixture.parent.mkdir(exist_ok=True)
    fixture.write_text(json.dumps(samples,separators=(',',':'))+'\n')
    report=experiment()
    (ROOT/'reports/evaluation_results.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'reports/decision_tree.json').write_text(json.dumps(approved_tree(rows,questions),indent=2,ensure_ascii=False)+'\n')
    template=(ROOT/'src/templates/index.html').read_text()
    page=template.replace('@@STATES@@',script_json(states)).replace('@@RANKING@@',script_json(RANKING)).replace('@@COMPARISON@@',comparison(rows)).replace('@@EVALUATION@@',evaluation(report))
    if '@@' in page:raise ValueError('Unresolved template placeholder')
    (ROOT/'index.html').write_text(page)
    docs=ROOT/'docs'
    table='# Implementation Usage Table\n\n|'+ '|'.join(label for _,label in FIELDS)+'|\n|'+ '|'.join('---' for _ in FIELDS)+'|\n'
    for row in rows:table+='|'+'|'.join(row[key] for key,_ in FIELDS)+'|\n'
    table+='\nAll lengths are bytes: n = plaintext, a = associated data, p = PKCS#7 padding (1–16), v = IV/nonce, t = authentication tag, s = timestamp. CBC IVs are 16 bytes; full HMAC-SHA256 tags are 32 bytes. Storage is output data plus explicitly stored metadata, excluding keys, AAD, protocol headers and replay state. Bounds assume linear processing and fixed-size key/tag/timestamp. Variable-length AAD also makes CBC+MAC O(n+a). Timestamp checking alone does not ensure complete replay protection or ordering.\n\nSee [Sources](sources.md).\n'
    (docs/'comparison_table.md').write_text(table)
    notes='''# Current Slide Notes

## Project and table
Chosen primitive: private-key encryption. The original table is Lecture 6 PDF p. 27. Rows 1–3 are instantiated as CBC with PKCS#7 and HMAC-SHA256 in an independent-key Encrypt-then-MAC composition. GCM/CCM are added rows. Added columns are Freshness Check, Storage Complexity — Output, Time Complexity, Message Length Required in Advance, Integrated Authentication and Parallel Encryption. See comparison_table.md and sources.md.

## Adaptive filtering
Expected candidate reduction = 0.5 × (current candidates − candidates after Yes), with equal Yes/No prior. No means not required; IDK preserves candidates. Ties use question-list order. Recalculate after each answer. Initially Q2 and Q3 both score 2; Q2 comes first. After Q2 No/unknown, Q3 is next. Q7/Q8 can also filter based on explicit user preferences. Q4 storage is inactive without a byte limit.

## Accessible questions
All prompts offer Yes / No / I don’t know. The first unknown displays a plain-English example and repeats the question. A second unknown advances without guessing. Unknown and unasked items remain unconfirmed. The permanently inactive Storage question is omitted from the result’s Not assessed list.

## Final ranking
If filtering leaves multiple candidates, ask useful differing preferences. Rank question priority is balanced property splits, with list-order tie breaking. A matching Yes earns one point. No/IDK adds zero points. Candidates are never removed in this phase. Equal scores share a rank; tied display order has no meaning. This is a preference ranking, not a security or speed ranking. One candidate skips this phase.

## Browser and CLI
Find My Scheme | Comparison Table | Decision Tree | Evaluation | Sources. The browser works offline with no backend. Python supplies standard input/output. Both use the same data and are verified for matching outputs. The tree shows filtering and ranking branches. Source inputs are data/*.csv and data/*.json; build with python3 run.py build after changes.

## Evaluation
'''
    notes+=f"Uniformly sample a target; answer all questions consistently with its features; pass if the target appears anywhere in the final ranked list. Default: {report['trials']:,} trials, seed {report['seed']}. Choice correctness: {report['metrics']['choice_correctness_success_probability']:.2%}. This is inclusion, not unique identification. No IDK is simulated in the base experiment. The Evaluation tab shows this primary metric and Expected/Actual cases only. Raw reports keep secondary diagnostics. Inclusion is not directly comparable to a single random choice.\n"
    notes+='\n## Current questions and examples\n'
    for q in questions+RANKING:
        status=' (inactive: budget needed)' if q['id']=='Q4' else ''
        notes+='\n### '+q['id']+status+'\n'+q['question']+'\n\nIDK example: '+q['example']+'\n'
    notes+='\n## Limits and remaining submission work\nStorage budgets are not assessed. The filtering capability mapping supports this table schema, rather than arbitrary cryptographic features. Evaluation is synthetic; no user study or encryption implementation is claimed. A finished slide deck and 10–15 minute video recording remain to be produced.\n'
    (docs/'slide_notes.md').write_text(notes)
    (docs/'presentation_outline.md').write_text('''# Presentation Outline — 10–15 minutes

1. Problem and chosen primitive (1 min): private-key encryption for non-experts.
2. Table and extensions (2 min): lecture page, concrete CBC/HMAC choices, GCM/CCM and added columns. Show analytic storage/time assumptions.
3. Adaptive filtering (2 min): expected candidate reduction, equal answer prior, No and IDK meanings.
4. Accessible interaction (1 min): easy questions; example after IDK; one retry.
5. Preference ranking (1–2 min): matching Yes = one point; neutral No/IDK; shared ranks for ties; no candidate deletion.
6. Live demo (2 min): use Find My Scheme, result table, Comparison Table, interactive Decision Tree and Sources. Show an IDK retry and ranked multi-candidate result.
7. Evaluation (1–2 min): random target, feature-consistent answers, inclusion-based correctness and Expected/Actual cases. Explain why 100% inclusion is not unique identification.
8. Limitations (1 min): inactive storage budget, synthetic evaluation, ties and schema-specific feature mapping.

Use slide_notes.md for the current exact questions/examples and sources.md for references. Record your own demonstration and narration; the outline is not a finished slide deck.
''')
    source='<section id="sourcesView"'+page.split('<section id="sourcesView"')[1].split('</section>')[0]+'</section>';parser=Markdown();parser.feed(source);(docs/'sources.md').write_text(parser.result())
    (ROOT/'README.md').write_text('''# CiGuide

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
''')
    return {'filter_states':len(states),'trials':report['trials'],'correctness':report['metrics']['choice_correctness_success_probability']}

if __name__=='__main__':print(json.dumps(build()))
