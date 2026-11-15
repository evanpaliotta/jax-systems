#!/usr/bin/env python3
"""Render one Markdown source into the reading view and existing Playbooks tab.

Requires markdown-it-py. No client records belong in the public source.
"""
from html import escape
from pathlib import Path
import re
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / 'customer-lifecycle-playbook.md').read_text(encoding='utf-8')
# Turn the mechanically rendered citation ledger into readable source links.
text = re.sub(r'^\[(\d+)\] (https://\S+) — (.+)$',
              lambda m: f'- [{m[1]}] [{m[3]}]({m[2]})', text, flags=re.M)
md = MarkdownIt('commonmark', {'html': False}).enable('table')
tokens = md.parse(text)
sections = []
for index, token in enumerate(tokens):
    if token.type == 'heading_open' and token.tag == 'h2':
        title = tokens[index + 1].content
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        if not slug or any(item[0] == slug for item in sections):
            raise ValueError(f'Invalid or duplicate section ID: {slug}')
        token.attrSet('id', slug)
        sections.append((slug, title))
if len(sections) != 18:
    raise ValueError(f'Expected 18 sections including Sources, got {len(sections)}')


def render(part):
    """Add functional citation jumps and locally scrollable reference tables."""
    out = md.renderer.render(part, md.options, {})
    out = re.sub(r'\[(\d+)\]', lambda m: f'<a class="citation" href="#source-{m[1]}" aria-label="Source {m[1]}">[{m[1]}]</a>', out)
    out = re.sub(r'<li><a class="citation" href="#source-(\d+)"', r'<li id="source-\1"><a class="citation" href="#source-\1"', out)
    return out.replace('<table>', '<div class="table-scroll" role="region" aria-label="Scrollable reference table" tabindex="0"><table>').replace('</table>', '</table></div>')

