import pandas as pd
import numpy as np
import crcmod

def eRx_crcCheck(df_eRx, df_ROC_SM):
    vals = df_eRx.values
    State = df_ROC_SM.StateText.values

    crc = crcmod.mkCrcFun(0x104c11db7,initCrc=0, xorOut=0, rev=False)
    N = len(State)
    remainder = np.zeros(12,dtype=np.int64)
    valsBytes = np.vectorize(bytes.fromhex)(vals)
    crcCompare = []
    for i in range(N):
        if State[i]=='HOME':
            remainder[:]=0
        elif State[i]=='CRC':
            crcCompare.append((np.vectorize(int)(vals[i],16)==remainder).astype(int))
        else:
            remainder = np.vectorize(crc)(valsBytes[i],remainder)
    return pd.DataFrame(crcCompare,columns=[f'CRC_eRx{i}' for i in range(12)], index=df_ROC_SM[State=='CRC'].index)
