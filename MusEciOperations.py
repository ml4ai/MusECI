from copy import deepcopy
import MusEciDataStructures as ds
import BasicOperations as basic
#import abc # this isn't working when trying to register new classes

class AbstractOpException(Exception):
    """
    For throwing errors
    """
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)

class MusEciOp(object):
    #__metaclass__ = abc.ABCMeta # not working
    #@abc.abstractmethod # still can't get this to work
    def apply(self):
        raise AbstractOpException("Abstract MusECI operation can't be applied.")

class Transpose(MusEciOp):
    def __init__(self, halfsteps=0, key=None, scalePreserving=False, inPlace=False):
        self.halfsteps = halfsteps
        self.scalePreserving = scalePreserving
        self.key = key
        self.inPlace = inPlace
    def __str__(self):
        return 'Transpose(' + str(self.halfsteps) + ',' + str(self.key) + ',' + str(self.key) + ')'

    def __repr__(self):
        return str(self)

    def apply(self, musicVal, inPlace=False):
        x = ds.handleInPlace(musicVal, self.inPlace)
        if self.scalePreserving:
            basic.scaleTransposeM(x, self.halfsteps, self.key.scale)
        else:
            basic.transpose(x, self.halfsteps)
        return x

#MusEciOp.register(Transpose)

class Retrograde(MusEciOp):
    def __init__(self, revPs = True, revRhythm = True, inPlace=False):
        self.revPs = revPs
        self.revRhythm = revRhythm
        self.inPlace = inPlace
    def __str__(self):
        return 'Retrograde('+str(self.revPs)+','+str(self.revRhythm)+')'
    def __repr__(self):
        str(self)
    def apply(self, musicVal, inPlace=False):
        x = ds.handleInPlace(musicVal, self.inPlace)
        if (self.revPs and self.revRhythm):
            basic.reverseOnsetInPlace(x)
            return x
        else:
            print("Retrograde currently only supports revPs=True and revDurs=True. Music not changed!")
            return x

#MusEciOp.register(Retrograde)

class Invert(MusEciOp):
    def __init__(self, refPitch = None, scalePreserving = False, key=None, inPlace = False):
        self.scalePreserving = scalePreserving
        self.refPitch = refPitch
        self.key = key
        self.inPlace = inPlace
    def __str__(self):
        return 'Invert('+str(self.refPitch)+','+str(self.scalePreserving)+')'
    def __repr__(self):
        str(self)
    def apply(self, musicVal):
        x = ds.handleInPlace(musicVal, self.inPlace)
        if self.scalePreserving:
            if self.key == None:
                print("Can't invert with scale preservation without a scale. Music not changed!")
                # do nothing to x
            else:
                if self.refPitch==None:
                    basic.scaleInvert(x, self.key)
                else:
                    basic.scaleInvertAt(x, self.refPitch, self.key.scale)
        else:
            if self.refPitch==None:
                basic.invert(x)
            else:
                basic.invertAt(x, self.refPitch)
        return x

#MusEciOp.register(Invert)

class ScaleDurs(MusEciOp): # factor of 0.5 turns QN ito EN, etc.
    def __init__(self, factor=0, quantize=False, quantizeUnit=ds.SN, inPlace=False):
        self.factor = factor
        self.quantize = quantize
        self.quantizeUnit = quantizeUnit
        self.inPlace = inPlace
    def __str__(self):
        print(('TimeStretch('+self.factor+','+self.quantize+','+self.quantizeUnit+','+self.inPlace+')'))
    def __repr__(self):
        return str(self)
    def apply(self, musicValue):
        x = ds.handleInPlace(musicValue, self.inPlace)
        if (self.quantize):
            print("Quantization not yet supported. Music value not changed!")
        else:
            basic.scaleDursOnsets(x, self.factor)
        return x

#MusEciOp.register(ScaleDurs)


class Cut(MusEciOp): # TO-DO
    def __init__(self):
        pass
    def __str__(self):
        pass
    def __repr__(self):
        return str(self)
    def apply(self, musicVal):
        pass

#MusEciOp.register(Cut)

class Remove(MusEciOp): # TO-DO
    def __init__(self, shiftBack=True):
        pass
    def __str__(self):
        pass
    def __repr__(self):
        return str(self)
    def apply(self, musicVal):
        pass

#MusEciOp.register(Remove)

class Cleanup(MusEciOp): # to do restructuring, insert/remove rests appropriatey etc.
    def __init__(self, inPlace=False):
        self.inPlace = inPlace
    def __str__(self):
        return 'Cleanup('+str(self.inPlace)+')'
    def __repr__(self):
        return str(self)
    def apply(self, musicVal):
        x = ds.handleInPlace(musicVal, self.inPlace)
        basic.removeZeros(x)
        basic.stripRests(x)
        basic.fillRests(x)
        return x

class Flatten(MusEciOp): # flatten unnecessary nested Seq/Pars
    def __init__(self):
        pass
    def __str__(self):
        return 'Flatten()'
    def __repr__(self):
        return str(self)
    def apply(self, musicVal):
        pass

#MusEciOp.register(Cleanup)

class Repeat(MusEciOp):
    def __init__(self, times=2):
        self.times = times
    def __str__(self):
        return 'Repeat('+str(self.times)+')'
    def __repr__(self):
        return str(self)
    def apply(self, musicVal):
        ms = list()
        offset = 0
        d = basic.durOnset(musicVal)
        for i in range (0,self.times):
            x = deepcopy(musicVal)
            basic.shiftOnsets(x, offset)
            ms.append(x)
            offset += d
        return ds.Seq(trees=ms, inPlace=True) # in place is allowable here because we are already copying

#MusEciOp.register(Repeat)


class CombinePar(MusEciOp): # Note: there are no checks here if two of the same note overlap in the same instrument!
    def __init__(self, inPlace=False):
        self.inPlace = inPlace
    def __str__(self):
        return 'Par()'
    def __repr__(self):
        return str(self)
    def apply(self, musicList):
        ms = list()
        minO = min(list(map(basic.minOnset, musicList)))
        for m in musicList:
            x = ds.handleInPlace(m, self.inPlace)
            basic.setDefaultOffset(x, minO)
            ms.append(x)
        return ds.Par(trees=ms, inPlace=True)  # in place is allowable here because we are already copying

#MusEciOp.register(CombinePar)


class CombineSeq(MusEciOp):
    def __init__(self, inPlace=False):
        self.inPlace = inPlace
    def __str__(self):
        return 'CombineSeq()'
    def __repr__(self):
        return str(self)
    def apply(self, musicList):
        ms = list()
        offset = 0
        for m in musicList:
            basic.deriveOnsets(m) # Ensure that everything has an onset assigned
            x = ds.handleInPlace(m, self.inPlace)
            d = basic.durOnset(x)
            basic.shiftOnsets(x, offset)
            ms.append(x)
            offset += d
        return ds.Seq(trees=ms, inPlace=True)  # in place is allowable here because we are already copying

#MusEciOp.register(CombineSeq)

def applyInSequence(listOfOps, musicVal):
    '''
    Applies a list of MusEciOps to a MusECI music value
    :param listOfOps: list of operations to be applied from LEFT TO RIGHT: [f1, f2, ..., fn]
    :param musicVal: starting music value
    :return: the result of computing fn(...f2(f1(musicVal)))
    '''
    retVal = musicVal
    for op in listOfOps:
        if isinstance(op, MusEciOp):
            retVal = op.apply(retVal)
        else:
            raise ds.MusEciException("Invalid operation of type "+op.__class__.__name__)
    return retVal