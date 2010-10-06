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

import logging
import subprocess
import sys
import time
from desktop.supervisor import DjangoCommandSupervisee
from desktop.conf import KERBEROS as CONF

LOG = logging.getLogger(__name__)

SPEC = DjangoCommandSupervisee("kt_renewer")

def renew_from_kt():
  cmdv = [CONF.KINIT_PATH.get(),
          "-k", # host ticket
          "-t", CONF.HUE_KEYTAB.get(), # specify keytab
          "-c", CONF.CCACHE_PATH.get(), # specify credentials cache
          CONF.HUE_PRINCIPAL.get()]
  LOG.info("Reinitting kerberos from keytab: " +
           " ".join(cmdv))
  ret = subprocess.call(cmdv)
  if ret != 0:
    LOG.error("Couldn't reinit from keytab!")
    sys.exit(ret)

def run():
  if CONF.HUE_KEYTAB.get() is None:
    LOG.debug("Keytab renewer not starting, no keytab configured")
    sys.exit(0)

  while True:
    renew_from_kt()
    time.sleep(CONF.KEYTAB_REINIT_FREQUENCY.get())
