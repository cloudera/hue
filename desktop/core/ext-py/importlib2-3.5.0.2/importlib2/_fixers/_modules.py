import gc
import inspect
import sys
import types

from . import builtins


MODULE_TYPE = type(sys)


class _ModuleTypeMeta(type(MODULE_TYPE)):
    # Metaclass needed since we can't set __class__ on modules.
    def __instancecheck__(cls, obj):
        if super(_ModuleTypeMeta, cls).__instancecheck__(obj):
            return True
        return isinstance(obj, MODULE_TYPE)


class _ModuleType(MODULE_TYPE):
    def __init__(self, name):
        name = str(name)  # Coerce for 2.7.
        super(_ModuleType, self).__init__(name)
        self.__spec__ = None
        self.__loader__ = None
    # Add a __repr__ using bootstrap._module_repr().


# destructive but idempotent
def get_moduletype(bootstrap=None):
    if bootstrap is None:
        bootstrap = sys.modules['importlib2._bootstrap']

    ModuleType = getattr(bootstrap, 'ModuleType', None)
    if ModuleType is not None:
        # Already changed!
        return ModuleType

    def __repr__(self):
        return bootstrap._module_repr(self)

    # Build a custom module type.
    #_ModuleTypeMeta = type(MODULE_TYPE)
    ModuleType = _ModuleTypeMeta('ModuleType',
                                 (_ModuleType,),
                                 {'__repr__': bootstrap._module_repr})
    ModuleType.__module__ = bootstrap.__name__
    bootstrap.ModuleType = ModuleType
    return ModuleType


# destructive but idempotent
def inject_moduletype():
    import importlib2._bootstrap
    types.ModuleType = importlib2._bootstrap.ModuleType

    for name, module in sys.modules.items():
        # XXX How to get better __repr__?
        # Can't set __class__.
        #if module.__class__ is MODULE_TYPE:
        #    module.__class__ = types.ModuleType
        if module is None:
            # This entry will be removed later (in _importstate.fix_modules()).
            continue
        if not hasattr(module, '__spec__'):
            module.__spec__ = None
        if not hasattr(module, '__loader__'):
            module.__loader__ = None


#################################################
# attr lookup helpers

def type_lookup(obj, name):
    # See _PyType_Lookup from Objects/typeobject.c.
    # By itself, inspect.getattr_static() (3.2+) isn't enough because we
    # only want to look at the MRO, not the object and not the metaclasses.
    # XXX Cache values for each new lookup tree?
    cls = type(obj)

    # Handle known types.
    if cls is type or cls is object:
        # XXX Do this for all builtin types?
        try:
            return type.__dict__[name]
        except KeyError:
            raise AttributeError(name)

    # Otherwise extract the raw value.
    for base in cls.__mro__:
        # ns = base->tp_dict;
        descr = type.__dict__['__dict__']
        ns = descr.__get__(base, type)
        if name in ns:
            return ns[name]
    else:
        raise AttributeError(name)


def resolve_from_type(obj, name):
    raw = type_lookup(obj, name)

    # Resolve any descriptors.
    if (inspect.ismethoddescriptor(raw) or
        inspect.isgetsetdescriptor(raw) or
        inspect.ismemberdescriptor(raw)):
        getter = raw.__get__
    else:
        try:
            getter = resolve_from_type(raw, '__get__')
        except AttributeError:
            # Not a descriptor.
            return raw
    return getter(obj, type(obj))


def is_special(name, obj=None):
    # XXX Check against explicit lists (attrs, methods)
    #  (https://docs.python.org/3.5)
    # generic:
    #  /reference/datamodel.html#special-method-names
    #  /library/unittest.mock.html?highlight=__sizeof__#magic-mock
    # type-specific (make use of obj?):
    #  /library/inspect.html#types-and-members
    #  /library/types.html
    #  /library/stdtypes.html#dict ("d[key]")
    #  /library/pickle.html#pickling-class-instances
    #  /library/copy.html (__copy__ and __deepcopy__)

    return name.startswith('__') and name.endswith('__')


def get_special_attr(obj, name):
    # This is a best effort.
    # See _PyObject_LookupSpecial from Objects/typeobject.c.
    if not is_special(name, obj):
        raise AttributeError('not a special attribute: {!r}'.format(name))

    return resolve_from_type(obj, name)


