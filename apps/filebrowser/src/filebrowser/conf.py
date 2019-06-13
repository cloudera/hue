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

from django.utils.translation import ugettext_lazy as _

from desktop.conf import ENABLE_DOWNLOAD
from desktop.lib.conf import Config, coerce_bool
from desktop.conf import is_oozie_enabled


MAX_SNAPPY_DECOMPRESSION_SIZE = Config(
  key="max_snappy_decompression_size",
  help=_("Max snappy decompression size in bytes."),
  private=True,
  default=1024*1024*25,
  type=int)

ARCHIVE_UPLOAD_TEMPDIR = Config(
  key="archive_upload_tempdir",
  help=_("Location on local filesystem where the uploaded archives are temporary stored."),
  default=None,
  type=str)

def get_desktop_enable_download():
  """Get desktop enable_download default"""
  return ENABLE_DOWNLOAD.get()

SHOW_DOWNLOAD_BUTTON = Config(
  key="show_download_button",
  help=_("whether to show the download button in hdfs file browser."),
  type=coerce_bool,
  dynamic_default=get_desktop_enable_download)

SHOW_UPLOAD_BUTTON = Config(
  key="show_upload_button",
  help=_("whether to show the upload button in hdfs file browser."),
  type=coerce_bool,
  default=True)


ENABLE_EXTRACT_UPLOADED_ARCHIVE = Config(
  key="enable_extract_uploaded_archive",
  help=_("Flag to enable the extraction of a uploaded archive in HDFS."),
  type=bool,
  dynamic_default=is_oozie_enabled
)

REDIRECT_DOWNLOAD = Config(
  key="redirect_download",
  help=_(
    'Redirect client to WebHdfs or S3 for file download. Note: Turning this on will override notebook/redirect_whitelist for user selected file downloads on WebHdfs & S3.'),
  type=coerce_bool,
  default=False)