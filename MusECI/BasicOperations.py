from copy import deepcopy
from MusECI.MusEciDataStructures import *
from random import *

# =================================================================
# OPERATIONS ON MUSICAL STRUCTURES
# Haskell Euterpea provides a number of basic operations on the
# Music type. Only a few of them are presented here.
# =================================================================

def removeDurs(musicVal):
    def stripDur(x): x.dur = None
    mMap(stripDur, musicVal)

def removeOnsets(musicVal):
    def stripOnset(x): x.onset = None
    mMap(stripOnset, musicVal)

def findBy(selectFun, x):
    retVals = []
    if selectFun(x):
        retVals.append(x)
    elif x.__class__.__name__ == "Seq" or isinstance(x, Par):
        for t in x.trees:
            newVals = findBy(selectFun, t)
            retVals = retVals+newVals
    elif x.__class__.__name__=="Note" or x.__class__.__name__=="Rest":
        if selectFun(x):
            retVals.append(x)
    elif x.__class__.__name__=="Part": # formerly Modify
        newVals = findBy(selectFun, x.tree)
        retVals = retVals+newVals
    return retVals

def minOnset(x):
    os = getOnsets(x)
    retVal = 0
    for o in os:
        if o==None:
            pass
        else:
            if o < retVal:
                retVal = o
    return retVal

