import os
import sys


#################################################
# import state helpers

def _get_old_default_finders(finders):
    # The only metapath finder classes in _boostrap are defaults.
    oldfinders = []
    for finder in finders:
        modname = getattr(finder, '__module__',
                          finder.__class__.__module__)
        if modname == '_frozen_importlib':
            oldfinders.append(finder)
    return oldfinders


def _remove_old_default_finders(finders):
    # Remove 3.4+ defaults from sys.meta_path.
    oldfinders = _get_old_default_finders(finders)
    for finder in oldfinders:
        finders.remove(finder)
    return oldfinders


def _add_default_finders(finders):
    # See _bootstrap._install().
    from importlib2 import _bootstrap
    finders.append(_bootstrap.BuiltinImporter)
    finders.append(_bootstrap.FrozenImporter)
    if os.name == 'nt':
        finders.append(_bootstrap.WindowsRegistryFinder)
    finders.append(_bootstrap.PathFinder)


def _replace_finders(finders):
    old = _remove_old_default_finders(finders)
    _add_default_finders(finders)
    return old


def _get_old_default_hooks(hooks):
    # The only hooks from _bootstrap come from FileFinder.
    oldhooks = []
    for hook in hooks:
        if hook.__module__ == '_frozen_importlib':
            oldhooks.append(hook)
    # XXX Include imp.NullImporter?
    return oldhooks


def _remove_old_default_hooks(hooks):
    # Remove 3.4+ defaults from sys.path_hooks.
    oldhooks = _get_old_default_hooks(hooks)
    for hook in oldhooks:
        hooks.remove(hook)
    return oldhooks


def _add_default_hooks(hooks):
    # See _bootstrap._install().
    from importlib2 import _bootstrap
    supported_loaders = _bootstrap._get_supported_file_loaders()
    hook = _bootstrap.FileFinder.path_hook(*supported_loaders)
    hooks.extend([hook])


def _replace_hooks(hooks):
    old = _remove_old_default_hooks(hooks)
    _add_default_hooks(hooks)
    return old


#################################################
# fixers

def fix_modules():
    # See PEP 328
    # "Relative Imports and Indirection Entries in sys.modules"
    #   http://legacy.python.org/dev/peps/pep-0328/#id12
    indirections = [n for n, v in sys.modules.items() if v is None]
    for name in indirections:
        del sys.modules[name]


def inject_hooks():
    _replace_hooks(sys.path_hooks)


def inject_finders():
    _replace_finders(sys.meta_path)


def inject_finder_cache():
    sys.path_importer_cache.clear()


def inject_import_state():
    inject_hooks()
    inject_finders()
    inject_finder_cache()
    fix_modules()


def verify_import_state():
    # path hooks
    for hook in sys.path_hooks:
        assert hook.__module__ != 'importlib._bootstrap'
    # meta path
    from importlib2 import _bootstrap
    if os.name == 'nt':
        assert sys.meta_path[-4] is _bootstrap.BuiltinImporter
        assert sys.meta_path[-3] is _bootstrap.FrozenImporter
        assert sys.meta_path[-2] is _bootstrap.WindowsRegistryFinder
    else:
        assert sys.meta_path[-3] is _bootstrap.BuiltinImporter
        assert sys.meta_path[-2] is _bootstrap.FrozenImporter
    assert sys.meta_path[-1] is _bootstrap.PathFinder
    # path importer cache
    for finder in sys.path_importer_cache.values():
        assert not finder.__class__.__module__.startswith('importlib.')