def has_special_attr(obj, name):
    try:
        get_special_attr(obj, name)
    except AttributeError:
        if not is_special(name, obj):
            raise
        return False
    else:
        return True


def get_container_type(obj):
    # XXX Return the types from collections.abc?
    if not has_special_attr(obj, '__contains__'):
        return None
    # XXX Skip the __iter__ check?
    if not has_special_attr(obj, '__iter__'):
        raise NotImplementedError
    # XXX Also require __len__?

    if not has_special_attr(obj, '__getitem__'):
        return 'set'
    # XXX Is there a better way to distinguish mapping from sequence?
    try:
        type_lookup(obj, 'items')
    except AttributeError:
        return 'sequence'
    else:
        return 'mapping'


def iter_where_bound(obj, ignoreframes=True):
    # return (referrer, binding, kind) where kind in (attr, key, index, element)
    # Only use "is" test for containment.
    if obj in builtins.__dict__.values():
        raise RuntimeError('not what you wanted')

    for referrer in gc.get_referrers(obj):
        kind = None

        if ignoreframes and inspect.isframe(referrer):
            # XXX Be more selective?
            continue

        # Try the 3 container types.
        container = get_container_type(referrer)
        if container == 'set':
            for value in referrer:
                if value is obj:
                    kind = 'element'
                    binding = None
                    break
        elif container == 'sequence':
            for index, value in enumerate(referrer):
                if value is obj:
                    kind = 'index'
                    binding = index
        elif container == 'mapping':
            for key, value in referrer.items():
                if value is obj:
                    kind = 'key'
                    binding = key
            else:
                for key in referrer:
                    if key is obj:
                        kind = 'element'
                        binding = None

        if kind is None:
            # Fall back to attributes.
            for name in dir(referrer):
                if getattr(referrer, name, None) is obj:
                    kind = 'attr'
                    binding = name
                    break
            else:
                # XXX Fall back to referrer.__dict__?
                pass

        if kind is not None:
            yield referrer, binding, kind


#################################################
# module helpers

def mod_from_ns(ns):
    # XXX Support looking up in sys.modules first?

    #try:
    #    nsname = ns['__name__']
    #except KeyError:
    #    return None

    #nsrefs = [obj for obj in gc.get_referrers(ns)
    #          if getattr(obj, '__globals__', None) is not ns]
    for obj in gc.get_referrers(ns):
        if not isinstance(obj, MODULE_TYPE):
            continue
        if obj.__dict__ is not ns:
            continue
        # XXX Could be others?
        return obj
    else:
        return None


def iter_where_from_imported(mod):
    for name, attr in mod.__dict__.items():
        for obj, binding, _ in iter_where_bound(attr):
            if not isinstance(obj, MODULE_TYPE):
                # XXX Handle function/class-local imports?
                continue
            yield name, attr, obj, binding


def iter_where_imported(mod, globalonly=True):
    for obj, binding, _ in iter_where_bound(mod):
        if globalonly and not isinstance(obj, MODULE_TYPE):
            continue
        # XXX Specially handle function/class-local imports?
        yield obj, binding


def _get_parent(mod):
    parent = mod.__name__.rpartition('.')[0]
    return sys.modules[parent] if parent else None


def _get_path(mod):
    parent = _get_parent(mod)
    if not parent:
        #return sys.path
        return None
    else:
        return parent.__path__


# XXX Move to a classmethod of ModuleSpec?
def _copy_spec(spec, cls=None):
    if cls is None:
        from importlib2._bootstrap import _new_module as cls
    smsl = spec.submodule_search_locations
    copied = cls(spec.name, spec.loader,
                 origin=spec.origin,
                 loader_state=spec.loader_state,
                 is_package=(smsl is None))
    if smsl is not None:
        copied.submodule_search_locations.extend(smsl)
    copied.cached = spec.cached
    copied.has_location = spec.has_location
    return copied


