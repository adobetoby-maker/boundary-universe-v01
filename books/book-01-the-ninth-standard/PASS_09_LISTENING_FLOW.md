# PASS 09 — LISTENING FLOW / TECHNICAL TRANSLATION

**Branch:** `revision/listening-flow-book1`
**Source baseline:** `revision/pass8-reader-review-book1`
**Primary complaint addressed:** the manuscript is compelling but can become difficult to follow aloud, especially when technical vocabulary, unusual sentence order, rapid fragment sequences, and compressed mathematical reasoning arrive before the listener has a concrete picture.

## Benchmark comparison: Contact Zero

`Contact Zero` is not uniformly simpler. It contains many longer technical sentences and nested clauses. Its strongest listening technique is more specific:

1. it establishes a physical relationship the listener can picture;
2. it states the technical distinction afterward;
3. it lets character humor release pressure;
4. it returns quickly to a human decision.

Representative method: the difference between a general signal and an address is explained as the difference between a sound in a room and someone saying your name. The listener understands the relationship before receiving the technical label.

`The Ninth Standard` sometimes reverses that order. It presents a transfer manifold, tensor convention, coupled correction loop, load path, source/path/sink model, or boundary architecture first, then supplies the ordinary-life analogy later. A print reader can reread. An audiobook listener must hold several undefined objects in working memory while narration continues.

## Measured cross-manuscript finding

A repository-wide diagnostic audited all 33 `Ninth Standard` chapters against all 24 `Contact Zero` chapters. The audit is intentionally a triage tool rather than a quality grade.

The result clarified the user's listening reaction:

- `Contact Zero` has the **longer sentence problem**: its average chapter-level 95th-percentile sentence was roughly 39 words, and the audit found hundreds of sentences above 45 words.
- `The Ninth Standard` has the **staccato problem**: its 95th-percentile sentences averaged roughly 15 words, but the audit flagged an extremely high number of repeated one-to-four-word fragment bursts.
- Therefore the principal Book 1 fatigue is not simply “sentences are too long.” It is rapid alternation among short fragments, banter, displayed text, technical terms, names, numbers, and scene-state changes. The listener repeatedly has to restart the mental sentence.
- The correct repair is a mixed cadence: retain short lines for impact and humor, but regroup explanatory and transitional fragments into natural short–medium–long spoken patterns.

The diagnostic is implemented in `scripts/listening_flow_audit.py` and runs through `.github/workflows/listening-flow-audit.yml`. It compares both manuscripts and produces a Markdown/JSON artifact without automatically rewriting prose.

## Locked listening-flow rules

### 1. Concrete first; term second
Before introducing a technical term, give the listener an object, action, or familiar problem.

Preferred ladder:

1. **Object:** a table, door, shopping cart, crowded hallway, stretcher, bridge, backpack, cup, or line of people.
2. **Action:** what is being moved, held, shared, delayed, or redirected.
3. **Failure:** what goes wrong and who notices.
4. **Technical label:** the mathematical or Boundary term that names the relationship.

The analogy is a bridge into the real model, not a replacement for it.

### 2. One new relationship per spoken beat
Do not ask the listener to learn source, path, sink, feedback, correction, delay, and shared state in one paragraph. Establish one relationship, test it, then add the next.

### 3. Translate noun stacks into actions
Prefer subjects and verbs over stacked abstractions.

Instead of:

> recursive multi-operator transfer-state stabilization

Use:

> three operators kept predicting one another. Each prediction changed what the next operator had to correct.

Then name the formal model.

### 4. Sentence order should follow thought order
Default spoken order:

**who/what → does what → to whom/what → why it matters.**

Inversion is reserved for emphasis, not routine exposition. Long qualifying clauses should follow the core sentence instead of delaying it.

### 5. Reserve fragments for jobs fragments do well
Short lines remain part of Kade's voice. They should mark:

- impact;
- discovery;
- emotional refusal;
- punch line;
- a decisive correction;
- a true change in attention.

Do not use four or more fragments in sequence merely to list ordinary information, bridge time, or explain a technical process. In those cases, combine the pieces into a sentence the narrator can carry on one breath.

### 6. Technical passage breath gate
During a dense explanation:

- no more than two unfamiliar technical terms before a plain-language restatement;
- no more than one long multi-clause sentence in sequence;
- after roughly 150–220 spoken words, return to character, consequence, humor, or a visible object;
- displayed equations must be narrated by function, not merely read as symbols.

### 7. Use the school cast as translators
Asterion is a school. The teaching should sound like teaching.

- **Amadi:** dry, exact, and funny enough to make the idea memorable. She translates without becoming sentimental or performing for applause.
- **Kade:** gives fast, concrete, occasionally disrespectful analogies.
- **Mara:** identifies where the analogy stops being exact.
- **Eli:** turns the concept into a physical simulator or machine failure.
- **Sera:** asks who gets hurt or what success actually means.
- **Julian:** separates capability from authority.

No single character becomes the permanent exposition machine.

### 8. Humor releases pressure; it does not interrupt emotion
Use a short joke after comprehension, not before it. A joke should confirm the listener understood the object or reveal character attitude. Do not place a punch line between an emotional question and its answer.

