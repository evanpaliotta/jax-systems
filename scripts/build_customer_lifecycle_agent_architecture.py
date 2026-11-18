#!/usr/bin/env python3
"""Render the customer lifecycle agent architecture Markdown into a standalone HTML page."""
from pathlib import Path
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'customer-lifecycle-agent-architecture.md'
out = ROOT / 'customer-lifecycle-agent-architecture.html'
text = source.read_text(encoding='utf-8')
md = MarkdownIt('commonmark', {'html': False}).enable('table')
body = md.render(text)
html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <meta name="color-scheme" content="light">
  <title>Customer Lifecycle Agent Architecture — Jax Systems</title>
  <style>
    :root{{--ink:#17251f;--muted:#5f6c63;--paper:#f3f0e7;--card:#fffdf7;--line:#d9d7c9;--clay:#b8562f;--moss:#1d4a3f}}
    *{{box-sizing:border-box}}
    html{{scroll-behavior:smooth}}
    body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}}
    a{{color:var(--moss);text-underline-offset:3px}}
    a:focus-visible{{outline:3px solid var(--clay);outline-offset:3px}}
    .skip{{position:absolute;left:15px;top:-100px;background:var(--card);padding:12px;z-index:10}}
    .skip:focus{{top:12px}}
    .bar{{border-bottom:1px solid var(--line)}}
    .bar-inner{{max-width:1200px;margin:auto;padding:17px 24px;display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}}
    .brand{{font-weight:750}}
    .brand:before{{content:"";display:inline-block;background:var(--clay);width:10px;height:10px;border-radius:50%;margin-right:10px;box-shadow:0 0 0 4px rgba(184,86,47,.14)}}
    .label{{color:var(--muted);font-size:.8rem;font-weight:500}}
    main{{max-width:1200px;margin:auto;padding:28px 24px 80px}}
    article{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:32px 42px;min-width:0;overflow-wrap:anywhere;box-shadow:0 18px 44px rgba(20,35,28,.04)}}
    h1,h2,h3,h4{{font-family:Georgia,"Times New Roman",serif;font-weight:500;line-height:1.22;letter-spacing:-.02em}}
    h1{{font-size:clamp(2rem,4vw,3rem);margin:.1em 0 .6em}}
    h2{{font-size:clamp(1.45rem,3vw,1.85rem);border-top:1px solid var(--line);margin:2.2em 0 .75em;padding-top:1em;scroll-margin-top:20px}}
    h3{{font-size:1.2rem;margin:1.8em 0 .55em}}
    h4{{font-size:1.05rem;margin:1.4em 0 .45em}}
    p,li{{max-width:84ch}}
    p{{margin:.85em 0}}
    li{{margin:.45em 0}}
    ul,ol{{padding-left:1.45em}}
    strong{{font-weight:650}}
    code,pre{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}
    code{{background:#f2eee3;border:1px solid #e6e1d1;padding:.08em .35em;border-radius:6px;font-size:.92em}}
    pre{{background:#f2eee3;border:1px solid #e6e1d1;border-radius:10px;padding:16px;overflow:auto;line-height:1.55}}
    pre code{{background:none;border:0;padding:0}}
    blockquote{{margin:1em 0;border-left:3px solid var(--moss);background:#e8ecd9;padding:.35em 1em}}
    table{{border-collapse:collapse;width:100%;font-size:.9rem;margin:1.1em 0}}
    th,td{{padding:12px 14px;text-align:left;vertical-align:top;border:1px solid var(--line)}}
    th{{background:#e8ecd9}}
    footer{{color:var(--muted);font-size:.8rem;margin-top:22px}}
    @media(max-width:760px){{main{{padding:22px 14px 50px}}.bar-inner{{padding:14px}}.label{{display:none}}article{{padding:24px 20px}}h1{{font-size:2.1rem}}}}
    @media print{{body{{background:#fff;font-size:10pt}}.bar,.skip,footer{{display:none}}main{{padding:0}}article{{border:0;box-shadow:none;padding:0}}a{{color:#111}}}}
  </style>
</head>
<body>
  <a class="skip" href="#manual">Skip to document</a>
  <header class="bar"><div class="bar-inner"><div class="brand">Jax Systems <span class="label">— agent architecture</span></div><div><a href="./">← Workspace</a></div></div></header>
  <main>
    <article id="manual">{body}</article>
    <footer>Internal architecture note, publicly accessible. No live client data, automation, outreach, monitoring, or support coverage is activated by this document.</footer>
  </main>
</body>
</html>'''
out.write_text(html, encoding='utf-8')
print(f'Rendered {source.name} -> {out.name}')
