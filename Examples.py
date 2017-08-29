'''
Some examples of using the structures in MusECI to create music.
'''

import BasicOperations as basic
from MusEciDataStructures import *
from MusEciOperations import *
from MidiWriter import musicToMidi
from copy import deepcopy

# Twinkle Twinkle Little Star
twinkleA = Seq([Note(60, QN), Note(60, QN), Note(67,QN), Note(67, QN), Note(69,QN), Note(69, QN), Note(67,HN)])
twinkleB = Seq([Note(65, QN), Note(65, QN), Note(64,QN), Note(64, QN), Note(62,QN), Note(62, QN), Note(60,HN)])
twinkleC = Seq([Note(67, QN), Note(67, QN), Note(65,QN), Note(65, QN), Note(64,QN), Note(64, QN), Note(62,HN)])
# note: using deriveOnsets is optional
twinkle = Music([Part(CombineSeq().apply([twinkleA, twinkleB, twinkleC, twinkleC, twinkleA, twinkleB]))])
musicToMidi("twinkle.mid", twinkle)

# The motifs used in "Blue Lambda" (see http://donyaquick.com/interesting-music-in-four-lines-of-code/)
# Note: they must be more verbose here for two reasons: handling of onsets and the fact that Euterpea's Transpose
# node interacts with inversion in a strange way that MusECI's features do not.

x1 = Seq([Note(60, EN), Note(67, EN), Note(72,EN), Note(79, EN)])
basic.deriveOnsets(x1)
musicToMidi("x1.mid", Music([Part(x1)]))
x2 = CombineSeq().apply([x1, Transpose(3).apply(x1)])
musicToMidi("x2.mid", Music([Part(x2)]))
x3 = CombineSeq().apply([x2, x2, Invert().apply(x1), Transpose(3).apply(Invert().apply(x1)), Retrograde().apply(x2)])
musicToMidi("x3.mid", Music([Part(x3)]))
x3b = deepcopy(x3)
basic.scaleDurations(x3b, 1.5)
basic.scaleOnsets(x3b, 1.5)
x4a = CombineSeq().apply([x3]*6)
x4b = CombineSeq().apply([x3b]*4)
x4 = Music([Part(x4a), Part(x4b)])
print(x4)
musicToMidi("x4a.mid", Music([Part(x4a)]))
musicToMidi("x4b.mid", Music([Part(x4b)]))
musicToMidi("x4.mid", x4)
