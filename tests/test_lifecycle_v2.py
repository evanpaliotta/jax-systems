"""Release checks for the monolithic manual, not operational-readiness proof."""
from pathlib import Path
import re
import unittest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

class LifecycleV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = BeautifulSoup((ROOT / 'customer-lifecycle-playbook.html').read_text(), 'html.parser')
        cls.index = BeautifulSoup((ROOT / 'index.html').read_text(), 'html.parser')

    def test_researched_v2_is_rendered(self):
        text = self.doc.article.get_text(' ', strip=True)
        self.assertIn('Operating draft v2', text)
        for marker in ['Business Improvement Plan', 'Scope-change inject', 'Production-failure inject', 'Monitoring-contract template', 'Exit checklist', 'CAN-SPAM', '08:20', 'SEV2']:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertEqual(len(self.doc.article.select('h2')), 18)
        self.assertNotIn('paid versus free entry decision remains open', text.lower())

    def test_tables_are_readable_and_locally_scrollable(self):
        tables = self.doc.article.select('table')
        self.assertGreaterEqual(len(tables), 4)
        for table in tables:
            self.assertIn('table-scroll', table.parent.get('class', []))

    def test_sources_link_to_ledger_urls_in_reading_copy(self):
        source_links = self.doc.select('article h2#sources ~ ul a[href^="https://"]')
        self.assertGreaterEqual(len(source_links), 10)
        for link in source_links:
            self.assertRegex(link.get('href', ''), r'^https://')
        self.assertGreaterEqual(len(self.doc.select('a.citation')), 10)

    def test_complete_embedded_version_and_default_view_link(self):
        inline = self.index.select_one('#page-playbooks #lifecycle-inline')
        self.assertEqual(inline.get_text(' ',strip=True), self.doc.article.get_text(' ',strip=True))
        self.assertEqual(len(inline.select('details')), 18)
        self.assertIsNotNone(self.index.select_one('#page-model a[href="customer-lifecycle-playbook.html"]'))

    def test_no_real_client_or_work_data(self):
        text = self.doc.article.get_text(' ',strip=True)
        for forbidden in ['paliotta.evan@gmail.com', '119,174', '94,246', 'Helm', 'iAltA', 'access_token=', 'gho_']:
            self.assertNotIn(forbidden, text)
        ids = [node['id'] for node in self.doc.select('[id]')]
        self.assertEqual(len(ids), len(set(ids)))
        for a in self.doc.select('a[href^="#"]'):
            self.assertIn(a['href'][1:], ids)

if __name__ == '__main__':
    unittest.main()