### 9. Stable vocabulary for audio memory
Once a concept has a usable spoken name, repeat that name. Do not cycle through three elegant synonyms in adjacent paragraphs. Repetition can aid one-hearing comprehension when it is structural rather than tic-driven.

### 10. Math must change a decision
A mathematical explanation stays only if it changes what somebody does, risks, notices, or believes. If the same plot and character result survives without the explanation, compress it.

### 11. No intelligence downgrade
The goal is not to remove the physics or make the characters less capable. The goal is to let the listener build the model in the same order the characters do.

## Whole-book pass order

### Tier A — technical and action load-bearing chapters
- Ch6 `Forty-Seven Seconds`
- Ch8 `The Ladder`
- Ch10 `Vector Class`
- Ch11 `The Broken Floor`
- Ch12 `Boundary Conditions`
- Ch13 `Cross Examination`
- Ch14–15 House Trial sequence
- Ch22 `Mercer v. Vey`
- Ch24 `The Quiet War`
- Ch30 `Siege of Asterion`
- Ch32 `Consensus`

### Tier B — global syntax/cadence sweep
Across all 33 chapters:

- delayed subject/verb caused by introductory clauses;
- sentences carrying three or more abstract nouns;
- fragment runs that become staccato rather than intentional;
- repeated negative-definition ladders (`not X / not Y / but Z`) when one positive sentence is clearer;
- ambiguous pronouns or dialogue ownership in audio;
- numerical or displayed-text sequences that need spoken framing;
- paragraphs that require rereading to identify the physical action.

### Tier C — listening verification
Render or read every revised chapter aloud. Edit only demonstrated listening problems after this stage.

## Acceptance test for every technical explanation

A thirteen-year-old listener should be able to answer, after one hearing:

1. What physical thing is happening?
2. What changed?
3. Why is the ordinary explanation insufficient?
4. What does the new technical term add?
5. What decision or danger follows?

The listener does not need to reproduce the equation. The listener does need to understand the causal model.

## Completed first batch

### Chapter 10 — Vector Class
**Major rewrite complete.**

- Amadi now begins with three people trying to move a couch through a narrow stairwell before naming a transfer manifold.
- The platform problem begins as six people holding a sagging tarp.
- Initial conditions become “where everybody stands before anybody moves.”
- A delayed sensor becomes driving by a mirror that shows where the road was half a second ago.
- The shared-state insight is translated through a table, shopping cart, doorway, and stretcher before formal notation.
- Foundations Clinic and the timed recitation remain rigorous; the analogies make the rigor followable rather than replacing it.

### Chapter 12 — Boundary Conditions
**Major rewrite complete.**

- Sen begins with a glass of water, table, laptop, and room before moving to the arena model.
- The cracked-floor event is reduced first to four facts: Pike supplies the hit, no extra energy appears, the force takes an unexpected route, and Kade's conventional output remains near zero.
- The brain's unknown role becomes engine, steering wheel, dashboard, or fuse before the medical distinctions are named.
- Source/path/sink becomes “where the trouble starts, what carries it, where it ends.”
- Formal vocabulary remains intact, but each term now follows a physical picture.

### Chapter 6 — Forty-Seven Seconds
**Cadence and mechanics rewrite complete.**

- Repeated explanatory fragments were regrouped while impact fragments remain.
- Priya's acceleration is explained as pushing into the floor and changing what the floor gives back.
- The final transfer is narrated as one causal chain before becoming “one system.”
- Medical and telemetry sequences now use clearer spoken grouping.
- Eli's block model begins with the ordinary version before displaying the formal mismatch.

### Chapter 8 — The Ladder
**First cadence micro-pass complete.**

- Repetitive list fragments were combined.
- The ranking formula is split into audibly manageable groups.
- Training, loss, and montage sequences now use varied sentence length.
- Oren's Storage mechanics are stated as an action before the label carries the explanation.

### Chapter 11 — The Broken Floor
**Editorial review complete; no major rewrite justified yet.**

This chapter already establishes physical geography before speed, gives explicit abort triggers, and makes the load path visible through bodies, floor, dampers, and service trench. It should receive the global cadence sweep, but it does not need the same conceptual translation surgery as Chapters 10 and 12.

## Reproducibility

- `scripts/listening_flow_audit.py` ranks candidate problems but does not change prose.
- `.github/workflows/listening-flow-audit.yml` runs the cross-manuscript comparison.
- `scripts/apply_listening_flow_micro_edits.py` contains exact asserted replacements for small cadence fixes.
- `.github/workflows/apply-listening-flow-micro-edits.yml` applies and commits those transparent micro-edits on this branch.

## Current status

- Contact Zero benchmark review: **REPRESENTATIVE REVIEW COMPLETE; separate long-sentence polish recommended later.**
- Book 1 listening diagnosis: **COMPLETE.**
- Ch6 cadence rewrite: **COMPLETE.**
- Ch8 first cadence pass: **COMPLETE.**
- Ch10 listening-flow rewrite: **COMPLETE.**
- Ch11 conceptual review: **COMPLETE / global cadence sweep still required.**
- Ch12 listening-flow rewrite: **COMPLETE.**
- Ch13–15 technical/action sequence: **NEXT.**
- Ch22, Ch24, Ch30, Ch32: **BACKLOG.**
- Whole-book Tier B sweep: **IN PROGRESS.**
- Full audio verification: **BACKLOG.**
