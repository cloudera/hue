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
import uuid

from dateutil.parser import parse

from django.conf import settings
from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode, smart_str

from indexer import conf
from indexer.models import DATE_FIELD_TYPES, TEXT_FIELD_TYPES, INTEGER_FIELD_TYPES, DECIMAL_FIELD_TYPES, BOOLEAN_FIELD_TYPES


LOG = logging.getLogger(__name__)
TIMESTAMP_PATTERN = '\[([\w\d\s\-\/\:\+]*?)\]'
FIELD_XML_TEMPLATE = '<field name="%(name)s" type="%(type)s" indexed="%(indexed)s" stored="%(stored)s" required="%(required)s" multiValued="%(multiValued)s" />'
DEFAULT_FIELD = {
  'name': None,
  'type': 'text',
  'indexed': 'true',
  'stored': 'true',
  'required': 'false',
  'multiValued': 'false'
}


def get_config_template_path(solr_cloud_mode):
  if solr_cloud_mode:
    return os.path.join(conf.CONFIG_TEMPLATE_PATH.get(), 'solrcloud')
  else:
    return os.path.join(conf.CONFIG_TEMPLATE_PATH.get(), 'nonsolrcloud')


class SchemaXml(object):

  def __init__(self, xml):
    self.xml = xml
    self.unique_key_field = None

  def uniqueKeyField(self, unique_key_field):
    self.unique_key_field = unique_key_field
    self.xml = force_unicode(force_unicode(self.xml).replace(u'<!-- REPLACE UNIQUE KEY -->', force_unicode(unique_key_field)))

  def fields(self, fields):
    fields_xml = ''
    for field in fields:
      field_dict = DEFAULT_FIELD.copy()
      field_dict.update(field)
      if self.unique_key_field == field['name']:
        field_dict['required'] = 'true'
      fields_xml += FIELD_XML_TEMPLATE % field_dict + '\n'
    self.xml = force_unicode(force_unicode(self.xml).replace(u'<!-- REPLACE FIELDS -->', force_unicode(fields_xml)))


class SolrConfigXml(object):

  def __init__(self, xml):
    self.xml = xml

  def defaultField(self, df=None):
    self.xml = force_unicode(force_unicode(self.xml).replace(u'<str name="df">text</str>', u'<str name="df">%s</str>' % force_unicode(df) if df is not None else ''))


def copy_configs(fields, unique_key_field, df, solr_cloud_mode=True, is_solr_six_or_more=False, is_solr_hdfs_mode=True, is_sentry_protected=False):
  # Create temporary copy of solr configs
  tmp_path = tempfile.mkdtemp()

  try:
    config_template_path = get_config_template_path(solr_cloud_mode)

    solr_config_path = os.path.join(tmp_path, 'solr_configs')
    shutil.copytree(config_template_path, solr_config_path)

    if fields or unique_key_field:
      # Get complete schema.xml
      with open(os.path.join(config_template_path, 'conf/schema.xml')) as f:
        schemaxml = SchemaXml(f.read())
        schemaxml.uniqueKeyField(unique_key_field)
        schemaxml.fields(fields)

      # Write complete schema.xml to copy
      with open(os.path.join(solr_config_path, 'conf/schema.xml'), 'w') as f:
        f.write(smart_str(schemaxml.xml))

    # Use template depending on type of Solr
    solr_config_name = 'solrconfig.xml'

    if is_solr_six_or_more:
      if is_solr_hdfs_mode:
        solr_config_name = 'solrconfig.xml.solr6'
      else:
        solr_config_name = 'solrconfig.xml.solr6NonHdfs'

    if is_sentry_protected:
      solr_config_name += '.secure'

    solrconfig = 'conf/%s' % solr_config_name

    # Get complete solrconfig.xml
    with open(os.path.join(config_template_path, solrconfig)) as f:
      solrconfigxml = SolrConfigXml(f.read())
      solrconfigxml.defaultField(df)

    with open(os.path.join(solr_config_path, 'conf/solrconfig.xml'), 'w') as f:
      f.write(smart_str(solrconfigxml.xml))
    return tmp_path, solr_config_path
  except Exception:
    # Don't leak the tempdir if there was an exception.
    shutil.rmtree(tmp_path)
    raise


