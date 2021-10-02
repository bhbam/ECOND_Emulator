import pandas as pd
import numpy as np

from .HeaderSyncCheck import headerSyncCheck
from .EBO_Counters import eboCounter


packetProcessing = {'EMPTYHEADER':'HOME',
                    'STANDARDHEADER':'CM',
                    'UNEXPECTEDHEADER':'CM',
                    'CM':'CH0',
                    'CH0':'CH1',
                    'CH1':'CH2',
                    'CH2':'CH3',
                    'CH3':'CH4',
                    'CH4':'CH5',
                    'CH5':'CH6',
                    'CH6':'CH7',
                    'CH7':'CH8',
                    'CH8':'CH9',
                    'CH9':'CH10',
                    'CH10':'CH11',
                    'CH11':'CH12',
                    'CH12':'CH13',
                    'CH13':'CH14',
                    'CH14':'CH15',
                    'CH15':'CH16',
                    'CH16':'CH17',
                    'CH17':'CALIB',
                    'CALIB':'CH18',
                    'CH18':'CH19',
                    'CH19':'CH20',
                    'CH20':'CH21',
                    'CH21':'CH22',
                    'CH22':'CH23',
                    'CH23':'CH24',
                    'CH24':'CH25',
                    'CH25':'CH26',
                    'CH26':'CH27',
                    'CH27':'CH28',
                    'CH28':'CH29',
                    'CH29':'CH30',
                    'CH30':'CH31',
                    'CH31':'CH32',
                    'CH32':'CH33',
                    'CH33':'CH34',
                    'CH34':'CH35',
                    'CH35':'CRC',
                    'CRC':'HOME',
                   }

def L1A_Predictor(L1A,
                  L1A_latency_HGCROC,
                  L1A_latency_Aligner,
                  N=-1
                 ):

    if N==-1:
        N=len(L1A)
    arr_Header_Predictor=np.array([0]*N,dtype=int)

    L1A_delay_counter = 0
    L1A_predictor_count = 0
    Total_L1A_Latency = L1A_latency_HGCROC + L1A_latency_Aligner
    L1A_withLatency = np.zeros_like(L1A)
    L1A_withLatency[Total_L1A_Latency:] = L1A[:-1*Total_L1A_Latency]

    for i in range(N):
        Header_Predictor=0
        if L1A_withLatency[i]==1:
            L1A_predictor_count += 1 #count how many L1A's would be in the predictor fifo

        if L1A_delay_counter==0:
            if L1A_predictor_count>0:
                Header_Predictor = 1
                L1A_predictor_count -= 1
                L1A_delay_counter = 41
        else:
            L1A_delay_counter -= 1
        arr_Header_Predictor[i] = Header_Predictor

    return arr_Header_Predictor

