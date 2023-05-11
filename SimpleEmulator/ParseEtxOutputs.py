import numpy as np
import crcmod,codecs

def toHex(x):
    if len(x)==0:
        return ''
    elif len(x)==16:
        return f'{int(x,2):04X}'
    elif len(x)==24:
        return f'{int(x,2):06X}'
    elif len(x)==32:
        return f'{int(x,2):08X}'
toHexV=np.vectorize(toHex)

def parseOutputPackets(dfOutput, i2c):
    #get outputs, select the active eTx, and flatten them into a continuous stream of data
    outputStream=dfOutput.values[:,i2c.ETx_active][:,::-1].flatten()
    outputStreamInt=np.vectorize(lambda x: int(x,16))(outputStream)

    # check for idle pattern
    isIDLE = (outputStreamInt>>8)==int(i2c.IdlePattern,16)
    #check for output header
    isOutputHeader = (outputStreamInt>>23)==int(i2c.HeaderMarker,16)
    #packets are considered started if an output header is present, and the previous BX is an idle
    isPacketStart=np.concatenate([[False],isOutputHeader[1:] & isIDLE[:-1]])

    #get starting index
    outputStartIndices=np.where(isPacketStart)[0]

    packets=[]
    for outputStartIdx in outputStartIndices:
        HdrMarker, PayloadLength, P, E, HT, EBO, M, T, Hamming = parseHeaderWord0(outputStreamInt[outputStartIdx])
        BX, L1A, Orb, S, RR, CRC=parseHeaderWord1(outputStreamInt[outputStartIdx+1])

        packetOut=outputStream[outputStartIdx:(outputStartIdx+PayloadLength+2)]

        packets.append(packetOut)

    return packets

def parseIdle(Idle):
    BuffStat=Idle&0x7
    Err=(Idle>>3)&0x7
    RR=(Idle>>6)&0b11
    Pattern=(Idle>>8)
    return Pattern, RR, Err, BuffStat

def parseHeaderWords(HeaderWords, returnDict=False):
    if type(HeaderWords[0]) in [str,np.str_,np.string_]:
        hdr_0=int(HeaderWords[0],16)
    elif type(HeaderWords[0]) in [int,np.int]:
        hdr_0=HeaderWords[0]
    if type(HeaderWords[1]) in [str,np.str_,np.string_]:
        hdr_1=int(HeaderWords[1],16)
    elif type(HeaderWords[1]) in [int,np.int]:
        hdr_1=HeaderWords[1]

    if returnDict:
        hdrFields=parseHeaderWord0(hdr_0,returnDict=returnDict)
        hdrFields.update(parseHeaderWord1(hdr_1,returnDict=returnDict))
    else:
        hdrFields=parseHeaderWord0(hdr_0)
        hdrFields+=parseHeaderWord1(hdr_1)

    return hdrFields


def parseHeaderWord0(HeaderWord0, returnDict=False):
    HdrMarker=(HeaderWord0>>23)&0x1ff
    PayloadLength=(HeaderWord0>>14)&0x1ff
    P=(HeaderWord0>>13)&0x1
    E=(HeaderWord0>>12)&0x1
    HT=(HeaderWord0>>10)&0x3
    EBO=(HeaderWord0>>8)&0x3
    M=(HeaderWord0>>7)&0x1
    T=(HeaderWord0>>6)&0x1
    Hamming=(HeaderWord0>>0)&0x3f
    if returnDict:
        return {"HdrMarker":HdrMarker,
                "PayloadLength":PayloadLength,
                "P":P,
                "E":E,
                "HT":HT,
                "EBO":EBO,
                "M":M,
                "T":T,
                "Hamming":Hamming
               }
    else:
        return HdrMarker, PayloadLength, P, E, HT, EBO, M, T, Hamming

def parseHeaderWord1(HeaderWord1, returnDict=False):
    BX=(HeaderWord1>>20)&0xfff
    L1A=(HeaderWord1>>14)&0x3f
    Orb=(HeaderWord1>>11)&0x7
    S=(HeaderWord1>>10)&0x1
    RR=(HeaderWord1>>8)&0x3
    CRC=(HeaderWord1)&0xff
    if returnDict:
        return {"Bunch":BX,
                "Event":L1A,
                "Orbit":Orb,
                "S":S,
                "RR":RR,
                "CRC":CRC}
    else:
        return BX, L1A, Orb, S, RR, CRC


def parsePacketHeader(packetHeader0,packetHeader1=0,asHex=True):
    Stat=(packetHeader0>>29)&0x7
    Ham = (packetHeader0>>26)&0x7
    F=(packetHeader0>>25)&0x1
    CM0=(packetHeader0>>15)&0x3ff
    CM1=(packetHeader0>>5)&0x3ff
    if F==1:
        E=(packetHeader0>>4)&0x1
    else:
        E=0
    ChMap=((packetHeader0&0x1f)<<32)+packetHeader1
    if asHex:
        return f'{Stat:01x}',f'{Ham:01x}',f'{F:01x}',f'{CM0:03x}',f'{CM1:03x}',f'{E:01x}',f'{ChMap:010x}',
    else:
        return Stat, Ham, F, CM0, CM1, E, ChMap

crc = crcmod.mkCrcFun(0x104c11db7,initCrc=0, xorOut=0, rev=False)

def parseDAQLink(eLinkData,hdr_marker=15):
    DAQ_eRx_int=np.vectorize(lambda x: int(x,16))(eLinkData)
    #parse header
    goodHeaderTrailer=(((((DAQ_eRx_int[:,0])&0b1111)==5) | (((DAQ_eRx_int[:,0])&0b1111)==2)) &
                       (((DAQ_eRx_int[:,0]>>28)&0b1111)==hdr_marker))
    hammingErrors=(DAQ_eRx_int[:,0]>>4)&0b111
    orbitNum=(DAQ_eRx_int[:,0]>>7)&0b111
    eventNum=(DAQ_eRx_int[:,0]>>10)&0b111111
    bunchNum=(DAQ_eRx_int[:,0]>>16)&0xfff

    #parse CM
    CMHeaderCheck=((DAQ_eRx_int[:,1]>>30))==0b10
    CM0=(DAQ_eRx_int[:,1]>>10)&0x3ff
    CM1=DAQ_eRx_int[:,1]&0x3ff

    #parse
    Tc=(DAQ_eRx_int[:,2:39]>>31)
    Tp=(DAQ_eRx_int[:,2:39]>>30)&1
    ADCm1=(DAQ_eRx_int[:,2:39]>>20)&0x3ff
    ADCorTOT=(DAQ_eRx_int[:,2:39]>>10)&0x3ff
    TOA=(DAQ_eRx_int[:,2:39])&0x3ff


    crcGood=np.zeros(len(eLinkData),dtype=bool)
    for i in range(len(eLinkData)):
        crcGood[i]=crc(codecs.decode((''.join(eLinkData[i])), 'hex'))==0

    return goodHeaderTrailer, hammingErrors, orbitNum, eventNum, bunchNum, CM0, CM1, Tc, Tp, ADCm1, ADCorTOT, TOA, crcGood
