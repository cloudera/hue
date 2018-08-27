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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2


try:
  from functools import wraps
except ImportError:
  from django.utils.functional import wraps

from desktop.auth.backend import is_admin


LOG = logging.getLogger(__name__)


def hue_permission_required(action, app):
  """
  Checks that the user has permissions to do
  action 'action' on app 'app'.

  Note that user must already be logged in.
  """
  def decorator(view_func):
    @wraps(view_func)
    def decorated(request, *args, **kwargs):
      if not request.user.has_hue_permission(action, app):
        raise PopupException(_("Permission denied (%(action)s/%(app)s).") % {'action': action, 'app': app})
      return view_func(request, *args, **kwargs)
    return decorated
  return decorator


def check_superuser_permission(view_func):
  def decorate(request, *args, **kwargs):
    if not is_admin(request.user):
      raise PopupException(_('You must be a superuser to perform this operation.'), error_code=401)
    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


def check_document_access_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      doc_id = {}

      try:
        if request.GET.get('uuid'):
          doc_id['uuid'] = request.GET.get('uuid')
        elif 'doc_id' in kwargs:
          doc_id['id'] = kwargs['doc_id']

        if doc_id:
          doc2 = Document2.objects.get(**doc_id)
          doc2.doc.get().can_read_or_exception(request.user)
      except Document2.DoesNotExist:
        raise PopupException(_('Job %(id)s does not exist') % {'id': doc_id})

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner
