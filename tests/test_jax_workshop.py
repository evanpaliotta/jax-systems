import json,re,unittest,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'design-lab/concepts/13-jax-workshop'
class WorkshopTest(unittest.TestCase):
 def test_real_pages_and_animation(self):
  for p in ['index.html','ways-we-help.html','pricing.html','how-it-works.html','contact.html','workshop.css','workshop.js','hero.mp4','poster.webp','industries.json']:
   self.assertTrue((D/p).is_file(),p)
 def test_complete_category_map(self):
  self.assertTrue((D/'industries.json').exists())
  items=json.loads((D/'industries.json').read_text())
  self.assertEqual(len(items),19)
  for i in items:
   self.assertGreaterEqual(len(i['examples']),3,i['name'])
   self.assertTrue(i['human'])
  for slug in ['trades','property','professional','logistics','marine','cleaning','retail','food','beauty','lodging','automotive','recreation','healthcare','finance','education','brokerage','manufacturing','technology','other']:
   self.assertIn(slug,[i['id'] for i in items])
 def test_jaguar_palette_and_motion_controls(self):
  self.assertTrue((D/'workshop.css').exists())
  css=(D/'workshop.css').read_text().lower()
  for hex in ['#006778','#d7a22a','#101820']:self.assertIn(hex,css)
  self.assertIn('prefers-reduced-motion',css)
  self.assertIn('data-motion',(D/'index.html').read_text())
 def test_original_function_demo_not_borrowed_client_proof(self):
  self.assertTrue((D/'index.html').exists())
  h=(D/'index.html').read_text()
  for s in ['data-demo','Illustrative','hero.mp4','ways-we-help.html']:self.assertIn(s,h)
  for s in ['500,000','GTM engineers build on Clay','Trusted by']:self.assertNotIn(s,h)
 def test_js_syntax(self):
  self.assertTrue((D/'workshop.js').exists())
  self.assertEqual(subprocess.run(['node','--check',str(D/'workshop.js')],capture_output=True).returncode,0)
if __name__=='__main__':unittest.main()
