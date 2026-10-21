import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import contextlib
import io
import json
import unittest
from unittest.mock import patch
from decision_engine import ROOT, load, interactive, requirement_filter, next_question, question_score, approved_tree

class ApprovedQuestionTests(unittest.TestCase):
    def setUp(self):
        self.rows,self.features=load(ROOT/'data/schemes.csv')
        self.q=json.loads((ROOT/'data/questions.json').read_text())
    def run_flow(self,answers):
        out=io.StringIO()
        with patch('builtins.input',side_effect=answers),contextlib.redirect_stdout(out):
            interactive(self.rows,self.features,self.q)
        return out.getvalue()
    def test_best_question_first(self):
        self.assertEqual(next_question(self.rows,self.q)['id'],'Q2')
        self.assertEqual(question_score(self.rows,self.q[1]),2)
    def test_no_then_recalculate(self):
        text=self.run_flow(['no']*12)
        self.assertLess(text.index('Q2.'),text.index('Q3.'))
        self.assertLess(text.index('Q3.'),text.index('Q1.'))
        self.assertNotIn(self.q[3]['question'],text)
    def test_stop_at_one_candidate(self):
        text=self.run_flow(['yes'])
        self.assertNotIn(self.q[0]['question'],text)
        self.assertIn('Timestamping',text)
    def test_second_unknown_moves_on(self):
        text=self.run_flow(['idk']*24)
        for q in [q for q in self.q if q['id'] != 'Q4']:self.assertEqual(text.count(q['example']),1)
        self.assertNotIn(self.q[3]['example'],text)
        self.assertIn('Unanswered requirements:',text)
    def test_examples_only_on_unknown(self):
        text=self.run_flow(['no']*12)
        for q in self.q:self.assertNotIn(q['example'],text)
    def test_parallel_requires_gcm(self):
        result=requirement_filter(self.rows,'Q3','yes')
        self.assertEqual(len(result),1)
        self.assertNotIn('AES-CCM',[r['scheme'] for r in result])
    def test_q6_uses_new_table_column(self):
        result = requirement_filter(self.rows, 'Q6', 'yes')
        self.assertNotIn('AES-CCM', [r['scheme'] for r in result])
        self.assertIn('AES-GCM', [r['scheme'] for r in result])
        self.assertEqual(len(result), 4)
        self.assertEqual(len(requirement_filter(self.rows, 'Q6', 'no')), 5)
        text = self.run_flow(['no', 'no', 'no', 'no', 'yes', 'no'] + ['no']*6)
        self.assertIn(self.q[4]['question'], text)
        self.assertNotIn('Conditional candidate', text)

    def test_no_split_stops(self):
        self.assertIsNone(next_question(self.rows,[self.q[3]]))
        self.assertIn('candidates',approved_tree(self.rows,[self.q[3]]))

if __name__=='__main__':unittest.main()
