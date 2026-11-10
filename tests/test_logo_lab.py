"""Logo lab contract: vector marks, preserved choices and testable review controls."""
from pathlib import Path
import json,unittest,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/'logo-lab'
class LogoLabTest(unittest.TestCase):
 def test_exactly_50_distinct_vector_candidates(self):
  self.assertTrue((LAB/'logos.json').exists(),'Missing generated logo dataset')
  logos=json.loads((LAB/'logos.json').read_text())
  self.assertEqual(len(logos),50)
  self.assertEqual(len({x['id'] for x in logos}),50)
  self.assertEqual(len({x['svg'] for x in logos}),50)
  self.assertEqual(len({x['family'] for x in logos}),5)
  for i,l in enumerate(logos,1):
   with self.subTest(i=i):
    self.assertEqual(l['id'],f'{i:02}')
    self.assertTrue(l['name'] and l['meaning'])
    svg=ET.fromstring(l['svg'])
    self.assertEqual(svg.tag.split('}')[-1],'svg')
    self.assertEqual(svg.get('viewBox'),'0 0 100 100')
    self.assertGreaterEqual(len(svg),1)
    for item in svg.iter():
     self.assertIn(item.tag.split('}')[-1],{'svg','g','path','circle','rect','ellipse','polygon','polyline','line'})
     for key,val in item.attrib.items():
      self.assertFalse(key.lower().startswith('on'))
      self.assertNotIn('url(',val.lower())
      self.assertNotIn('href',key.lower())
    mark=LAB/'marks'/f'{i:02}.svg'
    self.assertTrue(mark.is_file())
    self.assertEqual(mark.read_text().strip(),l['svg'])
  js=(LAB/'logo-data.js').read_text()
  self.assertTrue(js.startswith('const LOGOS = '))
  self.assertEqual(json.loads(js.removeprefix('const LOGOS = ').strip().removesuffix(';')),logos)
 def test_review_app_has_palette_swag_and_export(self):
  p=LAB/'index.html';self.assertTrue(p.exists(),'Missing review page');h=p.read_text()
  for marker in ['Shortlist','Export feedback','Print / embroidery','Swag','Monochrome','No logo has been selected','jax-logo-lab-feedback-v1']:
   self.assertIn(marker,h)
  self.assertIn('name="viewport"',h)
 def test_generation_is_attributed_and_no_logo_selected(self):
  p=LAB/'logos.json';self.assertTrue(p.exists())
  for logo in json.loads(p.read_text()):
   self.assertEqual(logo['generator'],'moonshotai/kimi-k3.1-pro')
  self.assertNotIn('selected: true',(LAB/'index.html').read_text())
if __name__=='__main__':unittest.main()
