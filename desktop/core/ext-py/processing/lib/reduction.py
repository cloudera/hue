#
# Module to support the pickling of different types of connection
# objects and file objects so that they can be transferred between
# different processes.
#
# processing/reduction.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

__all__ = []

import os
import sys
import socket
import threading
import copy_reg
import processing

from processing import _processing
from processing.logger import debug, subDebug, subWarning
from processing.forking import thisThreadIsSpawning
from processing.process import _registerAfterFork

#
#
#

connections_are_picklable = (
    sys.platform == 'win32' or hasattr(_processing, 'recvFd')
    )

try:
    fromfd = socket.fromfd
except AttributeError:
    def fromfd(fd, family, type, proto=0):
        s = socket._socket.socket()
        _processing.changeFd(s, fd, family, type, proto)
        return s

#
# Platform specific definitions
#

if sys.platform == 'win32':
    import _subprocess
    from processing._processing import win32

    closeHandle = win32.CloseHandle
    
    def duplicateHandle(handle):
        return _subprocess.DuplicateHandle(
            _subprocess.GetCurrentProcess(), handle,
            _subprocess.GetCurrentProcess(),
            0, False, _subprocess.DUPLICATE_SAME_ACCESS
            ).Detach()

    def sendHandle(conn, handle, destination_pid):
        process_handle = win32.OpenProcess(
            win32.PROCESS_ALL_ACCESS, False, destination_pid
            )
        try:
            new_handle = _subprocess.DuplicateHandle(
                _subprocess.GetCurrentProcess(), handle, 
                process_handle, 0, False, _subprocess.DUPLICATE_SAME_ACCESS
                )
            conn.send(new_handle.Detach())
        finally:
            win32.CloseHandle(process_handle)
            
    def recvHandle(conn):
        return conn.recv()

    def isInheritableHandle(handle):
        return (win32.GetHandleInformation(handle) & win32.HANDLE_FLAG_INHERIT)

else:
    closeHandle = os.close
    duplicateHandle = os.dup
    
    def sendHandle(conn, handle, destination_pid):
        _processing.sendFd(conn.fileno(), handle)
        
    def recvHandle(conn):
        return _processing.recvFd(conn.fileno())
    
    def isInheritableHandle(handle):
        return True

#
# Support for a per-process server thread which caches pickled handles
#

_cache = set()

def _reset(obj):
    global _lock, _listener, _cache
    for h in _cache:
        closeHandle(h)
    _cache.clear()
    _lock = threading.Lock()
    _listener = None

_reset(None)
_registerAfterFork(_reset, _reset)

def _getListener():
    global _listener

    if _listener is None:
        _lock.acquire()
        try:
            if _listener is None:
                from processing.connection import Listener
                debug('starting listener and thread for sending handles')
                _listener = Listener(authenticate=True)
                t = threading.Thread(target=_serve)
                t.setDaemon(True)
                t.start()
        finally:
            _lock.release()

    return _listener

def _serve():
    while 1:
        try:
            conn = _listener.accept()
            handle_wanted, destination_pid = conn.recv()
            _cache.remove(handle_wanted)
            sendHandle(conn, handle_wanted, destination_pid)
            closeHandle(handle_wanted)
            conn.close()
        except (SystemExit, KeyboardInterrupt):
            raise
        except:
            if not processing.currentProcess()._exiting:
                import traceback
                subWarning(
                    'thread for sharing handles raised exception :\n' +
                    '-'*79 + '\n' + traceback.format_exc() + '-'*79
                    )
    
#
# Functions to be used for pickling/unpickling objects with handles
#

def reduceHandle(handle):
    if thisThreadIsSpawning() and isInheritableHandle(handle):
        return (None, handle, True)
    dup_handle = duplicateHandle(handle)
    _cache.add(dup_handle)
    subDebug('reducing handle %d', handle)
    return (_getListener().address, dup_handle, False)

def rebuildHandle(pickled_data):
    from processing.connection import Client
    address, handle, inherited = pickled_data
    if inherited:
        return handle
    subDebug('rebuilding handle %d', handle)
    conn = Client(address, authenticate=True)
    conn.send((handle, os.getpid()))
    new_handle = recvHandle(conn)
    conn.close()
    return new_handle

#
# Register `_processing.Connection` with `copy_reg`
#

def reduceConnection(conn):
    return rebuildConnection, (reduceHandle(conn.fileno()),)

def rebuildConnection(reduced_handle):
    fd = rebuildHandle(reduced_handle)
    return _processing.Connection(fd, duplicate=False)

copy_reg.pickle(_processing.Connection, reduceConnection)

#
# Register `socket.socket` with `copy_reg`
#

def reduceSocket(s):
    try:
        Family, Type, Proto = s.family, s.type, s.proto
    except AttributeError:
        # have to guess family, type, proto
        address = s.getsockname()
        Family = type(address) is str and socket.AF_UNIX or socket.AF_INET
        Type = s.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
        Proto = 0
    reduced_handle = reduceHandle(s.fileno())
    return rebuildSocket, (reduced_handle, Family, Type, Proto)

def rebuildSocket(reduced_handle, family, type, proto):
    fd = rebuildHandle(reduced_handle)
    _sock = fromfd(fd, family, type, proto)
    closeHandle(fd)
    return socket.socket(_sock=_sock)

copy_reg.pickle(socket.socket, reduceSocket)

#
# Register `_processing.PipeConnection` with `copy_reg`
#

if sys.platform == 'win32':
    
    def reducePipeConnection(conn):
        return rebuildPipeConnection, (reduceHandle(conn.fileno()),)
    
    def rebuildPipeConnection(reduced_handle):
        handle = rebuildHandle(reduced_handle)
        return _processing.PipeConnection(handle, duplicate=False)
    
    copy_reg.pickle(_processing.PipeConnection, reducePipeConnection)
