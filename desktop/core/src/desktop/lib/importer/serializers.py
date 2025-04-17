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
from rest_framework import serializers


class LocalFileUploadSerializer(serializers.Serializer):
  """Serializer for file upload validation.

  This serializer validates that the uploaded file is present and has an
  acceptable file format and size.

  Attributes:
    file: File field that must be included in the request
  """

  file = serializers.FileField(required=True, help_text="CSV or Excel file to upload and process")

  def validate_file(self, value):
    # Add file format validation
    extension = value.name.split('.')[-1].lower()
    if extension not in ['csv', 'xlsx', 'xls']:
      raise serializers.ValidationError("Unsupported file format. Please upload a CSV or Excel file.")

    # TODO: Check upper limit for file size
    # Add file size validation (e.g., limit to 150 MiB)
    if value.size > 150 * 1024 * 1024:  # 150 MiB in bytes
      raise serializers.ValidationError("File too large. Maximum file size is 150 MiB.")

    return value
