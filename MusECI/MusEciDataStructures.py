# ===============================================================================
# MusECI data structures
# An adaptation of PythonEuterpeaN's classes.
# ===============================================================================

from copy import deepcopy
from MusECI.GMInstruments import gmNames  # Bring in a bunch of GM instrument names
# from GMInstruments import gmNames
import math


class MusEciException(Exception):
    """
    For throwing errors
    """
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


# =================================================================
# DURATION CONSTANTS (EUTERPEAN)
# =================================================================

WN = 1.0        # whole note = one measure in 4/4
DHN = 0.75      # dotted half
HN = 0.5        # half note
DQN = 0.375     # dotted quarter
QN = 0.25       # quarter note
DEN = 0.1875    # dotted eighth
EN = 0.125      # eighth note
DSN = 0.09375   # dotted sixteenth
SN = 0.0625     # sixteenth note
DTN = 0.046875  # dotted thirtysecond
TN = 0.03125    # thirtysecond note


# =================================================================
# MUSICAL STRUCTURE REPRESENTATIONS
# Haskell Euterpea features a type called Music, that is polymorphic
# and has several constructors. In Python, these constructors are
# represented as different classes that can (but do not have to)
# fall under an umbrella Music class to store everything.
# =================================================================

class Note:
    '''
    A Euterpea Note has a pitch, duration, volume, and other possible parameters.
    (these other parameters are application-specific)

    UPDATE 03-Aug-2017: Notes have TWO possble temporal representations: (1) Euterpean time, where 0.25=QN and there
    is no handling of time signatures, and (2) MetricalValue objects that keep track of measures and beats as separate
    numbers. For example, MetricalValue(0,2) is the Euterpean value 0.75 (3 beats). This exists for both duration and
    onset values.
    '''
    # TODO?: store params?  Perhaps as python dictionary param: **params ?
    def __init__(self, pitch, dur=0.25, onset=None, vol=100, params=None):
        self.pitch = pitch
        self.dur = dur
        self.vol = vol
        self.onset = onset
        self.params = params

    def __str__(self):
        return 'Note' + str((self.pitch, self.dur, self.onset, self.vol))

    def __repr__(self):
        return str(self)

    def equals(self, musicVal):
        if musicVal.__class__.__name__ == "Note":
            if self.pitch == musicVal.pitch:
                if self.dur == musicVal.dur:
                    if self.vol == musicVal.vol:
                        if self.onset == musicVal.onset:
                            if self.params == musicVal.params:
                                return True
        return False

    def forcePitchNumber(self):
        '''
        Convert other representations of pitch to a MIDI pitch number.
        :return:
        '''
        if isinstance(self.pitch, tuple):
            pc = self.pitch[0]
            oct = self.pitch[1]
            if isinstance(pc, PitchClass):
                pc = pc.number
            elif not isinstance(pc, int):
                raise MusEciException("Invalid pitch class type.")

            self.pitch = oct * 12 + pc
        # elif self.pitch.__class__.__name__ == "Pitch":
        #    self.pitch = self.pitch.number
        elif isinstance(self.pitch, PitchNumber):   # PitchNumber, PitchClass, or Pitch
            self.pitch = self.pitch.toNumber()
        elif isinstance(self.pitch, int):
            pass    # ok
        else:
            raise MusEciException("Can't convert value to pitch number.")

    def forceMIDICompatible(self, meta=None):
        self.forcePitchNumber()
        if isinstance(self.dur, MetricalValue):
            self.dur = self.dur.toMIDICompatible(meta)
        else:
            pass
        if isinstance(self.onset, MetricalValue):
            self.onset = self.onset.toMIDICompatible(meta)
        else:
            pass


