#!/usr/bin/env python3
"""Render the checked-in Jax Systems lifecycle playbook as an offline static page.

Requires markdown-it-py. Edit the Markdown and rebuild; synchronize the Obsidian
project note when the text changes. No client/prospect data belongs here.
"""
from html import escape
from pathlib import Path
import re
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / 'customer-lifecycle-playbook.md').read_text(encoding='utf-8')
md = MarkdownIt('commonmark', {'html': False})
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
if len(sections) != 13:
    raise ValueError(f'Expected 13 sections, got {len(sections)}')
body = md.renderer.render(tokens, md.options, {})
nav = ''.join(f'<li><a href="#{escape(slug)}">{escape(title)}</a></li>' for slug, title in sections)
html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light">
<title>Customer Lifecycle Playbook — Jax Systems</title>
<style>
:root{--ink:#141715;--muted:#5f6c63;--paper:#f3f0e7;--card:#fffdf7;--line:#d9d7c9;--clay:#b8562f;--moss:#1d4a3f}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--moss);text-underline-offset:3px}a:focus-visible,summary:focus-visible{outline:3px solid var(--clay);outline-offset:3px}
.bar{border-bottom:1px solid var(--line);background:rgba(243,240,231,.96)}.bar-inner{max-width:1020px;margin:auto;padding:15px 25px;display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}
.brand{font-weight:700}.brand:before{content:"";display:inline-block;background:var(--clay);width:10px;height:10px;border-radius:50%;margin-right:10px;box-shadow:0 0 0 4px rgba(184,86,47,.14)}
.label{color:var(--muted);font-size:.8rem;font-weight:500}.bar a{font-size:.9rem}
main{max-width:1020px;margin:auto;padding:30px 25px 80px}.kicker{font-size:.7rem;font-family:monospace;letter-spacing:.13em;text-transform:uppercase;color:var(--clay);font-weight:700}
article{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:30px 38px;box-shadow:0 18px 44px rgba(20,35,28,.07)}
h1,h2,h3{font-family:Georgia,"Times New Roman",serif;font-weight:500;line-height:1.18;letter-spacing:-.02em}h1{font-size:clamp(2rem,4.7vw,3.2rem);margin:.3em 0 .45em}h2{font-size:clamp(1.45rem,3vw,1.8rem);border-top:1px solid var(--line);margin:2.2em 0 .6em;padding-top:1em;scroll-margin-top:20px}h3{font-size:1.15rem;margin:1.6em 0 .5em}p,li{max-width:78ch}p{margin:.8em 0}li{margin:.4em 0}ul,ol{padding-left:1.4em}blockquote{margin:1em 0;border-left:3px solid var(--moss);background:#e8ecd9;border-radius:4px;padding:.35em 1em}blockquote p{margin:.4em 0}
.jump{margin:18px 0 22px;background:#e9e5d6;border:1px solid var(--line);border-radius:10px;padding:12px 16px}.jump summary{font-weight:700;cursor:pointer}.jump ol{columns:2;column-gap:30px;margin:.8em 0 .2em}.jump li{break-inside:avoid;font-size:.9rem}
footer{color:var(--muted);font-size:.8rem;margin-top:22px}.status{color:var(--clay)}
@media(max-width:620px){main{padding:22px 14px 50px}.bar-inner{padding:13px 15px}article{padding:23px 20px}.jump ol{columns:1}h1{font-size:2.1rem}body{font-size:16px}}
@media print{body{background:#fff}.bar,.jump{display:none}main{padding:0}article{border:0;box-shadow:none;padding:0}h2{break-after:avoid}a{color:#111}}
</style></head><body><header class="bar"><div class="bar-inner"><div class="brand">Jax Systems <span class="label">— working notes</span></div><a href="./">← Back to workspace</a></div></header>
<main><div class="kicker">Internal planning · draft · publicly accessible</div>
<details class="jump"><summary>Jump to a section</summary><ol>''' + nav + '''</ol></details>
<article>''' + body + '''</article><footer>Working draft · no marketing, outreach or customer access is activated by this page.</footer></main></body></html>'''
(ROOT / 'customer-lifecycle-playbook.html').write_text(html, encoding='utf-8')
print(f'Rendered {len(sections)} sections, {len(html)} characters')
