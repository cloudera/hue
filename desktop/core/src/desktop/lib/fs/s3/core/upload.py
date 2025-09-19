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

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException

from desktop.lib.fs.s3.conf_utils import get_default_connector
from desktop.lib.fs.s3.core.path import S3Path
from desktop.lib.fs.s3.core.s3fs import make_s3_client
from filebrowser.utils import is_file_upload_allowed

LOG = logging.getLogger()

# Default chunk size for uploads
DEFAULT_WRITE_SIZE = 1024 * 1024 * 8  # 8MiB


class S3ConnectorUploadError(UploadFileException):
  """Exception for S3 Storage Connector upload errors"""

  pass


class S3ConnectorUploadHandler(FileUploadHandler):
  """
  Modern S3 upload handler using Storage Connector system with boto3.

  This handler:
  - Uses the new Storage Connector configuration system
  - Leverages boto3 for reliable multipart uploads
  - Streams data chunks directly to S3 without local storage
  - Supports all S3-compatible providers (AWS, NetApp, Dell, etc.)
  """

  def __init__(self, request):
    super(S3ConnectorUploadHandler, self).__init__(request)
    self.chunk_size = DEFAULT_WRITE_SIZE
    self.destination = request.GET.get("dest", None)  # GET param avoids infinite looping
    self.target_path = None
    self.file = None
    self._request = request
    self._multipart_upload = None
    self._part_num = 1
    self._upload_rejected = False
    self._parts = []  # Track uploaded parts for completion

    if self._is_s3_upload():
      # Use Storage Connector system to get S3FileSystem
      connector_id = self._get_connector_id_for_upload()
      self._s3fs = make_s3_client(connector_id, request.user.username)

      # Parse destination path
      self._s3path = S3Path.from_path(self.destination)

      # Validate destination exists and we have write access
      self._validate_destination()

  def _get_connector_id_for_upload(self) -> str:
    """
    Get appropriate connector ID for this upload.
    Uses smart defaulting to pick the best connector.
    """
    # TODO: In the future, we could extract connector from the destination path or request params
    # For now, use the default connector selection
    return get_default_connector()

  def _validate_destination(self) -> None:
    """Validate that we can upload to the destination"""
    try:
      if not self._s3fs.check_access(self.destination, permission="WRITE"):
        raise S3ConnectorUploadError(f"Cannot write to destination: {self.destination}")

    except Exception as e:
      LOG.error(f"Upload destination validation failed: {e}")
      raise S3ConnectorUploadError(f"Invalid upload destination: {e}")

  def new_file(self, field_name, file_name, *args, **kwargs):
    """Initialize new file upload"""
    if self._is_s3_upload():
      LOG.info(f"Using S3ConnectorUploadHandler for file upload: {file_name}")

      # Check file extension restrictions
      is_allowed, err_message = is_file_upload_allowed(file_name)
      if not is_allowed:
        LOG.error(f"File upload rejected: {err_message}")
        self._request.META["upload_failed"] = err_message
        self._upload_rejected = True
        return None

      super(S3ConnectorUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

      # Build target path using S3Path.join() for proper slash handling
      target_s3path = self._s3path.join(file_name)
      self.target_path = str(target_s3path)

      try:
        # Initiate multipart upload using boto3
        LOG.debug(f"Initiating boto3 multipart upload to: {self.target_path}")

        response = self._s3fs.s3_client.create_multipart_upload(Bucket=target_s3path.bucket, Key=target_s3path.key)

        self._multipart_upload = {"UploadId": response["UploadId"], "Bucket": target_s3path.bucket, "Key": target_s3path.key}

        LOG.debug(f"Multipart upload initiated: UploadId={response['UploadId']}")

        self.file = SimpleUploadedFile(name=file_name, content="")
      except Exception as e:
        LOG.error(f"Failed to initiate S3 multipart upload: {e}")
        self._request.META["upload_failed"] = str(e)
        raise StopUpload()

      raise StopFutureHandlers()

  def receive_data_chunk(self, raw_data, start):
    """Receive and upload data chunk"""
    if self._upload_rejected:
      return None

    if self._is_s3_upload():
      try:
        LOG.debug(f"Uploading part {self._part_num}, size: {len(raw_data)} bytes")

        # Upload part using boto3
        response = self._s3fs.s3_client.upload_part(
          Bucket=self._multipart_upload["Bucket"],
          Key=self._multipart_upload["Key"],
          PartNumber=self._part_num,
          UploadId=self._multipart_upload["UploadId"],
          Body=raw_data,
        )

        # Track uploaded part for completion
        self._parts.append({"ETag": response["ETag"], "PartNumber": self._part_num})

        self._part_num += 1
        return None

      except Exception as e:
        LOG.error(f"Failed to upload part {self._part_num}: {e}")
        self._abort_multipart_upload()
        raise StopUpload()
    else:
      return raw_data

  def file_complete(self, file_size):
    """Complete the multipart upload"""
    if self._upload_rejected:
      return None

    if self._is_s3_upload():
      try:
        LOG.info(f"Completing multipart upload: {self.target_path}, size: {file_size} bytes")

        # Complete multipart upload
        self._s3fs.s3_client.complete_multipart_upload(
          Bucket=self._multipart_upload["Bucket"],
          Key=self._multipart_upload["Key"],
          UploadId=self._multipart_upload["UploadId"],
          MultipartUpload={"Parts": self._parts},
        )

        LOG.info(f"S3 upload completed successfully: {self.target_path}")

        self.file.size = file_size
        return self.file

      except Exception as e:
        LOG.error(f"Failed to complete S3 multipart upload: {e}")
        self._abort_multipart_upload()
        raise StopUpload()
    else:
      return None

  def _abort_multipart_upload(self):
    """Abort multipart upload on error"""
    try:
      if self._multipart_upload:
        LOG.warning(f"Aborting multipart upload: {self._multipart_upload['UploadId']}")

        self._s3fs.s3_client.abort_multipart_upload(
          Bucket=self._multipart_upload["Bucket"], Key=self._multipart_upload["Key"], UploadId=self._multipart_upload["UploadId"]
        )

    except Exception as e:
      LOG.error(f"Failed to abort multipart upload: {e}")

  def _is_s3_upload(self):
    """Check if this is an S3 upload based on destination scheme"""
    return self._get_scheme() and self._get_scheme().startswith("S3")

  def _get_scheme(self):
    """Extract scheme from destination path"""
    if self.destination:
      if "://" in self.destination:
        return self.destination.split("://")[0].upper()
    return None
