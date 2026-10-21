"""Transparent preference scoring; never removes an eligible candidate."""
import json
from pathlib import Path
QUESTIONS = json.loads((Path(__file__).resolve().parent.parent/'data/ranking_questions.json').read_text())

def value(row, prop):
    if prop=='integrated':return row.get('integrated_authentication')=='yes'
    if prop=='no_timestamp':return row.get('freshness_check')=='no'
    if prop=='parallel':return row.get('parallel_encryption')=='yes'
    raise ValueError('Unknown preference')

def next_preference(rows, answers):
    if len(rows)<=1:return None
    options=[q for q in QUESTIONS if q['id'] not in answers and len({value(r,q['property']) for r in rows})>1]
    # Prefer balanced property splits; ties follow the approved list order.
    return max(options,key=lambda q:sum(value(r,q['property']) for r in rows)*sum(not value(r,q['property']) for r in rows)) if options else None

def rank(rows, answers):
    result=[]
    for row in rows:
        matched=[q for q in QUESTIONS if answers.get(q['id'])=='yes' and value(row,q['property'])]
        result.append({**row,'score':len(matched),'reasons':[q['id'] for q in matched]})
    result.sort(key=lambda r:-r['score'])
    scores=sorted({r['score'] for r in result},reverse=True)
    for row in result:row['rank']=scores.index(row['score'])+1
    return result
