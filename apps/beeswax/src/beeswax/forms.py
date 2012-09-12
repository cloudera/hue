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

from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy as _t

import hive_metastore

from desktop.lib.django_forms import simple_formset_factory, DependencyAwareForm
from desktop.lib.django_forms import ChoiceOrOtherField, MultiForm, SubmitButton
from beeswax import db_utils, common, conf, models
from filebrowser.forms import PathField


def query_form():
  """Generates a multi form object for queries."""
  return MultiForm(
      query=HQLForm,
      settings=SettingFormSet,
      file_resources=FileResourceFormSet,
      functions=FunctionFormSet,
      saveform=SaveForm,
      query_servers=QueryServerForm)


class QueryServerForm(forms.Form):
  server = forms.CharField(max_length=128, help_text=_t('Host:port of the query server.'))

  def __init__(self, *args, **kwargs):
    super(QueryServerForm, self).__init__(*args, **kwargs)

    if conf.QUERY_SERVERS:
      servers = ((server, server) for server in conf.QUERY_SERVERS.keys())
    else:
      servers = (('default', 'default'),)
    self.fields['server'].widget = forms.Select(choices=servers)


class SaveForm(forms.Form):
  """Used for saving query design."""
  name = forms.CharField(required=False,
                        max_length=64,
                        initial=models.SavedQuery.DEFAULT_NEW_DESIGN_NAME,
                        help_text=_t('Change the name to save as a new design.'))
  desc = forms.CharField(required=False, max_length=1024, label=_t("Description"))
  save = forms.BooleanField(widget=SubmitButton, required=False)
  saveas = forms.BooleanField(widget=SubmitButton, required=False)

  def __init__(self, *args, **kwargs):
    forms.Form.__init__(self, *args, **kwargs)
    self.fields['save'].label = _t('Save')
    self.fields['save'].widget.label = _('Save')
    self.fields['saveas'].label = _t('Save As')
    self.fields['saveas'].widget.label = _('Save As')

  def clean_name(self):
    name = self.cleaned_data.get('name', '').strip()
    return name

  def clean(self):
    if self.errors:
      return
    save = self.cleaned_data.get('save')
    name = self.cleaned_data.get('name')
    if save and len(name) == 0:
      # Bother with name iff we're saving
      raise forms.ValidationError(_('Please enter a name'))
    return self.cleaned_data

  def set_data(self, name, desc=''):
    """Set the name and desc programmatically"""
    data2 = self.data.copy()
    data2[self.add_prefix('name')] = name
    data2[self.add_prefix('desc')] = desc
    self.data = data2


class SaveResultsForm(DependencyAwareForm):
  """Used for saving the query result data"""

  SAVE_TYPES = (SAVE_TYPE_TBL, SAVE_TYPE_DIR) = (_('to a new table'), _('to HDFS directory'))
  save_target = forms.ChoiceField(required=True,
                                  choices=common.to_choices(SAVE_TYPES),
                                  widget=forms.RadioSelect)
  target_table = common.HiveIdentifierField(
                                  label=_t("Table Name"),
                                  required=False,
                                  help_text=_t("Name of the new table"))
  target_dir = PathField(label=_t("Results Location"),
                        required=False,
                        help_text=_t("Empty directory in HDFS to put the results"))
  dependencies = [
    ('save_target', SAVE_TYPE_TBL, 'target_table'),
    ('save_target', SAVE_TYPE_DIR, 'target_dir'),
  ]

  def clean_target_table(self):
    tbl = self.cleaned_data.get('target_table')
    if tbl:
      try:
        db_utils.meta_client().get_table("default", tbl)
        raise forms.ValidationError(_('Table already exists'))
      except hive_metastore.ttypes.NoSuchObjectException:
        pass
    return tbl


class HQLForm(forms.Form):
  query = forms.CharField(label=_t("Query Editor"),
                          required=True,
                          widget=forms.Textarea(attrs={'class':'beeswax_query'}))
  is_parameterized = forms.BooleanField(required=False, initial=True)
  email_notify = forms.BooleanField(required=False, initial=False)


class FunctionForm(forms.Form):
  name = forms.CharField(required=True)
  class_name = forms.CharField(required=True)

FunctionFormSet = simple_formset_factory(FunctionForm)


