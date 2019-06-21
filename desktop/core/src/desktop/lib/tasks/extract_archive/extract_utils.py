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


def extract_archive_in_hdfs(request, upload_path, file_name):
  _upload_extract_archive_script_to_hdfs(request.fs)

  output_path = upload_path + '/' + file_name.split('.')[0]
  start_time = json.loads(request.POST.get('start_time', '-1'))

  shell_notebook = Notebook(
      name=_('HDFS Extraction of %(upload_path)s/%(file_name)s') % {'upload_path': upload_path, 'file_name': file_name},
      isManaged=True,
      onSuccessUrl='/filebrowser/view=' + urllib.quote(output_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
  )

  shell_notebook.add_shell_snippet(
      shell_command='extract_archive_in_hdfs.sh',
      arguments=[{'value': '-u=' + upload_path}, {'value': '-f=' + file_name}, {'value': '-o=' + output_path}],
      archives=[],
      files=[{'value': '/user/' + DEFAULT_USER.get() + '/common/extract_archive_in_hdfs.sh'}, {"value": upload_path + '/' + urllib.quote(file_name)}],
      env_var=[{'value': 'HADOOP_USER_NAME=${wf:user()}'}],
      last_executed=start_time
  )

  return shell_notebook.execute(request, batch=True)


def _upload_extract_archive_script_to_hdfs(fs):
  if not fs.exists('/user/' + DEFAULT_USER.get() + '/common/'):
    fs.do_as_user(DEFAULT_USER.get(), fs.mkdir, '/user/' + DEFAULT_USER.get() + '/common/')
    fs.do_as_user(DEFAULT_USER.get(), fs.chmod, '/user/' + DEFAULT_USER.get() + '/common/', 0755)

  if not fs.do_as_user(DEFAULT_USER.get(), fs.exists, '/user/' + DEFAULT_USER.get() + '/common/extract_archive_in_hdfs.sh'):
    fs.do_as_user(DEFAULT_USER.get(), fs.copyFromLocal, get_desktop_root() + '/core/src/desktop/lib/tasks/extract_archive/extract_in_hdfs.sh',
                          '/user/' + DEFAULT_USER.get() + '/common/extract_archive_in_hdfs.sh')
    fs.do_as_user(DEFAULT_USER.get(), fs.chmod, '/user/' + DEFAULT_USER.get() + '/common/', 0755)
