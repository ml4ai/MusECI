
#import midi  # This is the python-midi library
from MusEciDataStructures import *
from BasicOperations import *
from MEvent import musicToMEvents, musicToMEventByPart

def checkMidiCompatible(x):
    """
    Check whether pitch and volume values are within 0-127.
    If they are not, an exception is thrown.
    :param x: the music structure to search through
    :return: nothing if successful - otherwise an exception is thrown.
    """
    def f(xNote):
        if xNote.vol < 0 or xNote.vol > 127:
            raise MusEciException("Invalid volume found: " + str(xNote.vol))
        if xNote.pitch < 0 or xNote.pitch > 127:
            raise MusEciException("Invalid pitch found: " + str(xNote.pitch))
    mMap (f,x)


def forceMidiCompatible(x):
    """
    Check whether pitch and volume values are within 0-127.
    Values <0 are converted to 0 and those >127 become 127.
    :param x: the music structure to alter
    :return: a MIDI-compatible version of the input
    """
    def f(xNote):
        if xNote.vol < 0: xNote.vol = 0
        elif xNote.vol > 127: xNote.vol = 127
        if xNote.pitch <0: xNote.pitch = 0
        elif xNote.pitch >127: xNote.pitch = 127
    mMap (f,x)


# =================================================================
# MIDI CONVERSION BACKEND
# From this point onwards, we deviate from the Haskell Euterpea and
# provide classes and functions specific to peforming conversion to
# MIDI in Python.
# =================================================================

#First, some constants:
ON = 1  # note on event type
OFF = 0  # note off event type

class MEventMidi:
    """
    This is an intermediate type to aid in conversion to MIDI. A single
    MEvent will get split into two events, an on and off event. These
    will need to be sorted by event time (eTime) in larger lists.
    Field information:
     - eTime will be either relative to the last event depending on the
       current step on the way to conversion to MIDI.
     - eType should be either ON=1 or OFF=0.
    """
    def __init__(self, eTime, eType, pitch, vol=100, patch=-1):
        self.eTime = eTime
        self.eType = eType
        self.pitch = pitch
        self.vol = vol
        self.patch = patch
    def typeStr(self):
        return ["OFF", "ON"][self.eType]
    def __str__(self):
        return "MEMidi("+str(self.eTime)+","+str(self.pitch)+","+self.typeStr()+")"
    def __repr__(self):
        return str(self)


def mEventsToOnOff(mevs):
    """
    This function is an intermediate on the way from the MEvent-style
    representation to MIDI format.
    :param mevs:
    :return:
    """
    def f(e):
        return [MEventMidi(e.eTime, ON, e.pitch, e.vol, e.patch),
                MEventMidi(e.eTime+e.dur, OFF, e.pitch, e.vol, e.patch)]
    onOffs = []
    for e in mevs:
        onOffs = onOffs + f(e)
    return sorted(onOffs, key=lambda e: e.eTime)


def onOffToRelDur(evs):
    """
    This function will convert an event sequence with an eTime field into
    a relative time stamp format (time since the last event). This is intended
    for use with the MEventMidi type.
    :param evs:
    :return:
    """
    durs = [0] + list([e.eTime for e in evs])
    for i in range(0, len(evs)):
        evs[i].eTime -= durs[i]


def eventPatchList(mevs):
    patches = [e.patch for e in mevs] # extract just the patch from each note
    return list(set(patches)) # remove duplicates


def linearPatchMap(patchList):
    """
    A linearPatchMap assigns channels to instruments exculsively and top to bottom
    with the exception of percussion, which will always fall on channel 9. Note that
    this implementation allows the creation of tracks without any program changes
    through the use of negative numbers.
    :param patchList:
    :return:
    """
    currChan = 0 # start from channel 0 and work upward
    pmap = [] # initialize patch map to be empty
    for p in patchList:
        if p[1]: # do we have percussion?
            pmap.append((p,9))
        else:
            if currChan==15:
                raise Exception("ERROR: too many instruments. Only 15 unique instruments with percussion (channel 9) is allowed in MIDI.")
            else:
                pmap.append((p,currChan)) # update channel map
                if currChan==8: currChan = 10 # step over percussion channel
                else: currChan = currChan+1 # increment channel counter
    return sorted(pmap, key = lambda x: x[1])


