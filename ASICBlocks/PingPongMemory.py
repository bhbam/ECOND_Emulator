import numpy as np
import pandas as pd

channelDataStates = ['CH0',   'CH1',  'CH2',  'CH3',  'CH4',  'CH5',
                     'CH6',   'CH7',  'CH8',  'CH9', 'CH10', 'CH11',
                     'CH12', 'CH13', 'CH14', 'CH15', 'CH16', 'CH17',
                     'CALIB',
                     'CH18', 'CH19', 'CH20', 'CH21', 'CH22', 'CH23',
                     'CH24', 'CH25', 'CH26', 'CH27', 'CH28', 'CH29',
                     'CH30', 'CH31', 'CH32', 'CH33', 'CH34', 'CH35']

channelNumMap = {x:i for i,x in enumerate(channelDataStates)}

def chMapToString(chMapData):
    chMaps = []
    for chMapeRx in chMapData:
        chMaps.append(''.join(map(str,chMapeRx)))
    return np.array(chMaps)


def PingPongMemory(dfFormattedData, dfHeader, df_ROC_DAQ_Control):
    writeToPong = df_ROC_DAQ_Control.PP_State.isin(['S1','S2']).values
    readFromPong = df_ROC_DAQ_Control.PP_State.isin(['S2','S3']).values

    write_PP_Index = writeToPong.astype(int)
    read_PP_Index = readFromPong.astype(int)

    State = df_ROC_DAQ_Control.StateText
    Data = dfFormattedData.values
    RegisterData = dfHeader.values

    PacketComplete = df_ROC_DAQ_Control.PacketComplete.values
    PP_ReadState = df_ROC_DAQ_Control.PP_ReadState.values

    ChNumber = np.vectorize(channelNumMap.get)(State)
    Ch=0

    N=len(State)
    SRAM_ChData = np.array(['0'*10]*2*12*37).reshape(2,37,12)
    SRAM_ChMap = np.zeros(2*12*37,dtype=int).reshape(2,37,12)
    PingPong_Registers = np.zeros((2,(RegisterData.shape[1])),dtype=int)


    SRAM_Output = np.array(['0000000000']*12*N,dtype='<U40').reshape(-1,12)
    outputData = np.array(['0000000000']*12,dtype='<U40')

    outputShape = list(RegisterData.shape)
    outputShape[1] += 12 #add 12 more slots, for channelMap
    Register_Output = np.zeros(outputShape,dtype=int)



    for i in np.arange(N):
        if not ChNumber[i] is None:
            Ch = ChNumber[i]

            SRAM_ChData[write_PP_Index[i],Ch] = Data[i,12:]
            SRAM_ChMap[write_PP_Index[i],Ch] = Data[i,:12]

        if PP_ReadState[i]=='CLK0':
            outputData[:4] = ['0000000000']*4
            outputData[4:] = SRAM_ChData[read_PP_Index[i],:8,0]
        elif PP_ReadState[i]=='CLK1':
            outputData = SRAM_ChData[read_PP_Index[i],8:20,0]
        elif PP_ReadState[i]=='CLK2':
            outputData = SRAM_ChData[read_PP_Index[i],20:32,0]
        elif PP_ReadState[i]=='CLK3':
            outputData[:5] = SRAM_ChData[read_PP_Index[i],32:,0]
            outputData[5:7] = ['0000000000']*2
            outputData[7:] = SRAM_ChData[read_PP_Index[i],:5,1]
        elif PP_ReadState[i]=='CLK4':
            outputData = SRAM_ChData[read_PP_Index[i],5:17,1]
        elif PP_ReadState[i]=='CLK5':
            outputData = SRAM_ChData[read_PP_Index[i],17:29,1]
        elif PP_ReadState[i]=='CLK6':
            outputData[:8] = SRAM_ChData[read_PP_Index[i],29:,1]
            outputData[8:10] = ['0000000000']*2
            outputData[10:] = SRAM_ChData[read_PP_Index[i],:2,2]
        elif PP_ReadState[i]=='CLK7':
            outputData = SRAM_ChData[read_PP_Index[i],2:14,2]
        elif PP_ReadState[i]=='CLK8':
            outputData = SRAM_ChData[read_PP_Index[i],14:26,2]
        elif PP_ReadState[i]=='CLK9':
            outputData[:11] = SRAM_ChData[read_PP_Index[i],26:,2]
            outputData[11:] = ['0000000000']
        elif PP_ReadState[i]=='CLK10':
            outputData[1:] = SRAM_ChData[read_PP_Index[i],:11,3]
        elif PP_ReadState[i]=='CLK11':
            outputData = SRAM_ChData[read_PP_Index[i],11:23,3]
        elif PP_ReadState[i]=='CLK12':
            outputData = SRAM_ChData[read_PP_Index[i],23:35,3]
        elif PP_ReadState[i]=='CLK13':
            outputData[:2] = SRAM_ChData[read_PP_Index[i],35:,3]
            outputData[2:4] = ['0000000000']*2
            outputData[4:] = SRAM_ChData[read_PP_Index[i],:8,4]
        elif PP_ReadState[i]=='CLK14':
            outputData = SRAM_ChData[read_PP_Index[i],8:20,4]
        elif PP_ReadState[i]=='CLK15':
            outputData = SRAM_ChData[read_PP_Index[i],20:32,4]
        elif PP_ReadState[i]=='CLK16':
            outputData[:5] = SRAM_ChData[read_PP_Index[i],32:,4]
            outputData[5:7] = ['0000000000']*2
            outputData[7:] = SRAM_ChData[read_PP_Index[i],:5,5]
        elif PP_ReadState[i]=='CLK17':
            outputData = SRAM_ChData[read_PP_Index[i],5:17,5]
        elif PP_ReadState[i]=='CLK18':
            outputData = SRAM_ChData[read_PP_Index[i],17:29,5]
        elif PP_ReadState[i]=='CLK19':
            outputData[:8] = SRAM_ChData[read_PP_Index[i],29:,5]
            outputData[8:10] = ['0000000000']*2
            outputData[10:] = SRAM_ChData[read_PP_Index[i],:2,6]
        elif PP_ReadState[i]=='CLK20':
            outputData = SRAM_ChData[read_PP_Index[i],2:14,6]
        elif PP_ReadState[i]=='CLK21':
            outputData = SRAM_ChData[read_PP_Index[i],14:26,6]
        elif PP_ReadState[i]=='CLK22':
            outputData[:11] = SRAM_ChData[read_PP_Index[i],26:,6]
            outputData[11:] = ['0000000000']
        elif PP_ReadState[i]=='CLK23':
            outputData[:1] = ['0000000000']
            outputData[1:] = SRAM_ChData[read_PP_Index[i],:11,7]
        elif PP_ReadState[i]=='CLK24':
            outputData = SRAM_ChData[read_PP_Index[i],11:23,7]
        elif PP_ReadState[i]=='CLK25':
            outputData = SRAM_ChData[read_PP_Index[i],23:35,7]
        elif PP_ReadState[i]=='CLK26':
            outputData[:2] = SRAM_ChData[read_PP_Index[i],35:,7]
            outputData[2:4] = ['0000000000']*2
            outputData[4:] = SRAM_ChData[read_PP_Index[i],:8,8]
        elif PP_ReadState[i]=='CLK27':
            outputData = SRAM_ChData[read_PP_Index[i],8:20,8]
        elif PP_ReadState[i]=='CLK28':
            outputData = SRAM_ChData[read_PP_Index[i],20:32,8]
        elif PP_ReadState[i]=='CLK29':
            outputData[:5] = SRAM_ChData[read_PP_Index[i],32:,8]
            outputData[5:7] = ['0000000000']*2
            outputData[7:] = SRAM_ChData[read_PP_Index[i],:5,9]
        elif PP_ReadState[i]=='CLK30':
            outputData = SRAM_ChData[read_PP_Index[i],5:17,9]
        elif PP_ReadState[i]=='CLK31':
            outputData = SRAM_ChData[read_PP_Index[i],17:29,9]
        elif PP_ReadState[i]=='CLK32':
            outputData[:8] = SRAM_ChData[read_PP_Index[i],29:,9]
            outputData[8:10] = ['0000000000']*2
            outputData[10:] = SRAM_ChData[read_PP_Index[i],:2,10]
        elif PP_ReadState[i]=='CLK33':
            outputData = SRAM_ChData[read_PP_Index[i],2:14,10]
        elif PP_ReadState[i]=='CLK34':
            outputData = SRAM_ChData[read_PP_Index[i],14:26,10]
        elif PP_ReadState[i]=='CLK35':
            outputData[:11] = SRAM_ChData[read_PP_Index[i],26:,10]
            outputData[11:] = ['0000000000']
        elif PP_ReadState[i]=='CLK36':
            outputData[:1] = ['0000000000']
            outputData[1:] =  SRAM_ChData[read_PP_Index[i],:11,11]
        elif PP_ReadState[i]=='CLK37':
            outputData = SRAM_ChData[read_PP_Index[i],11:23,11]
        elif PP_ReadState[i]=='CLK38':
            outputData = SRAM_ChData[read_PP_Index[i],23:35,11]
        elif PP_ReadState[i]=='CLK39':
            outputData[:2] = SRAM_ChData[read_PP_Index[i],35:,11]
            outputData[2:] = ['0000000000']*10

        PingPong_Registers[write_PP_Index[i]] = RegisterData[i]
        Register_Output[i,:-12] = PingPong_Registers[read_PP_Index[i]]

        chMapString = chMapToString(SRAM_ChMap[read_PP_Index[i]].T)
        Register_Output[i,-12:] = np.vectorize(int)(chMapString,2)

        SRAM_Output[i] = outputData

    df_RegisterArrays = pd.DataFrame(Register_Output,columns=list(dfHeader.columns)+[f'Channel_Map_{i_eRx}' for i_eRx in range(12)])
    df_SRAM_Out = pd.DataFrame(SRAM_Output[:,::-1],columns=[f'SRAM_Out_{i}' for i in range(12)[::-1]])

    return df_SRAM_Out, df_RegisterArrays
