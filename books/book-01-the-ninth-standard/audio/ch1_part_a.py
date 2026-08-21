# Chapter 1 SSML — part A (opening through the break before testing)
#
# Markup philosophy: the manuscript is written in single-line beats, and that
# line-breaking IS the performance direction. TTS sees a paragraph, so every
# beat is re-encoded as an explicit <break>. Values used consistently:
#   250-300ms  inside a fast dialogue exchange
#   400ms      a normal beat (one manuscript line)
#   600ms      a joke landing — breathe, don't milk it
#   900ms      paragraph / topic shift
#   1400ms     scene break
# Rate starts at 0.94 and tightens through the exam. || marks a safe chunk split.

PART_A = """
Chapter One. The Kid in Room Four.<break time="1200ms"/>
Kade Mercer had been at Northline Alternative for forty-three school days, which was long enough to know that Room Four had three reliable clocks<break time="250ms"/> and none of them told time.<break time="800ms"/>
The first was the white plastic clock above the door. Its second hand twitched twice for every second, and stopped whenever the heater kicked on.<break time="700ms"/>
The second was Ms. Alvarez's coffee.<break time="400ms"/> Full meant first period.<break time="300ms"/> Half meant lunch was getting close.<break time="300ms"/> Empty meant nobody should ask her anything<break time="200ms"/> unless someone was bleeding.<break time="800ms"/>
The third was Darius Bell.<break time="800ms"/>
At exactly ten seventeen every morning, Darius decided he had endured enough education for one day, stood up, announced a destination that was obviously false, and walked out.<break time="600ms"/>
Today he made it to ten nineteen.<break time="800ms"/>
"Bathroom," Darius said.<break time="500ms"/>
Ms. Alvarez did not look up from the district tablet in her hands.<break time="450ms"/>
"You went fourteen minutes ago."<break time="400ms"/>
"Different bathroom."<break time="400ms"/>
"There is one bathroom."<break time="500ms"/>
Darius considered that.<break time="450ms"/>
"Then I forgot something in it."<break time="800ms"/>
||
Across the room, Kade kept his eyes on his own tablet and moved his thumb over the blank answer field without touching it.<break time="600ms"/>
The question read:<break time="600ms"/>
<prosody rate="90%">A cargo tram with a mass of eighteen thousand kilograms accelerates from rest to twelve meters per second over eight seconds. What average force is required?</prosody><break time="800ms"/>
It was a stupid question.<break time="600ms"/>
Not mathematically. Mathematically it was almost insulting.<break time="600ms"/>
The problem was the word<break time="200ms"/> required.<break time="700ms"/>
Required by what?<break time="700ms"/>
If the tram was on rails, friction mattered. If it was magnetic, the field geometry mattered. If twelve meters per second was measured relative to the track, fine<break time="200ms"/> but if the track itself was moving<break time="500ms"/>
Kade exhaled through his nose and typed the answer they wanted.<break time="600ms"/>
<prosody rate="90%">Twenty-seven thousand newtons.</prosody><break time="600ms"/>
Green check.<break time="500ms"/>
A cartoon rocket ship appeared and performed a tiny victory loop.<break time="600ms"/>
Kade hated the rocket ship.<break time="800ms"/>
"Mercer."<break time="500ms"/>
He looked up.<break time="450ms"/>
Ms. Alvarez pointed at Darius without moving anything but her eyes.<break time="500ms"/>
Darius had reached the door.<break time="500ms"/>
Kade looked at him.<break time="450ms"/>
"You know she has to log it if you leave again."<break time="500ms"/>
Darius's hand stopped on the push bar.<break time="450ms"/>
"Don't start."<break time="350ms"/>
"I didn't."<break time="350ms"/>
"You got that face."<break time="350ms"/>
"What face?"<break time="400ms"/>
"The one where you think you're smarter than everybody."<break time="500ms"/>
Kade leaned back in his chair.<break time="450ms"/>
"I don't have enough facial muscles for that."<break time="650ms"/>
A laugh escaped from somewhere behind him.<break time="500ms"/>
Darius did not smile.<break time="700ms"/>
||
He was sixteen, two inches taller than Kade, and built like the district had accidentally enrolled a linebacker in remedial geometry. He had been suspended from Canyon Ridge High after putting another kid through the glass panel beside a classroom door. The other kid needed eleven stitches.<break time="600ms"/>
Darius needed none.<break time="700ms"/>
Northline had taught Kade that none of those facts meant what people assumed they meant.<break time="800ms"/>
"I'm leaving," Darius said.<break time="400ms"/>
"Okay."<break time="350ms"/>
"You gonna stop me?"<break time="350ms"/>
"No."<break time="550ms"/>
That irritated him more.<break time="600ms"/>
Kade turned his tablet around just enough for Darius to see the red banner in the upper corner.<break time="600ms"/>
<prosody rate="88%">Attendance contract.<break time="250ms"/> Four of five unexcused exits.</prosody><break time="800ms"/>
Darius stared at it.<break time="500ms"/>
"One more," Kade said, "and Russell sends you back to review."<break time="400ms"/>
"So?"<break time="350ms"/>
"So your review is Friday."<break time="600ms"/>
Darius's jaw tightened.<break time="600ms"/>
Kade knew about Friday because Darius had spent most of the previous afternoon pretending not to care whether his mother could get off work for the meeting.<break time="700ms"/>
"If they push it another week," Kade said, "your mom misses another shift for nothing."<break time="600ms"/>
Darius looked toward Ms. Alvarez.<break time="500ms"/>
She was studying her tablet with the intense concentration of someone who had absolutely not heard the conversation.<break time="700ms"/>
"Sit down," Kade said. "Walk out at lunch and call it rebellion."<break time="650ms"/>
Darius stared at him for another two seconds.<break time="500ms"/>
Then he came back to his chair.<break time="600ms"/>
"Still hate you," he muttered.<break time="400ms"/>
"I know."<break time="700ms"/>
Ms. Alvarez lifted her coffee and drank.<break time="500ms"/>
Still half full.<break time="400ms"/>
Not lunch yet.<break time="1200ms"/>
||
Northline Alternative occupied an old county records building between a tire warehouse and a self-storage facility. Someone had painted the exterior blue three years earlier, but the desert sun had bleached the south wall to a color best described as disappointed gray.<break time="700ms"/>
The district website called it a personalized transitional learning campus.<break time="500ms"/>
Students called it Northline.<break time="500ms"/>
Parents called it whatever they needed to call it when relatives asked where their kid went to school now.<break time="800ms"/>
There were forty-two students enrolled, divided among six classrooms. Some had been expelled. Some had been arrested. Some had stopped showing up at regular school until the district stopped pretending they would. A few had panic disorders, complicated families, pregnancies, probation officers, jobs, addictions, or combinations of all six.<break time="700ms"/>
Northline did not have a mascot.<break time="600ms"/>
It had a metal detector, two social workers, one security officer who spent most afternoons fixing bicycles, and a vending machine that occasionally dispensed three bags of pretzels for the price of one.<break time="600ms"/>
Nobody knew why.<break time="500ms"/>
Darius believed the machine respected him.<break time="900ms"/>
Kade had none of the obvious reasons for being there.<break time="600ms"/>
That was, according to Vice Principal Russell, part of his problem.<break time="800ms"/>
At seventeen, Kade had collected three suspensions, two school transfers, a semester of failed classes he could have passed, and enough teacher comments to assemble a personality entirely from administrative adjectives.<break time="800ms"/>
<prosody rate="90%">Bright but inconsistent.<break time="450ms"/> Argumentative.<break time="450ms"/> Fails to demonstrate appropriate investment.<break time="450ms"/> Challenges authority.<break time="450ms"/> Does not utilize available opportunities.</prosody><break time="900ms"/>
His favorite came from ninth grade.<break time="600ms"/>
<prosody rate="90%">Kade often appears disengaged even when he understands the material.</prosody><break time="800ms"/>
As if understanding it should have made pretending to enjoy it easier.<break time="800ms"/>
He had read the whole file once while Russell was out of the office.<break time="600ms"/>
Not hacked it.<break time="500ms"/>
That was an important distinction.<break time="700ms"/>
Russell had left the file open on his desk while he went to make a phone call, which in Kade's opinion transformed unauthorized access into poor information security.<break time="700ms"/>
Ms. Alvarez disagreed.<break time="500ms"/>
They had argued about that for eleven minutes.<break time="500ms"/>
Kade had enjoyed the argument.<break time="450ms"/>
She had not.<break time="500ms"/>
Probably.<break time="1200ms"/>
"""
