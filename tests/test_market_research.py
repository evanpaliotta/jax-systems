import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])


class MarketResearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text(encoding='utf-8')
        cls.start = cls.html.find('<!-- MARKET-RESEARCH:START -->')
        cls.end = cls.html.find('<!-- MARKET-RESEARCH:END -->')
        cls.section = cls.html[cls.start:cls.end] if cls.start >= 0 and cls.end > cls.start else ''

    def test_complete_aggregate_delivery_is_inside_research_tab(self):
        self.assertGreaterEqual(self.start, 0)
        self.assertGreater(self.end, self.start)
        resources_start = self.html.index('<main class="page" id="page-resources">')
        resources_end = self.html.index('</main>', resources_start)
        self.assertGreater(self.start, resources_start)
        self.assertLess(self.end, resources_end)
        self.assertIn('id="market-inventory-research"', self.section)
        self.assertIn('id="market-category-breakdown"', self.section)
        self.assertIn('id="market-tam-scenarios"', self.section)
        self.assertIn('id="market-segment-ranking"', self.section)
        self.assertIn('id="market-current-positioning"', self.section)

    def test_inventory_scope_enrichment_and_official_baselines_are_present(self):
        for marker in ['119,174', '94,246', '59,794', '15,916', '18,536', '1,072',
                       '59,622', '72,962', '32,814', '14,971', '7,017',
                       '28,342', '100,757', '8,633', '32,619']:
            self.assertIn(marker, self.section)
        self.assertIn('Duval master-tax', self.section)
        self.assertIn('not a verified census', self.section)

    def test_every_observed_category_is_included(self):
        categories = [
            'Other / unknown commercial', 'Retail / consumer services', 'Healthcare',
            'Food / hospitality', 'Trades / field services', 'Professional services',
            'Beauty / wellness', 'Real estate brokerage', 'Finance / insurance',
            'Education / childcare', 'Automotive', 'Logistics / transport / warehousing',
            'Manufacturing / industrial', 'Technology / IT', 'Lodging / travel',
            'Cleaning / facilities services', 'Marine',
            'Property management / real estate operations', 'Recreation / events',
        ]
        for category in categories:
            self.assertIn(category, self.section)
        category_section = self.section.split('id="market-category-breakdown"', 1)[1].split('</table>', 1)[0]
        self.assertEqual(category_section.count('<tr>'), 20)  # header + 19 categories

    def test_tam_unit_economics_and_starting_segment_are_corrected(self):
        for marker in ['$43,094,000', '$4,245,600', '$52,142,000', '$15,462,800', '$742,400',
                       '$6,100', '$11,600', '$17,100', '$3,475', '$7,681', '$12,700',
                       '571', '19 customers', 'Duval HVAC, plumbing and electrical']:
            self.assertIn(marker, self.section)
        self.assertIn('credited toward deployment', self.section)
        self.assertIn('not break-even', self.section)
        self.assertIn('scenario', self.section.lower())

    def test_current_positioning_is_present_and_old_gtm_research_is_preserved(self):
        self.assertIn('Keep quotes moving when the day gets busy.', self.section)
        self.assertIn('id="gtm-research-sprint"', self.html)
        self.assertIn('10 providers + 2 native alternatives', self.html)

    def test_no_company_level_inventory_or_contact_export_is_published(self):
        for forbidden in ['duval-st-johns-location-prospects', 'initial-duval-trades-research-queue',
                          'qualification-public-channels', '@aol.com', '@gmail.com']:
            self.assertNotIn(forbidden, self.section)

    def test_html_ids_remain_unique(self):
        parser = IdParser()
        parser.feed(self.html)
        duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        self.assertEqual(duplicates, [])


if __name__ == '__main__':
    unittest.main()
