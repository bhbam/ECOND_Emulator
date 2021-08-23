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


def simpleSRAM(dfChannel, dfHeader, latency=40):
    df = dfChannel.copy().loc[dfChannel.Ch>-1]
    df['eRxCh'] = df.Ch + 100*df.eRx

    df['OutCLK'] = df.CLK - df.Ch - 2

    df = df.pivot(index='OutCLK',columns='eRxCh',values='ChData')

    df = df.merge(dfHeader.set_index('CLK'),left_index=True, right_index=True)

    columns = ['EvtPacketHeader_0', 'EvtPacketHeader_1']
    for i_eRx in range(12):
        columns += [f'SubpacketHeader_eRx{i_eRx}_0',f'SubpacketHeader_eRx{i_eRx}_1']
        columns += (np.arange(37) + i_eRx*100).tolist()

    df = df[columns]

    #there are 10 empty words at the end of each read cycle
    for i in range(10):
        df[f'pad{i}'] = ''


    clk = []
    for i in range(40):
        clk.append(df.index + i + latency)
    clk = np.array(clk).flatten()
    clk.sort()

    #group values into 12 value outputs
    x = df.values.reshape(-1,12)

    df2 = pd.DataFrame(x,columns=[f'SRAM_OUT_{i}' for i in range(12)], index=clk)
    df2.index.name='CLK'
    return df, df2


def simpleSRAMandFormatter(dfChannel, dfHeader, latency=40):
    df = dfChannel.copy().loc[dfChannel.Ch>-1]
    df['eRxCh'] = df.Ch + 100*df.eRx

    df['OutCLK'] = df.CLK - df.Ch - 2

    df = df.pivot(index='OutCLK',columns='eRxCh',values='ChData_Short')

    df = df.merge(dfHeader.set_index('CLK'),left_index=True, right_index=True)

    allcolumns = ['EvtPacketHeader_0', 'EvtPacketHeader_1']
    columns = ['EvtPacketHeader_0', 'EvtPacketHeader_1']
    words = df[columns].apply(lambda x: ''.join(x.values),axis=1)
    for i_eRx in range(12):
        columns = [f'SubpacketHeader_eRx{i_eRx}_0',f'SubpacketHeader_eRx{i_eRx}_1']
        columns += (np.arange(37) + i_eRx*100).tolist()
        allcolumns += columns
        subpacket = df[columns].apply(lambda x: ''.join(x.values),axis=1)

        paddingRequired=subpacket.str.len()%8
        paddingRequired[paddingRequired>0] = 8-paddingRequired
        padding = paddingRequired.apply(lambda x: '0'*x)

        words += subpacket + padding

#        df[f'subpacket_{i_eRx}'] = subpacket + padding

    df = df[allcolumns]# + [f'subpacket_{i_eRx}' for i_eRx in range(12)]]

    crcWord = '00ff00ff'
    words += crcWord

    idleWord = 'cccccccc'
    words += idleWord

    x = pd.DataFrame(words.apply(lambda x: [x[i:i+8] for i in range(0,len(x),8)]),columns=['Formatter_Out_N'])
    x['NumW'] = (words.str.len()/8).astype(int)
    return df, x
