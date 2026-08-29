#!/usr/bin/env python3
"""Apply concrete-first and cadence edits to Chapters 4 and 24."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "books/book-01-the-ninth-standard/manuscript/chapter-04-ten-thousand-four-hundred-eighty-two.md": [
        (
            "By six forty-five, he had been scanned, weighed, measured, photographed, tested for color perception, lung capacity, reflex response, joint stability, hearing range, balance, sleep debt, reaction latency, blood chemistry, Conduit compatibility markers, and several things Kade suspected existed solely to justify expensive equipment.",
            "By six forty-five, they had measured nearly everything medical, sensory, or mechanical about him: blood chemistry, breathing, hearing, balance, reflexes, joint stability, sleep debt, reaction time, and Conduit compatibility. Several remaining tests seemed designed solely to justify expensive equipment.",
        ),
        (
            "The tests repeated.\n\nGravity differential.\n\nElectromagnetic gradient.\n\nKinetic storage field.\n\nThermal transfer.\n\nLocalized structural cohesion.\n\nEach time, Park asked the same kind of question.\n\nEach time Kade gave the same answer.\n\nNothing.",
            "The equipment cycled through gravity, electromagnetic force, kinetic storage, heat transfer, and structural cohesion. Each time Park asked the same kind of question, and each time Kade gave the same answer: nothing.",
        ),
        (
            "Kade stared at the puck.\n\nThe puck continued being a puck.\n\nHe concentrated.\n\nNothing.\n\nHe imagined pushing it.\n\nNothing.\n\nHe pictured it sliding.\n\nNothing.\n\nHe thought of acceleration, friction, weight, every physical thing that should matter.\n\nNothing.",
            "Kade stared at the puck. It continued being a puck.\n\nHe concentrated, imagined pushing it, pictured it sliding, and ran through acceleration, friction, weight—every physical thing that should matter. Nothing changed.",
        ),
        (
            "They reset.\n\nNothing.\n\nThey changed the object.\n\nNothing.\n\nThey gave him a training bead designed to respond to first-time Resonants.\n\nNothing.\n\nThey gave him a suspended ribbon sensitive to microscopic field interaction.\n\nNothing.",
            "They reset and changed the object. A training bead designed for first-time Resonants stayed still. A suspended ribbon sensitive to microscopic field interaction stayed still too.",
        ),
        (
            "His reaction metrics climbed.\n\nSeventy-third percentile.\n\nEighty-first.\n\nNinety-sixth in adaptive route selection.\n\nThe technicians became interested again.",
            "His reaction metrics climbed from the seventy-third percentile to the eighty-first, then reached the ninety-sixth in adaptive route selection. The technicians became interested again.",
        ),
    ],
    "books/book-01-the-ninth-standard/manuscript/chapter-24-the-quiet-war.md": [
        (
            "Official history said Resonance emerged from experimental physics thirty-one years ago. A cascade of breakthroughs. New sensors. New neural interfaces. A rare compatibility between human cognition and previously undetected field behavior.\n\nKade had read versions of that story in school.",
            "Official history said Resonance emerged from experimental physics thirty-one years ago through a cascade of breakthroughs: new sensors, new neural interfaces, and a rare compatibility between human cognition and previously undetected field behavior. Kade had read versions of that story in school.",
        ),
        (
            "Sen continued.\n\n“A deep-space survey detected a patterned emission. Artificial. Repeating, but unstable. The object producing it was damaged. We did not understand its language, if it had one. We did understand that its field emissions interacted with human neural activity in ways no known physical model predicted.”\n\n“Resonance,” Mara said.",
            "Sen pointed to the damaged object.\n\n“Plain version first. Imagine finding a broken instrument beyond Neptune. We could not read its music, but some human nervous systems responded to its field the way glassware answers the right note.”\n\nMara frowned. “Not literally vibrating.”\n\n“No. But the relationship existed before we had a theory or a name for it.”\n\nSen returned to the record. “A deep-space survey detected a patterned emission—artificial, repeating, but unstable. The object producing it was damaged. We did not understand its language, if it had one. We did understand that its field emissions interacted with human neural activity in ways no known physical model predicted.”\n\n“Resonance,” Mara said.",
        ),
        (
            "“Attempts to understand why some compatible subjects could stabilize one another’s field interactions.”\n\n“Multi-user Resonance?”\n\n“Crude versions.”",
            "“Imagine two people carrying the same tray. Every correction by one person changes the weight the other person feels. Some pairings made the tray steadier. Others shook it apart. We were trying to learn why.”\n\n“Multi-user Resonance?” Eli asked.\n\n“Crude versions.”",
        ),
        (
            "“Competition produces high-quality observation under stress.”\n\nSomething settled unpleasantly into place.\n\nEvery fight recorded.\n\nEvery decision scored.\n\nEvery personality exposed under pressure.",
            "“Competition produces high-quality observation under stress. A calm drill shows what a student knows. A broken plan shows what survives when knowledge, pride, and fear collide.”\n\nSomething settled unpleasantly into place: every fight recorded, every decision scored, every personality exposed under pressure.",
        ),
        (
            "“How people adapt. Whether they can coordinate. Whether they remain themselves under pressure. Whether power makes them more or less capable of sharing control.”",
            "“What they do when a plan breaks, a teammate disagrees, or the strongest operator disappears. Whether they adapt, coordinate, and remain themselves under pressure. Whether power makes them more or less capable of sharing control.”",
        ),
        (
            "“Then coherence did not mean sameness.”\n\nSen’s hand dropped from the control.\n\n“No. We learned that afterward.”",
            "“Then coherence did not mean sameness.”\n\nKade looked at the ring of unequal traces. “Same tray. Different hands.”\n\nSen’s hand dropped from the control. “Yes. We learned that afterward.”",
        ),
        (
            "Some bright.\n\nSome faint.\n\nAaron’s looked wrong compared with the others—not larger, but crossing between categories instead of staying inside one.",
            "Some traces were bright and others faint. Aaron’s looked wrong compared with all of them—not larger, but crossing between categories instead of staying inside one.",
        ),
        (
            "Not a photograph.\n\nNot a frozen face.\n\nHis father shifted his weight, said something to a person beside him, and laughed.",
            "This was not a photograph or a frozen face. His father shifted his weight, said something to a person beside him, and laughed.",
        ),
    ],
}


def apply(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise RuntimeError(
                f"Expected one match in {path}; got {count} for {old[:100]!r}"
            )
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for relative, replacements in REPLACEMENTS.items():
        apply(ROOT / relative, replacements)
        print(f"updated {relative}: {len(replacements)} replacements")


if __name__ == "__main__":
    main()
