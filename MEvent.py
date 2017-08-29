from copy import deepcopy
from MusEciDataStructures import INST, Par, Music, Part
from BasicOperations import dur, mMap

# =================================================================
# EVENT-STYLE REPRESENTATION
# Euterpea features an event-based representation of music called
# MEvent. Conversion from Music to MEvent requires processing of
# certain modifiers, such as Tempo.
# =================================================================

def applyTempo(x, tempo=1.0):
    """
    applyTempo copies its input and interprets its Tempo modifiers. This
    scales durations in the tree and removes Modify nodes for Tempo. The
    original input structure, however, is left unchanged.
    :param x:
    :param tempo:
    :return:
    """
    y = deepcopy(x)
    y = applyTempoInPlace(y, tempo)
    return y


def applyTempoInPlace(x, tempo=1.0):
    """
    applyTempoInPlace performs in-place interpretation of Tempo modifiers.
    However, it still has to be used as: foo = applyTempoInPace(foo)
    :param x:
    :param tempo:
    :return:
    """
    if (x.__class__.__name__ == 'Music'):
        #x.tree = applyTempo(x.tree, 120/x.bpm)
        #return x
        newTrees = []
        for t in x.trees:
            newTrees.append(applyTempo(t))
        x.trees = newTrees
        x.bpm = 120
        return x
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        x.dur = x.dur / tempo
        if not(x.onset is None):
            x.onset = x.onset / tempo
        return x
    elif (x.__class__.__name__ == 'Par' or x.__class__.__name__ == 'Seq'):
        newTrees = []
        for t in x.trees:
            newTrees.append(applyTempo(t))
        x.trees = newTrees
        return x
    elif (x.__class__.__name__ == 'Part'): # formerly Modify
        #if (x.mod.__class__.__name__ == 'Tempo'):
        #    x.tree = applyTempo(x.tree, x.mod.value)
        #    return x.tree
        #else:
        x.tree = applyTempo(x.tree, tempo)
        return x
    else:
        raise Exception("Unrecognized musical structure: "+str(x))


class MEvent:
    """
    MEvent is a fairly direct representation of Haskell Euterpea's MEvent type,
    which is for event-style reasoning much like a piano roll representation.
    eTime is absolute time for a tempo of 120bpm. So, 0.25 is a quarter note at
    128bpm. The patch field should be a patch number, like the patch field of
    the Instrument class.
    """
    def __init__(self, eTime, pitch, dur, vol=100, patch=(-1, INST)):
        self.eTime = eTime
        self.pitch = pitch
        self.dur = dur
        self.vol = vol
        self.patch = patch

    def __str__(self):
        return "MEvent({0}, {1}, {2}, {3})".format(str(self.eTime), str(self.pitch), str(self.dur), str(self.patch))

    def __repr__(self):
        return str(self)


def musicToMEvents(musicVal, currentTime=0, currentInstrument=(-1,INST)): # TO-DO: finish onset handling
    """
    The musicToMEvents function converts a tree of Notes and Rests into an
    event structure.
    :param x:
    :param currentTime:
    :param currentInstrument:
    :return:
    """
    x = deepcopy(musicVal)
    x.forceMIDICompatible()
    if (x.__class__.__name__ == 'Music'):
        #y = applyTempo(x) # interpret all tempo scaling factors before continuing
        #return musicToMEvents(y.tree, 0, (-1,INST))
        evs = []
        for t in x.trees:
            evs = evs + musicToMEvents(t, currentTime, currentInstrument)
        return sorted(evs, key=lambda e: e.eTime) # need to sort events by onset
    elif (x.__class__.__name__ == 'Note'):
        if x.dur > 0: # one note = one event as long as the duration is positive
            if (x.onset==None):
                return [MEvent(currentTime, x.pitch, x.dur, x.vol, currentInstrument)] # relative placement used if no onset
            else:
                return [MEvent(x.onset, x.pitch, x.dur, x.vol, currentInstrument)] # onset used if it exists
        else: # when duration is <0, there should be no event.
            return []
    elif (x.__class__.__name__ == 'Rest'):
        return [] # rests don't contribute to an event representation
    elif (x.__class__.__name__ == 'Seq'):
        evs = []
        nextCurrentTime = currentTime
        for t in x.trees:
            evs = evs + musicToMEvents(t, nextCurrentTime, currentInstrument)
            nextCurrentTime = nextCurrentTime + dur(t)
        #return evs # events can be concatenated, doesn't require sorting
        return sorted(evs, key=lambda e: e.eTime)  # with Note onsets allowed, need to sort events by onset to be safe
    elif isinstance(x, Par):
        evs = []
        for t in x.trees:
            evs = evs + musicToMEvents(t, currentTime, currentInstrument)
        return sorted(evs, key=lambda e: e.eTime) # need to sort events by onset
    elif (x.__class__.__name__ == 'Part'): # formerly Modify
        #if (x.mod.__class__.__name__ == 'Tempo'):
        #    y = applyTempo(x)
        #    return musicToMEvents(y, currentTime, currentInstrument)
        #elif (x.mod.__class__.__name__ == 'Instrument'):
        if x.instrument is None:
            return musicToMEvents(x.tree, currentTime, (-1, INST))  # formerly x.mod
        else:
            return musicToMEvents(x.tree, currentTime, x.instrument.patch)  # formerly x.mod
    else:
        raise Exception("Unrecognized musical structure: "+str(x))

def musicToMEventByPart(musicVal, currentTime=0):
    if isinstance(musicVal, Music):
        vals = list()
        for t in musicVal.trees:
            vals.append(musicToMEvents(t, currentTime))
        return vals
    else:
        return musicToMEvents(musicVal, currentTime)
