# BOOK 1 MANUSCRIPT LENGTH STATUS

**Source branch:** `polish/second-half`
**Chapter files:** 33
**Raw UTF-8 manuscript bytes across chapter files:** 388,563 bytes
**Original target:** 187,000 words / ~20.1 hours at 9,300 words/hour

## Current finding
The polished manuscript is substantially shorter than the original 187k target.

The GitHub connector exposes exact file sizes but does not expose a server-side word-count operation in this session. Based on 388,563 bytes of English dialogue-heavy prose, the current manuscript is expected to be roughly **70k–78k words**. This estimate is sufficient to establish that the book is well below the planned ~187k length, but it should not be treated as the final exact count.

## Exact reproducible count
Run from repository root:

```bash
python scripts/word_count.py
```

The script prints:
- every chapter's exact token-style word count;
- total words;
- estimated finished-audio hours at 9,300 words/hour;
- gap to 187,000 words.

A GitHub Actions workflow is also included at `.github/workflows/manuscript-metrics.yml` on the Book 2 prep branch so the count can be captured as a build artifact when Actions executes.

## Editorial implication
Do **not** add filler to reach 187k.

If a 18–20 hour finished audiobook remains the goal, expansion should come from scene-level depth that the story genuinely benefits from:
- more ordinary academy life and classes;
- longer training/fight sequences with tactical clarity;
- deeper supporting-character scenes;
- more aftermath and consequence;
- fuller Aaron/Elena history;
- more gradual tournament progression;
- more room in grief, siege and Consensus sequences.

If the audio build proves the current pacing feels excellent at a shorter runtime, revisiting the 187k target is preferable to padding the novel.
