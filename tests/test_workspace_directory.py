"""Ensure the workspace's default view links to both creative labs."""
import unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class DirectoryParser(HTMLParser):
 def __init__(self):
  super().__init__();self.in_main=False;self.depth=0;self.cards=[];self.link=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='main' and a.get('id')=='page-model':self.in_main=True
  elif self.in_main and tag=='main':self.depth+=1
  if self.in_main and tag=='a' and 'workspace-tile' in (a.get('class') or '').split():self.link={'href':a.get('href'),'text':''}
 def handle_data(self,data):
  if self.link is not None:self.link['text']+=data
 def handle_endtag(self,tag):
  if tag=='a' and self.link is not None:self.cards.append(self.link);self.link=None
  if tag=='main' and self.in_main:
   if self.depth:self.depth-=1
   else:self.in_main=False
class DirectoryTest(unittest.TestCase):
 def test_default_view_has_clickable_lab_tiles(self):
  parser=DirectoryParser();parser.feed((ROOT/'index.html').read_text())
  links={c['href']:c['text'] for c in parser.cards}
  for href,label in [('design-lab/','Design Lab'),('logo-lab/','Logo Lab')]:
   with self.subTest(href=href):
    self.assertIn(href,links)
    self.assertIn(label,links[href])
    self.assertTrue((ROOT/href/'index.html').is_file())
if __name__=='__main__':unittest.main()
