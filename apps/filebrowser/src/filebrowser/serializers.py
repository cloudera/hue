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

from filebrowser.schemas import RenameSchema


class UploadFileSerializer(serializers.Serializer):
  """
  Validates the query parameters for the file upload API.
  """

  destination_path = serializers.CharField(required=True, allow_blank=False)
  overwrite = serializers.BooleanField(default=False)


class RenameSerializer(serializers.Serializer):
  """
  Validates the parameters for the file/directory rename API.
  """

  source_path = serializers.CharField(required=True, allow_blank=False)
  destination_path = serializers.CharField(required=True, allow_blank=False)

  def validate(self, data):
    try:
      RenameSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())

    return data