class Rest:
    '''
    A Euterpea Rest has just a duration. It's a temporal place-holder just like a
    rest on a paper score.

    UPDATE 03-Aug-2017: Rests have TWO possble temporal representations: (1) Euterpean beats, where 0.25=QN and there
    is no handling of time signatures, and (2) MetricalValue objects that keep track of measures and beats as separate
    numbers. For example, MetricalValue(0,2) is the Euterpean value 0.75 (3 beats). This exists for both duration and
    onset values.
    '''
    def __init__(self, dur=0.25, onset=None, params=None):
        self.dur = dur
        self.onset = onset  # TO-DO: fill in later
        self.params = params

    def forceMIDICompatible(self, meta=None):
        if isinstance(self.dur, MetricalValue):
            self.dur = self.dur.toMIDICompatible(meta)
        else:
            pass
        if isinstance(self.onset, MetricalValue):
            self.onset = self.onset.toMIDICompatible(meta)
        else:
            pass

    def __str__(self):
        return 'Rest(' + str(self.dur) + ',' + str(self.onset) + ')'

    def equals(self, musicVal):
        if musicVal.__class__.__name__ == "Rest":
            if self.dur == musicVal.dur or musicVal.dur:
                if self.onset == musicVal.onset or musicVal.onset:
                    if self.params == musicVal.params == musicVal.params:
                        return True
        return False

    def __repr__(self):
        return str(self)


class Harmony:
    def __init__(self, root, kind, onset=None):
        self.root = root
        self.kind = kind
        self.onset = onset

    def __str__(self):
        return "Harmony({0}, {1}, {2})".format(self.root, self.kind, self.onset)

    def __repr__(self):
        return str(self)

    def forceMIDICompatible(selfself, meta):
        raise MusEciException("forceMIDICompatible not yet implemented for Harmoy objects")


class Mode:
    CHROMATIC = "Chromatic"
    MAJOR = "Major"
    MINOR = "Minor"
    PENTATONIC_MAJOR = "Pentatonic Major"
    PENTATONIC_MINOR = "Pentatonic Minor"
    CHROMATIC_SCALE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
    MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
    PENTATONIC_MAJOR_SCALE = [0, 2, 4, 7, 9]
    PENTATONIC_MINOR_SCALE = [0, 3, 5, 7, 10]
    scaleMap = {MAJOR:MAJOR_SCALE, MINOR:MINOR_SCALE, PENTATONIC_MAJOR:PENTATONIC_MAJOR_SCALE,
                PENTATONIC_MINOR:PENTATONIC_MINOR_SCALE, CHROMATIC:CHROMATIC_SCALE}

    def deriveScale(root, modeName):
        baseScale = Mode.scaleMap[modeName]
        return [x + root for x in baseScale]


class Key:
    def __init__(self, root, modeName, onset=None):
        self.rootPC = root
        self.modeName = modeName
        self.scale = Mode.deriveScale(root.number, modeName)
        self.onset = onset
        self.keySig = KeySig(0)
        if self.modeName == Mode.MAJOR:
            # derive key signature - TO-DO
            pass
        elif self.modeName == Mode.MINOR:
            # derive key signature - TO-DO
            pass

    def __str__(self):
        return "Key({0}, {1}, {2})".format(self.root, self.modeName, self.onset)

    def __repr__(self):
        return str(self)


'''
def intersperse(iterable, delimiter):
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimiter
        yield x
'''


class Seq:
    """
    Seq is similar to Haskell Euterpexa's (:+:) operator. It composes n
    musical objects in sequence, or left to right in trees.
    """
    def __init__(self, trees=[], params=None, inPlace=False):
        self.trees = handleInPlace(trees, inPlace)
        self.params = params

    def __str__(self):
        return 'Seq(' + str(self.trees) + ')'

    def __repr__(self):
        return str(self)

    def forceMIDICompatible(self, meta=None):
        for t in self.trees:
            t.forceMIDICompatible(meta)

    def equals(self, musicVal):
        if isinstance(musicVal, Seq):
            if musicVal.params == self.params:
                if len(musicVal.trees) == len(self.trees):
                    for i in range(0, len(self.trees)):
                        if not(self.trees[i].equals(musicVal.trees[i])):
                            return False
                    return True
        return False


