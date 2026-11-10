"""Generate 50 original Jax Systems vector directions with Kimi K3.1 Pro.

Pure vector concepts: model provides markup; strict validation prohibits active SVG,
external assets, text and gradients. The resulting marks remain review drafts.
"""
from pathlib import Path
import json,sys,xml.etree.ElementTree as ET,re,hashlib
from design_budget import call
ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/'logo-lab'
JOB=Path.home()/'Library/Mobile Documents/iCloud~md~obsidian/Documents/Brain Dump/Projects/Deploy Lab/Research/Logo Exploration/2026-11-10'
FAMILIES=[
 ('Connection','Ten different bold ways to express things joining, interlocking, linking or resolving into one clear handoff. Vary silhouette as well as geometry; avoid literal chain links, obvious tech nodes and the infinity symbol.'),
 ('Coastal Current','Ten distinct abstract forms informed by Jacksonville rivers, tide, flow, the coastline, movement and a clear channel. Mix glyphs, freeforms, angular and rounded silhouettes. Avoid surf shop cliches, literal fish, palms or jaguar logos.'),
 ('Jax Letterforms','Ten original abstract lettermarks: a mix of distinctive J, JS, JX and JAX letterforms constructed as vector shapes, some enclosed and some uncontained. Avoid text elements, fonts, text reading AI, and nearly identical X marks.'),
 ('Direction & Momentum','Ten distinct visual metaphors for making progress and finding a clear next step: pathway, turning point, waypoint, horizon, signal, forward, opening, rising, navigational cues. Avoid generic corporate arrows and the same silhouette repeated.'),
 ('Human & Craft','Ten distinct marks evoking a dependable human partner, meaningful collaboration, competent craft, small business and practical systems. Use abstract forms, badge, tools or negative-space architecture; avoid hearts, handshake stock icons, shields and robots.')]

def validate(body):
 root=ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'+body+'</svg>')
 tags={'svg','g','path','circle','rect','ellipse','polygon','polyline','line'}
 attrs={'d','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','fill-rule','clip-rule','points','x','y','width','height','rx','ry','cx','cy','r','x1','x2','y1','y2','transform'}
 if not len(root):raise ValueError('Empty SVG')
 for e in root.iter():
  if e.tag.split('}')[-1] not in tags:raise ValueError('Invalid SVG element '+e.tag)
  for k,v in e.attrib.items():
   if e is root and k=='viewBox':continue
   if k not in attrs or 'url(' in v.lower() or 'href' in v.lower():raise ValueError('Disallowed SVG attribute')
   if k in ('fill','stroke') and v not in ('none','currentColor'):raise ValueError('Only single ink')
   if k=='stroke-width' and float(v)<5:raise ValueError('Fine lines do not support embroidery')
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="currentColor">'+body+'</svg>'

def main():
 LAB.mkdir(parents=True,exist_ok=True);(LAB/'marks').mkdir(exist_ok=True)
 previous=[];all_marks=[]
 for fam,direction in FAMILIES:
  prompt=f'''Generate exactly 10 distinctly different art-directed BRAND LOGO SYMBOLS for Jax Systems; family {fam}: {direction}

Jax Systems is a Jacksonville-rooted practical systems partner for small businesses. Ethos: make day-to-day work flow, connect loose ends in existing tools, local trust, purposeful craft, humans keep judgment. Not an AI hype company, not only one industry. Visual tone: approachable, capable, confident and modern, with understated coastal roots. The user likes Clay.com and a Jaguars-inspired teal/black/gold palette, but DO NOT use Jaguars marks, sports logos, copied existing logos, overt coastline icons, or any gradients. These are for logos, hats, embroidery, shirts and website favicons, not concept illustrations. Optimize for one solid ink, clean negative space, clear at 24px and sewn at 1 inch.

Return ONLY a JSON object {{"logos":[{{"name":"short evocative name", "meaning":"one short line describing why this fits the brand", "body":"SVG child elements"}}, ... 10 total]}}. Each body is only SVG elements within a 100x100 viewBox, centered with margins ~12; use path, circle, rect, ellipse, polygon, polyline, line, g. Use one ink only: fill="currentColor" or stroke="currentColor" (or fill="none"). Stroke width at least 6, rounded joins/caps when suitable. Restrained single-color construction, no more than 5 objects, no tiny gaps under 5 units. No text, no style, no filter, no clip, no masks, no defs, no script, no logos in circles as the same repeated motif, no gradients or rendered lettering. Use geometry paths to render letterforms if applicable. Code should be valid XML using double-quoted attributes. Each of the 10 must have an immediately distinct outline and construction, not ten minor variations. Carefully craft actual SVG paths, not placeholders. Avoid reproducing existing brand marks. Already used names: {', '.join(previous)}.''' 
  result,usage=call(JOB,prompt,'You are a senior identity designer who draws original, minimal and distinctive SVG vector brand marks by hand. Return valid JSON only.',max_tokens=7500)
  items=result.get('logos',[])
  if len(items)!=10:raise ValueError(f'{fam}: expected 10, received {len(items)}')
  for x in items:
   name=x['name'].strip();meaning=x['meaning'].strip();svg=validate(x['body'].strip());index=len(all_marks)+1
   if any(m['svg']==svg for m in all_marks):raise ValueError('Duplicate geometry')
   item={'id':f'{index:02}','name':name,'family':fam,'meaning':meaning,'svg':svg,'generator':'moonshotai/kimi-k3.1-pro'}
   all_marks.append(item);previous.append(name)
   (LAB/'marks'/f'{index:02}.svg').write_text(svg+'\n')
  (LAB/'logos.json').write_text(json.dumps(all_marks,indent=2,ensure_ascii=False))
  print(json.dumps({'family':fam,'count':len(all_marks),'usage':usage}),flush=True)
 print('Generated',len(all_marks),'unique SVG symbols')
if __name__=='__main__':main()
