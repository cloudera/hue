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

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from desktop import appmanager
from hadoop.fs import LocalSubFileSystem

import markdown
import urllib
import os

INDEX_FILENAMES = ("index.md", "index.html", "index.txt")

def _unquote_path(path):
  """Normalizes paths."""
  return urllib.unquote(path)

def get_help_fs(app_name):
  """
  Creates a local file system for a given app's help directory.
  """
  app = appmanager.get_desktop_module(app_name)
  if app is not None:
    if app.help_dir is None:
      raise PopupException("No help available for app '%s'." % app_name)
    return LocalSubFileSystem(app.help_dir)
  else:
    raise PopupException("App '%s' is not loaded, so no help is available for it!" % app_name)

def view(request, app, path):
  """
  Views and renders a file at a given path.

  Markdown files are parsed through markdown; others
  are just pasted in <pre>'s.

  TODO: Expose a way to do images.
  """

  path = _unquote_path(path)
  fs = get_help_fs(app)

  if fs.isdir(path):
    for i in INDEX_FILENAMES:
      tmp_path = os.path.join(path, i)
      if fs.isfile(tmp_path):
        path = tmp_path

  if not fs.isfile(path):
    raise PopupException("Could not find or read the file: %s (app %s)" % (path, app))

  content = fs.open(path, 'r').read()
  content = unicode(content, 'utf-8', errors='replace')
  if path.lower().endswith(".md"):
    content = ('<div class="print rendered-markdown">' +
               markdown.markdown(content, ['extra']) +
               '</div>')
  elif path.lower().endswith(".html"):
    content = '<div class="print">%s</div>' % (content,)
  else:
    # TODO(todd) escape content?
    content = '<pre>' + content + '</pre>'

  data = {
    'content': content,
    'apps': sorted([ x for x in appmanager.DESKTOP_MODULES if x.help_dir ],
      key = lambda app: app.menu_index),
    'title': appmanager.get_desktop_module(app).nice_name,
    'current': app,
    'is_embeddable': request.GET.get('is_embeddable', False),
  }
  return render("display.mako", request, data)
