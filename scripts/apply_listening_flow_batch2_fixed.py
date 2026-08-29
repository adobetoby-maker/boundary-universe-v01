#!/usr/bin/env python3
"""Run Batch 2 with the verified Cross Examination replacements only."""

from apply_listening_flow_batch2 import REPLACEMENTS, ROOT, apply

CH13 = "books/book-01-the-ninth-standard/manuscript/chapter-13-cross-examination.md"

# The fourth optional Ch13 candidate described a pattern that is not present in
# the current manuscript. Preserve the three verified Ch13 replacements and all
# 22 verified Consensus replacements.
REPLACEMENTS[CH13] = REPLACEMENTS[CH13][:3]

for relative, replacements in REPLACEMENTS.items():
    apply(ROOT / relative, replacements)
    print(f"updated {relative}: {len(replacements)} replacements")
