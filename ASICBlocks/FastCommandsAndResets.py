import pandas as pd

#list of fast commands to process taken from lists here
#   https://gitlab.cern.ch/cmshgcalasic/econd_rtl/-/blob/master/constants/Project_constants.sv#L1840-1869
#   https://indico.cern.ch/event/882853/contributions/3722675/attachments/1979350/3295476/Fast_Commands_Jan20.pdf

L1A_CommandList = ['FASTCMD_L1A',
                   'FASTCMD_L1A_PREL1A',
                   'FASTCMD_L1A_NZS',
                   'FASTCMD_L1A_NZS_PREL1A',
                   'FASTCMD_L1A_BCR',
                   'FASTCMD_L1A_BCR_PREL1A',
                   'FASTCMD_L1A_CALPULSEINT',
                   'FASTCMD_L1A_CALPULSEEXT',
                   'FASTCMD_L1A_CALPULSEINT_PREL1A',
                   'FASTCMD_L1A_CALPULSEEXT_PREL1A']

NZS_CommandList = ['FASTCMD_L1A_NZS',
                   'FASTCMD_L1A_NZS_PREL1A']

BCR_CommandList = ['FASTCMD_L1A_BCR',
                   'FASTCMD_L1A_BCR_PREL1A',
                   'FASTCMD_BCR',
                   'FASTCMD_BCR_PREL1A',
                   'FASTCMD_BCR_OCR']

ChipSync_CommandList = ['FASTCMD_CHIPSYNC']

EBR_CommandList = ['FASTCMD_EBR']

ECR_CommandList = ['FASTCMD_ECR']

OCR_CommandList = ['FASTCMD_BCR_OCR']

LinkResetRocD_CommandList = ['FASTCMD_LINKRESETROCD']

LinkResetEconD_CommandList = ['FASTCMD_LINKRESETECOND']

def processFastCommands(df_Inputs):
    df_FastCommands = df_Inputs[['FastCommand','HardReset','SoftReset']].copy()

    df_FastCommands['L1A'] = df_FastCommands.FastCommand.isin(L1A_CommandList).astype(int)
    df_FastCommands['NZS'] = df_FastCommands.FastCommand.isin(NZS_CommandList).astype(int)
    df_FastCommands['BCR'] = df_FastCommands.FastCommand.isin(BCR_CommandList).astype(int)
    df_FastCommands['ChipSync'] = df_FastCommands.FastCommand.isin(ChipSync_CommandList).astype(int)
    df_FastCommands['EBR'] = df_FastCommands.FastCommand.isin(EBR_CommandList).astype(int)
    df_FastCommands['ECR'] = df_FastCommands.FastCommand.isin(ECR_CommandList).astype(int)
    df_FastCommands['OCR'] = df_FastCommands.FastCommand.isin(OCR_CommandList).astype(int)
    df_FastCommands['LinkResetRocD'] = df_FastCommands.FastCommand.isin(LinkResetRocD_CommandList).astype(int)
    df_FastCommands['LinkResetEconD'] = df_FastCommands.FastCommand.isin(LinkResetEconD_CommandList).astype(int)

    return df_FastCommands.drop('FastCommand',axis=1)
