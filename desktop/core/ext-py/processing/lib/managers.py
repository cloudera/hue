#
# Module providing the `SyncManager` class for dealing
# with shared objects
#
# processing/managers.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'BaseManager', 'SyncManager', 'BaseProxy',
            'CreatorMethod', 'Token' ]

#
# Imports
#

import os
import sys
import socket
import weakref
import threading
import traceback
import array
import copy_reg
import cPickle

from processing.connection import Listener, Client, Pipe, AuthenticationError
from processing.connection import deliverChallenge, answerChallenge
from processing.process import Process, currentProcess
from processing.process import activeChildren, _registerAfterFork
from processing.logger import debug, info, subWarning
from processing.finalize import Finalize, _runFinalizers
from processing.forking import exit

#
# Register `array.array` for pickling
#

def reduceArray(a):
    return array.array, (a.typecode, a.tostring())

copy_reg.pickle(array.array, reduceArray)

#
# Exception class
#

class RemoteError(Exception):
    '''
    Exception type raised by managers
    '''
    def __init__(self, *args):
        if args:
            self.args = args
        else:
            info = sys.exc_info()
            self.args = (info[1], ''.join(traceback.format_exception(*info)))

    def __str__(self):
        return ('\n' + '-'*75 + '\nRemote ' + self.args[1] + '-'*75)

#
# Type for identifying shared objects
#

class Token(object):
    '''
    Type to uniquely indentify a shared object
    '''
    def __init__(self, typeid, address, id):
        self.typeid = typeid
        self.address = address
        self.id = id

    def __repr__(self):
        return 'Token(typeid=%r, address=%r, id=%r)' % \
               (self.typeid, self.address, self.id)

#
# Functions for communication with a manager's server process
#

def dispatch(c, id, methodname, args=(), kwds={}):
    '''
    Send a message to manager using connection `c` and return response
    '''
    c.send((id, methodname, args, kwds))
    kind, result = c.recv()
    if kind == '#RETURN':
        return result
    elif kind == '#ERROR':
        raise result
    else:
        raise ValueError

def transact(address, authkey, methodname, args=(), kwds={}):
    '''
    Create connection then send a message to manager and return response
    '''
    conn = Client(address, authkey=authkey)
    try:
        return dispatch(conn, None, methodname, args, kwds)
    finally:
        conn.close()

#
# Functions for finding the method names of an object
#

def allMethods(obj):
    '''
    Return a list of names of methods of `obj`
    '''
    temp = []
    for name in dir(obj):
        func = getattr(obj, name)
        if hasattr(func, '__call__'):
            temp.append(name)
    return temp

def publicMethods(obj):
    '''
    Return a list of names of methods of `obj` which do not start with '_'
    '''
    return filter(lambda name: name[0] != '_', allMethods(obj))

#
# Server which is run in a process controlled by a manager
#

