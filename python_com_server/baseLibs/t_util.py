#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: 
Version: 1.0.0
Created: Tuyj
Created date:2015/1/19
'''

import datetime,re,uuid,os,sys
import random

#------------Common Function---------
def getLocalIp(ifname = 'eth0'):
    ifname = str(ifname)
    import socket,re
    try:
        import fcntl,struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        localIP = socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24]
        )
        s.close()
    except:
        localIP = None
    if localIP is not None:
        m = re.match(r'^(\d+).(\d+).(\d+).(\d+)', localIP)
    
    if localIP is None or m is None or localIP == '127.0.0.1' or localIP == '0.0.0.0':
        localIP = socket.gethostbyname(socket.gethostname())
        
    return localIP

def geNowTime(): #return yyyy-mm-dd-HH-MM-SS-mirsec
    timenow = datetime.datetime.now()
    return "%04d-%02d-%02d-%02d:%02d:%02d.%02s" % (timenow.year,timenow.month,timenow.day,timenow.hour,timenow.minute,timenow.second,str(timenow.microsecond)[:2])

def geSmartNowTime(): #return yyyymmddHHMMSS.mirsec
    timenow = datetime.datetime.now()
    return "%04d%02d%02d%02d%02d%02d.%02s" % (timenow.year,timenow.month,timenow.day,timenow.hour,timenow.minute,timenow.second,str(timenow.microsecond)[:2])

tsYear,tsMonth,tsDay,tsHour,tsMin,tsSec,tsMs = 0,1,2,3,4,5,6
tsValue = ["timenow.year","timenow.month","timenow.day","timenow.hour","timenow.minute","timenow.second","str(timenow.microsecond)[:2]"]
tsFormat = ["%04d","%02d","%02d","%02d","%02d","%02d",".%02s"]
def getTimestampByDate(level):
    timenow = datetime.datetime.now()
    ts = ""
    for i in range(0, level+1):
        ts += tsFormat[i] % eval(tsValue[i])
    return ts

def isPortUsed(port, protocol='tcp'):
    out = os.popen(''' netstat -anp | egrep :%s | grep %s | grep -v "grep" | awk '{print $4}' ''' % (port, protocol)).read()
    out.strip('\r')
    out.strip('\n')
    out.strip()
    if out == '':
        return False
    else:
        return True
    
def findUnusedPort(base, protocol='tcp'):
    while isPortUsed(base, protocol):
        base += 1
        if base > 65534:
            raise -2
    return base

import argparse
class eg_ArgumentParser(argparse.ArgumentParser):
    def __init__(self, eg='', *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, **kwargs)
        self.eg = eg
    def print_usage(self, file=None):
        argparse.ArgumentParser.print_usage(self, file)
        self._print_message('e.g.:\n', file)
        self._print_message(self.eg+'\n', file)
 
def getRealZmqAddr(addrs, fix):
    for addr in addrs:
        if addr[:3] == 'ipc':
            return addr
        if addr[:3] not in ['tcp', 'udp']:
            continue
        m = re.match(r'(tcp|udp)://(.+):(\d+)', addr)
        if m is None:
            continue
        typ,ip,port = m.groups()
        if ip in ['*', '127.0.0.1', 'localhost']:
            return '%s://%s:%s' % (typ, fix, port)
        else:
            return addr
    return None

def getMAC(by_uuid=True, ethx=None):
    if by_uuid:
        node = uuid.getnode()
        mac = uuid.UUID(int = node).hex[-12:] 
        #return ":".join([mac[e:e+2] for e in range(0,11,2)])  
        return '%s:%s:%s:%s:%s:%s' % (mac[0:2],mac[2:4],mac[4:6],mac[6:8],mac[8:10],mac[10:])
    else:
        if sys.platform == "win32":
            for line in os.popen("ipconfig /all"):
                if line.lstrip().startswith("Physical Address") or line.lstrip().startswith("物理地址"):
                    return line.split(":")[1].strip().replace("-", ":").lower()
        else:
            for line in os.popen("/sbin/ifconfig"):
                if 'Ether' in line:
                    if ethx is not None and not ethx in line:
                        continue
                    return line.split()[4].lower()
        return None

class fixList(list):
    def __init__(self, size):
        self.size = size
        for i in xrange(0,size):
            self.append(None)
    def clear(self):
        for i in xrange(0,self.size):
            self[i] = None
    def getLeft(self):
        for i in xrange(0,self.size):
            if self[i] is None:
                return i
        return None
    def remove(self, value):
        for i in xrange(0,self.size):
            if self[i] == value:
                self[i] = None
                return i
        return None
    def pop(self, key):
        if key > self.size:
            raise IndexError
        re = self[key]
        self[key] = None
        return re
    def key(self, value):
        for i in xrange(0,self.size):
            if self[i] == value:
                return i
        return None
    get = getLeft
    
class p2pDict(dict):
    def get_key(self, value):
        for k,v in self.iteritems():
            if v == value:
                return k
        return None

def get_pids(cmd):
    out = []
    pids = os.popen(cmd).read().strip('\r').strip('\n').strip()
    for pid in pids.split('\n'):
        if pid != '':
            out.append(pid)
    return out

strMaps = 'ZYXWVUTSRQPONMLKJIHGFEDCBA0123456789'
def getRandomStr(width):
    map = strMaps
    while len(map) < width:
        map = map * 2
    return ''.join(random.sample(map, width))

