"""Assignment experiment: target inclusion is the primary success metric."""
import json
import random
from decision_engine import ROOT, load, capability
from local_server import state
from ranking import value

def trace(target):
    history=[]
    while True:
        result=state(history)
        if result['done']:return result,history
        q=result['question']
        truth=value(target,q['property']) if q['id'].startswith('R') else capability(target,q['id'])
        history.append({'id':q['id'],'answer':'yes' if truth is True else 'no' if truth is False else None})

def experiment(trials=10000,seed=6903):
    rows,_=load(ROOT/'data/schemes.csv');rng=random.Random(seed)
    traces={r['scheme']:trace(r) for r in rows}
    details={r['scheme']:{'trials':0,'included':0,'exact':0,'top':0,'unique_top':0,'top_credit':0,'reciprocal':0,'questions':0,'candidates':0} for r in rows}
    for _ in range(trials):
        target=rng.choice(rows);result,history=traces[target['scheme']];candidates=result['candidates'];names=[r['scheme'] for r in candidates];hit=target['scheme'] in names
        top=[r['scheme'] for r in candidates if r['rank']==1];d=details[target['scheme']]
        d['trials']+=1;d['included']+=hit;d['exact']+=names==[target['scheme']];d['top']+=target['scheme'] in top;d['unique_top']+=top==[target['scheme']]
        d['top_credit']+=1/len(top) if target['scheme'] in top else 0;d['reciprocal']+=1/len(names) if hit else 0;d['questions']+=len(history);d['candidates']+=len(names)
    def summary(d):
        n=d['trials']
        return {'trials':n,'choice_correctness_success_probability':d['included']/n,'target_inclusion_probability':d['included']/n,'exact_identification_probability':d['exact']/n,'target_in_top_rank_probability':d['top']/n,'unique_top_rank_probability':d['unique_top']/n,'tie_adjusted_top1_probability':d['top_credit']/n,'expected_uniform_pick_success_probability':d['reciprocal']/n,'mean_questions':d['questions']/n,'mean_candidates':d['candidates']/n}
    total={k:sum(x[k] for x in details.values()) for k in next(iter(details.values()))}
    cases=[]
    for r in rows:
        result,path=traces[r['scheme']]
        cases.append({'expected':r['scheme'],'path':path,'actual':[{'scheme':x['scheme'],'rank':x['rank'],'score':x['score']} for x in result['candidates']]})
    return {'trials':trials,'seed':seed,'metrics':summary(total),'per_scheme':{k:summary(v) for k,v in details.items()},'expected_actual_cases':cases,'random_single_scheme_baseline':.2,'correctness_definition':'Success means the randomly selected target appears anywhere in the returned list, per the user-approved rule. Rank is not part of this primary metric. Exact identification and top-rank metrics are secondary.','protocol':'Uniform random target; requirement and preference answers consistently reflect target table properties; no uncertainty. Ranking preserves eligible candidates.','limitations':['Inclusion can reach 100% with many candidates; it is not unique identification.','A 20% random-single-choice baseline is not directly comparable to list inclusion.','Synthetic feature-matched preferences do not measure real user preferences or security.','A correct target tied for first is not uniquely first; tie-adjusted top-1 randomly selects among tied leaders.','Storage budgets remain unassessed.']}

if __name__=='__main__':
    result=experiment();(ROOT/'reports/evaluation_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