class Server(object):
    '''
    Server class which runs in a process controlled by a manager object
    '''
    public = ['shutdown', 'create', 'acceptConnection',
              'getMethods', 'debugInfo', 'dummy', 'incref', 'decref']

    def __init__(self, registry, address, authkey):
        assert type(authkey) is str
        self.registry = registry
        self.authkey = authkey

        # do authentication later
        self.listener = Listener(address=address, backlog=5)

        self.address = self.listener.address
        if type(self.address) is tuple:
            self.address = (socket.getfqdn(self.address[0]), self.address[1])

        self.id_to_obj = {0: (None, ())}
        self.id_to_refcount = {}
        self.mutex = threading.RLock()
        self.stop = 0

    def serveForever(self):
        '''
        Run the server forever
        '''
        try:
            try:
                while 1:
                    c = self.listener.accept()
                    t = threading.Thread(target=self.handleRequest, args=(c,))
                    t.setDaemon(True)
                    t.start()
            except (KeyboardInterrupt, SystemExit):
                return
        finally:
            self.stop = 999
            self.listener.close()

    def handleRequest(self, c):
        '''
        Handle a new connection
        '''
        funcname = result = request = None
        try:
            deliverChallenge(c, self.authkey)
            answerChallenge(c, self.authkey)
            request = c.recv()
            ignore, funcname, args, kwds = request
            assert funcname in self.public, '%r unrecognized' % funcname
            func = getattr(self, funcname)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            msg = ('#ERROR', RemoteError())
        else:
            try:
                result = func(c, *args, **kwds)
                msg = ('#RETURN', result)
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                msg = ('#ERROR', RemoteError())

        try:
            c.send(msg)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception, e:
            if msg[0] == '#ERROR':
                subWarning('Failure to send exception: %r', msg[1])
            else:
                subWarning('Failure to send result: %r', msg[1])
            subWarning(' ... request was %r', request)
            subWarning(' ... exception was %r', e)

        c.close()

    def serveClient(self, connection):
        '''
        Handle requests from the proxies in a particular process/thread
        '''
        debug('starting server thread to service %r',
              threading.currentThread().getName())

        recv = connection.recv
        send = connection.send
        id_to_obj = self.id_to_obj

        while not self.stop:

            try:
                methodname = obj = None
                request = recv()
                ident, methodname, args, kwds = request
                obj, exposed = id_to_obj[ident]

                if methodname not in exposed:
                    raise AttributeError, (
                        'method %r of %r object is not in exposed=%r' %
                        (methodname, type(obj), exposed)
                        )

                function = getattr(obj, methodname)

                try:
                    result = function(*args, **kwds)
                    msg = ('#RETURN', result)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception, e:
                    msg = ('#ERROR', e)

            except AttributeError, e:
                if methodname is None:
                    msg = ('#ERROR', RemoteError())
                else:
                    try:
                        fallback_func = self.fallback_mapping[methodname]
                        result = fallback_func(
                            self, connection, ident, obj, *args, **kwds
                            )
                        msg = ('#RETURN', result)
                    except (SystemExit, KeyboardInterrupt):
                        raise
                    except Exception:
                        msg = ('#ERROR', RemoteError())

            except EOFError:
                debug('got EOF -- exiting thread serving %r',
                      threading.currentThread().getName())
                sys.exit(0)

            except (SystemExit, KeyboardInterrupt):
                raise

            except:
                msg = ('#ERROR', RemoteError())

            try:
                try:
                    send(msg)
                except cPickle.PicklingError:
                    result = msg[1]
                    if hasattr(result, '__iter__') and hasattr(result, 'next'):
                        try:
                            # send a proxy for this iterator
                            res_ident, _ = self.create(
                                connection, 'iter', result
                                )
                            res_obj, res_exposed = self.id_to_obj[res_ident]
                            token = Token('iter', self.address, res_ident)
                            result = IteratorProxy(token, incref=False)
                            msg = ('#RETURN', result)
                        except (SystemExit, KeyboardInterrupt):
                            raise
                        except Exception:
                            msg = ('#ERROR', RemoteError())
                    else:
                        msg = ('#ERROR', RemoteError())
                    send(msg)
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e:
                subWarning('exception in thread serving %r',
                        threading.currentThread().getName())
                subWarning(' ... message was %r', msg)
                subWarning(' ... exception was %r', e)
                connection.close()
                sys.exit(1)

    def fallbackGetValue(self, connection, ident, obj):
        return obj

    def fallbackStr(self, connection, ident, obj):
        return str(obj)

    def fallbackRepr(self, connection, ident, obj):
        return repr(obj)

    def fallbackCmp(self, connection, ident, obj, *args):
        return cmp(obj, *args)

    fallback_mapping = {
        '__str__':fallbackStr, '__repr__':fallbackRepr,
        '__cmp__':fallbackCmp, '#GETVALUE':fallbackGetValue
        }

    def dummy(self, c):
        pass

    def debugInfo(self, c):
        '''
        Return some info --- useful to spot problems with refcounting
        '''
        self.mutex.acquire()
        try:
            result = []
            keys = self.id_to_obj.keys()
            keys.sort()
            for ident in keys:
                if ident != 0:
                    result.append('  %s:       refcount=%s\n    %s' %
                                  (hex(ident), self.id_to_refcount[ident],
                                   str(self.id_to_obj[ident][0])[:75]))
            return '\n'.join(result)
        finally:
            self.mutex.release()

    def shutdown(self, c):
        '''
        Shutdown this process
        '''
        c.send(('#RETURN', None))
        info('manager received shutdown message')

        # do some cleaning up
        _runFinalizers(0)
        for p in activeChildren():
            debug('terminating a child process of manager')
            p.terminate()
        for p in activeChildren():
            debug('terminating a child process of manager')
            p.join()
        _runFinalizers()
        info('manager exiting with exitcode 0')

        # now exit without waiting for other threads to finish
        exit(0)
            
    def create(self, c, typeid, *args, **kwds):
        '''
        Create a new shared object and return its id
        '''
        self.mutex.acquire()
        try:
            callable, exposed = self.registry[typeid]
            obj = callable(*args, **kwds)

            if exposed is None:
                exposed = publicMethods(obj)

            ident = id(obj)

            debug('have created %r object with id %r', typeid, ident)

            self.id_to_obj[ident] = (obj, set(exposed))
            if ident not in self.id_to_refcount:
                self.id_to_refcount[ident] = None
            return ident, tuple(exposed)
        finally:
            self.mutex.release()

    def getMethods(self, c, token):
        '''
        Return the methods of the shared object indicated by token
        '''
        return tuple(self.id_to_obj[token.id][1])

    def acceptConnection(self, c, name):
        '''
        Spawn a new thread to serve this connection
        '''
        threading.currentThread().setName(name)
        c.send(('#RETURN', None))
        self.serveClient(c)

    def incref(self, c, ident):
        self.mutex.acquire()
        try:
            try:
                self.id_to_refcount[ident] += 1
            except TypeError:
                assert self.id_to_refcount[ident] is None
                self.id_to_refcount[ident] = 1
        finally:
            self.mutex.release()

    def decref(self, c, ident):
        self.mutex.acquire()
        try:
            assert self.id_to_refcount[ident] >= 1
            self.id_to_refcount[ident] -= 1
            if self.id_to_refcount[ident] == 0:
                del self.id_to_obj[ident], self.id_to_refcount[ident]
                debug('disposing of obj with id %d', ident)
        finally:
            self.mutex.release()

