import numpy as np
import pandas as pd

from .headerProcessor import headerVerticalVoter, getHeader, checkHTStatus, EBOSelect, headerProcessor
from .CommonMode import getCommonMode, commonModeMuxAndAvg
from .ChannelData import getChannelData, formatChannelData

def formatEventPacketHeaderWords(row, asHex=True):
    word0 = '{0:06b}'.format(row.headerCounter)
    word0 += '{0:014b}'.format(0) #packet length and header filled in during formatter
    word0 += '{0:012b}'.format(row.eRxStatus)

    word1 = '{0:012b}'.format(row.BX)
    word1 += '{0:06b}'.format(row.Evt)
    word1 += '{0:03b}'.format(row.Orbit)

    word1 += '{0:01b}'.format(row.E)
    word1 += '{0:02b}'.format(row.HT)
    word1 += '{0:02b}'.format(row.EBO)
    word1 += '{0:01b}'.format(row.M)
    word1 += '{0:01b}'.format(0)  #set truncation bit to 0 here, would be replaced in buffer?
    word1 += '{0:04b}'.format(0) #zero padding at end

    if asHex:
        word0 = '{0:08x}'.format(int(word0,2))
        word1 = '{0:08x}'.format(int(word1,2))

    return word0, word1

def formatSubpacketHeaderWords(row, asHex=True):
    words = []

    for i_eRx in range(12):
        word  = '{0:03b}'.format(row[f'Stat_eRx{i_eRx}'])
        word += '{0:03b}'.format(row[f'Hamming_eRx{i_eRx}'])
        word += '{0:01b}'.format(0)
        word += '{0:010b}'.format(row[f'CM_{i_eRx}_0'])
        word += '{0:010b}'.format(row[f'CM_{i_eRx}_1'])
        word += row[f'ChannelMap_{i_eRx}'][0:5]
        if asHex: word = '{0:08x}'.format(int(word,2))
        words.append(word)

        word = row[f'ChannelMap_{i_eRx}'][5:37]
        if asHex: word = '{0:08x}'.format(int(word,2))
        words.append(word)

    return words

def eLinkProcessor(df_eRx,
                   df_ROC_SM,
                   k=np.array([10]*37*12),
                   lam=np.array([10]*37*12),
                   beta=np.array([10]*37*12),
                   CE=10,
                   CI=np.array([10]*37*12),
                   CIm1=np.array([10]*37*12),
                   CM_MUX=np.arange(12),
                   CM_Mask=0,
                   forcePassZS=np.array([False]*37*12),
                   forceMaskZS=np.array([False]*37*12),
                   forcePassZSm1=np.array([False]*37*12),
                   forceMaskZSm1=np.array([False]*37*12),
                   N_eRx_Thresh=10,
                   reconMode=0,
                   activeChannels=4095,
                   Error_Check = np.array([15]*12,dtype=int),
                   ):

    #check bits of active channel 
    activeChannelMask = np.array([(activeChannels >> n) & 1 for n in range(12)], dtype=bool)
    activeChannelNames = []

    #reshape channel-by-channel values
    forcePassZS.shape=(12,37)
    forceMaskZS.shape=(12,37)
    forcePassZSm1.shape=(12,37)
    forceMaskZSm1.shape=(12,37)
    CI.shape=(12,37)
    CIm1.shape=(12,37)
    k.shape=(12,37)
    lam.shape=(12,37)
    beta.shape=(12,37)

    #get arrays for data and state
    data = df_eRx[[f'Aligner_Out_Ch{i}' for i in range(12)]].values

    State = df_ROC_SM['StateText'].values
    GoodHeader = df_ROC_SM['StateText'].values

    #process headers
    dfHeader = headerProcessor(df_eRx = df_eRx,
                               df_ROC_SM = df_ROC_SM,
                               activeChannelMask = activeChannelMask,
                               N_eRx_Thresh = N_eRx_Thresh,
                               reconMode = reconMode,
                               Error_Check = Error_Check,
                              )
    
    dfCommonMode = getCommonMode(data, State)
    dfCommonMode.dropna(how='all',inplace=True)
    dfCommonMode = dfCommonMode.astype(int)
    dfCM_AVG = commonModeMuxAndAvg(dfCommonMode, CM_MUX, CM_Mask)

    dfHeader[dfCM_AVG.columns] = dfCM_AVG
    dfHeader[dfCommonMode.columns] = dfCommonMode    
    dfHeader = dfHeader.ffill().fillna(0).astype(int)
    
    # mapping to which CM average gets used for each eRx
    CM_AVG_Map = {0 : 'CM_AVG_0',
                  1 : 'CM_AVG_0',
                  2 : 'CM_AVG_1',
                  3 : 'CM_AVG_1',
                  4 : 'CM_AVG_2',
                  5 : 'CM_AVG_2',
                  6 : 'CM_AVG_3',
                  7 : 'CM_AVG_3',
                  8 : 'CM_AVG_4',
                  9 : 'CM_AVG_4',
                  10: 'CM_AVG_5',
                  11: 'CM_AVG_5'}
    
    ChannelData, channelNumber = getChannelData(data, State)
    dfDataList = []

    NZS = df_ROC_SM.TopNZS.values==1
    
    for i_eRx in range(12):
        dfLink = pd.DataFrame(ChannelData[0],columns=['TC','TP','ADCm1','ADC_TOT','TOA'],index=df_eRx.index)
        dfLink['Ch'] = channelNumber
        dfLink.Ch.fillna(-1,inplace=True)

        #get CM Avg
        dfLink['CMAvg'] = dfHeader[CM_AVG_Map[i_eRx]]

        dfLink['TopNZS'] = NZS

        channelData = dfLink.apply(formatChannelData, 
                                   args=(k[i_eRx], 
                                         lam[i_eRx],
                                         beta[i_eRx],
                                         CE,
                                         CI[i_eRx],
                                         CIm1[i_eRx],
                                         forcePassZS[i_eRx],
                                         forceMaskZS[i_eRx],
                                         forcePassZSm1[i_eRx],
                                         forceMaskZSm1[i_eRx]),
                                   axis=1)

        ###FINISH FROM HERE
        dfLink[['ChData','passZS']] = pd.DataFrame(channelData.tolist(),columns=['ChData','passZS'])
        dfLink.loc[:,'eRx'] = i_eRx
        dfLink = dfLink[['eRx','Ch','ChData','passZS']].reset_index()
        dfLink.columns = ['CLK','eRx','Ch','ChData','passZS']
        dfDataList.append(dfLink)

    dfFormattedData = pd.concat(dfDataList)

    dfFormattedData = dfFormattedData.pivot(index='CLK',columns='eRx',values=['passZS','ChData'])
    dfFormattedData.columns = [f'ChMap_{i}' for i in range(12)] + [f'ChData_{i}' for i in range(12)]

    c = ['Event', 'Bunch', 'Orbit', 'Event_Status', 'eRxStatus']
    c += [f'SubpacketStatus_eRx{i}' for i in range(12)]
    c += [f'Hamming_eRx{i}' for i in range(12)]

    for i in range(12):
        c.append(f'CM_{i}_0')
        c.append(f'CM_{i}_1')


    return dfHeader[c], dfFormattedData

