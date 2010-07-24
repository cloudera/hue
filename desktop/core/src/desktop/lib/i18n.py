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
Library methods to deal with non-ascii data
"""

import codecs
import desktop.conf
import logging

SITE_ENCODING = None
REPLACEMENT_CHAR = u'\ufffd'

def get_site_encoding():
  """Get the default site encoding"""
  global SITE_ENCODING
  if SITE_ENCODING is None:
    encoding = desktop.conf.DEFAULT_SITE_ENCODING.get()
    if not validate_encoding(encoding):
      default = desktop.conf.DEFAULT_SITE_ENCODING.config.default_value
      msg = 'Invalid HUE configuration value for %s: "%s". Using default "%s"' % \
                  (desktop.conf.DEFAULT_SITE_ENCODING.config.key, encoding, default)
      logging.error(msg)
      encoding = default
    SITE_ENCODING = encoding
  return SITE_ENCODING

def validate_encoding(encoding):
  """Return True/False on whether the system understands this encoding"""
  try:
    codecs.lookup(encoding)
    return True
  except LookupError:
    return False
