import numpy as np
import pandas as pd

def simulateCounters(dfFC):

    Bunch_Count = np.zeros(len(dfFC),dtype=int)
    Orbit_Count = np.zeros(len(dfFC),dtype=int)
    Event_Count = np.zeros(len(dfFC),dtype=int)

    FifoOccupancy= np.zeros(len(dfFC),dtype=int)
    FifoTopEvent = np.zeros(len(dfFC),dtype=int)
    FifoTopBunch = np.zeros(len(dfFC),dtype=int)
    FifoTopOrbit = np.zeros(len(dfFC),dtype=int)
    FifoTopNZS   = np.zeros(len(dfFC),dtype=int)

    _bcr=dfFC.BCR.values
    _l1a=dfFC.L1A.values
    _nzs=dfFC.NZS.values
    _ecr=dfFC.ECR.values
    _ocr=dfFC.OCR.values
    _isHeader=dfFC.isHeader.values

    EBO_Fifo=[]


    for i in range(1,len(dfFC)):
        if _bcr[i-1]==1:
            Bunch_Count[i]=3514
        else:
            Bunch_Count[i]=Bunch_Count[i-1]+1

        if Bunch_Count[i]==3565:
            Orbit_Count[i] = (Orbit_Count[i-1]+1)%8
            Bunch_Count[i]=1
        else:
            Orbit_Count[i] = Orbit_Count[i-1]
        if _ocr[i-1]==1:
            Orbit_Count[i]=0
        if _l1a[i-1]==1:
            Event_Count[i] = (Event_Count[i-1]+1)%64
            EBO_Fifo.append([Event_Count[i-1],Bunch_Count[i-1],Orbit_Count[i-1],_nzs[i-1]])
        else:
            Event_Count[i]=Event_Count[i-1]

        if _ecr[i-1]==1:
            Event_Count[i] = 1

        FifoOccupancy[i]=len(EBO_Fifo)

        if len(EBO_Fifo)>0:
            FifoTopEvent[i]=EBO_Fifo[0][0]
            FifoTopBunch[i]=EBO_Fifo[0][1]
            FifoTopOrbit[i]=EBO_Fifo[0][2]
            FifoTopNZS[i]=EBO_Fifo[0][3]
        if _isHeader[i]:
            EBO_Fifo=EBO_Fifo[1:]


    return pd.DataFrame({'BunchCount':Bunch_Count,
                          'OrbitCount':Orbit_Count,
                          'EventCount':Event_Count,
                          'FifoOccupancy':FifoOccupancy,
                          'FifoTopEvent':FifoTopEvent,
                          'FifoTopBunch':FifoTopBunch,
                          'FifoTopOrbit':FifoTopOrbit,
                          'FifoTopNZS':FifoTopNZS},
                         index=dfFC.index)
