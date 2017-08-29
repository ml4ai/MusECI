# Weird problem: MidiWriter is successful when calling python from commandline, but not
# from within PyCharm.

# VERSION ROLLED BACK BEFORE THE ISSUE BELOW WAS FIXED (IT CAUSED SOME MYSTERIOUS OTHER PROBLEMS)
# Note: time stampping in 7-bit format causes an extra padded byte on small numbers.
# This should be fixed eventually (both in Haskell and here) but it does not affect
# the vast majority of MIDI software, since there is no rule in the MIDI spec
# forbidding it.

import MidiConversion as mc
from copy import deepcopy
import MEvent as me

'''
> binStrToNum :: String -> Int
> binStrToNum [] = 0
> binStrToNum ('0':xs) = 2* binStrToNum xs
> binStrToNum ('1':xs) = 1 + 2*binStrToNum xs
> binStrToNum _ = error "bad data."
'''

def binStrToNum(strData):
    result = 0
    i = len(strData)-1
    while (i>=0):
        if strData[i] == '0':
            result = 2 * result
        elif strData[i] == '1':
            result = 1 + 2 * result
        else:
            raise Exception("bad data supplied to binStrToNum: "+strData)
        i -= 1
    return result


'''
> fixBinStrs :: [String] -> [String]
> fixBinStrs xs =
>     let n = length xs
>         bits = take (n-1) (repeat '1') ++ "0"
>     in  Prelude.zipWith (:) bits xs
'''

def fixBinStrs(strList):
    n = len(strList)
    bits = ['1']*(n-1) + ['0']
    result = list()
    for i in range(0,n):
        result.append(bits[i] + strList[i])
    return result


'''
> pad :: Int -> a -> [a] -> [a]
> pad b x xs = if length xs >= b then xs else pad b x (x:xs)
'''

def pad(b, x, xs):
    if len(xs)>= b:
        return xs
    else:
        return pad(b, x, [x]+xs)

def padX(b, x, xs): # assumes x is a list
    if len(xs) >= b:
        return xs
    else:
        return padX(b, x, x + xs)

'''
> breakBinStrs :: Int -> String -> [String]
> breakBinStrs i s =
>     if length s <= i then [s] else take i s : breakBinStrs i (drop i s)
'''

def breakBinStrs(amt, singleStr):
    if len(singleStr) <= amt:
        return [singleStr]
    else:
        return [singleStr[:amt]] + breakBinStrs(amt, singleStr[amt:])

'''
> numToBinStr :: (Integral a, Show a) => a -> String
> numToBinStr i = showIntAtBase 2 intToDigit i ""
'''

def numToBinStr(number):
    return "{0:b}".format(number)

'''
> padTo :: Int -> String -> String
> padTo i xs = if length xs `mod` i == 0 then xs else padTo i ('0':xs)
'''

def padTo(amt, strData):
    if len(strData) % amt == 0:
        return strData
    else:
        return padTo(amt, "0"+strData)


'''
> to7Bits :: (Integral a, Show a) => a -> Byte.ByteString
> to7Bits =  Byte.pack . map (fromIntegral . binStrToNum . reverse) .
>            fixBinStrs . map (padTo 7 . reverse). reverse .
>            breakBinStrs 7 . reverse . padTo 7 . numToBinStr
'''

def to7Bits(number):
    def padTo7Rev(input):
        return padTo(7, input[::-1])
    def binStrRev(input):
        return binStrToNum(input[::-1])
    step1 = breakBinStrs(7, (padTo(7, numToBinStr(number)))[::-1])
    step2 = fixBinStrs(list(map(padTo7Rev, step1[::-1])))
    step3 = bytes(list(map(binStrRev, step2)))
    return step3

'''
> midiHeaderConst :: Byte.ByteString
> midiHeaderConst =
>     Byte.pack [0x4D, 0x54, 0x68, 0x64, 0x00, 0x00, 0x00, 0x06]
'''

def midiHeaderConst():
    return bytes([0x4D, 0x54, 0x68, 0x64, 0x00, 0x00, 0x00, 0x06])

#f = open('myfile2.txt', 'wb')
#f.write(midiHeaderConst())

'''
> padByte :: Integral a => Int -> a -> Byte.ByteString
> padByte byteCount i =
>   let b = Byte.pack [fromIntegral i]
>       n = Byte.length b
>       padding = Byte.pack $ take (byteCount - n) $ repeat 0x00
>   in  if n < byteCount then Byte.concat [padding, b] else b
'''

