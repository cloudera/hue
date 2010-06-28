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

from django.conf.urls.defaults import url, patterns

# TODO(philip): The names below should be converted to be "qualified", i.e.,
# should be made "filebrowser.ajax_view" instead of "ajax_view".

urlpatterns = patterns('',

  # Base view
  url(r'^$', 'django.views.generic.simple.redirect_to', { "url": "/filebrowser/view/" }),

  url(r'listdir(?P<path>/.*)', 'filebrowser.views.listdir', name='listdir'),
  url(r'display(?P<path>/.*)', 'filebrowser.views.display', name='display'),
  url(r'stat(?P<path>/.*)', 'filebrowser.views.stat', name='stat'),
  url(r'download(?P<path>/.*)', 'filebrowser.views.download', name='download'),
  url(r'status', 'filebrowser.views.status', name='status'),
  # Catch-all for viewing a file (display) or a directory (listdir)
  url(r'view(?P<path>/.*)', 'filebrowser.views.view', name='view'),
  url(r'chooser(?P<path>/.*)', 'filebrowser.views.chooser', name='view'),
  url(r'edit(?P<path>/.*)', 'filebrowser.views.edit', name='edit'),
  url(r'save', 'filebrowser.views.save_file'),

  # POST operations
  url(r'upload_flash$', 'filebrowser.views.upload_flash', name='upload_flash'),
  url(r'upload$', 'filebrowser.views.upload', name='upload'),
  url(r'rename', 'filebrowser.views.rename', name='rename'),
  url(r'mkdir', 'filebrowser.views.mkdir', name='mkdir'),
  url(r'^move', 'filebrowser.views.move', name='move'),
  url(r'remove', 'filebrowser.views.remove', name='remove'),
  url(r'rmdir', 'filebrowser.views.rmdir', name='rmdir'),
  url(r'rmtree', 'filebrowser.views.rmtree', name='rmtree'),
  url(r'chmod', 'filebrowser.views.chmod', name='chmod'),
  url(r'chown', 'filebrowser.views.chown', name='chown'),
)
