packetStateProgression = {'EMPTYHEADER':'HOME',
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
 
#definitions of GRAY6 and mapping of ROCSM states to GRAY6 codes taken from Project_constants.sv in RTL

#Modified from Project_constants.sv#L1158
GRAY6_0     =   int('000000',2)
GRAY6_1     =   int('000001',2)
GRAY6_2     =   int('000011',2)
GRAY6_3     =   int('000010',2)
GRAY6_4     =   int('000110',2)
GRAY6_5     =   int('000111',2)
GRAY6_6     =   int('000101',2)
GRAY6_7     =   int('000100',2)
GRAY6_8     =   int('001100',2)
GRAY6_9     =   int('001101',2)
GRAY6_10    =   int('001111',2)
GRAY6_11    =   int('001110',2)
GRAY6_12    =   int('001010',2)
GRAY6_13    =   int('001011',2)
GRAY6_14    =   int('001001',2)
GRAY6_15    =   int('001000',2)
GRAY6_16    =   int('011000',2)
GRAY6_17    =   int('011001',2)
GRAY6_18    =   int('011011',2)
GRAY6_19    =   int('011010',2)
GRAY6_20    =   int('011110',2)
GRAY6_21    =   int('011111',2)
GRAY6_22    =   int('011101',2)
GRAY6_23    =   int('011100',2)
GRAY6_24    =   int('010100',2)
GRAY6_25    =   int('010101',2)
GRAY6_26    =   int('010111',2)
GRAY6_27    =   int('010110',2)
GRAY6_28    =   int('010010',2)
GRAY6_29    =   int('010011',2)
GRAY6_30    =   int('010001',2)
GRAY6_31    =   int('010000',2)
GRAY6_32    =   int('110000',2)
GRAY6_33    =   int('110001',2)
GRAY6_34    =   int('110011',2)
GRAY6_35    =   int('110010',2)
GRAY6_36    =   int('110110',2)
GRAY6_37    =   int('110111',2)
GRAY6_38    =   int('110101',2)
GRAY6_39    =   int('110100',2)
GRAY6_40    =   int('111100',2)
GRAY6_41    =   int('111101',2)
GRAY6_42    =   int('111111',2)
GRAY6_43    =   int('111110',2)
GRAY6_44    =   int('111010',2)
GRAY6_45    =   int('111011',2)
GRAY6_46    =   int('111001',2)
GRAY6_47    =   int('111000',2)
GRAY6_48    =   int('101000',2)
GRAY6_49    =   int('101001',2)
GRAY6_50    =   int('101011',2)
GRAY6_51    =   int('101010',2)
GRAY6_52    =   int('101110',2)
GRAY6_53    =   int('101111',2)
GRAY6_54    =   int('101101',2)
GRAY6_55    =   int('101100',2)
GRAY6_56    =   int('100100',2)
GRAY6_57    =   int('100101',2)
GRAY6_58    =   int('100111',2)
GRAY6_59    =   int('100110',2)
GRAY6_60    =   int('100010',2)
GRAY6_61    =   int('100011',2)
GRAY6_62    =   int('100001',2)
GRAY6_63    =   int('100000',2)

#Taken from Project_constants.sv#L1546
ROCSM_S0_HOME           =   GRAY6_0
ROCSM_S1_HEADER         =   GRAY6_1
ROCSM_S2_CM             =   GRAY6_2
ROCSM_S3_CH0            =   GRAY6_3
ROCSM_S4_CH1            =   GRAY6_4
ROCSM_S5_CH2            =   GRAY6_5
ROCSM_S6_CH3            =   GRAY6_6
ROCSM_S7_CH4            =   GRAY6_7
ROCSM_S8_CH5            =   GRAY6_8
ROCSM_S9_CH6            =   GRAY6_9
ROCSM_S10_CH7           =   GRAY6_10
ROCSM_S11_CH8           =   GRAY6_11
ROCSM_S12_CH9           =   GRAY6_12
ROCSM_S13_CH10          =   GRAY6_13
ROCSM_S14_CH11          =   GRAY6_14
ROCSM_S15_CH12          =   GRAY6_15
ROCSM_S16_CH13          =   GRAY6_16
ROCSM_S17_CH14          =   GRAY6_17
ROCSM_S18_CH15          =   GRAY6_18
ROCSM_S19_CH16          =   GRAY6_19
ROCSM_S20_CH17          =   GRAY6_20
ROCSM_S21_CALIB         =   GRAY6_21
ROCSM_S22_CH18          =   GRAY6_22
ROCSM_S23_CH19          =   GRAY6_23
ROCSM_S24_CH20          =   GRAY6_24
ROCSM_S25_CH21          =   GRAY6_25
ROCSM_S26_CH22          =   GRAY6_26
ROCSM_S27_CH23          =   GRAY6_27
ROCSM_S28_CH24          =   GRAY6_28
ROCSM_S29_CH25          =   GRAY6_29
ROCSM_S30_CH26          =   GRAY6_30
ROCSM_S31_CH27          =   GRAY6_31
ROCSM_S32_CH28          =   GRAY6_32
ROCSM_S33_CH29          =   GRAY6_33
ROCSM_S34_CH30          =   GRAY6_34
ROCSM_S35_CH31          =   GRAY6_35
ROCSM_S36_CH32          =   GRAY6_36
ROCSM_S37_CH33          =   GRAY6_37
ROCSM_S38_CH34          =   GRAY6_38
ROCSM_S39_CH35          =   GRAY6_39
ROCSM_S40_CRC           =   GRAY6_40
ROCSM_S41_ALIGN_RST     =   GRAY6_41
ROCSM_S42_ALIGN_STEP1   =   GRAY6_42
ROCSM_S43_ALIGN_STEP2   =   GRAY6_43
ROCSM_S44_UHEADER       =   GRAY6_44
ROCSM_S45_EMPTY_HDR     =   GRAY6_45
ROCSM_S46_CHIPSYNC      =   GRAY6_46
ROCSM_S47_EBR           =   GRAY6_47
ROCSM_S48_UNUSED        =   GRAY6_48
ROCSM_S49_UNUSED        =   GRAY6_49
ROCSM_S50_UNUSED        =   GRAY6_50
ROCSM_S51_UNUSED        =   GRAY6_51
ROCSM_S52_UNUSED        =   GRAY6_52
ROCSM_S53_UNUSED        =   GRAY6_53
ROCSM_S54_UNUSED        =   GRAY6_54
ROCSM_S55_UNUSED        =   GRAY6_55
ROCSM_S56_UNUSED        =   GRAY6_56
ROCSM_S57_UNUSED        =   GRAY6_57
ROCSM_S58_UNUSED        =   GRAY6_58
ROCSM_S59_UNUSED        =   GRAY6_59
ROCSM_S60_UNUSED        =   GRAY6_60
ROCSM_S61_UNUSED        =   GRAY6_61
ROCSM_S62_UNUSED        =   GRAY6_62
ROCSM_S63_UNUSED        =   GRAY6_63

StateToValMapping = {'HOME'             : ROCSM_S0_HOME,
                     'STANDARDHEADER'   : ROCSM_S1_HEADER,
                     'CM'               : ROCSM_S2_CM,
                     'CH0'              : ROCSM_S3_CH0,
                     'CH1'              : ROCSM_S4_CH1,
                     'CH2'              : ROCSM_S5_CH2,
                     'CH3'              : ROCSM_S6_CH3,
                     'CH4'              : ROCSM_S7_CH4,
                     'CH5'              : ROCSM_S8_CH5,
                     'CH6'              : ROCSM_S9_CH6,
                     'CH7'              : ROCSM_S10_CH7,
                     'CH8'              : ROCSM_S11_CH8,
                     'CH9'              : ROCSM_S12_CH9,
                     'CH10'             : ROCSM_S13_CH10,
                     'CH11'             : ROCSM_S14_CH11,
                     'CH12'             : ROCSM_S15_CH12,
                     'CH13'             : ROCSM_S16_CH13,
                     'CH14'             : ROCSM_S17_CH14,
                     'CH15'             : ROCSM_S18_CH15,
                     'CH16'             : ROCSM_S19_CH16,
                     'CH17'             : ROCSM_S20_CH17,
                     'CALIB'            : ROCSM_S21_CALIB,
                     'CH18'             : ROCSM_S22_CH18,
                     'CH19'             : ROCSM_S23_CH19,
                     'CH20'             : ROCSM_S24_CH20,
                     'CH21'             : ROCSM_S25_CH21,
                     'CH22'             : ROCSM_S26_CH22,
                     'CH23'             : ROCSM_S27_CH23,
                     'CH24'             : ROCSM_S28_CH24,
                     'CH25'             : ROCSM_S29_CH25,
                     'CH26'             : ROCSM_S30_CH26,
                     'CH27'             : ROCSM_S31_CH27,
                     'CH28'             : ROCSM_S32_CH28,
                     'CH29'             : ROCSM_S33_CH29,
                     'CH30'             : ROCSM_S34_CH30,
                     'CH31'             : ROCSM_S35_CH31,
                     'CH32'             : ROCSM_S36_CH32,
                     'CH33'             : ROCSM_S37_CH33,
                     'CH34'             : ROCSM_S38_CH34,
                     'CH35'             : ROCSM_S39_CH35,
                     'CRC'              : ROCSM_S40_CRC,
                     'UNEXPECTEDHEADER' : ROCSM_S44_UHEADER,
                     'EMPTYHEADER'      : ROCSM_S45_EMPTY_HDR,
                     'ALIGNRESET'       : ROCSM_S41_ALIGN_RST,
                     'ALIGNSTEP1'       : ROCSM_S42_ALIGN_STEP1,
                     'ALIGNSTEP2'       : ROCSM_S43_ALIGN_STEP2,
                     'CSYNC'            : ROCSM_S46_CHIPSYNC,
                     'EBR'              : ROCSM_S47_EBR,
                   }
