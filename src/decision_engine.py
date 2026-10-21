#!/usr/bin/env python3
"""Table-driven educational cryptographic scheme selector; Python 3 standard library."""
import argparse
import csv
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load(path):
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames or []
    if 'scheme' not in fields or not rows:
        raise ValueError('Table must contain scheme and at least one row.')
    if len({r['scheme'] for r in rows}) != len(rows):
        raise ValueError('Scheme names must be unique.')
    if any(not v or v is None for r in rows for v in r.values()):
        raise ValueError('Table cells must not be empty.')
    return rows, [f for f in fields if f not in ('scheme', 'notes', 'no')]

def entropy(n):
    return math.log2(n) if n else 0

def choose(rows, features):
    # Uniform prior over schemes; maximize expected reduction in candidate entropy.
    best, best_gain = None, 0
    for key in features:
        groups = {}
        for row in rows:
            groups.setdefault(row[key], []).append(row)
        gain = entropy(len(rows)) - sum(len(g)/len(rows)*entropy(len(g)) for g in groups.values())
        if gain > best_gain + 1e-12:
            best, best_gain = key, gain
    return best

def build(rows, features):
    key = choose(rows, features)
    if key is None:
        return {'schemes': [r['scheme'] for r in rows]}
    return {'feature': key, 'branches': {v: build([r for r in rows if r[key] == v], [k for k in features if k != key]) for v in sorted({r[key] for r in rows})}}

def select(rows, features, answer):
    remaining, available, questions = rows[:], features[:], 0
    while True:
        key = choose(remaining, available)
        if key is None:
            return remaining, questions
        choices = sorted({r[key] for r in remaining})
        value = answer(key, choices)
        available.remove(key)
        questions += 1
        if value is None:
            continue  # Unknown is not evidence; retain all current candidates.
        remaining = [r for r in remaining if r[key] == value]
        if not remaining:
            return [], questions

def capability(row, qid):
    if qid == 'Q7':
        return row.get('integrated_authentication') == 'yes'
    if qid == 'Q8':
        return row['freshness_check'].lower() == 'no'
    if qid == 'Q1':
        return 'IND-CCA' in row['security']
    if qid == 'Q2':
        return row['freshness_check'].lower() == 'yes'
    if qid == 'Q6':
        required = row.get('message_length_required_in_advance', '')
        return {'no': True, 'yes': False}.get(required)
    if qid == 'Q3':
        return {'yes': True, 'no': False}.get(row.get('parallel_encryption'))
    return None

def requirement_filter(rows, qid, value):
    # No means the feature is not required, not that it must be absent.
    if value != 'yes':
        return rows[:]
    return [r for r in rows if capability(r, qid) is not False]

def question_score(rows, question):
    if not rows:
        return 0.0
    # Equal Yes/No prior. No and unknown never eliminate candidates.
    return (len(rows) - len(requirement_filter(rows, question['id'], 'yes'))) / 2

def next_question(rows, questions):
    if len(rows) <= 1:
        return None
    useful = [q for q in questions if question_score(rows, q) > 0 and not (q['id'] == 'Q8' and all(r['freshness_check'].lower() == 'yes' for r in rows))]
    return max(useful, key=lambda q: question_score(rows, q)) if useful else None

def approved_tree(rows, questions):
    q = next_question(rows, questions)
    if q is None:
        return {'candidates': [r['scheme'] for r in rows],
                'meaning': 'Eligible candidates enter a preference-ranking phase. Ranking never removes candidates; Yes earns one matching-property point, No/IDK earns zero. Ties share a rank.',
                'ranking_questions': __import__('ranking').QUESTIONS}
    rest = [item for item in questions if item['id'] != q['id']]
    return {'id': q['id'], 'question': q['question'],
            'expected_candidate_reduction': question_score(rows, q),
            'example_after_unknown': q['example'],
            'branches': {label: approved_tree(requirement_filter(rows, q['id'], value), rest)
                         for label, value in [('Yes','yes'),('No','no'),('I don’t know',None)]}}


