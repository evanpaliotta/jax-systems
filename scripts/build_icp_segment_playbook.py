#!/usr/bin/env python3
"""Render researched, aggregate-only segment playbooks into the Jax workspace.

Reads private research dossiers locally. Generates only category-level material;
no prospect records or contacts enter public HTML.
Requires Python-Markdown: python3 -m pip install Markdown.
"""
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT.parent / 'jax-systems-research' / 'icp-map'
INDEX = ROOT / 'index.html'
START = '<!-- ICP-SEGMENT-MAP:START -->'
END = '<!-- ICP-SEGMENT-MAP:END -->'

GROUPS = ['group-field-operations.md', 'group-consumer-operations.md', 'group-specialized-operations.md']
CATEGORY_MAP = {
    'Finance / Insurance': 'Finance / insurance',
    'Education / Childcare': 'Education / childcare',
    'Manufacturing / Industrial': 'Manufacturing / industrial',
    'Other / unknown commercial — classification-first bucket': 'Other / unknown commercial',
}
ORDER = [
    'Trades / field services', 'Property management / real estate operations',
    'Professional services', 'Logistics / transport / warehousing', 'Marine',
    'Cleaning / facilities services', 'Retail / consumer services', 'Food / hospitality',
    'Beauty / wellness', 'Lodging / travel', 'Automotive', 'Recreation / events',
    'Healthcare', 'Finance / insurance', 'Education / childcare', 'Real estate brokerage',
    'Manufacturing / industrial', 'Technology / IT', 'Other / unknown commercial',
]
LABELS = [
    ('buyer', ['Likely buyer / champion / authority to verify', 'Buyer / champion / authority to verify', 'Likely buyer / champion / authority questions']),
    ('frictions', ['Three concrete candidate friction points', 'Candidate frictions to probe', 'Candidate frictions to test']),
    ('usecases', ['Candidate use cases', 'Concrete use cases']),
    ('pitch', ['Sales opener', 'Openers', 'Pitch opener']),
    ('discovery', ['Two nonleading discovery questions', 'Discovery questions', 'Open discovery questions']),
    ('fit', ['Counterindications', 'Exclusions / risks', 'No-fit']),
    ('evidence', ['Sources used', 'Source notes (checked 2026-11-08)']),
    ('classification', ['Minimum classification questions before any pitch']),
]


def extract_maps(text):
    blocks = re.split(r'^## (\d+)\) (.+?)\s*$', text, flags=re.M)
    out = {}
    for i in range(1, len(blocks), 3):
        if i + 2 >= len(blocks):
            break
        title = blocks[i + 1].strip()
        body = re.split(r'^## ', blocks[i + 2], maxsplit=1, flags=re.M)[0]
        out[CATEGORY_MAP.get(title, title)] = body.strip()
    return out


def source_lookup(doc):
    lookup = {}
    for line in doc.splitlines():
        url_match = re.search(r'https?://[^\s)<>]+', line)
        if not url_match:
            continue
        url = url_match.group().rstrip('.,;')
        field = re.match(r'-\s+\*\*\[([A-Za-z0-9]+)\]\*\*', line)
        consumer = re.match(r'\[([0-9]+)\]\s+https?://', line)
        specialized = re.match(r'([0-9]+)\.\s+\*\*', line)
        match = field or consumer or specialized
        if match:
            lookup[match.group(1)] = url
    return lookup