def _get_spec(mod):
    from importlib2 import _bootstrap
    spec = getattr(mod, '__spec__', None)
    if spec is not None:
        if spec.__class__.__module__.startswith('importlib.'):
            # XXX Direct subclasses of importlib's ModuleSpec too?
            return _copy_spec(spec)
        else:
            return spec
    # Generate a new spec.
    # XXX Use _bootstrap._spec_from_module()?
    name = mod.__name__
    loader = getattr(mod, '__loader__', None)
    filename = getattr(mod, '__file__', None)
    if loader is None:
        if name == '__main__':
            if not filename:
                return None
            # XXX Use SourceFileLoader.
            spec = None
        else:
            path = _get_path(mod)
            spec = _bootstrap._find_spec(name, path)
    else:
        if name == '__main__':
            # XXX Figure out the name for the spec?
            spec = None
        else:
            spec = _bootstrap.spec_from_loader(name, loader)
    return spec


def _loader_class(loader):
    if isinstance(loader, type):
        return loader
    else:
        return loader.__class__


def _copy_loader(loader):
    cls = _loader_class(loader)
    instance = (loader is not cls)
    # Fix the class.
    if cls.__module__ == 'importlib._bootstrap':
        from importlib2 import _bootstrap
        cls = getattr(_bootstrap, cls.__name__)
    elif cls.__module__ == 'importlib.util':
        import importlib2.util
        cls = getattr(importlib2.util, cls.__name__)
    elif cls.__module__.startswith('importlib.'):
        # There shouldn't be any!
        raise NotImplementedError
    else:
        # Not an importlib loader, so don't copy!
        # XXX Replace importlib loaders in __bases__?
        return loader
    # Copy the loader.
    if not instance:
        copied = cls
    elif cls is not loader.__class__:
        # no-op!
        copied = loader
    else:
        argspec = inspect.getargspec(cls.__init__)
        kwargs = {getattr(loader, n) for n in argspec.args}
        copied = cls(**kwargs)
    return copied


def _get_loader(mod, spec=None):
    loader = getattr(mod, '__loader__', None)
    if loader is None:
        if spec is None:
            spec = getattr(mod, '__spec__', None)
            if spec is None:
                raise RuntimeError('{}: __spec__ should have been set already'
                                   .format(mod))
        loader = spec.loader
        if loader is None:
            from importlib2 import _bootstrap
            cls = _bootstrap._NamespaceLoader
            loader = cls.__new__(cls)
    assert loader is not None
    return _copy_loader(loader)


#################################################
# module fixers

def inject_module(mod):
    if mod.__class__ is not MODULE_TYPE:
        return
    if mod.__name__ == '__main__':
        # XXX __main__ might have a valid spec/loader...
        return

    spec = _get_spec(mod)
    if spec is None:
        raise RuntimeError('no spec found for {!r}'.format(mod))
    loader = _get_loader(mod, spec=spec)
    # Fix them up.
    if hasattr(mod, '__loader__') and spec.loader is mod.__loader__:
        # Keep them in sync.
        spec.loader = loader
    else:
        spec.loader = _copy_loader(spec.loader)
    # Set them.
    mod.__spec__ = spec
    mod.__loader__ = loader
    # XXX Fix __pycache__?
    # XXX Fix any attributes in the module from importlib?


def inject_modules():
    # See _bootstrap.setup().
    for _, mod in sorted(sys.modules.items()):
        inject_module(mod)


def verify_module(mod, injected=True):
    if mod.__name__ == '__main__':
        return

    spec = getattr(mod, '__spec__', None)
    loader = getattr(mod, '__loader__', None)

    error = None
    if spec is None:
        error = '{!r} missing __spec__'
    elif loader is None:
        error = '{!r} missing __loader__'
    else:
        # __class__ is not writeable...
        #if mod.__class__ is MODULE_TYPE:
        #    error = '{!r} has wrong module type'
        if spec.__class__.__module__.startswith('importlib.'):
            error = '{!r} has wrong spec type'
        if _loader_class(loader).__module__.startswith('importlib.'):
            error = '{!r} has wrong loader type'

    if error is not None:
        raise RuntimeError(error.format(mod.__name__))


def verify_modules(injected=True):
    for _, mod in sys.modules.items():
        if mod is None:
            continue  # Entry will be removed later in fix_modules().
        verify_module(mod, injected=injected)
