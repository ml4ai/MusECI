# Testing select statements

from MusECI.MusEciOperations import *
from MusECI.BasicOperations import line, deriveOnsets
from MusECI.MusEciDataStructures import *
from MusECI.Shorthands import *
from MusECI.MidiWriter import musicToMidi
from MusECI.MusicPlayer import MusicPlayer
import pygame as pm
import MusECI.MEvent as me
from MusECI.Select import *

v = Seq([Note(40), Note(60)])
deriveOnsets(v)
target = Repeat(2).apply(v)
q1 = Note(lambda p: p<70)
q2 = Note(lambda p: p<50)
q3 = Note(lambda p: p<10)
q4 = deepcopy(v)
basic.removeOnsets(q4)


x = select(q1, target) # should find 4 notes
print(str(len(x))+" things found: "+str(x))
x = select(q2, target) # should find 2 notes
print(str(len(x))+" things found: "+str(x))
x = select(q3, target) # should find nothing
print(str(len(x))+" things found: "+str(x))
x = select(q4, target) # should find two seqs
print(str(len(x))+" things found: "+str(x))