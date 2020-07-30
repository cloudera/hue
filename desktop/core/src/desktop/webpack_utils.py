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

from django.conf import settings
from webpack_loader.exceptions import WebpackError, WebpackLoaderTimeoutError
from webpack_loader.utils import get_loader

def get_hue_bundles(app_name, config='DEFAULT'):
  '''
  Util function to get all bundles related to app_name including vendor bundles
  similar to get_bundle in https://github.com/owais/django-webpack-loader/blob/master/webpack_loader/loader.py
  '''
  loader = get_loader(config)
  assets = loader.get_assets()

  if settings.DEBUG and assets.get('status') == 'compiling':
    timeout = loader.config['TIMEOUT'] or 0
    timed_out = False
    start = time.time()

    while assets.get('status') == 'compiling' and not timed_out:
      time.sleep(loader.config['POLL_INTERVAL'])
      if timeout and (time.time() - timeout > start):
        timed_out = True
      assets = loader.get_assets()

    if timed_out:
      raise WebpackLoaderTimeoutError(
        "Timed Out. Bundles for `{0}` took more than {1} seconds "
        "to compile.".format(app_name, timeout)
      )

  chunks = []
  if assets.get('status') == 'done':
    chunks = [chunk for chunk in assets['chunks'] if
              chunk.startswith(app_name) or
              chunk.startswith('vendors~' + app_name) or
              (not chunk.startswith('hue') and not chunk.startswith('vendors~hue') and app_name in chunk)]
    if not chunks:
      raise WebpackError("Failed to find bundles for `{0}` in config `{1}`".format(app_name, config))

  return chunks
