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
Utilities for django database operations.
"""

import logging
from django.contrib.contenttypes.models import ContentType

LOG = logging.getLogger(__name__)

def remove_content_type(app_label, model_name):
  """
  Delete from the Django ContentType table, as applications delete
  old unused tables.

  See django.contrib.contenttypes.management.update_contenttypes().
  If applications don't delete their stale content types, users will
  be prompted with a question as they run syncdb.
  """
  try:
    ct = ContentType.objects.get(app_label=app_label,
                                 model=model_name.lower())
    ct.delete()
  except ContentType.DoesNotExist:
    pass
