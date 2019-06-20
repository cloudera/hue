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

import json
import urllib

from django.urls import reverse
from django.utils.translation import ugettext as _

from desktop.conf import DEFAULT_USER
from desktop.lib.paths import get_desktop_root, SAFE_CHARACTERS_URI_COMPONENTS

from notebook.connectors.base import Notebook

def compress_files_in_hdfs(request, file_names, upload_path, archive_name):

  _upload_compress_files_script_to_hdfs(request.fs)

  files = [{"value": upload_path + '/' + file_name} for file_name in file_names]
  files.append({'value': '/user/' + DEFAULT_USER.get() + '/common/compress_files_in_hdfs.sh'})
  start_time = json.loads(request.POST.get('start_time', '-1'))

  shell_notebook = Notebook(
    name=_('HDFS Compression to %(upload_path)s/hue_compressed.zip') % {'upload_path': upload_path},
    isManaged=True,
    onSuccessUrl='/filebrowser/view=' + urllib.quote(upload_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
  )

  shell_notebook.add_shell_snippet(
      shell_command='compress_files_in_hdfs.sh',
      arguments=[{'value': '-u=' + upload_path}, {'value': '-f=' + ','.join(file_names)}, {'value': '-n=' + archive_name}],
      archives=[],
      files=files,
      env_var=[{'value': 'HADOOP_USER_NAME=${wf:user()}'}],
      last_executed=start_time
  )

  return shell_notebook.execute(request, batch=True)

def _upload_compress_files_script_to_hdfs(fs):
  if not fs.exists('/user/' + DEFAULT_USER.get() + '/common/'):
    fs.do_as_user(DEFAULT_USER.get(), fs.mkdir, '/user/' + DEFAULT_USER.get() + '/common/')
    fs.do_as_user(DEFAULT_USER.get(), fs.chmod, '/user/' + DEFAULT_USER.get() + '/common/', 0755)

  if not fs.do_as_user(DEFAULT_USER.get(), fs.exists, '/user/' + DEFAULT_USER.get() + '/common/compress_files_in_hdfs.sh'):
    fs.do_as_user(DEFAULT_USER.get(), fs.copyFromLocal, get_desktop_root() + '/core/src/desktop/lib/tasks/compress_files/compress_in_hdfs.sh',
                          '/user/' + DEFAULT_USER.get() + '/common/compress_files_in_hdfs.sh')
    fs.do_as_user(DEFAULT_USER.get(), fs.chmod, '/user/' + DEFAULT_USER.get() + '/common/', 0755)
