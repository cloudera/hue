import copy
import operator
from functools import wraps
import sys

from django.utils import six
from django.utils.six.moves import copyreg


# You can't trivially replace this with `functools.partial` because this binds
# to classes and returns bound instances, whereas functools.partial (on
# CPython) is a type and its instances don't bind.
def curry(_curried_func, *args, **kwargs):
    def _curried(*moreargs, **morekwargs):
        return _curried_func(*(args + moreargs), **dict(kwargs, **morekwargs))
    return _curried


def memoize(func, cache, num_args):
    """
    Wrap a function so that results for any argument tuple are stored in
    'cache'. Note that the args to the function must be usable as dictionary
    keys.

    Only the first num_args are considered when creating the key.
    """
    @wraps(func)
    def wrapper(*args):
        mem_args = args[:num_args]
        if mem_args in cache:
            return cache[mem_args]
        result = func(*args)
        cache[mem_args] = result
        return result
    return wrapper


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res


class Promise(object):
    """
    This is just a base class for the proxy class created in
    the closure of the lazy function. It can be used to recognize
    promises in code.
    """
    pass


def lazy(func, *resultclasses):
    """
    Turns any callable into a lazy evaluated callable. You need to give result
    classes or types -- at least one is needed so that the automatic forcing of
    the lazy evaluation code is triggered. Results are not memoized; the
    function is evaluated on every access.
    """

    @total_ordering
    class __proxy__(Promise):
        """
        Encapsulate a function call and act as a proxy for methods that are
        called on the result of that function. The function is not evaluated
        until one of the methods on the result is called.
        """
        __dispatch = None

        def __init__(self, args, kw):
            self.__args = args
            self.__kw = kw
            if self.__dispatch is None:
                self.__prepare_class__()

        def __reduce__(self):
            return (
                _lazy_proxy_unpickle,
                (func, self.__args, self.__kw) + resultclasses
            )

        def __prepare_class__(cls):
            cls.__dispatch = {}
            for resultclass in resultclasses:
                cls.__dispatch[resultclass] = {}
                for type_ in reversed(resultclass.mro()):
                    for (k, v) in type_.__dict__.items():
                        # All __promise__ return the same wrapper method, but
                        # they also do setup, inserting the method into the
                        # dispatch dict.
                        meth = cls.__promise__(resultclass, k, v)
                        if hasattr(cls, k):
                            continue
                        setattr(cls, k, meth)
            cls._delegate_bytes = bytes in resultclasses
            cls._delegate_text = six.text_type in resultclasses
            assert not (cls._delegate_bytes and cls._delegate_text), "Cannot call lazy() with both bytes and text return types."
            if cls._delegate_text:
                if six.PY3:
                    cls.__str__ = cls.__text_cast
                else:
                    cls.__unicode__ = cls.__text_cast
            elif cls._delegate_bytes:
                if six.PY3:
                    cls.__bytes__ = cls.__bytes_cast
                else:
                    cls.__str__ = cls.__bytes_cast
        __prepare_class__ = classmethod(__prepare_class__)

        def __promise__(cls, klass, funcname, method):
            # Builds a wrapper around some magic method and registers that
            # magic method for the given type and method name.
            def __wrapper__(self, *args, **kw):
                # Automatically triggers the evaluation of a lazy value and
                # applies the given magic method of the result type.
                res = func(*self.__args, **self.__kw)
                for t in type(res).mro():
                    if t in self.__dispatch:
                        return self.__dispatch[t][funcname](res, *args, **kw)
                raise TypeError("Lazy object returned unexpected type.")

            if klass not in cls.__dispatch:
                cls.__dispatch[klass] = {}
            cls.__dispatch[klass][funcname] = method
            return __wrapper__
        __promise__ = classmethod(__promise__)

        def __text_cast(self):
            return func(*self.__args, **self.__kw)

        def __bytes_cast(self):
            return bytes(func(*self.__args, **self.__kw))

        def __cast(self):
            if self._delegate_bytes:
                return self.__bytes_cast()
            elif self._delegate_text:
                return self.__text_cast()
            else:
                return func(*self.__args, **self.__kw)

        def __eq__(self, other):
            if isinstance(other, Promise):
                other = other.__cast()
            return self.__cast() == other

        def __lt__(self, other):
            if isinstance(other, Promise):
                other = other.__cast()
            return self.__cast() < other

        def __hash__(self):
            return hash(self.__cast())

        def __mod__(self, rhs):
            if self._delegate_bytes and six.PY2:
                return bytes(self) % rhs
            elif self._delegate_text:
                return six.text_type(self) % rhs
            return self.__cast() % rhs

        def __deepcopy__(self, memo):
            # Instances of this class are effectively immutable. It's just a
            # collection of functions. So we don't need to do anything
            # complicated for copying.
            memo[id(self)] = self
            return self

    @wraps(func)
    def __wrapper__(*args, **kw):
        # Creates the proxy object, instead of the actual value.
        return __proxy__(args, kw)

    return __wrapper__


