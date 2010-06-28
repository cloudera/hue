#
# Module supporting logging 
#
# processing/logger.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

import sys

__all__ = ['enableLogging', 'getLogger', 'subDebug',
           'debug', 'info', 'subWarning']

NOTSET = 0
SUBDEBUG = 5
DEBUG = 10
INFO = 20
SUBWARNING = 25

DEFAULT_FORMAT = '[%(levelname)s/%(processName)s] %(message)s'

_logger = None

def subDebug(msg, *args):
    if _logger:
        _logger.log(SUBDEBUG, msg, *args)

def debug(msg, *args):
    if _logger:
        _logger.log(DEBUG, msg, *args)

def info(msg, *args):
    if _logger:
        _logger.log(INFO, msg, *args)

def subWarning(msg, *args):
    if _logger:
        _logger.log(SUBWARNING, msg, *args)

def getLogger():
    '''
    Returns logger used by processing
    '''
    return _logger


def enableLogging(level, HandlerType=None, handlerArgs=(), format=None):
    '''
    Enable logging using `level` as the debug level
    '''
    global _logger
    import logging, atexit
    from processing import process

    logging._acquireLock()
    try:
        if _logger is None:
            temp = logging.getLogger('processing')
            temp._extra_args = (HandlerType, handlerArgs, format)
            _logger = temp
            _logger.propagate = 0

            def makeRecord(self, *args):
                record = self.__class__.makeRecord(self, *args)
                record.processName = process.currentProcess()._name
                return record
            
            MethodType = type(_logger.log)
            _logger.makeRecord = MethodType(makeRecord, _logger)
            logging.addLevelName(SUBDEBUG, 'SUBDEBUG')
            logging.addLevelName(SUBWARNING, 'SUBWARNING')

            # cleanup func of `processing` should run before that of `logging`
            atexit._exithandlers.remove((process._exitFunction, (), {}))
            atexit._exithandlers.append((process._exitFunction, (), {}))

            HandlerType = HandlerType or logging.StreamHandler

        if HandlerType:
            format = format or DEFAULT_FORMAT
            handler = HandlerType(*handlerArgs)
            handler.setFormatter(logging.Formatter(format))
            _logger.handlers = [handler]     # overwrites any old handler
            _logger.setLevel(level)
            _logger._extra_args = (HandlerType, handlerArgs, format)
        else:
            _logger.setLevel(level)
    finally:
        logging._releaseLock()