class Par:  # For composing two things in parallel
    """
    Par is similar to Haskell Euterpea's (:=:) operator. It composes n
    musical objects in parallel (all at the same starting time).
    """
    def __init__(self, trees=[], params=None, inPlace=False):
        self.trees = handleInPlace(trees, inPlace)
        self.params = params

    def __str__(self):
        return 'Par(' + str(self.trees) + ')'

    def __repr__(self):
        return str(self)

    def forceMIDICompatible(self, meta=None):
        for t in self.trees:
            t.forceMIDICompatible(meta)

    def equals(self, musicVal):
        if isinstance(musicVal, Seq):
            if musicVal.params == self.params:
                if len(musicVal.trees) == len(self.trees):
                    for i in range(0, len(self.trees)):
                        if not(self.trees[i].equals(musicVal.trees[i])):
                            return False
                    return True
        return False


class Chord(Par):
    def __init__(self, notes, kind=None, params=None):
        # super(Chord, self).__init__(trees=notes, params=params)
        # FIXME: need to set trees in the Par() super class
        self.trees = notes  # would like to see that this is EITHER a harmony object or a collection of real notes
        self.kind = kind    # Not being used for anything within MusECI; seems potentially redundant with Harmony objects

    def forceMIDICompatible(self, meta=None):
        for t in self.trees:
            t.forceMIDICompatible(meta)

    def __str__(self):
        return "Chord(Type: {0}, Notes: {1})".format(self.kind, self.trees)

    def __repr__(self):
        return str(self)


class Music(Par):
    """
    A piece of music consists of a tree of musical structures interpreted within
    a particular collection of global meta information like tempo and key events.
    """
    def __init__(self, trees, meta=None, params=None, inPlace=False):
        self.trees = handleInPlace(trees, inPlace)
        self.meta = meta    # meta info for context like tempo changes, key signature changes, etc.
        self.params = params
        self.inPlace = inPlace

    def __str__(self):
        return 'Music(' + str(self.trees) + ', ' + str(self.meta)+')'

    def __repr__(self):
        return str(self)

    def forceMIDICompatible(self):  # no meta argument
        for t in self.trees:
            t.forceMIDICompatible(self.meta)

    def addMeta(self, metaItem):    # meta info should be stored in temporally sorted order
        self.meta.append(metaItem)
        self.meta = sorted(self.meta, key=lambda e: e.onset)


class LeadSheetMusic(Music):
    def __init__(self, trees, meta=None, params=None, inPlace=False):
        super().__init__(trees, meta=meta, params=params, inPlace=inPlace)

    def __str__(self):
        return 'LeadSheetMusic(' + str(self.trees) + ', ' + str(self.meta)+')'

    def __repr__(self):
        return str(self)


class Part(object):     # Part is not a Par for most instruments

    def __init__(self, component, instrument=None, params=None):    # vol removed, see below
        # super(Part, self).__init__(trees=components, params=params)
        self.tree = component   # part should hold just one thing
        self.instrument = instrument

    def forceMIDICompatible(self, meta=None):
        #self.tree.forceMIDICompatible(meta) # todo: fix this later
        self.tree.forceMIDICompatible()

    def __str__(self):
        return "Part(Instrument: {0}, {1})".format(self.instrument, self.tree)

    def __repr__(self):
        return str(self)


# class Modify:
#     """
#     Modify is equivalent to Haskell Euterpea's Modify constructor and allows
#     alterations to a musical tree.  Which modifiers are allowed are application
#     specific.
#     """
#     def __init__(self, modifier, tree, params=None, inPlace = False):
#         self.mod = handleInPlace(modifier, inPlace)
#         self.tree = handleInPlace(tree, inPlace)
#
#     def __str__(self):
#         return 'Mod(' + str(self.mod) + ', ' + str(self.tree)+')'
#
#     def __repr__(self):
#         return str(self)

class Tempo:
    """
    Altered from Euterpea definition: now uses bpm instead of a factor of 120bpm and stores onset.
    """
    def __init__(self, bpm, onset=0):
        self.bpm = bpm
        self.onset = onset

    def __str__(self):
        return 'Tempo(' + str(self.bpm) + ')'

    def __repr__(self):
        return str(self)


