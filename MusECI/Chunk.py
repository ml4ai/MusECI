from MusECI.MusEciDataStructures import *
from MusECI.BasicOperations import line, par

class Chunk:

    def __init__(self, kind, value):
        self.kind = kind
        self.value = value
        self.onset = 0
        self.end = 0
        self.dur = 0

        if (kind=="R"): # value is a tuple of onset and duration
            self.onset = value[0]
            self.dur = value[1]
            self.end = self.onset + self.dur
        elif (kind=="E"): # value is an MEvent
            self.onset = self.value.eTime
            self.dur = self.value.dur
            self.end = self.onset + self.dur
        elif (kind=="Seq"): # value is a list of back-to-back chunks sorted by onset
            if (len(self.value) > 0):
                self.onset = self.value[0].onset
                self.dur = sum ([x.dur for x in self.value])
                self.end = self.value[-1].onset + self.value[-1].dur
        elif (kind=="Chord"): # value is a list of chunks with identical onsets and durs
            if (len(self.value) > 0):
                self.onset = self.value[0].onset
                self.dur = self.value[0].dur
                self.end = self.value[0].end
        elif (kind=="Par"): # value is a list of potentially overlapping chunks
            if (len(self.value) > 0):
                self.onset = min([x.onset for x in self.value])
                self.end = min([x.end for x in self.value])
                self.dur = self.end - self.onset
        else:
            raise Exception("Unrecognized Chunk kind: "+kind)

    def __str__(self):
        if (self.kind=="E"):
            return self.kind + " "+str(self.value.eTime)+" "+str(self.value.pitch)+" "+str(self.value.dur)
        else:
            return self.kind + " "+str(self.value)

    def __repr__(self):
        return str(self)

    def isPrim(self):
        return self.kind=="R" or self.kind=="E"

    def toMusic(self):
        if (self.kind=="R"):
            return Rest(self.value[1])
        elif (self.kind=="E"):
            return Note(self.value.pitch, self.value.dur, self.value.eTime, self.value.vol)
        elif (self.kind=="Seq"): # avoid a single-item Seq
            if len(self.value) == 1:
                return self.value[0].toMusic()
            else:
                return line([x.toMusic() for x in self.value])
        elif (self.kind=="Chord"): # avoid a single-item Par
            return Chord([x.toMusic() for x in self.value])
        elif (self.kind=="Par"):
            if len(self.value) == 1:
                return self.value[0].toMusic()
            else:
                return par([line([Rest(x.onset, 0), x.toMusic()]) for x in self.value])
        else:
            raise Exception("Unrecognized Chunk kind: "+self.kind)