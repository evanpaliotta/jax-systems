#!/usr/bin/env python3
"""Regression checks for the existing playbook rendered inside the workspace."""
from pathlib import Path
import unittest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


class LifecycleWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = BeautifulSoup((ROOT / 'index.html').read_text(encoding='utf-8'), 'html.parser')
        cls.standalone = BeautifulSoup((ROOT / 'customer-lifecycle-playbook.html').read_text(encoding='utf-8'), 'html.parser')

    def test_full_playbook_exists_inside_playbooks_tab(self):
        inline = self.index.select_one('#page-playbooks #lifecycle-inline')
        self.assertIsNotNone(inline, 'Full playbook must be embedded inside the Playbooks tab')
        self.assertEqual(len(inline.select('details')), 13)
        expected = self.standalone.select_one('article').get_text(' ', strip=True)
        self.assertEqual(inline.get_text(' ', strip=True), expected)

    def test_existing_navigation_and_standalone_link_are_preserved(self):
        tabs = {tag['data-page'] for tag in self.index.select('nav.tabs button.tab')}
        self.assertTrue({'model', 'offer', 'delivery', 'gtm', 'verticals', 'fde', 'playbooks', 'agency', 'resources', 'names'}.issubset(tabs))
        link = self.index.select_one('#page-playbooks a[href="./customer-lifecycle-playbook.html"]')
        self.assertIsNotNone(link)


if __name__ == '__main__':
    unittest.main()