class FileResourceForm(forms.Form):
  type = forms.ChoiceField(required=True,
    choices=[
      ("JAR", _("jar")),
      ("ARCHIVE", _("archive")),
      ("FILE", ("file")),
    ], help_text=_t("Resources to upload with your Hive job." +
       "  Use 'jar' for UDFs.  Use 'file' and 'archive' for "
       "files to be copied and made locally available duirng MAP/TRANSFORM. " +
       "Paths are on HDFS.")
  )
  # TODO(philip): Could upload files here, too.  Or merely link
  # to upload utility?
  path = forms.CharField(required=True, help_text=_t("Path to file on HDFS."))

FileResourceFormSet = simple_formset_factory(FileResourceForm)


class SettingForm(forms.Form):
  # TODO: There are common settings that should be always exposed?
  key = forms.CharField()
  value = forms.CharField()

SettingFormSet = simple_formset_factory(SettingForm)


# In theory, there are only 256 of these...
TERMINATOR_CHOICES = [ (hive_val, desc) for hive_val, desc, ascii in common.TERMINATORS ]

class CreateTableForm(DependencyAwareForm):
  """
  Form used in the create table page
  """
  dependencies = []

  # Basic Data
  name = common.HiveIdentifierField(label=_t("Table Name"), required=True)
  comment = forms.CharField(label=_t("Description"), required=False)

  # Row Formatting
  row_format = forms.ChoiceField(required=True,
                                choices=common.to_choices([ "Delimited", "SerDe" ]),
                                initial="Delimited")

  # Delimited Row
  # These initials are per LazySimpleSerDe.DefaultSeparators
  field_terminator = ChoiceOrOtherField(label=_t("Field terminator"), required=False, initial=TERMINATOR_CHOICES[0][0],
    choices=TERMINATOR_CHOICES)
  collection_terminator = ChoiceOrOtherField(label=_t("Collection terminator"), required=False, initial=TERMINATOR_CHOICES[1][0],
    choices=TERMINATOR_CHOICES)
  map_key_terminator = ChoiceOrOtherField(label=_t("Map key terminator"), required=False, initial=TERMINATOR_CHOICES[2][0],
    choices=TERMINATOR_CHOICES)
  dependencies += [
    ("row_format", "Delimited", "field_terminator"),
    ("row_format", "Delimited", "collection_terminator"),
    ("row_format", "Delimited", "map_key_terminator"),
  ]

  # Serde Row
  serde_name = forms.CharField(required=False, label=_t("SerDe Name"))
  serde_properties = forms.CharField(
                        required=False,
                        help_text=_t("Comma-separated list of key-value pairs, eg., 'p1=v1, p2=v2'"))

  dependencies += [
    ("row_format", "SerDe", "serde_name"),
    ("row_format", "SerDe", "serde_properties"),
  ]

  # File Format
  file_format = forms.ChoiceField(required=False, initial="TextFile",
                        choices=common.to_choices(["TextFile", "SequenceFile", "InputFormat"]),
                        widget=forms.RadioSelect)
  input_format_class = forms.CharField(required=False, label=_t("InputFormat Class"))
  output_format_class = forms.CharField(required=False, label=_t("OutputFormat Class"))

  dependencies += [
    ("file_format", "InputFormat", "input_format_class"),
    ("file_format", "InputFormat", "output_format_class"),
  ]

  # External?
  use_default_location = forms.BooleanField(required=False, initial=True,
    label=_t("Use default location"))
  external_location = forms.CharField(required=False, help_text=_t("Path to HDFS directory or file of table data."))

  dependencies += [
    ("use_default_location", False, "external_location")
  ]

  def clean_field_terminator(self):
    return _clean_terminator(self.cleaned_data.get('field_terminator'))

  def clean_collection_terminator(self):
    return _clean_terminator(self.cleaned_data.get('collection_terminator'))

  def clean_map_key_terminator(self):
    return _clean_terminator(self.cleaned_data.get('map_key_terminator'))

  def clean_name(self):
    return _clean_tablename(self.cleaned_data['name'])


def _clean_tablename(name):
  try:
    db_utils.meta_client().get_table("default", name)
    raise forms.ValidationError(_('Table "%(name)s" already exists') % {'name': name})
  except hive_metastore.ttypes.NoSuchObjectException:
    return name


def _clean_terminator(val):
  if val is not None and len(val.decode('string_escape')) != 1:
      raise forms.ValidationError(_('Terminator must be exactly one character.'))
  return val


