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

from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import get_cluster_config

from indexer.solr_client import SolrClient
from indexer.fields import FIELD_TYPES, Field
from indexer.file_format import get_file_indexable_format_types
from indexer.management.commands import indexer_setup
from indexer.indexers.morphline_operations import OPERATORS


LOG = logging.getLogger(__name__)


def collections(request, is_redirect=False):
  if not request.user.has_hue_permission(action="access", app='indexer'):
    raise PopupException(_('Missing permission.'), error_code=403)

  return render('collections.mako', request, {
    'is_embeddable': request.GET.get('is_embeddable', False),
  })


def indexes(request, index=''):
  if not request.user.has_hue_permission(action="access", app='indexer'):
    raise PopupException(_('Missing permission.'), error_code=403)

  return render('indexes.mako', request, {
    'is_embeddable': request.GET.get('is_embeddable', False),
    'index': index
  })


def topics(request, index=''):
  if not request.user.has_hue_permission(action="access", app='search'):
    raise PopupException(_('Missing permission.'), error_code=403)

  return render('topics.mako', request, {
    'is_embeddable': request.GET.get('is_embeddable', False),
    'index': index
  })


def indexer(request):
  if not request.user.has_hue_permission(action="access", app='indexer'):
    raise PopupException(_('Missing permission.'), error_code=403)

  searcher = SolrClient(request.user)
  indexes = searcher.get_indexes()

  for index in indexes:
    index['isSelected'] = False

  return render('indexer.mako', request, {
      'is_embeddable': request.GET.get('is_embeddable', False),
      'indexes_json': json.dumps(indexes),
      'fields_json' : json.dumps([field.name for field in FIELD_TYPES]),
      'operators_json' : json.dumps([operator.to_dict() for operator in OPERATORS]),
      'file_types_json' : json.dumps([format_.format_info() for format_ in get_file_indexable_format_types()]),
      'default_field_type' : json.dumps(Field().to_dict())
  })


HIVE_PRIMITIVE_TYPES = \
    ("string", "tinyint", "smallint", "int", "bigint", "boolean",
      "float", "double", "decimal", "timestamp", "date", "char", "varchar")
HIVE_TYPES = HIVE_PRIMITIVE_TYPES + ("array", "map", "struct")


def importer(request):
  prefill = {
    'source_type': '',
    'target_type': '',
    'target_path': ''
  }

  return _importer(request, prefill)


def importer_prefill(request, source_type, target_type, target_path=None):
  prefill = {
    'source_type': source_type,
    'target_type': target_type,
    'target_path': target_path or ''
  }

  return _importer(request, prefill)


def _importer(request, prefill):
  source_type = request.GET.get('sourceType') or get_cluster_config(request.user)['default_sql_interpreter']

  return render('importer.mako', request, {
      'is_embeddable': request.GET.get('is_embeddable', False),
      'fields_json': json.dumps({'solr': [field.name for field in FIELD_TYPES], 'hive': HIVE_TYPES, 'hivePrimitive': HIVE_PRIMITIVE_TYPES}),
      'operators_json': json.dumps([operator.to_dict() for operator in OPERATORS]),
      'file_types_json': json.dumps([format_.format_info() for format_ in get_file_indexable_format_types()]),
      'default_field_type': json.dumps(Field().to_dict()),
      'prefill': json.dumps(prefill),
      'source_type': source_type
  })


def install_examples(request, is_redirect=False):
  result = {'status': -1, 'message': ''}

  if request.method != 'POST':
    result['message'] = _('A POST request is required.')
  else:
    try:
      data = request.POST.get('data')
      indexer_setup.Command().handle(data=data)
      result['status'] = 0
    except Exception, e:
      LOG.exception(e)
      result['message'] = str(e)

  return JsonResponse(result)
