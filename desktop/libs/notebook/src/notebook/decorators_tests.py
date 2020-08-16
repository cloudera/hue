#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from notebook.decorators import rewrite_ssh_api_url

from nose.tools import assert_equal


def test_rewrite_ssh_api_url():
  assert_equal(
    {
      'server_host': 'ip-172-31-6-77',
      'server_port': '31676',
      'url': 'postgresql://hue:hue@127.0.0.1:31676/hue'
    },
    rewrite_ssh_api_url('postgresql://hue:hue@ip-172-31-6-77:31676/hue')
  )
