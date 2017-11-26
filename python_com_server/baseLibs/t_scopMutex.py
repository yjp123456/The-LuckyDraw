#!/usr/bin/python2.7
#coding=utf8
r'''
Created: Tuyj
Created date:2015/12/15
'''
if __name__ == '__main__': import _env


class scopeMutex:
    def __init__(self, lock):
        self.lock = lock
        self.lock.acquire()
    def __del__(self):
        self.lock.release()
        self.lock = None

if __name__ == "__main__":
    import time, threading
    def test(l):
        print '1'
        sl = scopeMutex(l)
        print '2'
    
    l = threading.Lock()
    
    test(l)
    print '5'
    l.acquire()
    l.release()
    print '6'