#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: wrapper of pipe work-threading
Created: Tuyj
Created date:2015/05/15
'''
if __name__ == '__main__': import _env

import baseLibs.t_com as t_com
from baseLibs.taskQue import taskQue,Queue,Full,Empty
import thread,threading,time

from baseLibs.log.t_log import *
logger = LOG_MODULE_DEFINE('tWorker')
SET_LOG_LEVEL(logger, 'debug')

thread_loop_max_wait_time = 2 #sec
class pipeWorker:
    def __init__(self, name, max_task=0, 
                 max_thread_stack_size=t_com.default_small_thread_stack_size, 
                 max_wait_time=thread_loop_max_wait_time):
        self.obj_name = name
        self.tasks = taskQue(max_task)
        self.cancels = []
        self.cur_task_id = 0
        self.max_thread_stack_size = max_thread_stack_size 
        self.max_wait_time = max_wait_time
        self.thread_id = None
        self.running = False
        
    def start(self):
        if self.running:
            OBJ_INFO(self, logger, "worker had started")
            return
        try:
            self.running = True
            thread.stack_size(self.max_thread_stack_size)
            self.thread_id = thread.start_new(self.__working, ())
            thread.stack_size(t_com.default_large_thread_stack_size)
        except:
            self.running = False
            raise
        
    def stop(self):
        if not self.running:
            OBJ_INFO(self, logger, "worker had stopped")
            return True
        self.running = False
        self.cur_task_id = 0
        self.put(None)
        wait = 0
        while self.thread_id is not None and wait <= self.max_wait_time:
            time.sleep(0.1)
            wait += 0.1
        if wait > self.max_wait_time:
            OBJ_WARNING(self, logger, "wait working thread timeout")
        while self.tasks.qsize() > 0:
            self.tasks.get(block=False)
        self.cancels = []
    
    def __working(self):
        OBJ_INFO(self, logger, "working thread starting")
        while self.running:
            try:
                self.cur_task_id, (func, args, kwargs) = self.tasks.get(self.max_wait_time)
                if func is None or not self.running : continue
                if self.cancels.count(self.cur_task_id) > 0:
                    self.cancels.remove(self.cur_task_id)
                    OBJ_DEBUG(self, logger, "cancel task[%d]", self.cur_task_id)
                    continue
                while len(self.cancels) > 0 and self.cancels[0] < self.cur_task_id:
                    self.cancels.pop(0)
                func(*args, **kwargs)
            except Empty:
                continue
            except Exception as ex:
                OBJ_ERROR(self, logger, "working thread Exception: %s",ex.message)
                continue
        self.thread_id = None
        OBJ_INFO(self, logger, "working thread exiting")
    
    def put(self, func, *args, **kwargs):
        return self.tasks.put([func, args, kwargs])

    def cancel(self, task_id):
        if task_id <= self.cur_task_id:
            return False
        self.cancels.append(task_id)
        return True

if __name__ == '__main__':
    if not LOG_INIT():
        raise -1
    
    worker = pipeWorker('testWorker')
    worker.start()
    def testA():
        print 'testA'
    def testB(x, y=0):
        print x,y
        time.sleep(0.5)
    try:
        i = 0
        while True:
            worker.put(testB, i, y=i)
            i += 1
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass 

    print 'cancle-0:',worker.cancel(0)
    print 'cancle-2:',worker.cancel(2)
    print 'cancle-4:',worker.cancel(4)
    print 'cancle-6:',worker.cancel(6)
    print 'cancle-8:',worker.cancel(8)
    print 'cancle-10:',worker.cancel(10)

    time.sleep(3)

    worker.stop()















  