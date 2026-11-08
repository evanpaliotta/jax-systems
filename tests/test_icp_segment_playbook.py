"""Acceptance checks for the aggregate-only Jax Systems segment playbook."""
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    'Trades / field services', 'Property management / real estate operations',
    'Professional services', 'Logistics / transport / warehousing', 'Marine',
    'Cleaning / facilities services', 'Retail / consumer services', 'Food / hospitality',
    'Beauty / wellness', 'Lodging / travel', 'Automotive', 'Recreation / events',
    'Healthcare', 'Finance / insurance', 'Education / childcare',
    'Real estate brokerage', 'Manufacturing / industrial', 'Technology / IT',
    'Other / unknown commercial',
}


class SegmentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.categories = []
        self.card_roles = []
        self.card_active = False
        self.detail_depth = 0
        self.links = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'details' and 'icp-card' in attrs.get('class', '').split():
            self.card_active = True
            self.detail_depth = 1
            self.categories.append(attrs.get('data-category', ''))
            self.card_roles.append(set())
            self.links.append([])
        elif self.card_active and tag == 'details':
            self.detail_depth += 1
        if self.card_active:
            if 'data-icp-field' in attrs:
                self.card_roles[-1].add(attrs['data-icp-field'])
            if tag == 'a' and attrs.get('href', '').startswith('http'):
                self.links[-1].append(attrs['href'])

    def handle_endtag(self, tag):
        if self.card_active and tag == 'details':
            self.detail_depth -= 1
            if self.detail_depth == 0:
                self.card_active = False

    def handle_data(self, value):
        self.text.append(value)


class ICPSegmentPlaybookTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text(encoding='utf-8')
        start = cls.html.find('<!-- ICP-SEGMENT-MAP:START -->')
        end = cls.html.find('<!-- ICP-SEGMENT-MAP:END -->')
        cls.section = cls.html[start:end] if start >= 0 and end > start else ''
        cls.parser = SegmentParser()
        cls.parser.feed(cls.section)
        cls.text = ' '.join(cls.parser.text).lower()

    def test_all_19_categories_have_exactly_one_playbook(self):
        self.assertEqual(set(self.parser.categories), CATEGORIES)
        self.assertEqual(len(self.parser.categories), len(CATEGORIES))

    def test_playbooks_are_inside_verticals_and_preserve_prior_research(self):
        start = self.html.index('<!-- ICP-SEGMENT-MAP:START -->')
        section = self.html.index('<main class="page" id="page-verticals">')
        end = self.html.index('</main>', section)
        self.assertGreater(start, section)
        self.assertLess(start, end)
        self.assertIn('id="gtm-research-sprint"', self.html)
        self.assertIn('id="market-inventory-research"', self.html)

    def test_each_mapped_category_has_a_useful_sales_playbook(self):
        required = {'buyer', 'frictions', 'usecases', 'alternatives', 'measures', 'pitch', 'discovery', 'fit', 'evidence'}
        for category, fields, links in zip(self.parser.categories, self.parser.card_roles, self.parser.links):
            if category == 'Other / unknown commercial':
                self.assertIn('classification', fields)
                continue
            with self.subTest(category=category):
                self.assertTrue(required.issubset(fields), required - fields)
                self.assertGreaterEqual(len(links), 1, 'Cite at least one inspected source per segment')

    def test_unverified_pains_are_not_presented_as_account_facts(self):
        for phrase in ['hypotheses', 'not verified', 'actual prospect', 'customer conversations']:
            self.assertIn(phrase, self.text)
        self.assertIn('classify', self.text)

    def test_sensitive_segment_boundaries_are_explicit(self):
        for phrase in ['hipaa', 'financial', 'children', 'human']:
            self.assertIn(phrase, self.text)

    def test_specialized_inline_citations_point_to_the_right_source(self):
        cases = {
            'Healthcare': ('1', 'https://www.ama-assn.org/practice-management/prior-authorization/fixing-prior-auth-nearly-40-prior-authorizations-week-way'),
            'Finance / insurance': ('4', 'https://www.independentagent.com/news/big-i-and-future-one-release-2024-agency-universe-findings/'),
            'Education / childcare': ('9', 'https://www.naeyc.org/sites/default/files/globally-shared/downloads/PDFs/our-work/public-policy-advocacy/feb_2024_brief_wearenotok_final_1.pdf'),
        }
        for category, (number, url) in cases.items():
            with self.subTest(category=category):
                card = self.section.split(f'data-category="{category}"', 1)[1].split('</details>', 1)[0]
                self.assertIn(f'<a href="{url}">[{number}]</a>', card)

    def test_contact_exports_not_public(self):
        for forbidden in ['duval-st-johns-location-prospects.csv',
                          'qualification-public-channels', '@gmail.com', '@aol.com']:
            self.assertNotIn(forbidden, self.section)


if __name__ == '__main__':
    unittest.main()
