import sys,csv,json,re,unittest
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from decision_engine import ROOT
from build_assets import FIELDS
from ranking import QUESTIONS
class Cells(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=[];self.cell=None
 def handle_starttag(self,t,a):
  if t in ('th','td'):self.cell=''
 def handle_data(self,d):
  if self.cell is not None:self.cell+=d
 def handle_endtag(self,t):
  if t in ('td','th') and self.cell is not None:self.row.append(self.cell);self.cell=None
  if t=='tr':self.rows.append(self.row);self.row=[]
class AssetSyncTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.page=(ROOT/'index.html').read_text()
 def test_every_table_cell_matches_csv_in_order(self):
  section=self.page.split('<section id="tableView"')[1].split('</section>')[0]
  cells=Cells();cells.feed(section)
  with (ROOT/'data/schemes.csv').open(newline='') as f:rows=list(csv.DictReader(f))
  self.assertEqual(cells.rows[0],[label for _,label in FIELDS])
  self.assertEqual(cells.rows[1:],[[row[k] for k,_ in FIELDS] for row in rows])
 def test_ranking_question_config_is_shared(self):
  embedded=json.loads(re.search(r'const RANK_QUESTIONS=(.*?);\nfunction rankingValue',self.page,re.S).group(1))
  self.assertEqual(embedded,QUESTIONS)
 def test_displayed_metric_matches_current_report(self):
  report=json.loads((ROOT/'reports/evaluation_results.json').read_text())
  part=self.page.split('<section id="evaluationView"')[1].split('</section>')[0]
  self.assertIn(f"{report['metrics']['choice_correctness_success_probability']:.2%}",part)
  for removed in ['Exact single-candidate identification','Mean candidates','Mean questions','Unique first-ranked target','Tie-adjusted top-1']:
   self.assertNotIn(removed,part)
 def test_requested_ui_removals_persist(self):
  for text in ['id="treeDetails"','Returned candidates','Drag the background to move · Click a node to expand','See the <strong>Sources</strong> tab for lecture pages','Educational selection tool · No encryption is performed.']:
   self.assertNotIn(text,self.page)
 def test_tab_order(self):
  self.assertEqual(re.findall(r'role="tab"[^>]*>([^<]+)',self.page),['Find My Scheme','Comparison Table','Decision Tree','Evaluation','Sources'])
 def test_docs_are_current_not_update_logs(self):
  text='\n'.join(f.read_text() for f in (ROOT/'docs').glob('*.md'))+(ROOT/'README.md').read_text()
  for obsolete in ['No ranking is implemented','58 precomputed','3.0161','3.8309','56.16%','supersedes','Use only the four questions']:
   self.assertNotIn(obsolete,text)
if __name__=='__main__':unittest.main()