# Constants for instrument creation
PERC = True
INST = False


class Instrument:
    """
    An Instrument class to be used with the Modify class.
    """
    def __init__(self, value, itype=False):
        if isinstance(value, int):
            self.patch = (value, itype)
            self.name = gmName(self.patch)  # need to update this - should look up from patch
        elif isinstance(value, str):
            self.name = value
            if self.name == "DRUMS":
                self.patch = (0, True)
            else:
                self.patch = (gmNames.index(self.name), itype)
        else:
            print(("Unrecognized Instrument value: ", value))
            self.value = ""
            self.patch = (0, False)

    def __str__(self):
        return self.name + '(' + str(self.patch) + ')'

    def __repr__(self):
        return str(self)


def gmName(patch):
    if patch[0] < 0 or patch[0] > 127:
        return "NO_INSTRUMENT"
    elif patch[1]:
        return "DRUMS"
    else:
        return gmNames[patch[0]]


def handleInPlace(obj, inPlace):
    if inPlace:
        return obj
    else:
        return deepcopy(obj)

# ============================================================
# New things for TRIPS compatibility


class Accidental:
    sharp = 'sharp'
    flat = 'flat'
    double_sharp = 'double_sharp'
    double_flat = 'double_flat'
    natural = 'natural'
    halfsteps = {sharp: 1, flat: -1, double_sharp: 2, double_flat: -2, natural: 0}


def acShortStr(accidental):
    if accidental == 'sharp':
        return 's'
    elif accidental == 'flat':
        return 'f'
    elif accidental == 'double_sharp':
        return 'ss'
    elif accidental == 'double_flat':
        return 'ff'
    elif accidental == 'natural':
        return 'n'
    else:
        return ''


class Letter:
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'
    pcnums = {C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11}


def pcResolve(letter, accidental):
    letterNum = Letter.pcnums[letter]
    if accidental == Accidental.sharp:
        letterNum += 1
    elif accidental == Accidental.double_sharp:
        letterNum += 2
    elif accidental == Accidental.flat:
        letterNum -= 1
    elif accidental == Accidental.double_flat:
        letterNum -= 2
    return letterNum


def pitchResolve(letter, accidental, octave):
    pcNum = pcResolve(letter, accidental)
    return octave * 12 + pcNum


class PitchNumber(object):
    def __init__(self, number):
        self.number = number

    def toNumber(self):
        return self.number


class PitchClass(PitchNumber):
    def __init__(self, number=None, letter=None, accidental=None):
        self.letter = letter
        self.accidental = accidental
        self.number = number
        if (number is None and letter is not None):
            pcResolve(letter, accidental)   # NEEDS TO HANDLE RETURN VALUE

    def __repr__(self):
        acStr = ''
        if self.accidental is not None:
            acStr = acShortStr(self.accidental)
        return str(self.letter)+acStr

    def __str__(self):
        return repr(self)

    def setNumber(self, number, keyContext=None):
        self.number = number
        # to-do: derive accidental

    def setLetter(self, letter, accidental=None):
        self.letter = letter
        self.accidental = accidental
        self.number = None  # to-do: derive number automatically

    def toNumber(self):
        return self.number


class Pitch(PitchNumber):
    def __init__(self, number=None, pitchClass=None, octave=None, keyContext=None):
        self.pitchClass = pitchClass
        # NEED TO STORE OCTAVE
        self.number = number
        if (number is None):
            pass    # to-do: derive the number from the other data members
        elif (number is not None):
            pass    # to-do: derive other info if possible

    def __repr__(self):
        return '('+str(self.pitchClass)+','+str(self.octave)+')'

    def __str__(self):
        return repr(self)

    def setNumber(self, number, keyContext=None):
        self.number = number
        # to-do: derive pitch class and octave info

    def setPitchClass(self, pitchClass, octave=None):
        self.pitchClass = pitchClass
        if octave is not None:
            self.octave = octave
        if self.octave is None:
            self.number = None
        else:
            self.number = self.octave * 12 + self.pitchClass.number

    def setOctave(self, octave):
        self.octave = octave
        # to-do: derive pitch number

    def toNumber(self):
        return self.number