def ROC_SM_L1A_PREDICTOR(simpleMode,
                         GoodHeaderWord,
                         GoodSyncWord,
                         LinkReset,
                         ChipSync,
                         EBR,
                         L1A,
                         NZS,
                         Event,
                         Bunch,
                         Orbit,
                         HardReset,
                         SoftReset,
                         L1A_Prediction,
                         #L1A_latency_HGCROC,
                         #L1A_latency_Aligner,
                         ALIGNMENT_STEP1_PERIOD=255,
                         ALIGNMENT_STEP2_PERIOD=1,
                         N=-1):

    if N==-1:
        N=len(GoodHeaderWord)

    arr_state=np.array(['']*N,dtype='<U16')
    arr_topEvent=np.array([0]*N,dtype=int)
    arr_topBunch=np.array([0]*N,dtype=int)
    arr_topOrbit=np.array([0]*N,dtype=int)
    arr_topNZS=np.array([0]*N,dtype=int)
    arr_L1AFifoEmpty=np.array([False]*N)
    arr_L1AFifoFull=np.array([False]*N)
    
    L1AFIFO = np.array([[-1,-1,-1,-1]]*129)
    writePointer = 0

    state='HOME'
    L1A_FIFO_EMPTY=True
    L1A_FIFO_FULL=False
    Top_Event=-1
    Top_Bunch=-1
    Top_Orbit=-1
    Top_NZS=-1
    Header_Predictor=0

    AlignmentCounter=-1

    for i in range(N):

        #ROCSM
        if state == 'HOME':
            if not simpleMode:
                if (L1A_Prediction[i]==1) and (GoodHeaderWord[i]==0):
                    state='EMPTYHEADER'
                elif (L1A_Prediction[i]==1) and (GoodHeaderWord[i]==1):
                    state='STANDARDHEADER'
                elif (L1A_Prediction[i]==0) and (GoodHeaderWord[i]==1):
                    state='UNEXPECTEDHEADER'
                elif (ChipSync[i]==1) or (EBR[i]==1):
                    state='CSYNC'
                elif (LinkReset[i]==1) and (GoodSyncWord[i]==1):
                    state='ALIGNRESET'
                else:
                    state='HOME'
            else:
                if (GoodSyncWord[i]==0) and (GoodHeaderWord[i]==1) and (not L1A_FIFO_EMPTY):
                    state='STANDARDHEADER'
                elif (GoodSyncWord[i]==0) and (GoodHeaderWord[i]==1) and (L1A_FIFO_EMPTY):
                    state='UNEXPECTEDHEADER'
                elif (ChipSync[i]==1) or (EBR[i]==1):
                    state='CSYNC'
                elif (LinkReset[i]==1) and (GoodSyncWord[i]==1):
                    state='ALIGNRESET'
                else:
                    state='HOME'
        elif state == 'CSYNC':
            if GoodSyncWord[i]==1:
                state='HOME'
            else:
                state='CSYNC'
        elif state == 'ALIGNRESET':
            AlignmentCounter=0
            state='ALIGNSTEP1'
        elif state == 'ALIGNSTEP1':
            if AlignmentCounter>ALIGNMENT_STEP1_PERIOD:
                state='ALIGNSTEP2'
                AlignmentCounter=0
        elif state == 'ALIGNSTEP2':
            if AlignmentCounter>ALIGNMENT_STEP2_PERIOD:
                state='HOME'
                AlignmentCounter=-1
        elif state in packetProcessing:
            state=packetProcessing[state]
        else:
            print('Unknown State', state)
            #for now, just go back to home
            state='HOME'

        if AlignmentCounter>=0:
            AlignmentCounter += 1

        #L1A FIFO
        if ((HardReset[i]==0) or (SoftReset[i]==0) or (EBR[i]==1) or (ChipSync[i]==1)):
            L1AFIFO = np.array([[-1,-1,-1,-1]]*129)
            writePointer = 0
            L1A_FIFO_EMPTY=True

        if (L1A[i]==1):
            L1AFIFO[writePointer] = [Event[i], Bunch[i], Orbit[i], NZS[i]]
            writePointer += 1

        if state=='CRC':
            Top_Event, Top_Bunch, Top_Orbit, Top_NZS = L1AFIFO[0]
            #strip of top EBO
            L1AFIFO[:-1] = L1AFIFO[1:]
            writePointer = max(writePointer-1, 0)
        L1A_FIFO_EMPTY = (L1AFIFO==-1).all()
        L1A_FIFO_FULL = ~(L1AFIFO==-1).any()

        #dump into arrays
        arr_state[i]=state
        arr_topEvent[i]=Top_Event
        arr_topBunch[i]=Top_Bunch
        arr_topOrbit[i]=Top_Orbit
        arr_topNZS[i]=Top_NZS
        arr_L1AFifoEmpty[i]=L1A_FIFO_EMPTY
        arr_L1AFifoFull[i]=L1A_FIFO_FULL
            
    return arr_state, arr_topEvent, arr_topBunch, arr_topOrbit, arr_topNZS, arr_L1AFifoEmpty, arr_L1AFifoFull

