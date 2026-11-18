from pathlib import Path
import unittest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


class AgentArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = (ROOT / 'customer-lifecycle-agent-architecture.md').read_text(encoding='utf-8')
        cls.html = (ROOT / 'customer-lifecycle-agent-architecture.html').read_text(encoding='utf-8')
        cls.doc = BeautifulSoup(cls.html, 'html.parser')

    def test_markdown_contains_required_sections(self):
        for marker in [
            '# Jax Systems: Customer Lifecycle Agent Architecture',
            '## Verdict',
            '## Architecture',
            '## Router logic',
            '## Approval boundaries',
            '## Proposed skills',
            '## State model',
            '## File layout',
            '## Implementation order',
            '## Avoid',
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, self.md)

    def test_html_renders_title_and_sections(self):
        self.assertEqual(self.doc.title.get_text(strip=True), 'Customer Lifecycle Agent Architecture — Jax Systems')
        text = self.doc.get_text(' ', strip=True)
        for marker in [
            'Jax Systems: Customer Lifecycle Agent Architecture',
            'Do not turn the full playbook into one giant bot.',
            'The router should follow this order:',
            'Recommended v1 layout:',
            'That gets Jax an operator it can trust before it gets an agent it can brag about.',
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_document_does_not_publish_private_home_paths(self):
        self.assertNotIn('/Users/evanpaliotta', self.md)
        self.assertNotIn('/Users/evanpaliotta', self.html)


if __name__ == '__main__':
    unittest.main()
