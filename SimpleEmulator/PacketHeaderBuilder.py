import numpy as np
import crcmod, codecs
READOUT_HGCROC=0
ECON_FIFO=1
FIRST_ACTIVE=2

standard_Reco={'10000':READOUT_HGCROC,
               '10001':READOUT_HGCROC,
               '10010':ECON_FIFO,
               '10011':ECON_FIFO,
               #^^^ Expected, Perfect HT

               '10100':READOUT_HGCROC,
               '10101':READOUT_HGCROC,
               '10110':ECON_FIFO,
               '10111':ECON_FIFO,
               #^^^ Expected, Good HT

               '11000':ECON_FIFO,
               '11001':ECON_FIFO,
               '11010':ECON_FIFO,
               '11011':ECON_FIFO,
               #^^^ Expected, Failed HT

               '11100':ECON_FIFO,
               '11101':ECON_FIFO,
               '11110':ECON_FIFO,
               '11111':ECON_FIFO,
               #^^^ Expected, Ambiguous HT

               '00000':READOUT_HGCROC,
               '00001':READOUT_HGCROC,
               '00010':FIRST_ACTIVE,
               '00011':FIRST_ACTIVE,
               #^^^ Unexpected, Perfect HT

               '00100':READOUT_HGCROC,
               '00101':READOUT_HGCROC,
               '00110':FIRST_ACTIVE,
               '00111':FIRST_ACTIVE,
               #^^^ Unexpected, Good HT

               '01000':FIRST_ACTIVE,
               '01001':FIRST_ACTIVE,
               '01010':FIRST_ACTIVE,
               '01011':FIRST_ACTIVE,
               #^^^ Unexpected, Failed HT

               '01100':FIRST_ACTIVE,
               '01101':FIRST_ACTIVE,
               '01110':FIRST_ACTIVE,
               '01111':FIRST_ACTIVE,
               #^^^ Unexpected, Ambiguous HT
              }


ht_bits_used = np.array([31,30,29,28,3,2,1,0])
ebo_bits_used = np.arange(27,6,-1)
parityGroups = np.array([[56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41,
                          40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26],
                         [56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41,
                          25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11],
                         [56, 55, 54, 53, 52, 51, 50, 49, 40, 39, 38, 37, 36, 35, 34, 33,
                          25, 24, 23, 22, 21, 20, 19, 18, 10,  9,  8,  7,  6,  5,  4],
                         [56, 55, 54, 53, 48, 47, 46, 45, 40, 39, 38, 37, 32, 31, 30, 29,
                          25, 24, 23, 22, 17, 16, 15, 14, 10,  9,  8,  7,  3,  2,  1],
                         [56, 55, 52, 51, 48, 47, 44, 43, 40, 39, 36, 35, 32, 31, 28, 27,
                          25, 24, 21, 20, 17, 16, 13, 12, 10,  9,  6,  5,  3,  2,  0],
                         [56, 54, 52, 50, 48, 46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26,
                          25, 23, 21, 19, 17, 15, 13, 11, 10,  8,  6,  4,  3,  1,  0]])

crc8 = crcmod.mkCrcFun(0x1a7,initCrc=0, xorOut=0, rev=False)


