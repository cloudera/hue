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

from desktop.models import Document2, Document


def _save_pipeline(pipeline, user):
  pipeline_type = pipeline.get('type', 'pipeline')
  save_as = False

  if pipeline.get('parentSavedQueryUuid'): # We save into the original saved query, not into the query history
    pipeline_doc = Document2.objects.get_by_uuid(user=user, uuid=pipeline['parentSavedQueryUuid'])
  elif pipeline.get('id'):
    pipeline_doc = Document2.objects.get(id=pipeline['id'])
  else:
    pipeline_doc = Document2.objects.create(name=pipeline['name'], uuid=pipeline['uuid'], type=pipeline_type, owner=user)
    Document.objects.link(pipeline_doc, owner=pipeline_doc.owner, name=pipeline_doc.name, description=pipeline_doc.description, extra=pipeline_type)
    save_as = True

    if pipeline.get('directoryUuid'):
      pipeline_doc.parent_directory = Document2.objects.get_by_uuid(user=user, uuid=pipeline.get('directoryUuid'), perm_type='write')
    else:
      pipeline_doc.parent_directory = Document2.objects.get_home_directory(user)

  pipeline['isSaved'] = True
  pipeline['isHistory'] = False
  pipeline['id'] = pipeline_doc.id
  pipeline_doc1 = pipeline_doc._get_doc1(doc2_type=pipeline_type)
  pipeline_doc.update_data(pipeline)
  #pipeline_doc.search = _get_statement(pipeline)
  pipeline_doc.name = pipeline_doc1.name = pipeline['name']
  pipeline_doc.description = pipeline_doc1.description = pipeline['description']
  pipeline_doc.save()
  pipeline_doc1.save()

  return pipeline_doc, save_as


FIELD_TYPES = (
  "alphaOnlySort",
  "ancestor_path",
  "boolean",
  "currency",
  "date",
  "descendent_path",
  "double",
  "float",
  "int",
  "location",
  "location_rpt",
  "long",
  "lowercase",
  "pdate",
  "pdouble",
  "pfloat",
  "pint",
  "plong",
  "point",
  "random",
  "string",
  "text_ar",
  "text_bg",
  "text_ca",
  "text_char_norm",
  "text_cjk",
  "text_cz",
  "text_da",
  "text_de",
  "text_el",
  "text_en",
  "text_en_splitting",
  "text_en_splitting_tight",
  "text_es",
  "text_eu",
  "text_fa",
  "text_fi",
  "text_fr",
  "text_ga",
  "text_general",
  "text_general_rev",
  "text_gl",
  "text_greek",
  "text_hi",
  "text_hu",
  "text_hy",
  "text_id",
  "text_it",
  "text_ja",
  "text_lv",
  "text_nl",
  "text_no",
  "text_pt",
  "text_ro",
  "text_ru",
  "text_sv",
  "text_th",
  "text_tr",
  "text_ws"
)

TEXT_FIELD_TYPES = (
  "alphaOnlySort",
  "lowercase",
  "random",
  "string",
  "text_ar",
  "text_bg",
  "text_ca",
  "text_char_norm",
  "text_cjk",
  "text_cz",
  "text_da",
  "text_de",
  "text_el",
  "text_en",
  "text_en_splitting",
  "text_en_splitting_tight",
  "text_es",
  "text_eu",
  "text_fa",
  "text_fi",
  "text_fr",
  "text_ga",
  "text_general",
  "text_general_rev",
  "text_gl",
  "text_greek",
  "text_hi",
  "text_hu",
  "text_hy",
  "text_id",
  "text_it",
  "text_ja",
  "text_lv",
  "text_nl",
  "text_no",
  "text_pt",
  "text_ro",
  "text_ru",
  "text_sv",
  "text_th",
  "text_tr",
  "text_ws"
)

DATE_FIELD_TYPES = (
  "date",
  "pdate"
)

INTEGER_FIELD_TYPES = (
  "int",
  "pint",
  "long",
  "plong"
)

DECIMAL_FIELD_TYPES = (
  "float",
  "pfloat",
  "double",
  "pdouble",
  "currency"
)

BOOLEAN_FIELD_TYPES = (
  'boolean',
)