def splitByPatch(mevs, pListIn=[]):
    """
    This function splits a list of MEvents (or MEventMidis) by their
    patch number.
    :param mevs:
    :param pListIn:
    :return:
    """
    pList = []
    # did we already get a patch list?
    if len(pListIn)==0: pList = eventPatchList(mevs) # no - need to build it
    else: pList = pListIn # use what we already were supplied
    evsByPatch = [] # list of lists to sort events
    unsorted = mevs # our starting list to work with
    for p in pList: # for each patch...
        pEvs = [x for x in unsorted if x.patch == p] # fetch the list of matching events
        evsByPatch.append(pEvs) # add them to the outer list of lists
        unsorted = [x for x in unsorted if x not in pEvs] # which events are left over?
    return evsByPatch


# Tick resolution constant
RESOLUTION = 96


# Conversion from Kulitta's durations to MIDI ticks
def toMidiTick(dur):
    ticks = int(round(dur * RESOLUTION * 4)) # bug fix 26-June-2016
    return ticks


class NoteOn:
    def __init__(self, timeStamp=None, channel=0, pitch=60, volume=100):
        self.timeStamp = timeStamp
        self.channel = channel
        self.pitch = pitch
        self.volume = volume
    def __repr__(self):
        return "NoteOn("+str(self.timeStamp)+","+str(self.channel)+","+str(self.pitch)+","+str(self.volume)+")"
    def __str__(self):
        return repr(self)

class NoteOff:
    def __init__(self, timeStamp=None, channel=0, pitch=60, volume=100):
        self.timeStamp = timeStamp
        self.channel = channel
        self.pitch = pitch
        self.volume = volume
    def __repr__(self):
        return "NoteOff("+str(self.timeStamp)+","+str(self.channel)+","+str(self.pitch)+","+str(self.volume)+")"
    def __str__(self):
        return repr(self)

class ProgramChange:
    def __init__(self, timeStamp=None, channel=0, patch=0):
        self.timeStamp = timeStamp
        self.channel = channel
        self.patch = patch
    def __repr__(self):
        return "ProgramChange("+str(self.timeStamp)+","+str(self.channel)+","+str(self.patch)+")"
    def __str__(self):
        return repr(self)

class KeyChange:
    def __init__(self, timeStamp=None, channel=0, accidentals=0, mode=0):
        self.timeStamp = timeStamp
        self.channel = channel
        self.accidentals=0
        self.mode=0
    def __repr__(self):
        return "KeyChange(" + str(self.timeStamp) + "," + str(self.channel) + "," + str(self.accidentals) +  "," + str(self.mode) +")"

    def __str__(self):
        return repr(self)

class TempoChange:
    def __init__(self, timeStamp=None, microsecPerBeat=500000): # 120bpm = 500000
        self.timeStamp = timeStamp
        self.microsecPerBeat = microsecPerBeat

    def __repr__(self):
        return "TempoChange(" + str(self.timeStamp) + "," + str(self.microsecPerBeat) + ")"

    def __str__(self):
        return repr(self)

class TimeSignature:
    def __init__(self, timeStamp=None, numerator=4, denominator=4, clocksPerClick=24, thirtysecondsPerQn=32):  # 120bpm = 500000
        self.timeStamp = timeStamp
        self.numerator = numerator
        self.denominator = denominator
        self.clocksPerClick = 24
        self.thirtysecondsPerQn = 32

    def __repr__(self):
        return "TempoChange(" + str(self.timeStamp) + "," + str(self.microsecPerBeat) + ")"

    def __str__(self):
        return repr(self)



