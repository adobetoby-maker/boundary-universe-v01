# MULTI-REVIEW ORCHESTRATION — AUTONOMOUS PRODUCTION LOOP

**Status:** PROVISIONAL GOVERNANCE — intended to become LOCKED after first full book pilot
**Branch:** `planning/universe-kanban`
**Purpose:** turn the productive Claude + ChatGPT + Grok review pattern into a repeatable, provenance-aware ticket loop that can advance work from chapter → book → trilogy → origin cycle → ensemble saga without losing quality or canon state.

---

# 1. CORE PRINCIPLE

No single model is both sole author and sole judge of a major production layer.

The preferred pattern is:

`PRIMARY WORK → INDEPENDENT REVIEW A → INDEPENDENT REVIEW B → RECONCILIATION → REVISION → ATTESTATION → NEXT TICKET`

For high-risk layers, use three independent reviews before reconciliation.

The system is **model-agnostic but provenance-aware**. Claude, ChatGPT, Grok, or future reviewers may fill any review role. Canon belongs to the repository, not to a model.

A reviewer must always evaluate a named artifact at a named commit/SHA/version. Never review an undefined "latest" draft when parallel work may exist.

---

# 2. REVIEW ROLES

Use roles rather than assuming each provider always does the same job.

## AUTHOR / IMPLEMENTER
Creates or revises the artifact against the ticket acceptance criteria.

## STRUCTURE REVIEWER
Checks scene logic, pacing, escalation, promise/payoff, missing causal steps, and whether the artifact fulfills its architecture.

## CHARACTER REVIEWER
Checks motivation, emotional truth, supporting-character agency, relationship pacing, protagonist dominance, and whether choices feel earned.

## CANON / MYSTERY REVIEWER
Checks continuity, chronology, power accounting, Rule 6 clue fairness, reveal ownership, spoiler boundaries, and cross-series compatibility.

## AUDIO / LINE REVIEWER
Checks read-aloud clarity, speaker attribution, action geography, repetition, sentence rhythm, naming, and family-clean standard.

## ADVERSARIAL REVIEWER
Attempts to break the work: identifies contradictions, cheap progression, accidental exposition, unresolved promises, convenience, derivative structure, reader-confusion risks, or hidden assumptions.

## RECONCILER
Compares all reviews against canon and ticket criteria. Does not majority-vote blindly. Produces a disposition for every material finding: `ACCEPT`, `REJECT`, `DEFER`, or `NEEDS CREATOR DECISION`.

## ATTESTER
Confirms acceptance criteria are actually met after revision and records the exact source commit(s).

A single model may fill more than one role on low-risk tickets, but major chapter/book/trilogy gates should include independent model families where practical.

---

# 3. TICKET STATE MACHINE

Every production ticket moves through these states:

`READY → CLAIMED → IMPLEMENTING → REVIEW_READY → REVIEWING → RECONCILE → REVISING → VERIFY → ATTESTED → CLOSED`

Exception states:

`BLOCKED_CANON`
`BLOCKED_DEPENDENCY`
`NEEDS_CREATOR_DECISION`
`REOPENED`

### READY
All upstream dependencies are satisfied and acceptance criteria are explicit.

### CLAIMED
One author/implementer is assigned. The ticket records branch/path and source inputs.

### IMPLEMENTING
Artifact is created or revised.

### REVIEW_READY
Artifact has a stable review commit/SHA. Review packets may now be dispatched independently.

### REVIEWING
Required reviewers inspect the same frozen artifact independently. Reviewers should not see each other's conclusions until their own review is recorded when practical.

### RECONCILE
Reconciler compares findings, canon, architecture, and acceptance criteria. Material disagreements are resolved explicitly.

### REVISING
Accepted findings are implemented. No new untracked scope is added casually.

### VERIFY
Attester checks revised artifact and confirms accepted findings are closed.

### ATTESTED
Artifact passes the layer gate. Ledgers and downstream dependencies are updated.

### CLOSED
Next tickets are promoted to READY.

---

# 4. REVIEW PACKET CONTRACT

Every review request should include:

- ticket ID;
- artifact path(s);
- exact commit/SHA/version;
- governing canon/bible/architecture paths;
- intended reader promise;
- explicit acceptance criteria;
- known open questions;
- spoiler boundary;
- review role requested;
- instruction to distinguish `BLOCKER`, `MAJOR`, `MINOR`, `OPTIONAL` findings;
- instruction not to rewrite canon silently.

