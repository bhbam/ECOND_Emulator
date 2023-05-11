import numpy as np
import crcmod,codecs

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
