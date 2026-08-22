#!/usr/bin/env python3
"""
Split a chapter into (voice, text) spans for full-cast narration.

THE PROBLEM THIS SOLVES
-----------------------
    "Bathroom," Darius said.

A single render has Darius announcing his own attribution. The quote must go to
Darius and the tag to the narrator, which means cutting a sentence in half on a
boundary that is invisible on the page. CAST.md flagged this as the reason
full-cast costs more than "same text, more voices"; this is that cost, paid.

THE HARDER PROBLEM
------------------
Chapter 2 has 247 lines of dialogue and 18 inline tags. Attribution for the
other 229 is positional -- the reader knows who is speaking because of who
spoke last and who is in the room. There is no marker to key on.

So: scenes declare their participants, and inside a scene an untagged line
alternates from the previous speaker. That is right most of the time and wrong
often enough that the output is reviewed by hand before anything is rendered.
OVERRIDES carries every correction, by line number, so the review is durable
rather than repeated.

Narration and Kade share a voice -- the narrator IS Kade's interiority -- so
they merge, which collapses the span count by roughly half.
"""
import json, pathlib, re, sys

from normalise import chapter_heading, normalise, strip_markdown

# voice key -> (base voice, semitone shift from that voice's baseline)
# Male shifts are from Holden's locked +0.5st narrator baseline (voice_chain.py).
VOICE_ID = {
    'holden': '3c9d6053-6334-592c-8997-4e325286af3f',
    'maeve':  '64cf4f1a-61c8-5938-9aea-83d12b2e1d13',   # chosen from a five-way
}                                                       # audition on Elena's hardest line

CAST = {
    'narrator': ('holden', 0.00),   # = Kade. The narrator is his interiority.
    'kade':     ('holden', 0.00),
    'russell':  ('holden', +0.50),  # harried VP; up separates him from the others.
                                    # +1.00 was auditioned and set back to +0.50 by Toby.
    'darius':   ('holden', -1.15),  # was -1.25 in CAST.md; reset by Toby after
                                    # hearing the ladder. Costs nothing to change:
                                    # the single-narrator renders never applied
                                    # per-character shifts, so nothing to re-cut.
    'renn':     ('holden', -1.35),  # set by Toby. NOTE: only 0.20 st below Darius
                                    # -- far tighter than any other pair here, and
                                    # tight enough that the two may not separate.
                                    # Flagged, rendered as specified, judge by ear.
    # Shifts here are absolute from Maeve's own pitch -- see BASE_BASELINE in
    # assemble_cast.py. Elena is the anchor and the other two are placed around
    # her, so moving Elena moves the whole female cast.
    'elena':    ('maeve', -1.00),   # the emotional centre; chosen off a 4-rung ladder
    'vale':     ('maeve',  0.00),   # 35, military, clipped -- a full 1.00 above Elena
    'alvarez':  ('maeve', -1.75),   # 0.75 below Elena. Holding the original -1.25
                                    # offset would have put her at -2.25 from Maeve,
                                    # past the point where a shading reads as an
                                    # impression. She has three lines and CAST.md
                                    # already says she separates by attitude, not
                                    # pitch, so she gives up the depth.
}

