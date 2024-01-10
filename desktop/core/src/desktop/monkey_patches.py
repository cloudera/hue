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

import hashlib
import imp
import importlib
import logging
import re
import sys

from django.conf import settings
from django.core.validators import RegexValidator
from django.template.context import RequestContext
from django.utils.module_loading import import_string

LOG = logging.getLogger()


def monkey_patch_username_validator():
  """
  In 1.6, the `User.username` field gained some validation rules to check that
  it conformed to a particular regex. Unfortunately we use to support a more
  liberal username scheme. The proper solution would be to use our own custom
  user model, but that touches a lot of code. It's easier if we just modify the
  regular expression inside the username validator.
  """

  from useradmin.models import User
  from desktop.lib.django_util import get_username_re_rule

  username = User._meta.get_field("username")

  regex = re.compile('^%s$' % get_username_re_rule())

  for validator in username.validators:
    if isinstance(validator, RegexValidator):
      validator.regex = regex


_standard_context_processors = None
_builtin_context_processors = ('django.template.context_processors.csrf',)


# This is a function rather than module-level procedural code because we only
# want it to execute if somebody uses RequestContext.
def get_standard_processors():
  global _standard_context_processors
  if _standard_context_processors is None:
    processors = []
    collect = []
    collect.extend(_builtin_context_processors)
    collect.extend(settings.GTEMPLATE_CONTEXT_PROCESSORS)
    for path in collect:
      func = import_string(path)
      processors.append(func)
    _standard_context_processors = tuple(processors)
  return _standard_context_processors


def monkey_patch_request_context_init(self, request, dict_=None, processors=None, use_l10n=None, use_tz=None, autoescape=True):
  super(RequestContext, self).__init__(
    dict_, use_l10n=use_l10n, use_tz=use_tz, autoescape=autoescape)
  self.request = request
  self._processors = () if processors is None else tuple(processors)
  self._processors_index = len(self.dicts)

  updates = dict()
  # @TODO@ Prakash to Implement context processor
  for processor in get_standard_processors():
    updates.update(processor(request))
  self.update(updates)


def monkey_patch_md5(modules_to_patch):
  """Monkey-patch calls to MD5 that aren't used for security purposes.

  Sets RHEL's custom flag `usedforsecurity` to False allowing MD5 in FIPS mode.
  `modules_to_patch` must be an iterable of module names (strings).
  Modules must use `import hashlib` and not `from hashlib import md5`.
  """
  orig_hashlib_md5 = hashlib.md5
  def _non_security_md5(*args, **kwargs):
    kwargs['usedforsecurity'] = False
    return orig_hashlib_md5(*args, **kwargs)

  LOG.debug("Start monkey patch md5 ...")
  if sys.version_info[0] > 2:
    hashlib_spec = importlib.util.find_spec('hashlib')
    patched_hashlib = importlib.util.module_from_spec(hashlib_spec)
    hashlib_spec.loader.exec_module(patched_hashlib)
  else:
    patched_hashlib = imp.load_module('hashlib', *imp.find_module('hashlib'))

  patched_hashlib.md5 = _non_security_md5

  # Inject the patched hashlib for all requested modules
  for module_name in modules_to_patch:
    module = importlib.import_module(module_name)
    module.hashlib = patched_hashlib
  LOG.debug("Finish monkey patch md5 ...")
