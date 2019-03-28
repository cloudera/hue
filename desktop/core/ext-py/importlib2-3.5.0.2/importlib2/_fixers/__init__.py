from contextlib import contextmanager
import imp
import os
import sys
import types


def import_safe(name, alternative, _import=__import__):
    try:
        return sys.modules[name]
    except KeyError:
        try:
            return sys.modules[alternative]
        except KeyError:
            try:
                return _import(name)
            except ImportError:
                try:
                    return _import(alternative)
                except ImportError:
                    return None


builtins = import_safe('builtins', '__builtin__')
_imp = import_safe('_imp', 'imp')
_thread = import_safe('_thread', 'thread')  # Will be None if no threading.


@contextmanager
def swap(obj, attr, value, pop=True, detect=False):
    getter = getattr
    setter = setattr
    exctype = AttributeError
    if detect and hasattr(obj, 'items'):
        cls = type(obj)
        try:
            getter = cls.__getitem__
            setter = cls.__setitem__
        except AttributeError:
            getter = getattr
        else:
            exctype = KeyError
    try:
        original = getter(obj, attr)
    except exctype:
        original = None
        restore = False
    else:
        restore = True
    setter(obj, attr, value)
    try:
        yield original if pop else value
    finally:
        if restore:
            setter(obj, attr, original)


@contextmanager
def ns_injected(nsitems):
    injected = []
    for ns, name, value in nsitems:
        if name not in ns:
            ns[name] = value
            injected.append((ns, name))
    try:
        yield
    finally:
        for ns, name in injected:
            del ns[name]


#################################################
# custom implementations

def _w_long(x):
    """Convert a 32-bit integer to little-endian."""
    x = int(x)
    int_bytes = []
    int_bytes.append(x & 0xFF)
    int_bytes.append((x >> 8) & 0xFF)
    int_bytes.append((x >> 16) & 0xFF)
    int_bytes.append((x >> 24) & 0xFF)
    return bytearray(int_bytes)


def _r_long(int_bytes):
    """Convert 4 bytes in little-endian to an integer."""
    try:
        x = ord(int_bytes[0])
    except TypeError:
        x = int_bytes[0]
        x |= int_bytes[1] << 8
        x |= int_bytes[2] << 16
        x |= int_bytes[3] << 24
    else:
        x |= ord(int_bytes[1]) << 8
        x |= ord(int_bytes[2]) << 16
        x |= ord(int_bytes[3]) << 24
    return x


try:
    SimpleNamespace = types.SimpleNamespace
