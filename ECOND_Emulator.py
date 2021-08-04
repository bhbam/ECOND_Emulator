import pandas as pd
import numpy as np

from ASICBlocks.eLinkProcessor import eLinkProcessor
from ASICBlocks.PingPongSRAM import fillSRAM

#load eRx dataframe from CSV files
#eRxInputs = pd.read_csv('../ECOND_ROC_Emulator/rocData/ROC_DAQ_10692fc_200L1As-fixedfreq50_wbcr.csv',comment='#',header=None)
eRxInputs = pd.read_csv('ROC_DAQ_10692fc_200L1As-fixedfreq50_wbcr.csv',comment='#',header=None)
eRxInputs.columns = ['HardReset','SoftReset']+[f'eRx{i}'for i in range(12)]+['FastCommand']


dfHeader, dfCommonMode, dfCM_AVG, dfChannelData = eLinkProcessor(eRxInputs)

dfHeader.to_csv('output/header.csv')
dfCommonMode.to_csv('output/commonMode.csv')
dfCM_AVG.to_csv('output/commonModeAverages.csv')
dfChannelData.to_csv('output/channelData.csv')

dfSRAM = fillSRAM(dfChannelData)
dfSRAM.to_csv('output/sram.csv')
