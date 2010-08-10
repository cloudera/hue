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
Views & controls for creating tables
"""

import logging
import gzip

from django.core import urlresolvers

from desktop.lib import django_mako, i18n
from desktop.lib.django_util import render, PopupException
from desktop.lib.django_forms import MultiForm
from hadoop.fs import hadoopfs

import beeswax.common
import beeswax.forms
from beeswax.views import describe_table, confirm_query, execute_directly
from beeswax.views import make_beeswax_query
from beeswax import db_utils

LOG = logging.getLogger(__name__)

def index(request):
  """Main create table entry point, to divert into manual creation vs create from file."""
  return render("create_table_index.mako", request, {})


def create_table(request):
  """Create a table by specifying its attributes manually"""
  form = MultiForm(
      table=beeswax.forms.CreateTableForm,
      columns=beeswax.forms.ColumnTypeFormSet,
      partitions=beeswax.forms.PartitionTypeFormSet)
  if request.method == "POST":
    form.bind(request.POST)
    if form.is_valid():
      columns = [ f.cleaned_data for f in form.columns.forms ]
      partition_columns = [ f.cleaned_data for f in form.partitions.forms ]
      proposed_query = django_mako.render_to_string("create_table_statement.mako",
        {
          'table': form.table.cleaned_data,
          'columns': columns,
          'partition_columns': partition_columns
        }
      )
      # Mako outputs bytestring in utf8
      proposed_query = proposed_query.decode('utf-8')
      tablename = form.table.cleaned_data['name']
      on_success_url = urlresolvers.reverse(describe_table, kwargs={'table': tablename})
      return confirm_query(request, proposed_query, on_success_url)
  else:
    form.bind()
  return render("create_table_manually.mako", request, dict(
    action="#",
    table_form=form.table,
    columns_form=form.columns,
    partitions_form=form.partitions,
    has_tables=len(db_utils.meta_client().get_tables("default", ".*")) > 0
  ))


IMPORT_PEEK_SIZE = 8192
IMPORT_PEEK_NLINES = 10
DELIMITERS = [ hive_val for hive_val, _, _ in beeswax.common.TERMINATORS ]
DELIMITER_READABLE = {'\\001' : 'ctrl-As',
                      '\\002' : 'ctrl-Bs',
                      '\\003' : 'ctrl-Cs',
                      '\\t'   : 'tabs',
                      ','     : 'commas',
                      ' '     : 'spaces'}
FILE_READERS = [ ]

def import_wizard(request):
  """
  Help users define table and based on a file they want to import to Hive.
  Limitations:
    - Rows are delimited (no serde).
    - No detection for map and array types.
    - No detection for the presence of column header in the first row.
    - No partition table.
    - Does not work with binary data.
  """
  encoding = i18n.get_site_encoding()

  if request.method == 'POST':
    # Have a while loop to allow an easy way to break
    for _ in range(1):
      #
      # General processing logic:
      # - We have 3 steps. Each requires the previous.
      #   * Step 1      : Table name and file location
      #   * Step 2a     : Display sample with auto chosen delim
      #   * Step 2b     : Display sample with user chosen delim (if user chooses one)
      #   * Step 3      : Display sample, and define columns
      # - Each step is represented by a different form. The form of an earlier step
      #   should be present when submitting to a later step.
      # - To preserve the data from the earlier steps, we send the forms back as
      #   hidden fields. This way, when users revisit a previous step, the data would
      #   be there as well.
      #
      delim_is_auto = False
      fields_list, n_cols = [ [] ], 0
      s3_col_formset = None

      # Everything requires a valid file form
      s1_file_form = beeswax.forms.CreateByImportFileForm(request.POST)
      if not s1_file_form.is_valid():
        break

      do_s2_auto_delim = request.POST.get('submit_file')        # Step 1 -> 2
      do_s2_user_delim = request.POST.get('submit_preview')     # Step 2 -> 2
      do_s3_column_def = request.POST.get('submit_delim')       # Step 2 -> 3
      do_hive_create = request.POST.get('submit_create')        # Step 3 -> execute

      # Exactly one of these should be True
      assert len(filter(None, (do_s2_auto_delim,
                               do_s2_user_delim,
                               do_s3_column_def,
                               do_hive_create))) == 1, 'Invalid form submission'

      #
      # Fix up what we should do in case any form is invalid
      #
      if not do_s2_auto_delim:
        # We should have a valid delim form
        s2_delim_form = beeswax.forms.CreateByImportDelimForm(request.POST)
        if not s2_delim_form.is_valid():
          # Go back to picking delimiter
          do_s2_user_delim, do_s3_column_def, do_hive_create = True, False, False

      if do_hive_create:
        # We should have a valid columns formset
        s3_col_formset = beeswax.forms.ColumnTypeFormSet(prefix='cols', data=request.POST)
        if not s3_col_formset.is_valid():
          # Go back to define columns
          do_s3_column_def, do_hive_create = True, False

      #
      # Go to step 2: We've just picked the file. Preview it.
      #
      if do_s2_auto_delim:
        delim_is_auto = True
        fields_list, n_cols, s2_delim_form = _delim_preview(
                                              request.fs,
                                              s1_file_form,
                                              encoding,
                                              [ reader.TYPE for reader in FILE_READERS ],
                                              DELIMITERS)

      if (do_s2_user_delim or do_s3_column_def) and s2_delim_form.is_valid():
        # Delimit based on input
        fields_list, n_cols, s2_delim_form = _delim_preview(
                                              request.fs,
                                              s1_file_form,
                                              encoding,
                                              (s2_delim_form.cleaned_data['file_type'],),
                                              (s2_delim_form.cleaned_data['delimiter'],))

      if do_s2_auto_delim or do_s2_user_delim:
        return render('choose_delimiter.mako', request, dict(
          action=urlresolvers.reverse(import_wizard),
          delim_readable=DELIMITER_READABLE[s2_delim_form['delimiter'].data[0]],
          initial=delim_is_auto,
          file_form=s1_file_form,
          delim_form=s2_delim_form,
          fields_list=fields_list,
          delimiter_choices=beeswax.forms.TERMINATOR_CHOICES,
          n_cols=n_cols,
        ))

      #
      # Go to step 3: Define column.
      #
      if do_s3_column_def:
        if s3_col_formset is None:
          columns = []
          for i in range(n_cols):
            columns.append(dict(
                column_name='col_%s' % (i,),
                column_type='string',
            ))
          s3_col_formset = beeswax.forms.ColumnTypeFormSet(prefix='cols', initial=columns)
        return render('define_columns.mako', request, dict(
          action=urlresolvers.reverse(import_wizard),
          file_form=s1_file_form,
          delim_form=s2_delim_form,
          column_formset=s3_col_formset,
          fields_list=fields_list,
          n_cols=n_cols,
        ))

      #
      # Finale: Execute
      #
      if do_hive_create:
        delim = s2_delim_form.cleaned_data['delimiter']
        table_name = s1_file_form.cleaned_data['name']
        proposed_query = django_mako.render_to_string("create_table_statement.mako",
          {
            'table': dict(name=table_name,
                          comment=s1_file_form.cleaned_data['comment'],
                          row_format='Delimited',
                          field_terminator=delim),
            'columns': [ f.cleaned_data for f in s3_col_formset.forms ],
            'partition_columns': []
          }
        )

        do_load_data = s1_file_form.cleaned_data.get('do_import')
        path = s1_file_form.cleaned_data['path']
        return _submit_create_and_load(request, proposed_query, table_name, path, do_load_data)
  else:
    s1_file_form = beeswax.forms.CreateByImportFileForm()

  return render('choose_file.mako', request, dict(
    action=urlresolvers.reverse(import_wizard),
    file_form=s1_file_form,
  ))


def _submit_create_and_load(request, create_hql, table_name, path, do_load):
  """
  Submit the table creation, and setup the load to happen (if ``do_load``).
  """
  on_success_params = { }
  if do_load:
    on_success_params['table'] = table_name
    on_success_params['path'] = path
    on_success_url = urlresolvers.reverse(beeswax.create_table.load_after_create)
  else:
    on_success_url = urlresolvers.reverse(describe_table, kwargs={'table': table_name})

  query_msg = make_beeswax_query(request, create_hql)
  return execute_directly(request, query_msg,
                          on_success_url=on_success_url,
                          on_success_params=on_success_params)


def _delim_preview(fs, file_form, encoding, file_types, delimiters):
  """
  _delim_preview(fs, file_form, encoding, file_types, delimiters)
                              -> (fields_list, n_cols, delim_form)

  Look at the beginning of the file and parse it according to the list of
  available file_types and delimiters.
  """
  assert file_form.is_valid()

  path = file_form.cleaned_data['path']
  try:
    file_obj = fs.open(path)
    delim, file_type, fields_list = _parse_fields(
              path, file_obj, encoding, file_types, delimiters)
    file_obj.close()
  except IOError, ex:
    msg = "Failed to open file '%s': %s" % (path, ex)
    LOG.exception(msg)
    raise PopupException(msg)

  n_cols = max([ len(row) for row in fields_list ])
  # ``delimiter`` is a MultiValueField. delimiter_0 and delimiter_1 are the sub-fields.
  delim_form = beeswax.forms.CreateByImportDelimForm(dict(delimiter_0=delim,
                                                          delimiter_1='',
                                                          file_type=file_type,
                                                          n_cols=n_cols))
  if not delim_form.is_valid():
    assert False, 'Internal error when constructing the delimiter form'
  return fields_list, n_cols, delim_form


def _parse_fields(path, file_obj, encoding, filetypes, delimiters):
  """
  _parse_fields(path, file_obj, encoding, filetypes, delimiters)
                                  -> (delimiter, filetype, fields_list)

  Go through the list of ``filetypes`` (gzip, text) and stop at the first one
  that works for the data. Then apply the list of ``delimiters`` and pick the
  most appropriate one.
  ``path`` is used for debugging only.

  Return the best delimiter, filetype and the data broken down into rows of fields.
  """
  file_readers = [ reader for reader in FILE_READERS if reader.TYPE in filetypes ]

  for reader in file_readers:
    LOG.debug("Trying %s for file: %s" % (reader.TYPE, path))
    file_obj.seek(0, hadoopfs.SEEK_SET)
    lines = reader.readlines(file_obj, encoding)
    if lines is not None:
      delim, fields_list = _readfields(lines, delimiters)
      return delim, reader.TYPE, fields_list
  else:
    # Even TextFileReader doesn't work
    msg = "Failed to decode file '%s' into printable characters under %s" % (path, encoding,)
    LOG.error(msg)
    raise PopupException(msg)


def _readfields(lines, delimiters):
  """
  readfields(lines, delimiters) -> (delim, a list of lists of fields)

  ``delimiters`` is a list of escaped characters, e.g. r'\\t', r'\\001', ','

  Choose the best delimiter from the given list of delimiters. Return that delimiter
  and the fields parsed by using that delimiter.
  """
  def score_delim(fields_list):
    """
    How good is this fields_list? Score based on variance of the number of fields
    The score is always non-negative. The higher the better.
    """
    n_lines = len(fields_list)
    len_list = [ len(fields) for fields in fields_list ]

    # All lines should break into multiple fields
    if min(len_list) == 1:
      return 0

    avg_n_fields = sum(len_list) / n_lines
    sq_of_exp = avg_n_fields * avg_n_fields

    len_list_sq = [ l * l for l in len_list ]
    exp_of_sq = sum(len_list_sq) / n_lines
    var = exp_of_sq - sq_of_exp
    # Favour more fields
    return (1000.0 / (var + 1)) + avg_n_fields


  max_score = -1
  res = (None, None)

  for delim in delimiters:
    fields_list = [ ]
    for line in lines:
      if line:
        # Unescape the delimiter back to its character value
        fields_list.append(line.split(delim.decode('string_escape')))
    score = score_delim(fields_list)
    LOG.debug("'%s' gives score of %s" % (delim, score))
    if score > max_score:
      max_score = score
      res = (delim, fields_list)
  return res


def _peek_file(fs, file_form):
  """_peek_file(fs, file_form) -> (path, initial data)"""
  try:
    path = file_form.cleaned_data['path']
    file_obj = fs.open(path)
    file_head = file_obj.read(IMPORT_PEEK_SIZE)
    file_obj.close()
    return (path, file_head)
  except IOError, ex:
    msg = "Failed to open file '%s': %s" % (path, ex)
    LOG.exception(msg)
    raise PopupException(msg)


class GzipFileReader(object):
  """Class for extracting lines from a gzipped file"""
  TYPE = 'gzip'

  @staticmethod
  def readlines(fileobj, encoding):
    """readlines(fileobj, encoding) -> list of lines"""
    gz = gzip.GzipFile(fileobj=fileobj, mode='rb')
    try:
      data = gz.read(IMPORT_PEEK_SIZE)
    except IOError:
      return None
    try:
      return unicode(data, encoding, errors='replace').split('\n')[:IMPORT_PEEK_NLINES]
    except UnicodeError:
      return None

FILE_READERS.append(GzipFileReader)


class TextFileReader(object):
  """Class for extracting lines from a regular text file"""
  TYPE = 'text'

  @staticmethod
  def readlines(fileobj, encoding):
    """readlines(fileobj, encoding) -> list of lines"""
    try:
      data = fileobj.read(IMPORT_PEEK_SIZE)
      return unicode(data, encoding, errors='replace').split('\n')[:IMPORT_PEEK_NLINES]
    except UnicodeError:
      return None

FILE_READERS.append(TextFileReader)


def load_after_create(request):
  """
  Automatically load data into a newly created table.

  We get here from the create's on_success_url, and expect to find
  ``table`` and ``path`` from the parameters.
  """
  tablename = request.REQUEST.get('table')
  path = request.REQUEST.get('path')
  if not tablename or not path:
    msg = 'Internal error: Missing needed parameter to load data into table'
    LOG.error(msg)
    raise PopupException(msg)

  LOG.debug("Auto loading data from %s into table %s" % (path, tablename))
  hql = "LOAD DATA INPATH '%s' INTO TABLE `%s`" % (path, tablename)
  query_msg = make_beeswax_query(request, hql)
  on_success_url = urlresolvers.reverse(describe_table, kwargs={'table': tablename})

  return execute_directly(request, query_msg, on_success_url=on_success_url)
