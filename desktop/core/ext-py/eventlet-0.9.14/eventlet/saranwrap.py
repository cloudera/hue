import cPickle as Pickle
import os
import struct
import sys

from eventlet.processes import Process, DeadProcess
from eventlet import pools

import warnings
warnings.warn("eventlet.saranwrap is deprecated due to underuse.  If you love "
        "it, let us know by emailing eventletdev@lists.secondlife.com",
        DeprecationWarning, stacklevel=2)

# debugging hooks
_g_debug_mode = False
if _g_debug_mode:
    import traceback
    import tempfile

def pythonpath_sync():
    """
    apply the current ``sys.path`` to the environment variable ``PYTHONPATH``,
    so that child processes have the same paths as the caller does.
    """
    pypath = os.pathsep.join(sys.path)
    os.environ['PYTHONPATH'] = pypath

def wrap(obj, dead_callback = None):
    """
    wrap in object in another process through a saranwrap proxy
    :param object: The object to wrap.
    :dead_callback: A callable to invoke if the process exits.
    """

    if type(obj).__name__ == 'module':
        return wrap_module(obj.__name__, dead_callback)
    pythonpath_sync()
    if _g_debug_mode:
        p = Process(sys.executable,
                    ["-W", "ignore", __file__, '--child',
                     '--logfile', os.path.join(tempfile.gettempdir(), 'saranwrap.log')],
                    dead_callback)
    else:
        p = Process(sys.executable, ["-W", "ignore", __file__, '--child'], dead_callback)
    prox = Proxy(ChildProcess(p, p))
    prox.obj = obj
    return prox.obj

def wrap_module(fqname, dead_callback = None):
    """
    wrap a module in another process through a saranwrap proxy

    :param fqname: The fully qualified name of the module.
    :param dead_callback: A callable to invoke if the process exits.
    """
    pythonpath_sync()
    global _g_debug_mode
    if _g_debug_mode:
        p = Process(sys.executable,
                    ["-W", "ignore", __file__, '--module', fqname,
                     '--logfile', os.path.join(tempfile.gettempdir(), 'saranwrap.log')],
                    dead_callback)
    else:
        p = Process(sys.executable,
                    ["-W", "ignore", __file__, '--module', fqname,], dead_callback)
    prox = Proxy(ChildProcess(p,p))
    return prox

def status(proxy):
    """
    get the status from the server through a proxy

    :param proxy: a :class:`eventlet.saranwrap.Proxy` object connected to a
        server.
    """
    return proxy.__local_dict['_cp'].make_request(Request('status', {}))

class BadResponse(Exception):
    """This exception is raised by an saranwrap client when it could
    parse but cannot understand the response from the server."""
    pass

class BadRequest(Exception):
    """This exception is raised by a saranwrap server when it could parse
    but cannot understand the response from the server."""
    pass

class UnrecoverableError(Exception):
    pass

class Request(object):
    "A wrapper class for proxy requests to the server."
    def __init__(self, action, param):
        self._action = action
        self._param = param
    def __str__(self):
        return "Request `"+self._action+"` "+str(self._param)
    def __getitem__(self, name):
        return self._param[name]
    def get(self, name, default = None):
        try:
            return self[name]
        except KeyError:
            return default
    def action(self):
        return self._action

def _read_lp_hunk(stream):
    len_bytes = stream.read(4)
    if len_bytes == '':
        raise EOFError("No more data to read from %s" % stream)
    length = struct.unpack('I', len_bytes)[0]
    body = stream.read(length)
    return body

def _read_response(id, attribute, input, cp):
    """local helper method to read respones from the rpc server."""
    try:
        str = _read_lp_hunk(input)
        _prnt(repr(str))
        response = Pickle.loads(str)
    except (AttributeError, DeadProcess, Pickle.UnpicklingError), e:
        raise UnrecoverableError(e)
    _prnt("response: %s" % response)
    if response[0] == 'value':
        return response[1]
    elif response[0] == 'callable':
        return CallableProxy(id, attribute, cp)
    elif response[0] == 'object':
        return ObjectProxy(cp, response[1])
    elif response[0] == 'exception':
        exp = response[1]
        raise exp
    else:
        raise BadResponse(response[0])

