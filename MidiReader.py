'''
MIDI to PythonEuterpea Conversion
Donya Quick

Assumptions:
- No mixed-channel tracks (but there can be more than one track with the same channel)
- Ticks per beat = 96

Output format:
- Outermost Par(s) are by instrument
- Within an instrument's subtree, everything is still parallelized - each note is
  simply offset by a rest representing its onset time.
- All "expression" events like aftertouch, modulation, etc. are ignored.

Things not yet supported:
- Tempo change events (currently everything is 120bpm with on changes)
- ProgramChange events ocurring in the middle of a track. Currently assuming
  one track per instrument per channel.
'''

from mido import MidiFile
from MusEciDataStructures import Note, Rest, Music, Part, INST, PERC, Instrument
from BasicOperations import par, line, deriveOnsets
#from MidiConversion import RESOLUTION
from MEvent import MEvent
import MusEciOperations as op
import BasicOperations as basic

def findNoteDuration(pitch, events):
    '''
    Scan through a list of MIDI events looking for a matching note-off.
    A note-on of the same pitch will also count to end the current note,
    assuming an instrument can't play the same note twice simultaneously.
    If no note-off is found, the end of the track is used to truncate
    the current note.
    :param pitch:
    :param events:
    :return:
    '''
    sumTicks = 0
    for e in events:
        #sumTicks = sumTicks + e.tick
        sumTicks = sumTicks + e.time
        #c = e.__class__.__name__
        c = e.type
        #if c == "NoteOffEvent" or c == "NoteOnEvent":
        if c == "note_on" or c == "note_off":
            if e.note == pitch:
                return sumTicks
    return sumTicks


def toPatch(channel, patch):
    '''
    Convert MIDI patch info to PythonEuterpea's version.
    :param channel: if this is 9, it's the drum track
    :param patch:
    :return: a tuple of an int and boolean, (patch, isDrums)
    '''
    if channel==9:
        return (patch, PERC)
    else:
        return (patch, INST)


def tickToDur(ticks, resolution = 96):
    '''
    Convert from pythonmidi ticks back to PythonEuterpea durations
    :param ticks:
    :param resolution:
    :return:
    '''
    #return float(ticks) / float((RESOLUTION * 4))
    return float(ticks) / float((resolution * 4))

def getChannel(track):
    '''
    Determine the channel assigned to a track.
    ASSUMPTION: all events in the track should have the same channel.
    :param track:
    :return:
    '''
    if len(track) > 0:
        e = track[0]
        #if (e.__class__.__name__ == "EndOfTrackEvent"): # mido has no end of track?
        #    return -1
        if track[0].type == 'note_on' or track[0].type=='note_off':
            return track[0].channel
    return -1

def trackToMEvents(track, ticksPerBeat=96, defaultPatch = -1):
    '''
    Turn a pythonmidi track (list of events) into MEvents
    :param track:
    :return:
    '''
    currTicks = 0
    currPatch = defaultPatch
    channel = getChannel(track);
    mevs = []
    for i in range(0,len(track)):
        e = track[i]
        c = e.type
        currTicks = currTicks + e.time # add time after last event
        if c == "program_change":
            # assign new instrument
            currPatch = e.program # e.data[0]
        elif c == "note_on":
            # 1. find matching noteOn event OR another note on with the same pitch & channel
            noteDur = findNoteDuration(e.note, track[(i + 1):])
            # 2. create an MEvent for the note
            n = MEvent(tickToDur(currTicks, ticksPerBeat), e.note, tickToDur(noteDur, ticksPerBeat), e.velocity, patch=toPatch(channel, currPatch))
            mevs.append(n)
        #elif c == "SetTempoEvent":
            #print(("Tempo change ignored (not supported yet): ", e))
        elif c == 'time_signature':
            print("TO-DO: handle time signature event")
            pass # need to handle this later
        elif c == 'track_name':
            print("TO-DO: handle track name event")
            pass
        elif c == 'key_signature':
            print("TO-DO: handle key signature event")
            pass # need to handle this later
        elif c == 'note_off' or 'end_of_track':
            pass # nothing to do here; note offs and track ends are handled in on-off matching in other cases.
        else:
            print("Unsupported event type (ignored): ", e.type, vars(e),e)
            pass
    return mevs

def checkPatch(mevs):
    '''
    Determines the PythonEuterpea patch for a collection of MEvents.
    :param mevs:
    :return:
    '''
    retVal = (-1,INST)
    if len(mevs) > 0:
        retVal = mevs[0].patch
    return retVal

def mEventsToMusic(mevs, preserveTracks=True):
    '''
    Convert a list of MEvents to a Music value
    :param mevs:
    :return:
    '''
    mVals = []
    patch = checkPatch(mevs) # NEED TO UPDATE THIS
    for e in mevs:
        n = Note(e.pitch, e.dur, e.eTime, e.vol)
        r = Rest(e.eTime, 0)
        mVals.append(line([r,n]))
    mTotal = par(mVals)
    #if (patch[0] >= 0):
    if (preserveTracks or patch[0] >= 0):
        i = Instrument(patch[0], patch[1])
        mTotal = Part(mTotal, i) # Modify(i, mTotal)
    return mTotal

def midiToMusic(filename, preserveTracks = True):
    '''
    Read a MIDI file and convert it to a Music structure.
    :param filename:
    :return:
    '''
    #pattern = read_midifile(filename) # a list of tracks
    midi_file = MidiFile(filename)
    mVals = []
    #for t in pattern:
    defaultInst = -1
    for i, t in enumerate(midi_file.tracks):
        evs = trackToMEvents(t, midi_file.ticks_per_beat, defaultInst)
        if len(evs) > 0:
            mVals.append(mEventsToMusic(evs, preserveTracks))
            defaultInst -= 1
    music = Music(mVals, 120)
    return basic.removeZeros(music)