def padByte(byteCount, value):
    b = bytes([value])
    n = len(b)
    padding = bytes ([0x00]*(byteCount-n))
    if n < byteCount:
        return padding + b
    else:
        return b

#f = open('myfile2.txt', 'wb')
#f.write(padByte(4,192))

'''
> trackHeaderConst :: Byte.ByteString
> trackHeaderConst = Byte.pack [0x4D, 0x54, 0x72, 0x6B]
'''

def trackHeaderConst():
    return bytes([0x4D, 0x54, 0x72, 0x6B])



'''
> endOfTrack = Byte.concat [to7Bits 96, Byte.pack [0xFF, 0x2F, 0x00]]
'''

endOfTrack = to7Bits(96)+bytes([0xFF, 0x2F, 0x00])

#f = open('myfile.txt', 'wb')
#f.write(endOfTrack())


'''
> msgToBytes :: Message -> Byte.ByteString
> msgToBytes (NoteOn c k v) =
>     Byte.concat [Byte.pack [0x90 + fromIntegral c], padByte 1 k, padByte 1 v]
> msgToBytes (NoteOff c k v) =
>     Byte.concat [Byte.pack [0x80 + fromIntegral c], padByte 1 k, padByte 1 v]
> msgToBytes (ProgramChange c p) =
>     Byte.concat [Byte.pack [0xC0 + fromIntegral c], padByte 1 p]
> msgToBytes (ControlChange c n v) =
>     Byte.concat [Byte.pack [0xB0 + fromIntegral c], padByte 1 n, padByte 1 v]
> msgToBytes (TempoChange t) = -- META EVENT, HAS NO CHANNEL NUMBER
>     Byte.concat [Byte.pack [0xFF, 0x51, 0x03], fixTempo t]
> msgToBytes x = error ("(msgToBytes) Message type not currently "++
>                "supported: "++show x)
'''

def msgToBytes(message):
    if message.__class__.__name__ == "NoteOn":
        return bytes([0x90 + message.channel]) + padByte(1, message.pitch) + padByte(1, message.volume)
    elif message.__class__.__name__ == "NoteOff":
        return bytes([0x80 + message.channel]) + padByte(1, message.pitch) + padByte(1, message.volume)
    elif message.__class__.__name__ == "ProgramChange":
        return bytes([0xC0 + message.channel]) + padByte(1, message.patch)
    elif message.__class__.__name__ == "TempoChange":
        return bytes([0xFF, 0x51, 0x03]) + padByte(3, message.microsecondsPerBeat)
    elif message.__class__.__name__ == "KeyChange":
        return bytes([0xFF, 0x59, 0x02]) + padByte(1, message.accidentals) + padByte(1, message.mode)
    elif message.__class__.__name__ == "TimeSignature":
        return bytes([0xFF, 0x58, 0x04]) + padByte(1, message.numerator) + padByte(1, message.denominator) + \
               padByte(1, message.clocksPerClick) + padByte(1, message.thirtysecondsPerQn)
    else:
        raise Exception("Unsupported message: "+str(message))

# Class defs needed: program change, note on, note off
# Must have these before pythonmidi can be removed as dependency


'''
> makeTrackBody :: Track Ticks -> Byte.ByteString
> makeTrackBody [] = endOfTrack -- end marker, very important!
> makeTrackBody ((ticks, msg):rest) =
>     let b = msgToBytes msg
>         b' = [to7Bits ticks, msgToBytes msg, makeTrackBody rest]
>     in  if Byte.length b > 0 then Byte.concat b'
>         else makeTrackBody rest
'''

def makeTrackBody(onOffMsgs):
    tBody = list()
    for e in onOffMsgs:
        ticks = e.timeStamp
        msgBytes = msgToBytes(e)
        allEventBytes = to7Bits(ticks) + msgBytes
        if (len(msgBytes) > 0):
            tBody.append(allEventBytes)
    tBody.append(endOfTrack) # EOT belongs here instead
    return b''.join(tBody)

'''
> makeTrackHeader :: Byte.ByteString -> Byte.ByteString
> makeTrackHeader tbody =
>     let len = Byte.length tbody
>         f = Byte.pack . map (fromIntegral . binStrToNum . reverse) .
>             breakBinStrs 8 . pad (8*4) '0' . numToBinStr
>     in  Byte.concat [trackHeaderConst, f len]
'''

