import numpy as np
import pandas as pd

channelDataStates = ['CH0',   'CH1',  'CH2',  'CH3',  'CH4',  'CH5',  
                     'CH6',   'CH7',  'CH8',  'CH9', 'CH10', 'CH11',
                     'CH12', 'CH13', 'CH14', 'CH15', 'CH16', 'CH17', 
                     'CALIB',
                     'CH18', 'CH19', 'CH20', 'CH21', 'CH22', 'CH23',
                     'CH24', 'CH25', 'CH26', 'CH27', 'CH28', 'CH29',
                     'CH30', 'CH31', 'CH32', 'CH33', 'CH34', 'CH35']

channelNumMap = {x:i for i,x in enumerate(channelDataStates)}

def unpackChannelData(vHex):
    x = int(vHex,16)

    tc = (x>>31) & 1
    tp = (x>>30) & 1

    adcm1 = (x>>20) & 1023 #(2**10 - 1)
    adc_tot = (x>>10) & 1023 #(2**10 - 1)
    toa = (x) & 1023 #(2**10 - 1)

    return tc, tp, adcm1, adc_tot, toa

def getChannelData(data, State):
    State_ = State.reshape(-1,1)
    isChannelData = np.isin(State_,channelDataStates)

    chData = np.where(State_,
                      np.vectorize(unpackChannelData)(data),
                      -1)

    #return channel number index (used later for ZS)
    chNumber = np.vectorize(channelNumMap.get)(State)

    return np.swapaxes(chData,0,2), chNumber

hammingCodes = {'0000': '00000000',
                '1000': '00001111',
                '0100': '00110011',
                '1100': '00111100',
                '0010': '01010101',
                '1010': '01011010',
                '0110': '01100110',
                '1110': '01101001',
                '0001': '10010110',
                '1001': '10011001',
                '0101': '10100101',
                '1101': '10101010',
                '0011': '11000011',
                '1011': '11001100',
                '0111': '11110000',
                '1111': '11111111'}


def formatChannelData(row, k, lam, beta, CE, CI, CIm1, forcePassZS, forceMaskZS, forcePassZSm1, forceMaskZSm1, asHex=True):
    if row.Ch==-1: return '',0

    Ch = int(row.Ch)

    TC = row.TC==1
    TP = row.TP==1

    FC_NZS = row.TopNZS
    
    passZSbit = '1'

    if TC: #Automatic full readout for TCTP=11 or Invalid Code (TCTCP=10)
        word  = '{0:010b}'.format(row.ADCm1)
        word += '{0:010b}'.format(row.ADC_TOT)
        word += '{0:010b}'.format(row.TOA)

        if TP:
            word40 = word + '00' + hammingCodes['1100']
        else:
            word40 = word + '00' + hammingCodes['1000']

    elif TP: #No ZS or BX-1 ZS applied, but TOA suppresed for TCTP=01
        word  = '{0:010b}'.format(row.ADCm1)
        word += '{0:010b}'.format(row.ADC_TOT)

        word40 = word + '000000000000' + hammingCodes['0010']

    else:
        threshold = ((int(lam[Ch]*row.CMAvg)>>6) +
                     (int(k[Ch]*row.ADCm1)>>5) +
                     CI[Ch] )

        passZS = False if forceMaskZS[Ch] else ((row.ADC_TOT + CE) > threshold) | forcePassZS[Ch] | FC_NZS
        
        thresholdm1 = 8*CIm1[Ch] + (int(beta[Ch] * row.CMAvg)>>7)
        
        passZSm1 = False if forceMaskZSm1[Ch] else (row.ADCm1 > thresholdm1) | forcePassZSm1[Ch] | FC_NZS

        passZSTOA = row.TOA>0

        if not passZS: #fails ZS
            word = ''

            word40 = '{0:032b}'.format(0) + hammingCodes['1111']

            passZSbit = '0'

        elif (passZSm1) and (not passZSTOA): #TOA ZS
            word  = '{0:010b}'.format(row.ADCm1)
            word += '{0:010b}'.format(row.ADC_TOT)

            word40 = word + '000000000000' + hammingCodes['0000']

        elif (not passZSm1) and (not passZSTOA): #ADC(-1) and TOA ZS
            word  = '{0:010b}'.format(row.ADC_TOT)
            word += '00'

            word40 = word + '00000000000000000000' + hammingCodes['0001']

        elif (not passZSm1) and (passZSTOA): #ADC(-1) ZS
#             if toaSaveAll: #option to transmit ADCm1 every time TOA is sent
#                 word  = '{0:010b}'.format(row.ADCm1)
#                 word += '{0:010b}'.format(row.ADC_TOT)
#                 word += '{0:010b}'.format(row.TOA)

#                 word40 = word + '00' + hammingCodes['0100']
#             else:
            word  = '{0:010b}'.format(row.ADC_TOT)
            word += '{0:010b}'.format(row.TOA)

            word40 = word + '000000000000' + hammingCodes['0011']

        elif passZSm1 and passZSTOA: #ADC(-1), ADC, TOA pass ZS
            word  = '{0:010b}'.format(row.ADCm1)
            word += '{0:010b}'.format(row.ADC_TOT)
            word += '{0:010b}'.format(row.TOA)

            word40 = word + '00' + hammingCodes['0100']


    if asHex:
#         if len(word)==16:
#             word = '{0:04x}'.format(int(word,2))
#         elif len(word)==24:
#             word = '{0:06x}'.format(int(word,2))
#         elif len(word)==32:
#             word = '{0:08x}'.format(int(word,2))
        word40 = '{0:010x}'.format(int(word40,2))
    return word40, passZSbit


