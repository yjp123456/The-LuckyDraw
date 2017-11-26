#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: wrapper of multitask.py with threading
Created: Tuyj
Created date:2015/02/07
'''
if __name__ == '__main__': import _env

import baseLibs.t_com as t_com
import multitask
from multitask import Queue,recvfrom,Timeout,sleep,recv,read,send,sendto
import types
import threading,signal
import time 

from baseLibs.log.t_log import *
logger = LOG_MODULE_DEFINE('tMultitask')
SET_LOG_LEVEL(logger, 'debug')

class tMultitaskMgr(multitask.TaskManager):
    default_stop_timeout = 5.0
    def __init__(self, name):
        multitask.TaskManager.__init__(self)
        self.obj_name = name
        self.running = False
        self.hastask = False
        self.isEnd = True
        self.working = None
        self.cond = threading.Condition()
    
    def stop(self, timeout = int(default_stop_timeout)):
        self.cond.acquire()
        self.running = False
        self.cond.notify()
        self.cond.release()
        if self.working is not None:
            if self.isWorkingthread():
                self.working = None
                OBJ_INFO(self, logger, 'stop successfully(return stop)')
                return
            else:
                try:
                    self.working.join(timeout)
                    self.working = None
                except RuntimeError as ex:
                    OBJ_ERROR(self, logger, "join failure:%s",ex.message)
        else:
            cnt = timeout/0.1
            while cnt > 0 and not self.isEnd:
                time.sleep(0.1)
                cnt -= 1
        if not self.isEnd:
            OBJ_ERROR(self, logger, 'stop timeout')
        else:
            OBJ_DEBUG(self, logger, 'stop successfully')
    
    def run(self, thread_stack_size=None, ext_func=None, ext_args=(), ext_kwargs={}):
        if (not self.running) and self.working is None:
            if thread_stack_size is not None and thread_stack_size != 0:
                threading.stack_size(thread_stack_size)
            self.working = threading.Thread(target=self.run_forever, args=(ext_func,ext_args,ext_kwargs), name=self.obj_name)
            self.working.start()
            if thread_stack_size is not None and thread_stack_size != 0:
                threading.stack_size(t_com.default_large_thread_stack_size)
            OBJ_DEBUG(self, logger, "multitask working-thread started")
    
    def run_forever(self, ext_func=None, ext_args=(), ext_kwargs={}):
        if self.running:
            return
        if ext_func is not None:
            ext_func(*ext_args, **ext_kwargs)
        self.isEnd = False
        self.running = True
        self.add(self._taskCheck())
        while self.running:
            self.cond.acquire()
            while self.running and not self.hastask:
                self.cond.wait()
            self.cond.release()
            if not self.running:
                return
            while self.running and (self.has_runnable() or self.has_io_waits() or self.has_timeouts()):
                self.run_next()
            else:
                self.hastask = False
        self.isEnd = True
        OBJ_DEBUG(self, logger, 'multitask working-thread end')
    
    def add(self, task):
        multitask.TaskManager.add(self, task)
        self.cond.acquire()
        if not self.hastask:
            self.hastask = True
            self.cond.notify()
        self.cond.release()
    
    def isWorkingthread(self):
        return self.working is threading.current_thread()
    
    def _taskCheck(self):
        inv = t_com.max_multitask_inv
        while True:
            yield multitask.sleep(inv)

class TEST_STOPER:
    def __init__(self, tasker):
        self.tasker = tasker
        signal.signal(signal.SIGINT, self.stop_thread)
        signal.signal(signal.SIGTERM, self.stop_thread)
    def __del__(self):
        self.stop_thread()
    def stop_thread(self, *args, **kwargs):
        if self.tasker is not None:
            self.tasker.stop()
            self.tasker = None

def testQueue():
    def printT():
        while True:
            print '+++'
            yield multitask.sleep(3)
    def printT2():
        while True:
            print '---'
            yield multitask.sleep(0.2)
    def get1(que):
        while True:
            print 'xxxx'
            print (yield que.get())
    def put1(que):
        for x in xrange(0,10):
            yield que.put(x)
            time.sleep(0.5)
    
    t = tMultitaskMgr('testQueue')
    TEST_STOPER(t)
    t.run()    
    t.add(printT())
    t.add(printT2())
    
    que = Queue()
    t.add(get1(que))
    t.add(put1(que))
    time.sleep(10)
    t.stop()
    print 'over'

def testM():
    def waitExit():
        import socket
        sock = socket.socket(type=socket.SOCK_DGRAM)
        while True:
            try:
                yield multitask.recv(sock, 2)
            except multitask.Timeout: pass
    def printT():
        while True:
            print '+++'
            yield multitask.sleep(3)
            
    def printT2():
        while True:
            print '---'
            yield multitask.sleep(0.2)
    
    t = tMultitaskMgr('testT')
    TEST_STOPER(t)
    t.run()
    print 'add'
    t.add(waitExit())
    t.add(printT())
    t.add(printT2())
    print 'sleep'
    time.sleep(5)
    print 'sleeped'
    t.stop()
    print 'over'
    
if __name__ == '__main__':
    if not LOG_INIT():
        raise -1
#    testM()
    testQueue()



