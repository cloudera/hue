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

from notebook.decorators import rewrite_ssh_api_url, build_ssh_command

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

  assert_equal(
    {
      'server_host': 'ip-10-0-135-100',
      'server_port': '31006',
      'url': 'phoenix://127.0.0.1:31006'
    },
    rewrite_ssh_api_url('phoenix://ip-10-0-135-100:31006')
  )


def test_build_ssh_command():
  assert_equal(
    'ssh -f -L 10000:172.18.0.5:10000 ubuntu@ec2-3-133-116-35.us-east-2.compute.amazonaws.com -o ExitOnForwardFailure=yes -4 '
    '-o StrictHostKeyChecking=no sleep 1000',
    build_ssh_command({
      'options': {
        'ssh_server_host': 'ubuntu@ec2-3-133-116-35.us-east-2.compute.amazonaws.com',
        'server_host': '172.18.0.5',
        'server_port': '10000',
        'is_llap': False,
        'has_ssh': True,
        'url': 'postgresql://hue:hue@127.0.0.1:31676/hue',
        'idle_time': 1000
      },
      'interface': 'hive',
    }),
  )
