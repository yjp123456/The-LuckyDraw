#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: 
Version: 1.0.0
Created: Tuyj
Created date:2015/5/16
'''

from Queue import Queue,Full,Empty,_time
class taskQue(Queue):
    def __init__(self, maxsize=0):
        Queue.__init__(self, maxsize)
        self.task_id = 0
        
    def put(self, item, block=True, timeout=None):
        """reference to Queue.Queue"""
        self.not_full.acquire()
        try:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() == self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() == self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a positive number")
                else:
                    endtime = _time() + timeout
                    while self._qsize() == self.maxsize:
                        remaining = endtime - _time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            task_id = self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
        finally:
            self.not_full.release()
        return task_id
    
    def _put(self, item):
        self.task_id += 1
        self.queue.append((self.task_id, item))
        return self.task_id
    