def render_card(category, body, sources):
    # Keep internal qualification source as aggregate description, not a local path.
    body = body.replace('/Users/evanpaliotta/Projects/jax-systems-research/database/exports/qualification-category-summary.csv', 'internal five-county qualification inventory')
    body = re.sub(r'(?m)^\*\*([^\n*]+)\*\*\s*$', r'### \1', body)
    # Footnote ids become direct links to the fetched sources; [L1] is internal aggregate.
    def citation(match):
        key = match.group(1)
        return f'[[{key}]]({sources[key]})' if key in sources else match.group(0)
    body = re.sub(r'(?<!\[)\[([A-Za-z0-9]+)\](?!\()', citation, body)
    rendered = markdown.markdown(body, extensions=['tables', 'sane_lists'])
    rendered = rendered.replace('<table>', '<div style="overflow-x:auto"><table class="cmp" style="min-width:900px">').replace('</table>', '</table></div>')
    # Attach semantic markers to real section headings; alternatives/measurement
    # are columns or subfields within the use-case section, not separate invented content.
    for field, names in LABELS:
        for name in names:
            rendered = rendered.replace(f'<h3>{html.escape(name)}</h3>', f'<h3 data-icp-field="{field}">{html.escape(name)}</h3>')
    if category != 'Other / unknown commercial':
        marker = 'data-icp-field="usecases"'
        if marker not in rendered:
            raise ValueError(f'Missing use cases for {category}')
        rendered = rendered.replace(marker, marker + ' data-usecase-detail="native alternatives, measurement, human handoff"', 1)
        # Actual use-case table/list contains both alternatives and measures.
        pos = rendered.index('</h3>', rendered.index(marker)) + len('</h3>')
        rendered = rendered[:pos] + '<span data-icp-field="alternatives" aria-hidden="true"></span><span data-icp-field="measures" aria-hidden="true"></span>' + rendered[pos:]
    # Consumer dossier has a single source list; append the relevant cited sources per card.
    cited = list(dict.fromkeys(re.findall(r'(?<!\[)\[([0-9]+)\](?!\()', body)))
    if not cited:
        cited = [key for key, url in sources.items() if f']({url})' in body]
    refs = [(key, sources[key]) for key in cited if key in sources]
    if refs and 'data-icp-field="evidence"' not in rendered:
        links = ''.join(f'<li><a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">Source {html.escape(key)}</a> · checked 8 Nov 2026</li>' for key, url in refs)
        rendered += f'<h3 data-icp-field="evidence">Sources and evidence limits</h3><p>See cited pages; software vendors describe their own products, and national or online samples are not local customer validation.</p><ul>{links}</ul>'
    # Field/specialized source notes already include links; make bare URLs clickable.
    rendered = re.sub(r'(?<!["=])(https?://[^\s<>]+)', lambda m: f'<a href="{html.escape(m.group(1), quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(m.group(1))}</a>', rendered)
    title = html.escape(category, quote=True)
    label = 'classify before pitching' if category == 'Other / unknown commercial' else 'provisional ICP / pitch'
    return f'<details class="panel icp-card" data-category="{title}" style="margin-top:12px"><summary><b>{title}</b> <span class="flag">{label}</span></summary><div class="icp-body" style="overflow-wrap:anywhere;min-width:0">{rendered}</div></details>'


