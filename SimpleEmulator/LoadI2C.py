import numpy as np
from .UnpackZSConstants import ZS_Constants_unpack, ZS_M1_Constants_unpack

# Turns a dictionary into a class
class Dict2Class(object):
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])

def parseI2C(i2cValues=None):
    """
    Function to convert i2c data from csv file output by UVM, and create i2c class with variables for all registers relavent for emulator
    """

    if i2cValues is None:
        return defaultI2Csettings()

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

def defaultI2Csettings():
    i2c={}

    i2c['ZS_ce']=0x0

    i2c['ZS_lambda']=np.array([0x20]*12*37).reshape(12,37)
    i2c['ZS_kappa']=np.array([0]*12*37).reshape(12,37)
    i2c['ZS_c']=np.array([255]*12*37).reshape(12,37)
    i2c['ZS_pass']=np.array([0]*12*37).reshape(12,37)
    i2c['ZS_mask']=np.array([0]*12*37).reshape(12,37)
    i2c['ZS_m1_c']=np.array([0xf]*12*37).reshape(12,37)
    i2c['ZS_m1_beta']=np.array([0x20]*12*37).reshape(12,37)
    i2c['ZS_m1_pass']=np.array([0]*12*37).reshape(12,37)
    i2c['ZS_m1_mask']=np.array([0]*12*37).reshape(12,37)

    i2c['CM_eRX_Route']=np.array([0,1,2,3,4,5,6,7,8,9,10,11])
    i2c['CM_Selections']=np.array([6]*12)
    i2c['CM_UserDef']=np.array([0]*12)

    i2c['ERx_active']=np.array([1]*12,dtype=bool)
    i2c['ETx_active']=np.array([1]*6,dtype=bool)

    i2c['SimpleMode']=False
    i2c['PassThruMode']=False

    i2c['HeaderMarker']=0x1e6
    i2c['IdlePattern']=0x555555

    i2c['VReconstruct_thresh'] = 0
    i2c['Match_thresh'] = 0
    i2c['EBO_ReconMode'] = 0

    i2c['ROC_FirstSyncHeader']=0x9
    i2c['ROC_SyncHeader']=0xa
    i2c['ROC_SyncBody']=0xaaaaaaa
    i2c['ROC_HdrMarker']=0xf

    return Dict2Class(i2c)

def convertI2CtoYAML(i2c, yamlName="i2cConfig.yaml"):
    """
    Function to convert i2c class returned from parseI2C to a yaml file that can be used in chip testing
    """

    if isinstance(i2c,Dict2Class):
        i2c=vars(i2c)

    lines = ""

    if 'ZS_ce' in i2c:
        lines +=  "ZSCommon:\n"
        lines +=  "  Global:\n"
        lines +=  "    zs_ce:\n"
        lines += f"      {i2c['ZS_ce']}\n"


    if any([x in i2c.keys() for x in ['ZS_lambda', 'ZS_kappa', 'ZS_c', 'ZS_pass', 'ZS_mask']]):
        lines += "ZS:\n"
        for i in range(12):
            lines += f"  {i}:\n"
            if 'ZS_c' in i2c:
                lines += f"    zs_c_i:\n"
                lines += f"      [{','.join([f'{x}' for x in i2c['ZS_c'][i]])}]\n"
            if 'ZS_lambda' in i2c:
                lines += f"    zs_lambda:\n"
                lines += f"      [{','.join([f'{x}' for x in i2c['ZS_lambda'][i]])}]\n"
            if 'ZS_lambda' in i2c:
                lines += f"    zs_kapa:\n"
                lines += f"      [{','.join([f'{x}' for x in i2c['ZS_kappa'][i]])}]\n"
            if 'ZS_pass' in i2c:
                lines += f"    zs_pass_i:\n"
                lines += f"      [{','.join([f'{x:b}' for x in i2c['ZS_pass'][i]])}]\n"
            if 'ZS_mask' in i2c:
                lines += f"    zs_mask_i:\n"
                lines += f"      [{','.join([f'{x:b}' for x in i2c['ZS_mask'][i]])}]\n"

    if any([x in i2c.keys() for x in ['ZS_m1_c', 'ZS_m1_beta', 'ZS_m1_pass', 'ZS_m1_mask']]):
        lines += "ZSmOne:\n"
        for i in range(12):
            lines += f"  {i}:\n"
            if 'ZS_m1_c' in i2c:
                lines += f"    zs_c_i_m:\n"
                lines += f"      [{','.join([f'{x}' for x in i2c['ZS_m1_c'][i]])}]\n"
            if 'ZS_m1_beta' in i2c:
                lines += f"    zs_beta_m:\n"
                lines += f"      [{','.join([f'{x}' for x in i2c['ZS_m1_beta'][i]])}]\n"
            if 'ZS_m1_pass' in i2c:
                lines += f"    zs_pass_i_m:\n"
                lines += f"      [{','.join([f'{x:b}' for x in i2c['ZS_m1_pass'][i]])}]\n"
            if 'ZS_m1_mask' in i2c:
                lines += f"    zs_mask_i_m:\n"
                lines += f"      [{','.join([f'{x:b}' for x in i2c['ZS_m1_mask'][i]])}]\n"


    if any([x in i2c.keys() for x in ['CM_eRX_Route', 'CM_Selections', 'CM_UserDef', 'VReconstruct_thresh', 'EBO_ReconMode']]):
        lines += "ELinkProcessors:\n"
        lines += "  Global:\n"
        if 'CM_eRX_Route' in i2c:
            lines += "    cm_erx_route:\n"
            lines +=f"      0x{''.join([f'{x:X}' for x in i2c['CM_eRX_Route']])}\n"
        if 'CM_Selections' in i2c:
            lines += "    cm_selection_x:\n"
            lines += f"      [{','.join([f'{x}' for x in i2c['CM_Selections']])}]\n"
        if 'CM_UserDef' in i2c:
            lines += "    cm_user_def_x:\n"
            lines += f"      [{','.join([f'{x}' for x in i2c['CM_UserDef']])}]\n"
        if 'VReconstruct_thresh' in i2c:
            lines += "    v_reconstruct_thresh:\n"
            lines += f"      {i2c['VReconstruct_thresh']}\n"
        if 'EBO_ReconMode' in i2c:
            lines += "    recon_mode_result:\n"
            lines += f"      {i2c['EBO_ReconMode']}\n"



    if any([x in i2c.keys() for x in ['ERx_active', 'SimpleMode', 'PassThruMode', 'Match_thresh', 'ROC_FirstSyncHeader', 'ROC_SyncHeader', 'ROC_SyncBody', 'ROC_HdrMarker']]):
        lines += "RocDaqCtrl:\n"
        lines += "  Global:\n"
        if 'ERx_active' in i2c:
            lines += "    active_erxs:\n"
            lines +=f"      0x{int(''.join([f'{x:b}' for x in i2c['ERx_active']]),2):03X}\n"
        if 'SimpleMode' in i2c:
            lines += "    simple_mode:\n"
            lines +=f"      {i2c['SimpleMode']:b}\n"
        if 'PassThruMode' in i2c:
            lines += "    pass_thru_mode:\n"
            lines +=f"      {i2c['PassThruMode']:b}\n"
        if 'Match_thresh' in i2c:
            lines += "    match_threshold:\n"
            lines +=f"      0x{i2c['Match_thresh']}\n"
        if 'ROC_FirstSyncHeader' in i2c:
            lines += "    first_sync_header:\n"
            lines +=f"      0x{i2c['ROC_FirstSyncHeader']}\n"
        if 'ROC_SyncHeader' in i2c:
            lines += "    sync_header:\n"
            lines +=f"      0x{i2c['ROC_SyncHeader']}\n"
        if 'ROC_SyncBody' in i2c:
            lines += "    sync_body:\n"
            lines +=f"      0x{i2c['ROC_SyncBody']}\n"
        if 'ROC_HdrMarker' in i2c:
            lines += "    hgcroc_hdr_marker:\n"
            lines +=f"      0x{i2c['ROC_HdrMarker']}\n"


    if any([x in i2c.keys() for x in ['ETx_active', 'IdlePattern', 'HeaderMarker']]):
        lines += "FormatterBuffer:\n"
        lines += "  Global:\n"
        if 'ETx_active' in i2c:
            lines += "    active_etxs:\n"
            lines +=f"      0x{int(''.join([f'{x:b}' for x in i2c['ETx_active']]),2):02X}\n"
        if 'IdlePattern' in i2c:
            lines += "    idle_pattern:\n"
            lines +=f"      0x{i2c['IdlePattern']}\n"
        if 'HeaderMarker' in i2c:
            lines += "    header_marker:\n"
            lines +=f"      0x{i2c['HeaderMarker']}\n"

