"""Beaker utilities"""
try:
    import thread as _thread
    import threading as _threading
except ImportError:
    import dummy_thread as _thread
    import dummy_threading as _threading

from datetime import datetime, timedelta
import os
import string
import types
import weakref
import warnings

try:
    Set = set
except NameError:
    from sets import Set
try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1

from beaker.converters import asbool

try:
    from base64 import b64encode, b64decode
except ImportError:
    import binascii

    _translation = [chr(_x) for _x in range(256)]

    # From Python 2.5 base64.py
    def _translate(s, altchars):
        translation = _translation[:]
        for k, v in altchars.items():
            translation[ord(k)] = v
        return s.translate(''.join(translation))

    def b64encode(s, altchars=None):
        """Encode a string using Base64.

        s is the string to encode.  Optional altchars must be a string of at least
        length 2 (additional characters are ignored) which specifies an
        alternative alphabet for the '+' and '/' characters.  This allows an
        application to e.g. generate url or filesystem safe Base64 strings.

        The encoded string is returned.
        """
        # Strip off the trailing newline
        encoded = binascii.b2a_base64(s)[:-1]
        if altchars is not None:
            return _translate(encoded, {'+': altchars[0], '/': altchars[1]})
        return encoded

    def b64decode(s, altchars=None):
        """Decode a Base64 encoded string.

        s is the string to decode.  Optional altchars must be a string of at least
        length 2 (additional characters are ignored) which specifies the
        alternative alphabet used instead of the '+' and '/' characters.

        The decoded string is returned.  A TypeError is raised if s were
        incorrectly padded or if there are non-alphabet characters present in the
        string.
        """
        if altchars is not None:
            s = _translate(s, {altchars[0]: '+', altchars[1]: '/'})
        try:
            return binascii.a2b_base64(s)
        except binascii.Error, msg:
            # Transform this exception for consistency
            raise TypeError(msg)

try:
    from threading import local as _tlocal
except ImportError:
    try:
        from dummy_threading import local as _tlocal
    except ImportError:
        class _tlocal(object):
            def __init__(self):
                self.__dict__['_tdict'] = {}

            def __delattr__(self, key):
                try:
                    del self._tdict[(thread.get_ident(), key)]
                except KeyError:
                    raise AttributeError(key)

            def __getattr__(self, key):
                try:
                    return self._tdict[(thread.get_ident(), key)]
                except KeyError:
                    raise AttributeError(key)

            def __setattr__(self, key, value):
                self._tdict[(thread.get_ident(), key)] = value


__all__  = ["ThreadLocal", "Registry", "WeakValuedRegistry", "SyncDict",
            "encoded_path", "verify_directory"]


def verify_directory(dir):
    """verifies and creates a directory.  tries to
    ignore collisions with other threads and processes."""

    tries = 0
    while not os.access(dir, os.F_OK):
        try:
            tries += 1
            os.makedirs(dir)
        except:
            if tries > 5:
                raise

    
def deprecated(func, message):
    def deprecated_method(*args, **kargs):
        warnings.warn(message, DeprecationWarning, 2)
        return func(*args, **kargs)
    try:
        deprecated_method.__name__ = func.__name__
    except TypeError: # Python < 2.4
        pass
    deprecated_method.__doc__ = "%s\n\n%s" % (message, func.__doc__)
    return deprecated_method

class ThreadLocal(object):
    """stores a value on a per-thread basis"""

    __slots__ = 'tlocal'

    def __init__(self):
        self.tlocal = _tlocal()
    
    def put(self, value):
        self.tlocal.value = value
    
    def has(self):
        return hasattr(self.tlocal, 'value')
            
    def get(self, default=None):
        return getattr(self.tlocal, 'value', default)
            
    def remove(self):
        del self.tlocal.value
    
class SyncDict(object):
    """
    An efficient/threadsafe singleton map algorithm, a.k.a.
    "get a value based on this key, and create if not found or not
    valid" paradigm:
    
        exists && isvalid ? get : create

    Works with weakref dictionaries and the LRUCache to handle items
    asynchronously disappearing from the dictionary.  

    Use python 2.3.3 or greater !  a major bug was just fixed in Nov.
    2003 that was driving me nuts with garbage collection/weakrefs in
    this section.

    """    
    def __init__(self):
        self.mutex = _thread.allocate_lock()
        self.dict = {}
        
    def get(self, key, createfunc, *args, **kwargs):
        try:
            if self.has_key(key):
                return self.dict[key]
            else:
                return self.sync_get(key, createfunc, *args, **kwargs)
        except KeyError:
            return self.sync_get(key, createfunc, *args, **kwargs)

    def sync_get(self, key, createfunc, *args, **kwargs):
        self.mutex.acquire()
        try:
            try:
                if self.has_key(key):
                    return self.dict[key]
                else:
                    return self._create(key, createfunc, *args, **kwargs)
            except KeyError:
                return self._create(key, createfunc, *args, **kwargs)
        finally:
            self.mutex.release()

    def _create(self, key, createfunc, *args, **kwargs):
        self[key] = obj = createfunc(*args, **kwargs)
        return obj

    def has_key(self, key):
        return self.dict.has_key(key)
        
    def __contains__(self, key):
        return self.dict.__contains__(key)
    def __getitem__(self, key):
        return self.dict.__getitem__(key)
    def __setitem__(self, key, value):
        self.dict.__setitem__(key, value)
    def __delitem__(self, key):
        return self.dict.__delitem__(key)
    def clear(self):
        self.dict.clear()


