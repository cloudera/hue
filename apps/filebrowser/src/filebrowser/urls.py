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

from django.conf.urls import url
from filebrowser import views as filebrowser_views
from filebrowser import api as filebrowser_api

urlpatterns = [
  # Base view
  url(r'^$', filebrowser_views.index, name='index'),

  # Catch-all for viewing a file (display) or a directory (listdir)
  url(r'^view=(?P<path>.*)$', filebrowser_views.view, name='filebrowser.views.view'),

  url(r'^listdir=(?P<path>.*)$', filebrowser_views.listdir, name='listdir'),
  url(r'^display=(?P<path>.*)$', filebrowser_views.display, name='display'),
  url(r'^stat=(?P<path>.*)$', filebrowser_views.stat, name='stat'),
  url(r'^content_summary=(?P<path>.*)$', filebrowser_views.content_summary, name='content_summary'),
  url(r'^download=(?P<path>.*)$', filebrowser_views.download, name='filebrowser_views_download'),
  url(r'^status$', filebrowser_views.status, name='status'),
  url(r'^home_relative_view=(?P<path>.*)$', filebrowser_views.home_relative_view, name='home_relative_view'),
  url(r'^edit=(?P<path>.*)$', filebrowser_views.edit, name='filebrowser_views_edit'),

  # POST operations
  url(r'^save$', filebrowser_views.save_file, name="filebrowser_views_save_file"),
  url(r'^upload/file$', filebrowser_views.upload_file, name='upload_file'),
  url(r'^extract_archive', filebrowser_views.extract_archive_using_batch_job, name='extract_archive_using_batch_job'),
  url(r'^compress_files', filebrowser_views.compress_files_using_batch_job, name='compress_files_using_batch_job'),
  url(r'^trash/restore$', filebrowser_views.trash_restore, name='trash_restore'),
  url(r'^trash/purge$', filebrowser_views.trash_purge, name='trash_purge'),
  url(r'^rename$', filebrowser_views.rename, name='rename'),
  url(r'^mkdir$', filebrowser_views.mkdir, name='mkdir'),
  url(r'^touch$', filebrowser_views.touch, name='touch'),
  url(r'^move$', filebrowser_views.move, name='move'),
  url(r'^copy$', filebrowser_views.copy, name='copy'),
  url(r'^set_replication$', filebrowser_views.set_replication, name='set_replication'),
  url(r'^rmtree$', filebrowser_views.rmtree, name='rmtree'),
  url(r'^chmod$', filebrowser_views.chmod, name='chmod'),
  url(r'^chown$', filebrowser_views.chown, name='chown'),
]

# API
urlpatterns += [
  url(r'^api/get_filesystems/?', filebrowser_api.get_filesystems, name='get_filesystems'),
]
