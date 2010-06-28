#
# Module which supports allocation of ctypes objects from shared memory
#
# processing/sharedctypes.py
#
# Copyright (c) 2007-2008, R Oudkerk --- see COPYING.txt
#

import sys
import ctypes
import weakref
import copy_reg

from processing import heap, RLock
from processing.forking import assertSpawning

__all__ = ['RawValue', 'RawArray', 'Value', 'Array', 'copy', 'synchronized']

#
#
#

typecode_to_type = {
    'c': ctypes.c_char,  'u': ctypes.c_wchar,
    'b': ctypes.c_byte,  'B': ctypes.c_ubyte,
    'h': ctypes.c_short, 'H': ctypes.c_ushort,
    'i': ctypes.c_int,   'I': ctypes.c_uint,
    'l': ctypes.c_long,  'L': ctypes.c_ulong,
    'f': ctypes.c_float, 'd': ctypes.c_double
    }

#
#
#

def _newValue(type_):
    size = ctypes.sizeof(type_)
    wrapper = heap.BufferWrapper(size)
    return rebuildCtype(type_, wrapper, None)

def RawValue(typecode_or_type, *args):
    '''
    Returns a ctypes object allocated from shared memory
    '''
    type_ = typecode_to_type.get(typecode_or_type, typecode_or_type)
    obj = _newValue(type_)
    ctypes.memset(ctypes.addressof(obj), 0, ctypes.sizeof(obj))
    obj.__init__(*args)
    return obj

def RawArray(typecode_or_type, size_or_initializer):
    '''
    Returns a ctypes array allocated from shared memory
    '''
    type_ = typecode_to_type.get(typecode_or_type, typecode_or_type)
    if isinstance(size_or_initializer, int):
        type_ = type_ * size_or_initializer
        return _newValue(type_)
    else:
        type_ = type_ * len(size_or_initializer)
        result = _newValue(type_)
        result.__init__(*size_or_initializer)
        return result

def Value(typecode_or_type, *args, **kwds):
    '''
    Same as RawValue(), but by default uses a synchronization wrapper
    '''    
    lock = kwds.pop('lock', True)
    if kwds:
        raise ValueError, 'unrecognized keyword argument(s): %s' % kwds.keys()
    obj = RawValue(typecode_or_type, *args)
    if lock and not hasattr(lock, 'acquire'):
        lock = RLock()
    if lock:
        obj = synchronized(obj, lock)
    return obj

def Array(typecode_or_type, size_or_initializer, **kwds):
    '''
    Same as RawArray(), but by default uses a synchronization wrapper
    '''    
    lock = kwds.pop('lock', True)
    if kwds:
        raise ValueError, 'unrecognized keyword argument(s): %s' % kwds.keys()
    obj = RawArray(typecode_or_type, size_or_initializer)
    if lock and not hasattr(lock, 'acquire'):
        lock = RLock()
    if lock:
        obj = synchronized(obj, lock)
    return obj

def copy(obj):
    new_obj = _newValue(type(obj))
    ctypes.pointer(new_obj)[0] = obj
    return new_obj
    
def synchronized(obj, lock=None):
    assert not isinstance(obj, SynchronizedBase), 'object already synchronized'
    
    if isinstance(obj, ctypes._SimpleCData):
        return Synchronized(obj, lock)
    elif isinstance(obj, ctypes.Array):
        if obj._type_ is ctypes.c_char:
            return SynchronizedString(obj, lock)
        return SynchronizedArray(obj, lock)
    else:
        cls = type(obj)
        try:
            scls = classcache[cls]
        except KeyError:
            names = [field[0] for field in cls._fields_]
            d = dict((name, makeProperty(name)) for name in names)
            classname = 'Synchronized' + cls.__name__
            scls = classcache[cls] = type(classname, (SynchronizedBase,), d)
        return scls(obj, lock)

#
# Functions for pickling/unpickling
#

def reduceCtype(obj):
    assert sys.platform == 'win32', \
           'synchronized objects should only be shared through inheritance'
    if isinstance(obj, ctypes.Array):
        return rebuildCtype, (obj._type_, obj._wrapper, obj._length_)
    else:
        return rebuildCtype, (type(obj), obj._wrapper, None)
    
def rebuildCtype(type_, wrapper, length):
    if length is not None:
        type_ = type_ * length
    if sys.platform == 'win32' and type_ not in copy_reg.dispatch_table:
        copy_reg.pickle(type_, reduceCtype)
    obj = type_.from_address(wrapper.getAddress())
    obj._wrapper = wrapper
    return obj

#
# Function to create properties
#

def makeProperty(name):
    try:
        return propcache[name]
    except KeyError:
        d = {}
        exec template % ((name,)*7) in d
        propcache[name] = d[name]
        return d[name]

template = '''
def get%s(self):
    self.acquire()
    try:
        return self._obj.%s
    finally:
        self.release()            
def set%s(self, value):
    self.acquire()
    try:
        self._obj.%s = value
    finally:
        self.release()
%s = property(get%s, set%s)
'''

propcache = {}
classcache = weakref.WeakKeyDictionary()

#
# Synchronized wrappers
#

class SynchronizedBase(object):
    
    def __init__(self, obj, lock=None):
        self._obj = obj
        self._lock = lock or RLock()
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    def __reduce__(self):
        assertSpawning(self)
        return synchronized, (self._obj, self._lock)
    
    def getobj(self):
        return self._obj
    
    def getlock(self):
        return self._lock
    
    def __repr__(self):
        return '<%s wrapper for %s>' % (type(self).__name__, self._obj)
    
    
class Synchronized(SynchronizedBase):
    value = makeProperty('value')
    
    
class SynchronizedArray(SynchronizedBase):
    
    def __len__(self):
        return len(self._obj)
    
    def __getitem__(self, i):
        self.acquire()
        try:
            return self._obj[i]
        finally:
            self.release()
            
    def __setitem__(self, i, value):
        self.acquire()
        try:
            self._obj[i] = value
        finally:
            self.release()
            
    def __getslice__(self, start, stop):
        self.acquire()
        try:
            return self._obj[start:stop]
        finally:
            self.release()
            
    def __setslice__(self, start, stop, values):
        self.acquire()
        try:
            self._obj[start:stop] = values
        finally:
            self.release()
            
            
class SynchronizedString(SynchronizedArray):
    value = makeProperty('value')
    raw = makeProperty('raw')