def pcLetterToNumberExt(letter, accidental=None):
    '''
    Convert a pitch class letter and accidental to the range -2 to 14. With this representation,
    C double-flat will become -2. This is useful for preserving octave information in some siuations.
    :param letter:
    :param accidental:
    :return:
    '''
    baseNum = Letter.pcnums[letter]
    adjustment = 0
    if (accidental is not None):
        adjustment = Accidental.halfsteps[accidental]
    return (baseNum+adjustment)


def pcLetterToNumber(letter, accidental=None):
    '''
    Convert a pitch class letter and accidental to the range 0 to 11.
    :param letter:
    :param accidental:
    :return:
    '''
    return pcLetterToNumberExt(letter, accidental) % 12


enHarmEqsExt = {
    0: [PitchClass(0, 'C', None), PitchClass(0, 'C', 'natural'), PitchClass(0, 'D', 'double_flat'), PitchClass(13, 'B', 'sharp')],  # 0
    1: [PitchClass(1, 'C', 'sharp'), PitchClass(1, 'D', 'flat'), PitchClass(13, 'B', 'double_sharp')],  # 1
    2: [PitchClass(2, 'D', None), PitchClass(2, 'D', 'natural'), PitchClass(2, 'E', 'double_flat'), PitchClass(2, 'C', 'double_sharp')],    # 2
    3: [PitchClass(3, 'D', 'sharp'), PitchClass(3, 'E', 'flat'), PitchClass(2, 'F', 'double_flat')],    # 3
    4: [PitchClass(4, 'E', None), PitchClass(4, 'E', 'natural'), PitchClass(4, 'F', 'flat')],   # 4
    5: [PitchClass(5, 'F', None), PitchClass(5, 'F', 'natural'), PitchClass(5, 'E', 'sharp')],  # 5
    6: [PitchClass(6, 'F', 'sharp'), PitchClass(6, 'G', 'flat')],   # 6
    7: [PitchClass(7, 'G', None), PitchClass(7, 'G', 'natural'), PitchClass(7, 'A', 'double_flat'), PitchClass(7, 'F', 'double_sharp')],    # 7
    8: [PitchClass(8, 'G', 'sharp'), PitchClass(8, 'A', 'flat')],   # 8
    9: [PitchClass(9, 'A', None), PitchClass(9, 'A', 'natural'), PitchClass(9, 'B', 'double_flat'), PitchClass(9, 'G', 'double_sharp')],    # 9
    10: [PitchClass(10, 'A', 'sharp'), PitchClass(10, 'B', 'flat'), PitchClass(-2, 'C', 'double_flat')],    # 10
    11: [PitchClass(11, 'B', None), PitchClass(11, 'B', 'natural'), PitchClass(9, 'A', 'double_sharp'), PitchClass(-1, 'C', 'flat')],   # 11
}

