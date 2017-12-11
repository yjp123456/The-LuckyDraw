#!/usr/bin/python2.7
# -*- coding:utf-8 -*-
r'''
Fuction: Wrapper of rFid Reader/Writer using pySerial 
Created: Tuyj
Created date:2015/12/14
'''

if __name__ == '__main__': import _env
import serial, time, threading
import msg_defines as MSG
import common
import websocket

from baseLibs.log.t_log import *
logger = LOG_MODULE_DEFINE('rfidReader')
SET_LOG_LEVEL(logger, 'info')

class StatusError(Exception): pass
class TimeoutError(Exception): pass
class ReadError(Exception): pass
class rfidReader:
    def __init__(self, port = None, 
                 baudrate = 115200, 
                 bytesize = 8,
                 parity   = 'N',
                 stopbits = 1,
                 timeout = None):
        self.port_cfg = None
        self.COM = None
        self.req_read_msg = MSG.req_ReadTags().getMsg().decode('hex')
        self.req_info_msg = MSG.req_ReaderInfo().getMsg().decode('hex')
        self.com_lock = threading.RLock()
        self.loop_thread = None
        self.reading = False
        self.isEnd = False
        self.cond = threading.Condition()
        self.cb_funcs = []
        self.err_funcs = []
        self.loop_inv = 0.1
        self.about = None
        if port is not None:
            self.port_cfg = (port, baudrate, bytesize, parity, stopbits, timeout)
            try:self.openPort()
            except Exception as ex:
                L_ERROR(logger, "init rfidReader failure:%s", ex.message)
    
    def Close(self):
        self.isEnd = True
        self.cond.acquire()
        if self.loop_thread is not None:
            self.stopReading()
            self.cond.notifyAll()
            self.cond.release()
            try:
                self.loop_thread.join(5)
                self.loop_thread = None
            except RuntimeError:
                L_ERROR(logger, "wait loop thread exit timeout")
        else:
            self.cond.release()
        self.closePort()
    
    def setPort(self, port, 
                 baudrate = 115200, 
                 bytesize = 8,
                 parity   = 'N',
                 stopbits = 1,
                 timeout = None):
        '''
        If set failure,raise serial.serialutil.SerialException
        '''
        port_cfg = (port, baudrate, bytesize, parity, stopbits, timeout)
        if self.port_cfg == port_cfg:
            return
        self.closePort()
        self.port_cfg = port_cfg
        self.openPort()
    
    def checkPort(self):
        self.com_lock.acquire()
        if self.COM is None or not self.COM.isOpen():
            self.com_lock.release()
            return False
        self.com_lock.release()
        return True
    
    def closePort(self):
        self.com_lock.acquire()
        if self.COM is not None:
            self.COM.close()
            self.COM = None
        self.com_lock.release()
    
    def openPort(self):
        '''
        If open failure,raise serial.serialutil.SerialException
        '''
        if self.checkPort():
            return
        self.com_lock.acquire()
        try:
            self.COM = serial.Serial(*self.port_cfg)
        except serial.serialutil.SerialException:
            L_ERROR(logger, "openPort[%s] failure", self.port_cfg)
            self.com_lock.release()
            raise
        self.com_lock.release()

    def readTags(self):
        self.com_lock.acquire()        
        try:
            if not self.checkPort():
                raise StatusError("serial port is not ready")
        
            self._send(self.req_read_msg)
            
            tags = {}
#             tags = []
            payloads = self._readPayloads(MSG.cmdReadTags, self.port_cfg[-1])
            cnt = len(payloads)
            for index in xrange(0, cnt-1):
                payload  = payloads[index].encode('hex')
                tag_type = payload[0:2]
                tag_DSFID= payload[2:4]
                tag_UID  = payload[4:20]
                tags[tag_UID] = (tag_type, tag_DSFID)
#                 tags.append((tag_UID, tag_type, tag_DSFID))
            
            end_payload = payloads[-1]
            number = int(end_payload[0:2].encode('hex'), 16)
            hard_state = end_payload[2].encode('hex')
            if hard_state != MSG.hOk:
                if MSG.hStates.has_key(hard_state):
                    raise ReadError(MSG.hStates[hard_state])
                raise ReadError("unknow hard_state[%s]" % hard_state)
            if len(tags) != number:
                L_WARNING(logger, "really number[%d] of tags received is not match the end-code[%d]" , len(tags), number)
        except:
            self._discardBuffer()
            self.com_lock.release()
            raise
        self.com_lock.release()
