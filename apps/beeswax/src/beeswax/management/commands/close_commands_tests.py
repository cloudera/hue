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

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command, CommandError

from beeswax.management.commands import close_queries, close_sessions

COMMANDS = [
  ('close_queries', close_queries.Command),
  ('close_sessions', close_sessions.Command),
]


@pytest.mark.parametrize('name, command_class', COMMANDS)
class TestCloseCommandsArguments:
  def parse(self, name, command_class, argv):
    return command_class().create_parser('hue', name).parse_args(argv)

  def test_defaults_to_7_days_and_no_scope(self, name, command_class):
    options = self.parse(name, command_class, [])

    assert options.age_in_days == 7
    assert options.scope is None

  def test_age_in_days(self, name, command_class):
    options = self.parse(name, command_class, ['0'])

    assert options.age_in_days == 0
    assert options.scope is None

  def test_age_in_days_and_all(self, name, command_class):
    options = self.parse(name, command_class, ['3', 'all'])

    assert options.age_in_days == 3
    assert options.scope == 'all'

  def test_rejects_an_unknown_scope(self, name, command_class):
    with pytest.raises(CommandError):
      self.parse(name, command_class, ['3', 'everything'])

  def test_rejects_a_non_numeric_age(self, name, command_class):
    with pytest.raises(CommandError):
      self.parse(name, command_class, ['week'])


class TestCloseCommandsExecution:
  def run_command(self, name, module, model, *args):
    model_objects = MagicMock()
    model_objects.filter.return_value = model_objects
    model_objects.all.return_value = model_objects
    model_objects.__iter__.return_value = iter([])
    model_objects.__len__.return_value = 0
    out = StringIO()

    with patch.object(module, model) as model_class, patch.dict('os.environ', {'HIVE_CONF_DIR': '/tmp'}):
      model_class.objects = model_objects
      model_class.STATE = MagicMock()
      with patch('beeswax.hive_site.reset'), patch('beeswax.hive_site.get_conf'), patch('beeswax.conf.HIVE_CONF_DIR'):
        call_command(name, *args, stdout=out)

    return out.getvalue()

  def test_close_queries_with_the_age_and_all(self):
    output = self.run_command('close_queries', close_queries, 'QueryHistory', '0', 'all')

    assert 'Closing (all=True) HiveServer2 queries older than 0 days' in output

  def test_close_queries_without_arguments(self):
    output = self.run_command('close_queries', close_queries, 'QueryHistory')

    assert 'Closing (all=False) HiveServer2 queries older than 7 days' in output

  def test_close_sessions_with_the_age_and_all(self):
    output = self.run_command('close_sessions', close_sessions, 'Session', '2', 'all')

    assert 'Closing (all=True) HiveServer2 sessions older than 2 days' in output

  def test_close_sessions_without_arguments(self):
    output = self.run_command('close_sessions', close_sessions, 'Session')

    assert 'Closing (all=False) HiveServer2 sessions older than 7 days' in output
