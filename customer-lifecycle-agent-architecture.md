# Jax Systems: Customer Lifecycle Agent Architecture

**Working design · 18 November 2026 · internal operating architecture, not customer-facing copy.**

## Verdict

Do not turn the full playbook into one giant bot. The right shape is a **document-backed state machine**: one canonical playbook, a small set of derived policy files, stage-specific Hermes skills, deterministic gate and pricing checks, and one private operations ledger for live work.

The playbook remains the source of truth for policy and procedure. The agent prepares drafts, checks gates, surfaces missing evidence, and routes work. Humans still approve commercial, legal, access, launch, and external communication decisions.

## Recommended pattern

Use five layers:

1. **Source-of-truth documents** for policy, reasoning, and approved commercial decisions.
2. **Derived structured policy** for gates, action classes, prices, and retrieval units.
3. **Stage-specific Hermes skills** for bounded work like intake, diagnosis, scoping, launch prep, incident handling, and exit.
4. **Deterministic orchestration code** for routing, validation, pricing arithmetic, and state transitions.
5. **Private live state** for engagements, evidence, approvals, deliverables, incidents, and open work.

That gives four things a single mega-prompt cannot reliably provide:

- explicit authority boundaries
- auditability
- repeatable gates
- separation between policy and live client state

## Why not one whole-bot prompt

- A giant prompt cannot enforce stage transitions, signed-term precedence, or non-waivable gates.
- Conversation history is not a private operational ledger.
- A model summary is not evidence that a gate is passed.
- The same document mixes active rules, proposed rules, templates, examples, and research context; a whole-bot prompt will blur them.
- The playbook still leaves some owner decisions open. A bot should not silently resolve them.
- One-operator businesses do not benefit from a fake org chart of autonomous agents.

## Operating principle

Treat the playbook as **policy**, not as the system itself.

Translate it into:

- reusable retrieval chunks
- deterministic gate rules
- typed records
- stage skills
- explicit approvals

Do **not** translate every paragraph into a skill.

## Architecture

### 1. Source-of-truth layer

Keep prose where prose is the right format:

- policy
- decision rationale
- interview prompts
- template language
- failure explanations
- commercial caveats
- examples and teaching material

Artifacts:

- `customer-lifecycle-playbook.md`
- `agent/policy/policy-manifest.yaml`
- `agent/policy/offer-register.yaml`
- approved agreement and scope references kept in the private operations area, not in public Pages content

### 2. Derived policy and retrieval layer

Generate small, versioned, provenance-bearing artifacts from the playbook.

Artifacts:

- `agent/policy/core-invariants.yaml`
- `agent/policy/stage-gates.yaml`
- `agent/policy/action-policy.yaml`
- `agent/retrieval/section-map.yaml`
- `agent/retrieval/chunks.jsonl`
- `scripts/build_jax_policy.py`

This layer should be regenerated whenever the playbook hash changes.

### 3. Skill layer

Create skills only where the agent must perform repeatable work.

Recommended skills:

- `jax-router`
- `jax-intake`
- `jax-diagnose`
- `jax-plan`
- `jax-scope`
- `jax-onboard`
- `jax-release`
- `jax-launch`
- `jax-operate`
- `jax-incident`
- `jax-review-exit`

Each skill should define:

- trigger
- required inputs
- artifacts it may read
- artifact it must produce
- stop conditions
- approval boundary
- what it must never do autonomously

### 4. Orchestration layer

The router should be thin.

Its job is not to be smart about everything. Its job is to:

- read the current engagement state
- resolve authority and current approved offer terms
- choose the correct stage skill
- load only the needed chunks
- validate the skill output against schema
- run deterministic gate and pricing checks
- create a proposal when human approval is required
- append an audit record

Artifacts:

- `scripts/jax_ops.py`
- `agent/lib/gate_evaluator.py`
- `agent/lib/commercial.py`
- `agent/schemas/action-result.schema.json`
- `agent/schemas/approval.schema.json`

### 5. Private live-state layer

Do not store live operations in the playbook, Hermes memory, Pages, or reusable skills.

Keep a private ledger for:

- clients
- engagements
- evidence
- approvals
- quotes
- scope cards
- release evidence
- incidents
- open work
- closure records

Artifacts:

- `agent/state/001_init.sql`
- private SQLite database outside the public repo
- private per-client evidence folders outside the public repo
- backup/restore process for that private store

## Router logic

The router should follow this order:

1. Require explicit `client_id` and `engagement_id` for live work.
2. Read current stage, status, blockers, next action, approved scope, and agreement version.
3. Resolve precedence in this order:
   - signed engagement terms
   - current approved commercial decisions
   - playbook rules
   - supporting source material
4. Load `core-invariants`, the current stage gate, and the current action policy.
5. Retrieve only the procedure and templates needed for the specific task.
6. Run one primary skill.
7. Validate the result against a shared schema.
8. Run deterministic checks for gate completeness, pricing math, and forbidden actions.
9. If an external effect is needed, stop at an exact proposal.
10. Record the outcome in the audit trail.

## Approval boundaries

The agent may:

