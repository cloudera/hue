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
from django.conf import settings


# When a Thrift or REST call finishes, the level at which we log its duration
# depends on the number of millis the call took.
WARN_LEVEL_CALL_DURATION_MS = 5000
INFO_LEVEL_CALL_DURATION_MS = 1000


def get_current_app(frame=None):
  """
  Return the name of the app from INSTALLED_APPS that is most recently
  present on the call stack.
  """
  if frame == None:
    frame = inspect.currentframe().f_back

  while frame:
    module = inspect.getmodule(frame.f_code)
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
    if module.__name__.startswith('desktop.lib.metrics.views'):
      return app
    if module.__name__.startswith(app) and not module.__name__.startswith("desktop.lib"):
      return app
  return None
