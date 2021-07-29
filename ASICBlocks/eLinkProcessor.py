import numpy as np
import pandas as pd


def findHeaderWord(vals):
    x = np.vectorize(int)(vals,16)
    GoodHeader = ((x>>28)==5) & ((x&15)==5)

    x_prevBX = np.append(x[-1:],x[:-1])
    previousIDLE = ((x_prevBX==2630667468) | (x_prevBX==2899102924))
    return GoodHeader & previousIDLE

def unpackHeader(vHex):
    x = int(vHex,16)
    hammingBits = (x>>4) & ((2**3) - 1)
    orbitNum = (x>>7) & ((2**3) - 1)
    eventNum = (x>>10) & ((2**6) - 1)
    bxNum    = (x>>16) & ((2**12) - 1)
    return bxNum, eventNum, orbitNum, hammingBits

def unpackCommonModes(vHex):
    x = int(vHex,16)
    CM1 = x & ((2**10)-1)
    CM2 = x & ((2**10)-1)
    CMAvg = int((CM1+CM2)/2)
    return CM1, CM2, CMAvg

def unpackChannelData(vHex):
    x = int(vHex,16)

    tc = (x>>31) & 1
    tp = (x>>30) & 1

    adcm1 = (x>>20) & (2**10 - 1)
    adc_tot = (x>>10) & (2**10 - 1)
    toa = (x) & (2**10 - 1)

    return tc, tp, adcm1, adc_tot, toa

# TODO
# Order of this needs to be verified (just taking from wikipedia Hamming(7,4) page right now
hammingCodes = {'0000':'0000000',
                '1000':'1110000',
                '0100':'0111100',
                '0010':'0101010',
                '1010':'1011010',
                '0110':'1100110',
                '1110':'0010110',
                '0001':'1101001',
                '1001':'0011001',
                '0101':'0100101',
                '1101':'1010101',
                '0011':'1000011',
                '1011':'0110011',
                '0111':'0001111',
                '1111':'1111111'}

def formatChannelData(row, k, lam, beta, CE, CI, CIm1):
    if row.Ch==-1: return '',''

    TC = row.TC==1
    TP = row.TP==1

    if TC: #Automatic full readout for TCTP=11 or Invalid Code (TCTCP=10)
        word = '{0:01b}'.format(TC)
        word += '{0:01b}'.format(TP)
        word += '{0:010b}'.format(row.ADCm1)
        word += '{0:010b}'.format(row.ADC_TOT)
        word += '{0:010b}'.format(row.TOA)

        if TP:
            word40 = word + hammingCodes['1100']
        else:
            word40 = word + hammingCodes['1000']

        return word, word40

    if TP: #No ZS or BX-1 ZS applied, but TOA suppresed for TCTP=01
        word = '0010'
        word += '{0:010b}'.format(row.ADCm1)
        word += '{0:010b}'.format(row.ADC_TOT)

        word40 = word + '00000000' + hammingCodes['0010']

        return word, word40

    threshold = ((int(lam*row.CMAvg)>>6) +
                 (int(k*row.ADCm1)>>5) +
                 CI[row.Ch] )

    passZS = (row.ADC_TOT + CE) > threshold

    if not passZS: #fails ZS
        word = ''

        word40 = '{0:032b}'.format(0) + hammingCodes['1111']

        return word, word40

    passZSm1 = row.ADCm1 > (8*CIm1[row.Ch] + (int(beta * row.CMAvg)>>7))

    passZSTOA = row.TOA>0

    if (passZSm1) and (not passZSTOA): #TOA ZS
        word = '0000'
        word += '{0:010b}'.format(row.ADCm1)
        word += '{0:010b}'.format(row.ADC_TOT)

        word40 = word + '00000000' + hammingCodes['0000']

        return word, word40

    if (not passZSm1) and (not passZSTOA): #ADC(-1) and TOA ZS
        word = '0001'
        word += '{0:010b}'.format(row.ADC_TOT)
        word += '00'

        word40 = word + '00000000' + '00000000' + hammingCodes['0001']

        return word, word40

    if (not passZSm1) and (passZSTOA): #ADC(-1) ZS
        word = '0011'
        word += '{0:010b}'.format(row.ADC_TOT)
        word += '{0:010b}'.format(row.TOA)

        word40 = word + '00000000' + hammingCodes['0011']

        return word, word40

    if passZSm1 and passZSTOA: #ADC(-1), ADC, TOA pass ZS
        word = '01'
        word += '{0:010b}'.format(row.ADCm1)
        word += '{0:010b}'.format(row.ADC_TOT)
        word += '{0:010b}'.format(row.TOA)

        word40 = word + hammingCodes['0100']

        return word, word40


def eLinkProcessor(vals):

    isDataStart = findHeaderWord(vals)

    N = len(vals)
    readPattern = np.array([70,80] + list(range(37)) + [90,99])


    readCycle = np.ones_like(vals)*-9

    readStart = np.arange(N)[isDataStart]
    readStop = readStart+41
    readStop[readStop>N] = N
    readLen = readStop-readStart

    for j in range(len(readStart)):
        readCycle[readStart[j]:readStop[j]] = readPattern[:readLen[j]]

    # parse header information, setup columns for this data
    headerData = np.where(readCycle==70,
                          np.vectorize(unpackHeader)(vals),
                          np.where(readCycle<0,-1,np.nan))

    dfLink = pd.DataFrame(headerData.T,columns=['BX','Evt','Orbit','Hamming'])

    #parse common mode words, populating CM1, CM2, and CM
    CM = np.where(readCycle==80,
                  np.vectorize(unpackCommonModes)(vals),
                  np.where(readCycle<0,-1,np.nan))

    dfLink[['CM1','CM2','CMAvg']] = pd.DataFrame(CM.T,columns=['CM1','CM2','CMAvg'])

    chData = np.where((readCycle>=0) & (readCycle<37),
                      np.vectorize(unpackChannelData)(vals),
                      -1)

    dfLink['Ch'] = np.where((readCycle>=0) & (readCycle<37),
                            readCycle,
                            -1)

    dfLink[['TC','TP','ADCm1','ADC_TOT','TOA']] = pd.DataFrame(chData.T,columns=['TC','TP','ADCm1','ADC_TOT','TOA'])

    dfLink = dfLink.fillna(method='ffill').astype(int)

    # Need to encorprate these registes in a way that can be passed between.
    # Likely will be csv files, thought this should wait for Cristian's implementation as well
    k= 0.03125
    lam=0.015625
    beta=0.03125
    CE = 10
    CI = np.random.randint(10,size=37)
    CIm1 = np.random.randint(6,size=37)

    channelData = dfLink.apply(formatChannelData,args=(k, lam, beta, CE, CI, CIm1),axis=1)

    dfLink[['ChData_Short','ChData']] = pd.DataFrame(channelData.tolist(),columns=['ChData_Short','ChData'])

    return dfLink
