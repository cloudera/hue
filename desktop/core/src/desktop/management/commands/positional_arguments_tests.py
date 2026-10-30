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
Django only accepts the positional arguments that a command declares, so a command that reads them from `args`
has to declare them in `add_arguments`.
"""

from unittest.mock import patch

import pytest
from django.core.management import call_command, CommandError

from beeswax.management.commands import beeswax_install_examples
from desktop.management.commands import create_proxy_app
from hbase.management.commands import hbase_setup

COMMANDS = [
  ('beeswax_install_examples', beeswax_install_examples, [('hive',), ('impala', 'sample_db')]),
  ('hbase_setup', hbase_setup, [(), ('bob',)]),
  ('create_proxy_app', create_proxy_app, [('my_app',), ('my_app', 'http://localhost:8080'), ('my_app', 'http://localhost:8080', '/tmp')]),
]


@pytest.mark.parametrize('name, module, calls', COMMANDS, ids=[command[0] for command in COMMANDS])
def test_the_positional_arguments_are_passed_to_handle(name, module, calls):
  for positional_arguments in calls:
    with patch.object(module.Command, 'handle', return_value=None) as handle:
      call_command(name, *positional_arguments)

    assert handle.call_args.args == positional_arguments


def test_beeswax_install_examples_requires_a_dialect_from_the_command_line():
  with pytest.raises(CommandError, match='Expected arguments'):
    call_command('beeswax_install_examples')