enHarmEqs = {
    0: [PitchClass(0, 'C', None), PitchClass(0, 'C', 'natural'), PitchClass(0, 'D', 'double_flat'), PitchClass(0, 'B', 'sharp')],   # 0
    1: [PitchClass(1, 'C', 'sharp'), PitchClass(1, 'D', 'flat'), PitchClass(0, 'B', 'double_sharp')],   # 1
    2: [PitchClass(2, 'D', None), PitchClass(2, 'D', 'natural'), PitchClass(2, 'E', 'double_flat'), PitchClass(2, 'C', 'double_sharp')],    # 2
    3: [PitchClass(3, 'D', 'sharp'), PitchClass(3, 'E', 'flat'), PitchClass(2, 'F', 'double_flat')],    # 3
    4: [PitchClass(4, 'E', None), PitchClass(4, 'E', 'natural'), PitchClass(4, 'F', 'flat')],   # 4
    5: [PitchClass(5, 'F', None), PitchClass(5, 'F', 'natural'), PitchClass(5, 'E', 'sharp')],  # 5
    6: [PitchClass(6, 'F', 'sharp'), PitchClass(6, 'G', 'flat')],   # 6
    7: [PitchClass(7, 'G', None), PitchClass(7, 'G', 'natural'), PitchClass(7, 'A', 'double_flat'), PitchClass(7, 'F', 'double_sharp')],    # 7
    8: [PitchClass(8, 'G', 'sharp'), PitchClass(8, 'A', 'flat')],   # 8
    9: [PitchClass(9, 'A', None), PitchClass(9, 'A', 'natural'), PitchClass(9, 'B', 'double_flat'), PitchClass(9, 'G', 'double_sharp')],    # 9
    10: [PitchClass(10, 'A', 'sharp'), PitchClass(10, 'B', 'flat'), PitchClass(10, 'C', 'double_flat')],    # 10
    11: [PitchClass(11, 'B', None), PitchClass(11, 'B', 'natural'), PitchClass(9, 'A', 'double_sharp'), PitchClass(9, 'C', 'flat')],    # 11
}


def numberToPCExt(number, keyContext=None):
    '''
    Convert a pitch class number to a PitchClass object with letter and accidental labelings. The
    key context will be used to try to guess the correct "spelling" of the pitch class number.
    :param number:
    :param keyContext:
    :return:
    '''
    eClass = enHarmEqsExt[number % 12]
    if keyContext is None:
        return eClass[0]
    else:
        raise Exception("Not implemented")  # TO-DO: choose based on mode membership


def numberToPC(number, keyContext=None):
    '''
    Convert a pitch class number to a PitchClass object with letter and accidental labelings. The
    key context will be used to try to guess the correct "spelling" of the pitch class number.
    :param number:
    :param keyContext:
    :return:
    '''
    pc = numberToPCExt(number, keyContext)
    pc.number = pc.number % 12
    return pc


def numberToPitch(number, keyContext=None):
    '''
    Convert a pitch number to a Pitch object with letter and accidental labelings. The key context
    will be used to try to guess the correct "spelling" of the pitch number.
    :param number:
    :param keyContext:
    :return:
    '''
    if keyContext is None:
        return KeySig(0).spell(number)
    else:
        return keyContext.keySig.spell(number)


def find(f, seq):
    """
    Return first item in sequence where f(item) == True.
    """
    for item in seq:
        if f(item):
            return item


class KeySig(object):
    '''
    Key signature class. A key signature can have EITHER flats or sharps, not both.
    No double flats or sharps are allowed in this implementation. This means that not all
    pitch classes and modes can be valid key signatures. For example, G-sharp-major is
    not a valid key because it contains a double sharp.
    '''
    def __init__(self, accidentals, kind=None, onset=0):
        flatOrderLetter = "BEADGCF"  # order in which flats get added to keysig (from 1 flat to 7 flats)
        sharpOrerLetter = "FCGDAEB"  # order in which sharps get added to keysig (from 1 sharp to 7 sharps)
        self.sharps = 0
        self.flats = 0
        self.kind = kind
        self.pcs = []
        self.onset = onset
        if (accidentals > 0):
            sharpOrderPCNum = [6, 1, 8, 3, 10, 5, 12]
            sharps = accidentals
            pcs = sharpOrderPCNum[:accidentals]
        else:
            flatOrderPCNum = [10, 3, 8, 1, 6, -1, 4]
            flats = accidentals
            pcs = flatOrderPCNum[:accidentals]
        self.root = accidentals

    def spell(self, pitchNumber):
        pc = pitchNumber % 12
        octave = math.floor(pitchNumber / 12)
        newPC = pc
        newOct = octave
        if (pc in self.pcs and self.accidentals > 0):   # sharp case
            return find(lambda x: x.accidental == "sharp", enHarmEqs[pc])
        elif (pc in self.pcs and self.accidentals < 0):     # flat case
            return find(lambda x: x.accidental == "flat", enHarmEqs[pc])
        else:
            newPC = enHarmEqs[pc]
        return Pitch(pitchNumber, newPC, newOct)