#
# Definition of BaseManager
#

class BaseManager(object):
    '''
    Base class for managers
    '''
    def __init__(self, address=None, authkey=None):
        '''
        `address`:
            The address on which manager should listen for new
            connections.  If `address` is None then an arbitrary one
            is chosen (which will be available as `self.address`).

        `authkey`:
            Only connections from clients which are using `authkey` as an
            authentication key will be accepted.  If `authkey` is `None`
            then `currentProcess().getAuthKey()` is used.
        '''
        self._address = address     # XXX not necessarily the final address
        if authkey is None:
            self._authkey = authkey = currentProcess().getAuthKey()
        else:
            self._authkey = authkey
        assert type(authkey) is str
        self._started = False

    def start(self):
        '''
        Spawn a server process for this manager object
        '''
        assert not self._started
        self._started = True

        self._registry, _ = BaseManager._getRegistryCreators(self)

        # pipe over which we will retreive address of server
        reader, writer = Pipe(duplex=False)

        # spawn process which runs a server
        self._process = Process(
            target=self._runServer,
            args=(self._registry, self._address, self._authkey, writer),
            )
        ident = ':'.join(map(str, self._process._identity))
        self._process.setName(type(self).__name__  + '-' + ident)
        self._process.setAuthKey(self._authkey)
        self._process.start()

        # get address of server
        writer.close()
        self._address = reader.recv()
        reader.close()

        # register a finalizer
        self.shutdown = Finalize(
            self, BaseManager._finalizeManager,
            args=(self._process, self._address, self._authkey),
            exitpriority=0
            )

    @classmethod
    def _runServer(cls, registry, address, authkey, writer):
        '''
        Create a server, report its address and run it
        '''
        # create server
        server = Server(registry, address, authkey)
        currentProcess()._server = server

        # inform parent process of the server's address
        writer.send(server.address)
        writer.close()

        # run the manager
        info('manager serving at %r', server.address)
        server.serveForever()

    def serveForever(self, verbose=True):
        '''
        Start server in the current process
        '''
        assert not self._started
        self._started = True

        registry, _ = BaseManager._getRegistryCreators(self)
        server = Server(registry, self._address, self._authkey)
        currentProcess()._server = server
        if verbose:
            print >>sys.stderr, '%s serving at address %s' % \
                  (type(self).__name__, server.address)
        server.serveForever()

    @classmethod
    def fromAddress(cls, address, authkey):
        '''
        Create a new manager object for a pre-existing server process
        '''
        manager = cls(address, authkey)
        transact(address, authkey, 'dummy')
        manager._started = True
        return manager

    def _create(self, typeid, *args, **kwds):
        '''
        Create a new shared object; return the token and exposed tuple
        '''
        assert self._started
        id, exposed = transact(
            self._address, self._authkey, 'create', (typeid,) + args, kwds
            )
        return Token(typeid, self._address, id), exposed

    def join(self, timeout=None):
        '''
        Join the manager process (if it has been spawned)
        '''
        self._process.join(timeout)

    def _debugInfo(self):
        '''
        Return some info about the servers shared objects and connections
        '''
        return transact(self._address, self._authkey, 'debugInfo')

    def _proxyFromToken(self, token):
        '''
        Create a proxy for a token
        '''
        assert token.address == self.address
        _, creators = BaseManager._getRegistryCreators(self)
        proxytype = creators[token.typeid]._proxytype
        return proxytype(token, authkey=self._authkey)

    @staticmethod
    def _getRegistryCreators(self_or_cls):
        registry = {}
        creators = {}
        for name in dir(self_or_cls):
            obj = getattr(self_or_cls, name)
            info = getattr(obj, '_manager_info', None)
            if info is not None and hasattr(obj, '__call__'):
                creators[name] = obj
                typeid, callable, exposed = info
                assert typeid not in registry, 'typeids must be unique'
                registry[typeid] = (callable, exposed)
        return registry, creators

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @staticmethod
    def _finalizeManager(process, address, authkey):
        '''
        Shutdown the manager process; will be registered as a finalizer
        '''
        if process.isAlive():
            info('sending shutdown message to manager')
            try:
                transact(address, authkey, 'shutdown')
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception:
                pass

            process.join(timeout=0.2)
            if process.isAlive():
                info('manager still alive')
                if hasattr(process, 'terminate'):
                    info('trying to `terminate()` manager process')
                    process.terminate()
                    process.join(timeout=0.1)
                    if process.isAlive():
                        info('manager still alive after terminate')

        try:
            del BaseProxy._address_to_local[address]
        except KeyError:
            pass
        
    address = property(lambda self: self._address)

    # deprecated
    from_address = fromAddress
    serve_forever = serveForever