Every review response should record:

- reviewer/model/provider;
- artifact SHA reviewed;
- role;
- findings by severity;
- evidence/location;
- recommended action;
- confidence;
- any detected canon conflict;
- whether the artifact should advance.

---

# 5. DISAGREEMENT PROTOCOL

Different reviewers disagreeing is useful, not failure.

For every disputed material finding, the reconciler asks in this order:

1. Does LOCKED canon decide it?
2. Does the current architecture / reader contract decide it?
3. Is one review based on a factual misread of the artifact?
4. Can both concerns be satisfied without damaging the chapter/book promise?
5. Is the disagreement aesthetic rather than structural?
6. Would either choice create downstream continuity or spoiler debt?

Disposition:

- `ACCEPT` — implement.
- `REJECT` — record why.
- `DEFER` — valid issue belongs to later layer; create explicit ticket.
- `NEEDS_CREATOR_DECISION` — only when two or more viable choices materially change creative direction/canon and repository rules do not resolve it.

Never resolve disagreement by simple 2-of-3 voting when canon or story function points the other way.

---

# 6. AUTONOMOUS CHAPTER LOOP

For each planned chapter:

1. Create/claim chapter ticket from architecture.
2. Pass 1 structure draft.
3. Independent structure review.
4. Reconcile + revise.
5. Pass 2 density expansion.
6. Independent character/density review.
7. Reconcile + revise.
8. Pass 3 character/clue/continuity pass.
9. Independent canon/mystery review.
10. Reconcile + revise.
11. Pass 4 audio-first polish.
12. Independent audio/line review.
13. Reconcile + final revision.
14. Chapter attestation.
15. Update state/clue/progression ledgers.
16. Promote next chapter ticket to READY.

For high-risk reveal/climax chapters add an **adversarial third review** before attestation.

The loop continues without creator intervention unless an exception state is triggered.

---

# 7. AUTONOMOUS BOOK LOOP

When all chapter tickets are ATTESTED:

1. Exact word-count audit.
2. Chapter-density distribution audit.
3. Whole-book structural review by independent reviewer.
4. Whole-book character/relationship review by a different reviewer.
5. Rule 6 / canon / continuity review by a different reviewer.
6. Reconciliation ticket consolidates findings.
7. Targeted repair tickets created and completed through the same review loop.
8. Family-clean audit.
9. Audio-first / listening audit.
10. Listening-driven fixes only.
11. Copyedit.
12. Production-lock attestation.
13. Audio production/QC tickets.
14. Post-book canon reconciliation.
15. Promote next-book architecture/drafting ticket.

### Book autonomy gate
A book may be declared complete only when:
- all planned chapters are attested;
- all BLOCKER/MAJOR review findings are closed or explicitly deferred with valid downstream owner;
- reader promise is fulfilled;
- exact end state matches the trilogy contract or an approved change-control ticket;
- canon/state/clue ledgers reconcile;
- production source commit is recorded.

---

# 8. AUTONOMOUS TRILOGY LOOP

After each book locks:

1. Reconcile published end state into trilogy state ledger.
2. Run standalone-satisfaction audit.
3. Check trilogy mystery ladder and reveal ownership.
4. Re-evaluate later-book architecture against newly earned prose discoveries.
5. Create change tickets only where evidence requires them; do not casually rewrite locked books.
6. Draft next book through book loop.

After Book 3:

1. Full trilogy emotional-arc review.
2. Full trilogy external-arc review.
3. Rule 6 clue/payoff review across all three books.
4. Reader-contract 3-book satisfaction audit.
5. Crossover-seam audit: remove cross-series knowledge mentally and verify trilogy still works.
6. End-state contract attestation.
7. Update master timeline/spoiler matrix.
8. Unlock relevant prequel and ensemble dependency tickets.

---

# 9. ORIGIN-CYCLE / UNIVERSE LOOP

After each origin trilogy locks:

- update five-lead role matrix;
- update counterpart matrix;
- update ability translation matrix;
- update convergence contribution;
- update release-order options;
- update spoiler ownership;
- run partial-reader stop-point tests.

