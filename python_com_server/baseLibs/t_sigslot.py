#!/usr/bin/python2.7
#coding=utf8
r'''
Created: Tuyj
Created date:2015/11/12
'''
if __name__ == '__main__': import _env

import baseLibs.t_com as t_com
import socket, os
import baseLibs.t_util as t_util

from baseLibs.log.t_log import *
logger = LOG_MODULE_DEFINE('sigslot')
SET_LOG_LEVEL(logger, 'debug')
_local_debug_mode = True

tytUnixSk = 0
class siglots:
    def __init__(self, path_prefix, type=tytUnixSk):
        if type == tytUnixSk:
            self.handler = _unixSocket(path_prefix)
        else: raise ValueError("just Support tytUnixSk")
    def __del__(self):
        self.close()
    def close(self):
        if self.handler:
            self.signal()
            self.handler.close()
        self.handler = None
    def FD(self):
        return self.handler.read_endpoint()
    def signal(self):
        self.handler.send("#BYE#")
    def msg(self, message):
        self.handler.send(message)

class _unixSocket:
    def __init__(self, path_prefix):
        self.recv_sk = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.send_sk = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sk_path = "%s.%s.sk" % (path_prefix, t_util.getTimestampByDate(t_util.tsMs))
        self.recv_sk.bind(self.sk_path)
        self.send_sk.connect(self.sk_path)
    def close(self):
        if self.recv_sk:
            self.recv_sk.close()
            self.send_sk.close()
        self.recv_sk = self.send_sk = None
        if os.path.exists(self.sk_path):
            os.remove(self.sk_path)
    def read_endpoint(self):
        return self.recv_sk
    def write_endpoint(self):
        return self.send_sk
    def send(self, message):
        if self.send_sk:
            self.send_sk.send(message)
        
if __name__ == '__main__':
    if not LOG_INIT():
        raise -1
    import select,thread
    
    def loop(sl):
        sk = sl.FD()
        inputs=[sk]
        while True:
            print 'trying...'
            try:
                rs,ws,es=select.select(inputs, [], [], 1)
            except socket.error as ex:
                print ex.errno
                break
            for r in rs:
                if r is sk:
                    print 'recv:',sk.recv(512)
                    return
                else:
                    print '---'
                
    
    sl = siglots("main")
    thread.start_new(loop, (sl,))
    
    raw_input('put in message to exit\n')
    sl.close()
    raw_input('put in message to exit\n')
    print 'exit'
    
    
    
    
    

