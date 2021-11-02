import numpy as np
import pandas as pd

from .crcCheck import eRx_crcCheck

def getHeader(data, State):
    State_ = State.reshape(-1,1)

    #find header data from clock cylces in a header state
    headerData = np.where((State_=='STANDARDHEADER') | (State_=='UNEXPECTEDHEADER'),
                          np.vectorize(unpackHeader)(data),
                          np.nan)

    dfHeader = pd.DataFrame(headerData[0],columns=[f'BxEvtOrb_eRx{i_eRx}' for i_eRx in range(12)])
    dfHeader[[f'Hamming_eRx{i_eRx}' for i_eRx in range(12)]] =  pd.DataFrame(headerData[1])

    return dfHeader

def unpackHeader(vHex):
    x = int(vHex,16)
    hammingBits = (x>>4) & 7        #(2**3 - 1)
    BxOrbEvtNum = (x>>7) & 2097151  #(2**21 - 1)
    return BxOrbEvtNum, hammingBits

def checkHTStatus(vals, goodHeaderWord):

    firstByte = vals.astype('<U8').T.view('<U1').T[::8]
    lastByte  = vals.astype('<U8').T.view('<U1').T[7::8]

    hasHeader = (firstByte=='5') & (lastByte=='5')

    return hasHeader[goodHeaderWord==1].astype(int)

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

    EBO_flag=np.where(perfectReco, 3,
                      np.where(goodReco, 2,
                               np.where(failedReco,0,1)))  #gives preferences to failed reco over ambiguous reco

    outputBits = np.where(goodReco.reshape(-1,1),
                          np.where(isOne,1,0),
                          bits[:,0,:])

    #get bits, multiply by appropriate 2**N multiple, and sum to get an integer value
    BxNum  = (outputBits[:,:12] * 2**np.arange(12)[::-1]).sum(axis=1)
    EvtNum = (outputBits[:,12:18] * 2**np.arange(6)[::-1]).sum(axis=1)
    OrbNum = (outputBits[:,18:] * 2**np.arange(3)[::-1]).sum(axis=1)

    FullNum = (outputBits * 2**np.arange(21)[::-1]).sum(axis=1).reshape(-1,1)
    EBO_eRx_errBits = (eRx_EBO_Values==FullNum)

    return EvtNum, BxNum, OrbNum, EBO_flag, EBO_eRx_errBits

def EBOSelect(dfEBO, reconMode, activeChannelMask):
    
    mode=reconMode>>4 & 3
    linkSelect = reconMode & 15
    
    #get first active channel
    firstActiveChannel = np.arange(12)[activeChannelMask][0]

    BxEvtOrb = dfEBO[f'BxEvtOrb_eRx{firstActiveChannel}'].values.astype(int)

    firstActiveBunch = (BxEvtOrb >> 9) & 4095
    firstActiveEvent = (BxEvtOrb>>3) & 63
    firstActiveOrbit = BxEvtOrb & 7

    dfEBO_Output = pd.DataFrame({'Event':0,'Bunch':0,'Orbit':0},index=dfEBO.index)
    
    if mode==0:
        dfEBO_Output['Event'] = np.where(dfEBO.EBO_flag>=2,                   
                                 dfEBO.Event_Vote,
                                 np.where(dfEBO.TopEvent>-1,
                                          dfEBO.TopEvent,
                                          firstActiveEvent)
                                        )
        dfEBO_Output['Bunch'] = np.where(dfEBO.EBO_flag>=2,                   
                                         dfEBO.Bunch_Vote,
                                         np.where(dfEBO.TopBunch>-1,
                                                  dfEBO.TopBunch,
                                                  firstActiveBunch)
                                        )
        dfEBO_Output['Orbit'] = np.where(dfEBO.EBO_flag>=2,                   
                                         dfEBO.Orbit_Vote,
                                         np.where(dfEBO.TopOrbit>-1,
                                                  dfEBO.TopOrbit,
                                                  firstActiveOrbit)
                                        )
    elif mode==1:
        dfEBO_Output['Event'] = np.where(dfEBO.TopEvent>-1,
                                         dfEBO.TopEvent,
                                         firstActiveEvent)
        dfEBO_Output['Bunch'] = np.where(dfEBO.TopBunch>-1,
                                         dfEBO.TopBunch,
                                         firstActiveBunch)
        dfEBO_Output['Orbit'] = np.where(dfEBO.TopOrbit>-1,                                     
                                         dfEBO.TopOrbit,
                                         firstActiveOrbit)
    elif mode==2:
        dfEBO_Output['Bunch'] = firstActiveBunch
        dfEBO_Output['Event'] = firstActiveEvent
        dfEBO_Output['Orbit'] = firstActiveOrbit
    else:
        BxEvtOrb = dfEBO[f'BxEvtOrb_eRx{linkSelect}'].values
        dfEBO_Output['Bunch'] = (BxEvtOrb >> 9) & 4095
        dfEBO_Output['Event'] = (BxEvtOrb>>3) & 63
        dfEBO_Output['Orbit'] = BxEvtOrb & 7
    
    return dfEBO_Output
    
