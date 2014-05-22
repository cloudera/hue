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

from django.conf import settings
from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode, smart_str

from indexer import conf
from indexer.models import DATE_FIELD_TYPES, TEXT_FIELD_TYPES, INTEGER_FIELD_TYPES,\
                           DECIMAL_FIELD_TYPES, BOOLEAN_FIELD_TYPES

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

    if len(value) > 50 or len(value) < 3:
      raise ValueError()

    if value.startswith('[') and value.endswith(']'):
      value = value[1:-1]

    try:
      parse(value)
    except:
      raise ValueError()

  def test_int(value):
    if len(bin(int(value))) - 2 > 32:
      raise ValueError()

  def test_string(value):
    if len(smart_str(value).split(' ')) > 4:
      raise ValueError()

  test_fns = [('tint', test_int),
              ('tlong', int),
              ('tdouble', float),
              ('boolean', test_boolean),
              ('tdate', test_timestamp),
              ('string', test_string)]
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


def field_values_from_separated_file(fh, delimiter, quote_character, fields=None):
  if fields is None:
    field_names = None
  else:
    field_names = [field['name'] for field in fields]

  if fields is None:
    timestamp_fields = None
  else:
    timestamp_fields = [field['name'] for field in fields if field['type'] in DATE_FIELD_TYPES]

  if fields is None:
    integer_fields = None
  else:
    integer_fields = [field['name'] for field in fields if field['type'] in INTEGER_FIELD_TYPES]

  if fields is None:
    decimal_fields = None
  else:
    decimal_fields = [field['name'] for field in fields if field['type'] in DECIMAL_FIELD_TYPES]

  if fields is None:
    boolean_fields = None
  else:
    boolean_fields = [field['name'] for field in fields if field['type'] in BOOLEAN_FIELD_TYPES]

  content = fh.read()
  headers = None
  while content:
    last_newline = content.rfind('\n')
    if last_newline > -1:
      # If new line is quoted, skip this iteration and try again.
      if content[:last_newline].count('"') % 2 != 0:
        content += fh.read()
        continue
      else:
        if headers is None:
          csvfile = StringIO.StringIO(content[:last_newline])
        else:
          csvfile = StringIO.StringIO('\n' + content[:last_newline])
        content = content[last_newline+1:] + fh.read()
    else:
      if headers is None:
        csvfile = StringIO.StringIO(content)
      else:
        csvfile = StringIO.StringIO('\n' + content)
      content = fh.read()

    # First line is headers
    if headers is None:
      headers = next(csv.reader(csvfile, delimiter=smart_str(delimiter), quotechar=smart_str(quote_character)))

    # User dict reader
    reader = csv.DictReader(csvfile, fieldnames=headers, delimiter=smart_str(delimiter), quotechar=smart_str(quote_character))

    remove_keys = None
    for row in reader:
      # Remove keys that aren't in collection
      if remove_keys is None:
        if field_names is None:
          remove_keys = []
        else:
          remove_keys = set(row.keys()) - set(field_names)
      if remove_keys:
        for key in remove_keys:
          del row[key]

      # Parse dates
      if timestamp_fields:
        tzinfo = pytz.timezone(settings.TIME_ZONE)
        for key in timestamp_fields:
          if key in row:
            dt = parse(row[key])
            if not dt.tzinfo:
              dt = tzinfo.localize(dt)
            row[key] = dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

      # Parse decimal
      if decimal_fields:
        for key in decimal_fields:
          if key in row:
            row[key] = float(row[key])

      # Parse integer
      if integer_fields:
        for key in integer_fields:
          if key in row:
            row[key] = int(row[key])

      # Parse boolean
      if boolean_fields:
        for key in boolean_fields:
          if key in row:
            row[key] = str(row[key]).lower() == "true"

      yield row


def field_values_from_log(fh, fields=[ {'name': 'message', 'type': 'text_general'}, {'name': 'tdate', 'type': 'timestamp'} ]):
  """
  Only timestamp and message
  """
  buf = ""
  prev = content = fh.read()
  if fields is None:
    timestamp_key = 'timestamp'
    message_key = 'message'
  else:
    try:
      timestamp_key = next(iter(filter(lambda field: field['type'] in DATE_FIELD_TYPES, fields)))['name']
    except:
      timestamp_key = None
    try:
      message_key = next(iter(filter(lambda field: field['type'] in TEXT_FIELD_TYPES, fields)))['name']
    except:
      message_key = None

  def value_generator(buf):
    rows = buf.split('\n')
    for row in rows:
      if row:
        data = {}
        matches = re.search(TIMESTAMP_PATTERN, row)
        if matches and timestamp_key:
          data[timestamp_key] = parse(matches.groups()[0]).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        if message_key:
          data[message_key] = row
        yield data

  while prev:
    last_newline = content.rfind('\n')
    if last_newline > -1:
      buf = content[:last_newline]
      content = content[last_newline+1:]
      for row in value_generator(buf):
        yield row
    prev = fh.read()
    content += prev

  if content:
    for row in value_generator(content):
      yield row


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
    fields.append(('timestamp', 'tdate'))
  fields.append(('message', 'text_general'))

  return fields
