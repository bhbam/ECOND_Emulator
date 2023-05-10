import codecs
from SimpleEmulator.UnpackZSConstants import DIV_Factors
from .ParseEtxOutputs import parseDAQLink, crc, parseIdle
from .PacketHeaderBuilder import processERXHeaders, buildHeaders

import numpy as np


def ECOND_Simple_Emulator(dfInput, dfCounters, startIndices, i2c, RR, debug=False):

    emulatorPackets=[]

    chMaps = []
    chDatas = []
    eboGoods = []
    goodHeaderTrailers = []
    ADCm1s, ADCorTOTs, TOAs=[],[],[]
    for startIdx in startIndices[:]:
        #     print(startIdx)
        d=dfInput.values[startIdx:(startIdx+40)]
        NZS=dfCounters.iloc[startIdx]['FifoTopNZS']==1
        inputHeaderWords=dfInput.iloc[startIdx][i2c.ERx_active].apply(int,base=16).values

        d[:,~i2c.ERx_active]='00000000'
        goodHeaderTrailer, hammingErrors, orbitNum, eventNum, bunchNum, CM0, CM1, Tc, Tp, ADCm1, ADCorTOT, TOA, crcGood=parseDAQLink(d.T,int(i2c.ROC_HdrMarker,16))
        CM0_padded=np.concatenate([CM0,[0,0,0,0]])
        CM1_padded=np.concatenate([CM1,[0,0,0,0]])
        ROC_CM_SUM=CM0_padded[i2c.CM_eRX_Route.reshape(6,2)].sum(axis=1)+CM1_padded[i2c.CM_eRX_Route.reshape(6,2)].sum(axis=1)
        MOD_CM=ROC_CM_SUM.sum()
        erx_active_padded=np.concatenate([i2c.ERx_active,[0,0,0,0]])
        N_CM=erx_active_padded[i2c.CM_eRX_Route.reshape(6,2)].sum(axis=1)*2
        DIV_N=DIV_Factors[N_CM]
        ROC_CM_AVG=np.concatenate([(ROC_CM_SUM*DIV_N)>>16,[(MOD_CM*DIV_Factors[N_CM.sum()])>>16,0]])

        A_CM=np.where(i2c.CM_Selections<7,
                      ROC_CM_AVG[i2c.CM_Selections],
                      i2c.CM_UserDef
                      ).reshape(12,1)

        passZS = (ADCorTOT+i2c.ZS_ce) > (((A_CM*i2c.ZS_lambda)>>5) + ((ADCm1*i2c.ZS_kappa)>>5) + i2c.ZS_c)
        passZS = passZS | i2c.ZS_pass | NZS

        passZSm1 = ADCm1 > (8*i2c.ZS_m1_c + ((i2c.ZS_m1_beta*A_CM)>>5))
        passZSm1 = passZSm1 | i2c.ZS_m1_pass | NZS
        passZSm1 = passZSm1 & ~i2c.ZS_m1_mask

        passTOA=TOA>0


        ADCm1_10bit=np.vectorize(lambda x: f'{x:010b}')(ADCm1).astype(object)
        ADCorTOT_10bit=np.vectorize(lambda x: f'{x:010b}')(ADCorTOT).astype(object)
        TOA_10bit=np.vectorize(lambda x: f'{x:010b}')(TOA).astype(object)
        CM0_10bit=np.vectorize(lambda x: f'{x:010b}')(CM0).astype(object)
        CM1_10bit=np.vectorize(lambda x: f'{x:010b}')(CM1).astype(object)
        TcTp_2bit=np.vectorize(lambda x: f'{x:02b}')(Tc*2+Tp).astype(object)

        format_ZS=''
        format_0000='0000'+ADCm1_10bit+ADCorTOT_10bit
        format_0001='0001'+ADCorTOT_10bit+'00'
        format_0010='0010'+ADCm1_10bit+ADCorTOT_10bit
        format_0011='0011'+ADCorTOT_10bit+TOA_10bit
        format_0100='01'+ADCm1_10bit+ADCorTOT_10bit+TOA_10bit
        format_1100='11'+ADCm1_10bit+ADCorTOT_10bit+TOA_10bit
        format_1000='10'+ADCm1_10bit+ADCorTOT_10bit+TOA_10bit
        format_passThru=TcTp_2bit+ADCm1_10bit+ADCorTOT_10bit+TOA_10bit

        chMap=np.where(i2c.ZS_mask,
                       '0',
                       np.where((Tc==1)|(Tp==1),
                                '1',
                                np.where(passZS,'1','0')))

        chData=np.where(i2c.ZS_mask,
                        format_ZS, #
                        np.where((Tc==0) & (Tp==0),
                                 np.where(~passZS, format_ZS,#if not pass ZeroSuppression, send ZS
                                          np.where(~passZSm1 & passTOA, format_0011, #TOA & not ADC-1
                                                   np.where(passZSm1 & passTOA, format_0100, #TOA and ADC-1
                                                            np.where(~passTOA & ~passZSm1, format_0001, #not TOA, not ADC-1
                                                                     format_0000) #TOA, not ADC-1
                                                            )
                                                   )
                                          ),
                                 np.where((Tc==0) & (Tp==1), format_0010,
                                          np.where((Tc==1) & (Tp==0), format_1000,
                                                   format_1100)
                                          )
                                 )
                        )

        if i2c.PassThruMode:
            chMap[:]='1'
            chData=format_passThru

        chMap_37bit=np.array([''.join(list(c[::-1])) for c in chMap])
        F=(chMap=='1').sum(axis=1)>0
        fBit=np.where(F,'0','1').astype(object)

        expected=dfCounters.iloc[startIdx].FifoOccupancy>0
        fifoTop=(dfCounters.iloc[startIdx].FifoTopBunch, dfCounters.iloc[startIdx].FifoTopEvent, dfCounters.iloc[startIdx].FifoTopOrbit)

        transmit_Bunch, transmit_Event, transmit_Orbit, e_ht_ebo_bits, matchBit = processERXHeaders(inputHeaderWords, i2c, expected, fifoTop)

        eboGood=((bunchNum==transmit_Bunch) &
                 (orbitNum==transmit_Orbit) &
                 (eventNum==transmit_Event))

        eboBit=np.where(eboGood,'1','0').astype(object)
        htBit=np.where(goodHeaderTrailer,'1','0').astype(object)
        crcBit=np.where(crcGood,'1','0').astype(object)

        statBits=htBit+eboBit+crcBit
        eBit=np.where(eboGood & goodHeaderTrailer & crcGood,'0','1')

        hammingBits=np.vectorize(lambda x: f'{x:03b}')(hammingErrors).astype(object)

        suppressedSubPacket=statBits+hammingBits+fBit+CM0_10bit+CM1_10bit+eBit+'0000'

        chData_SubPacket=np.array([''.join(c) for c in chData]).astype(object)
        zeroPadLen=(32-(np.vectorize(len)(chData_SubPacket)%32))%32
        zeroPadBits=np.array(['0'*n for n in zeroPadLen]).astype(object)
        subPacketData=chData_SubPacket+zeroPadBits
        fullSubPacket=statBits+hammingBits+fBit+CM0_10bit+CM1_10bit+chMap_37bit+subPacketData

        data=np.where(F,fullSubPacket,suppressedSubPacket)
        subPacketBits=''.join(list(data[i2c.ERx_active]))
        subPacketWords=[f'{int(subPacketBits[i:i+32],2):08X}' for i in range(0,len(subPacketBits),32)]

        crcWord=f"{crc(codecs.decode((''.join(subPacketWords)), 'hex')):08X}"

        N=len(subPacketWords)+1

        Sbit=(statBits[i2c.ERx_active]=='111').all()
        Tbit='0'

        ## cheat, getting RR bits from previous BX Idle packet
        RRbits=RR[startIdx]

        packetHeader=buildHeaders(i2c, N, e_ht_ebo_bits, matchBit, Tbit, transmit_Bunch, transmit_Event, transmit_Orbit, Sbit, RRbits)

        emulatorPackets.append(np.array(packetHeader+subPacketWords+[crcWord]))
        if debug:
            chMaps.append(chMap)
            chDatas.append(chData)
            eboGoods.append(eboGood)
            goodHeaderTrailers.append(goodHeaderTrailer)
            ADCm1s.append(ADCm1)
            ADCorTOTs.append(ADCorTOT)
            TOAs.append(TOA)
    if debug:
        return emulatorPackets, chMaps, chDatas, eboGoods, goodHeaderTrailers, ADCm1s, ADCorTOTs, TOAs
    else:
        return emulatorPackets
