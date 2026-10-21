import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from evaluate import experiment
class EvaluationTests(unittest.TestCase):
 def test_reproducible_and_strict(self):
  a=experiment(1000,6903);self.assertEqual(a,experiment(1000,6903))
  m=a['metrics'];self.assertEqual(m['target_inclusion_probability'],1)
  self.assertEqual(m['choice_correctness_success_probability'],m['target_inclusion_probability'])
  self.assertLess(m['exact_identification_probability'],1)
  self.assertGreater(m['mean_candidates'],1)
  self.assertEqual(sum(d['trials'] for d in a['per_scheme'].values()),1000)
if __name__=='__main__':unittest.main()