def ROC_DAQ_CONTROL(dfAlignerOutput,
                    dfFastCommands,
                    idlePattern,
                    idleHeader,
                    idleHeaderBC0,
                    BCR_Bucket_Default,
                    L1A_HGCROC_Latency,
                    L1A_Aligner_Latency,
                    MatchThreshold,
                    ROC_SM_simpleMode,
                    Alignment_Step1_Period,
                    Alignment_Step2_Period):

    
#  *          I2C_RW_Active_Channels  (12-bit programmable number indicating which channels are active)
#  *          I2C_RW_badWord_Threshold    (8-bit programmable number indicating the maximum number of badWords allowed before errorFlag_MissedPkt)
#  *          I2C_RW_Align1Count      (15-bit Number of steps in the Align1 Count)



    dfHeaderSync = headerSyncCheck(dfAlignerOutput, 
                                   idlePattern=idlePattern, 
                                   idleHeader=idleHeader,
                                   idleHeaderBC0=idleHeaderBC0, 
                                   MatchThreshold=MatchThreshold)

    dfEBO = eboCounter(dfFastCommands, BCR_Bucket_Default)

    dfInput = dfFastCommands.merge(dfEBO,left_index=True,right_index=True)
    dfInput[['GoodSyncWord','GoodHeaderWord']] = dfHeaderSync[['GoodSyncWord','GoodHeaderWord']]


    L1A_Header_Prediction = L1A_Predictor(L1A = dfInput.L1A.values, 
                                          L1A_latency_HGCROC = L1A_HGCROC_Latency, 
                                          L1A_latency_Aligner = L1A_Aligner_Latency)


    ROC_SM_Outputs = ROC_SM_L1A_PREDICTOR(simpleMode = ROC_SM_simpleMode,
                                          GoodHeaderWord = dfInput.GoodHeaderWord.values,
                                          GoodSyncWord = dfInput.GoodSyncWord.values,
                                          LinkReset = dfInput.LinkResetRocD.values,
                                          ChipSync = dfInput.ChipSync.values,
                                          EBR = dfInput.EBR.values,
                                          L1A = dfInput.L1A.values,
                                          NZS = dfInput.NZS.values,
                                          Event = dfInput.Event.values,
                                          Bunch = dfInput.Bunch.values,
                                          Orbit = dfInput.Orbit.values,
                                          HardReset = dfInput.HardReset.values,
                                          SoftReset = dfInput.SoftReset.values,
                                          L1A_Prediction=L1A_Header_Prediction,
                                          ALIGNMENT_STEP1_PERIOD=Alignment_Step1_Period,
                                          ALIGNMENT_STEP2_PERIOD=Alignment_Step2_Period)

    State, TopEvent, TopBunch, TopOrbit, TopNZS, L1AFifoEmpty, L1AFifoFull = ROC_SM_Outputs

    df_ROC_DAQ_Control = pd.DataFrame({'GoodHeaderWord' : dfInput.GoodHeaderWord.values,
                  'GoodSyncWord' : dfInput.GoodSyncWord.values,
                  'Event' : dfInput.Event.values,
                  'Bunch' : dfInput.Bunch.values,
                  'Orbit' : dfInput.Orbit.values,
                  'State' : State,
                  'TopEvent' : TopEvent,
                  'TopBunch' : TopBunch,
                  'TopOrbit' : TopOrbit,
                  'TopNZS' : TopNZS,
                  'L1AFifoEmpty' : L1AFifoEmpty,
                  'L1AFifoFull' : L1AFifoFull,
                  'Header_Predictor' : L1A_Header_Prediction,
                  'Flag_Home' : (State=='HOME').astype(int),
                  'Flag_Header' : ((State=='STANDARDHEADER')|(State=='UNEXPECTEDHEADER')).astype(int),
                  'Flag_Unexpected' : (State=='UNEXPECTEDHEADER').astype(int),
                  'Flag_Packet_Done' : (State=='CRC').astype(int),
                  'Flag_Alignment_Done' : (State=='ALIGNSTEP2').astype(int),
                  'Flag_Csynch' : (State=='CSYNC').astype(int),
                 },
                 index=dfInput.index
                )
    
    return df_ROC_DAQ_Control