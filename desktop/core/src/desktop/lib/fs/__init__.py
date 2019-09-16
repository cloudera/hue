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

from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from builtins import filter
import posixpath
import sys
import urllib.parse

from desktop.lib.fs.proxyfs import ProxyFS

if sys.version_info[0] > 2:
  from urllib.parse import urlparse as lib_urlparse
else:
  from urlparse import urlparse as lib_urlparse

def splitpath(path):
  split = lib_urlparse(path)
  if split.scheme and split.netloc:
    parts = [split.scheme + '://', split.netloc] + split.path.split('/')
  elif split.scheme and split.path:
    parts = [split.scheme + ':/'] + split.path.split('/')
  elif split.scheme:
    parts = [split.scheme + ("://" if path.find("://") >= 0 else ":/")]
  else:
    parts = ['/'] + posixpath.normpath(path).split('/')
  # Filter empty parts out
  return list(filter(len, parts))