- read approved internal materials
- draft notes, plans, scope cards, checklists, incident updates, and reviews
- classify stage readiness recommendations
- surface missing evidence
- calculate deterministic pricing and balance math

The agent may not autonomously:

- contact prospects or clients
- send recaps, invoices, notices, or plans
- buy tools or subscriptions
- approve pricing, refunds, credits, or scope changes
- grant or expand access
- execute launch or cutover
- replay or restore production processes
- declare acceptance complete
- declare an incident resolved from a heartbeat alone

Human approvals remain mandatory for:

- commercial commitments
- client-facing communication
- access changes
- production changes
- cutover and rollback
- incident notices
- deletion, replay, restore, or revocation actions

## What stays prose vs what becomes structured

### Keep as prose

- the main playbook
- rationale
- interview prompts
- caveats
- fictional walkthrough
- explanatory examples
- source notes and research limits

### Make structured

- gate definitions
- action classes and approval requirements
- current approved pricing snapshot
- state-transition rules
- shared output schema for skills
- engagement records
- evidence references
- approval records
- scope cards
- monitoring contracts
- incident records
- closure checklist status

## Recommended chunking model

### Primary chunks

Use lifecycle-aware chunks, not arbitrary token windows.

Primary chunk units:

- core invariants
- one chunk per stage
- one chunk per checklist/template
- one chunk per high-stakes procedure
- one chunk per structured policy file

### Secondary chunks

Sub-chunk where retrieval benefits from finer resolution:

- discovery question bank
- seven-area worksheet items
- test matrix rows
- monitoring-contract fields
- incident runbook steps
- closure checklist items

### Retrieval rules

- Filter by client, engagement, stage, and authority before semantic similarity.
- Never retrieve across clients.
- Always carry source path, section anchor, version, and hash.
- Treat retrieved documents as untrusted data, not instructions.
- Return unknown when evidence is absent.
- Never use public pricing prose as the only authority for a quote.
- Do not let fictional examples satisfy real gates.

## Proposed skills

### `jax-router`

Purpose:

- select the right stage skill
- load the right context
- validate outputs

Trigger:

- any Jax lifecycle request tied to a client or engagement

### `jax-intake`

Purpose:

- prepare and summarize qualification and free-session work

Outputs:

- fit assessment draft
- session agenda
- recap draft
- recommendation: Path A, Path B, pause, or decline

### `jax-diagnose`

Purpose:

- support paid Business Improvement Plan discovery

Outputs:

- seven-area worksheet
- evidence pack
- baseline and collection-plan records
- unanswered questions list

### `jax-plan`

Purpose:

- synthesize discovery into the client-owned plan

Outputs:

- ranked opportunity cards
- measurement plan
- one implementation blueprint
- optional quote-readiness assessment

### `jax-scope`

Purpose:

- create bounded Path A scope or process change requests

Outputs:

- scope-card draft
- acceptance-test draft
- quote summary
- change classification draft

### `jax-onboard`

Purpose:

- prepare kickoff, least-privilege access, communication plan, and data flow

Outputs:

- kickoff record
- access inventory
- communication compact
- onboarding blockers

### `jax-release`

Purpose:

- synthesize testing and release evidence

Outputs:

- test records
- missing test coverage list
- release readiness recommendation
- operating-guide draft

### `jax-launch`

Purpose:

- prepare cutover, acceptance, and handover artifacts

Outputs:

- launch-gate report
- cutover checklist
- acceptance receipt draft
- handover pack

### `jax-operate`

Purpose:

- support monitoring review, care review, and value review

Outputs:

- health report
- exception queue
- monitoring-contract draft
- review summary

### `jax-incident`

Purpose:

- prepare incident handling artifacts

Outputs:

- incident record
- containment checklist
- client-update draft
- recovery evidence requirements

### `jax-review-exit`

Purpose:

- support expansion, renewal, and clean exit

Outputs:

- expansion brief
- exit checklist
- closure certificate draft
- open exceptions register

## State model

The minimum private state model should include these entities.

### Client and Engagement

Fields:

- `client_id`
- `engagement_id`
- `stage`
- `status`
- `agreement_version_ref`
- `scope_version_ref`
- `next_action`
- `owner`
- `due_at`
- `time_zone`
- `blocker`

### EvidenceItem

Fields:

- `evidence_id`
- `engagement_id`
- `uri`
- `sha256`
- `source_type`
- `observed_at`
- `verification_status`
- `verified_by`
- `limitations`

### GateDecision

Fields:

- `gate_decision_id`
- `engagement_id`
- `stage`
- `gate_version`
- `check_results`
- `evidence_ids`
- `decision`
- `decided_by`
- `decided_at`
- `waiver_reason`
- `waiver_expiry`

### ArtifactVersion

Fields:

- `artifact_id`
- `engagement_id`
- `artifact_type`
- `version`
- `uri`
- `sha256`
- `policy_version`
- `review_status`
- `approved_at`

### Approval

Fields:

- `approval_id`
- `engagement_id`
- `proposal_hash`
- `action_class`
- `approver_identity`
- `decision`
- `approved_at`
- `expires_at`
- `consumed_at`