class WeakValuedRegistry(SyncDict):
    def __init__(self):
        self.mutex = _threading.RLock()
        self.dict = weakref.WeakValueDictionary()

            
def encoded_path(root, identifiers, extension = ".enc", depth = 3,
                 digest_filenames=True):
    """Generate a unique file-accessible path from the given list of
    identifiers starting at the given root directory."""
    ident = string.join(identifiers, "_")

    if digest_filenames:
        ident = sha1(ident).hexdigest()
    
    ident = os.path.basename(ident)

    tokens = []
    for d in range(1, depth):
        tokens.append(ident[0:d])
    
    dir = os.path.join(root, *tokens)
    verify_directory(dir)
    
    return os.path.join(dir, ident + extension)


def verify_options(opt, types, error):
    if not isinstance(opt, types):
        if not isinstance(types, tuple):
            types = (types,)
        coerced = False
        for typ in types:
            try:
                if typ in (list, tuple):
                    opt = [x.strip() for x in opt.split(',')]
                else:
                    if typ == bool:
                        typ = asbool
                    opt = typ(opt)
                coerced = True
            except:
                pass
            if coerced:
                break
        if not coerced:
            raise Exception(error)
    elif isinstance(opt, str) and not opt.strip():
        raise Exception("Empty strings are invalid for: %s" % error)
    return opt


def verify_rules(params, ruleset):
    for key, types, message in ruleset:
        if key in params:
            params[key] = verify_options(params[key], types, message)
    return params


def coerce_session_params(params):
    rules = [
        ('data_dir', (str, types.NoneType), "data_dir must be a string "
         "referring to a directory."),
        ('lock_dir', (str,), "lock_dir must be a string referring to a "
         "directory."),
        ('type', (str, types.NoneType), "Session type must be a string."),
        ('cookie_expires', (bool, datetime, timedelta), "Cookie expires was "
         "not a boolean, datetime, or timedelta instance."),
        ('cookie_domain', (str, types.NoneType), "Cookie domain must be a "
         "string."),
        ('id', (str,), "Session id must be a string."),
        ('key', (str,), "Session key must be a string."),
        ('secret', (str, types.NoneType), "Session secret must be a string."),
        ('validate_key', (str, types.NoneType), "Session encrypt_key must be "
         "a string."),
        ('encrypt_key', (str, types.NoneType), "Session validate_key must be "
         "a string."),
        ('secure', (bool, types.NoneType), "Session secure must be a boolean."),
        ('timeout', (int, types.NoneType), "Session timeout must be an "
         "integer."),
        ('auto', (bool, types.NoneType), "Session is created if accessed."),
    ]
    return verify_rules(params, rules)


def coerce_cache_params(params):
    rules = [
        ('data_dir', (str, types.NoneType), "data_dir must be a string "
         "referring to a directory."),
        ('lock_dir', (str,), "lock_dir must be a string referring to a "
         "directory."),
        ('type', (str,), "Cache type must be a string."),
        ('enabled', (bool, types.NoneType), "enabled must be true/false "
         "if present."),
        ('expire', (int, types.NoneType), "expire must be an integer representing "
         "how many seconds the cache is valid for"),
        ('regions', (list, tuple, types.NoneType), "Regions must be a "
         "comma seperated list of valid regions")
    ]
    return verify_rules(params, rules)


def parse_cache_config_options(config, include_defaults=True):
    """Parse configuration options and validate for use with the
    CacheManager"""
    # Load default cache options
    if include_defaults:
        options= dict(type='memory', data_dir=None, expire=None, 
                           log_file=None)
    else:
        options = {}
    for key, val in config.iteritems():
        if key.startswith('beaker.cache.'):
            options[key[13:]] = val
        if key.startswith('cache.'):
            options[key[6:]] = val
    coerce_cache_params(options)
    
    # Set cache to enabled if not turned off
    if 'enabled' not in options:
        options['enabled'] = True
    
    # Configure region dict if regions are available
    regions = options.pop('regions', None)
    if regions:
        region_configs = {}
        for region in regions:
            # Setup the default cache options
            region_options = dict(data_dir=options.get('data_dir'),
                                  lock_dir=options.get('lock_dir'),
                                  type=options.get('type'),
                                  enabled=options['enabled'],
                                  expire=options.get('expire'))
            region_len = len(region) + 1
            for key in options.keys():
                if key.startswith('%s.' % region):
                    region_options[key[region_len:]] = options.pop(key)
            coerce_cache_params(region_options)
            region_configs[region] = region_options
        options['cache_regions'] = region_configs
    return options

def func_namespace(func):
    """Generates a unique namespace for a function"""
    kls = None
    if hasattr(func, 'im_func'):
        kls = func.im_class
        func = func.im_func
    
    if kls:
        return '%s.%s' % (kls.__module__, kls.__name__)
    else:
        return func.__module__
