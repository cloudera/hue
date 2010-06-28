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

from desktop.lib import apputil
import os
from django.template.loaders import app_directories
import logging
import sys
from django.template import TemplateDoesNotExist

# Django is bad at namespacing their templates,
# and auth's templates live in the admin module.
APP_REMAP = {
  "django.contrib.auth": "django.contrib.admin"
}

def load_template_source(name, dirs=[]):
  app = apputil.get_current_app()
  if not app:
    logging.info("No app found while loading template %s" % name)
    raise TemplateDoesNotExist("No app: " + name)
  if app in APP_REMAP:
    app = APP_REMAP[app]
  # We can import the app, and then find it in sys.modules,
  # thereby, in cases of "a.b.c", finding the whole thing, and not
  # just "a".
  __import__(app)
  app_module = sys.modules[app]
  app_dir = os.path.dirname(app_module.__file__)
  default_dir = os.path.join(app_dir, 'templates')

  return app_directories.load_template_source(name, [default_dir])

load_template_source.is_usable = True
