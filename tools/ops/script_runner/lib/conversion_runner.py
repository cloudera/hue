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

import time
import logging
from django.contrib.auth.models import User
from hue_converters import DocumentConverterHueScripts

LOG = logging.getLogger(__name__)

class DocumentConversionRunner(object):
  """
  Given a user, converts any existing Document objects to Document2 objects
  """

  def __init__(self, usernames, allowdupes=False, startqueryname=None, startuser=None):
    self.usernames = usernames
    self.allowdupes = allowdupes
    self.startqueryname = startqueryname
    self.startuser = startuser


  def runconversions(self):
    if not self.usernames:
      users = User.objects.all()
    else:
      userlist = self.usernames.split(",")
      users = User.objects.filter(username__in = userlist)

    if self.startqueryname or self.startuser:
      processdocs = False
    else:
      processdocs = True

    LOG.info("Converting docs for %s users" % users.count())
    for user in users:

      LOG.info("Converting docs for user: %s" % user.username)
      if user.username == self.startuser:
        processdocs = True

      start = time.time()

      try:
        converter = DocumentConverterHueScripts(user, allowdupes = self.allowdupes, startqueryname = self.startqueryname, startuser = self.startuser, processdocs = processdocs)
        processdocs = converter.convertfailed()
      except:
        LOG.warn("Conversions failed for user: %s" % user.username)
      end = time.time()
      elapsed = (end - start) / 60
      LOG.info("Finished user: %s : elapsed time: %s" % (user.username, elapsed))