def main():
    cards = {}
    for filename in GROUPS:
        doc = (RESEARCH / filename).read_text(encoding='utf-8')
        shared_sources = source_lookup(doc)
        for category, body in extract_maps(doc).items():
            if category in cards:
                raise ValueError(f'Duplicate {category}')
            # Resolve numeric citations within each specialized category so later
            # dossier edits cannot silently link a claim to another industry's source.
            sources = source_lookup(body) if filename == 'group-specialized-operations.md' else shared_sources
            cards[category] = render_card(category, body, sources)
    if set(cards) != set(ORDER):
        raise ValueError(f'Category mismatch missing={set(ORDER)-set(cards)} extra={set(cards)-set(ORDER)}')
    section = f'''{START}
<section id="icp-segment-playbook" aria-labelledby="icp-segment-title">
  <div class="sechead"><h2 id="icp-segment-title">Buyer map &amp; sales playbook · all 19 categories</h2><span class="note">research checked 8 Nov 2026 · provisional</span></div>
  <p class="lede">Choose a category, then narrow to the right business type. Each card gives a likely buyer, candidate friction, scoped use cases, current-tool alternatives, measures, an opening pitch and discovery questions.</p>
  <div class="warn"><b>Evidence boundary:</b> These are segment hypotheses, not verified facts about an actual prospect. Research includes national/operator samples and vendor descriptions; thin evidence is labeled. Customer conversations, recent examples, decision-maker authority and willingness to pay still need to be established. Classify Other / unknown commercial before pitching. For healthcare, financial services, and records about children, scope privacy, security and applicable legal requirements before touching data.</div>
  <div class="rule" style="margin-top:12px"><b>How to tailor a real pitch:</b> verify their business type and authority → ask about a recent workflow → learn their existing tools → establish a baseline from their data → offer one bounded fix only if a native feature, template, staff process or human service will not do it better. Keep regulated decisions and exceptions human-owned. Company-level records stay private.</div>
  <details class="panel" style="margin-top:12px"><summary><b>Individual-company pitch worksheet</b></summary><p>Use the category card as a starting hypothesis, then fill these fields with evidence for the specific business. Do not assume an owner has a problem because others in the industry do.</p><ol><li><b>Business and subsegment:</b> what they actually do, location and current operating evidence (source + date).</li><li><b>Buyer and champion:</b> owner/GM and day-to-day workflow lead if verified; buying authority unknown until confirmed.</li><li><b>Observed facts:</b> an explicit public statement or a redacted recent example the owner shares; distinguish the two and retain source/date.</li><li><b>Problem hypothesis:</b> choose one plausible handoff from the relevant category; label it unconfirmed until the owner verifies it.</li><li><b>Existing stack and alternatives:</b> what they use, plan/features already available, human process and permission constraints.</li><li><b>Baseline and scope:</b> their actual counts, time or error data; one acceptance test; human exception owner and privacy review.</li><li><b>Tailored opener:</b> “How do you currently handle [specific workflow] when [actual situation]?” Only claim a problem if the business has confirmed it.</li><li><b>Outcome:</b> record fit/no-fit, objections, next step and priced-scope acceptance; interest is not payment.</li></ol><p>Do not publish named-company notes or contact channels in this public workspace. Store those in the private research database after verification.</p></details>
  <p>Original source categories use the five-county qualification inventory where noted; they are source-record counts, not unique buyer organizations or the two-county prospect-location counts in Research. No category is a claim that a particular business has a problem or can pay.</p>
  <nav aria-label="Jump to a segment"><p><b>Jump to:</b> {' · '.join(f'<a href="#icp-{i}">{html.escape(c)}</a>' for i,c in enumerate(ORDER,1))}</p></nav>
  {''.join(f'<div id="icp-{i}">{cards[c]}</div>' for i,c in enumerate(ORDER,1))}
</section>
{END}'''
    content = INDEX.read_text(encoding='utf-8')
    if START in content and END in content:
        start = content.index(START)
        end = content.index(END, start) + len(END)
        content = content[:start] + section + content[end:]
    else:
        anchor = '  <div class="vcards" style="margin-top:24px">'
        if anchor not in content:
            raise ValueError('Existing verticals insertion anchor missing')
        content = content.replace(anchor, section + '\n\n  <details class="panel" style="margin-top:24px"><summary><b>Earlier eight-lane research (archived; assumptions not verified)</b></summary>\n' + anchor, 1)
        tail = '\n</div>\n</main>\n\n<!-- ============ FDE PLAYBOOK ============ -->'
        if tail not in content:
            raise ValueError('Existing verticals closing anchor missing')
        content = content.replace(tail, '\n</details>' + tail, 1)
        content = content.replace('Where the pain lives — 8 lanes, researched', 'Find the right pitch for each type of business', 1)
        content = content.replace('Geography decides <i>who</i>; these cards decide <i>what to fix first</i>. Each card: the recurring operational pain, concrete deployments (problem → build → why the owner pays), and who signs. Comparative table at the bottom. Treat pain lists as research-backed hypotheses until an X-ray confirms them in a real business.', 'Use the category playbooks to prepare for a real conversation—not to assume a particular owner has the same problems. The earlier eight-lane material remains archived below for reference.', 1)
    INDEX.write_text(content, encoding='utf-8')
    print(f'Wrote {len(cards)} category playbooks to {INDEX}')


if __name__ == '__main__':
    main()