def makeTrackHeader(trackBodyBytes):
    bodyLen = len(trackBodyBytes)
    step1 = breakBinStrs(8, padX(8*4, '0', numToBinStr(bodyLen)))
    def mapFun(value):
        return binStrToNum(value[::-1])
    step2 = bytes(list(map(mapFun, step1)))
    return trackHeaderConst() + step2


'''
> makeTrack :: Track Ticks -> Byte.ByteString
> makeTrack t =
>     let body = makeTrackBody t
>         header = makeTrackHeader body
>     in  Byte.concat [header, body]
'''

def makeTrack(onOffMsgs):
    bodyBytes = makeTrackBody(onOffMsgs)
    headerBytes = makeTrackHeader(bodyBytes)
    allBytes = headerBytes + bodyBytes
    return allBytes # + endOfTrack # EOT shouldn't go here

'''
> makeHeader :: FileType -> TrackCount -> TicksPerQN -> Byte.ByteString
> makeHeader ft numTracks ticksPerQn =
>     let
>         ft' = case ft of SingleTrack -> [0x00, 0x00]
>                          MultiTrack -> [0x00, 0x01]
>                          MultiPattern -> error ("(makeHeader) Don't know "++
>                                          "how to handle multi-pattern yet.")
>         numTracks' = padByte 2 numTracks
>         ticksPerQn' = padByte 2 ticksPerQn
>     in  if numTracks > 16 then error ("(makeHeader) Don't know how to "++
>                                "handle >16 tracks!")
>         else Byte.concat [midiHeaderConst, Byte.pack ft', numTracks', ticksPerQn']
'''

def makeHeader(fileTypeStr, numTracks, ticksPerQN):
    if (numTracks > 16):
        raise Exception("Too many tracks! MIDI file format only supports 16 tracks.")
    fileTypeBytes = None
    if fileTypeStr == "SingleTrack":
        fileTypeBytes = bytes([0x00, 0x00])
    elif fileTypeStr == "MultiTrack":
        fileTypeBytes = bytes([0x00, 0x01])
    else:
        raise Exception("Unsupported file type:" + fileTypeStr)
    numTrackBytes = padByte(2, numTracks)
    ticksPerQnBytes = padByte(2, ticksPerQN)
    return midiHeaderConst() + fileTypeBytes + numTrackBytes + ticksPerQnBytes

'''
> makeFile :: Midi -> Byte.ByteString
> makeFile (Midi ft td trs) =
>     let ticksPerQn =
>             case td of TicksPerBeat x -> x
>                        TicksPerSecond x y ->
>                            error ("(makeFile) Don't know how "++
>                            "to handle TicksPerSecond yet.")
>         header = makeHeader ft (length trs) ticksPerQn
>         body = map makeTrack trs
>     in  Byte.concat (header:body)
'''

def makeFile(pattern):
    ticksPerQN = mc.RESOLUTION
    numTracks = len(pattern)
    fileTypeStr = ""
    if numTracks < 1:
        raise Exception("No tracks!")
    if numTracks == 1:
        fileTypeStr = "SingleTrack"
    else:
        fileTypeStr = "MultiTrack"
    headerBytes = makeHeader(fileTypeStr, numTracks, ticksPerQN)
    bodyBytes = makeTrack(pattern[0])
    for i in range(1,len(pattern)):
        bodyBytes = bodyBytes + makeTrack(pattern[i])
    return headerBytes + bodyBytes

#=====================================

def write_midifile(filename,pattern):
    patternBytes = makeFile(pattern)
    f = open(filename, 'wb')
    f.write(patternBytes)

def musicToMidi(filename, music, partTracks=True):
    """
    musicToMidi takes a filename (which must end in ".mid") and a music structure and writes
    a MIDI file.
    :param filename:
    :param music:
    :return:
    """
    #mc.checkMidiCompatible(x) # are the volumes and pitches within 0-127?
    if partTracks:
        es = me.musicToMEventByPart(music)
        print(es)
        p = mc.mEventsByPartToPattern(es)
        print(p)
        write_midifile(filename,p)
    else:
        e = me.musicToMEvents(music) # convert to MEvents
        p = mc.mEventsToPattern(e) # convert to a pattern (mido)
        write_midifile(filename,p)
