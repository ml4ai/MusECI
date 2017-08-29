# For testing the correctness of MusECI operations

from MusEciOperations import *
from BasicOperations import line, deriveOnsets
from MusEciDataStructures import *
from Shorthands import *
from MidiWriter import musicToMidi
from MusicPlayer import MusicPlayer
import pygame as pm
import MEvent as me
from Select import *

m = Seq([C(4,QN), D(4,QN), E(4,HN)])
print(m)
deriveOnsets(m)

op1 = Transpose(2)
op2 = Retrograde()
op3 = Invert()
op4 = Cleanup()

m1 = op1.apply(m)
m2 = op2.apply(m)
m3 = op1.apply(op2.apply(m))
m4 = op3.apply(m3)
m5 = applyInSequence([op1,op2,op3], m)

musicToMidi("m.mid", m)
musicToMidi("m1.mid", m1)
musicToMidi("m2.mid", m2)
musicToMidi("m3.mid", m3)
musicToMidi("m4.mid", m4)
musicToMidi("m5.mid", m5)
