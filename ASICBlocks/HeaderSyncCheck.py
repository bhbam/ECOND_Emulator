import numpy as np
import pandas as pd

def findHeaderWord(vals, N_eRx_Thresh, activeChannelMask):

    firstByte = vals.astype('<U8').view('<U1')[::8, activeChannelMask]
    lastByte  = vals.astype('<U8').view('<U1')[7::8, activeChannelMask]

    hasHeader = (firstByte=='5') & (lastByte=='5')

    headerVote = (hasHeader.sum(axis=1) >= N_eRx_Thresh)

    return headerVote.astype(int)

##attempt at implementing something to match specifications in Specification_for_the_Sync_Check_Block.pdf
def checkSync(df, idlePattern, idleHeader, idleHeaderBC0, N_threshold, activeChannelMask):
    headerPatterns = [f'{idleHeader}{idlePattern}',f'{idleHeaderBC0}{idlePattern}']
    sync = (np.isin(df.values[:,activeChannelMask],headerPatterns).sum(axis=1) >= N_threshold)
    return pd.DataFrame(sync.astype(int),columns=['GoodSyncWord'])

def headerSyncCheck(df, idlePattern='CCCCCCC', idleHeader='A', idleHeaderBC0='9', MatchThreshold=9, activeChannelMask=np.array([True]*12)):
    dfSyncHeader = checkSync(df, idlePattern, idleHeader, idleHeaderBC0, MatchThreshold, activeChannelMask)
    headerInfo = findHeaderWord(df.values,MatchThreshold, activeChannelMask)

    dfSyncHeader['GoodHeaderWord'] = headerInfo

    return dfSyncHeader