#
# Function for adding methods to managers
#

def CreatorMethod(callable=None, proxytype=None, exposed=None, typeid=None):
    '''
    Returns a method for a manager class which will create
    a shared object using `callable` and return a proxy for it.
    '''
    if exposed is None and hasattr(callable, '__exposed__'):
        exposed = callable.__exposed__

    if proxytype is None:
        proxytype = MakeAutoProxy

    typeid = typeid or _uniqueLabel(callable.__name__)

    def temp(self, *args, **kwds):
        debug('requesting creation of a shared %r object', typeid)
        token, exp = self._create(typeid, *args, **kwds)
        proxy = proxytype(
            token, manager=self, authkey=self._authkey, exposed=exp
            )
        return proxy

    try:
        temp.__name__ = typeid
    except TypeError:
        pass
    temp._manager_info = (typeid, callable, exposed)
    temp._proxytype = proxytype
    return temp

def _uniqueLabel(prefix, _count={}):
    '''
    Return a string beginning with 'prefix' which has not already been used.
    '''
    try:
        _count[prefix] += 1
        return prefix + '-' + str(_count[prefix])
    except KeyError:
        _count[prefix] = 0
        return prefix

#
# Subclasses of threading.local and set which get cleared after a fork
#

class ProcessLocalSet(set):
    def __init__(self):
        _registerAfterFork(self, set.clear)
    def __reduce__(self):
        return type(self), ()

