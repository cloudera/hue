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

from django.utils.translation import gettext_lazy as _

from desktop.conf import ENABLE_DOWNLOAD, is_oozie_enabled
from desktop.lib.conf import Config, coerce_bool, coerce_csv

MAX_SNAPPY_DECOMPRESSION_SIZE = Config(
  key="max_snappy_decompression_size", help=_("Max snappy decompression size in bytes."), private=True, default=1024 * 1024 * 25, type=int
)

ARCHIVE_UPLOAD_TEMPDIR = Config(
  key="archive_upload_tempdir",
  help=_("Location on local filesystem where the uploaded archives are temporary stored."),
  default="/tmp/hue_uploads",
  type=str,
)

FILE_UPLOAD_CHUNK_SIZE = Config(
  key="file_upload_chunk_size",
  default=5242880,
  type=int,
  help=_('Configure chunk size of the chunked file uploader. Default chunk size is set to 5MB.'),
)

CONCURRENT_MAX_CONNECTIONS = Config(
  key="concurrent_max_connections",
  default=5,
  type=int,
  help=_('Configure the maximum number of concurrent connections(chunks) for file uploads using the chunked file uploader.'),
)


def get_desktop_enable_download():
  """Get desktop enable_download default"""
  return ENABLE_DOWNLOAD.get()


SHOW_DOWNLOAD_BUTTON = Config(
  key="show_download_button",
  help=_("whether to show the download button in hdfs file browser."),
  type=coerce_bool,
  dynamic_default=get_desktop_enable_download,
)

SHOW_UPLOAD_BUTTON = Config(
  key="show_upload_button", help=_("whether to show the upload button in hdfs file browser."), type=coerce_bool, default=True
)

ENABLE_EXTRACT_UPLOADED_ARCHIVE = Config(
  key="enable_extract_uploaded_archive",
  help=_("Flag to enable the extraction of a uploaded archive in HDFS."),
  type=coerce_bool,
  dynamic_default=is_oozie_enabled,
)

REDIRECT_DOWNLOAD = Config(
  key="redirect_download",
  help=_(
    "Redirect client to WebHdfs or S3 for file download. Note: Turning this on will "
    "override notebook/redirect_whitelist for user selected file downloads on WebHdfs & S3."
  ),
  type=coerce_bool,
  default=False,
)

# DEPRECATED in favor of DEFAULT_HOME_PATH per FS config level.
REMOTE_STORAGE_HOME = Config(
  key="remote_storage_home",
  type=str,
  default=None,
  help="Optionally set this if you want a different home directory path. e.g. s3a://gethue.",
)

MAX_FILE_SIZE_UPLOAD_LIMIT = Config(
  key="max_file_size_upload_limit",
  default=-1,
  type=int,
  help=_('A limit on a file size (bytes) that can be uploaded to a filesystem. ' 'A value of -1 means there will be no limit.'),
)


def max_file_size_upload_limit():
  return MAX_FILE_SIZE_UPLOAD_LIMIT.get()


FILE_DOWNLOAD_CACHE_CONTROL = Config(
  key="file_download_cache_control", type=str, default=None, help="Optionally set this to control the caching strategy for files download"
)

RESTRICT_FILE_EXTENSIONS = Config(
  key='restrict_file_extensions',
  default='',
  type=coerce_csv,
  help=_(
    'Specify file extensions that are not allowed, separated by commas. For example: .exe, .zip, .rar, .tar, .gz'
  ),
)
