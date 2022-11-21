import numpy as np

def ZS_Constants_unpack(registers):
    ZS_lambda = np.zeros(37*12,dtype=int).reshape(12,37)
    ZS_kappa  = np.zeros(37*12,dtype=int).reshape(12,37)
    ZS_c      = np.zeros(37*12,dtype=int).reshape(12,37)
    ZS_pass   = np.zeros(37*12,dtype=int).reshape(12,37)
    ZS_mask   = np.zeros(37*12,dtype=int).reshape(12,37)
    for i in range(12):
        register = registers[i]
        for j in range(37):
            r = (register>>(24*j))&0xffffff #grab bottom 3 bytes
            ZS_lambda[i][j] = ((r>>0)&0x7f)
            ZS_kappa[i][j]  = ((r>>7)&0x3f)
            ZS_c[i][j]      = ((r>>13)&0xff)
            ZS_pass[i][j]   = ((r>>21)&0x1)
            ZS_mask[i][j]   = ((r>>22)&0x1)
    return ZS_lambda,ZS_kappa,ZS_c,ZS_pass.astype(bool),ZS_mask.astype(bool)

def ZS_M1_Constants_unpack(registers):
    ZS_m1_c    = np.zeros(37*12,dtype=int).reshape(12,37)
    ZS_m1_beta = np.zeros(37*12,dtype=int).reshape(12,37)
    ZS_m1_pass = np.zeros(37*12,dtype=int).reshape(12,37)
    ZS_m1_mask = np.zeros(37*12,dtype=int).reshape(12,37)
    for i in range(12):
        register = registers[i]
        for j in range(37):
            r = (register>>(16*j))&0xffff #grab bottom 2 bytes
            ZS_m1_c[i][j]    = ((r>>0)&0xf)
            ZS_m1_beta[i][j] = ((r>>4)&0x7f)
            ZS_m1_pass[i][j] = ((r>>11)&0x1)
            ZS_m1_mask[i][j] = ((r>>12)&0x1)
    return ZS_m1_c,ZS_m1_beta,ZS_m1_pass.astype(bool),ZS_m1_mask.astype(bool)


DIV_Factors=np.array([0, 65536, 32768, 21845, 16384, 13107, 10923, 9362, 8192, 7282, 6554, 5958, 5461, 5041, 4681, 4369, 4096, 3855, 3641, 3449, 3277, 3121, 2979, 2849, 2731])
