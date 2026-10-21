import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import unittest
from decision_engine import ROOT,load,requirement_filter,next_question
import json
class PreferenceTests(unittest.TestCase):
 def setUp(self):
  self.rows,_=load(ROOT/'data/schemes.csv');self.q=json.loads((ROOT/'data/questions.json').read_text())
 def test_combined_protection(self):
  self.assertEqual([r['scheme'] for r in requirement_filter(self.rows,'Q7','yes')],['AES-GCM','AES-CCM'])
 def test_skip_time(self):
  result=requirement_filter(self.rows,'Q8','yes')
  self.assertEqual(len(result),4)
  self.assertTrue(all(r['freshness_check']=='no' for r in result))
 def test_no_and_unknown_preserve(self):
  for key in ['Q7','Q8']:
   for value in ['no',None]:self.assertEqual(requirement_filter(self.rows,key,value),self.rows)
 def test_timestamp_requirement_does_not_trigger_skip(self):
  rows=requirement_filter(self.rows,'Q2','yes')
  self.assertIsNone(next_question(rows,self.q))
 def test_examples_exist(self):
  for q in self.q:self.assertTrue(q['example'])
if __name__=='__main__':unittest.main()
