import numpy as np
import pandas as pd

def Aligner(dfERx, LinkResetRocD, LinkResetOutput='00000000', AlignerLatency=1, LinkResetLength=256, DelayFillValue='ACCCCCCC'):
    linkResets = np.argwhere(LinkResetRocD==1).flatten()

    N = len(LinkResetRocD)
    dfChannelData = dfERx.copy()
    for idx in linkResets:
        dfChannelData.loc[idx:idx+LinkResetLength] = LinkResetOutput

    dfChannelData.columns = [f'Aligner_Out_Ch{i}' for i in range(12)]
    return dfChannelData.shift(AlignerLatency).fillna(DelayFillValue)
