from MusECI.Chunk import *
from MusECI.MusEciDataStructures import *
from MusECI.GMInstruments import *
from copy import deepcopy
from MusECI.MidiReader import *
from MusECI.MEvent import MEvent, musicToMEvents
from MusECI.BasicOperations import removeZeros, removeZerosOnset, par
from MusECI.MidiConversion import splitByPatch


def extractChord(startChunk, chunks):
    '''
    Locate well-formed chords of Chunks with the same onsets and durations
    :param startChunk: Chunk to compare against
    :param chunks: All the other chunks to check
    :return: A chord, if one is found (otherwise startChunk is returned), and leftover chunks
    '''
    cChunks = [startChunk]
    for c in chunks:
        if c.onset == startChunk.onset and c.dur == startChunk.dur:
            cChunks.append(c)
    r = list(range(len(chunks)))
    r.reverse()
    for i in r:
        if chunks[i] in cChunks:
            chunks.remove(chunks[i])
    if len(cChunks) > 1:
        return Chunk("Chord", cChunks), chunks
    else:
        return startChunk, chunks

def extractMel(startChunk, chunks):
    '''
    Locate sequential patterns of back-to-back chunks
    :param startChunk: The Chunk to compare against
    :param chunks: All Chunks to check.
    :return: A sequential pattern, if found (otherwise startChunk is returned), and any leftover chunks
    '''
    mChunks = [startChunk]
    for c in chunks:
        if c.onset == mChunks[-1].end:
            mChunks.append(c)
    r = list(range(len(chunks)))
    r.reverse()
    for i in r:
        if chunks[i] in mChunks:
            chunks.remove(chunks[i])
    if len(mChunks)>1:
        return Chunk("Seq", mChunks), chunks
    else:
        return startChunk, chunks

def extractSeqs(startChunk, chunks):
    '''
    Find sequential patterns that may include gaps
    :param startChunk: First Chunk to start comparing against
    :param chunks: All other Chunks to check
    :return: A new sequence, if found (otherwise startChunk is returned), and then any leftover chunks
    '''
    sChunks = [startChunk]
    inds = []
    for i in range(len(chunks)):
        c = chunks[i]
        if c.onset == sChunks[-1].end:
            sChunks.append(c)
            inds.append(i)
        elif c.onset > sChunks[-1].end:
            r = Chunk("R", (sChunks[-1].end, c.onset - sChunks[-1].end)) # create a rest
            sChunks.append(r)
            sChunks.append(c)
            inds.append(i)
    inds.reverse()
    for i in inds:
        chunks.remove(chunks[i])
    if len(sChunks)>1:
        return Chunk("Seq", sChunks), chunks
    else:
        return startChunk, chunks

def chunkByFun(chunks, f):
    '''
    Apply a chunk-merging function, f, left to right over a list of input chunks
    :param chunks:
    :param f:
    :return: Reformatted Chunks
    '''
    fChunks = list()
    while len(chunks) > 0:
        c = chunks.pop(0)
        cChunks, chunks = f(c, chunks)
        fChunks.append(cChunks)
    return fChunks

def chunkByChords(chunks0):
    return chunkByFun(chunks0, extractChord)

def chunkByMel(chunks0):
    return chunkByFun(chunks0, extractMel)

def seqWithRests(chunks0):
    return chunkByFun(chunks0, extractSeqs)

def initChunk(evs):
    return [Chunk("E", e) for e in evs]

def chunkEvents(evs):
    '''
    Given a list of MEvents, apply the algorithms above to turn it into a single Par Chunk.
    :param evs0:
    :return:
    '''
    init = initChunk(evs)
    chords = chunkByChords(init)
    mels = chunkByMel(chords)
    seqs = seqWithRests(mels) # NEED TO TEST THIS STEP MORE
    return Chunk("Par", seqs) # This step needs to be smarter about whether it's a Par or not

def restructure(inMusic, preserveTracks = True):
    '''
    Restructure a PythonEuterpea music value using the algorithms here.
    :param inMusic:
    :return: A new music structure
    '''
    evs = musicToMEvents(inMusic)
    evsP = splitByPatch(evs)
    parts = []
    for e in evsP:
        p = checkPatch(e)
        chunk = chunkEvents(e)
        em = chunk.toMusic() # removeZerosOnset(chunk.toMusic())
        if (preserveTracks or p[0]>=0):
            em = Part(em, Instrument(p[0], p[1])) # Modify(Instrument(p[0], p[1]), em)
        parts.append(em)
    return Music(parts, 120)

def midiToMusic2(filename, flatten=False, preserveTracks = True):
    m = midiToMusic(filename)
    m2 = None
    if preserveTracks:
        newTrees = list()
        for t in m.trees:
            newTrees.append(restructure(t))
        m2 = Music(newTrees, m.meta, m.params, m.inPlace)
    else:
        m2 = restructure(m, preserveTracks)
    if flatten:
        m2 = basic.flatten(m2)
    return m2