def headerProcessor(df_eRx, 
                    df_ROC_SM,
                    activeChannelMask,
                    N_eRx_Thresh,
                    reconMode,
                    Error_Check
                   ):

    dfHeader = getHeader(data=df_eRx.values,
                         State=df_ROC_SM['StateText'].values)

    dfHeaderSubset = dfHeader.dropna(how='all').astype(int)

    HTstatus = checkHTStatus(df_eRx.values,df_ROC_SM['GoodHeaderWord'].values)
    dfHeaderSubset[[f'HT_eRx{i}' for i in range(12)]] = pd.DataFrame(HTstatus,index=dfHeaderSubset.index)
    dfHeaderSubset['HT'] = np.where(dfHeaderSubset[[f'HT_eRx{i}' for i in range(12)]].sum(axis=1)==12,3,2)

    EvtNum, BxNum, OrbNum, EBO_flag, EBO_eRx_errBits = headerVerticalVoter(dfHeaderSubset[[f'BxEvtOrb_eRx{i}' for i in range(12)]].astype(int).values, N=N_eRx_Thresh)
    dfHeaderSubset[['Bunch_Vote','Event_Vote','Orbit_Vote','EBO_flag']] = pd.DataFrame({'Bunch_Vote':BxNum,
                                                                                        'Event_Vote':EvtNum,
                                                                                        'Orbit_Vote':OrbNum,
                                                                                        'EBO_flag':EBO_flag},
                                                                                       index=dfHeaderSubset.index)

    dfHeaderSubset[['TopEvent','TopBunch','TopOrbit']] = df_ROC_SM[['TopEvent','TopBunch','TopOrbit']]    

    dfHeaderSubset[['Event','Bunch','Orbit']] = EBOSelect(dfHeaderSubset, reconMode, activeChannelMask)
    dfHeaderSubset['BxEvtOrb'] = (dfHeaderSubset.Bunch.values<<9) + (dfHeaderSubset.Event.values<<3) + (dfHeaderSubset.Orbit.values) 

    #get Event Header Packet Match Bit
    dfHeaderSubset['EBOMatch'] = ((dfHeaderSubset.Event_Vote==dfHeaderSubset.TopEvent) & 
                                  (dfHeaderSubset.Bunch_Vote==dfHeaderSubset.TopBunch) &
                                  (dfHeaderSubset.Orbit_Vote==dfHeaderSubset.TopOrbit)).astype(int)

    #get Subpacket EBO Match Bit
    for i_eRx in range(12):
        dfHeaderSubset[f'EBOMatch_eRx{i_eRx}'] = dfHeaderSubset[f'BxEvtOrb_eRx{i_eRx}'] == dfHeaderSubset['BxEvtOrb']

    #first set equal to state, just to easily get state only for those BX, then check if STANDARDHEADER
    dfHeaderSubset['ExpectedEvent'] = df_ROC_SM.StateText
    dfHeaderSubset['ExpectedEvent'] = (dfHeaderSubset['ExpectedEvent']=='STANDARDHEADER').astype(int)

    #Event_Status  (7-bit The E, HT, EBO, M, and T status of the event)
    dfHeaderSubset['Event_Status'] = ((dfHeaderSubset.ExpectedEvent.values << 6)+
                                      (dfHeaderSubset.HT.values<<4) + 
                                      (dfHeaderSubset.EBO_flag.values<<2) + 
                                      (dfHeaderSubset.EBOMatch.values<<1)
                                     )
    
    dfCRC = eRx_crcCheck(df_eRx, df_ROC_SM)

    df = pd.DataFrame(index=dfHeader.index)
    df[dfHeaderSubset.columns] = dfHeaderSubset

    df[dfCRC.columns] = dfCRC
    df = df.ffill().fillna(0).astype(int)

    for i_eRx in range(12):
        df[f'SubpacketStatus_eRx{i_eRx}'] = ((df[f'HT_eRx{i_eRx}'].values<<2) + 
                                             (df[f'EBOMatch_eRx{i_eRx}'].values<<1) +
                                             (df[f'CRC_eRx{i_eRx}'].values))

    #split ErrorCheck register into its 4 bit components
    Error_Check_All   = ((Error_Check>>3) & 1)==1
    Error_Check_HT    = ((Error_Check>>2) & 1)==1
    Error_Check_Match = ((Error_Check>>1) & 1)==1
    Error_Check_CRC   = ((Error_Check>>0) & 1)==1

    #check eRx status, 
    df['eRxStatus'] = 0
    for i_eRx in range(12):
        #0 = error, 1 = good state
        # check if each component is in error, and that error check is active, or of these means we have an error state, take the not to invert logic to 0=error, 1=good 
        df[f'eRxStatus_{i_eRx}'] =~((((df[f'CRC_eRx{i_eRx}']==0)      & Error_Check_HT[i_eRx]   ) |
                                     ((df[f'EBOMatch_eRx{i_eRx}']==0) & Error_Check_Match[i_eRx]) |
                                     ((df[f'CRC_eRx{i_eRx}']==0)      & Error_Check_CRC[i_eRx]  )) 
                                    & Error_Check_All[i_eRx])
        df['eRxStatus'] += df[f'eRxStatus_{i_eRx}'].values << i_eRx
        
    return df.astype(int)