def processERXHeaders(headerWords, i2c, expected, fifoTop):

    ht_vote=[]
    for i in ht_bits_used:
        ht_vote.append((headerWords>>i)&1)
    ht_vote=np.array(ht_vote)

    isZero=(ht_vote==0).sum(axis=1)>i2c.VReconstruct_thresh
    isZero_Perfect=(ht_vote==0).all(axis=1)
    isOne =(ht_vote==1).sum(axis=1)>i2c.VReconstruct_thresh
    isOne_Perfect =(ht_vote==1).all(axis=1)

    ht_perfect=(isZero_Perfect|isOne_Perfect).all()
    ht_good=(isZero|isOne).all()
    ht_amb=(isZero&isOne).any()
    ht_bits=3 if ht_amb else 0 if ht_perfect else 1 if ht_good else 0

    ebo_vote=[]
    for i in ebo_bits_used:
        ebo_vote.append((headerWords>>i)&1)
    ebo_vote=np.array(ebo_vote)

    isZero=(ebo_vote==0).sum(axis=1)>i2c.VReconstruct_thresh
    isZero_Perfect=(ebo_vote==0).all(axis=1)
    isOne =(ebo_vote==1).sum(axis=1)>i2c.VReconstruct_thresh
    isOne_Perfect =(ebo_vote==1).all(axis=1)

    ebo_perfect=(isZero_Perfect|isOne_Perfect).all()
    ebo_good=(isZero|isOne).all()
    ebo_amb=(isZero&isOne).any()
    ebo_bits=3 if ht_amb else 0 if ht_perfect else 1 if ht_good else 0

    e_ht_ebo_bits=f'{expected:01b}{ht_bits:02b}{ebo_bits:02b}'

    firstActive_Bunch = (headerWords[0]>>16)&0xfff
    firstActive_Event = (headerWords[0]>>10)&0x3f
    firstActive_Orbit = (headerWords[0]>>7)&0x7

    hgcroc_Bunch = (isOne[:12].astype(int)[::-1] * 2**np.arange(12)).sum()
    hgcroc_Event = (isOne[12:18].astype(int)[::-1] * 2**np.arange(6)).sum()
    hgcroc_Orbit = (isOne[18:].astype(int)[::-1] * 2**np.arange(3)).sum()

    fifo_Bunch, fifo_Event, fifo_Orbit = fifoTop

    transmit_Bunch,transmit_Event,transmit_Orbit=0,0,0

    if i2c.EBO_ReconMode==0: #standard reconstruction mode
        ebo_transmit_type=standard_Reco[e_ht_ebo_bits]

        if ebo_transmit_type==READOUT_HGCROC:
            transmit_Bunch=hgcroc_Bunch
            transmit_Event=hgcroc_Event
            transmit_Orbit=hgcroc_Orbit
        elif ebo_transmit_type==ECON_FIFO:
            transmit_Bunch=fifo_Bunch
            transmit_Event=fifo_Event
            transmit_Orbit=fifo_Orbit
        elif ebo_transmit_type==FIRST_ACTIVE:
            transmit_Bunch=firstActive_Bunch
            transmit_Event=firstActive_Event
            transmit_Orbit=firstActive_Orbit
    elif i2c.EBO_ReconMode==1:
        if expected:
            transmit_Bunch=fifo_Bunch
            transmit_Event=fifo_Event
            transmit_Orbit=fifo_Orbit
        else:
            transmit_Bunch=firstActive_Bunch
            transmit_Event=firstActive_Event
            transmit_Orbit=firstActive_Orbit
    elif i2c.EBO_ReconMode==2:
        transmit_Bunch=firstActive_Bunch
        transmit_Event=firstActive_Event
        transmit_Orbit=firstActive_Orbit

    matchBit=((transmit_Bunch==fifo_Bunch)&
              (transmit_Event==fifo_Event)&
              (transmit_Orbit==fifo_Orbit))

    return transmit_Bunch, transmit_Event, transmit_Orbit, e_ht_ebo_bits, matchBit

def buildHeaders(i2c, N, e_ht_ebo_bits, matchBit, Tbit, transmit_Bunch, transmit_Event, transmit_Orbit, Sbit, RRbits):

    header1=f'{int(i2c.HeaderMarker,16):09b}{N:09b}{i2c.PassThruMode:01b}{e_ht_ebo_bits}{matchBit:01b}{Tbit}'
    header2=f'{transmit_Bunch:012b}{transmit_Event:06b}{transmit_Orbit:03b}{Sbit:01b}{RRbits}'

    hdr_for_hamming=(header1+header2+'0000000')
    hdr_for_hamming_bits=np.array([x for x in hdr_for_hamming]).astype(int)[::-1]
    hammingBits=hdr_for_hamming_bits[parityGroups].sum(axis=1)%2
    hammingBits=''.join([f'{x}' for x in hammingBits])
    hdr_for_crc='00000000'+header1+'000000'+header2
    crcBits=f"{crc8(codecs.decode(f'{int(hdr_for_crc,2):064x}', 'hex')):08b}"

    return [f"{int(header1+hammingBits,2):08X}",f"{int(header2+crcBits,2):08X}"]
