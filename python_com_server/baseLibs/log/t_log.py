#!/usr/bin/python2.7
#coding=utf8
r'''
Fuction: 
Version: 1.0.0
Created: Tuyj
Created date:2015/1/22
'''

__all__ = [
           'LOG_INIT', 'RETRY_LOG_INIT', 'STD2FILE', 'BAK2STD', 'LOG_MODULE_DEFINE', 'SET_LOG_LEVEL', 'DealException',
           'T_DEBUG', 'T_INFO', 'T_WARNING', 'T_ERROR',
           'L_PRINT_DEBUG', 'L_PRINT_INFO', 'L_PRINT_WARNING', 'L_PRINT_ERROR',
           'L_DEBUG', 'L_INFO', 'L_WARNING', 'L_ERROR',
           'OBJ_DEBUG', 'OBJ_INFO', 'OBJ_WARNING', 'OBJ_ERROR',
           'WATCHING_LOG_MODULE', 'LOG_LEVELS', 'SWITCH_LOG_LEVEL', 'GET_LOG_CURLEVEL',
          ]

DEBUG_MODEL = True
import os,sys,logging,traceback
import log

LOG_MODULE_DEFINE = logging.getLogger
level_map = {
             'none'     : logging.NOTSET, 
             'debug'    : logging.DEBUG, 
             'info'     : logging.INFO,
             'warning'  : logging.WARNING,
             'error'    : logging.ERROR
            }

__LOG_MODULEs__ = {}
def SET_LOG_LEVEL(logger, level):
    if not level_map.has_key(level):
        return False
    logger.setLevel(level_map[level])
    __LOG_MODULEs__[logger] = level
    return True

WATCHING_LOG_MODULE = {}
def LOG_LEVELS():
    return ['debug','info','warning','error']
def GET_LOG_CURLEVEL(module_names=None):
    out = {}
    for name,logger in WATCHING_LOG_MODULE.iteritems():
        if module_names is None or name in module_names:
            if __LOG_MODULEs__.has_key(logger):
                out[name] = __LOG_MODULEs__[logger]
            else:
                out[name] = 'none' #logical error
    return out
def SWITCH_LOG_LEVEL(module_name, level_name):
    if not WATCHING_LOG_MODULE.has_key(module_name):
        return -1
    return 0 if SET_LOG_LEVEL(WATCHING_LOG_MODULE[module_name], level_name) else -1


class t_ColorizingStreamHandler(log.ColorizingStreamHandler):
    if os.name == 'nt':
        level_map = {
            logging.DEBUG: (None, 'blue', True),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', True),
            logging.ERROR: (None, 'red', True),
            logging.CRITICAL: ('red', 'white', True),
        }
    else:
        level_map = {
            logging.DEBUG: (None, 'white', False),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
        }

__handler = __root = __bak_stderr = __bak_stdout = None
def LOG_INIT(filePath = None):
    global __handler,__root
    if __root is None:
        __root = logging.getLogger()
        __root.setLevel(logging.INFO)
    if __handler is None:
        if filePath is None:
            __handler = t_ColorizingStreamHandler(stream=sys.stdout)
        else:
            try:
                __handler = logging.FileHandler(filePath)
            except:
                print 'logging.FileHandler failure:%s' % (sys and sys.exc_info() or None)
                return False
        __handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)d[%(levelname)s][%(name)s]%(message)s', datefmt='%H:%M:%S'))
        __handler.setLevel(logging.DEBUG)
        __root.addHandler(__handler)
    return True

def RETRY_LOG_INIT(filePath = None):
    global __handler,__root
    if __handler is not None:
        if __root is not None:
            __root.removeHandler(__handler)
        __handler.close()
        __handler = None
    return LOG_INIT(filePath)

def STD2FILE(file):
    global __bak_stderr,__bak_stdout
    if file is not None:
        __bak_stderr = sys.stderr
        __bak_stdout = sys.stdout
        sys.stdout = open(file, 'w+') 
        sys.stderr = sys.stdout

def BAK2STD():
    global __bak_stderr,__bak_stdout
    if __bak_stderr is not None:
        sys.stderr = __bak_stderr
        __bak_stderr = None
    if __bak_stdout is not None:
        sys.stdout = __bak_stdout
        __bak_stdout = None