class Quality(object):
    MAJ = "Maj"     # major
    MIN = "Min"     # minor
    DIMI = "Dim"    # diminished
    AUG = "Aug"     # augmented
    DOM = "Dom"     # dominant
    HALFDIM = "Half-diminished"
    SUS4 = "Sus4"
    MAJ6 = "Maj6"
    MIN6 = "Min6"
    MAJ7 = "Maj7"
    MIN7 = "Min7"
    AUG7 = "Aug7"
    DIM7 = "Dim7"
    MAJ9 = "Maj9"
    MIN9 = "Min9"
    DOM9 = "Dom9"
    MIN11 = "Min11"
    DOM13 = "Dom13"
    SUS2 = "Sus2"
    UNSET = "Unset"


def tempos(meta):
    if meta is None:
        return []
    else:
        return [elem for elem in meta if isinstance(elem, Tempo)]


def timeSigs(meta):
    if meta is None:
        return []
    else:
        return [elem for elem in meta if isinstance(elem, TimeSig)]


def keySigs(meta):
    if meta is None:
        return []
    else:
        return [elem for elem in meta if isinstance(elem, KeySig)]


class MetricalValue(object):
    def __init__(self, value1, value2):
        self.measure = 0
        self.beat = 0
        if isinstance(value1, Measure) and isinstance(value2, Beat):
            self.measure = value1
            self.beat = float(value2)
        elif isinstance(value1, int) and (isinstance(value2, float) or isinstance(value2, int)):
            self.measure = Measure(value1)
            self.beat = Beat(value2)
        else:
            raise MusEciException("Badly formed MetricalValue arguments: "+str(value1)+", "+str(value2))

    def fillMeasures(self, meta):
        ts = timeSigs(meta)
        tSig = TimeSig(4, 4)
        if len(ts) > 1:
            raise MusEciException("Music can only have one time signature currently.")
        elif len(ts) == 1:
            tSig = ts[0]
        beatsPerMeasure = tSig.numerator  # todo: need to fetch this from meta to do conversion appropriately
        newM, newB = divmod(self.beat, beatsPerMeasure)
        self.measure += newM    # need to add because meausres might not have been zero. Ex: 2 measures and 7 beats in 4/4
        self.beat = newB

    def toBeats(self, meta):
        if (self.measure.value > 0):
            ts = timeSigs(meta)
            tSig = TimeSig(4, 4)
            if len(ts) > 1:     # todo: handle additional time signature changes
                raise MusEciException("Music can only have one time signature currently.")
            elif len(ts) == 1:
                tSig = ts[0]
            beatsPerMeasure = tSig.numerator
            self.beat.value = self.measure.value*beatsPerMeasure + self.beat.value
            self.measure.value = 0

    def toMIDICompatible(self, meta):
        self.toBeats(meta)
        return self.beat.value / 4


class Measure(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.number)

    def __str__(self):
        return str(self.number)


class Beat(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


class Onset(MetricalValue):
    pass


class Duration(MetricalValue):
    pass


class TimeSig(object):
    def __init__(self, numerator, denominator, onset=None):
        self.numerator = 4
        self.denominator = 4
        self.onset = onset
        if numerator > 0 and denominator in [2, 4, 8]:
            self.numerator = numerator
            self.denominator = denominator
        else:
            raise MusEciException("Bad time signature: "+str(numerator)+"/"+str(denominator))

    def __str__(self):
        return str(self.numerator) + '/' + str(self.denominator)

    def __repr__(self):
        return str(self)


# =================================================================
# New stuff to deal with conditional logic in select statements


# class Conditional(object):  # Not using this - ended up using lambdas instead for beter versatility
#     def __init__(self, operation):
#         self.operation = operation
#
#     def __repr__(self):
#         return "Conditional"
#
#     def __str__(self):
#         return "Conditional"
#
#     def apply(self, value):
#         return self.operation(value)