def _write_lp_hunk(stream, hunk):
    write_length = struct.pack('I', len(hunk))
    stream.write(write_length + hunk)
    if hasattr(stream, 'flush'):
        stream.flush()

def _write_request(param, output):
    _prnt("request: %s" % param)
    str = Pickle.dumps(param)
    _write_lp_hunk(output, str)

def _is_local(attribute):
    "Return ``True`` if the attribute should be handled locally"
#    return attribute in ('_in', '_out', '_id', '__getattribute__',
#    '__setattr__', '__dict__')
    # good enough for now. :)
    if '__local_dict' in attribute:
        return True
    return False

def _prnt(message):
    global _g_debug_mode
    if _g_debug_mode:
        print message

_g_logfile = None
def _log(message):
    global _g_logfile
    if _g_logfile:
        _g_logfile.write(str(os.getpid()) + ' ' + message + '\n')
        _g_logfile.flush()

def _unmunge_attr_name(name):
    """ Sometimes attribute names come in with classname prepended, not sure why.
    This function removes said classname, because we're huge hackers and we didn't
    find out what the true right thing to do is.  *TODO: find out. """
    if(name.startswith('_Proxy')):
        name = name[len('_Proxy'):]
    if(name.startswith('_ObjectProxy')):
        name = name[len('_ObjectProxy'):]

    return name

class ChildProcess(object):
    """
    This class wraps a remote python process, presumably available in an
    instance of a :class:`Server`.
    """
    def __init__(self, instr, outstr, dead_list = None):
        """
        :param instr: a file-like object which supports ``read()``.
        :param outstr: a file-like object which supports ``write()`` and
            ``flush()``.
        :param dead_list: a list of ids of remote objects that are dead
        """
        # default dead_list inside the function because all objects in method
        # argument lists are init-ed only once globally
        _prnt("ChildProcess::__init__")
        if dead_list is None:
            dead_list = set()
        self._dead_list = dead_list
        self._in = instr
        self._out = outstr
        self._lock = pools.TokenPool(max_size=1)

    def make_request(self, request, attribute=None):
        _id = request.get('id')

        t = self._lock.get()
        try:
            _write_request(request, self._out)
            retval = _read_response(_id, attribute, self._in, self)
        finally:
            self._lock.put(t)

        return retval

    def __del__(self):
        self._in.close()


class Proxy(object):
    """
    This is the class you will typically use as a client to a child
    process.

    Simply instantiate one around a file-like interface and start calling
    methods on the thing that is exported. The ``dir()`` builtin is not
    supported, so you have to know what has been exported.
    """
    def __init__(self, cp):
        """
        :param cp: :class:`ChildProcess` instance that wraps the i/o to the
            child process.
        """
        #_prnt("Proxy::__init__")
        self.__local_dict = dict(
            _cp = cp,
            _id = None)

    def __getattribute__(self, attribute):
        #_prnt("Proxy::__getattr__: %s" % attribute)
        if _is_local(attribute):
            # call base class getattribute so we actually get the local variable
            attribute = _unmunge_attr_name(attribute)
            return super(Proxy, self).__getattribute__(attribute)
        elif attribute in ('__deepcopy__', '__copy__'):
            # redirect copy function calls to our own versions instead of
            # to the proxied object
            return super(Proxy, self).__getattribute__('__deepcopy__')
        else:
            my_cp = self.__local_dict['_cp']
            my_id = self.__local_dict['_id']

            _dead_list = my_cp._dead_list
            for dead_object in _dead_list.copy():
                request = Request('del', {'id':dead_object})

                my_cp.make_request(request)
                try:
                    _dead_list.remove(dead_object)
                except KeyError:
                    pass

            # Pass all public attributes across to find out if it is
            # callable or a simple attribute.
            request = Request('getattr', {'id':my_id, 'attribute':attribute})
            return my_cp.make_request(request, attribute=attribute)

    def __setattr__(self, attribute, value):
        #_prnt("Proxy::__setattr__: %s" % attribute)
        if _is_local(attribute):
            # It must be local to this actual object, so we have to apply
            # it to the dict in a roundabout way
            attribute = _unmunge_attr_name(attribute)
            super(Proxy, self).__getattribute__('__dict__')[attribute]=value
        else:
            my_cp = self.__local_dict['_cp']
            my_id = self.__local_dict['_id']
            # Pass the set attribute across
            request = Request('setattr',
                              {'id':my_id, 'attribute':attribute, 'value':value})
            return my_cp.make_request(request, attribute=attribute)

