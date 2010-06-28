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

"""
Helpers to reuse and access native filebrowser views.
"""

from desktop.lib.django_util import render, render_injected

import filebrowser.plugin.toolbar

def render_with_toolbars(template, request, data, **kwargs):
  """
  render_with_toolbars(template, request, data, **kwargs) -> HttpResposne

  Return a HttpResponse of the filebrowser template view, plus all the registered toolbars.
  This also allow callers to reuse templates in the FileBrowser.
  """
  resp = render(template, request, data, **kwargs)
  toolbars = filebrowser.plugin.toolbar.all()
  context = filebrowser.plugin.toolbar.DisplayContext(template, request, data)

  for tb in toolbars:
    render_injected(resp, tb.display(context))
  return resp
