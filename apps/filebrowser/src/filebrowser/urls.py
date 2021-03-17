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

import sys

from filebrowser import views as filebrowser_views
from filebrowser import api as filebrowser_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  # Base view
  re_path(r'^$', filebrowser_views.index, name='index'),

  # Catch-all for viewing a file (display) or a directory (listdir)
  re_path(r'^view=(?P<path>.*)$', filebrowser_views.view, name='filebrowser.views.view'),

  re_path(r'^listdir=(?P<path>.*)$', filebrowser_views.listdir, name='listdir'),
  re_path(r'^display=(?P<path>.*)$', filebrowser_views.display, name='display'),
  re_path(r'^stat=(?P<path>.*)$', filebrowser_views.stat, name='stat'),
  re_path(r'^content_summary=(?P<path>.*)$', filebrowser_views.content_summary, name='content_summary'),
  re_path(r'^download=(?P<path>.*)$', filebrowser_views.download, name='filebrowser_views_download'),
  re_path(r'^status$', filebrowser_views.status, name='status'),
  re_path(r'^home_relative_view=(?P<path>.*)$', filebrowser_views.home_relative_view, name='home_relative_view'),
  re_path(r'^edit=(?P<path>.*)$', filebrowser_views.edit, name='filebrowser_views_edit'),

  # POST operations
  re_path(r'^save$', filebrowser_views.save_file, name="filebrowser_views_save_file"),
  re_path(r'^upload/file$', filebrowser_views.upload_file, name='upload_file'),
  re_path(r'^extract_archive', filebrowser_views.extract_archive_using_batch_job, name='extract_archive_using_batch_job'),
  re_path(r'^compress_files', filebrowser_views.compress_files_using_batch_job, name='compress_files_using_batch_job'),
  re_path(r'^trash/restore$', filebrowser_views.trash_restore, name='trash_restore'),
  re_path(r'^trash/purge$', filebrowser_views.trash_purge, name='trash_purge'),
  re_path(r'^rename$', filebrowser_views.rename, name='rename'),
  re_path(r'^mkdir$', filebrowser_views.mkdir, name='mkdir'),
  re_path(r'^touch$', filebrowser_views.touch, name='touch'),
  re_path(r'^move$', filebrowser_views.move, name='move'),
  re_path(r'^copy$', filebrowser_views.copy, name='copy'),
  re_path(r'^set_replication$', filebrowser_views.set_replication, name='set_replication'),
  re_path(r'^rmtree$', filebrowser_views.rmtree, name='rmtree'),
  re_path(r'^chmod$', filebrowser_views.chmod, name='chmod'),
  re_path(r'^chown$', filebrowser_views.chown, name='chown'),
]

# API
urlpatterns += [
  re_path(r'^api/get_filesystems/?', filebrowser_api.get_filesystems, name='get_filesystems'),
]