class ObjectProxy(Proxy):
    """
    This class wraps a remote object in the :class:`Server`

    This class will be created during normal operation, and users should
    not need to deal with this class directly.
    """

    def __init__(self, cp, _id):
        """
        :param cp: A :class:`ChildProcess` object that wraps the i/o of a child
            process.
        :param _id: an identifier for the remote object. humans do not provide
            this.
        """
        Proxy.__init__(self, cp)
        self.__local_dict['_id'] = _id
        #_prnt("ObjectProxy::__init__ %s" % _id)

    def __del__(self):
        my_id = self.__local_dict['_id']
        #_prnt("ObjectProxy::__del__ %s" % my_id)
        self.__local_dict['_cp']._dead_list.add(my_id)

    def __getitem__(self, key):
        my_cp = self.__local_dict['_cp']
        my_id = self.__local_dict['_id']
        request = Request('getitem', {'id':my_id, 'key':key})
        return my_cp.make_request(request, attribute=key)

    def __setitem__(self, key, value):
        my_cp = self.__local_dict['_cp']
        my_id = self.__local_dict['_id']
        request = Request('setitem', {'id':my_id, 'key':key, 'value':value})
        return my_cp.make_request(request, attribute=key)

    def __eq__(self, rhs):
        my_cp = self.__local_dict['_cp']
        my_id = self.__local_dict['_id']
        request = Request('eq', {'id':my_id, 'rhs':rhs.__local_dict['_id']})
        return my_cp.make_request(request)

    def __repr__(self):
        # apparently repr(obj) skips the whole getattribute thing and just calls __repr__
        # directly.  Therefore we just pass it through the normal call pipeline, and
        # tack on a little header so that you can tell it's an object proxy.
        val =  self.__repr__()
        return "saran:%s" % val

    def __str__(self):
        # see description for __repr__, because str(obj) works the same.  We don't
        # tack anything on to the return value here because str values are used as data.
        return self.__str__()

    def __nonzero__(self):
        # bool(obj) is another method that skips __getattribute__.
        # There's no good way to just pass
        # the method on, so we use a special message.
        my_cp = self.__local_dict['_cp']
        my_id = self.__local_dict['_id']
        request = Request('nonzero', {'id':my_id})
        return my_cp.make_request(request)

    def __len__(self):
        # see description for __repr__, len(obj) is the same.
        return self.__len__()

    def __contains__(self, item):
        # another special name that is normally called without recours to __getattribute__
        return self.__contains__(item)

    def __deepcopy__(self, memo=None):
        """Copies the entire external object and returns its
        value. Will only work if the remote object is pickleable."""
        my_cp = self.__local_dict['_cp']
        my_id = self.__local_dict['_id']
        request = Request('copy', {'id':my_id})
        return my_cp.make_request(request)

    # since the remote object is being serialized whole anyway,
    # there's no semantic difference between copy and deepcopy
    __copy__ = __deepcopy__


def proxied_type(self):
    """ Returns the type of the object in the child process.

    Calling type(obj) on a saranwrapped object will always return
    <class saranwrap.ObjectProxy>, so this is a way to get at the
    'real' type value."""
    if type(self) is not ObjectProxy:
        return type(self)

    my_cp = self.__local_dict['_cp']
    my_id = self.__local_dict['_id']
    request = Request('type', {'id':my_id})
    return my_cp.make_request(request)


def getpid(self):
    """ Returns the pid of the child process.  The argument should be
    a saranwrapped object."""
    my_cp = self.__local_dict['_cp']
    return my_cp._in.getpid()


class CallableProxy(object):
    """
    This class wraps a remote function in the :class:`Server`

    This class will be created by an :class:`Proxy` during normal operation,
    and users should not need to deal with this class directly.
    """

    def __init__(self, object_id, name, cp):
        #_prnt("CallableProxy::__init__: %s, %s" % (object_id, name))
        self._object_id = object_id
        self._name = name
        self._cp = cp

    def __call__(self, *args, **kwargs):
        #_prnt("CallableProxy::__call__: %s, %s" % (args, kwargs))

        # Pass the call across. We never build a callable without
        # having already checked if the method starts with '_' so we
        # can safely pass this one to the remote object.
        #_prnt("calling %s %s" % (self._object_id, self._name)
        request = Request('call', {'id':self._object_id,
                                   'name':self._name,
                                   'args':args, 'kwargs':kwargs})
        return self._cp.make_request(request, attribute=self._name)

