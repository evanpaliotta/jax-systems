"""Run 24 refinement reviews after the Kimi-authored 3D baseline, with checkpoints."""
from pathlib import Path
import sys,json,subprocess,shutil,base64,time
from PIL import Image
from design_budget import call
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'design-lab/concepts/13-jax-workshop'
JOB=Path.home()/'Library/Mobile Documents/iCloud~md~obsidian/Documents/Brain Dump/Projects/Deploy Lab/Research/Website Iteration/2026-11-10'
FOCUS=['hero visual hierarchy','first-impression clarity','Jaguar-inspired palette and contrast','mobile hero composition','interactive function example comprehension','homepage concision','tab keyboard behavior','industry navigation and discovery','SMB catalogue specificity','healthcare and sensitive-data boundaries','pricing legibility without changing prices','small-screen menu and touch targets','document intake and human accountability','workflow-board visual rhythm','tablet layout','search empty-state behavior','motion restraint and reduced motion','premium whitespace and typography','CTA honesty and preview behavior','cross-page visual consistency','accessibility and focus visibility','remove remaining generic-template cues','regression review and simplification','final skeptical-owner review']
allowed={'workshop.css','workshop.js','index.html','ways-we-help.html','how-it-works.html','pricing.html','contact.html'}
def cmd(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=80)
 if r.returncode:raise RuntimeError(r.stderr[:500])
 return r.stdout
reports=[]
for n,focus in enumerate(FOCUS,2):
 target='ways-we-help.html' if n in [9,10,11,17] else ('pricing.html' if n==12 else 'index.html')
 url='http://127.0.0.1:8765/design-lab/concepts/13-jax-workshop/'+target
 cmd(['agent-browser','--session','jax-loop','set','viewport','1440','1000']);cmd(['agent-browser','--session','jax-loop','open',url])
 shot=JOB/f'round-{n:02}-before.png';cmd(['agent-browser','--session','jax-loop','screenshot',str(shot)])
 im=Image.open(shot).convert('RGB');im.thumbnail((480,480));small=JOB/f'round-{n:02}-input.jpg';im.save(small,quality=75)
 geometry=cmd(['agent-browser','--session','jax-loop','eval',"JSON.stringify({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,words:document.body.innerText.split(/\\s+/).length})"])
 files=['workshop.css','workshop.js',target]
 text='\n'.join('FILE '+f+'\n'+(D/f).read_text() for f in files)
 prompt=f'''Refinement round {n}/25. Focus: {focus}. Inspect the actual screenshot first, then the current source. Improve only concrete weaknesses. Original brief: premium Clay.com-inspired concise Jax Systems SMB operations website; teal #006778, gold #D7A22A, black #101820. Original locally rendered 3D hero shows phone intake -> context sorting -> human approval. No copied Clay assets. 19 SMB categories/57 illustrative scenarios already exist on separate page. Keep breadth, pricing and human/privacy boundaries. No new widgets, claims, backend, testimonials or long sections. Keep what works; a no-change review is valid if no demonstrable improvement. Do not force feature growth. Current geometry: {geometry}. Previous accepted reviews: {json.dumps(reports[-5:])}. Return ONLY JSON {{"summary":"specific critique and improvement or reason to keep", "edits":[{{"file":"workshop.css or workshop.js or supplied html file","find":"unique exact source substring","replace":"replacement"}}]}}. Maximum 2 small, precise edits. A screenshot is evidence of layout, not conversion performance. Never add overflow hidden to mask text defects. Source:\n{text}'''
 before={f:(D/f).read_text() for f in allowed}
 result,cost=call(JOB,prompt,'You are Kimi K3.1 Pro, a senior frontend creative coder. Ground every proposed edit in the supplied screenshot and code. Return valid JSON only, no reasoning prose.',max_tokens=3500,image=small)
 accepted=True;reason=''
 try:
  edits=result.get('edits',[])
  if len(edits)>2:raise ValueError('Too many edits')
  for edit in edits:
   f=edit['file'];find=edit['find'];replace=edit['replace']
   if f not in files or f not in allowed:raise ValueError('Non-allowlisted path')
   current=(D/f).read_text()
   if not find or current.count(find)!=1:raise ValueError('Ambiguous/nonexistent source')
   (D/f).write_text(current.replace(find,replace,1))
  cmd(['node','--check',str(D/'workshop.js')])
  cmd(['agent-browser','--session','jax-loop','reload'])
  for width in [390,1440]:
   cmd(['agent-browser','--session','jax-loop','set','viewport',str(width),'1000'])
   state=cmd(['agent-browser','--session','jax-loop','eval','document.documentElement.scrollWidth>innerWidth'])
   if state.strip()=='true':raise ValueError('Introduced document overflow')
 except Exception as e:
  accepted=False;reason=str(e)
  for f,t in before.items():(D/f).write_text(t)
 record={'round':n,'focus':focus,'summary':result.get('summary'),'accepted':accepted,'edits':len(result.get('edits',[])) if accepted else 0,'rejection':reason,'cost':cost}
 reports.append(record)
 checkpoint=JOB/f'checkpoint-{n:02}';checkpoint.mkdir(exist_ok=True)
 for f in allowed:shutil.copy2(D/f,checkpoint/f)
 (JOB/'rounds.json').write_text(json.dumps(reports,indent=2))
 print(json.dumps(record),flush=True)
print('25-round study completed: baseline + 24 checkpointed refinement reviews',flush=True)
