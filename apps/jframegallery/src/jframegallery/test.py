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

"""
Tests for jframegallery
"""

import logging
import os
import os.path

from nose.tools import assert_equals, assert_true
from desktop.lib.django_test_util import make_logged_in_client

LOG = logging.getLogger(__name__)
CWD = os.path.dirname(__file__)



"""
def _get_all_gallery_files():
  Return a list of files in the gallery directory
  gallery_dir = os.path.join(CWD, 'templates', 'gallery')
  return os.listdir(gallery_dir)


def test_galleries():
  cli = make_logged_in_client()
  resp = cli.get('/jframegallery/')

  # Hit index. Make sure that all the galleries are there
  all_files = resp.context['files']
  all_paths = [ f['filename'] for f in all_files ]
  all_paths.sort()

  assert_true('gallery/html-table.html' in all_paths)
  assert_true('gallery/errors.html' in all_paths)
  assert_true('gallery/fit.text.(table).html' in all_paths)
  assert_true('gallery/partial_refresh.mako' in all_paths)

  # Hit all views
  for path in all_paths:
    LOG.debug('Testing %s' % (path,))
    demo_url = '/jframegallery/gallery/' + os.path.basename(path)
    source_url = '/jframegallery/source/' + os.path.basename(path)

    # Check that the demo renders
    cli.get(demo_url)

    # Check that the source renders
    cli.get(source_url)
"""