After all five origin trilogies:

- run 15-book macro-satisfaction audit;
- verify each lead independently reached one face of the shared problem;
- verify no origin requires ensemble books to resolve its promised arc;
- run Ensemble Book 1 cold-entry architecture audit;
- only then promote ensemble prose tickets.

Ensemble books then run the same chapter/book review loops.

---

# 10. ASSIGNMENT / HANDOFF RULES

Ticket assignment should follow **capability + independence**, not brand loyalty.

Recommended default for major book work:

- Primary author: whichever model/session currently owns prose continuity.
- Reviewer 1: different model/provider, structure/character focus.
- Reviewer 2: different model/provider or fresh-context reviewer, canon/clue focus.
- Reviewer 3 when high risk: adversarial review from a third independent perspective.
- Reconciler: model/session with strongest access to current repo canon and full review packet.
- Attester: preferably not the same context that performed the final revision.

Claude + ChatGPT + Grok is a proven useful three-perspective pattern for this project, but the workflow must survive substitution if a provider is unavailable.

### Handoff rule
Before handing work to another reviewer/agent, commit the current artifact and provide the exact SHA. After return, preserve the review as a ticket comment/file/result with reviewer identity and reviewed SHA.

---

# 11. AUTONOMY BOUNDARIES

The loop SHOULD proceed without asking the creator when:

- acceptance criteria already decide the issue;
- a continuity error has one clear repair;
- a chapter is under-dramatized relative to its own brief;
- a clue is missing and the reveal ledger specifies what must be seeded;
- line/audio clarity can be improved without changing intent;
- reviewers agree on a material weakness and repair does not alter locked canon.

The loop MUST stop with `NEEDS_CREATOR_DECISION` when:

- a change would alter LOCKED canon materially;
- two strong creative directions both satisfy the architecture but imply different future arcs;
- protagonist/ability/romance/death/release-order choices are still deliberately OPEN and the decision is consequential;
- a requested change would break the reader contract;
- rights/originality/safety concerns cannot be resolved mechanically.

Do not ask the creator to adjudicate ordinary editorial choices that the rules already settle.

---

# 12. FAILURE / RECOVERY RULES

If a reviewer is unavailable:
- substitute another independent reviewer role; record substitution.

If reviewers conflict badly:
- spawn a focused arbitration review using only disputed points plus canon evidence.

If branch moved:
- refetch SHA before write; never overwrite newer work.

If a later review uncovers an earlier-layer defect:
- reopen the smallest responsible ticket/layer;
- repair forward;
- rerun affected gates only;
- record audio/production invalidation where relevant.

If a book is already production locked:
- use change-control ticket; never silently edit.

---

# 13. TICKET TEMPLATE — MULTI-REVIEW WORK ITEM

**ID / Title:**
**Layer:** chapter / book / trilogy / universe
**Status:** READY
**Owner/Implementer:**
**Branch:**
**Artifact path(s):**
**Input SHA(s):**
**Governing docs:**
**Promise:**
**Acceptance criteria:**

### Required reviews
- [ ] Structure — reviewer / provider / reviewed SHA
- [ ] Character — reviewer / provider / reviewed SHA
- [ ] Canon/Clue — reviewer / provider / reviewed SHA
- [ ] Audio/Line — reviewer / provider / reviewed SHA
- [ ] Adversarial — when required

### Reconciliation
For each material finding:
- finding ID;
- severity;
- disposition;
- rationale;
- repair ticket/commit.

### Verification
- [ ] All BLOCKER findings closed.
- [ ] All MAJOR findings closed or validly deferred.
- [ ] Ledgers updated.
- [ ] Exact final SHA recorded.
- [ ] Next dependency promoted.

**Attestation:** PASS / REOPEN / NEEDS CREATOR DECISION

---

# 14. DEFINITION OF LOOP SUCCESS

The orchestration system succeeds when a ticket can be picked up by a fresh agent/model with no hidden conversational memory, use the repository and ticket packet as source of truth, complete its assigned layer, obtain independent reviews, reconcile, attest, and unlock the next unit of work without introducing canon drift.

The long-term objective is not unattended generation for its own sake. It is **autonomous quality-controlled progression** with clear provenance, independent criticism, finite gates, and creator escalation only for genuinely creative decisions.