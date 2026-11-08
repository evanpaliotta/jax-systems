#!/usr/bin/env python3
"""Insert aggregate-only Jax Systems market research into the public workspace."""
from __future__ import annotations

import csv
import gzip
import json
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT.parent / 'jax-systems-research'
TAM = RESEARCH / 'database/tam'
EXPORTS = RESEARCH / 'database/exports'
INDEX = ROOT / 'index.html'
START = '<!-- MARKET-RESEARCH:START -->'
END = '<!-- MARKET-RESEARCH:END -->'


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def integer(value: str | int | float) -> int:
    return int(float(value))


def number(value: str | int | float) -> str:
    return f'{integer(value):,}'


def money(value: str | int | float) -> str:
    return f'${integer(value):,}'


def percent(part: int, total: int) -> str:
    return f'{100 * part / total:.1f}%'


def table(headers: list[str], rows: list[list[str]], min_width: int = 700) -> str:
    head = ''.join(f'<th>{escape(str(header))}</th>' for header in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(cell))}</td>' for cell in row) + '</tr>' for row in rows)
    return f'<div style="overflow-x:auto"><table class="cmp" style="min-width:{min_width}px"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def category_stats() -> list[dict]:
    stats = Counter()
    grouped = {}
    with gzip.open(EXPORTS / 'duval-st-johns-location-prospects.csv.gz', 'rt', encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            item = grouped.setdefault(row['primary_category'], Counter())
            item['locations'] += 1
            for key, column in [('website', 'website_url'), ('phone', 'public_business_phone'), ('email', 'public_business_email'), ('legal', 'legal_entity_name'), ('dba', 'fictitious_name')]:
                item[key] += bool(row[column])
    output = []
    for category, values in sorted(grouped.items(), key=lambda item: (-item[1]['locations'], item[0])):
        output.append({'category': category, **values})
    return output


def build() -> str:
    metrics = json.loads((EXPORTS / 'prospect-metrics.json').read_text())
    legal_metrics = json.loads((EXPORTS / 'legal-match-metrics.json').read_text())
    categories = category_stats()
    coverage = read_csv(TAM / 'official_coverage.csv')
    baselines = {row['category']: row for row in read_csv(TAM / 'category_baselines.csv')}
    spend = read_csv(TAM / 'annual_spend_surface.csv')
    sensitivity = read_csv(TAM / 'annual_buyer_sensitivity.csv')
    economics = read_csv(TAM / 'first_year_unit_economics.csv')
    targets = read_csv(TAM / 'revenue_planning_targets.csv')
    ranking = read_csv(TAM / 'segment_ranking.csv')

    coverage_rows = [[row['county'], number(row['employer_establishments']), number(row['nonemployer_firms']), number(row['size_5_49_published_subtotal'])] for row in coverage]
    scope_rows = [[scope, number(value)] for scope, value in metrics['by_scope_county'].items()]
    category_rows = [[row['category'], number(row['locations']), percent(row['website'], row['locations']), percent(row['phone'], row['locations']), percent(row['email'], row['locations']), percent(row['legal'], row['locations']), percent(row['dba'], row['locations'])] for row in categories]
    tam_rows = []
    for category in ['Trades', 'Property management', 'Professional services', 'Logistics', 'Marine']:
        baseline = baselines[category]
        scenario_values = {row['scenario']: row for row in spend if row['category'] == category}
        tam_rows.append([category, number(baseline['baseline_count']), baseline['baseline_unit'], baseline['reference_year'], money(scenario_values['low']['category_scope_annual_spend_surface_usd']), money(scenario_values['base']['category_scope_annual_spend_surface_usd']), money(scenario_values['high']['category_scope_annual_spend_surface_usd'])])
    sensitivity_rows = []
    for row in sensitivity:
        if row['annual_buyer_share_assumption'] == '0.05':
            sensitivity_rows.append([row['category'], number(row['annual_buyers_scenario']), money(row['annual_spend_scenario_usd'])])
    economic_rows = []
    for row in economics:
        target140 = next(item for item in targets if item['scenario'] == row['scenario'] and item['annual_revenue_planning_target'] == '140000')
        target210 = next(item for item in targets if item['scenario'] == row['scenario'] and item['annual_revenue_planning_target'] == '210000')
        economic_rows.append([row['scenario'], money(row['full_year_equivalent_spend']), money(row['average_first_year_revenue']), f"{float(row['care_attach_rate']):.0%}", row['capacity_customers_assumption'], money(row['capacity_first_year_revenue']), target140['customers_needed_rounded_up'], target210['customers_needed_rounded_up']])
    ranking_rows = [[row['priority'], row['category'], row['initial_target'], number(row['observed_locations']), f"{row['website_pct']}%", f"{row['phone_pct']}%", row['recommendation_and_limit']] for row in ranking]

    html = f'''{START}
  <section id="market-inventory-research" aria-labelledby="market-delivery-title" style="overflow-wrap:anywhere">
  <div class="sechead"><h2 id="market-delivery-title">Local market inventory → TAM → starting segment</h2><span class="note">8 Nov 2026 · available-source delivery complete</span></div>
  <p class="lede"><b>Verdict: start validation with Duval HVAC, plumbing and electrical owners.</b> The private inventory supplies 571 channel-available research candidates. Property management is the second test; selected professional services is third. These are research priorities, not hot leads or proven demand.</p>
  <div class="grid g3" id="market-headline-metrics">
    <div class="panel"><h3>119,174 source records</h3><p>98,742 Overture places plus 20,432 St. Johns tax records, including 223 October 2026 additions and 90 tax-account closure records.</p></div>
    <div class="panel"><h3>94,246 observed prospect locations</h3><p>Duval and St. Johns business/location rows after category cleanup. Not unique active companies or buyer organizations.</p></div>
    <div class="panel"><h3>1,072 cross-source locations</h3><p>Exact normalized name + physical street + ZIP reconciliation. A 30-row sample was reviewed; no parent or buyer merge is implied.</p></div>
  </div>
  <p class="warn" style="margin-top:14px"><b>Coverage boundary:</b> this is a comprehensive available-source inventory, not a verified census. The official Duval master-tax report remains blocked by Cloudflare security verification. Current operating verification and verified size indicators are 0. Independence, revenue-band fit, buying authority and willingness to pay remain unknown.</p>

  <div class="sechead"><h2>Geographic and official coverage</h2><span class="note">observed rows ≠ official counting units</span></div>
  <div class="grid g2">
    <div class="panel"><h3>Requested inventory scope</h3>{table(['Scope', 'Observed locations'], scope_rows, 420)}</div>
    <div class="panel"><h3>Official 2023 guardrails</h3>{table(['County', 'CBP employer establishments', 'NES nonemployer firms', 'CBP 5–49 subtotal'], coverage_rows, 600)}</div>
  </div>
  <p>CBP employer establishments are locations and exclude nonemployers; NES counts nonemployer firms. The sources are complementary guardrails, not a one-for-one denominator for the prospect inventory.</p>

  <div class="sechead"><h2>Basic enrichment and source coverage</h2><span class="note">public channels unvalidated · no outreach-ready rows</span></div>
  <div class="grid g3" id="market-enrichment-metrics">
    <div class="panel"><h3>59,622 websites</h3><p>Source-published website candidates with source URL and checked date.</p></div>
    <div class="panel"><h3>72,962 phones · 32,814 emails</h3><p>Public business channels; no deliverability or decision-owner claim.</p></div>
    <div class="panel"><h3>14,971 corporate · 7,017 DBA</h3><p>Accepted matches at prospect-location level. Corporate legal entities and fictitious names stay separate.</p></div>
  </div>
  <p>The legal pipeline scanned {number(legal_metrics['runs']['fictitious_name']['raw_rows'])} fictitious-name records and 12,988,522 corporate records. At source-record level it accepted {number(legal_metrics['accepted_corporate_matches'])} corporate and {number(legal_metrics['accepted_fictitious_name_matches'])} geographically supported DBA matches. No FEI, owner, officer, registered-agent or mailing-address fields were imported.</p>

  <details class="panel" id="market-category-breakdown" style="margin-top:14px"><summary><b>All 19 observed categories · locations and field coverage</b></summary>
    <p>Counts are observed locations, not unique companies. “Other / unknown commercial” is retained for review rather than silently discarded. Percentages show populated source fields, not independent verification.</p>
    {table(['Category', 'Locations', 'Website', 'Phone', 'Email', 'Corporate', 'DBA'], category_rows, 900)}
  </details>

  <section id="market-tam-scenarios" aria-labelledby="market-tam-title">
  <div class="sechead"><h2 id="market-tam-title">TAM scenarios and corrected unit economics</h2><span class="note">scenario arithmetic · not demand or break-even</span></div>
  <p><b>Formula:</b> official category baseline × full-year equivalent Jax Systems package spend. SUSB supplies company-oriented firm counts for trades, logistics and professional services; property management and marine use narrow/partial CBP establishment proxies. Mixed units are not summed into one company total.</p>
  {table(['Category', 'Baseline', 'Unit', 'Year', 'Low · $6,100', 'Base · $11,600', 'High · $17,100'], tam_rows, 980)}
  <p>These category-scope spending surfaces do not incorporate current operations, independence, size fit, need, native-software substitution or willingness to buy.</p>
  <h3>Explicit 5% annual-buyer sensitivity</h3>
  <p>The 5% share is an arbitrary sensitivity input, not a measured conversion rate. The underlying analysis also includes 1% and 10% cases.</p>
  {table(['Category', 'Scenario annual buyers', 'Scenario annual spend at $11,600'], sensitivity_rows, 650)}

  <h3>First-year revenue and capacity</h3>
  <p>The X-ray is fully <b>credited toward deployment</b>, so it is not added twice. Full-year package = deployment + 12 months of care. First-year revenue assumes evenly timed wins (6.5 average paid care months) and 50% / 75% / 100% care attach rates. Capacity assumptions are unproved.</p>
  {table(['Scenario', 'Full-year package', 'First-year revenue / customer', 'Care attach', 'Capacity', 'Revenue at capacity', 'Customers for $140k', 'Customers for $210k'], economic_rows, 1000)}
  <p class="warn"><b>Base case:</b> 19 customers for a $140k revenue target versus a hypothetical capacity of 10. This is not break-even: fixed costs, variable delivery costs, retention, throughput and profit are unmeasured.</p>
  </section>

  <section id="market-segment-ranking" aria-labelledby="market-ranking-title">
  <div class="sechead"><h2 id="market-ranking-title">Ranked starting segments</h2><span class="note">validation order · not lead scores</span></div>
  {table(['Priority', 'Segment', 'Initial target', 'Observed locations', 'Website', 'Phone', 'Recommendation and limit'], ranking_rows, 1100)}
  <p>Ability-to-pay judgments in the research are hypotheses. Public channel coverage indicates research reachability only. No named business is asserted to have the target problem.</p>
  </section>

  <section id="market-current-positioning" aria-labelledby="market-positioning-title">
  <div class="sechead"><h2 id="market-positioning-title">Current website positioning draft</h2><span class="note">owner validation before hardening</span></div>
  <div class="panel" style="background:#e8ecd9"><span class="mono">For Jacksonville HVAC, plumbing &amp; electrical owners</span><h3 style="font-size:1.6rem;margin-top:8px">Keep quotes moving when the day gets busy.</h3><p>Find where inquiries, estimates and follow-ups stall. Fix the handoff with existing tools when possible. Give the result a baseline, acceptance test, named owner, fallback and exception route.</p><p><b>Lead service:</b> Ops X-ray → one fixed-scope quote/follow-up improvement → optional care for the running system.</p><p><b>Primary action:</b> Book a 30-minute owner qualification call.</p></div>
  <div class="grid g2" style="margin-top:14px">
    <div class="panel"><h3>Message order</h3><ul class="tight"><li>Keep quotes moving—not “AI transformation.”</li><li>Check configuration, plan changes, templates and staff process before custom work.</li><li>Protect expert judgment; do not make AI reception the default.</li><li>Measure response time, follow-up coverage, admin time and exceptions. Track accepted quotes separately.</li></ul></div>
    <div class="panel"><h3>Claims held back</h3><ul class="tight"><li>No guaranteed revenue, conversion lift or hours saved.</li><li>No “proven playbook,” “local moat” or invented client proof.</li><li>No named business is claimed to have the problem.</li><li>Owner conversations and paid commitments come before outcome copy.</li></ul></div>
  </div>
  </section>

  <div class="sechead"><h2>Method, sources and publication boundary</h2><span class="note">aggregate public synthesis only</span></div>
  <p>Public sources: <a href="https://docs.overturemaps.org/guides/places/" target="_blank" rel="noopener noreferrer">Overture Places</a>; <a href="https://sjctax.us/download-data-files/" target="_blank" rel="noopener noreferrer">St. Johns business-tax files</a>; <a href="https://dos.fl.gov/sunbiz/other-services/data-downloads/quarterly-data/" target="_blank" rel="noopener noreferrer">Florida Sunbiz quarterly data</a>; <a href="https://www.census.gov/programs-surveys/cbp/data.html" target="_blank" rel="noopener noreferrer">Census CBP</a>; <a href="https://www.census.gov/data/datasets/2023/econ/nonemployer-statistics/2023-ns.html" target="_blank" rel="noopener noreferrer">Census NES</a>; and <a href="https://www.census.gov/data/tables/2022/econ/susb/2022-susb-annual.html" target="_blank" rel="noopener noreferrer">Census SUSB</a>.</p>
  <p><b>Verification:</b> 46 automated tests passed; SQLite integrity and foreign keys passed; snapshot restoration and hashes were verified; both 30-row identity and legal-match audit samples were reviewed. Paid-data spend was $0. No outreach was sent.</p>
  <p class="warn">Company-level inventory, contact channels, raw registry records and evidence extracts remain in the private research repository and Obsidian. They are deliberately not embedded in this public artifact. The complete aggregate analysis is represented here; the next gate is owner/customer validation.</p>
  </section>
{END}'''
    return html


def main() -> None:
    html = INDEX.read_text(encoding='utf-8')
    generated = build()
    if START in html and END in html:
        start = html.index(START)
        end = html.index(END, start) + len(END)
        updated = html[:start] + generated + html[end:]
    else:
        anchor = '  <section id="gtm-research-sprint"'
        if anchor not in html:
            raise RuntimeError('Research insertion anchor missing')
        updated = html.replace(anchor, generated + '\n\n' + anchor, 1)
    updated = updated.replace('Research · 7 November 2026', 'Research · 8 November 2026', 1)
    updated = updated.replace('portfolio preserved · no vertical chosen', 'initial segment selected for validation · not demand proof', 1)
    INDEX.write_text(updated, encoding='utf-8')
    print(f'Wrote aggregate market research to {INDEX}')


if __name__ == '__main__':
    main()
