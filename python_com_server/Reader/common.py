#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: common defines for reader
Created: Tuyj
Created date:2015/12/14
'''

CRCCode = 0x1021
def calcCrc(data, crc_mul=CRCCode):
    '''e.g. data='1289ab', crc_mul=0x1021'''
    size = len(data)
    if size % 2:
        data = '0' + data
        size += 1
    size = size / 2
    index = 0
    crc = 0
    while size > 0:
        size -= 1
        i = 0x80
        while i != 0:
            if (crc & 0x8000) != 0:
                crc = (crc << 1) & 0xffffffff
                crc ^= crc_mul
            else:
                crc = (crc << 1) & 0xffffffff
            value = int(data[index:index+2], 16)
            if (value & i) != 0:
                crc ^= crc_mul
            i = i >> 1
        index += 2
    out = "%04x" % crc
    return out[-2:],out[-4:-2]

def str2hex_str(in_str):
    '''e.g. in_str='0xb'or'0x0b'or'b'or'0b' -> '\x0b' '''
    if in_str.startswith('0x'):
        in_str = in_str[2:]
    if len(in_str) % 2:
        in_str = '0' + in_str
    return in_str.decode('hex')









