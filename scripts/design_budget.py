"""Bounded, serial OpenRouter design calls. Never logs or persists the API key.

This controls this runner's incremental API spending, NOT the user's account-wide limit.
Unknown/failed calls retain their full reservation. No auto retries or model fallback.
"""
from pathlib import Path
from decimal import Decimal
import json
import math
import os
import time
import urllib.request
import urllib.error

MODEL = 'moonshotai/kimi-k3.1-pro'
CAP = 20.0
MAX_REQUESTS = 30  # 25 completed rounds plus a bounded allowance for failed calls
PROMPT_RATE = 2.0 / 1_000_000
OUTPUT_RATE = 10.0 / 1_000_000

def reserve(state, ceiling, cap=CAP):
    if ceiling is None or not math.isfinite(ceiling) or ceiling < 0:
        raise ValueError('Unverified request cost; refusing network call')
    if state['charged'] + state['pending'] + ceiling > cap:
        raise ValueError('Request reservation would exceed task budget')
    state['pending'] += ceiling


def credential():
    value = os.getenv('OPENROUTER_API_KEY')
    if value: return value
    for line in (Path.home() / '.hermes/.env').read_text().splitlines():
        if line.startswith('OPENROUTER_API_KEY='):
            return line.split('=', 1)[1].strip().strip('\"\'')
    raise ValueError('OpenRouter credential is unavailable')


def call(job, prompt, system, max_tokens=5000, image=None):
    job = Path(job)
    job.mkdir(parents=True, exist_ok=True)
    ledger = job / 'budget.json'
    state = json.loads(ledger.read_text()) if ledger.exists() else {'charged': 0, 'pending': 0, 'calls': []}
    if state['pending']:
        raise ValueError('Unresolved earlier request; stop rather than risk a duplicate charge')
    if len(state['calls']) >= MAX_REQUESTS: raise ValueError('25-request limit reached')
    content = [{'type': 'text', 'text': prompt}]
    # Image requests are capped to one 480x480 JPEG; a deliberately loose visual-token reserve.
    image_reserve = 0
    if image:
        import base64
        from PIL import Image
        p = Path(image)
        im = Image.open(p)
        if im.width > 480 or im.height > 480: raise ValueError('Image exceeds budgeted size')
        image_reserve = 262144
        content.append({'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + base64.b64encode(p.read_bytes()).decode()}})
    token_ceiling = len((prompt + system).encode('utf-8')) + 4096 + image_reserve
    ceiling = token_ceiling * PROMPT_RATE + max_tokens * OUTPUT_RATE
    reserve(state, ceiling)
    entry = {'round': len(state['calls']) + 1, 'reserved_usd': ceiling, 'model': MODEL, 'status': 'in_flight', 'started': time.time()}
    state['calls'].append(entry)
    ledger.write_text(json.dumps(state, indent=2))
    payload = {'model': MODEL, 'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': content}],
        'max_tokens': max_tokens, 'temperature': .55, 'reasoning': {'enabled': False},
        'provider': {'max_price': {'prompt': 2, 'completion': 10}, 'require_parameters': True, 'sort': 'price'},
        'usage': {'include': True}, 'response_format': {'type': 'json_object'}}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(payload).encode(),
        headers={'Authorization': 'Bearer ' + credential(), 'Content-Type': 'application/json', 'X-Title': 'Jax 25-round bounded design study'})
    try:
        with urllib.request.urlopen(req, timeout=240) as response: result = json.load(response)
        cost = result.get('usage', {}).get('cost')
        charge = float(cost) if cost is not None and float(cost) >= 0 else ceiling
        entry.update({'status': 'completed', 'id': result.get('id'), 'provider': result.get('provider'), 'usage': result.get('usage'), 'charged_usd': charge, 'finished': time.time()})
        state['charged'] += charge
        state['pending'] = 0
        ledger.write_text(json.dumps(state, indent=2))
        (job / f'response-{entry["round"]:02}.json').write_text(json.dumps(result, indent=2))
        if charge > ceiling: raise ValueError('Provider charge exceeded reservation; halted')
        msg = result['choices'][0]['message']['content']
        data = json.loads(msg)
        return data, {'round': entry['round'], 'cost': charge, 'total': state['charged'], 'provider': entry.get('provider')}
    except Exception:
        if entry['status'] == 'in_flight':
            entry['status'] = 'failed_or_unknown'
            state['charged'] += ceiling
            state['pending'] = 0
            ledger.write_text(json.dumps(state, indent=2))
        raise
