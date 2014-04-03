#!/usr/bin/env python
# -- coding: utf-8 --
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

import csv
import logging
import os
import pytz
import re
import shutil
import StringIO
import tempfile
from dateutil.parser import parse

from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode, smart_str

from collectionmanager import conf

LOG = logging.getLogger(__name__)
TIMESTAMP_PATTERN = '\[([\w\d\s\-\/\:\+]*?)\]'
FIELD_XML_TEMPLATE = '<field name="%(name)s" type="%(type)s" indexed="%(indexed)s" stored="%(stored)s" required="%(required)s" />'
DEFAULT_FIELD = {
  'name': None,
  'type': 'text',
  'indexed': 'true',
  'stored': 'true',
  'required': 'true'
}

def schema_xml_with_fields(schema_xml, fields):
  fields_xml = ''
  for field in fields:
    field_dict = DEFAULT_FIELD.copy()
    field_dict.update(field)
    fields_xml += FIELD_XML_TEMPLATE % field_dict + '\n'
  return force_unicode(force_unicode(schema_xml).replace(u'<!-- REPLACE FIELDS -->', force_unicode(fields_xml)))

def schema_xml_with_unique_key_field(schema_xml, unique_key_field):
  return force_unicode(force_unicode(schema_xml).replace(u'<!-- REPLACE UNIQUE KEY -->', force_unicode(unique_key_field)))

def schema_xml_with_fields_and_unique_key(schema_xml, fields, unique_key_field):
  return schema_xml_with_unique_key_field(schema_xml_with_fields(schema_xml, fields), unique_key_field)

def example_schema_xml_with_fields_and_unique_key(fields, unique_key_field):
  # Get complete schema.xml
  with open(os.path.join(conf.CONFIG_TEMPLATE_PATH.get(), 'conf/schema.xml')) as f:
    return schema_xml_with_fields_and_unique_key(f.read(), fields, unique_key_field)

def copy_config_with_fields_and_unique_key(fields, unique_key_field):
  # Get complete schema.xml
  with open(os.path.join(conf.CONFIG_TEMPLATE_PATH.get(), 'conf/schema.xml')) as f:
    schema_xml = schema_xml_with_fields_and_unique_key(f.read(), fields, unique_key_field)

  # Create temporary copy of solr configs
  tmp_path = tempfile.mkdtemp()
  solr_config_path = os.path.join(tmp_path, os.path.basename(conf.CONFIG_TEMPLATE_PATH.get()))
  shutil.copytree(conf.CONFIG_TEMPLATE_PATH.get(), solr_config_path)

  # Write complete schema.xml to copy
  with open(os.path.join(solr_config_path, 'conf/schema.xml'), 'w') as f:
    f.write(smart_str(schema_xml))

  return tmp_path, solr_config_path


def get_field_types(row):
  def test_boolean(value):
    if value.lower() not in ('false', 'true'):
      raise ValueError(_("%s is not a boolean value") % value)

  def test_timestamp(value):
    if not value:
      raise ValueError()

    if len(value) > 50:
      raise ValueError()

    if value.startswith('[') and value.endswith(']'):
      value = value[1:-1]

    try:
      parse(value)
    except:
      raise ValueError()

  test_fns = [('int', int),
              ('float', float),
              ('boolean', test_boolean),
              ('date', test_timestamp)]
  field_types = []
  for field in row:
    field_type = None
    for test_fn in test_fns:
      try:
        test_fn[1](field)
        field_type = test_fn[0]
        break
      except ValueError:
        pass
    field_types.append(field_type or 'text_general')
  return field_types


def get_type_from_morphline_type(morphline_type):
  if morphline_type in ('POSINT', 'INT', 'BASE10NUM', 'NUMBER'):
    return 'integer'
  else:
    return 'string'


def field_values_from_separated_file(fh, delimiter, quote_character):
  csvfile = StringIO.StringIO()
  content = fh.read()
  while content:
    last_newline = content.rfind('\n')
    if last_newline > -1:
      csvfile.write(content[:last_newline])
      content = content[last_newline+1:]
    else:
      csvfile.write(content[:])
      content = ""
    csvfile.seek(0)
    reader = csv.reader(csvfile, delimiter=smart_str(delimiter), quotechar=smart_str(quote_character))
    for row in reader:
      print 'here1'
      yield [cell for cell in row]
      print 'here2'
    
    csvfile.truncate()
    content += fh.read()


def field_values_from_log(fh):
  """
  Only timestamp and message
  """
  csvfile = StringIO.StringIO()
  prev = content = fh.read()
  while prev:
    last_newline = content.rfind('\n')
    if last_newline > -1:
      csvfile.write(content[:last_newline])
      content = content[last_newline:]
      rows = content.split('\n')
      for row in rows:
        if row:
          data = {}
          matches = re.search(TIMESTAMP_PATTERN, row)
          if matches:
            data['timestamp'] = parse(matches.groups()[0]).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
          data['message'] = row
          yield data
    prev = fh.read()
    content += prev


def fields_from_log(fh):
  """
  Only timestamp and message
  """
  rows = fh.read()
  row = rows.split('\n')[0]

  # Extract timestamp
  fields = []
  matches = re.search(TIMESTAMP_PATTERN, row)
  if matches:
    fields.append(('timestamp', 'date'))
  fields.append(('message', 'text_general'))

  return fields
