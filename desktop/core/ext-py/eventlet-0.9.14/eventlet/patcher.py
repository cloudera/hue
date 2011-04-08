import sys
import imp

__all__ = ['inject', 'import_patched', 'monkey_patch', 'is_monkey_patched']

__exclude = set(('__builtins__', '__file__', '__name__'))

class SysModulesSaver(object):
    """Class that captures some subset of the current state of
    sys.modules.  Pass in an iterator of module names to the
    constructor."""
    def __init__(self, module_names=()):
        self._saved = {}
        imp.acquire_lock()
        self.save(*module_names)

    def save(self, *module_names):
        """Saves the named modules to the object."""
        for modname in module_names:
            self._saved[modname] = sys.modules.get(modname, None)

    def restore(self):
        """Restores the modules that the saver knows about into
        sys.modules.
        """
        try:
            for modname, mod in self._saved.iteritems():
                if mod is not None:
                    sys.modules[modname] = mod
                else:
                    try:
                        del sys.modules[modname]
                    except KeyError:
                        pass
        finally:
            imp.release_lock()
                

def inject(module_name, new_globals, *additional_modules):
    """Base method for "injecting" greened modules into an imported module.  It
    imports the module specified in *module_name*, arranging things so
    that the already-imported modules in *additional_modules* are used when
    *module_name* makes its imports.

    *new_globals* is either None or a globals dictionary that gets populated
    with the contents of the *module_name* module.  This is useful when creating
    a "green" version of some other module.

    *additional_modules* should be a collection of two-element tuples, of the
    form (<name>, <module>).  If it's not specified, a default selection of
    name/module pairs is used, which should cover all use cases but may be
    slower because there are inevitably redundant or unnecessary imports.
    """
    patched_name = '__patched_module_' + module_name
    if patched_name in sys.modules:
        # returning already-patched module so as not to destroy existing
        # references to patched modules
        return sys.modules[patched_name]

    if not additional_modules:
        # supply some defaults
        additional_modules = (
            _green_os_modules() +
            _green_select_modules() +
            _green_socket_modules() +
            _green_thread_modules() +
            _green_time_modules()) 
            #_green_MySQLdb()) # enable this after a short baking-in period
    
    # after this we are gonna screw with sys.modules, so capture the
    # state of all the modules we're going to mess with, and lock
    saver = SysModulesSaver([name for name, m in additional_modules])
    saver.save(module_name)

    # Cover the target modules so that when you import the module it
    # sees only the patched versions
    for name, mod in additional_modules:
        sys.modules[name] = mod

    ## Remove the old module from sys.modules and reimport it while
    ## the specified modules are in place
    sys.modules.pop(module_name, None)
    try:
        module = __import__(module_name, {}, {}, module_name.split('.')[:-1])

        if new_globals is not None:
            ## Update the given globals dictionary with everything from this new module
            for name in dir(module):
                if name not in __exclude:
                    new_globals[name] = getattr(module, name)

        ## Keep a reference to the new module to prevent it from dying
        sys.modules[patched_name] = module
    finally:
        saver.restore()  ## Put the original modules back

    return module


def import_patched(module_name, *additional_modules, **kw_additional_modules):
    """Imports a module in a way that ensures that the module uses "green"
    versions of the standard library modules, so that everything works
    nonblockingly.

    The only required argument is the name of the module to be imported.
    """
    return inject(
        module_name,
        None,
        *additional_modules + tuple(kw_additional_modules.items()))


def patch_function(func, *additional_modules):
    """Decorator that returns a version of the function that patches
    some modules for the duration of the function call.  This is
    deeply gross and should only be used for functions that import
    network libraries within their function bodies that there is no
    way of getting around."""
    if not additional_modules:
        # supply some defaults
        additional_modules = (
            _green_os_modules() +
            _green_select_modules() +
            _green_socket_modules() +
            _green_thread_modules() + 
            _green_time_modules())

    def patched(*args, **kw):
        saver = SysModulesSaver()
        for name, mod in additional_modules:
            saver.save(name)
            sys.modules[name] = mod
        try:
            return func(*args, **kw)
        finally:
            saver.restore()
    return patched

def _original_patch_function(func, *module_names):
    """Kind of the contrapositive of patch_function: decorates a
    function such that when it's called, sys.modules is populated only
    with the unpatched versions of the specified modules.  Unlike
    patch_function, only the names of the modules need be supplied,
    and there are no defaults.  This is a gross hack; tell your kids not
    to import inside function bodies!"""
    def patched(*args, **kw):
        saver = SysModulesSaver(module_names)
        for name in module_names:
            sys.modules[name] = original(name)
        try:
            return func(*args, **kw)
        finally:
            saver.restore()
    return patched


def original(modname):
    """ This returns an unpatched version of a module; this is useful for 
    Eventlet itself (i.e. tpool)."""
    # note that it's not necessary to temporarily install unpatched
    # versions of all patchable modules during the import of the
    # module; this is because none of them import each other, except
    # for threading which imports thread
    original_name = '__original_module_' + modname
    if original_name in sys.modules:
        return sys.modules.get(original_name)

    # re-import the "pure" module and store it in the global _originals
    # dict; be sure to restore whatever module had that name already
    saver = SysModulesSaver((modname,))
    sys.modules.pop(modname, None)
    # some rudimentary dependency checking -- fortunately the modules
    # we're working on don't have many dependencies so we can just do
    # some special-casing here
    deps = {'threading':'thread', 'Queue':'threading'}
    if modname in deps:
        dependency = deps[modname]
        saver.save(dependency)
        sys.modules[dependency] = original(dependency)
    try:
        real_mod = __import__(modname, {}, {}, modname.split('.')[:-1])
        if modname == 'Queue' and not hasattr(real_mod, '_threading'):
            # tricky hack: Queue's constructor in <2.7 imports
            # threading on every instantiation; therefore we wrap
            # it so that it always gets the original threading
            real_mod.Queue.__init__ = _original_patch_function(
                real_mod.Queue.__init__, 
                'threading')
        # save a reference to the unpatched module so it doesn't get lost
        sys.modules[original_name] = real_mod
    finally:
        saver.restore()

    return sys.modules[original_name]