# Create a pythonmidi event from an MEventMidi value.
def toMidiEvent(onOffMsg, chan):
    m = None
    ticks = toMidiTick(onOffMsg.eTime)
    p = int(onOffMsg.pitch)
    v = int(onOffMsg.vol)
    if onOffMsg.eType==ON: m = NoteOn(ticks, chan, p, v)
    else: m = NoteOff(ticks, chan, p, v)
    return m


# Class defs needed: program change, note on, note off
# Must have these before pythonmidi can be removed as dependency

def mEventsToPattern(mevs, alreadyByPatch=False):
    """
    Converting MEvents to a MIDI file. The following function takes a music structure
    (Music, Seq, Par, etc.) and converts it to a pythonmidi Pattern. File-writing is
    not performed at this step.
    :param mevs:
    :return:
    """
    #pattern = midi.Pattern() # Instantiate a MIDI Pattern (contains a list of tracks)
    #pattern.resolution = RESOLUTION # Set the tick per beat resolution
    pattern = []
    pList = eventPatchList(mevs) # get list of active patches
    pList.reverse() # BUG FIX 30-Dec-2016: n-ary instrument list somehow ends up reversed - not sure why.
    pmap = linearPatchMap(pList) # linear patch/channel assignment
    usedChannels = [p[1] for p in pmap] # which channels are we using? (Important for drum track)
    mevsByPatch = splitByPatch(mevs, pList) # split event list by patch
    chanInd = 0;
    for i in range(0,16):
        #track = midi.Track()
        track = list()
        if i in usedChannels: # are we using this channel?
            # if yes, then we add events to it
            mevsP = mevsByPatch[chanInd] # get the relevant collection of events
            if pmap[chanInd][0][0] >= 0: # are we assigning an instrument?
                track.append(ProgramChange(0, i, pmap[chanInd][0][0])) # set the instrument
            mevsOnOff = mEventsToOnOff(mevsP) # convert to on/off messages
            onOffToRelDur(mevsOnOff) # convert to relative timestamps
            for e in mevsOnOff: # for each on/off event...
                m = toMidiEvent(e, i) # turn it into a pythonmidi event
                track.append(m) # add that event to the track
            chanInd = chanInd+1;
        if (len(track)>0):
            pattern.append(track) # add the track to the pattern
        # NOTE: end of track marker is delegated to bytes conversion step
    return pattern

def getPatch(mevents):
    if len(mevents) > 0:
        return mevents[0].patch
    return (-1,False)

def mEventsByPartToPattern(mevsByPart):
    """
    Converting MEvents to a MIDI file. The following function takes a music structure
    (Music, Seq, Par, etc.) and converts it to a pythonmidi Pattern. File-writing is
    not performed at this step.
    :param mevs:
    :return:
    """
    #pattern = midi.Pattern() # Instantiate a MIDI Pattern (contains a list of tracks)
    #pattern.resolution = RESOLUTION # Set the tick per beat resolution
    pattern = list()
    channel = 0
    for mevs in mevsByPart:
        print(mevs)
        track = list()
        p = getPatch(mevs)
        print(p)
        patchNum = p[0]
        isPerc = p[1]
        c = channel
        if isPerc:
            c = 9
        if (patchNum >= 0):
            print("PROG CHANGE")
            track.append(ProgramChange(0, c, patchNum))
        mevsOnOff = mEventsToOnOff(mevs)  # convert to on/off messages
        print(mevsOnOff)
        onOffToRelDur(mevsOnOff)  # convert to relative timestamps
        print(mevsOnOff)
        for e in mevsOnOff:  # for each on/off event...
            m = toMidiEvent(e, c)  # turn it into a pythonmidi event
            track.append(m)  # add that event to the track
        if not(isPerc):
            channel += 1
        pattern.append(track)
    print("Track count: ", len(pattern))
    return pattern
