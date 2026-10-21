import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from decision_engine import ROOT, load, select, build

class SelectorTests(unittest.TestCase):
    def setUp(self):
        self.rows, self.features = load(ROOT/'data/schemes.csv')
    def test_every_scheme_is_recovered(self):
        for row in self.rows:
            matches, count = select(self.rows, self.features, lambda k, _: row[k])
            self.assertEqual([r['scheme'] for r in matches], [row['scheme']])
            self.assertLessEqual(count, len(self.features))
    def test_unknown_does_not_discard_candidates(self):
        matches, _ = select(self.rows, self.features, lambda *_: None)
        self.assertEqual(matches, self.rows)
    def test_duplicate_features_remain_ambiguous(self):
        rows = [{'scheme':'A','x':'yes'}, {'scheme':'B','x':'yes'}]
        self.assertEqual(build(rows,['x']), {'schemes':['A','B']})
    def test_impossible_answer_has_no_result(self):
        matches, _ = select(self.rows,self.features,lambda *_:'not-a-value')
        self.assertEqual(matches,[])

if __name__ == '__main__':
    unittest.main()