except AttributeError:
    class SimpleNamespace(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format(type(self).__name__, ", ".join(items))
        def __eq__(self, other):
            return self.__dict__ == other.__dict__
        def __ne__(self, other):
            return not(self == other)

try:
    _new_class = types.new_class
except AttributeError:
    def new_class(name, bases=(), kwds=None, exec_body=None):
        name = str(name)
        if kwds and 'metaclass' in kwds:
            meta = kwds['metaclass']
        else:
            meta = type
        ns = {}
        if exec_body is not None:
            exec_body(ns)
        return meta(name, bases, ns)
else:
    def new_class(name, bases=(), kwds=None, exec_body=None):
        name = str(name)
        return _new_class(name, bases, kwds, exec_body)


try:
    extension_suffixes = _imp.extension_suffixes
except AttributeError:
    _ext_suffixes = None
    def extension_suffixes():
        global _ext_suffixes
        if _ext_suffixes is None:
            _ext_suffixes = get_ext_suffixes(imp)
        return _ext_suffixes


try:
    _fix_co_filename = imp._fix_co_filename
except AttributeError:
    def _fix_co_filename(code, filename):
        # Finish this.
        pass


try:
    is_frozen_package = imp.is_frozen_package
except AttributeError:
    def is_frozen_package(name):
        # XXX Finish this?  Were frozen packages always allowed?
        return False


# For _os.
def replace(src, dst):
    # This is better than leaving nothing.
    if os.path.exists(dst):
        os.remove(dst)
    os.rename(src, dst)


#################################################
# data external to importlib

PY3 = (sys.hexversion > 0x03000000)

# Based on six.exec_().
if PY3:
    exec_ = getattr(builtins, 'exec')
else:
    def exec_(_code_, _globs_, _locs_=None):
        """Execute code in a namespace."""
        if _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")


def get_magic():
    try:
        return sys.implementation._pyc_magic_number
    except AttributeError:
        # XXX Try bootstrap.MAGIC_NUMBER first?
        magic_bytes = imp.get_magic()
        return _r_long(magic_bytes)


def get_ext_suffixes(imp):
    return [s for s, _, t in imp.get_suffixes() if t == imp.C_EXTENSION]


def make_impl(name=None, version=None, cache_tag=None):
    hexversion = None
    if name is None:
        import platform
        name = platform.python_implementation().lower()
    if version is None:
        version = sys.version_info
        hexversion = getattr(sys, 'hexversion', None)
    major, minor, micro, releaselevel, serial = version
    if hexversion is None:
        assert releaselevel in ('alpha', 'beta', 'candidate', 'final')
        assert serial < 10
        hexversion = '0x{:x}{:>02x}{:>02x}{}{}'.format(major, minor, micro,
                                                       releaselevel[0], serial)
        hexversion = int(hexversion, 16)
    if cache_tag is None:
        #cache_tag = '{}-{}{}'.format(name, major, minor)
        cache_tag = '{}-{}{}-importlib2'.format(name, major, minor)

    impl = SimpleNamespace()
    impl.name = name
    impl.version = version
    impl.hexversion = hexversion
    impl.cache_tag = cache_tag
    return impl


#################################################
# only for importlib

def kwonly(names):
    # decorator factory to replace the kw-only syntax
    if isinstance(names, str):
        names = names.replace(',', ' ').split()
    def decorator(f):
        # XXX Return a wrapper that enforces kw-only.
        return f
    return decorator


# Destructive but idempotent.
def inject_importlib(name, _target='importlib2'):
    # for importlib2 and its submodules
    mod = sys.modules[name]

    if name != _target:
        if not name.startswith(_target+'.'):
            return
        importlib = sys.modules.get('importlib')
        if importlib and importlib.__name__ != _target:
            # Only clobber if importlib got clobbered.
            return
    else:
        importlib = mod

    # XXX Copy into existing namespace instead of replacing?
    newname = name.replace('importlib2', 'importlib')
    sys.modules[newname] = mod

    # Keep a reference to _bootstrap so it doesn't get garbage collected.
    if not hasattr(mod, '_bootstrap'):
        mod._boostrap = sys.modules['importlib2']._bootstrap


#################################################
# for importlib2.__init__()

# XXX Move all this to _fixers._bootstrap?

def _bootstrap_fix_unicode(bootstrap):
    # Make str checks more lenient.
    try:
        basestring
    except NameError:
        pass
    else:
        bootstrap.str = basestring


def _bootstrap_customize(bootstrap):
    # Replace bootstrap implementations.
    bootstrap._w_long = _w_long
    bootstrap._r_long = _r_long
    bootstrap.MAGIC_NUMBER = _w_long(get_magic())


def _bootstrap_fix_module_type(bootstrap):
    from ._modules import get_moduletype
    ModuleType = get_moduletype(bootstrap)
    bootstrap._new_module = ModuleType


def _bootstrap_fix_os(bootstrap):
    # XXX Use a ModuleProxy.
    try:
        _os = sys.modules['posix']
    except KeyError:
        try:
            _os = sys.modules['nt']
        except KeyError:
            raise _ImportError('importlib requires posix or nt')
    _os.replace = replace
    return _os


def _bootstrap_fix_sys(bootstrap, sys):
    if getattr(sys, 'implementation', None) is None:
        sys.implementation = make_impl()
    sys.implementation._pyc_magic_number = get_magic()
    return sys


def _bootstrap_fix_imp(bootstrap, _imp):
    # XXX Use a ModuleProxy.

    if not hasattr(_imp, 'extension_suffixes'):
        _imp.extension_suffixes = extension_suffixes
    if not hasattr(_imp, '_fix_co_filename'):
        _imp._fix_co_filename = _fix_co_filename
    if not hasattr(_imp, 'is_frozen_package'):
        _imp.is_frozen_package = is_frozen_package

    return _imp


def _bootstrap_dependencies(bootstrap):
    # Ensure modules needed by _bootstrap._setup() are ready to go.
    # We temporarily inject builtins in the _setup() wrapper, if needed.
    # We temporarily inject _thread in the _setup() wrapper, if needed.
    # We temporarily inject _os fixes in the _setup() wrapper, if needed.
    # We skip _winreg.
    import _io, _warnings, marshal, _weakref

    _os = _bootstrap_fix_os(bootstrap)

    inject = [(sys.modules, 'builtins', builtins),
              (sys.modules, '_thread', _thread),
              (sys.modules, os.name, _os),
              ]
    return inject


def _bootstrap_wrap_setup(bootstrap, inject=()):
    setup = bootstrap._setup
    def _setup(sys_module, _imp_module):
        sys_module = _bootstrap_fix_sys(bootstrap, sys_module)
        _imp_module = _bootstrap_fix_imp(bootstrap, _imp_module)
        with ns_injected(inject):
            setup(sys_module, _imp_module)
    return _setup


def fix_bootstrap(bootstrap):
    _bootstrap_fix_unicode(bootstrap)
    _bootstrap_customize(bootstrap)
    _bootstrap_fix_module_type(bootstrap)

    # Do remaining fixes in _setup().
    inject = _bootstrap_dependencies(bootstrap)
    bootstrap._setup = _bootstrap_wrap_setup(bootstrap, inject)


def fix_importlib(ns):
    if not getattr(imp, '_testing_importlib2', None):
        # Remove deprecated APIs.
        name = ns['__name__']
        if name == 'importlib2':
            del ns['find_loader']
        elif name == 'importlib2.abc':
            del ns['Finder'].find_module
            del ns['MetaPathFinder'].find_module
            del ns['PathEntryFinder'].find_loader
            del ns['PathEntryFinder'].find_module
            del ns['Loader'].load_module
            del ns['Loader'].module_repr
            del ns['InspectLoader'].load_module
        elif name == 'importlib2.machinery':
            del ns['BuiltinImporter'].find_module
            #del ns['BuiltinImporter'].load_module
            del ns['BuiltinImporter'].module_repr
            del ns['FrozenImporter'].find_module
            del ns['FrozenImporter'].load_module
            del ns['FrozenImporter'].module_repr
            del ns['WindowsRegistryFinder'].find_module
            del ns['_LoaderBasics'].load_module
            del ns['FileLoader'].load_module
            #del ns['ExtensionFileLoader'].load_module
            del ns['_NamespaceLoader'].load_module
            del ns['_NamespaceLoader'].module_repr
            del ns['PathFinder'].find_module
            del ns['FileFinder'].find_loader
            del ns['FileFinder'].find_module
        elif name == 'importlib2.util':
            del ns['set_package']
            del ns['set_loader']
            del ns['module_for_loader']
