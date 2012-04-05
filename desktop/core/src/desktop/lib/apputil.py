#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import os
import sys
from django.conf import settings


def get_current_app(frame=None):
  """
  Return the name of the app from INSTALLED_APPS that is most recently
  present on the call stack.
  """
  if frame == None:
    frame = inspect.currentframe().f_back

  while frame:
    module = getmodule_wrapper(frame.f_code)
    if not module:
      raise Exception(("No module for code %s (frame %s). Perhaps you have an old " +
                       ".pyc file hanging around?") % (repr(frame.f_code), repr(frame)))
    app = get_app_for_module(module)
    if app:
      return app
    frame = frame.f_back

  # did not find any app
  return None

def get_app_for_module(module):
  for app in settings.INSTALLED_APPS:
    # TODO(philip): This is quite hacky.  If desktop becomes a more
    # full application, we'll want to separate this out more cleanly.
    if module.__name__.startswith(app) and not module.__name__.startswith("desktop.lib"):
      return app
  return None


def getmodule_wrapper(obj):
  """
  inspect.getmodule() does not work with symlink well before Python 2.5. It
  uses realpath() to determine the locations of sys.modules.

  So we borrow the getmodule() code from Python 2.5 and do it ourselves.
  """
  if sys.version_info >= (2, 5):
    return inspect.getmodule(obj)
  return getmodule_2_5(obj)


#
# The following is taken from Python-2.5.4's inspect.py.
#
modulesbyfile = {}
_filesbymodname = {}

def getmodule_2_5(object, _filename=None):
    """Return the module an object was defined in, or None if not found."""
    global modulesbyfile
    global _filesbymodname

    if inspect.ismodule(object):
        return object
    if hasattr(object, '__module__'):
        return sys.modules.get(object.__module__)
    # Try the filename to modulename cache
    if _filename is not None and _filename in modulesbyfile:
        return sys.modules.get(modulesbyfile[_filename])
    # Try the cache again with the absolute file name
    try:
        file = inspect.getabsfile(object)
    except TypeError:
        return None
    if file in modulesbyfile:
        return sys.modules.get(modulesbyfile[file])
    # Update the filename to module name cache and check yet again
    # Copy sys.modules in order to cope with changes while iterating
    for modname, module in sys.modules.items():
        if inspect.ismodule(module) and hasattr(module, '__file__'):
            f = module.__file__
            if f == _filesbymodname.get(modname, None):
                # Have already mapped this module, so skip it
                continue
            _filesbymodname[modname] = f
            f = inspect.getabsfile(module)
            # Always map to the name the module knows itself by
            modulesbyfile[f] = modulesbyfile[
                os.path.realpath(f)] = module.__name__
    if file in modulesbyfile:
        return sys.modules.get(modulesbyfile[file])
    # Check the main module
    main = sys.modules['__main__']
    if not hasattr(object, '__name__'):
        return None
    if hasattr(main, object.__name__):
        mainobject = getattr(main, object.__name__)
        if mainobject is object:
            return main
    # Check builtins
    builtin = sys.modules['__builtin__']
    if hasattr(builtin, object.__name__):
        builtinobject = getattr(builtin, object.__name__)
        if builtinobject is object:
            return builtin
