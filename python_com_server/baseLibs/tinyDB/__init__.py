#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: a tiny Database
Created: Tuyj
Created date:2015/12/18
'''

if __name__ == '__main__': import _env

import os,copy,json,re,shutil,threading
import baseLibs.t_com as t_com
import baseLibs.multi_task.t_multitask as t_multitask 
from baseLibs.t_util import geSmartNowTime

from baseLibs.log.t_log import *
logger = LOG_MODULE_DEFINE('tinyDB')
SET_LOG_LEVEL(logger, 'debug')

tTypes = {}
class ParamsInvalid(Exception): pass
class KeyInflict(Exception): pass

class tItem:
    _Keys = [] #keyNames
    _KeyFuncs = {} #keyName: (preProcessFunction,postProcessingFunction)
    _Separator = '||' #Separator of Record
    def __init__(self, *args, **kwargs):
        for keyname in self._Keys:
            self.__dict__[keyname] = None
        self.Update(*args, **kwargs)
    def Update(self, *args, **kwargs):
        for key,value in zip(self._Keys, args):
            func = self._KeyFuncs[key][0]
            self.__dict__[key] = value if func is None else func(value)
        for key,value in kwargs.iteritems():
            if key in self._Keys:
                func = self._KeyFuncs[key][0]
                self.__dict__[key] = value if func is None else func(value)
    def UpdateFromString(self, record):
        tmp = record.split(self._Separator)
        values = []
        for v in tmp:
            values.append(v.strip())
        return self.Update(*values)
    def UpdateFromOther(self, other):
        for key in self._Keys:
            value = other.__dict__[key]
            if value is not None:
                self.__dict__[key] = value 
    def isEqual(self, other):
        if other.__class__ != self.__class__:
            return False
        for key in self._Keys:
            if self.__dict__[key] != other.__dict__[key]:
                return False
        return True
    def isEqualWithString(self, ValueStr):
        other = self.__class__()
        other.UpdateFromString(ValueStr)
        return self.isEqual(other)
    def Value(self, key, flag=None): #preProcess:0 postProcess:1 nullProcess:None
        if flag is None:
            return self.__dict__[key]
        else:
            func = self._KeyFuncs[key][flag]
            return self.__dict__[key] if func is None else func(self.__dict__[key])
    def Values(self, flag=None):    #preProcess:0 postProcess:1 nullProcess:None
        values = []
        for key in self._Keys:
            values.append(self.Value(key, flag))
        return values
    def __repr__(self):
        values = []
        for key in self._Keys:
            func = self._KeyFuncs[key][1]
            value = self.__dict__[key]
            values.append( value if func is None else func(value) )
        out = self._Separator.join(values)
        if isinstance(out, unicode):
            return out.encode('utf8')
        return out
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key , value):
        self.__dict__[key] = value
        
class tTable:
    _pKey = None  #primaryKey
    _pKeyFuncs = [str, None] #primaryKey's preProcessFunction,postProcessingFunction
    _uKeys = [] #uniqueKeys
    def __init__(self, itemType, itemStrs={}, items={}, needCopy=False):
        '''items={primaryKey: tItem} ,itemStrs={primaryKey: tItemString} '''
        self.itemType = itemType
        self.uMap = {}
        for key in self._uKeys:
            self.uMap[key] = {}
        if needCopy:
            self.items = copy.deepcopy(items)
        else:
            self.items = items
        self.AddByString(itemStrs)
    
    def Reset(self, *args, **kwargs):
        return False

#     def Reset(self):
#         changed = False
#         for uKey in self._uKeys:
#             self.uMap[uKey] = {}
#         for pKey,item in self.items.iteritems():
#             for uKey in self._uKeys:
#                 if item.__dict__[uKey] is not None:
#                     item.__dict__[uKey] = None
#                     changed = True
#         return changed

    def Add(self, valuess):
        ''' valuess={primaryKey: [...]} or {primaryKey: {}} '''
        items,errs = self._valuess2Items(valuess)
        out = self.AddByItem(items)
        if out is not None:
            errs.update(out)
        return None if len(errs) == 0 else errs
    
    def AddByItem(self, items):
        ''' items={primaryKey: tItem} '''
        errs = {}
        for pKey,item in items.iteritems():
            pKey_ = self._pKeyFuncs[0](pKey)
            u_values,err = self._checkLegality(pKey_, item)
            if err is not None:
#                 L_WARNING(logger, "AddByItem failure:%s", err)
                errs[pKey] = err
                continue
            for u_key,u_value in u_values.iteritems():
                self.uMap[u_key][u_value] = pKey_
            self.items[pKey_] = item
        return None if len(errs) == 0 else errs
    
    def AddByString(self, itemStrs):
        ''' itemStrs={primaryKey: tItemString} '''
        items,errs = self._itemStr2Items(itemStrs)
        out = self.AddByItem(items)
        if out is not None:
            errs.update(out)
        return None if len(errs) == 0 else errs

    def Remove(self, pKeys):
        ''' pKeys=[pK1, pK2, ...] '''
        errs = {}
        for pKey in pKeys:
            pKey_ = self._pKeyFuncs[0](pKey)
            try:
                item = self.items.pop(pKey_)
                try: self._onRemovedItem(item)
                except KeyError: L_WARNING(logger, "logical error")
            except KeyError:
                err = "primaryKey[%s] not found" % pKey_
#                 L_WARNING(logger, "%s", err)
                errs[pKey] = err
        return None if len(errs) == 0 else errs

    def Get(self, pKeys):
        '''pKeys = [pK1, pK2] return {pK1: item1, pK2: None} or None
           if pKeys is None, it means get all items
        '''
        if pKeys is None:
            pKeys = self.items.keys()
        out = {}
        for pKey in pKeys:
            pKey_ = self._pKeyFuncs[0](pKey)
            try: out[pKey] = self.items[pKey_]
            except KeyError:
                out[pKey] = None
        return None if len(out) == 0 else out

    def GetValues(self, pKeys, flag=None):
        '''pKeys = {pK1: [pK1k1, pK1k2], pK2: None} or None or [pK1, pK2]
           flag = preProcess:0 postProcess:1 nullProcess:None 
           return {pK1: [pK1v1, pK1v2], pK2: [....]} or None
           if pKeys is None, it means get all items
           if pKk is None or pKeys is list, it means get all value for the pKey
        '''
        if pKeys is None:
            pKeys = self.items.keys()
        if isinstance(pKeys, list):
            pKeys = dict( zip(pKeys, [None]*len(pKeys)) )
        out = {}
        for pKey,Ks in pKeys.iteritems():
            pKey_ = self._pKeyFuncs[0](pKey)
            try: 
                item = self.items[pKey_]
                if Ks is None:
                    kVs = item.Values(flag)
                else:
                    kVs = []
                    for key in Ks:
                        kVs.append(item.Value(key, flag))
                out[pKey] = kVs
            except KeyError:
                out[pKey] = None
        return None if len(out) == 0 else out

    def GetByUKey(self, uKeyName, uKeys):
        '''uKeys = [uK1, uK2] return {uK1: (pKey,item1), uK2: None} or None
           if uKeys is None, it means get all items which has uKeyName
        '''
        out = {}
        u_keys = self.uMap[uKeyName]
        func = self.itemType._KeyFuncs[uKeyName][0]
        if uKeys is None:
            uKeys = u_keys.keys()
        for uKey in uKeys:
            uKey_ = uKey if func is None else func(uKey)
            try:
                pKey = u_keys[uKey_]
                out[uKey] = (pKey, self.items[pKey])
            except KeyError:
                out[uKey] = None
        return None if len(out) == 0 else out

    def Select(self, Cond):
        out = {}
        for pKey,item in self.items.iteritems():
            if Cond(pKey, item):
                out[pKey] = item
        return None if len(out) == 0 else out

    def Update(self, valuess):
        ''' valuess={primaryKey: [...]} or {primaryKey: {}} '''
        items,errs = self._valuess2Items(valuess)
        out = self.UpdateByItem(items)
        if out is not None:
            errs.update(out)
        return None if len(errs) == 0 else errs
    
    def UpdateByItem(self, items):
        ''' items={primaryKey: tItem} '''
        errs = {}
        for pKey,item in items.iteritems():
            pKey_ = self._pKeyFuncs[0](pKey)
            if not self.items.has_key(pKey_):
                err = "primaryKey[%s] not found", pKey_
#                 L_WARNING(logger, "UpdateByItem failure:%s", err)
                errs[pKey] = err
                continue
            u_values,err = self._checkLegality(pKey_, item, checkPKey=False)
            if err is not None:
#                 L_WARNING(logger, "UpdateByItem failure:%s", err)
                errs[pKey] = err
                continue
            update_item = self.items[pKey_]
            for u_key,u_new_value in u_values.iteritems():
                u_old_value = update_item.Value(u_key)
                if u_old_value != u_new_value:
                    if u_old_value is not None:
                        self.uMap[u_key].pop(u_old_value)
                    if u_new_value is not None:
                        self.uMap[u_key][u_new_value] = pKey_
            update_item.UpdateFromOther(item)
        return None if len(errs) == 0 else errs

    def UpdateByString(self, itemStrs):
        ''' items={primaryKey: tItemString} '''
        items,errs = self._itemStr2Items(itemStrs)
        out = self.UpdateByItem(items)
        if out is not None:
            errs.update(out)
        return None if len(errs) == 0 else errs
    
    def pKeys(self, flag = None):
        #flag = preProcess:0 postProcess:1 nullProcess:None
        if flag is None or self._pKeyFuncs[flag] is None:
            return self.items.keys()
        func = self._pKeyFuncs[flag]
        out = []
        for pkey in self.items.keys():
            out.append(func(pkey))
        return out
    
    def Dump2Json(self):
        data = {}
        for pKey,item in self.items.iteritems():
            func = self._pKeyFuncs[1]
            pKey = pKey if func is None else func(pKey)
            data[pKey] = str(item)
        return (self.__class__.__name__, data)
    
    def _checkLegality(self, key, item, checkPKey=True):
        if checkPKey and self.items.has_key(key):
            err = "primaryKey[%s:%s] inflict" % (self._pKey, key)
            return None,err
        u_values = {}
        for u_key in self._uKeys:
            u_value = item.Value(u_key)
            if u_value is not None:
                try:
                    p_key = self.uMap[u_key][u_value]
                    if p_key != key:
                        err = "uniqueKey[%s:%s] inflict with [%sX%s]" % (u_key, u_value, p_key, key)
                        return None,err
                except KeyError: pass
                u_values[u_key] = u_value
        return u_values,None

    def _onRemovedItem(self, item):
        for u_key in self._uKeys:
            u_value = item.Value(u_key)
            if u_value is not None:
                self.uMap[u_key].pop(u_value)

    def _valuess2Items(self, valuess):
        errs = {}
        items = {}
        for pKey,values in valuess.iteritems():
            pKey = self._pKeyFuncs[0](pKey)
            try:
                if isinstance(values, (list, tuple)):
                    item = self.itemType(*values)
                elif isinstance(values, dict):
                    item = self.itemType(**values)
                else:
                    raise ParamsInvalid('Invalid Values')
            except ParamsInvalid as ex:
                err = "New %s failure:%s" % (self.itemType, ex.message)
#                 L_WARNING(logger, "%s", err)
                errs[pKey] = err
                continue
            items[pKey] = item
        return items,errs

    def _itemStr2Items(self, itemStrs):
        errs = {}
        items = {}
        for pKey,itemStr in itemStrs.iteritems():
            pKey = self._pKeyFuncs[0](pKey)
            item = self.itemType()
            try:
                item.UpdateFromString(itemStr)
            except ParamsInvalid as ex:
                err = "item[%s] UpdateFromString failure:%s" % (self.itemType, ex.message)
#                 L_WARNING(logger, "%s", err)
                errs[pKey] = err
                continue
            items[pKey] = item
        return items,errs

class tDatabase:
    def __init__(self, full_filename, indent=2, smart=True, tasker=None, intervals=(3, 2, 2)):
        self.filename,self.indent,self.smart,self.tasker = full_filename,indent,smart,tasker
        self.autoSaveInv,self.deletelastBad,self.deletelastBak = intervals
        self.autoSaveInv = self.autoSaveInv if self.autoSaveInv > 0 else 3
        self.is_ext_tasker = True
        self.changed = False
        self.gen_auto_flush = None
        self.rlock = threading.RLock()
        self.tables = None

    def Close(self):
        self.rlock.acquire()
        self.__flush2file()
        self.rlock.release()
        if self.gen_auto_flush is not None:
            self.gen_auto_flush.close()
            self.gen_auto_flush = None
        if self.tasker is not None and not self.is_ext_tasker:
            self.tasker.stop()
            self.tasker = None

    def Init(self):
        if self.tables is None:
            self.tables = {}
            if os.path.isdir(self.filename):
                raise ValueError('[%s] is Directory' % self.filename)
            if not os.path.exists(self.filename):
                fp = open(self.filename, 'w')
                fp.write('{}')
                fp.close()
            fp = open(self.filename, 'r')
            try:
                entrys = json.load(fp)
                fp.close()
            except:
                fp.close()
                if not self.smart or not self.__auto_fix():
                    raise
                fp = open(self.filename, 'r')
                entrys = json.load(fp)
                fp.close()
            for tName,(tType, tData) in entrys.iteritems():
                if tTypes.has_key(tType):
                    self.tables[tName] = tTypes[tType](itemStrs=tData)
                else:
                    L_ERROR(logger, "Init failure:[%s] is unknow", tName)
                    continue
        
        if self.smart and self.tasker is None:
            self.tasker = t_multitask.tMultitaskMgr('cfg-tasker@'+self.filename)
            self.tasker.run(t_com.default_mini_thread_stack_size)
            self.is_ext_tasker = False
        if self.tasker is not None:
            self.gen_auto_flush = self._g_auto_flush()
            self.tasker.add(self.gen_auto_flush)

    def Save(self, force=False):
        self.rlock.acquire()
        self.__flush2file(force)
        self.rlock.release()

    def CreateTable(self, tClass, tName):
        self.rlock.acquire()
        try:
            if self.tables.has_key(tName):
                raise KeyInflict("Table Name[%s]" % tName)
            self.tables[tName] = tClass()
            self.changed = True
        except:
            self.rlock.release()
            raise
        self.rlock.release()

    def DropTable(self, tName):
        self.rlock.acquire()
        try:
            if not self.tables.has_key(tName):
                self.rlock.release()
                L_WARNING(logger, "Table[%s] not found", tName)
                return
            self.tables.pop(tName)
            self.changed = True
        except:
            self.rlock.release()
            raise
        self.rlock.release()
    
    def Reset(self, tName, *args, **kwargs):
        self.rlock.acquire()
        try:
            if self.tables[tName].Reset(*args, **kwargs):
                self.changed = True
        except:
            self.rlock.release()
            raise
        self.rlock.release()
    
    def pKeys(self, tName, flag = None):
        return self.tables[tName].pKeys(flag)
    
    def Insert(self, tName, Values):
        ''' Values={primaryKey: [...]} or {primaryKey: {}} '''
        self.rlock.acquire()
        try:
            out = self.tables[tName].Add(Values)
            if out is None or len(out) < len(Values):
                self.changed = True
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out
        
    def InsertByString(self, tName, ValueStrs):
        ''' ValueStrs={primaryKey: tItemString} '''
        self.rlock.acquire()
        try:
            out = self.tables[tName].AddByString(ValueStrs)
            if out is None or len(out) < len(ValueStrs):
                self.changed = True
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out
        
    def Delete(self, tName, pKeys):
        self.rlock.acquire()
        try:
            out = self.tables[tName].Remove(pKeys)
            if out is None or len(out) < len(pKeys):
                self.changed = True
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out
        
    def SearchByPKeys(self, tName, pKeys):
        '''if pKeys is None, it means get all items'''
        self.rlock.acquire()
        try:
            out = self.tables[tName].Get(pKeys)
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out
    
    def SearchValues(self, tName, pKeys, flag=None):
        '''pKeys = {pK1: [pK1k1, pK1k2], pK2: None} or None or [pK1, pK2]
           flag = preProcess:0 postProcess:1 nullProcess:None 
           return {pK1: [pK1v1, pK1v2], pK2: [....]} or None
           if pKeys is None, it means get all items
           if pKk is None or pKeys is list, it means get all value for the pKey
        '''
        self.rlock.acquire()
        try:
            out = self.tables[tName].GetValues(pKeys, flag)
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out
    
    def SearchByUKeys(self, tName, uKeyName, uKeys):
        '''if uKeys is None, it means get all items which has uKeyName'''
        self.rlock.acquire()
        try:
            out = self.tables[tName].GetByUKey(uKeyName, uKeys)
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out
    
    def Select(self, tName, Cond):
        self.rlock.acquire()
        try:
            out = self.tables[tName].Select(Cond)
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out
        
    def Update(self, tName, Values):
        self.rlock.acquire()
        try:
            out = self.tables[tName].Update(Values)
            if out is None or len(out) < len(Values):
                self.changed = True
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out
        
    def UpdateByString(self, tName, ValueStrs):
        self.rlock.acquire()
        try:
            out = self.tables[tName].UpdateByString(ValueStrs)
            if out is None or len(out) < len(ValueStrs):
                self.changed = True
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out

    def DumpTable(self, tName):
        self.rlock.acquire()
        try:
            out = self.tables[tName].Dump2Json()
        except:
            self.rlock.release()
            raise
        self.rlock.release()
        return out[1]

    def _g_auto_flush(self):
        while True:
            yield t_multitask.sleep(self.autoSaveInv)
            self.rlock.acquire()
            self.__flush2file()
            self.rlock.release()
        
    def __flush2file(self, force=False):
        if self.changed or force:
            self.__auto_bak()
            out = {}
            for tName,tb in self.tables.iteritems():
                out[tName] = tb.Dump2Json()
            fp = open(self.filename, 'w')
            json.dump(out, fp, indent=self.indent)
            fp.close()
            self.changed = False
    
    def __auto_bak(self):
        path = os.path.dirname(self.filename)
        name = os.path.basename(self.filename)
        if path == '':
            path = './'
        files = os.listdir(path)
        baks = []
        for file_ in files:
            if not os.path.isfile(os.path.join(path, file_)):
                continue
            m = re.match(r'^.%s.(\d+\.\d+)$' % name, file_)
            if m is None:
                continue
            baks.append(m.groups()[0])
        baks.sort(reverse=True)
        while len(baks) >= self.deletelastBak:
            oldest = '.%s.%s' % (name,baks.pop())
            oldest = os.path.join(path, oldest)
            os.remove(oldest)
        bak_name = '.%s.%s' % (name, geSmartNowTime())
        shutil.copyfile(self.filename, os.path.join(path, bak_name))
        
    def __auto_fix(self):
        path = os.path.dirname(self.filename)
        name = os.path.basename(self.filename)
        files = os.listdir(path)
        baks = []
        bads = []
        for file_ in files:
            if not os.path.isfile(os.path.join(path, file_)):
                continue
            m = re.match(r'^%s.\d+\.\d+.bad$' % name, file_)
            if m is not None:
                bads.append(os.path.join(path, file_))
                continue
            m = re.match(r'^.%s.(\d+\.\d+)$' % name, file_)
            if m is None:
                continue
            baks.append(m.groups()[0])
        baks.sort(reverse=True)
        last_bak_file = None
        if len(baks) > 0: 
            last_bak_file = '.%s.%s' % (name,baks[0])
            last_bak_file = os.path.join(path, last_bak_file)
        if last_bak_file is None:
            return False
        bads.sort(reverse=True)
        while len(bads) >= self.deletelastBad:
            os.remove(bads.pop())
        os.rename(self.filename, '%s.%s.bad' % (self.filename, geSmartNowTime()))
        shutil.copyfile(last_bak_file, self.filename)
        return True







