import numpy as np
import pandas as pd

def getHeader(data, readCycle, i_eRx):
    # parse header information, setup columns for this data
    headerData = np.where(readCycle==70,
                          np.vectorize(unpackHeader)(data),
                          np.nan)

    dfHeader = pd.DataFrame(headerData.T,columns=[f'BxOrbEvt_eRx{i_eRx}',f'Hamming_eRx{i_eRx}'])

    return dfHeader

def unpackHeader(vHex):
    x = int(vHex,16)
    hammingBits = (x>>4) & 7        #(2**3 - 1)
    BxOrbEvtNum = (x>>7) & 2097151  #(2**21 - 1)
    return BxOrbEvtNum, hammingBits

splitHeaderInts = np.vectorize(lambda x: np.array(list('{0:021b}'.format(x))).astype(int),signature='()->(n)', otypes=[np.int64])

def headerVerticalVoter(eRx_EBO_Values, N):
    #eRx_EBO_Values should be an array of the values of the BxOrbEvtNum for all 12 links
    # will go through bitwise, preforming the vertical comparison

    #splits values into arrays of 21 bits, then sums (counting how many times each bit is 0 or 1)
    bits = splitHeaderInts(eRx_EBO_Values)
    isZero=(bits==0).sum(axis=1)
    isOne =(bits==1).sum(axis=1)

    perfectReco   = ((isZero==12) ^ (isOne==12)).all(axis=1)
    goodReco      = ((isZero>N) ^ (isOne>N)).all(axis=1)
    ambiguousReco = ((isZero>N) & (isOne>N)).any(axis=1)
    failedReco    = (~(isZero>N) & ~(isOne>N)).any(axis=1)

    EBO_flag=np.where(perfectReco, '11',
                      np.where(goodReco, '10',
                               np.where(failedReco,'00','01')))  #gives preferences to failed reco over ambiguous reco

    outputBits = np.where(goodReco.reshape(200,1),
                          np.where(isOne,1,0),
                          bits[:,0,:])

    #get bits, multiply by appropriate 2**N multiple, and sum to get an integer value
    EvtNum = (outputBits[:,:12] * 2**np.arange(12)[::-1]).sum(axis=1)
    BxNum  = (outputBits[:,12:18] * 2**np.arange(6)[::-1]).sum(axis=1)
    OrbNum = (outputBits[:,18:] * 2**np.arange(3)[::-1]).sum(axis=1)

    FullNum = (outputBits * 2**np.arange(21)[::-1]).sum(axis=1).reshape(-1,1)
    EBO_eRx_errBits = (eRx_EBO_Values==FullNum)

    return EvtNum, BxNum, OrbNum, EBO_flag, EBO_eRx_errBits

def getReadCycle(vals, N_eRx_Thresh=10):

    isDataStart, headerTrailerErr = findHeaderWord(vals, N_eRx_Thresh)

    N = len(vals)
    readPattern = np.array([70,80] + list(range(37)) + [90,99])

    readCycle = np.ones(N,dtype=int)*-9

    readStart = np.arange(N)[isDataStart]
    readStop = readStart+41
    readStop[readStop>N] = N
    readLen = readStop-readStart

    for j in range(len(readStart)):
        readCycle[readStart[j]:readStop[j]] = readPattern[:readLen[j]]

    return readCycle, headerTrailerErr
