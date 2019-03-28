from contextlib import contextmanager


@contextmanager
def _locked():
    from . import _bootstrap
    _bootstrap._imp.acquire_lock()
    try:
        yield
    finally:
        _bootstrap._imp.release_lock()


#################################################
# install

__original_import__ = None
__installed__ = False


def _install___import__():
    from ._fixers import builtins
    from . import __import__ as importlib___import__
    global __original_import__
    assert __original_import__ is None  # should only be called once...
    __original_import__ = builtins.__import__
    builtins.__import__ = importlib___import__

    import sys
    if sys.version_info[0] == 2:
        implicit = importlib___import__.__defaults__[:-1] + (-1,)
        importlib___import__.__defaults__ = implicit


def inject():
    from ._fixers import inject_importlib, _modules, _importstate
    inject_importlib('importlib2')
    inject_importlib('importlib2._bootstrap')
    # XXX Tie this directly to "importlib"?
#    if name == _target + '._bootstrap':
#        # XXX Inject _boostrap into _frozen_importlib (if it exists)?
#        if not sys.modules.get('importlib._bootstrap'):
#            sys.modules['_frozen_importlib'] = bootstrap
    _importstate.inject_import_state()
    _modules.inject_moduletype()
    _modules.inject_modules()

    _importstate.verify_import_state()
    _modules.verify_modules()

    from ._fixers._stdlib import inject_py_compile, inject_tokenize
    inject_py_compile()
    inject_tokenize()


def install(_inject=True):
    global __installed__
    if __installed__:
        return
    with _locked():
        if _inject:
            inject()
        _install___import__()
        __installed__ = True