def _lazy_proxy_unpickle(func, args, kwargs, *resultclasses):
    return lazy(func, *resultclasses)(*args, **kwargs)


def allow_lazy(func, *resultclasses):
    """
    A decorator that allows a function to be called with one or more lazy
    arguments. If none of the args are lazy, the function is evaluated
    immediately, otherwise a __proxy__ is returned that will evaluate the
    function when needed.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in list(args) + list(six.itervalues(kwargs)):
            if isinstance(arg, Promise):
                break
        else:
            return func(*args, **kwargs)
        return lazy(func, *resultclasses)(*args, **kwargs)
    return wrapper

empty = object()


def new_method_proxy(func):
    def inner(self, *args):
        if self._wrapped is empty:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class LazyObject(object):
    """
    A wrapper for another class that can be used to delay instantiation of the
    wrapped class.

    By subclassing, you have the opportunity to intercept and alter the
    instantiation. If you don't need to do that, use SimpleLazyObject.
    """

    # Avoid infinite recursion when tracing __init__ (#19456).
    _wrapped = None

    def __init__(self):
        self._wrapped = empty

    __getattr__ = new_method_proxy(getattr)

    def __setattr__(self, name, value):
        if name == "_wrapped":
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is empty:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if name == "_wrapped":
            raise TypeError("can't delete _wrapped.")
        if self._wrapped is empty:
            self._setup()
        delattr(self._wrapped, name)

    def _setup(self):
        """
        Must be implemented by subclasses to initialise the wrapped object.
        """
        raise NotImplementedError

    # Introspection support
    __dir__ = new_method_proxy(dir)

    # Dictionary methods support
    @new_method_proxy
    def __getitem__(self, key):
        return self[key]

    @new_method_proxy
    def __setitem__(self, key, value):
        self[key] = value

    @new_method_proxy
    def __delitem__(self, key):
        del self[key]


# Workaround for http://bugs.python.org/issue12370
_super = super


class SimpleLazyObject(LazyObject):
    """
    A lazy object initialised from any function.

    Designed for compound objects of unknown type. For builtins or objects of
    known type, use django.utils.functional.lazy.
    """
    def __init__(self, func):
        """
        Pass in a callable that returns the object to be wrapped.

        If copies are made of the resulting SimpleLazyObject, which can happen
        in various circumstances within Django, then you must ensure that the
        callable can be safely run more than once and will return the same
        value.
        """
        self.__dict__['_setupfunc'] = func
        _super(SimpleLazyObject, self).__init__()

    def _setup(self):
        self._wrapped = self._setupfunc()

    if six.PY3:
        __bytes__ = new_method_proxy(bytes)
        __str__ = new_method_proxy(str)
    else:
        __str__ = new_method_proxy(str)
        __unicode__ = new_method_proxy(unicode)

    def __deepcopy__(self, memo):
        if self._wrapped is empty:
            # We have to use SimpleLazyObject, not self.__class__, because the
            # latter is proxied.
            result = SimpleLazyObject(self._setupfunc)
            memo[id(self)] = result
            return result
        else:
            return copy.deepcopy(self._wrapped, memo)

    # Because we have messed with __class__ below, we confuse pickle as to what
    # class we are pickling. It also appears to stop __reduce__ from being
    # called. So, we define __getstate__ in a way that cooperates with the way
    # that pickle interprets this class.  This fails when the wrapped class is
    # a builtin, but it is better than nothing.
    def __getstate__(self):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped.__dict__

    # Python 3.3 will call __reduce__ when pickling; this method is needed
    # to serialize and deserialize correctly.
    @classmethod
    def __newobj__(cls, *args):
        return cls.__new__(cls, *args)

    def __reduce_ex__(self, proto):
        if proto >= 2:
            # On Py3, since the default protocol is 3, pickle uses the
            # ``__newobj__`` method (& more efficient opcodes) for writing.
            return (self.__newobj__, (self.__class__,), self.__getstate__())
        else:
            # On Py2, the default protocol is 0 (for back-compat) & the above
            # code fails miserably (see regression test). Instead, we return
            # exactly what's returned if there's no ``__reduce__`` method at
            # all.
            return (copyreg._reconstructor, (self.__class__, object, None), self.__getstate__())

    # Return a meaningful representation of the lazy object for debugging
    # without evaluating the wrapped object.
    def __repr__(self):
        if self._wrapped is empty:
            repr_attr = self._setupfunc
        else:
            repr_attr = self._wrapped
        return '<SimpleLazyObject: %r>' % repr_attr

    # Need to pretend to be the wrapped class, for the sake of objects that
    # care about this (especially in equality tests)
    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))
    __eq__ = new_method_proxy(operator.eq)
    __ne__ = new_method_proxy(operator.ne)
    __hash__ = new_method_proxy(hash)
    __bool__ = new_method_proxy(bool)       # Python 3
    __nonzero__ = __bool__                  # Python 2


class lazy_property(property):
    """
    A property that works with subclasses by wrapping the decorated
    functions of the base class.
    """
    def __new__(cls, fget=None, fset=None, fdel=None, doc=None):
        if fget is not None:
            @wraps(fget)
            def fget(instance, instance_type=None, name=fget.__name__):
                return getattr(instance, name)()
        if fset is not None:
            @wraps(fset)
            def fset(instance, value, name=fset.__name__):
                return getattr(instance, name)(value)
        if fdel is not None:
            @wraps(fdel)
            def fdel(instance, name=fdel.__name__):
                return getattr(instance, name)()
        return property(fget, fset, fdel, doc)


def partition(predicate, values):
    """
    Splits the values into two sets, based on the return value of the function
    (True/False). e.g.:

        >>> partition(lambda x: x > 3, range(5))
        [0, 1, 2, 3], [4]
    """
    results = ([], [])
    for item in values:
        results[predicate(item)].append(item)
    return results

if sys.version_info >= (2, 7, 2):
    from functools import total_ordering
else:
    # For Python < 2.7.2. Python 2.6 does not have total_ordering, and
    # total_ordering in 2.7 versions prior to 2.7.2 is buggy. See
    # http://bugs.python.org/issue10042 for details. For these versions use
    # code borrowed from Python 2.7.3.
    def total_ordering(cls):
        """Class decorator that fills in missing ordering methods"""
        convert = {
            '__lt__': [('__gt__', lambda self, other: not (self < other or self == other)),
                       ('__le__', lambda self, other: self < other or self == other),
                       ('__ge__', lambda self, other: not self < other)],
            '__le__': [('__ge__', lambda self, other: not self <= other or self == other),
                       ('__lt__', lambda self, other: self <= other and not self == other),
                       ('__gt__', lambda self, other: not self <= other)],
            '__gt__': [('__lt__', lambda self, other: not (self > other or self == other)),
                       ('__ge__', lambda self, other: self > other or self == other),
                       ('__le__', lambda self, other: not self > other)],
            '__ge__': [('__le__', lambda self, other: (not self >= other) or self == other),
                       ('__gt__', lambda self, other: self >= other and not self == other),
                       ('__lt__', lambda self, other: not self >= other)]
        }
        roots = set(dir(cls)) & set(convert)
        if not roots:
            raise ValueError('must define at least one ordering operation: < > <= >=')
        root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
        for opname, opfunc in convert[root]:
            if opname not in roots:
                opfunc.__name__ = opname
                opfunc.__doc__ = getattr(int, opname).__doc__
                setattr(cls, opname, opfunc)
        return cls