r'''
T_XX vs     min(handler-level, root-level)
L_XX vs     min(handler-level, module-level)
OBJ_XX vs   min(handler-level, module-level)
'''
#-------------log with root module
def T_DEBUG(msg, *args, **kwargs):
    try:
        global __root
        if __root.isEnabledFor(logging.DEBUG):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + ']: ' + msg
            logging.debug(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def T_INFO(msg, *args, **kwargs):
    try:
        global __root
        if __root.isEnabledFor(logging.INFO):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + ']: ' + msg
            logging.info(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def T_WARNING(msg, *args, **kwargs):
    try:
        global __root
        if __root.isEnabledFor(logging.WARNING):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + ']: ' + msg
            logging.warning(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def T_ERROR(msg, *args, **kwargs):
    try:
        global __root
        if __root.isEnabledFor(logging.ERROR):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + ']: ' + msg
            logging.error(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

#-------------log with module name
def L_PRINT_DEBUG(logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def L_PRINT_INFO(logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.INFO):
            logger.debug(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def L_PRINT_WARNING(logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.WARNING):
            logger.debug(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def L_PRINT_ERROR(logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.ERROR):
            logger.debug(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)
              
def L_DEBUG(logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.DEBUG):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + ']: ' + msg
            logger.debug(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def L_INFO(logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.INFO):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + ']: ' + msg
            logger.info(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def L_WARNING(logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.WARNING):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + ']: ' + msg
            logger.warning(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def L_ERROR(logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.ERROR):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + ']: ' + msg
            logger.error(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

#-------------log with module name and obj name
def OBJ_DEBUG(obj, logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.DEBUG):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + '][' + obj.obj_name + ']: ' + msg
            logger.debug(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def OBJ_INFO(obj, logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.INFO):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + '][' + obj.obj_name + ']: ' + msg
            logger.info(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def OBJ_WARNING(obj, logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.WARNING):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + '][' + obj.obj_name + ']: ' + msg
            logger.warning(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)

def OBJ_ERROR(obj, logger, msg, *args, **kwargs):
    try:
        if logger.isEnabledFor(logging.ERROR):
            f = sys._getframe().f_back
            msg = '[' + f.f_code.co_filename + ':' +  str(f.f_lineno) + '][' + obj.obj_name + ']: ' + msg
            logger.error(msg, *args, **kwargs)
    except:
        print "Catch exception in X_DEGBUG/INFO/WARNING/ERROR:%s" % (sys and sys.exc_info() or None)


def DealException(level = 'error', extFlag = False):
    try:
        lvl = level_map[level]
        global __root
        if not __root.isEnabledFor(lvl):
            return ''
        
        (exc_type, exc_param, exc_tb) = sys.exc_info()
        errorInfo = 'Exception:'
        tracebackList = traceback.extract_tb(exc_tb)
        if DEBUG_MODEL:
            errorInfo += '\n======================traceback======================\n'
            for file, lineno, function, text in tracebackList:
                errorInfo += file + "::" + str(lineno) + "::" + function + '()\n'        
        else:
            file, lineno, function, text = tracebackList[-1]
            errorInfo += file + "::" + str(lineno) + ': '
        
        errorInfo += traceback.format_exception_only(exc_type, exc_param)[-1]
        if DEBUG_MODEL:
            errorInfo += '===================traceback over====================\n'
            
        if extFlag:
            return errorInfo
        if(lvl == logging.DEBUG):
            T_DEBUG(errorInfo)
        elif(lvl == logging.INFO):
            T_INFO(errorInfo)
        elif(lvl == logging.WARNING):
            T_WARNING(errorInfo)
        elif(lvl == logging.ERROR):
            T_ERROR(errorInfo)
        elif(lvl == logging.NOTSET):
            T_DEBUG(errorInfo)
        return ''
    except:pass

def test():
    LOG_INIT()
    logger = LOG_MODULE_DEFINE('local_test')
    SET_LOG_LEVEL(logger, 'info')
    T_INFO('global:%d', 123)
    L_INFO(logger, 'local:%d', 123)
    
    class T:
        def __init__(self, name):
            self.obj_name = name
        def test(self):
            OBJ_INFO(self, logger, 'obj: T::test')
            
    t = T('testT-0')
    t.test()
    SET_LOG_LEVEL(logger, 'error')
    t.test()
    try:
        xx.a
    except:
        DealException()

if __name__ == '__main__':
    test()