class Server(object):
    def __init__(self, input, output, export):
        """
        :param input: a file-like object which supports ``read()``.
        :param output: a file-like object which supports ``write()`` and
            ``flush()``.
        :param export: an object, function, or map which is exported to clients
            when the id is ``None``.
        """
        #_log("Server::__init__")
        self._in = input
        self._out = output
        self._export = export
        self._next_id = 1
        self._objects = {}

    def handle_status(self, obj, req):
        return {
            'object_count':len(self._objects),
            'next_id':self._next_id,
            'pid':os.getpid()}

    def handle_getattr(self, obj, req):
        try:
            return getattr(obj, req['attribute'])
        except AttributeError, e:
            if hasattr(obj, "__getitem__"):
                return obj[req['attribute']]
            else:
                raise e
        #_log('getattr: %s' % str(response))

    def handle_setattr(self, obj, req):
        try:
            return setattr(obj, req['attribute'], req['value'])
        except AttributeError, e:
            if hasattr(obj, "__setitem__"):
                return obj.__setitem__(req['attribute'], req['value'])
            else:
                raise e

    def handle_getitem(self, obj, req):
        return obj[req['key']]

    def handle_setitem(self, obj, req):
        obj[req['key']] = req['value']
        return None  # *TODO figure out what the actual return value
                     # of __setitem__ should be

    def handle_eq(self, obj, req):
        #_log("__eq__ %s %s" % (obj, req))
        rhs = None
        try:
            rhs = self._objects[req['rhs']]
        except KeyError:
            return False
        return (obj == rhs)

    def handle_call(self, obj, req):
        #_log("calling %s " % (req['name']))
        try:
            fn = getattr(obj, req['name'])
        except AttributeError, e:
            if hasattr(obj, "__setitem__"):
                fn = obj[req['name']]
            else:
                raise e

        return fn(*req['args'],**req['kwargs'])

    def handle_del(self, obj, req):
        id = req['id']
        _log("del %s from %s" % (id, self._objects))

        # *TODO what does __del__ actually return?
        try:
            del self._objects[id]
        except KeyError:
            pass

        return None

    def handle_type(self, obj, req):
        return type(obj)

    def handle_nonzero(self, obj, req):
        return bool(obj)

    def handle_copy(self, obj, req):
        return obj

    def loop(self):
        """Loop forever and respond to all requests."""
        _log("Server::loop")
        while True:
            try:
                try:
                    str_ = _read_lp_hunk(self._in)
                except EOFError:
                    if _g_debug_mode:
                        _log("Exiting normally")
                    sys.exit(0)

                request = Pickle.loads(str_)
                _log("request: %s (%s)" % (request, self._objects))
                req = request
                id = None
                obj = None
                try:
                    id = req['id']
                    if id:
                        id = int(id)
                        obj = self._objects[id]
                    #_log("id, object: %d %s" % (id, obj))
                except Exception, e:
                    #_log("Exception %s" % str(e))
                    pass
                if obj is None or id is None:
                    id = None
                    obj = self._export()
                    #_log("found object %s" % str(obj))

                # Handle the request via a method with a special name on the server
                handler_name = 'handle_%s' % request.action()

                try:
                    handler = getattr(self, handler_name)
                except AttributeError:
                    raise BadRequest, request.action()

                response = handler(obj, request)

                # figure out what to do with the response, and respond
                # apprpriately.
                if request.action() in ['status', 'type', 'copy']:
                    # have to handle these specially since we want to
                    # pickle up the actual value and not return a proxy
                    self.respond(['value', response])
                elif callable(response):
                    #_log("callable %s" % response)
                    self.respond(['callable'])
                elif self.is_value(response):
                    self.respond(['value', response])
                else:
                    self._objects[self._next_id] = response
                    #_log("objects: %s" % str(self._objects))
                    self.respond(['object', self._next_id])
                    self._next_id += 1
            except (KeyboardInterrupt, SystemExit), e:
                raise e
            except Exception, e:
                self.write_exception(e)

    def is_value(self, value):
        """
        Test if *value* should be serialized as a simple dataset.

        :param value: The value to test.
        :return: Returns ``True`` if *value* is a simple serializeable set of
            data.
        """
        return type(value) in (str,unicode,int,float,long,bool,type(None))

    def respond(self, body):
        _log("responding with: %s" % body)
        #_log("objects: %s" % self._objects)
        s = Pickle.dumps(body)
        _log(repr(s))
        _write_lp_hunk(self._out, s)

    def write_exception(self, e):
        """Helper method to respond with an exception."""
        #_log("exception: %s" % sys.exc_info()[0])
        # TODO: serialize traceback using generalization of code from mulib.htmlexception

        global _g_debug_mode
        if _g_debug_mode:
            _log("traceback: %s" % traceback.format_tb(sys.exc_info()[2]))

        self.respond(['exception', e])


