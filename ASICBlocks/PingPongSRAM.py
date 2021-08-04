import numpy as np
import pandas as pd

def fillSRAM(dfChannelData):

    CLK = dfChannelData.CLK.unique()

    #drop BX without data
    df = dfChannelData.loc[dfChannelData.Ch>-1]

    #index by SRAM, Channel, and Clock cycle
    df.set_index(['SRAM','Ch','CLK'], inplace=True)

    df.sort_index(inplace=True)

    dfSRAM = pd.DataFrame(index=CLK)
    for i_eRx in range(12):
        x = df.loc[i_eRx].reset_index()
        x = x.pivot(index='CLK',columns='Ch',values='ChData')
        x.columns = [f'SRAM{i_eRx}_Ch{i}' for i in x.columns]
        dfSRAM[x.columns] = x

    dfSRAM = dfSRAM.fillna(method='ffill').fillna('0'*40)

    return dfSRAM