class CreateByImportFileForm(forms.Form):
  """Form for step 1 (specifying file) of the import wizard"""
  # Basic Data
  name = common.HiveIdentifierField(label=_t("Table Name"), required=True)
  comment = forms.CharField(label=_t("Description"), required=False)

  # File info
  path = PathField(label=_t("Input File"))
  do_import = forms.BooleanField(required=False, initial=True,
                          label=_t("Import data from file"),
                          help_text=_t("Automatically load this file into the table after creation."))

  def clean_name(self):
    return _clean_tablename(self.cleaned_data['name'])


class CreateByImportDelimForm(forms.Form):
  """Form for step 2 (picking delimiter) of the import wizard"""
  delimiter = ChoiceOrOtherField(label=_t('Delimiter'), required=False, initial=TERMINATOR_CHOICES[0][0],
                                 choices=TERMINATOR_CHOICES)
  file_type = forms.CharField(widget=forms.HiddenInput, required=True)

  def clean(self):
    # ChoiceOrOtherField doesn't work with required=True
    delimiter = self.cleaned_data.get('delimiter')
    if not delimiter:
      raise forms.ValidationError(_('Delimiter value is required.'))
    _clean_terminator(delimiter)
    return self.cleaned_data

  def old(self):
    if delimiter.isdigit():
      try:
        chr(int(delimiter))
        return int(delimiter)
      except ValueError:
        raise forms.ValidationError(_('Delimiter value must be smaller than 256.'))
    val = delimiter.decode('string_escape')
    if len(val) != 1:
      raise forms.ValidationError(_('Delimiter must be exactly one character.'))
    return ord(val)


# Note, struct is not currently supported.  (Because it's recursive, for example.)
HIVE_TYPES = \
    ( "string", "tinyint", "smallint", "int", "bigint", "boolean",
      "float", "double", "array", "map",)
HIVE_PRIMITIVE_TYPES = \
    ("string", "tinyint", "smallint", "int", "bigint", "boolean", "float", "double")

class PartitionTypeForm(forms.Form):
  column_name = common.HiveIdentifierField(required=True)
  column_type = forms.ChoiceField(required=True, choices=common.to_choices(HIVE_PRIMITIVE_TYPES))

class ColumnTypeForm(DependencyAwareForm):
  """
  Form used to specify a column during table creation
  """
  dependencies = [
    ("column_type", "array", "array_type"),
    ("column_type", "map", "map_key_type"),
    ("column_type", "map", "map_value_type"),
  ]
  column_name = common.HiveIdentifierField(label=_t('Column Name'), required=True)
  column_type = forms.ChoiceField(label=_t('Column Type'), required=True,
    choices=common.to_choices(HIVE_TYPES))
  array_type = forms.ChoiceField(required=False,
    choices=common.to_choices(HIVE_PRIMITIVE_TYPES), label=_t("Array Value Type"))
  map_key_type = forms.ChoiceField(required=False,
                                   choices=common.to_choices(HIVE_PRIMITIVE_TYPES),
                                   help_text=_t("Specify if column_type is map."))
  map_value_type = forms.ChoiceField(required=False,
                                     choices=common.to_choices(HIVE_PRIMITIVE_TYPES),
                                     help_text=_t("Specify if column_type is map."))

ColumnTypeFormSet = simple_formset_factory(ColumnTypeForm, initial=[{}], add_label=_t("add a column"))
# Default to no partitions
PartitionTypeFormSet = simple_formset_factory(PartitionTypeForm, add_label=_t("add a partition"))


class LoadDataForm(forms.Form):
  """Form used for loading data into an existing table."""
  path = PathField(label=_t("Path"))
  overwrite = forms.BooleanField(required=False, initial=False,
    label=_t("Overwrite?"))

  def __init__(self, table_obj, *args, **kwargs):
    """
    @param table_obj is a hive_metastore.thrift Table object,
    used to add fields corresopnding to partition keys.
    """
    super(LoadDataForm, self).__init__(*args, **kwargs)
    self.partition_columns = dict()
    for i, column in enumerate(table_obj.partitionKeys):
      # We give these numeric names because column names
      # may be unpleasantly arbitrary.
      name = "partition_%d" % i
      char_field = forms.CharField(required=True, label=_t("%(column_name)s (partition key with type %(column_type)s)") % {'column_name': column.name, 'column_type': column.type})
      self.fields[name] = char_field
      self.partition_columns[name] = column.name