# Scenes: (first_line, last_line, [participants in speaking order])
# Line numbers are 1-based into the stripped paragraph list.
# Each entry: (first_line, last_line, [participants]). Two participants means
# "alternate from whoever spoke last" -- which is exactly how a reader resolves
# an untagged two-hander. One participant means "always this speaker".
SCENES = [
    (7, 13, ['darius', 'kade']),     (15, 15, ['russell']),
    (18, 18, ['kade']),              (32, 37, ['russell', 'kade']),
    (42, 47, ['kade', 'darius']),    (50, 51, ['russell', 'kade']),
    (55, 55, ['kade']),              (58, 61, ['kade', 'russell']),
    (65, 70, ['kade', 'russell']),   (74, 74, ['kade']),
    (88, 89, ['kade', 'darius']),    (95, 100, ['russell', 'kade']),
    (104, 108, ['kade', 'russell']), (110, 110, ['russell']),
    (113, 116, ['russell', 'darius']), (123, 125, ['renn', 'russell']),
    (128, 129, ['darius', 'kade']),  (133, 133, ['renn']),
    (140, 140, ['darius']),          (145, 145, ['kade']),
    (147, 149, ['darius', 'kade']),  (154, 154, ['kade']),
    (156, 156, ['renn']),            (168, 168, ['kade']),
    (170, 174, ['renn', 'kade']),    (177, 177, ['renn']),
    (179, 179, ['alvarez']),         (181, 181, ['alvarez']),
    (192, 192, ['kade']),            (194, 196, ['kade', 'vale']),
    (200, 206, ['renn', 'kade']),    (208, 208, ['kade']),
    (215, 215, ['vale']),            (216, 216, ['kade']),
    (221, 221, ['kade']),            (223, 223, ['vale']),
    (226, 226, ['vale']),            (228, 230, ['kade']),
    (232, 232, ['elena']),           (244, 244, ['elena']),
    (247, 249, ['elena', 'kade']),   (252, 260, ['elena', 'kade']),
    (263, 263, ['elena']),           (278, 286, ['elena', 'renn']),
    (291, 291, ['elena']),           (295, 295, ['vale']),
    (296, 296, ['kade']),            (298, 298, ['vale']),
    (302, 302, ['renn']),            (303, 303, ['kade']),
    (304, 304, ['elena']),           (307, 307, ['kade']),
    (314, 314, ['kade']),            (320, 327, ['kade', 'renn']),
    (330, 330, ['kade']),            (334, 336, ['kade', 'renn']),
    (339, 339, ['kade']),            (343, 344, ['kade', 'renn']),
    (346, 349, ['kade', 'renn']),    (357, 359, ['elena', 'renn']),
    (361, 363, ['elena', 'vale']),   (367, 367, ['elena']),
    (373, 376, ['kade', 'elena']),   (389, 392, ['kade', 'elena']),
    (395, 401, ['kade', 'elena']),   (403, 404, ['elena', 'kade']),
    (408, 408, ['kade']),            (410, 410, ['elena']),
    (415, 415, ['elena']),           (416, 421, ['kade', 'elena']),
    (436, 437, ['darius', 'kade']),  (442, 443, ['darius', 'kade']),
    (446, 449, ['darius', 'kade']),  (452, 452, ['darius']),
    (454, 455, ['kade', 'darius']),  (462, 462, ['darius']),
    (465, 465, ['elena']),           (467, 468, ['kade', 'elena']),
    (470, 475, ['kade', 'elena']),   (478, 478, ['elena']),
    (480, 482, ['elena', 'kade']),   (485, 491, ['elena', 'kade']),
    (493, 493, ['elena']),           (503, 504, ['kade', 'elena']),
    (508, 508, ['elena']),           (513, 515, ['kade', 'elena']),
    (518, 518, ['elena']),           (528, 528, ['kade']),
    (530, 530, ['elena']),           (544, 547, ['kade', 'elena']),
    (551, 552, ['kade', 'elena']),   (562, 562, ['kade']),
    (566, 568, ['elena', 'kade']),   (573, 573, ['kade']),
    (575, 578, ['elena', 'kade']),   (580, 582, ['elena', 'kade']),
    (590, 592, ['elena', 'kade']),
]

# Corrections found by reading the segmenter's output against the chapter.
# Two kinds live here, and it is worth keeping them distinct:
#
#   "he said" / "she asked"  -- a pronoun tag the name-matcher cannot resolve.
#   scene-opening lines      -- alternation assumes the previous speaker is
#                               being answered, but a scene sometimes opens with
#                               the SAME person who last spoke, and then every
#                               line after it inverts. These are the dangerous
#                               ones: one wrong seed flips a whole exchange.
OVERRIDES = {
    93: 'kade', 162: 'kade', 355: 'kade', 460: 'kade',      # "he said/asked"
    212: 'vale', 372: 'elena', 388: 'elena', 501: 'elena',  # "she said/asked"
    113: 'russell',                                          # Russell, twice running
    42: 'kade',      # Kade says "Darius." having just asked "What video?".
                     # Without this the whole 42-47 exchange inverts and Darius
                     # interrogates himself -- the exact failure this table exists
                     # for, and the only one the review caught in 247 lines.
    18: 'kade',      # "No," they said together -- Kade and Darius in chorus;
                     # rendered in Kade's voice rather than the narrator's.
    252: 'elena', 480: 'elena', 485: 'elena', 590: 'elena',  # Elena, twice running
    # Text messages, in the sender's voice rather than the narrator's.
    77: 'elena', 78: 'elena', 80: 'elena', 85: 'elena',
    83: 'kade', 536: 'kade', 534: 'darius',
}

