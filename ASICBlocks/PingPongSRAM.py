import numpy as np
import pandas as pd

def fillSRAM(dfChannelData):

    CLK = dfChannelData.CLK.unique()

    #drop BX without data
    df = dfChannelData.loc[dfChannelData.Ch>-1]

    #capture the CLK when channel 0 starts, for determining the flipping of ping/pong status
    CLK0 = df[df.Ch==0].CLK.unique()
    pingPong = np.arange(len(CLK0))&1
    dfPingPong = pd.DataFrame({'PingPong':pingPong},index=CLK0)

    #index by SRAM, Channel, and Clock cycle
    df.set_index(['SRAM','Ch','CLK'], inplace=True)

    df.sort_index(inplace=True)

    dfSRAM = pd.DataFrame(index=CLK)
    for i_eRx in range(12):
        x = df.loc[i_eRx].reset_index()

        # fill in alternating PING/PING status
        x.set_index('CLK',inplace=True)
        x.sort_index(inplace=True)
        x['PingPong'] = dfPingPong['PingPong']
        x['PingPong'] = x.PingPong.fillna(method='ffill').astype(int)
        x.reset_index(inplace=True)

        # get values that will go into PING SRAMs
        # pivot, create a new column for each unique channel, keeping track of which CLK cycle that data correpsonds to
        x0 = x[x.PingPong==0].pivot(index='CLK',columns='Ch',values='ChData')
        x0.columns = [f'PING_SRAM{i_eRx}_Ch{i}' for i in x0.columns]
        # add these columns to the full SRAM database
        dfSRAM[x0.columns] = x0

        # get values that will go into PONG SRAMs
        x1 = x[x.PingPong==1].pivot(index='CLK',columns='Ch',values='ChData')
        x1.columns = [f'PONG_SRAM{i_eRx}_Ch{i}' for i in x1.columns]
        dfSRAM[x1.columns] = x1

    # forward fill the dfSRAM dataframe
    # each column in this database corresponds to a different address in the SRAM, so forward-fill is just saying to keep the same value until it gets changed
    dfSRAM = dfSRAM.fillna(method='ffill').fillna('0'*40)

    return dfSRAM