def setDefaultOffset(x, defO):
    def oFun(x):
        if (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
            if (x.onset == None):
                x.onset = defO
    mMapAll(oFun, x)

def shiftOnsets(x, shiftAmt):
    def oFun(x):
        if (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
            if (x.onset != None):
                x.onset = x.onset + shiftAmt
    mMapAll(oFun, x)

def line(musicVals, correctOnsets=True):
    """
    The line function build a "melody" with Seq constructors
    out of a list of music substructures. Values are NOT copied.
    :param musicVals: a list of musical structures
    :return: the sequential composition of the input list
    """
    ms = deepcopy(musicVals)
    offset = 0
    if(correctOnsets):
        for m in ms:
            mdur = durOnset(m)
            shiftOnsets(m, offset)
        offset = offset + mdur
    return Seq(ms)

def par(musicVals): # Does NOT assign onsets by default
    """
    The chord function build a "chord" with Par constructors
    out of a list of music substructures. Values are NOT copied.
    :param musicVals: a list of music structures
    :return: the parallel composition of the input
    """
    ms = deepcopy(musicVals)
    return Par(ms)

def deriveOnsets(x, currentTime=0):
    #if (x.__class__.__name__ == 'Music'):
    #    deriveOnsets(x.tree, 0)
    if (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        if x.onset == None:
            x.onset = currentTime
    elif (x.__class__.__name__ == 'Seq'):
        ct = currentTime
        for t in x.trees:
            deriveOnsets(t, ct)
            ct = ct + dur(t)
    elif isinstance(x, Par):
        for t in x.trees:
            deriveOnsets(t, currentTime)
    elif (x.__class__.__name__ == 'Part'): # formerly Modify
        deriveOnsets(x.tree, currentTime)
    else:
        raise MusEciException("Unrecognized musical structure: " + str(x))

def getOnset(x): # We assume onsets are defined
    if x.__class__.__name__ == "Part": # formerly Modify
        return getOnset(x.tree)
    elif x.__class__.__name__=="Note" or x.__class__.__name__ == "Rest":
        return x.onset
    elif x.__class__.__name__=="Seq":
        return getOnset(x.trees[0]) # we assume structural correctness for Seq (first is earliest onset)
    elif isinstance(x, Par):
        return min(list(map(getOnsets, x.trees))) # can't really make the same assumption for Par
    else:
        raise MusEciException("Unrecognized musical structure: " + str(x))

def durOnset(x):  # WE ASSUME ALL ONSETS HAVE BEEN DERIVED (no mix of actual numbers and Nones allowed)
    minO = min(getOnsets(x))
    maxE = max(getEndTimes(x))
    return maxE - minO

def getOnsets(x): # UNTESTED
    def getter(val): return val.onset
    return mMapAllRet(getter, x)

def getEndTimes(x):# UNTESTED
    def getter(val): return (val.onset + val.dur)
    return mMapAllRet(getter, x)

def scaleOnsets(x, shiftAmt):
    def oFun(x):
        if (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
            if (x.onset != None):
                x.onset = x.onset * shiftAmt
    mMapAll(oFun, x)

def dur(x): # WILL NOT HANDLE ONSETS
    """
    Computes the duration of a music tree. Values are relative to the overall
    bpm for the entire tree, such that 0.25 is a quarter note.
    :param x: the music structure
    :return: the duration of x in whole notes (wn = 1.0)
    """
    if (x.__class__.__name__ == 'Music'):
        d = max(list(map(dur,x.trees)))
        return d * (120/x.bpm)
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        return x.dur
    elif (x.__class__.__name__ == 'Seq'):
        return sum(map(dur,x.trees)) # THIS IS NOT RIGHT FOR ONSETS
    elif isinstance(x, Par):
        return max(list(map(dur,x.trees)))
    elif (x.__class__.__name__ == 'Part'): # formerly Modify
        #if (x.mod.__class__.__name__ == 'Tempo'):
        #    d = dur(x.tree)
        #    return d / x.mod.value
        #else:
        return dur(x.tree)
    else:
        raise MusEciException("Unrecognized musical structure: " + str(x))


def line(musicVals): # Does NOT assign onsets by default.
    """
    The line function build a "melody" with Seq constructors
    out of a list of music substructures. Values are NOT copied.
    :param musicVals: a list of musical structures
    :return: the sequential composition of the input list
    """
    return Seq(musicVals)






def mMap(f, x):
    """
    The mMap function maps a function over the Notes in a Music value.
    :param f: Function to map over Notes
    :param x: the music structure to operate on
    :return: an in-place modification of the music structure
    """
    if (x.__class__.__name__ == 'Music'):
        for t in x.trees:
            mMap(f, t)
    elif (x.__class__.__name__ == 'Note'):
        f(x)
    elif (x.__class__.__name__ == 'Rest'):
        pass # nothing to do to a Rest
    elif (x.__class__.__name__ == 'Seq' or isinstance(x, Par)):
        for t in x.trees:
            mMap(f, t)
    elif (x.__class__.__name__ == 'Part'): # formerly Modify
        mMap(f, x.tree)
    else:
        raise MusEciException("Unrecognized musical structure: " + str(x))



def mMapAll(f, x):
    """
    The mMapDur function is not found in Haskell Euterpea but may prove useful.
    It maps a function over Notes and Rests and applies it to the entire musical
    structure. Note: the function MUST handle the constructors directly if using
    something other than dur.
    :param f: The function to apply to durations (v.dur for a Note or Rest)
    :param x: the music structure to traverse
    :return: an in-place altered version of the music structure
    """
    if (x.__class__.__name__ == 'Music'):
        for t in x.trees:
            mMapAll(f,t)
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        f(x)
    elif (x.__class__.__name__ == 'Seq' or isinstance(x, Par)):
        for t in x.trees:
            mMapAll(f,t)
    elif (x.__class__.__name__ == 'Part'): # formerly Modify
        mMapAll(f, x.tree)
    else:
        raise MusEciException("Unrecognized musical structure: " + str(x))

def mMapAllRet(f, x):
    """
    The mMapDur function is not found in Haskell Euterpea but may prove useful.
    It maps a function over Notes and Rests and applies it to the entire musical
    structure. Note: the function MUST handle the constructors directly if using
    something other than dur.
    :param f: The function to apply to durations (v.dur for a Note or Rest)
    :param x: the music structure to traverse
    :return: an in-place altered version of the music structure
    """
    if (x.__class__.__name__ == 'Music'):
        v = list()
        for t in x.trees:
            v += mMapAllRet(f,t)
            v += mMapAllRet(f,t)
        return v
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        return [f(x)]
    elif (x.__class__.__name__ == 'Seq' or isinstance(x, Par)):
        v = list()
        for t in x.trees:
            v += mMapAllRet(f,t)
            v += mMapAllRet(f,t)
        return v
    elif (x.__class__.__name__ == 'Part'):
        return mMapAllRet(f, x.tree)
    else:
        raise MusEciException("Unrecognized musical structure: " + str(x))


def transpose(x, amount):
    """
    transpose directly alters the Notes of the supplied structure.
    Each Note's pitch number has amount added to it.
    :param x:
    :param amount:
    :return:
    """
    def f(xNote): xNote.pitch = xNote.pitch+amount
    mMap(f, x)

# The following volume-related functions deviate slightly from
# Haskell Euterpea's methods of handling volume. This is because
# the volume is stored directly in the Note class in Python, which
# is not the case in Haskell Euterpea. Note: volumes are not
# guaranteed to be integers with scaleVolume. You sould use
# intVolume before converting to MIDI. You may wish to use
# scaleVolumeInt instead.

def setVolume(x, volume): # set everything to a constant volume
    def f(xNote): xNote.vol = volume
    mMap(f,x)

def scaleVolume(x, factor): # multiply all volumes by a factor
    def f(xNote): xNote.vol = xNote.vol * factor
    mMap (f,x)

def scaleVolumeInt(x, factor): # multiply but then round to an integer
    def f(xNote): xNote.vol = int(round(xNote.vol * factor))
    mMap (f,x)

def adjustVolume(x, amount): # add a constant amount to all volumes
    def f(xNote): xNote.vol = xNote.vol + amount
    mMap (f,x)

def reverseInPlace(x):
    """
    Reverse a musical structure in place (last note is first, etc.)
    :param x: the music structure to reverse.
    :return: the reversal of the input.
    """
    #if (x.__class__.__name__ == 'Music'):
    #    reverseInPlace(x.tree)
    if (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        pass # nothing to do
    elif (x.__class__.__name__ == 'Seq'):
        x.trees.reverse()
        for t in x.trees:
            reverseInPlace(t)
    elif (x.__class__.__name__ == 'Par' or x.__class__.__name__ == 'Music'):
        dMax = dur(x)
        newTrees = []
        for t in x.trees:
            newTrees.append(Seq[Rest(dMax - dur(t)), reverseInPlace(t)])
        x.trees = newTrees
    elif (x.__class__.__name__ == 'Part'):
        reverseInPlace(x.tree)
    else: raise MusEciException("Unrecognized musical structure: " + str(x))

def reverse(x): # DOES NOT HANDLE ONSETS
    x2 = deepcopy(x)
    reverseInPlace(x2)
    return x2

def reverseOnsetInPlace(x): # HANDLES ONSETS. Notes must store onsets. Rests may need to be cleared and redone.
    d = durOnset(x)
    reverseInPlace(x)
    def revOnset(aNote): aNote.onset = d - (aNote.onset + aNote.dur)
    mMapAll(revOnset, x)
    #deriveOnsets(x,0) # Might need to do this if rests are involved

def reverseOnset(x):
    x2 = deepcopy(x)
    reverseOnsetInPlace(x2)
    return x2

def reverseOnsetInPlaceWithin(x, startTime, endTime): # To reverse within a larger range.
    o = getOnset(x)
    d = durOnset(x)
    if (o==startTime and o+d==endTime):
        reverseOnsetInPlace(x)
    elif (o>startTime and o+d < endTime):
        reverseInPlace(x)
        def revOnset(aNote): aNote.onset = endTime - (aNote.onset - startTime + aNote.dur)
        mMapAll(revOnset, x)
        #deriveOnsets(x,0) # Might need to do this if rests are involved
    else:
        raise MusEciException("Selection must be a subset of the time span to be reversed.")

def reverseOnsetWithin(x, startTime, endTime):
    x2 = deepcopy(x)
    reverseOnsetInPlaceWithin(x2, startTime, endTime)
    return x2


def times(music, n): # TO-DO: ONSET HANDLING
    """
    Returns a new value that is n repetitions of the input musical structure.
    Deep copy is used, so there will be no shared references between the input
    and the output.
    :param music: the music structure to repeat
    :param n: how many times to repeat?
    :return: a new structure (so this should be called as a = times(b,n)
    """
    return Seq([music]*n)


def cut(x, amount): # Should not be affected by onset handling
    """
    Keeps only the first duration amount of a musical structure. The amount
    is in measures at the reference duration, which is 120bpm unless specified
    by the Music constructor. Note that this operation is messy - it can leave
    a lot of meaningless structure in place, with leaves occupied by Rest(0).
    :param x: the music value to alter
    :param amount: how many whole notes worth to take.
    :return: the furst amount of the music structure by time (whole note = 1.0)
    """
    #if (x.__class__.__name__ == 'Music'):
    #    cut(x.tree, amount)
    #    return x
    if (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        if amount <= x.dur:
            x.dur = amount
        return x
    elif (x.__class__.__name__ == 'Seq'):
        dLeft = amount
        newTree = []
        for t in x.trees:
            newTree.append(cut(t, dLeft))
            dLeft = max(0,dLeft - dur(t))
        x.trees = newTree
        return x
    elif isinstance(x, Par):
        newTrees = []
        for t in x.trees:
            newTrees.append(cut(t,amount))
        x.trees = newTrees
        return x
    elif (x.__class__.__name__ == 'Part'):
        #if (x.mod.__class__.__name__ == 'Tempo'):
        #    cut(x.tree, amount*x.mod.value)
        #else:
        cut(x.tree, amount)
        return x
    else: raise MusEciException("Unrecognized musical structure: " + str(x))


def remove(x, amount): # TO-DO: ONSET HANDLING (DO WE WANT IT TO NORMALIZE TO STARTING AT ZERO?)
    """
    The opposite of "cut," chopping away the first amount. Note that this
    operation is messy - it can leave a lot of meaningless structure in
    place, with leaves occupied by Rest(0).
    :param x: the music structure to alter
    :param amount: how much to cut off of the beginning?
    :return:
    """
    if amount<=0:
        return x # nothing to remove!
    #elif (x.__class__.__name__ == 'Music'):
    #    remove(x.tree, amount)
    #    return x
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        if amount >= x.dur:
            x.dur = 0
        if amount < x.dur:
            x.dur = x.dur - amount
        return x
    elif (x.__class__.__name__ == 'Seq'):
        dLeft = amount
        newTree = []
        for t in x.trees:
            d = dur(t)
            newTree.append(remove(t, dLeft))
            dLeft = max(0,dLeft - d)
        x.trees = newTree
        return x
    elif isinstance(x, Par):
        newTrees = []
        for t in x.trees:
            newTrees.append(remove(t,amount))
        x.trees = newTrees
        return x
    elif (x.__class__.__name__ == 'Part'):
        #if (x.mod.__class__.__name__ == 'Tempo'):
        #    remove(x.tree, amount*x.mod.value)
        #else:
        remove(x.tree, amount)
        return x
    else: raise MusEciException("Unrecognized musical structure: " + str(x))



# ======================== BEGIN UNTESTED ======================== #


def mFold(x, noteOp, restOp, seqOp, parOp, modOp): # Onsets can't reasonably be handled in this function. We are also unlikely to use it for anything.
    """
    The mFold operation traverses a music value with a series of operations
    for the various constructors. noteOp takes a Note, restOp takes a Rest,
    seqOp and parOp take the RESULTS of mFolding over their arguments, and
    modOp takes a modifier (x.mod) and the RESULT of mFolding over its
    tree (x.tree).
    :param x:
    :param noteOp:
    :param restOp:
    :param seqOp:
    :param parOp:
    :param modOp:
    :return:
    """
    #if (x.__class__.__name__ == 'Music'):
    #    return mFold(x.tree, noteOp, restOp, seqOp, parOp, modOp) # todo?: update modOp to something relevant to Part
    if (x.__class__.__name__ == 'Note'):
        return noteOp(x)
    elif (x.__class__.__name__ == 'Rest'):
        return restOp(x)
    elif (x.__class__.__name__ == 'Seq'):
        vals = [mFold(t, noteOp, restOp, seqOp, parOp, modOp) for t in x.trees]
        return seqOp(vals)
    elif isinstance(x, Par):
        vals = [mFold(t, noteOp, restOp, seqOp, parOp, modOp) for t in x.trees]
        return parOp(vals)
    elif (x.__class__.__name__ == 'Part'):
        val = mFold(x.tree, noteOp, restOp, seqOp, parOp, modOp)
        #return modOp(x.mod, val)
        return val
    else: raise MusEciException("Unrecognized musical structure: " + str(x))


def firstPitch(x): # TO-DO: ONSET HANDLING
    """
    The firstPitch function returns the first pitch in the Music value.
    None is returned if there are no notes. Preference is lef tand top.
    :param x:
    :return:
    """
    #if (x.__class__.__name__ == 'Music'):
    #    return firstPitch(x.tree)
    if (x.__class__.__name__ == 'Note'):
        return x.pitch
    elif (x.__class__.__name__ == 'Rest'):
        return None
    elif (x.__class__.__name__ == 'Seq' or isinstance(x, Par)):
        vals = list(map(firstPitch, x.trees))
        if len(vals) > 0:
            return vals[0]
        else:
            return -1
    elif (x.__class__.__name__ == 'Part'):
        return firstPitch(x.tree)
    else: raise MusEciException("Unrecognized musical structure: " + str(x))


def getPitches(m):
    """
    An application of mFold to extract all pitches in the music
    structure as a list.
    :param m:
    :return:
    """
    def fn(n): return [n.pitch]
    def fr(r): return []
    def fcat(a,b): return a+b
    def fm(m,t): return t
    return mFold(m, fn, fr, fcat, fcat, fm)


def invertAt(m, pitchRef):
    """
    Musical inversion around a reference pitch. Metrical structure
    is preserved; only pitches are altered.
    :param m:
    :param pitchRef:
    :return:
    """
    def f(aNote): aNote.pitch = 2 * pitchRef - aNote.pitch
    ret = mMap(f, m)
    return ret


def invert(m):
    """
    Musical inversion around the first pitch in a musical structure.
    :param m:
    :return:
    """
    p = firstPitch(m)
    ret = invertAt(m, p)
    return ret


def instrument(m, value):
    """
    Shorthand for setting an instrument.
    :param m:
    :param value:
    :return:
    """
    return Part(m, Instrument(value)) # Modify(Instrument(value), m)


def removeInstruments(x):
    """
    Remove Instrument modifiers from a musical structure
    :param x:
    :return:
    """
    def checkInstMod(x): # function to get rid of individual nodes
        if x.__class__.__name__ == 'Part':
            #if x.mod.__class__.__name__ == 'Instrument': return x.tree
            #else: return x
            return x.tree
        else: return x
    #if x.__class__.__name__ == 'Music':
    #    tNew = checkInstMod(x.tree)
     #   removeInstruments(x.tree)
    #    return x
    if x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest':
        return x
    elif x.__class__.__name__ == 'Seq' or isinstance(x, Par):
        newTrees = []
        for t in x.trees:
            newTrees.append(checkInstMod(x.left))
        x.trees = list(map(removeInstruments, newTrees))
        return x
    elif x.__class__.__name__ == 'Part':
        xNew = checkInstMod(x)
        return xNew
    else: raise MusEciException("Unrecognized musical structure: " + str(x))


def changeInstrument(m, value):
    x1 = instrument(value, x)
    x = removeInstruments(m)
    return x1


# Scale all durations in a music structure by the same amount.
def scaleDurations(m, factor):
    def f(x): x.dur = x.dur*factor
    x = mMapAll(f, m)
    return x

def scaleDursOnsets(m, factor): # Option for use with onsets
    def f(x):
        x.dur = x.dur * factor
        if (x.onset != None): x.onset * factor
    x = mMapAll(f,m)
    return x

# ======================== END UNTESTED ======================== #



# =============================================================================================
# Some extra supporting functions for compatibility with more pure vector/list
# representations of melodies and chords.


# Convert a pitch number to a single note. NO ONSET HANDLING (use deriveOnsets)
def pitchToNote(p, defDur=0.25, defVol=100):
    if p==None:
        return Rest(defDur)
    else:
        return Note(p, defDur, None, defVol)


# Convert a list of pitches to a melody using a default note duration. NO ONSET HANDLING (use deriveOnsets)
def pitchListToMusic(ps, defDur=0.25, defVol=100):
    ns = [pitchToNote(p, defDur, defVol) for p in ps]
    return line(ns)


# Synonym for consistency with some other naming schemes.  NO ONSET HANDLING (use deriveOnsets)
# This does the same thing as pitchListToMusic
def pitchListToMelody(ps, defDur=0.25, defVol=100):
    return pitchListToMusic(ps, defDur, defVol)

def pdPairsToMusic(pds, defVol=100): # NO ONSET HANDLING (use deriveOnsets)
    """
    Convert a list of pitch+duration pairs to a melody (a bunch of Notes in sequence).
    pdPair = pitch-duration pair
    :param pds: pairs of pitch and duration: [(p1,d1), (p2,d2), ...]
    :param defVol: default volume
    :return: music structure as a melody
    """
    ns = [Note(x[0], x[1], None, defVol) for x in pds]
    return line(ns)

def pdPairsToMelody(pds, defVol=100): # This is just a synonym for pdPairsToMusic - NO ONSET HANDLING
    return pdPairsToMusic(pds, defVol)

def pdPairsToChord(pds, defVol=100): # NO ONSET HANDLING
    """
    Convert a list of pitch+duration pairs to a chord (a bunch of Notes in parallel).
    NOTE: start times will be the same for all pitches, but end times will be based on
    the duration of the notes - so they may end at different times!
    pdPair = pitch-duration pair
    :param pds: pairs of pitch and duration: [(p1,d1), (p2,d2), ...]
    :param defVol: default volume
    :return: music structure as a chord
    """
    ns = [Note(x[0], x[1], None, defVol) for x in pds]
    return par(ns)


# Convert a list of pitches to a chord (a bunch of Notes in parallel). NO ONSET HANDLING (use deriveOnsets)
def pitchListToChord(ps, defDur=0.25, defVol=100):
    if ps == None:
        return Rest(defDur)
    else:
        ns = [Note(p, defDur, defVol) for p in ps]
        return par(ns)


# Convert a list of chords (a list of lists of pitches) to a music structure. NO ONSET HANDLING (use deriveOnsets)
def chordListToMusic(chords, defDur=0.25, defVol=100):
    cList = [pitchListToChord(x, defDur, defVol) for x in chords]
    return line(cList)


def removeZeros(x): # MAY NEED TO HANDLE ONSETS IN DURATION CALL
    #if (x.__class__.__name__ == 'Music'):
    #    x.tree = removeZeros(x.tree)
    #    return x
    if (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        return x # can't remove at this stage
    elif (x.__class__.__name__ == 'Seq' or isinstance(x, Par)):
        newTrees = []
        for t in x.trees:
            t2 = removeZeros(t)
            if dur(t2) > 0:
                newTrees.append(t2)
        x.trees = newTrees
        return x
    elif (x.__class__.__name__ == 'Part'):
        x.tree = removeZeros(x.tree)
        return x
    else:
        raise MusEciException("Unrecognized musical structure: " + str(x))

def removeZerosOnset(x):  # MAY NEED TO HANDLE ONSETS IN DURATION CALL
    #if (x.__class__.__name__ == 'Music'):
    #    x.tree = removeZerosOnset(x.tree)
    #    return x
    if (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        return x  # can't remove at this stage
    elif (x.__class__.__name__ == 'Seq' or isinstance(x, Par)):
        newTrees = []
        for t in x.trees:
            t2 = removeZerosOnset(t)
            if durOnset(t2) > 0:
                newTrees.append(t2)
        x.trees = newTrees
        return x
    elif (x.__class__.__name__ == 'Part'):
        x.tree = removeZerosOnset(x.tree)
        return x
    else:
        raise MusEciException("Unrecognized musical structure: " + str(x))

#=============================================================

def scaleTranspose1(pitchNum, halfsteps, scale):
    '''
    Transposes a single pitch within a scale by a certain number of halfsteps, if
    it is possible to do so. If it isn't, a different intervale +/-1 from the original
    is selected at random to match the scale. Note: this strategy only works with
    Major and Minor and would need reworking to be used with other scales like pentatonic.
    :param pitchNum:
    :param halfsteps:
    :param scale:
    :return:
    '''
    newPC = (halfsteps + pitchNum) % 12
    if newPC in scale:
        return pitchNum + halfsteps
    else:
        r = choice([-1,1])
        return pitchNum + halfsteps + r

def scaleTransposeM(music, halfsteps, scale):
    '''
    Transposes an entire music value using scaleTranspose1
    :param music:
    :param halfsteps:
    :param scale:
    :return:
    '''
    def notefun(x):
        newPNum = scaleTranspose1(x.pitch, halfsteps, scale)
        x.pitch = newPNum
    mMap(notefun, music)

def scaleInvertAt(m, pitchRef, scale):
    """
    Musical inversion around a reference pitch. Metrical structure
    is preserved; only pitches are altered.
    :param m:
    :param pitchRef:
    :return:
    """
    #def f(aNote): aNote.pitch = scaleTranspose1(0, 2 * pitchRef - aNote.pitch, scale)
    def f(aNote): aNote.pitch = scaleTranspose1(aNote.pitch, (2 * pitchRef) - (2 * aNote.pitch), scale)
    ret = mMap(f, m)
    return ret


def scaleInvert(m, scale):
    """
    Musical inversion around the first pitch in a musical structure.
    :param m:
    :return:
    """
    p = firstPitch(m)
    ret = scaleInvertAt(m, p, scale)
    return ret

def isNote(x): return x.__class__.__name__ == "Note"
def isRest(x): return x.__class__.__name__ == "Rest"

def stripRests(x):
    if x.__class__.__name__ == "Part":
        stripRests(x.tree)
    elif x.__class__.__name__ == "Seq" or isinstance(x, Par):
        for t in x.trees: # recursively strip rests from subtrees
            stripRests(t)
        okTrees = [x for x in x.trees if not (isRest(x))] # remove any rests appearing at this level
        x.trees = okTrees
    else:
        pass


def fillRests(x):
    if x.__class__.__name__ == "Part:":
        fillRests(x.tree)
    elif x.__class__.__name__ == "Seq": # Note: we assume a non-empty tree here! Probably need to update later
        newTrees = list()
        currOnset = getOnset(x)
        for t in x.trees:
            o = getOnset(t)
            if o > currOnset:
                newTrees.append(Rest(o - currOnset, currOnset))
            newTrees.append(t)
    elif isinstance(x, Par):
        for t in x.trees:
            fillRests(t) # Not sure how best to handle this. Do we necessarily want Rests within a Par?
    else:
        pass # don't need to alter existing notes and rests


# for generalizing transpose, invert etc. to lists of potentially disconnected items.

def inPlaceMusicOp(op, x):
    if hasattr(x, '__iter__'):
        for v in x:
            op(v)
    else:
        op(x)

def retMusicOp(op, x):
    if hasattr(x, '__iter__'):
        vals = list()
        for v in x:
            list.append(op(v))
    else:
        result = op(x)
        return result

def flatten(musicVal): # remove unnecessary Seq and Par intermediate nodes
    x = deepcopy(musicVal)
    if x.__class__.__name__ == "Seq" or isinstance(x, Par):
        newTrees = list()
        print(len(x.trees))
        for t in x.trees:
            newTrees.append(flatten(t))
        if len(newTrees) == 1:
            return newTrees[0]
        else:
            x.trees = newTrees
            return x
    elif x.__class__.__name__ == "Note" or x.__class__.__name__ == "Rest":
        return x
    elif x.__class__.__name__ == "Part":
        x.tree = flatten (x.tree)
        return x
