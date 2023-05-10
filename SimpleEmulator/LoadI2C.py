import numpy as np
from .UnpackZSConstants import ZS_Constants_unpack, ZS_M1_Constants_unpack

# Turns a dictionary into a class
class Dict2Class(object):
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])

def parseI2C(i2cValues):

    i2c={}

    try:
        i2c['ZS_ce']=int(i2cValues.I2C_RW_eRX_ZS_CE_Constants_eRXxx,16)
    except:
        i2c['ZS_ce']=0x0

    ZS_Constants=i2cValues[[f'I2C_RW_eRX_ZS_Constants_eRX{i}' for i in range(12)]].apply(int,base=16).values
    ZS_M1_Constants=i2cValues[[f'I2C_RW_eRX_ZS_M1_Constants_eRX{i}' for i in range(12)]].apply(int,base=16).values

    i2c['ZS_lambda'],i2c['ZS_kappa'],i2c['ZS_c'],i2c['ZS_pass'],i2c['ZS_mask']=ZS_Constants_unpack(ZS_Constants)
    i2c['ZS_m1_c'],i2c['ZS_m1_beta'],i2c['ZS_m1_pass'],i2c['ZS_m1_mask']=ZS_M1_Constants_unpack(ZS_M1_Constants)

    i2c['CM_eRX_Route']=np.array([int(i2cValues['I2C_RW_CM_eRX_Route'][i:i+1],16) for i in range(12)])
    i2c['CM_Selections']=np.array([int(i2cValues[f'I2C_RW_CM_Selection_eRX{i}'],16) for i in range(12)])
    i2c['CM_UserDef']=np.array([int(i2cValues[f'I2C_RW_CM_UserDef_eRX{i}'],16) for i in range(12)])

    eRx_active=int(i2cValues.I2C_RW_active_eRXs,16)
    i2c['ERx_active']=np.array([(eRx_active>>i)&1 for i in range(12)],dtype=bool)

    eTx_active=int(i2cValues.I2C_RW_Active_eTXs,16)
    i2c['ETx_active']=np.array([(eTx_active>>i)&1 for i in range(6)],dtype=bool)

    i2c['SimpleMode']=i2cValues.I2C_RW_SimpleMode=='1'
    i2c['PassThruMode']=i2cValues.I2C_RW_Pass_Thru_Mode=='1'

    i2c['HeaderMarker']=i2cValues.I2C_RW_Header_Marker
    i2c['IdlePattern']=i2cValues.I2C_RW_Idle_Pattern

    i2c['VReconstruct_thresh'] = int(i2cValues.I2C_RW_vReconstruct_thresh,16)
    i2c['Match_thresh'] = int(i2cValues.I2C_RW_MatchThreshold,16)
    i2c['EBO_ReconMode'] = int(i2cValues.I2C_RW_ReconMode_Result,16)

    i2c['ROC_FirstSyncHeader']=i2cValues.I2C_RW_FirstSyncHeader
    i2c['ROC_SyncHeader']=i2cValues.I2C_RW_SyncHeader
    i2c['ROC_SyncBody']=i2cValues.I2C_RW_SyncBody
    i2c['ROC_HdrMarker']=i2cValues.I2C_RW_hgcroc_hdr_marker

    return Dict2Class(i2c)
