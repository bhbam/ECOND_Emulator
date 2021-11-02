import numpy as np
import pandas as pd

def checkWatchDogs(_history, watchDogLimitMask, watchdog_Enables):

    LastOne = _history[:,0]
    Last2 = _history[:,:2].all(axis=1)
    Last4 = _history[:,:4].all(axis=1)
    Last8 = _history[:,:8].all(axis=1)
    Last32 = _history.all(axis=1)
    EightOf32 = _history.sum(axis=1)>=8
    SixteenOf32 = _history.sum(axis=1)>=16
    TwentyFourOf32 = _history.sum(axis=1)>=24

    watchDogStatuses = np.array([LastOne, Last2, Last4, Last8, Last32, EightOf32, SixteenOf32, TwentyFourOf32]).T

    #alert if status is active and not masked, and watchdog itself is enabled
    alerts = (watchDogStatuses & watchDogLimitMask).any(axis=1) & (watchdog_Enables==1)
    return alerts


def ResetRequests(df_RegisterArrays, 
                  dfFastCommands,
                  packetComplete,
                  I2C_WO_Watchdog_Cap_Clear,
                  watchdog_Limits,
                  watchdog_Enables,
                  requestSelect_A,
                  requestSelect_B
                 ):

    watchDogAlerts = np.zeros(53,dtype=bool)
    resetRequests = np.zeros(2,dtype=bool)
    watchDogHistory = np.zeros((53,32),dtype=int)

    #split limits into masks, bit0 is lastOne, bit7 is 24-of-32
    watchDogLimitMask = np.array([(watchdog_Limits>>i)&1 for i in range(8)]).T==1

    N = len(df_RegisterArrays)
    
    #build error statuses here (True = Error State,  = Good State)
    Packet_Veto = np.zeros(N,dtype=bool)   #NEEDS TO BE IMPLEMENTED
    EBO = ((df_RegisterArrays.Event_Status.values>>3)&1)==0
    HT = ((df_RegisterArrays.Event_Status.values>>5)&1)==0
    Match = ((df_RegisterArrays.Event_Status.values>>1)&1)==0
    EventExpected = ((df_RegisterArrays.Event_Status.values>>6)&1)==0

    Ham_eRx = [~(df_RegisterArrays[f'Hamming_eRx{i}'].values==0) for i in range(12)]
    CRC_eRx   = [(df_RegisterArrays[f'SubpacketStatus_eRx{i}'].values&1)==0 for i in range(12)]
    EBO_eRx = [((df_RegisterArrays[f'SubpacketStatus_eRx{i}'].values>>1)&1)==0 for i in range(12)]
    HT_eRx  = [((df_RegisterArrays[f'SubpacketStatus_eRx{i}'].values>>2)&1)==0 for i in range(12)]

    #order chosen to match order of reset request mask bits (lsb of reset_request i2c is packet_veto)
    errorStatuses = np.array([Packet_Veto, EventExpected, HT, EBO, Match] + Ham_eRx + CRC_eRx + EBO_eRx + HT_eRx)

    dfResetRequests = pd.DataFrame({'FC_Clear':(dfFastCommands[['ChipSync','EBR','ECR','LinkResetRocD']]==1).any(axis=1) | (dfFastCommands[['HardReset','SoftReset']]==0).any(axis=1)})
    dfResetRequests['I2C_Clear'] = I2C_WO_Watchdog_Cap_Clear==1
    dfResetRequests['Clear'] = dfResetRequests.FC_Clear | dfResetRequests.I2C_Clear

    clear = dfResetRequests.Clear.values

    watchDogStatus = np.zeros((N,53),dtype=int)
    resetStatus = np.zeros((N,2),dtype=int)

    for i in range(N):
        if clear[i]:
            watchDogHistory = np.zeros((53,32),dtype=int)
            watchDogAlerts = np.zeros(53,dtype=bool)
            resetRequests = np.zeros(2,dtype=bool)
        if packetComplete[i]==1:
            #move FIFO over one, adding newest event to beginning
            watchDogHistory[:,1:] = watchDogHistory[:,:-1]
            watchDogHistory[:,0] = errorStatuses[:,i]

            #check watchdog alert statuses
            currentWatchDogAlerts = checkWatchDogs(watchDogHistory, watchDogLimitMask, watchdog_Enables)
            #or with currently active alerts
            watchDogAlerts = watchDogAlerts | currentWatchDogAlerts

            resetRequests = np.array([watchDogAlerts & (requestSelect_A==1),
                                      watchDogAlerts & (requestSelect_B==1)]).any(axis=1)

        watchDogStatus[i] = watchDogAlerts
        resetStatus[i] = resetRequests

    df = pd.DataFrame(resetStatus,columns=['ResetRequest_A', 'ResetRequest_B'])

    columns=['WatchDog_PacketVeto','WatchDog_EBO','WatchDog_HT','WatchDog_Match','WatchDog_UnexpectedEvent']
    columns += [f'WatchDog_Hamming_eRx{i}' for i in range(12)]
    columns += [f'WatchDog_CRC_eRx{i}' for i in range(12)]
    columns += [f'WatchDog_EBO_eRx{i}' for i in range(12)]
    columns += [f'WatchDog_HT_eRx{i}' for i in range(12)]
    df[columns] = pd.DataFrame(watchDogStatus,columns=columns)        

    return df