def interactive(rows, features, questions):
    def ask(prompt):
        print('\n' + prompt)
        print('1. Yes\n2. No\n3. I don’t know')
        while True:
            try:
                value = input('Answer: ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                raise SystemExit('\nSession ended.')
            if value in ('1','yes'):
                return 'yes'
            if value in ('2','no'):
                return 'no'
            if value in ('3','?',"i don't know",'i don’t know','idk'):
                return None
            print('Please enter 1, 2, or 3.')
    remaining, answers = rows[:], {}
    available = questions[:]
    while True:
        q = next_question(remaining, available)
        if q is None:
            break
        available = [item for item in available if item['id'] != q['id']]
        value = ask(q['id'] + '. ' + q['question'])
        if value is None:
            value = ask(q['example'])
        answers[q['id']] = value
        remaining = requirement_filter(remaining, q['id'], value)
    from ranking import next_preference, rank
    while True:
        q = next_preference(remaining, answers)
        if q is None: break
        value = ask(q['question'])
        if value is None: value = ask(q['example'])
        answers[q['id']] = value
    remaining = rank(remaining, answers)
    print('\nRanked results (ties share a rank):')
    if not remaining:
        print('No listed configuration is confirmed to meet all your requirements.')
    for row in remaining:
        pending = [q['id'] for q in questions if answers.get(q['id']) == 'yes' and capability(row,q['id']) is None]
        print(str(row['rank']) + '. ' + row['scheme'] + ' — preference score: ' + str(row['score']))
        if pending:
            print('  Conditional candidate: confirm ' + ', '.join(pending) + ' before choosing it.')
        else:
            print('  Meets the requirements you answered Yes to; unasked or unknown requirements are not confirmed.')
    if answers.get('Q4') == 'yes':
        print('Storage limit recorded. A byte limit and IV/tag/padding sizes are needed to check it; no storage-based filtering was performed.')
    print('No means the feature is not required. Unknown answers keep candidates. No speed ranking is claimed.')
    unresolved = [qid for qid, value in answers.items() if value is None]
    unasked = [q['id'] for q in available if q['id'] != 'Q4']
    if unresolved:
        print('Unanswered requirements: ' + ', '.join(unresolved))
    if unasked:
        print('Not assessed: ' + ', '.join(unasked))
    print('Storage suitability has not been checked: a byte limit and concrete format sizes are needed.')


def evaluate(rows, features, trials, seed, unknown):
    rng = random.Random(seed)
    exact = included = total_questions = 0
    for _ in range(trials):
        target = rng.choice(rows)
        result, count = select(rows, features, lambda key, _: None if rng.random() < unknown else target[key])
        names = [r['scheme'] for r in result]
        included += target['scheme'] in names
        exact += names == [target['scheme']]
        total_questions += count
    return {'trials': trials, 'seed': seed, 'unknown_probability': unknown,
            'exact_identification_rate': exact/trials, 'target_in_candidate_set_rate': included/trials,
            'mean_questions': total_questions/trials, 'uniform_random_top1_baseline': 1/len(rows),
            'interpretation': 'Legacy feature-identification benchmark only; does not evaluate the approved user-question flow.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--table', type=Path, default=ROOT/'data/schemes.csv')
    p.add_argument('--questions', type=Path, default=ROOT/'data/questions.json')
    sub = p.add_subparsers(dest='command')
    sub.add_parser('tree')
    ev = sub.add_parser('evaluate')
    ev.add_argument('--trials', type=int, default=10000)
    ev.add_argument('--seed', type=int, default=6903)
    ev.add_argument('--unknown', type=float, default=0)
    args = p.parse_args()
    try:
        rows, features = load(args.table)
        if args.command == 'tree':
            questions = json.loads(args.questions.read_text())
            print(json.dumps(approved_tree(rows, questions), indent=2, ensure_ascii=False))
        elif args.command == 'evaluate':
            if args.trials < 1 or not 0 <= args.unknown <= 1:
                p.error('trials must be positive; unknown must be in [0,1]')
            print(json.dumps(evaluate(rows, features, args.trials, args.seed, args.unknown), indent=2))
        else:
            questions = json.loads(args.questions.read_text()) if args.questions.exists() else {}
            interactive(rows, features, questions)
    except (ValueError, OSError) as e:
        p.error(str(e))

if __name__ == '__main__':
    main()
