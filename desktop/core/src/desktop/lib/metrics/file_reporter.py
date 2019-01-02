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
import logging
import os
import tempfile

from pyformance.reporters.reporter import Reporter

from desktop.lib.metrics import global_registry


LOG = logging.getLogger(__name__)


class FileReporter(Reporter):
  def __init__(self, location, *args, **kwargs):
    super(FileReporter, self).__init__(*args, **kwargs)
    self.location = location

  def report_now(self, registry=None, timestamp=None):
    dirname = os.path.dirname(self.location)

    if not os.path.exists(dirname):
      try:
        os.makedirs(dirname)
      except OSError, e:
        LOG.error('failed to make the directory %s: %s' % (dirname, e))
      return

    # Write the metrics to a temporary file, then atomically
    # rename the file to the real location.

    f = tempfile.NamedTemporaryFile(
        dir=dirname,
        delete=False)

    try:
      json.dump(self.registry.dump_metrics(), f)
      f.close()

      os.rename(f.name, self.location)
    except Exception:
      LOG.exception('failed to write metrics to file')
      os.remove(f.name)
      raise

_reporter = None


def start_file_reporter():
  from desktop.conf import METRICS

  global _reporter

  if _reporter is None:
    location = METRICS.LOCATION.get()
    interval = METRICS.COLLECTION_INTERVAL.get()

    if location is not None and interval is not None:
      _reporter = FileReporter(
          location,
          reporting_interval=interval / 1000.0,
          registry=global_registry())
      _reporter.start()
