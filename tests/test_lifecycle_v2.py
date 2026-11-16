"""Release checks for the monolithic manual, not operational-readiness proof."""
from pathlib import Path
import re
import unittest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

class LifecycleV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc_html = (ROOT / 'customer-lifecycle-playbook.html').read_text()
        cls.index_html = (ROOT / 'index.html').read_text()
        cls.doc = BeautifulSoup(cls.doc_html, 'html.parser')
        cls.index = BeautifulSoup(cls.index_html, 'html.parser')

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

    def test_offer_contract_matches_the_two_path_public_offer(self):
        text = self.doc.article.get_text(' ', strip=True)
        for marker in [
            'free working session',
            'one of seven business areas',
            'one specific question',
            'up to 60 minutes',
            'owner or decision-maker',
            'client-owned tools',
            'read-only unless',
            'written summary',
            '$2,499',
            '$999 Business Improvement Plan',
            '$1,500',
            '$499/month',
            '$250/month',
            'signed scope card',
            'one implementation blueprint',
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertIn('direct build', text.lower())
        self.assertIn('plan', text.lower())

    def test_stage_table_plan_deliverable_and_build_entry_support_both_routes(self):
        lifecycle_text = self.doc.find('h2', id='2-the-lifecycle-and-its-advance-gates').find_next('table').get_text(' ', strip=True)
        self.assertIn('Free working session Fit decision, useful summary and route to Path A or Path B', lifecycle_text)
        self.assertIn('Paid Business Improvement Plan Seven-area high-level review, ranked opportunities, measurement plan and one client-owned implementation blueprint', lifecycle_text)
        self.assertIn('Sell the build Signed scope card or build agreement from Path A or Path B', lifecycle_text)
        self.assertNotIn('Current-state map, ranked recommendations, measurement and first-build quote', lifecycle_text)

    def test_plan_sections_name_all_seven_areas_and_blueprint_ownership(self):
        diagnose_html = self.doc_html.split('<h2 id="5-diagnose-conduct-the-business-improvement-plan">', 1)[1].split('<h2 id="6-deliver-the-business-improvement-plan">', 1)[0]
        for marker in (
            'Offer review',
            'Marketing review',
            'Sales review',
            'Delivery and customer experience review',
            'Retention review',
            'Operations and people review',
            'Finance review',
            'Measure only from records that already exist. When a measure is missing, record the gap and the lightest credible way to collect it.',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, diagnose_html)
        plan_html = self.doc_html.split('<h2 id="6-deliver-the-business-improvement-plan">', 1)[1].split('<h2 id="7-sell-and-scope-the-build">', 1)[0]
        for marker in (
            'Seven-area high-level review',
            'One detailed implementation blueprint',
            'The client can use the blueprint internally without Jax Systems or hand it to another provider.',
            'Optional fixed-price quote',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, plan_html)
        self.assertNotIn('Current-state map', plan_html)
        self.assertNotIn('Implementation sequence', plan_html)
        self.assertNotIn('First-build scope and fixed-price quote', plan_html)

    def test_scope_section_allows_direct_path_a_and_lists_scope_card_fields(self):
        scope_html = self.doc_html.split('<h2 id="7-sell-and-scope-the-build">', 1)[1].split('<h2 id="8-onboard-accounts-data-and-responsibilities">', 1)[0]
        scope_text = BeautifulSoup(scope_html, 'html.parser').get_text(' ', strip=True)
        scope_lower = scope_text.lower()
        self.assertIn('trigger: client wants a recommended improvement.', scope_lower)
        self.assertIn('free-session summary and direct-scope evidence, or approved plan blueprint and feasibility evidence', scope_lower)
        self.assertNotIn('inputs: reviewed plan', scope_lower)
        for marker in (
            'trigger',
            'end state',
            'tools/accounts',
            'rules/branches',
            'explicit exclusions',
            'acceptance tests',
            'workflow owner',
            'fixed price',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, scope_lower)

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
