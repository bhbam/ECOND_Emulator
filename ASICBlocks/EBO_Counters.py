import pandas as pd
import numpy as np

def eboCounter(dfFastCommands, BCR_Bucket_Default=3513):

    HardReset = dfFastCommands.HardReset.values
    SoftReset = dfFastCommands.SoftReset.values
    BCR = dfFastCommands.BCR.values
    OCR = dfFastCommands.OCR.values
    ChipSync = dfFastCommands.ChipSync.values
    ECR = dfFastCommands.ECR.values
    EBR = dfFastCommands.EBR.values
    L1A = dfFastCommands.L1A.values

    N = len(dfFastCommands)

    arr_Event = np.zeros(N,dtype=int)
    arr_Bunch = np.zeros(N,dtype=int)
    arr_Orbit = np.zeros(N,dtype=int)

    Event=0
    Bunch=0
    Orbit=0

    for i in range(N):
        arr_Event[i] = Event
        arr_Bunch[i] = Bunch
        arr_Orbit[i] = Orbit

        if HardReset[i]==0:
            Event=1
            Bunch=0
            Orbit=0

        elif SoftReset[i]==0:
            Event==1

        elif BCR[i]==1:
            Bunch=BCR_Bucket_Default

        elif OCR[i]==1:
            Orbit=0

        elif ChipSync[i]==1:
            Event=1
            Bunch=BCR_Bucket_Default
            Orbit=0

        elif ECR[i]==1 or EBR[i]==1:
            Event=1

        else:
            Bunch += 1
            if Bunch >= 3564:
                Bunch = 0
                Orbit += 1
                if Orbit >= 8:
                    Orbit = 0
            if L1A[i-1]==1:
                Event += 1
                if Event >= 64:
                    Event = 0

    return pd.DataFrame({'Event':arr_Event, 'Bunch':arr_Bunch, 'Orbit':arr_Orbit})
