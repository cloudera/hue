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

DJANGO_APPS = ['metastore']
NICE_NAME = "Table Browser"
REQUIRES_HADOOP = True
ICON = "metastore/art/icon_metastore_48.png"
MENU_INDEX = 20

IS_URL_NAMESPACED = True

PERMISSION_ACTIONS = (
  ("write", "Allow DDL operations. Need the app access too."),
)