class ThreadLocalStorage(threading.local):
    def __init__(self):
        _registerAfterFork(self, _clearNamespace)
    def __reduce__(self):
        return type(self), ()

def _clearNamespace(obj):
    obj.__dict__.clear()

#
# Definition of BaseProxy
#

class BaseProxy(object):
    '''
    A base for proxies of shared objects
    '''
    _address_to_local = {}
    _mutex = threading.Lock()

    def __init__(self, token, manager=None,
                 authkey=None, exposed=None, incref=True):
        BaseProxy._mutex.acquire()
        try:
            tls_idset = BaseProxy._address_to_local.get(token.address, None)
            if tls_idset is None:
                tls_idset = ThreadLocalStorage(), ProcessLocalSet()
                BaseProxy._address_to_local[token.address] = tls_idset
        finally:
            BaseProxy._mutex.release()

        # self._tls is used to record the connection used by this
        # thread to communicate with the manager at token.address
        self._tls = tls_idset[0]

        # self._idset is used to record the identities of all shared
        # objects for which the current process owns references and
        # which are in the manager at token.address
        self._idset = tls_idset[1]

        self._token = token
        self._id = self._token.id
        self._manager = manager

        if authkey:
            self._authkey = authkey
        elif self._manager:
            self._authkey = self._manager
        else:
            self._authkey = currentProcess().getAuthKey()
        
        if incref:
            self._incref()
            
        _registerAfterFork(self, BaseProxy._afterFork)
        
    def _connect(self):
        debug('making connection to manager')
        name = currentProcess().getName()
        if threading.currentThread().getName() != 'MainThread':
            name += '|' + threading.currentThread().getName()
        connection = Client(self._token.address, authkey=self._authkey)
        dispatch(connection, None, 'acceptConnection', (name,))
        self._tls.connection = connection
        
    def _callMethod(self, methodname, args=(), kwds={}):
        '''
        Try to call a method of the referrent and return a copy of the result
        '''
        try:
            conn = self._tls.connection
        except AttributeError:
            debug('thread %r does not own a connection',
                 threading.currentThread().getName())
            self._connect()
            conn = self._tls.connection

        conn.send((self._id, methodname, args, kwds))
        kind, result = conn.recv()
        if kind == '#RETURN':
            return result
        elif kind == '#ERROR':
            raise result
        else:
            raise ValueError

    def _getValue(self):
        '''
        Get a copy of the value of the referent
        '''
        return self._callMethod('#GETVALUE')

    def _incref(self):
        connection = Client(self._token.address, authkey=self._authkey)
        dispatch(connection, None, 'incref', (self._id,))
        debug('INCREF %r', self._token.id)

        assert self._id not in self._idset    
        self._idset.add(self._id)

        shutdown = getattr(self._manager, 'shutdown', None)

        self._close = Finalize(
            self, BaseProxy._decref,
            args=(self._token, self._authkey, shutdown,
                  self._tls, self._idset),
            exitpriority=10
            )

    @staticmethod
    def _decref(token, authkey, shutdown, tls, idset):
        idset.remove(token.id)

        # check whether manager is still alive
        manager_still_alive = shutdown is None or shutdown.stillActive()
        if manager_still_alive:
            # tell manager this process no longer cares about referent
            try:
                debug('DECREF %r', token.id)
                connection = Client(token.address, authkey=authkey)
                dispatch(connection, None, 'decref', (token.id,))
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception, e:
                debug('... decref failed %s', e)

        else:
            debug('DECREF %r -- manager already shutdown',
                  token.id)

        # check whether we can close this thread's connection because
        # the process owns no more references to objects for this manager
        if not idset and hasattr(tls, 'connection'):
            debug('thread %r has no more proxies so closing conn',
                  threading.currentThread().getName())
            tls.connection.close()
            del tls.connection
            
    def _afterFork(self):
        self._manager = None
        self._incref()

    def __reduce__(self):
        if hasattr(self, '_exposed'):
            return (RebuildProxy, (MakeAutoProxy, self._token,
                                   {'exposed': self._exposed}))
        else:
            return (RebuildProxy, (type(self), self._token, {}))

    def __deepcopy__(self, memo):
        return self._getValue()
    
    def __hash__(self):
        raise NotImplementedError, 'proxies are unhashable'
    
    def __repr__(self):
        return '<Proxy[%s] object at %s>' % (self._token.typeid,
                                             '0x%x' % id(self))

    def __str__(self):
        '''
        Return representation of the referent (or a fall-back if that fails)
        '''
        try:
            return self._callMethod('__repr__')
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            return repr(self)[:-1] + "; '__str__()' failed>"

    # deprecated
    _callmethod = _callMethod
    _getvalue = _getValue

