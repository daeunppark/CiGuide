import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from local_server import state
class GuiTests(unittest.TestCase):
 def test_first_question(self):self.assertEqual(state([])['question']['id'],'Q2')
 def test_timestamp(self):
  result=state([{'id':'Q2','answer':'yes'}]);self.assertTrue(result['done']);self.assertEqual(len(result['candidates']),1)
 def test_gcm(self):
  result=state([{'id':'Q2','answer':'no'},{'id':'Q3','answer':'yes'}]);self.assertEqual(result['candidates'][0]['scheme'],'AES-GCM');self.assertTrue(result['done'])
 def test_unknown_retains_pool(self):
  result=state([{'id':'Q2','answer':None}]);self.assertEqual(len(result['candidates']),5);self.assertEqual(result['unknown'],['Q2'])
 def test_reject_bad_sequence(self):
  with self.assertRaises(ValueError):state([{'id':'Q1','answer':'yes'}])
if __name__=='__main__':unittest.main()