#     if any([x in i2cDict.keys() for x in ['ERx_active', 'SimpleMode', 'PassThruMode', 'Match_thresh', 'ROC_FirstSyncHeader', 'ROC_SyncHeader', 'ROC_SyncBody', 'ROC_HdrMarker']]):
#         lines += "RocDaqCtrl:\n"
#         lines += "  Global:\n"
#         if 'ERx_active' in i2c:
#             lines += "    active_erxs:\n"
#             lines +=f"      0x{int(''.join([f'{x:b}' for x in i2c.ERx_active]),2):03X}\n"
#         if 'SimpleMode' in i2c:
#             lines += "    simple_mode:\n"
#             lines +=f"      {i2c.SimpleMode:b}\n"
#         if 'PassThruMode' in i2c:
#             lines += "    pass_thru_mode:\n"
#             lines +=f"      {i2c.PassThruMode:b}\n"
#         if 'Match_thresh' in i2c:
#             lines += "    match_threshold:\n"
#             lines +=f"      0x{i2c.Match_thresh}\n"
#         if 'ROC_FirstSyncHeader' in i2c:
#             lines += "    first_sync_header:\n"
#             lines +=f"      0x{i2c.ROC_FirstSyncHeader}\n"
#         if 'ROC_SyncHeader' in i2c:
#             lines += "    sync_header:\n"
#             lines +=f"      0x{i2c.ROC_SyncHeader}\n"
#         if 'ROC_SyncBody' in i2c:
#             lines += "    sync_body:\n"
#             lines +=f"      0x{i2c.ROC_SyncBody}\n"
#         if 'ROC_HdrMarker' in i2c:
#             lines += "    hgcroc_hdr_marker:\n"
#             lines +=f"      0x{i2c.ROC_HdrMarker}\n"


#     lines += "FormatterBuffer:\n"
#     lines += "  Global:\n"
#     lines += "    active_etxs:\n"
#     lines +=f"      0x{int(''.join([f'{x:b}' for x in i2c.ETx_active]),2):02X}\n"
#     lines += "    idle_pattern:\n"
#     lines +=f"      0x{i2c.IdlePattern}\n"
#     lines += "    header_marker:\n"
#     lines +=f"      0x{i2c.HeaderMarker}\n"

    with open(yamlName,'w') as _file:
        _file.write(lines)
