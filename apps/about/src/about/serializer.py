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


class UsageAnalyticsSerializer(serializers.Serializer):
  """Serializes and validates the usage analytics settings data."""

  collectUsage = serializers.BooleanField(required=True, help_text="Indicates whether usage analytics collection is enabled.")
  
  def to_internal_value(self, data):
    """Handle backward compatibility for snake_case field names during transition."""
    if isinstance(data, dict):
      # Create a copy to avoid modifying the original
      data = data.copy()
      # Support legacy snake_case field name during transition
      if 'collect_usage' in data and 'collectUsage' not in data:
        data['collectUsage'] = data.pop('collect_usage')
    return super().to_internal_value(data)
