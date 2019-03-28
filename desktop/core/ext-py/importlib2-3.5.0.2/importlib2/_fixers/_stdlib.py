from __future__ import absolute_import

from contextlib import contextmanager
import sys

from . import builtins, swap


def inject_py_compile():
    from . import py_compile
    sys.modules['py_compile'] = py_compile


@contextmanager
def _fix_token():
    import token
    defaults = {'N_TOKENS': 0,
                'ATEQUAL': 0,
                }
    managed = {}
    try:
        for name, value in defaults.items():
            try:
                original = getattr(token, name)
            except AttributeError:
                setattr(token, name, value)
            else:
                setattr(token, name, value)
                managed[name] = original
        __all__ = [n for n in dir(token) if not n.startswith('_')]
        setattr(token, '__all__', __all__)
        yield
    finally:
        for name, value in managed.items():
            setattr(token, name, value)


def inject_tokenize():
    import tokenize
    if not hasattr(tokenize, 'detect_encoding'):
        import re
        with swap(sys.modules, 'builtins', builtins, detect=True):
            with swap(re, 'ASCII', getattr(re, 'ASCII', 0)):
                with _fix_token():
                    #from . import tokenize
                    from .tokenize import detect_encoding
        #sys.modules['tokenize'] = tokenize
        tokenize.detect_encoding = detect_encoding
