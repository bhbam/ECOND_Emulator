import pandas as pd
import numpy as np

from .ParseEtxOutputs import parseHeaderWords,parsePacketHeader

def unpackSinglePacket(packet,activeLinks):

    chData=np.array([['']*37*12],dtype=object).reshape(12,37)
    eRxHeaderData=np.array([['','','','','','','']*12],dtype=object).reshape(12,7)

    #get header words
    headerInfo=parseHeaderWords(packet,returnDict=True)

    #grab subpackets and CRC
    subPackets=packet[2:-1]
    crc=packet[-1]

    #if truncated word, all values are 0
    if headerInfo['T']==1:
        assert len(subPackets)==0
        return list(headerInfo.values())+list(np.concatenate([eRxHeaderData,chData],axis=1).flatten())+[crc]

    subpacketBinString=''.join(np.vectorize(lambda x: f'{int(x,16):032b}')(subPackets))

    for eRx in activeLinks:
        eRxHeader=parsePacketHeader(int(subpacketBinString[:32],2),int(subpacketBinString[32:64],2))
        fullSubPacket=eRxHeader[2]=='0'
        eRxHeaderData[eRx]=eRxHeader
        if fullSubPacket:
            subpacketBinString=subpacketBinString[64:]
        else:
            subpacketBinString=subpacketBinString[32:]

        chMapInt=int(eRxHeader[-1],16)
        chMap=[(chMapInt>>(36-i))&0x1 for i in range(37)]
        chAddr=np.argwhere(chMap).flatten()
        bitCounter=0

        for ch in chAddr:
            if headerInfo['P']==1: #if passthrough, no unpacking needed
                chData[eRx][ch]=subpacketBinString[:32]
                subpacketBinString=subpacketBinString[32:]
            else:
                # check first two bits of string for next channel's code
                code=subpacketBinString[:2]
                # if code starts with 00, it is a 4 bit code
                if code=='00':
                    code=subpacketBinString[:4]
                # initialize
                tctp,adcm1,adc,toa='00','0'*10,'0'*10,'0'*10


                if code=='0000': ##24 bits, ADCm1 and ADC, TcTp=00
                    bitCounter+=24
                    adcm1=subpacketBinString[4:14]
                    adc=subpacketBinString[14:24]
                    toa='0'*10
                    tctp='00'
                    subpacketBinString=subpacketBinString[24:]
                elif code=='0001': ##16 bits, ADC only (2 padded bits), TcTp=00
                    bitCounter+=16
                    adcm1='0'*10
                    adc=subpacketBinString[4:14]
                    toa='0'*10
                    tctp='00'
                    subpacketBinString=subpacketBinString[16:]
                elif code=='0010': ##24 bits, ADCm1 and ADC, TcTp=01
                    bitCounter+=24
                    adcm1=subpacketBinString[4:14]
                    adc=subpacketBinString[14:24]
                    toa='0'*10
                    tctp='01'
                    subpacketBinString=subpacketBinString[24:]
                elif code=='0011': ##24 bits, ADC and TOA, TcTp=00
                    bitCounter+=24
                    adcm1='0'*10
                    adc=subpacketBinString[4:14]
                    toa=subpacketBinString[14:24]
                    tctp='00'
                    subpacketBinString=subpacketBinString[24:]
                elif code=='01': ##32 bits, all passing ZS TcTp=00
                    bitCounter+=32
                    adcm1=subpacketBinString[2:12]
                    adc=subpacketBinString[12:22]
                    toa=subpacketBinString[22:32]
                    tctp='00'
                    subpacketBinString=subpacketBinString[32:]
                elif code=='11': ##32 bits, TcTp=11
                    bitCounter+=32
                    adcm1=subpacketBinString[2:12]
                    adc=subpacketBinString[12:22]
                    toa=subpacketBinString[22:32]
                    tctp='11'
                    subpacketBinString=subpacketBinString[32:]
                elif code=='10': ##32 bits, Invalid Code, pass along
                    bitCounter+=32
                    adcm1=subpacketBinString[2:12]
                    adc=subpacketBinString[12:22]
                    toa=subpacketBinString[22:32]
                    tctp='10'
                    subpacketBinString=subpacketBinString[32:]
                chData[eRx][ch]=tctp+adcm1+adc+toa

        #Calculate how many padded zeros there should be before next eRx starts
        paddedBits = (32 - (bitCounter%32))%32
        #check that padded bits are actually all zeros
        assert subpacketBinString[:paddedBits]=='0'*paddedBits
        #strip off padded bits
        subpacketBinString=subpacketBinString[paddedBits:]
        #check we're
        assert (len(subpacketBinString)%32)==0

    return list(headerInfo.values())+list(np.concatenate([eRxHeaderData,chData],axis=1).flatten())+[crc]

def unpackPackets(packetList,activeLinks):
    unpackedInfo=[]
    for p in packetList:
        unpackedInfo.append(unpackSinglePacket(p,activeLinks))

    columns=['HeaderMarker','PayloadLength','P','E','HT','EBO','M','T','HdrHamming','BXNum', 'L1ANum', 'OrbNum', 'S', 'RR', 'HdrCRC']
    for i in range(12):
        columns+=[f'eRx{i:02d}_{x}' for x in ['Stat', 'Ham', 'F', 'CM0', 'CM1', 'E', 'ChMap']]
        columns+=[f'eRx{i:02d}_ChData{x:02d}' for x in range(37)]
    columns += ['CRC']

    return pd.DataFrame(unpackedInfo,columns=columns)