already_patched = {}
def monkey_patch(**on):
    """Globally patches certain system modules to be greenthread-friendly.

    The keyword arguments afford some control over which modules are patched.
    If no keyword arguments are supplied, all possible modules are patched.
    If keywords are set to True, only the specified modules are patched.  E.g.,
    ``monkey_patch(socket=True, select=True)`` patches only the select and 
    socket modules.  Most arguments patch the single module of the same name 
    (os, time, select).  The exceptions are socket, which also patches the ssl 
    module if present; and thread, which patches thread, threading, and Queue.

    It's safe to call monkey_patch multiple times.
    """    
    accepted_args = set(('os', 'select', 'socket', 
                         'thread', 'time', 'psycopg', 'MySQLdb'))
    default_on = on.pop("all",None)
    for k in on.iterkeys():
        if k not in accepted_args:
            raise TypeError("monkey_patch() got an unexpected "\
                                "keyword argument %r" % k)
    if default_on is None:
        default_on = not (True in on.values())
    for modname in accepted_args:
        if modname == 'MySQLdb':
            # MySQLdb is only on when explicitly patched for the moment
            on.setdefault(modname, False)
        on.setdefault(modname, default_on)
        
    modules_to_patch = []
    patched_thread = False
    if on['os'] and not already_patched.get('os'):
        modules_to_patch += _green_os_modules()
        already_patched['os'] = True
    if on['select'] and not already_patched.get('select'):
        modules_to_patch += _green_select_modules()
        already_patched['select'] = True
    if on['socket'] and not already_patched.get('socket'):
        modules_to_patch += _green_socket_modules()
        already_patched['socket'] = True
    if on['thread'] and not already_patched.get('thread'):
        patched_thread = True
        modules_to_patch += _green_thread_modules()
        already_patched['thread'] = True
    if on['time'] and not already_patched.get('time'):
        modules_to_patch += _green_time_modules()
        already_patched['time'] = True
    if on.get('MySQLdb') and not already_patched.get('MySQLdb'):
        modules_to_patch += _green_MySQLdb()
        already_patched['MySQLdb'] = True
    if on['psycopg'] and not already_patched.get('psycopg'):
        try:
            from eventlet.support import psycopg2_patcher
            psycopg2_patcher.make_psycopg_green()
            already_patched['psycopg'] = True
        except ImportError:
            # note that if we get an importerror from trying to
            # monkeypatch psycopg, we will continually retry it
            # whenever monkey_patch is called; this should not be a
            # performance problem but it allows is_monkey_patched to
            # tell us whether or not we succeeded
            pass

    imp.acquire_lock()
    try:
        for name, mod in modules_to_patch:
            orig_mod = sys.modules.get(name)
            if orig_mod is None:
                orig_mod = __import__(name)
            for attr_name in mod.__patched__:
                patched_attr = getattr(mod, attr_name, None)
                if patched_attr is not None:
                    setattr(orig_mod, attr_name, patched_attr)

        # hacks ahead; this is necessary to prevent a KeyError on program exit
        if patched_thread:
            _patch_main_thread(sys.modules['threading'])
    finally:
        imp.release_lock()

def _patch_main_thread(mod):
    """This is some gnarly patching specific to the threading module;
    threading will always be initialized prior to monkeypatching, and
    its _active dict will have the wrong key (it uses the real thread
    id but once it's patched it will use the greenlet ids); so what we
    do is rekey the _active dict so that the main thread's entry uses
    the greenthread key.  Other threads' keys are ignored."""
    thread = original('thread')
    curthread = mod._active.pop(thread.get_ident(), None)
    if curthread:
        import eventlet.green.thread
        mod._active[eventlet.green.thread.get_ident()] = curthread


def is_monkey_patched(module):
    """Returns True if the given module is monkeypatched currently, False if
    not.  *module* can be either the module itself or its name.

    Based entirely off the name of the module, so if you import a
    module some other way than with the import keyword (including
    import_patched), this might not be correct about that particular
    module."""
    return module in already_patched or \
           getattr(module, '__name__', None) in already_patched

def _green_os_modules():
    from eventlet.green import os
    return [('os', os)]

def _green_select_modules():
    from eventlet.green import select
    return [('select', select)]

def _green_socket_modules():
    from eventlet.green import socket
    try:
        from eventlet.green import ssl
        return [('socket', socket), ('ssl', ssl)]
    except ImportError:
        return [('socket', socket)]

def _green_thread_modules():
    from eventlet.green import Queue
    from eventlet.green import thread
    from eventlet.green import threading
    return [('Queue', Queue), ('thread', thread), ('threading', threading)]

def _green_time_modules():
    from eventlet.green import time
    return [('time', time)]

def _green_MySQLdb():
    try:
        from eventlet.green import MySQLdb
        return [('MySQLdb', MySQLdb)]
    except ImportError:
        return []


if __name__ == "__main__":
    import sys
    sys.argv.pop(0)
    monkey_patch()
    execfile(sys.argv[0])
