#!/usr/bin/env python3
"""Apply the second exact listening-flow edit batch.

This batch targets audiobook working-memory load in the Consensus climax and a
small number of repeated setup fragments in Cross Examination. Every source
match is asserted exactly once.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "books/book-01-the-ninth-standard/manuscript/chapter-32-consensus.md": [
        (
            "Containment read twenty-three percent.\n\nThen twenty-two.\n\nAaron braced one hand against the rail.",
            "Containment fell from twenty-three percent to twenty-two. Aaron braced one hand against the rail.",
        ),
        (
            "Kade looked around.\n\nMara.\n\nSera.\n\nJulian.\n\nTaren.\n\nSen.\n\nAaron.\n\nEli, present as a voice and a live network trace above them.\n\nEveryone carrying different fear.\n\nDifferent training.\n\nDifferent reasons to stay.\n\nDifferent reasons not to trust.",
            "Kade looked around at Mara, Sera, Julian, Taren, Sen, Aaron, and Eli—the last present as a voice and a live network trace above them. Each carried different fear and training, with a different reason to stay and a different reason not to trust.",
        ),
        (
            "The room had become a machine for transferring one failure into the next.\n\nField instability from the Node loaded the dampers. The dampers pushed correction into the containment spine. The cracked spine bled force into Asterion's foundation. Heat climbed through the emergency sinks. The sinks were already sharing coolant with the damaged engineering level overhead.\n\nIf they stabilized only one piece, another would fail faster.",
            "The chamber had become Professor Amadi's couch problem with an island underneath it: every correction changed the weight in everyone else's hands. Field instability from the Node loaded the dampers. The dampers pushed correction into the containment spine. The cracked spine bled force into Asterion's foundation. Heat climbed through the emergency sinks, which were already sharing coolant with the damaged engineering level overhead.\n\nIf they stabilized only one piece, another would fail faster.",
        ),
        (
            'Eli said, “So eventually one brain became the network bottleneck.”',
            '“So twelve people were carrying the same table, and one brain kept grabbing every corner to correct it,” Eli said. “Eventually the foreman became the bottleneck.”',
        ),
        (
            "They did not need one person willing to try Consensus.\n\nThey needed six people to reject the alternative separately.",
            "They did not need one person willing to try Consensus. They needed six people to reject the alternative separately.",
        ),
        (
            "He thought instead of the space they were both choosing to share.\n\nA physics problem with no owner.\n\nA House plan nobody owned anymore.\n\nA training partnership where both people could change the answer.\n\nThe world shifted.\n\nNo light.\n\nNo dramatic sound.",
            "He thought instead of the space they were both choosing to share: a physics problem with no owner, a House plan that had outgrown its author, and a training partnership where either person could change the answer.\n\nThe world shifted without light or dramatic sound.",
        ),
        (
            "Not her thoughts.\n\nNot memories.\n\nNothing private.\n\nHer balance.\n\nHer field geometry.\n\nHer intent to hold the chamber stable and remain herself while doing it.\n\nThe last part had weight.",
            "He received no thoughts, memories, or private rooms. He received her balance, her field geometry, and her intent to hold the chamber stable while remaining herself.\n\nThe last part had weight.",
        ),
        (
            "A boundary held around everything else.\n\nThere were rooms he could not enter.\n\nHer fear was not available to him.\n\nNeither were her memories, her family, or whatever she had thought when she first met him in a borrowed Asterion uniform trying not to look impressed.",
            "A boundary held around everything else. There were rooms he could not enter: her fear, her memories, her family, and whatever she had thought when she first met him in a borrowed Asterion uniform trying not to look impressed.",
        ),
        (
            "Sera entered differently.\n\nNot as more information.\n\nAs another center.\n\nDistribution.\n\nRisk as routes.\n\nLoads that needed somewhere safe to go.\n\nPeople before structures.",
            "Sera entered differently—not as more information, but as another center. She brought distribution, risk translated into routes, and loads that needed somewhere safe to go. People came before structures.",
        ),
        (
            "Julian's contribution arrived as decisions made before panic could own them.\n\nForce balance.\n\nPriorities.\n\nThe ability to accept that one option had to be abandoned so another survived.\n\nNot command.\n\nLeadership without control.\n\nHe did not bring a plan.\n\nThat surprised Kade.\n\nJulian always seemed to have one.",
            "Julian's contribution arrived as decisions made before panic could own them: force balance, priorities, and the ability to abandon one option so another survived. It was leadership without control, not command.\n\nHe did not bring a plan, which surprised Kade. Julian always seemed to have one.",
        ),
        (
            "The network became cleaner.\n\nStronger.\n\nWrong.",
            "The network became cleaner and stronger—and wrong.",
        ),
        (
            "They reformed.\n\nMara.\n\nSera.\n\nJulian.\n\nSeparate.\n\nPresent.\n\nNo one promoted to center.",
            "They reformed with Mara, Sera, and Julian separate, present, and still themselves. No one was promoted to center.",
        ),
        (
            "Everything between him and Kade remained unresolved.\n\nThe reports.\n\nThe friendship.\n\nThe betrayal.\n\nThe eight-second archive override.\n\nThe key that opened Sublevel Nine.",
            "Everything between him and Kade remained unresolved: the reports, friendship, betrayal, eight-second archive override, and the key that opened Sublevel Nine.",
        ),
        (
            "Every access route divided people into categories. Cleared or excluded. Useful or dangerous. Observer or subject. A maintenance panel in the east damper accepted commands from three Directorate pathways that did not appear on Asterion's own system map. Each pathway required a person with the correct inherited authority, and each authority could revoke the one below it.\n\nNothing moved sideways.\n\nEverything moved down.",
            "Every access route divided people into categories: cleared or excluded, useful or dangerous, observer or subject. A maintenance panel in the east damper accepted commands from three Directorate pathways that did not appear on Asterion's own system map. Each pathway required a person with the correct inherited authority, and each authority could revoke the one below it.\n\nNothing moved sideways. Everything moved down.",
        ),
        (
            "Information flooded everything.\n\nThermal loads.\n\nSignal phase.\n\nDamper latency.\n\nStructural temperatures.\n\nContainment geometry.\n\nEli processed the machine faster than the machine could present itself to everyone else.\n\nThe flood carried no sense of importance.\n\nThat was the problem.\n\nA temperature rise of point two degrees arrived beside a catastrophic phase inversion. An old maintenance warning from before the siege demanded the same attention as a cracked coolant manifold. Six thousand live values pushed toward the shared space because the systems had been built to report data, not meaning.",
            "Information flooded everything: thermal load, signal phase, damper latency, structural temperature, and containment geometry. Eli processed the machine faster than the machine could present itself to everyone else.\n\nThe flood carried no sense of importance. Everything shouted at the same volume: a temperature rise of point two degrees beside a catastrophic phase inversion, an old maintenance warning beside a cracked coolant manifold. Six thousand live values pushed toward the shared space because the systems had been built to report data, not meaning.",
        ),
        (
            "The data did not lessen.\n\nIt acquired grammar.",
            "The data did not lessen; it acquired grammar.",
        ),
        (
            "Kade found her presence.\n\nThen Sera.\n\nJulian.\n\nTaren.\n\nEli.\n\nSeparate.\n\nChosen.\n\nThe network stabilized.",
            "Kade found Mara, Sera, Julian, Taren, and Eli—separate, chosen, and still themselves. The network stabilized.",
        ),
        (
            "He looked at the entire containment problem.\n\nNode.\n\nDamper arrays.\n\nAsterion’s buried structure.\n\nAaron.\n\nThe six-person Consensus network.\n\nHeat sinks.\n\nSignal leakage.\n\nThe Directorate bypass routes.\n\nOne system.\n\nNot because the boundaries were unreal.\n\nBecause they could be chosen for the work that needed doing.",
            "He looked at the entire containment problem: the Node, damper arrays, Asterion's buried structure, Aaron, the six-person Consensus network, heat sinks, signal leakage, and the Directorate bypass routes. Together they formed one active system—not because the boundaries were unreal, but because they could be chosen for the work that needed doing.",
        ),
        (
            "Containment climbed.\n\nNine.\n\nEleven.\n\nFourteen.",
            "Containment climbed from nine to eleven to fourteen percent.",
        ),
        (
            "Containment climbed to twenty-eight percent.\n\nThen forty-one.",
            "Containment climbed to twenty-eight percent, then forty-one.",
        ),
        (
            "North shelter remained stable.\n\nThe dining-hall triage grid had full power.\n\nThe arena team was clear.\n\nShe released the counts instead of trying to carry them out of the network with her.",
            "North shelter remained stable, the dining-hall triage grid had full power, and the arena team was clear. Sera released the counts instead of trying to carry them out of the network with her.",
        ),
        (
            "The signal had been suppressed.\n\nAlmost.\n\nA burst lasting 0.83 seconds had escaped during the initial synchronization.",
            "The signal had been suppressed—almost. A burst lasting 0.83 seconds had escaped during the initial synchronization.",
        ),
    ],
    "books/book-01-the-ninth-standard/manuscript/chapter-13-cross-examination.md": [
        (
            "The first took nineteen seconds.\n\nThe second took twenty-three.\n\nThe third took fifteen because Kade became irritated by the first two and attempted something ambitious.\n\nBy the fifth, he understood why Rank One was Rank One.\n\nJulian did not look fast.\n\nHe removed decisions.",
            "The first took nineteen seconds, the second twenty-three, and the third fifteen because Kade became irritated and attempted something ambitious. By the fifth, he understood why Rank One was Rank One.\n\nJulian did not look fast. He removed decisions.",
        ),
        (
            "On reset six, Kade tried waiting.\n\nJulian waited better.\n\nOn reset seven, Kade attacked first.\n\nJulian used the attack to decide where Kade would be standing three exchanges later.\n\nOn reset eight, Kade attempted to become unpredictable.\n\nJulian swept him in fourteen seconds.",
            "On reset six, Kade tried waiting, and Julian waited better. On reset seven, Kade attacked first, allowing Julian to decide where he would be standing three exchanges later. On reset eight, Kade tried to become unpredictable and Julian swept him in fourteen seconds.",
        ),
        (
            "There.\n\nCompetitive.\n\nNot saintly.\n\nMuch better.",
            "There. Competitive, not saintly. Much better.",
        ),
        (
            "The first problem Kade solved was not the platform.\n\nIt was his own team.\n\nNot because they were incompetent.\n\nBecause everybody could see a different failure first.",
            "The first problem Kade solved was not the platform but his own team—not because they were incompetent, but because everyone could see a different failure first.",
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
