import numpy as np
import pandas as pd

BitShiftDivMultipliers = np.array([0, 65536, 32768, 21845, 16384,
                                   13107, 10923, 9362, 8192, 7282,
                                   6554, 5958, 5461, 5041, 4681,
                                   4369, 4096, 3855, 3641, 3449,
                                   3277, 3121, 2979, 2849, 2731])

def getCommonMode(data, State):

    State_ = State.reshape(-1,1)

    #parse common mode words, populating CM1, CM2
    CM = np.where(State_=='CM',
                  np.vectorize(unpackCommonModes)(data),
                  np.nan)

    dfCommonMode = pd.DataFrame(CM[0],columns=[f'CM_{i_eRx}_0' for i_eRx in range(12)])
    dfCommonMode[[f'CM_{i_eRx}_1' for i_eRx in range(12)]] = pd.DataFrame(CM[1],columns=[f'CM_{i_eRx}_0' for i_eRx in range(12)])

    return dfCommonMode[[ f'CM_{i_eRx}_{j}' for i_eRx in range(12) for j in (0,1) ]]

def unpackCommonModes(vHex):
    x = int(vHex,16)
    CM1 = x & 1023 #((2**10)-1)
    CM2 = x & 1023 #((2**10)-1)
    return CM1, CM2

def commonModeMuxAndAvg(dfCommonMode, CM_MUX, CM_Mask):

    CM_Values = dfCommonMode.values

    CM_Mask_Array = np.array([((CM_Mask>>i)&1)==1 for i in range(24)[::-1]])#.reshape(12,2)

    #zero out masked values
    CM_Values[:,CM_Mask_Array]=0

    #reshape into pairs to allow for easy muxing
    CM_Mask_Array = CM_Mask_Array.reshape(12,2)
    CM_Values = CM_Values.reshape(-1,12,2)

    #Mux, and reshape into groups of 4 (for summing into HGCROCs)
    CM_Mask_Array_Muxed = CM_Mask_Array[CM_MUX].reshape(6,4)
    CM_Values_Muxed = CM_Values[:,CM_MUX].reshape(-1,6,4)

    #count how many active channels are in each ROC and total (active meaning not masked)
    nActive=(~CM_Mask_Array_Muxed).sum(axis=-1)
    nActiveTotal=nActive.sum()

    CM_ROC_Sums = CM_Values_Muxed.sum(axis=2)
    CM_Total_Sum = CM_ROC_Sums.sum(axis=1)

    CM_ROC_Average = (CM_ROC_Sums*BitShiftDivMultipliers[nActive])>>16
    CM_Total_Average = (CM_Total_Sum*BitShiftDivMultipliers[nActiveTotal])>>16

    df_CM_AVG = pd.DataFrame(CM_ROC_Average, columns=[f'CM_AVG_{i}' for i in range(6)], index=dfCommonMode.index)
    df_CM_AVG['CM_AVG'] = CM_Total_Average

    return df_CM_AVG
    # CM_Mask_Array = np.array([((CM_Mask>>i)&1)==1 for i in range(24)[::-1]])

    # #clean CM_MUX values
    # CM_MUX[CM_MUX>11]=11
    # CM_MUX[CM_MUX<0]=0

    # muxOrderedColumns = []
    # for i in CM_MUX:
    #     muxOrderedColumns.append(f'CM_{i}_0')
    #     muxOrderedColumns.append(f'CM_{i}_1')
    # dfCommonModeMuxed = dfCommonMode[muxOrderedColumns]
    # #rename outputs, for convenientgrouping
    # dfCommonModeMuxed.columns = [f'CM_{i}' for i in range(24)]

    # #not an exact average, matches bit-shifting mean method from spec
    # if isHDM:
    #     dfCommonModeMuxed['CM_AVG'] = (dfCommonModeMuxed.sum(axis=1)*171/4096).astype(int)
    # else:
    #     dfCommonModeMuxed['CM_AVG'] = (dfCommonModeMuxed.sum(axis=1)*171/2048).astype(int)

    # #common mode average groupings
    # cm_avg_group = [['CM_0','CM_1','CM_2','CM_3'],
    #                 ['CM_4','CM_5','CM_6','CM_7'],
    #                 ['CM_8','CM_9','CM_10','CM_11'],
    #                 ['CM_12','CM_13','CM_14','CM_15'],
    #                 ['CM_16','CM_17','CM_18','CM_19'],
    #                 ['CM_20','CM_21','CM_22','CM_23']]

    # for i in range(6):
    #     dfCommonModeMuxed[f'CM_AVG_{i}'] = (dfCommonModeMuxed[cm_avg_group[i]].sum(axis=1)/4).astype(int)

    # return dfCommonModeMuxed[['CM_AVG'] + [f'CM_AVG_{i}' for i in range(6)]]

