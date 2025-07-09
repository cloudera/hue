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

from pydantic import ValidationError
from rest_framework import serializers

from filebrowser.schemas import SimpleFileUploadSchema


class SimpleFileUploadSerializer(serializers.Serializer):

  file = serializers.FileField(required=True, help_text="File to upload")
  destination_path = serializers.CharField(required=True, help_text="Destination path for the file")
  overwrite = serializers.BooleanField(default=False, help_text="Whether to overwrite existing file")

  def validate(self, data):
    try:
      schema_data = {
        "file": data["file"],
        "filename": data["file"].name,
        "filesize": data["file"].size,
        "destination_path": data["destination_path"],
        "overwrite": data["overwrite"],
      }
      return SimpleFileUploadSchema.model_validate(schema_data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
