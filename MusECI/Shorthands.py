from MusECI.MusEciDataStructures import Note

# Capital letters had to be used here to avoid conflict with "as" to mean a-sharp

def pcToNote(pcnum, oct, dur, onset=None, vol=100):
    return Note(pcnum+(oct+1)*12, dur, onset, vol)

def Cf(oct, dur, onset=None, vol=100):
    return pcToNote(11, oct, dur, onset, vol) # 11-apr-2017 changed from 1 to 11

def C(oct, dur, onset=None, vol=100):
    return pcToNote(0, oct, dur, onset, vol)

def Cs(oct, dur, onset=None, vol=100):
    return pcToNote(1, oct, dur, onset, vol)

def Df(oct, dur, onset=None, vol=100):
    return pcToNote(1, oct, dur, onset, vol)

def D(oct, dur, onset=None, vol=100):
    return pcToNote(2, oct, dur, onset, vol)

def Ds(oct, dur, onset=None, vol=100):
    return pcToNote(3, oct, dur, onset, vol)

def Ef(oct, dur, onset=None, vol=100):
    return pcToNote(3, oct, dur, onset, vol)

def E(oct, dur, onset=None, vol=100):
    return pcToNote(4, oct, dur, onset, vol)

def F(oct, dur, onset=None, vol=100):
    return pcToNote(5, oct, dur, onset, vol)

def Fs(oct, dur, onset=None, vol=100):
    return pcToNote(6, oct, dur, onset, vol)

def Gf(oct, dur, onset=None, vol=100):
    return pcToNote(6, oct, dur, onset, vol)

def G(oct, dur, onset=None, vol=100):
    return pcToNote(7, oct, dur, onset, vol)

def Gs(oct, dur, onset=None, vol=100):
    return pcToNote(8, oct, dur, onset, vol)

def Af(oct, dur, onset=None, vol=100):
    return pcToNote(8, oct, dur, onset, vol)

def A(oct, dur, onset=None, vol=100):
    return pcToNote(9, oct, dur, onset, vol)

def As(oct, dur, onset=None, vol=100):
    return pcToNote(10, oct, dur, onset, vol)

def Bf(oct, dur, onset=None, vol=100):
    return pcToNote(10, oct, dur, onset, vol)

def B(oct, dur, onset=None, vol=100):
    return pcToNote(11, oct, dur, onset, vol)

def Bs(oct, dur,onset=None, vol=100):
    return pcToNote(0, oct, dur, onset, vol) # 11-apr-2017 changed from 12 to 0

