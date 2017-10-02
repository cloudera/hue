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

DJANGO_APPS = ['filebrowser']
NICE_NAME = "File Browser"
REQUIRES_HADOOP = False
ICON = "filebrowser/art/icon_filebrowser_48.png"
MENU_INDEX = 20

from aws.s3.s3fs import PERMISSION_ACTION_S3
from azure.adls.webhdfs import PERMISSION_ACTION_ADLS


PERMISSION_ACTIONS = (
  (PERMISSION_ACTION_S3, "Access to S3 from filebrowser and filepicker."),
  (PERMISSION_ACTION_ADLS, "Access to ADLS from filebrowser and filepicker.")
)