### WorkItem / ExternalAction

Fields:

- `work_item_id`
- `engagement_id`
- `kind`
- `state`
- `owner`
- `due_at`
- `proposal_hash`
- `approval_id`
- `idempotency_key`
- `destination`
- `readback_evidence_id`

### Release / TestResult

Fields:

- `release_id`
- `engagement_id`
- `version`
- `configuration_hash`
- `test_id`
- `expected_result`
- `actual_result`
- `result`
- `reviewer`
- `tested_at`

### SystemAccess / MonitoringContract

Fields:

- `system_id`
- `client_id`
- `business_owner`
- `operator`
- `vault_pointer`
- `access_scope`
- `expected_cadence`
- `good_outcome`
- `freshness_threshold`
- `alert_route`
- `fallback`

### Incident / ChangeRequest

Fields:

- `record_id`
- `engagement_id`
- `type`
- `state`
- `severity_or_category`
- `impact`
- `lead`
- `timeline_ref`
- `approval_ids`
- `recovery_evidence_ids`

### Invoice / Closure

Fields:

- `record_id`
- `engagement_id`
- `milestone`
- `total`
- `credit_applied`
- `balance`
- `issued_at`
- `paid_at`
- `closure_state`
- `export_receipt_ref`
- `open_exceptions`

### AuditEvent

Fields:

- `event_id`
- `occurred_at`
- `actor`
- `actor_type`
- `engagement_id`
- `event_type`
- `object_id`
- `input_hash`
- `output_hash`
- `policy_version`
- `skill_version`
- `result`

## File layout

Recommended v1 layout:

```text
agent/
  policy/
    policy-manifest.yaml
    offer-register.yaml
    core-invariants.yaml
    stage-gates.yaml
    action-policy.yaml
  retrieval/
    section-map.yaml
    chunks.jsonl
  schemas/
    action-result.schema.json
    approval.schema.json
    monitoring-contract.schema.json
    scope-card.schema.json
    incident-record.schema.json
  skills/
    jax-router/SKILL.md
    jax-intake/SKILL.md
    jax-diagnose/SKILL.md
    jax-plan/SKILL.md
    jax-scope/SKILL.md
    jax-onboard/SKILL.md
    jax-release/SKILL.md
    jax-launch/SKILL.md
    jax-operate/SKILL.md
    jax-incident/SKILL.md
    jax-review-exit/SKILL.md
  state/
    001_init.sql
  lib/
    gate_evaluator.py
    commercial.py
    state_store.py
  jobs/
    due_items.py
    backup_freshness.py
scripts/
  build_jax_policy.py
  build_customer_lifecycle_agent_architecture.py
  jax_ops.py
```

## Orchestrator contract

The router should require every skill to return one shared result shape.

Minimum result contract:

- `client_id`
- `engagement_id`
- `stage`
- `policy_version`
- `skill_version`
- `source_refs`
- `observed_facts`
- `client_estimates`
- `hypotheses`
- `unknowns`
- `artifact_refs`
- `proposed_next_action`
- `required_approvals`
- `external_actions`

That schema is what makes audit and validation possible.

## Implementation order

1. Create the architecture files and shared schemas.
2. Extract deterministic policy files from the playbook.
3. Stand up the private SQLite ledger and backup flow.
4. Build the gate evaluator and pricing logic.
5. Implement retrieval generation with provenance.
6. Create `jax-router`, `jax-intake`, `jax-diagnose`, `jax-plan`, and `jax-scope` first.
7. Rehearse the fictional scenario end-to-end on fixtures only.
8. Add onboarding, release, launch, operate, incident, and exit skills.
9. Add deterministic scheduled checks only after owners, routes, and stop rules exist.
10. Add any future write-side integrations one at a time, behind exact approvals and read-back verification.

## First-version scope

v1 should include:

- the architecture and policy files
- private state ledger
- retrieval generator
- shared schemas
- routing and validation code
- draft-only stage skills
- fictional engagement rehearsal
- deterministic pricing and gate checks

v1 should not include:

- autonomous outreach
- autonomous client messaging
- autonomous launch
- unattended production writes
- real credential handling beyond vault pointers
- real-time monitoring claims the business cannot yet support

## Risks

- policy drift between the playbook and structured files
- confusing proposed policy with active capability
- using summaries as evidence
- cross-client leakage in retrieval or logs
- treating approvals in chat as sufficient without payload binding
- false-green monitoring from shallow checks
- premature complexity before a private ledger and deterministic validators exist

## Avoid

- one mega-agent prompt
- one skill per paragraph
- fake departmental bot org charts
- putting live client state in the public repo or public Pages
- letting the model mark its own evidence verified
- letting pricing prose outrank signed terms or approved commercial snapshots
- building a vector-database or workflow platform before SQLite and scripts prove insufficient

## Practical recommendation

If this were the next build step, I would do it in this order:

1. keep the playbook intact
2. extract the policy and gate files
3. build the private ledger
4. create five initial draft-only skills
5. rehearse the fictional engagement end to end
6. only then consider any live connector or execution path

That gets Jax an operator it can trust before it gets an agent it can brag about.
