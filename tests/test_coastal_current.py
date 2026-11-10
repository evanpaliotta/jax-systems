"""Acceptance contract for the visual-led, multi-page coastal design concept."""
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
CONCEPT = ROOT / 'design-lab/concepts/12-coastal-current'
PAGES = ['index.html', 'ways-we-help.html', 'how-it-works.html', 'pricing.html', 'contact.html']
OLD_IDS = ['01-tidepool', '02-atlantic-editorial', '03-surf-workshop', '04-coastal-fieldnotes',
           '05-harbor-desk', '06-sunrise-studio', '07-local-current', '08-open-water',
           '09-first-coast', '10-clear-harbor', '11-straight-answers']

class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements, self.words, self.ignore = [], [], 0
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag in ('script', 'style'): self.ignore += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.ignore -= 1
    def handle_data(self, data):
        if not self.ignore: self.words.extend(data.split())

class CoastalCurrentTest(unittest.TestCase):
    def text(self, page):
        p = CONCEPT / page
        self.assertTrue(p.exists(), f'Missing real page: {page}')
        return p.read_text()

    def test_five_real_pages_and_shared_assets_exist(self):
        for page in PAGES + ['site.css', 'site.js', 'current.svg', 'README.md']:
            with self.subTest(page=page): self.assertTrue((CONCEPT / page).is_file(), page)

    def test_homepage_is_short_and_details_live_elsewhere(self):
        home = self.text('index.html')
        self.assertLessEqual(len(Document(home).words), 240)
        self.assertNotIn('<details', home)
        self.assertNotIn('$2,499', home)
        for page in PAGES[1:]: self.assertIn(page, home)
        self.assertIn('current.svg', home)
        self.assertIn('data-flow=', home)

    def test_page_links_resolve_and_ids_are_unique(self):
        for page in PAGES:
            with self.subTest(page=page):
                doc = Document(self.text(page))
                ids = [a['id'] for _, a in doc.elements if 'id' in a]
                self.assertEqual(len(ids), len(set(ids)), 'Duplicate ID')
                for tag, attrs in doc.elements:
                    for attr in ('href', 'src'):
                        href = attrs.get(attr, '')
                        if not href or href.startswith(('https:', 'http:', 'data:', 'mailto:')): continue
                        url = urlsplit(href)
                        target = (CONCEPT / unquote(url.path)) if url.path else CONCEPT / page
                        if target.is_dir(): target /= 'index.html'
                        self.assertTrue(target.is_file(), f'{page}: {href}')
                        if url.fragment and target.suffix == '.html':
                            target_ids = [a['id'] for _, a in Document(target.read_text()).elements if 'id' in a]
                            self.assertIn(url.fragment, target_ids, href)

    def test_mobile_accessibility_and_preview_are_explicit(self):
        for page in PAGES:
            html = self.text(page)
            self.assertIn('name="viewport"', html)
            self.assertIn('aria-expanded="false"', html)
            self.assertIn('aria-controls="site-nav"', html)
            self.assertIn('Skip to content', html)
        css = self.text('site.css')
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn('[hidden]', css)
        contact = self.text('contact.html')
        self.assertIn('Nothing is sent', contact)
        self.assertNotRegex(contact, r'action=["\']https?://')

    def test_existing_price_structure_preserved_off_home(self):
        pricing = self.text('pricing.html')
        for marker in ['$999', '$2,499', '$1,500', '$499', '$4,999', '$249', 'subject to scope']:
            self.assertIn(marker, pricing)
        self.assertIn('credited once', pricing)

    def test_function_library_preserves_industry_breadth(self):
        html = self.text('ways-we-help.html')
        for industry in ['trades', 'property', 'marine']:
            self.assertIn(f'data-industry="{industry}"', html)
        self.assertGreaterEqual(html.count('class="example-card"'), 9)
        self.assertIn('Illustrative', html)
        self.assertIn('Stays human', html)

    def test_scripts_are_syntactically_valid(self):
        js = CONCEPT / 'site.js'
        self.assertTrue(js.exists())
        result = subprocess.run(['node', '--check', str(js)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_append_only_gallery_keeps_feedback_schema_and_old_ids(self):
        gallery = (ROOT / 'design-lab/index.html').read_text()
        ids = re.findall(r"\{id:'([^']+)'", gallery)
        self.assertEqual(ids[:12], OLD_IDS + ['12-coastal-current'])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("const KEY='jax-design-lab-feedback-v1'", gallery)
        self.assertIn("schema:'jax-design-lab-feedback-v1'", gallery)
        for url in ['https://clay.global', 'https://cohere.com', 'https://treg.to']:
            self.assertIn(url, gallery)

    def test_three_references_are_in_workspace_catalogue(self):
        html = (ROOT / 'index.html').read_text()
        for slug in ['clay', 'cohere', 'treg']:
            self.assertIn(f'id="agency-site-{slug}"', html)

if __name__ == '__main__': unittest.main()
