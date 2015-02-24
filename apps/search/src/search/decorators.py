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
import json

from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException

from search.models import Collection
from search.search_controller import SearchController


LOG = logging.getLogger(__name__)


def allow_viewer_only(view_func):
  def decorate(request, *args, **kwargs):

    collection_json = json.loads(request.POST.get('collection', '{}'))

    if collection_json['id']:
      try:
        SearchController(request.user).get_search_collections().get(id=collection_json['id'])
      except Collection.DoesNotExist:
        message = _("Dashboard does not exist or you don't have the permission to access it.")
        raise PopupException(message)

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


def allow_owner_only(view_func):
  def decorate(request, *args, **kwargs):

    collection_json = json.loads(request.POST.get('collection', '{}'))

    if collection_json['id']:
      try:
        collection = Collection.objects.get(id=collection_json['id'])

        if collection.owner != request.user and not request.user.is_superuser:
          message = _("Permission denied. You are not an Administrator.")
          raise PopupException(message)
      except Collection.DoesNotExist:
        pass

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)