def get_field_types(field_list, iterations=3):
  assert iterations > 0, "iterations should be a positive integer (not a negative integer or 0)"

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
    except OverflowError:
      raise ValueError()

  def test_int(value):
    if len(bin(int(value))) - 2 > 32:
      raise ValueError()

  def test_string(value):
    if len(smart_str(value).split(' ')) > 4:
      raise ValueError()

  test_fns = [('boolean', test_boolean),
              ('pint', test_int),
              ('plong', int),
              ('pdouble', float),
              ('pdate', test_timestamp),
              ('string', test_string),
              ('text_general', any)]
  all_field_types = []
  for row in field_list:
    # Try 'iterations' amount of times
    if iterations == 0:
      break

    iterations -= 1

    row_field_types = []
    for field in row:
      field_type_index = None
      for index in range(0, len(test_fns)):
        try:
          test_fns[index][1](field)
          field_type_index = index
          break
        except ValueError:
          pass
      row_field_types.append(field_type_index)
    all_field_types.append(row_field_types)

  # No rows to asses
  if not all_field_types:
    return []

  # Choose based on priority.
  # If a column has largely tint's, but one tlong, then the type should be tlong.
  final_field_types = all_field_types[0]
  for row_field_types in all_field_types:
    for index in range(0, len(row_field_types)):
      if row_field_types[index] > final_field_types[index]:
        final_field_types[index] = row_field_types[index]

  return [test_fns[index][0] for index in final_field_types]


def get_type_from_morphline_type(morphline_type):
  if morphline_type in ('POSINT', 'INT', 'BASE10NUM', 'NUMBER'):
    return 'integer'
  else:
    return 'string'


def field_values_from_separated_file(fh, delimiter, quote_character, fields=None):
  if fields is None:
    field_names = None
  else:
    field_names = [field['name'].strip() for field in fields]

  if fields is None:
    timestamp_fields = None
  else:
    timestamp_fields = [field['name'].strip() for field in fields if field['type'] in DATE_FIELD_TYPES]

  if fields is None:
    integer_fields = None
  else:
    integer_fields = [field['name'].strip() for field in fields if field['type'] in INTEGER_FIELD_TYPES]

  if fields is None:
    decimal_fields = None
  else:
    decimal_fields = [field['name'].strip() for field in fields if field['type'] in DECIMAL_FIELD_TYPES]

  if fields is None:
    boolean_fields = None
  else:
    boolean_fields = [field['name'].strip() for field in fields if field['type'] in BOOLEAN_FIELD_TYPES]

  content = fh.read()
  headers = None

  while content:
    last_newline = content.rfind('\n')
    if last_newline > -1:
      next_chunk = fh.read()
      # If new line is quoted, skip this iteration and try again.
      if content[last_newline - 1] == '"' and next_chunk:
        content += next_chunk
        continue
      else:
        if headers is None:
          csvfile = StringIO.StringIO(content[:last_newline])
        else:
          csvfile = StringIO.StringIO('\n' + content[:last_newline])
        content = content[last_newline + 1:] + next_chunk
    else:
      if headers is None:
        csvfile = StringIO.StringIO(content)
      else:
        csvfile = StringIO.StringIO('\n' + content)
      content = fh.read()

    # First line is headers
    if headers is None:
      headers = next(csv.reader(csvfile, delimiter=smart_str(delimiter), quotechar=smart_str(quote_character)))
      headers = [name.strip() for name in headers]

    # User dict reader
    reader = csv.DictReader(csvfile, fieldnames=headers, delimiter=smart_str(delimiter), quotechar=smart_str(quote_character))

    remove_keys = None
    for row in reader:
      row = dict([(force_unicode(k), force_unicode(v, errors='ignore')) for k, v in row.iteritems()]) # Get rid of invalid binary chars and convert to unicode from DictReader

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

      # Add mock id random value
      if 'id' not in row:
        row['id'] = str(uuid.uuid4())

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
      LOG.exception('failed to get timestamp key')
      timestamp_key = None
    try:
      message_key = next(iter(filter(lambda field: field['type'] in TEXT_FIELD_TYPES, fields)))['name']
    except:
      LOG.exception('failed to get message key')
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


def get_default_fields():
  """
  Returns a list of default fields for the Solr schema.xml
  :return:
  """
  default_field = DEFAULT_FIELD
  default_field.update({'name': 'id', 'type': 'string', 'multiValued': 'false'})
  return [default_field]