#
# Since BaseProxy._mutex might be locked at time of fork we reset it
#

def _resetMutex(obj):
    obj._mutex = threading.Lock()
_registerAfterFork(BaseProxy, _resetMutex)

#
# Function used for unpickling
#

def RebuildProxy(func, token, kwds={}):
    '''
    Function used for unpickling proxy objects.

    If possible the shared object is returned, or otherwise a proxy for it.
    '''
    server = getattr(currentProcess(), '_server', None)
    
    if server and server.address == token.address:
        return server.id_to_obj[token.id][0]
    else:
        incref = (
            kwds.pop('incref', True) and 
            not getattr(currentProcess(), '_inheriting', False)
            )
        try:
            return func(token, manager=None, authkey=None,
                        incref=incref, **kwds)
        except AuthenticationError:
            raise AuthenticationError, 'cannot rebuild proxy without authkey'

#
# Functions to create proxies and proxy types
#

def MakeAutoProxyType(exposed, typeid='unnamed', _cache={}):
    '''
    Return an auto-proxy type whose methods are given by `exposed`
    '''
    exposed = tuple(exposed)
    try:
        return _cache[(typeid, exposed)]
    except KeyError:
        pass

    dic = {}

    for name in exposed:
        exec '''def %s(self, *args, **kwds):
        return self._callMethod(%r, args, kwds)''' % (name, name) in dic

    ProxyType = type('AutoProxy[%s]' % typeid, (BaseProxy,), dic)
    ProxyType._exposed = exposed
    _cache[(typeid, exposed)] = ProxyType
    return ProxyType


def MakeAutoProxy(token, manager=None, authkey=None,
                  exposed=None, incref=True):
    '''
    Return an auto-proxy for `token`
    '''
    if exposed is None:
        exposed = transact(token.address, authkey, 'getMethods', (token,))
    ProxyType = MakeAutoProxyType(exposed, token.typeid)
    proxy = ProxyType(token, manager=manager, authkey=authkey, incref=incref)
    return proxy

#
# Types (or functions) which we will register with SyncManager
#

from threading import BoundedSemaphore, Condition, Event, \
     Lock, RLock, Semaphore
from Queue import Queue

class Namespace(object):
    '''
    Instances of this class can be used as namespaces.

    A namespace object has no public methods but does have writable
    attributes.  Its represention shows the values of its attributes.
    '''
    __exposed__ = ('__getattribute__', '__setattr__', '__delattr__')

    def __repr__(self):
        items = self.__dict__.items()
        temp = []
        for name, value in items:
            if not name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        return 'Namespace(%s)' % str.join(', ', temp)

class Value(object):
    '''
    Instances have a settable 'value' property
    '''
    def __init__(self, typecode, value, lock=True):
        self._typecode = typecode
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

    def __repr__(self):
        return '%s(%r, %r)'%(type(self).__name__, self._typecode, self._value)

    value = property(get, set)

#
# Proxy type used by BaseManager
#

class IteratorProxy(BaseProxy):
    '''
    Proxy type for iterators
    '''
    def __iter__(self):
        return self
    def next(self):
        return self._callMethod('next')

BaseManager._Iter = CreatorMethod(iter, IteratorProxy, ('next', '__iter__'))

#
# Proxy types used by SyncManager
#

