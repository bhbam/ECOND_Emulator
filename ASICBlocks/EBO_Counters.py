import pandas as pd
import numpy as np

from numba import njit, jit

def eboCounter(dfFastCommands, BCR_Bucket_Default=3513):

    df = pd.DataFrame({'Event':np.nan,'Bunch':np.nan,'Orbit':np.nan},index=dfFastCommands.index)

    #always just set first value to 0, to have something there until resets
    df.loc[0,['Orbit','Bunch']] = 0
    df.loc[0,'Event'] = 1

    #on hard reset (reset_b==0), set orbit and bucket to 0, event to 1
    df.loc[dfFastCommands.HardReset==0,['Orbit','Bunch']]=0
    df.loc[dfFastCommands.HardReset==0,['Event']]=1

    #on soft reset, set event to 1
    df.loc[dfFastCommands.SoftReset==0,['Event']]=1

    #on BCR reset bunch number to BCR_Bucket_Default register value
    df.loc[dfFastCommands.BCR==1,'Bunch']=BCR_Bucket_Default

    #on OCR reset orbit number to 0
    df.loc[dfFastCommands.OCR==1,'Orbit']=0

    #on ChipSync reset bunch number to BCR_Bucket_Default register value and orbit number to 0, event to 1
    df.loc[dfFastCommands.ChipSync==1,'Bunch']=BCR_Bucket_Default
    df.loc[dfFastCommands.ChipSync==1,'Orbit']=0
    df.loc[dfFastCommands.ChipSync==1,'Event']=1

    #on ECR or EBR, set event to 1
    df.loc[dfFastCommands.ECR==1,'Event']=1
    df.loc[dfFastCommands.EBR==1,'Event']=1
    
    #increment all null cells
    df['Bunch'] = (df.Bunch.ffill() + df.groupby(df.Bunch.notnull().cumsum()).cumcount()).astype(int)%3564

    #increment orbit number if bunch counter wraps around
    def incrementOrbit(bunch, orbit):
        for i in range(1,len(bunch)):
            if np.isnan(orbit)[i]:
                if bunch[i]==0 and bunch[i-1]==3563:
                    orbit[i] = (orbit[i-1]+1)%8
                else:
                    orbit[i] = orbit[i-1]
        return orbit

    df['Orbit'] = incrementOrbit(df.Bunch.values, df.Orbit.values).astype(int)

    def incrementEvent(event, l1a):
        for i in range(1,len(event)):
            if np.isnan(event)[i]:
                if l1a[i-1]==1:
                    event[i] = (event[i-1]+1)%64
                else:
                    event[i] = event[i-1]
        return event

    df['Event'] = incrementEvent(df.Event.values, dfFastCommands.L1A.values).astype(int)
    
    return df