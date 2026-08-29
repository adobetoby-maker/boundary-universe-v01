#!/usr/bin/env python3
"""Apply exact, reviewable audiobook-flow edits.

Every replacement is intentionally literal. The script fails if the expected
source text is absent or appears more than once, preventing silent broad edits.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "books/book-01-the-ninth-standard/manuscript/chapter-06-forty-seven-seconds.md": [
        (
            '“Pike—Priya. Me. The floor and wall.”',
            '“Priya. Me. The floor and wall.”',
        ),
    ],
    "books/book-01-the-ninth-standard/manuscript/chapter-08-the-ladder.md": [
        (
            "They said it was about placement.\n\nScholarship weighting.\n\nHouse points.\n\nProfessional scouting.\n\nTraining access.\n\nAll true.",
            "They said it was about placement, scholarship weighting, House points, professional scouting, and training access. All of that was true.",
        ),
        (
            "Students could normally challenge within a fixed band above or below their current rank. Winning did not simply exchange two numbers. The system recalculated performance based on opponent rating, margin, safety compliance, field efficiency, recent results, and something the academy called *competitive confidence*, which Kade suspected had been invented by mathematicians who disliked happiness.",
            "Students could normally challenge within a fixed band above or below their current rank. Winning did not simply exchange two numbers. The system considered opponent rating, margin, safety compliance, field efficiency, and recent results. It also measured something called *competitive confidence*, which Kade suspected had been invented by mathematicians who disliked happiness.",
        ),
        (
            "Mason beat Kade in seventy-eight seconds.\n\nThe second opponent beat him in fifty-two.\n\nThe third took ninety-one.\n\nKade left the hall furious.\n\nNot because he lost.\n\nBecause every loss became obvious one beat too late.\n\nHis stance was too high.\n\nHis feet crossed when he retreated.\n\nHe watched shoulders and ignored hips.\n\nHe chased hands instead of center mass.\n\nHe planted his rear foot before he knew which direction he needed to leave.\n\nWorst of all, none of those mistakes required classified physics to fix.",
            "Mason beat Kade in seventy-eight seconds. The second opponent needed fifty-two, and the third needed ninety-one.\n\nKade left the hall furious—not simply because he had lost, but because each mistake became obvious one beat too late. His stance was too high. His feet crossed when he retreated. He watched shoulders and ignored hips, chased hands instead of center mass, and planted his rear foot before he knew which direction he needed to leave.\n\nWorst of all, none of those mistakes required classified physics to fix.",
        ),
        (
            "For four days, Kade did almost nothing interesting.\n\nStance drills.\n\nBalance drills.\n\nFalls.\n\nRecoveries.\n\nFoot placement.\n\nBreathing.\n\nGrip breaks.\n\nHip escapes.",
            "For four days, Kade did almost nothing interesting: stance and balance drills, falls and recoveries, foot placement, breathing, grip breaks, and hip escapes.",
        ),
        (
            "On the fifth day, Kade beat Rank 10,205 in an unranked simulation.\n\nNot elegantly.\n\nHe absorbed two clean impacts, missed a sweep, recovered badly, and won because he recognized that his opponent always shifted weight before accelerating.\n\nNo cold line behind his eyes.\n\nNo impossible transfer.\n\nNo missing telemetry.\n\nJust timing.",
            "On the fifth day, Kade beat Rank 10,205 in an unranked simulation. It was not elegant. He absorbed two clean impacts, missed a sweep, recovered badly, and won because he recognized that his opponent always shifted weight before accelerating.\n\nThere was no cold line, impossible transfer, or missing telemetry. Just timing.",
        ),
        (
            "Kade won the next one.\n\nLost the third.\n\nWon two more.\n\nNo symptoms.\n\nNo anomalies.",
            "Kade won the next simulation, lost the third, and won two more. No symptoms appeared, and no anomalies followed.",
        ),
        (
            "Eli’s first version of the model had six columns.\n\nOpponent rank.\n\nDominant side.\n\nAverage opening distance.\n\nFirst-step direction.\n\nMost common finish.\n\nAnd one called **KADE DID SOMETHING DUMB**.",
            "Eli’s first five columns tracked opponent rank, dominant side, average opening distance, first-step direction, and most common finish. The sixth was called **KADE DID SOMETHING DUMB**.",
        ),
        (
            "The model was crude.\n\nUseful anyway.",
            "The model was crude, but useful.",
        ),
        (
            "Kade lost the first exchange.\n\nAdjusted.\n\nLost the second by less.\n\nOn the third, he stopped trying to catch her and started denying the route she preferred.",
            "Kade lost the first exchange, adjusted, and lost the second by less. On the third, he stopped trying to catch Mae and started denying the route she preferred.",
        ),
        (
            "It was only eighty-one places.\n\nIt felt enormous.\n\nNot because the number mattered.\n\nBecause he knew exactly how he had earned it.",
            "It was only eighty-one places, but it felt enormous—not because the number itself mattered, but because he knew exactly how he had earned it.",
        ),
        (
            "Oren did not rush.\n\nHe waited.\n\nKade hated waiting opponents.\n\nThey denied him obvious information.",
            "Oren did not rush. He waited, and Kade hated waiting opponents because they denied him obvious information.",
        ),
        (
            "The floor seemed to grab Oren’s stance.\n\nStorage.\n\nNot holding Kade.\n\nHolding the movement Oren had refused to spend.",
            "The floor seemed to grab Oren’s stance. Storage was not holding Kade; it was holding the movement Oren had refused to spend.",
        ),
        (
            "Second exchange.\n\nSame patience.\n\nSame offered distance.\n\nThis time Kade started in, then stopped before Oren could load the response.\n\nOren’s expression changed.\n\nTiny.\n\nAnnoyed.\n\nThere.\n\nKade had been watching bodies.\n\nHe needed to watch *timing*.",
            "The second exchange began with the same patience and the same offered distance. This time Kade started in, then stopped before Oren could load the response.\n\nOren’s expression changed by a tiny, annoyed fraction.\n\nThere. Kade had been watching bodies when he needed to watch *timing*.",
        ),
        (
            "Third exchange.\n\nKade stepped forward twice without committing.\n\nOren stored both reactions.\n\nThe field trace around his feet brightened.\n\nKade retreated.\n\nOren followed for the first time.\n\nThat was what Kade wanted.\n\nHe changed rhythm abruptly.\n\nFast entry.\n\nOren released early.\n\nKade was not where the release expected him to be.",
            "In the third exchange, Kade stepped forward twice without committing. Oren stored both reactions, and the field trace around his feet brightened.\n\nKade retreated. Oren followed for the first time. That was what Kade wanted.\n\nHe changed rhythm and entered fast. Oren released early, but Kade was no longer where the stored movement expected him to be.",
        ),
        (
            "Oren needed space to collect before he could release.\n\nKade stopped giving it to him.\n\nNot by charging.\n\nBy standing where Oren wanted to reset.\n\nFor the first time, Oren had to move around Kade instead of arranging Kade around himself.\n\nHis feet crossed.\n\nOne step.\n\nSmall mistake.\n\nEnough.",
            "Oren needed space to collect before he could release, so Kade stopped giving it to him. He did not charge. He simply stood where Oren wanted to reset.\n\nFor the first time, Oren had to move around Kade instead of arranging Kade around himself. His feet crossed for one small step. It was enough.",
        ),
        (
            "Kade won.\n\nNot because Oren’s ability had failed.\n\nBecause something he had learned against Mae had survived into a different problem.",
            "Kade won, not because Oren’s ability had failed, but because something he had learned against Mae had survived into a different problem.",
        ),
        (
            "The wins did not arrive in a montage when Kade actually lived them.\n\nBetween them were sore mornings, ordinary classes, laundry, a failed mechanics quiz because he had used the right reasoning with notation the professor refused to accept, two dinners where he was too tired to talk, and one spectacularly bad challenge that ended with Kade face-down at the boundary while Eli shouted useful advice approximately three seconds too late.",
            "The wins did not arrive as a montage while Kade was living them. They came between sore mornings, ordinary classes, and laundry. He failed a mechanics quiz after using the right reasoning with notation the professor refused to accept. He sat through two dinners too tired to talk, then ended one spectacularly bad challenge face-down at the boundary while Eli shouted useful advice approximately three seconds too late.",
        ),
        (
            "Fast.\n\nTechnically clean.\n\nComing off a loss.\n\nKade had already trained twice that day.",
            "She was fast, technically clean, and coming off a loss. Kade had already trained twice that day.",
        ),
    ],
}


def apply_replacements(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise RuntimeError(
                f"Expected exactly one match in {path}: got {count} for {old[:80]!r}"
            )
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for relative, replacements in REPLACEMENTS.items():
        apply_replacements(ROOT / relative, replacements)
        print(f"updated {relative}: {len(replacements)} replacements")


if __name__ == "__main__":
    main()