# test function used for testing return of unpicklable exceptions
def raise_an_unpicklable_error():
    class Unpicklable(Exception):
        pass
    raise Unpicklable()

# test function used for testing return of picklable exceptions
def raise_standard_error():
    raise FloatingPointError()

# test function to make sure print doesn't break the wrapper
def print_string(str):
    print str

# test function to make sure printing on stdout doesn't break the
# wrapper
def err_string(str):
    print >>sys.stderr, str

def named(name):
    """Return an object given its name.

    The name uses a module-like syntax, eg::

      os.path.join

    or::

      mulib.mu.Resource
    """
    toimport = name
    obj = None
    import_err_strings = []
    while toimport:
        try:
            obj = __import__(toimport)
            break
        except ImportError, err:
            # print 'Import error on %s: %s' % (toimport, err)  # debugging spam
            import_err_strings.append(err.__str__())
            toimport = '.'.join(toimport.split('.')[:-1])
    if obj is None:
        raise ImportError(
            '%s could not be imported.  Import errors: %r' % (name, import_err_strings))
    for seg in name.split('.')[1:]:
        try:
            obj = getattr(obj, seg)
        except AttributeError:
            dirobj = dir(obj)
            dirobj.sort()
            raise AttributeError(
                'attribute %r missing from %r (%r) %r.  Import errors: %r' % (
                seg, obj, dirobj, name, import_err_strings))
    return obj


def main():
    import optparse
    parser = optparse.OptionParser(
        usage="usage: %prog [options]",
        description="Simple saranwrap.Server wrapper")
    parser.add_option(
        '-c', '--child', default=False, action='store_true',
        help='Wrap an object serialized via setattr.')
    parser.add_option(
        '-m', '--module', type='string', dest='module', default=None,
        help='a module to load and export.')
    parser.add_option(
        '-l', '--logfile', type='string', dest='logfile', default=None,
        help='file to log to.')
    options, args = parser.parse_args()
    global _g_logfile
    if options.logfile:
        _g_logfile = open(options.logfile, 'a')

    from eventlet import tpool
    base_obj = [None]
    if options.module:
        def get_module():
            if base_obj[0] is None:
                base_obj[0] = named(options.module)
            return base_obj[0]
        server = Server(tpool.Proxy(sys.stdin),
                        tpool.Proxy(sys.stdout),
                        get_module)
    elif options.child:
        def get_base():
            if base_obj[0] is None:
                base_obj[0] = {}
            return base_obj[0]
        server = Server(tpool.Proxy(sys.stdin),
                        tpool.Proxy(sys.stdout),
                        get_base)

    # *HACK: some modules may emit on stderr, which breaks everything.
    class NullSTDOut(object):
        def noop(*args):
            pass
        def log_write(self, message):
            self.message = getattr(self, 'message', '') + message
            if '\n' in message:
                _log(self.message.rstrip())
                self.message = ''
        write = noop
        read = noop
        flush = noop

    sys.stderr = NullSTDOut()
    sys.stdout = NullSTDOut()
    if _g_debug_mode:
        sys.stdout.write = sys.stdout.log_write
        sys.stderr.write = sys.stderr.log_write

    # Loop until EOF
    server.loop()
    if _g_logfile:
        _g_logfile.close()


if __name__ == "__main__":
    main()
