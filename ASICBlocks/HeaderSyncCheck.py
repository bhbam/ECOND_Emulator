import numpy as np
import pandas as pd

def findHeaderWord(vals, N_eRx_Thresh):

    firstByte = vals.astype('<U8').view('<U1')[::8]
    lastByte  = vals.astype('<U8').view('<U1')[7::8]

    hasHeader = (firstByte=='5') & (lastByte=='5')

    headerVote = (hasHeader.sum(axis=1) >= N_eRx_Thresh)

    headerTrailerErr = np.zeros_like(vals)
    headerTrailerErr[headerVote] = ~(hasHeader[headerVote])

    return headerVote.astype(int), headerTrailerErr

##attempt at implementing something to match specifications in Specification_for_the_Sync_Check_Block.pdf
def checkSync(df, idlePattern, idleHeader, idleHeaderBC0, N_threshold):
    sync = (df.isin([f'{idleHeader}{idlePattern}',f'{idleHeaderBC0}{idlePattern}']).sum(axis=1)>N_threshold).astype(int)
    return pd.DataFrame(sync,columns=['GoodSyncWord'])

def headerSyncCheck(df, idlePattern='CCCCCCC', idleHeader='A', idleHeaderBC0='9', MatchThreshold=9):
    dfSyncHeader = checkSync(df, idlePattern, idleHeader, idleHeaderBC0, MatchThreshold)
    headerInfo = findHeaderWord(df.values,MatchThreshold)

    dfSyncHeader['GoodHeaderWord'] = headerInfo[0]
    dfSyncHeader[[f'HeaderError_eRx{i}' for i in range(12)]] = pd.DataFrame(headerInfo[1])
    
    return dfSyncHeader