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
Configuration options for the Shell UI.
This file specifies the structure that hue-shell.ini should follow.
See conf/hue-shell.ini to configure which shells are available.
"""
from desktop.lib.conf import Config, ConfigSection, UnspecifiedConfigSection
import shell.utils as utils

SHELL_TYPES = UnspecifiedConfigSection(
  key='shelltypes',
  each=ConfigSection(
    members=dict(
      nice_name=Config(
        key='nice_name',
        required=True
      ),
      command=Config(
        key='command',
        required=True
      ),
      help_doc=Config(
        key='help',
        required=False
      ),
      environment=UnspecifiedConfigSection(
        key='environment',
        each=ConfigSection(
          members=dict(
            value=Config(
              key='value',
              required=True
            ),
            doc=Config(
              key='doc',
              required=False
            )
          )
        )
      )
    )
  )
)

SHELL_BUFFER_AMOUNT = Config(
  key="shell_buffer_amount",
  help="Configure the number of output characters buffered for each shell",
  default=524288,
  type=int
)

SHELL_TIMEOUT = Config(
  key="shell_timeout",
  help="Number of seconds to keep shells open for users",
  default=600,
  type=int
)

SHELL_WRITE_BUFFER_LIMIT = Config(
  key="shell_write_buffer_limit",
  help="Number of bytes of commands to buffer for users",
  default=10000,
  type=int
)

SHELL_OS_READ_AMOUNT = Config(
  key="shell_os_read_amount",
  help="Number of bytes to read from child subprocess at a time",
  default=40960,
  type=int
)

SHELL_DELEGATION_TOKEN_DIR = Config(
  key="shell_delegation_token_dir",
  help="The directory to store the temporary delegation tokens used by shell subprocesses",
  default="/tmp/hue_shell_delegation_tokens",
  type=str
)

def config_validator():
  """
  config_validator() -> [ (config_variable, error_message) ]

  Called by core check_config() view.
  """
  result = []
  for item in SHELL_TYPES.keys():
    command = SHELL_TYPES[item].command.get().strip().split()
    nice_name = SHELL_TYPES[item].nice_name.get().strip()
    if not utils.executable_exists(command):
      result.append((SHELL_TYPES, "Command '%s' for entry '%s' in Shell app configuration cannot \
                                            be found on the path." % (' '.join(command), item,) ,))
  return result