#         tags.sort()
        return tags

    def aboutReader(self):
        if self.about is not None:
            return self.about
        
        self.com_lock.acquire()
        try:
            if not self.checkPort():
                raise StatusError("serial port is not ready")
        
            self._send(self.req_info_msg)
            
            payloads = self._readPayloads(MSG.cmdReaderInfo, self.port_cfg[-1])
            self.about = MSG.parseReaderInfo(payloads[-1].encode('hex'))
        except:
            self._discardBuffer()
            self.com_lock.release()
            raise
        self.com_lock.release()
        return self.about
    
    def startReading(self, cb_func=None, err_func=None, inva=None):
        self.cond.acquire()
        if self.reading:
            self.cond.release()
            return
        if cb_func is not None and self.cb_funcs.count(cb_func) == 0:
            self.cb_funcs.append(cb_func)
        if err_func is not None and self.err_funcs.count(err_func) == 0:
            self.err_funcs.append(err_func)
        if inva is not None:
            self.loop_inv = inva
        self.reading = True
        if self.loop_thread is None:
            self.loop_thread = threading.Thread(target=self.read_loop, name="rfidReaderLoop")
            self.loop_thread.daemon = True #主进程退出，马上结束线程
            self.loop_thread.start()
        self.cond.notifyAll()
        self.cond.release()
    
    def stopReading(self, cb_func=None, err_func=None):
        self.cond.acquire()
        if cb_func is not None and self.cb_funcs.count(cb_func) > 0:
            self.cb_funcs.remove(cb_func)
        if err_func is not None and self.err_funcs.count(err_func) > 0:
            self.err_funcs.remove(err_func)
        self.reading = False
        self.cond.release()

    def _discardBuffer(self):
        if self.COM:
            self.COM.flushOutput()
            self.COM.flushInput()
    
    def _read(self, need_size, timeout=None):
        wait_time = 0
        max_inv = 1
        wait_inv = 0.02
        while self.COM.inWaiting() < need_size:
            time.sleep(wait_inv)
            wait_time += wait_inv
            wait_inv = max_inv if wait_inv >= max_inv else wait_inv * 2
            if timeout is not None and wait_time >= timeout:
                raise TimeoutError
        return self.COM.read(need_size)
    
    def _send(self, hex_data):
        self.COM.write(hex_data)
        L_DEBUG(logger, "send:%s", hex_data.encode('hex'))

    def _readPayloads(self, cmd, timeout):
        '''e.g. cmd='01', timeout=2 '''
        end = False
        payloads = []
        while True:
            head_data = self._read(MSG.HeaderLen, timeout)
            header = MSG.rspHeader(head_data)
            if header.Cmd() != cmd:
                raise ReadError("recv Cmd[%s] is not match the sent Cmd[%s]" % (header.Cmd(), cmd))
            L_DEBUG(logger, "[%s]recv Head:%s", cmd, head_data.encode('hex'))
            
            status = header.Status()
            if status == MSG.rCompleted or status == MSG.rNone:
                end = True
            elif status == MSG.rNoise:
                end = True
                L_WARNING(logger, "Read Noise!!!")
            elif status != MSG.rIncomplete:
                if MSG.rErrors.has_key(status):
                    raise ReadError(MSG.rErrors[status])
                raise ReadError("unknow status[%s]" % status)
            
            left_data_size = header.payloadSize() + 2
            left_data = self._read(left_data_size, timeout)
            payload = left_data[:-2]
            L_DEBUG(logger, "[%s]recv Payload:%s", cmd, payload.encode('hex'))
            
#             recv_crc = (left_data[-2].encode('hex'), left_data[-1].encode('hex'))
#             if not self._checkCrc(payload.encode('hex'), recv_crc):
#                 raise ReadError(MSG.rErrors['\80'])

            payloads.append(payload)
            if end:
                break
        return payloads

    def _checkCrc(self, data, crc):
        c_crc = common.calcCrc(data)
        return crc == c_crc

    def read_loop(self):
        while True:
            self.cond.acquire()
            if self.isEnd: 
                self.cond.release()
                return
            while not self.reading:
                self.cond.wait(5)
                if self.isEnd:
                    self.cond.release()
                    return
            self.cond.release()
            
            try:
                tags = self.readTags()
                
                self.cond.acquire()
                inv = self.loop_inv
                for cb_fun in self.cb_funcs:
                    try:
                        cb_fun(tags)
                    except:
                        L_ERROR(logger, "callback failure")
                        DealException()
                self.cond.release()

                time.sleep(inv)
            except Exception as ex:
                self.cond.acquire()
                inv = self.loop_inv
                if len(self.err_funcs) > 0:
                    for err_fun in self.err_funcs:
                        try:
                            err_fun(ex)
                        except:
                            L_ERROR(logger, "error callback failure")
                            DealException()
                else:
                    L_ERROR(logger, "readTags failure:%s", ex.message)
                self.cond.release()
                time.sleep(inv)
    
if __name__ == '__main__':
    if not LOG_INIT():
        raise -1
    
    def onRead(tags):
        datas = []
        for UID,info in tags.iteritems():
                if UID not in read_buff:
                    read_buff.append(UID)
                    datas.append(UID)
                    L_ERROR(logger, "(%d)%s", len(UID), UID)
        if len(datas) > 0:
            result = websocket.notify(datas)
            if result is False:
                for item in datas:
                    read_buff.remove(item)


    reader = rfidReader('com5', timeout=3)
    read_buff = []
    server = websocket.websocket_server()
    server.daemon = True
    server.start()
    reader.startReading(onRead)
    while True:
        try:
            text = raw_input('Enter q/quit to quit --> ')
        except KeyboardInterrupt: 
            break
        if text == 'q' or text == 'quit':
            break
        elif text == 'read' or text == 'r':
            try:
                L_INFO(logger, "start reading...")
                tags = reader.readTags()
                L_INFO(logger, "number:%d", len(tags))
                L_INFO(logger, "%s", tags)
            except:
                DealException()
        elif text == 'start' or text == 's':
            reader.startReading(onRead)
        elif text == 'stop' or text == 'n':
            reader.stopReading()
        elif text == 'info' or text == 'i':
            L_INFO(logger, "%s", reader.aboutReader())
        else:
            print 'unknow key'
    
    reader.Close()
    reader = None

    print 'exit'







    