class AcquirerProxy(BaseProxy):
    '''
    Base class for proxies which have acquire and release methods
    '''
    def acquire(self, blocking=1):
        return self._callMethod('acquire', (blocking,))
    def release(self):
        return self._callMethod('release')
    def __enter__(self):
        self._callMethod('acquire')
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._callMethod('release')


class ConditionProxy(AcquirerProxy):
    def wait(self, timeout=None):
        return self._callMethod('wait', (timeout,))
    def notify(self):
        return self._callMethod('notify')
    def notifyAll(self):
        return self._callMethod('notifyAll')


class NamespaceProxy(BaseProxy):
    '''
    Proxy type for Namespace objects.

    Note that attributes beginning with '_' will "belong" to the proxy,
    while other attributes "belong" to the referent.
    '''
    def __getattr__(self, key):
        if key[0] == '_':
            return object.__getattribute__(self, key)
        callmethod = object.__getattribute__(self, '_callMethod')
        return callmethod('__getattribute__', (key,))
    
    def __setattr__(self, key, value):
        if key[0] == '_':
            return object.__setattr__(self, key, value)
        callmethod = object.__getattribute__(self, '_callMethod')
        return callmethod('__setattr__', (key, value))
    
    def __delattr__(self, key):
        if key[0] == '_':
            return object.__delattr__(self, key)
        callmethod = object.__getattribute__(self, '_callMethod')
        return callmethod('__delattr__', (key,))
    

_list_exposed = (
    '__add__', '__contains__', '__delitem__', '__delslice__',
    '__cmp__', '__getitem__', '__getslice__', '__iter__', '__imul__',
    '__len__', '__mul__', '__reversed__', '__rmul__', '__setitem__',
    '__setslice__', 'append', 'count', 'extend', 'index', 'insert',
    'pop', 'remove', 'reverse', 'sort'
    )

BaseListProxy = MakeAutoProxyType(_list_exposed, 'BaseListProxy')

class ListProxy(BaseListProxy):
    # augmented assignment functions must return self
    def __iadd__(self, value):
        self._callMethod('extend', (value,))
        return self
    def __imul__(self, value):
        # Inefficient since a copy of the target is transferred and discarded
        self._callMethod('__imul__', (value,))
        return self


_dict_exposed=(
    '__cmp__', '__contains__', '__delitem__', '__getitem__',
    '__iter__', '__len__', '__setitem__', 'clear', 'copy', 'get',
    'has_key', 'items', 'iteritems', 'iterkeys', 'itervalues',
    'keys', 'pop', 'popitem', 'setdefault', 'update', 'values'
    )


class ValueProxy(BaseProxy):
    def get(self):
        return self._callMethod('get')
    def set(self, value):
        return self._callMethod('set', (value,))
    value = property(get, set)

def Array(typecode, sequence, lock=True):
    return array.array(typecode, sequence)

_arr_exposed = (
    '__len__', '__iter__', '__getitem__', '__setitem__',
    '__getslice__', '__setslice__'
    )

#
# Definition of SyncManager
#

class SyncManager(BaseManager):
    '''
    Subclass of `BaseManager` which supports a number of shared object types.
    
    The types registered are those intended for the synchronization
    of threads, plus `dict`, `list` and `Namespace`.
    
    The `processing.Manager` function creates instances of this class.
    '''
    Event = CreatorMethod(Event)
    Queue = CreatorMethod(Queue)
    Lock = CreatorMethod(Lock, AcquirerProxy)
    RLock = CreatorMethod(RLock, AcquirerProxy)
    Semaphore = CreatorMethod(Semaphore, AcquirerProxy)
    BoundedSemaphore = CreatorMethod(BoundedSemaphore, AcquirerProxy)
    Condition = CreatorMethod(Condition, ConditionProxy)
    Namespace = CreatorMethod(Namespace, NamespaceProxy)
    list = CreatorMethod(list, ListProxy, exposed=_list_exposed)
    dict = CreatorMethod(dict, exposed=_dict_exposed)
    Value = CreatorMethod(Value, ValueProxy)
    Array = CreatorMethod(Array, exposed=_arr_exposed)