body = render(tokens)
nav = ''.join(f'<li><a href="#{escape(slug)}">{escape(title)}</a></li>' for slug, title in sections)
word_count = len(re.findall(r'\b[\w’\'-]+\b', text))
html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light">
<title>Customer Lifecycle Playbook — Jax Systems</title>
<style>
:root{--ink:#17251f;--muted:#5f6c63;--paper:#f3f0e7;--card:#fffdf7;--line:#d9d7c9;--clay:#b8562f;--moss:#1d4a3f}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--moss);text-underline-offset:3px}a:focus-visible,summary:focus-visible,.table-scroll:focus-visible,button:focus-visible{outline:3px solid var(--clay);outline-offset:3px}
.skip{position:absolute;left:15px;top:-100px;background:var(--card);padding:12px;z-index:10}.skip:focus{top:12px}
.bar{border-bottom:1px solid var(--line)}.bar-inner{max-width:1400px;margin:auto;padding:17px 24px;display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.bar-actions{display:flex;gap:18px;align-items:center;font-size:.84rem}
.brand{font-weight:750}.brand:before{content:"";display:inline-block;background:var(--clay);width:10px;height:10px;border-radius:50%;margin-right:10px;box-shadow:0 0 0 4px rgba(184,86,47,.14)}
.label{color:var(--muted);font-size:.8rem;font-weight:500}.bar button{font:inherit;color:var(--moss);background:transparent;border:1px solid var(--line);border-radius:5px;padding:7px 10px;cursor:pointer}
main{max-width:1400px;margin:auto;padding:28px 24px 80px}.kicker{font-size:.7rem;font-family:monospace;letter-spacing:.11em;text-transform:uppercase;color:var(--clay);font-weight:700}.meta{color:var(--muted);font-size:.8rem;margin:8px 0 22px}
.layout{display:grid;grid-template-columns:270px minmax(0,1fr);gap:26px;align-items:start}article{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:32px 42px;min-width:0;overflow-wrap:anywhere;box-shadow:0 18px 44px rgba(20,35,28,.04)}
h1,h2,h3{font-family:Georgia,"Times New Roman",serif;font-weight:500;line-height:1.22;letter-spacing:-.02em}h1{font-size:clamp(2rem,4vw,3.1rem);margin:.1em 0 .6em}h2{font-size:clamp(1.45rem,3vw,1.85rem);border-top:1px solid var(--line);margin:2.2em 0 .75em;padding-top:1em;scroll-margin-top:20px}h3{font-size:1.23rem;margin:1.8em 0 .55em}p,li{max-width:81ch}p{margin:.85em 0}li{margin:.45em 0}ul,ol{padding-left:1.45em}strong{font-weight:650}blockquote{margin:1em 0;border-left:3px solid var(--moss);background:#e8ecd9;padding:.35em 1em}blockquote p{margin:.4em 0}
.jump{position:sticky;top:20px;background:#e9e5d6;border:1px solid var(--line);border-radius:10px;padding:14px 16px;max-height:calc(100vh - 40px);overflow:auto}.jump summary{font-weight:700;cursor:pointer;font-size:.9rem}.jump ol{list-style:none;padding:0;margin:.9em 0 .2em}.jump li{font-size:.8rem;line-height:1.45;margin:.65em 0}.jump a{text-decoration:none}.jump a:hover{text-decoration:underline}
.table-scroll{overflow-x:auto;max-width:100%;margin:1em 0;border:1px solid var(--line);border-radius:7px}table{border-collapse:collapse;font-size:.85rem;min-width:560px;width:100%;line-height:1.5}th,td{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}th{background:#e8ecd9}tr:last-child td{border-bottom:0}.citation{font-size:.78em;white-space:nowrap;text-decoration:none;margin-left:2px}footer{color:var(--muted);font-size:.8rem;margin-top:22px}
@media(max-width:1000px){.layout{grid-template-columns:220px minmax(0,1fr);gap:18px}article{padding:25px}}
@media(max-width:760px){main{padding:22px 14px 50px}.bar-inner{padding:14px}.label{display:none}.layout{display:block}.jump{position:static;max-height:none;margin-bottom:18px}.jump ol{columns:2;column-gap:18px}.jump li{break-inside:avoid}article{padding:24px 20px}h1{font-size:2.1rem}}
@media(max-width:420px){.jump ol{columns:1}.bar-actions{gap:10px}.bar-actions a{max-width:115px;line-height:1.3}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:#fff;font-size:10pt}.bar,.jump,.kicker,.meta,.skip,footer{display:none}main{padding:0}.layout{display:block}article{border:0;box-shadow:none;padding:0}h2,h3{break-after:avoid}tr{break-inside:avoid}.table-scroll{overflow:visible;border:0}table{min-width:0;font-size:8pt}a{color:#111}}
</style></head><body><a class="skip" href="#manual">Skip to manual</a><header class="bar"><div class="bar-inner"><div class="brand">Jax Systems <span class="label">— operations field manual</span></div><div class="bar-actions"><a href="./">← Workspace</a><button id="print-manual" type="button">Print / Save PDF</button></div></div></header>
<main><div class="kicker">One client lifecycle · operating draft v2 · 14 November 2026</div>
<div class="meta">''' + f'{word_count:,} words · 17 operating sections + sources · Blank templates only; this is not a private client portal.' + '''</div>
<div class="layout"><details class="jump" open><summary>Contents / jump to a stage</summary><ol>''' + nav + '''</ol></details>
<article id="manual">''' + body + '''</article></div><footer>Internal operating design, publicly accessible. No outreach, monitoring, customer access or support service is activated by this manual.</footer></main>
<script>if(window.matchMedia('(max-width:760px)').matches)document.querySelector('.jump').open=false;document.getElementById('print-manual').addEventListener('click',()=>window.print());</script></body></html>'''
(ROOT / 'customer-lifecycle-playbook.html').write_text(html, encoding='utf-8')

# The marked region is the only generated part of the existing workspace.
starts = [i for i, t in enumerate(tokens) if t.type == 'heading_open' and t.tag == 'h2']
intro = render(tokens[:starts[0]])
intro = intro.replace('<h1>', '<h3>', 1).replace('</h1>', '</h3>', 1)
cards = []
for n, start in enumerate(starts):
    end = starts[n + 1] if n + 1 < len(starts) else len(tokens)
    title = escape(tokens[start + 1].content)
    content = render(tokens[start + 3:end])
    cards.append(f'<details class="panel lifecycle-stage" style="margin:10px 0"><summary style="cursor:pointer"><b>{title}</b></summary><div style="overflow-wrap:anywhere;min-width:0">{content}</div></details>')
embedded = ('\n  <style>#lifecycle-inline .table-scroll{overflow-x:auto;max-width:100%;margin:14px 0}#lifecycle-inline table{border-collapse:collapse;min-width:560px;width:100%;font-size:.85rem}#lifecycle-inline td,#lifecycle-inline th{padding:10px;text-align:left;vertical-align:top;border:1px solid var(--line)}#lifecycle-inline .citation{font-size:.8em;margin-left:2px}#lifecycle-inline details{min-width:0}#lifecycle-inline summary:focus-visible{outline:3px solid var(--clay)}</style>\n'
            '  <div class="sechead"><h2>Jax Customer Lifecycle Playbook</h2><span class="note">v2 · 17 operating sections + sources · expand sections</span></div>\n'
            '  <p><a href="./customer-lifecycle-playbook.html">Open the full reading / print view →</a></p>\n'
            '  <section id="lifecycle-inline" aria-label="Full customer lifecycle playbook">\n'
            '  <div class="panel lifecycle-intro">' + intro + '</div>\n  ' + '\n  '.join(cards) + '\n  </section>\n  ')
index_path = ROOT / 'index.html'
index_html = index_path.read_text(encoding='utf-8')
start_marker, end_marker = '<!-- LIFECYCLE EMBED START -->', '<!-- LIFECYCLE EMBED END -->'
if index_html.count(start_marker) != 1 or index_html.count(end_marker) != 1:
    raise ValueError('Expected one pair of lifecycle embed markers in index.html')
prefix, rest = index_html.split(start_marker, 1)
_, suffix = rest.split(end_marker, 1)
index_path.write_text(prefix + start_marker + embedded + end_marker + suffix, encoding='utf-8')
print(f'Rendered {len(sections)} sections / {word_count:,} words into standalone page and workspace')