# "...," Vale said.          quote, then attribution
TAG = re.compile(r'^(?P<q>[“"].+?[”"])\s*,?\s*(?P<tag>[^“"]+?)\.?$')
# Kade looked up. "..."     any narration, then quote
LEAD = re.compile(r'^(?P<pre>[^“"]+?)\s*(?P<q>[“"].+[”"])\s*$')
# "A," Vale said. "B."      the speaker is interrupted by their own attribution
SPLIT3 = re.compile(r'^(?P<a>[“"].+?[”"])\s*,?\s*(?P<tag>[^“"]+?)[.,]\s*(?P<b>[“"].+[”"])\s*$')
NAME = {'kade': 'kade', 'darius': 'darius', 'russell': 'russell', 'renn': 'renn',
        'vale': 'vale', 'elena': 'elena', 'alvarez': 'alvarez'}


def speaker_in(text):
    low = text.lower()
    for key, v in NAME.items():
        if re.search(rf'\b{key}\b', low):
            return v
    return None


def load(path):
    t = pathlib.Path(path).read_text()
    n = int(re.search(r'ch(\d+)', path).group(1))
    t = re.sub(r'^#\s*Chapter\s*\d+\s*[—–-]\s*(.+)$',
               lambda m: chapter_heading(n, m.group(1)), t, count=1, flags=re.M)
    t = strip_markdown(t)
    t = re.sub(r'(?m)^\s*---\s*$', '', t).replace('⸻', '')
    t = normalise(t)
    return [l.strip() for l in t.split('\n') if l.strip()]


def segment(lines, scenes, overrides):
    """Yield (line_no, voice, text). A tagged line yields two spans."""
    out = []
    scene_for = {}
    for a, b, parts in scenes:
        for i in range(a, b + 1):
            scene_for[i] = parts

    last = None
    for i, line in enumerate(lines, 1):
        is_dialogue = line.startswith(('“', '"'))

        m3 = SPLIT3.match(line)
        if m3:                                       # "A," Vale said. "B."
            who = overrides.get(i) or speaker_in(m3.group('tag')) or 'narrator'
            out.append((i, who, m3.group('a').strip()))
            out.append((i, 'narrator', m3.group('tag').strip() + '.'))
            out.append((i, who, m3.group('b').strip()))
            last = who
            continue

        if not is_dialogue:
            m = LEAD.match(line)
            if m:                                    # Kade looked up. "..."
                who = overrides.get(i) or speaker_in(m.group('pre')) or 'narrator'
                out.append((i, 'narrator', m.group('pre').strip()))
                out.append((i, who, m.group('q').strip()))
                last = who
                continue
            who = overrides.get(i, 'narrator')
            out.append((i, who, line))
            continue

        m = TAG.match(line)
        if m:                                        # "...," Vale said.
            who = overrides.get(i) or speaker_in(m.group('tag')) or 'narrator'
            out.append((i, who, m.group('q').strip()))
            out.append((i, 'narrator', m.group('tag').strip() + '.'))
            last = who
            continue

        who = overrides.get(i)
        if not who:
            parts = scene_for.get(i, ['kade'])
            if last in parts and len(parts) == 2:    # two-hander: alternate
                who = parts[1 - parts.index(last)]
            else:
                who = parts[0]
        out.append((i, who, line))
        last = who
    return out


def merge(spans):
    """Collapse consecutive same-voice spans. narrator and kade are one voice."""
    def key(v):
        return 'narrator' if v in ('narrator', 'kade') else v
    merged = []
    for ln, v, t in spans:
        k = key(v)
        if merged and merged[-1][0] == k:
            merged[-1][1].append(t)
            merged[-1][2].append((ln, v))
        else:
            merged.append([k, [t], [(ln, v)]])
    return merged
