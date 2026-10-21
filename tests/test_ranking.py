import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
from decision_engine import ROOT,load
from ranking import rank,next_preference,QUESTIONS
from local_server import state,filter_state
class RankingTests(unittest.TestCase):
 def setUp(self):self.rows,_=load(ROOT/'data/schemes.csv')
 def test_unknown_and_no_are_neutral(self):
  for answers in [{q['id']:None for q in QUESTIONS},{q['id']:'no' for q in QUESTIONS}]:
   result=rank(self.rows,answers)
   self.assertEqual(len(result),5);self.assertTrue(all(r['rank']==1 and r['score']==0 for r in result))
 def test_preferences_make_gcm_unique_first(self):
  result=rank(self.rows,{'R1':'yes','R2':'yes','R3':'yes'})
  self.assertEqual(result[0]['scheme'],'AES-GCM');self.assertEqual(result[0]['rank'],1);self.assertEqual(result[0]['score'],3)
  self.assertTrue(all(r['rank']>1 for r in result[1:]))
 def test_ties_shared_without_arbitrary_break(self):
  result=rank(self.rows,{'R1':'yes'})
  self.assertEqual({r['scheme'] for r in result if r['rank']==1},{'AES-GCM','AES-CCM'})
 def test_ranking_preserves_candidates(self):
  self.assertEqual({r['scheme'] for r in rank(self.rows,{'R3':'yes'})},{r['scheme'] for r in self.rows})
 def test_live_flow_enters_ranking(self):
  history=[]
  while not filter_state(history)['done']:
   q=filter_state(history)['question'];history.append({'id':q['id'],'answer':'no'})
  self.assertTrue(state(history)['question']['id'].startswith('R'))
  while not state(history)['done']:
   q=state(history)['question'];history.append({'id':q['id'],'answer':'yes'})
  result=state(history)
  self.assertEqual(result['candidates'][0]['scheme'],'AES-GCM');self.assertEqual(len(result['candidates']),5)
 def test_single_candidate_skips_preferences(self):self.assertIsNone(next_preference(self.rows[:1],{}))
 def test_examples_present(self):self.assertTrue(all(q['example'] for q in QUESTIONS))
if __name__=='__main__':unittest.main()
