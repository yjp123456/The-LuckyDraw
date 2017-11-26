#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: message defines for reader
Created: Tuyj
Created date:2015/12/14
'''

if __name__ == '__main__': import _env

import common

cmdReaderInfo,cmdReadTags = '00','01'

'''
reqMsg = [StartCode,Size,ChannelNumber,Payload,CRCLow,CRCHigh]
rspMsg = [StartCode,Size,ChannelNumber,Status,Payload,CRCLow,CRCHigh]
'''
StartCode = 'dd11ef'
StartCodeHex = '\xdd\x11\xef'
HeaderLen = 7
rCompleted,rIncomplete,rNone,rNoise  = '59','01',"94","58"
rErrors = {
    '58': ("ReadError58", "Noise"),
    '88': ("ReadError88", "Crc"),
    '95': ("ReadError95", "Others"),
}
hOk = '00'
hStates = {
    '01': ("HardError01", "RF"),
    '02': ("HardError02", "Overheat"),
    '03': ("HardError03", "Other"),
}
class reqMsg:
    def __init__(self, data, chn=0x00):
        '''e.g. data='0x0b' chn=0x00~0x03'''
        if data.startswith('0x'):
            data = data[2:]
        if len(data) % 2:
            self.data = '0' + data
        else:
            self.data = data
        self.chn  = chn
        self.msg_size = 7 + (len(self.data) / 2) #size of full msg=3+1+1+2+len(data)
        crc = common.calcCrc(self.data)
        self.msg_data = "%s%02x%02x%s%s%s" % (StartCode, self.msg_size, self.chn, self.data, crc[0], crc[1])
        
    def getMsg(self):
        return self.msg_data

class req_ReaderInfo(reqMsg):
    def __init__(self):
        reqMsg.__init__(self, '0x0000')

class req_ReadTags(reqMsg):
    def __init__(self):
        reqMsg.__init__(self, '0x0100')

class InvalidMsg(Exception): pass
class rspHeader:
    def __init__(self, hex_data):
        if hex_data[:3] != StartCodeHex:
            raise InvalidMsg("Start Code invalid")
        self.msg_size = int(hex_data[3].encode('hex'), 16)
        self.payload_size = self.msg_size - HeaderLen - 2
        self.chn = int(hex_data[4].encode('hex'), 16)
        self.cmd = hex_data[5].encode('hex')
        self.status = hex_data[6].encode('hex')
    def payloadSize(self):
        return self.payload_size
    def Cmd(self):
        return self.cmd
    def Status(self):
        return self.status

def parseReaderInfo(payload):
    return {
        'DIP': "%s-%s" % (payload[4:8], payload[8:10]), #date in produced
        'channels': int(payload[10:12], 16),
        'power': float(int(payload[12:14], 16)) / 10,
        'hard_version': '%s.%s' % (payload[14], payload[15]),
        'flash_version': '%s.%s' % (payload[16], payload[17]),
        'SN': payload[18:22],
        'PIP': payload[22:24] #place in produced
    }









