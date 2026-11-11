from pathlib import Path
import json,unittest
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
class OrgTests(unittest.TestCase):
 def test_page_has_all_roles_and_honest_limits(self):
  page=ROOT/'agent-org.html'
  self.assertTrue(page.exists(), 'Agent org page has not been generated')
  s=BeautifulSoup(page.read_text(),'html.parser')
  self.assertEqual(len(s.select('[data-org-role]')),6)
  text=s.get_text(' ',strip=True)
  self.assertIn('Chief of Staff',text)
  self.assertIn('No outreach',text)
  self.assertIn('No Anthropic/Claude',text)
  self.assertIn('Internal research',text)
 def test_public_data_excludes_private_runtime_records(self):
  text=(ROOT/'agent-org.json').read_text()
  for marker in ['paliotta.evan@gmail','/Users/','api_key','ledger.sqlite','state/','phone_number']:
   self.assertNotIn(marker,text)
if __name__=='__main__':unittest.main()
