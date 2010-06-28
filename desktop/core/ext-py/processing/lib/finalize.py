#
# Module supporting finaliztion using weakrefs
#
# processing/finalize.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

import weakref
import itertools

from processing.logger import subDebug

__all__ = ['Finalize', '_runFinalizers']


_registry = {}
_counter = itertools.count()


class Finalize(object):
    '''
    Class which supports object finalization using weakrefs
    '''  
    def __init__(self, obj, callback, args=(), kwargs=None, exitpriority=None):
        assert exitpriority is None or type(exitpriority) is int
        assert callback is not None
        
        if obj is not None:
            self._weakref = weakref.ref(obj, self)
        else:
            assert exitpriority is not None

        self._callback = callback
        self._args = args
        self._kwargs = kwargs or {}
        self._key = (exitpriority, _counter.next())
        
        _registry[self._key] = self
        
    def __call__(self, wr=None):
        '''
        Run the callback unless it has already been called or cancelled

        Returns True if callback was run otherwise returns False
        '''
        try:
            del _registry[self._key]
        except KeyError:
            subDebug('finalizer no longer registered')
        else:
            subDebug('finalizer calling %s with args %s and kwargs %s',
                     self._callback, self._args, self._kwargs)
            self._callback(*self._args, **self._kwargs)
            self._weakref = self._callback = self._args = \
                            self._kwargs = self._key = None
            return True

    def cancel(self):
        '''
        Cancel finalization of the object
        '''
        try:
            del _registry[self._key]
        except KeyError:
            pass
        else:
            self._weakref = self._callback = self._args = \
                            self._kwargs = self._key = None

    def stillActive(self):
        '''
        Return whether this finalizer is still waiting to invoke callback
        '''
        return self._key in _registry

    def __repr__(self):
        try:
            obj = self._weakref()
        except (AttributeError, TypeError):
            obj = None

        if obj is None:
            return '<Finalize object, dead>'

        x = '<Finalize object, callback=%s' % \
            getattr(self._callback, '__name__', self._callback)
        if self._args:
            x += ', args=' + str(self._args)
        if self._kwargs:
            x += ', kwargs=' + str(self._kwargs)
        if self._key[0] is not None:
            x += ', exitprority=' + str(self._key[0])
        return x + '>'


def _runFinalizers(minpriority=None):
    '''
    Run all finalizers whose exit priority is not None and at least minpriority
    
    Finalizers with highest priority are called first; finalizers with
    the same priority will be called in reverse order of creation.
    '''
    if minpriority is None:
        f = lambda p : p[0][0] is not None
    else:
        f = lambda p : p[0][0] is not None and p[0][0] >= minpriority

    items = sorted(filter(f, _registry.items()), reverse=True)

    for key, finalizer in items:
        subDebug('calling %s', finalizer)
        try:
            finalizer()
        except Exception:
            import traceback
            traceback.print_exc()

    if minpriority is None:
        _registry.clear()
