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

from builtins import chr
from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy as _t
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import NumberInput

from aws.s3 import S3_ROOT, S3A_ROOT
from desktop.lib.django_forms import simple_formset_factory, DependencyAwareForm
from desktop.lib.django_forms import ChoiceOrOtherField, MultiForm, SubmitButton
from filebrowser.forms import PathField

from beeswax import common
from beeswax.models import SavedQuery


class QueryForm(MultiForm):
  def __init__(self):
    super(QueryForm, self).__init__(
      query=HQLForm,
      settings=SettingFormSet,
      file_resources=FileResourceFormSet,
      functions=FunctionFormSet,
      saveform=SaveForm
    )


class SaveForm(forms.Form):
  """Used for saving query design."""
  name = forms.CharField(required=False,
                         max_length=64,
                         initial=SavedQuery.DEFAULT_NEW_DESIGN_NAME,
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
    return self.cleaned_data.get('name', '').strip()

  def clean(self):
    cleaned_data = super(SaveForm, self).clean()

    if self.errors:
      return
    save = cleaned_data.get('save')
    name = cleaned_data.get('name')
    if save and not name:
      # Bother with name iff we're saving
      raise forms.ValidationError(_('Enter a name.'))
    return cleaned_data

  def set_data(self, name, desc=''):
    """Set the name and desc programmatically"""
    data2 = self.data.copy()
    data2[self.add_prefix('name')] = name
    data2[self.add_prefix('desc')] = desc
    self.data = data2


class SaveResultsDirectoryForm(forms.Form):
  """Used for saving the query result data to hdfs directory"""

  target_dir = forms.CharField(label=_t("Directory"),
                               required=True,
                               help_text=_t("Path to directory"))

  def __init__(self, *args, **kwargs):
    self.fs = kwargs.pop('fs', None)
    super(SaveResultsDirectoryForm, self).__init__(*args, **kwargs)

  def clean_target_dir(self):
    if not self.cleaned_data['target_dir'].startswith('/'):
      raise forms.ValidationError(_("Target directory should begin with a /"))
    elif self.fs.exists(self.cleaned_data['target_dir']):
      raise forms.ValidationError(_('Directory already exists.'))
    return self.cleaned_data['target_dir']


class SaveResultsFileForm(forms.Form):
  """Used for saving the query result data to hdfs file"""

  target_file = forms.CharField(label=_t("File path"),
                                required=True,
                                help_text=_t("Path to file"))
  overwrite = forms.BooleanField(label=_t('Overwrite'),
                                 required=False,
                                 help_text=_t("Overwrite the selected files"))

  def clean_target_file(self):
    if not self.cleaned_data['target_file'].startswith('/'):
      raise forms.ValidationError("Target file should begin with a /")

    return self.cleaned_data['target_file']


class SaveResultsTableForm(forms.Form):
  """Used for saving the query result data to hive table"""

  target_table = common.HiveIdentifierField(
                                  label=_t("Table Name"),
                                  required=True,
                                  help_text=_t("Name of the new table")) # Can also contain a DB prefixed table name, e.g. DB_NAME.TABLE_NAME

  def __init__(self, *args, **kwargs):
    self.db = kwargs.pop('db', None)
    self.target_database = kwargs.pop('database', 'default')
    super(SaveResultsTableForm, self).__init__(*args, **kwargs)

  def clean(self):
    cleaned_data = super(SaveResultsTableForm, self).clean()
    target_table = cleaned_data.get('target_table')

    if not target_table:
      raise forms.ValidationError(_("Table name is required."))
    else:
      if self.db is None:
        raise forms.ValidationError(_("Cannot validate form, db object is required."))
      else:
        # Table field may be set to <database>.<table> so we need to parse it before validation
        name_parts = target_table.split(".")
        if len(name_parts) == 1:
          pass
        elif len(name_parts) == 2:   # Update table name without the DB prefix
          self.target_database, target_table = name_parts
        else:
          raise forms.ValidationError(_("Invalid table prefix name."))

        # Check if table already exists
        table = None
        try:
          table = self.db.get_table(self.target_database, target_table)
        except Exception:
          cleaned_data['target_table'] = target_table

        if table is not None:
          raise forms.ValidationError(_("Table %s.%s already exists") % (self.target_database, target_table))

    return cleaned_data


class HQLForm(forms.Form):
  query = forms.CharField(label=_t("Query Editor"),
                          required=True,
                          widget=forms.Textarea(attrs={'class': 'beeswax_query'}))
  is_parameterized = forms.BooleanField(required=False, initial=True)
  email_notify = forms.BooleanField(required=False, initial=False)
  type = forms.IntegerField(required=False, initial=0)
  database = forms.ChoiceField(required=False,
                           label='',
                           choices=(('default', 'default'),),
                           initial=0,
                           widget=forms.widgets.Select(attrs={'class': 'input-medium'}))


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
       "files to be copied and made locally available during MAP/TRANSFORM. " +
       "Paths are on HDFS.")
  )

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
                        help_text=_t("Comma-separated list of key-value pairs. E.g. 'p1=v1, p2=v2'"))

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
  use_default_location = forms.BooleanField(required=False, initial=True, label=_t("Use default location."))
  external_location = forms.CharField(required=False, help_text=_t("Path to HDFS directory or file of table data."))

  # Table Properties
  skip_header = forms.BooleanField(required=False, initial=False, label=_t("Use header row for column names?"))

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
    return _clean_tablename(self.db, self.cleaned_data['name'], self.database)


def _clean_tablename(db, name, database='default'):
  if ' ' in name:
    raise forms.ValidationError(_('Spaces are not allowed in table names.'))
  try:
    table = db.get_table(database, name)
    if table.name:
      raise forms.ValidationError(_('Table "%(name)s" already exists.') % {'name': name})
  except Exception:
    return name


def _clean_terminator(val):
  if val is not None and val == '':
    raise forms.ValidationError(_('Terminator must not be empty.'))
  return val


class CreateByImportFileForm(forms.Form):
  """Form for step 1 (specifying file) of the import wizard"""

  # Basic Data
  name = common.HiveIdentifierField(label=_t("Table Name"), required=True)
  comment = forms.CharField(label=_t("Description"), required=False)

  # File info
  path = PathField(label=_t("Input File or Directory"))
  load_data = forms.ChoiceField(required=True,
    choices=[
      ("IMPORT", _("Import data")),
      ("EXTERNAL", _("Create External Table")),
      ("EMPTY", ("Leave Empty")),
    ],
    help_text=_t("Select 'import' to load data from the file into the Hive warehouse directory after creation. "
       "Select 'external' if the table is an external table and the data files should not be moved. " +
       "Select 'empty' if the file should only be used to define the table schema but not loaded (table will be empty).")
  )

  def __init__(self, *args, **kwargs):
    self.db = kwargs.pop('db', None)
    super(CreateByImportFileForm, self).__init__(*args, **kwargs)

  def clean_name(self):
    return _clean_tablename(self.db, self.cleaned_data['name'])

  def clean_path(self):
    path = self.cleaned_data['path']
    if path.lower().startswith(S3_ROOT):
      path = path.lower().replace(S3_ROOT, S3A_ROOT)
    if not path.endswith('/'):
      path = '%s/' % path
    return path


class CreateByImportDelimForm(forms.Form):
  """Form for step 2 (picking delimiter) of the import wizard"""
  delimiter = ChoiceOrOtherField(label=_t('Delimiter'), required=False, initial=TERMINATOR_CHOICES[0][0],
                                 choices=TERMINATOR_CHOICES)
  file_type = forms.CharField(widget=forms.HiddenInput, required=True)

  def clean(self):
    # ChoiceOrOtherField doesn't work with required=True
    delimiter = self.cleaned_data.get('delimiter')
    if delimiter.isdigit():
      try:
        chr(int(delimiter))
        return int(delimiter)
      except ValueError:
        raise forms.ValidationError(_('Delimiter value must be smaller than 65533.'))
    if not delimiter:
      raise forms.ValidationError(_('Delimiter value is required.'))
    _clean_terminator(delimiter)
    return self.cleaned_data


# Note, struct is not currently supported.  (Because it's recursive, for example.)
HIVE_TYPES = \
    ( "string", "tinyint", "smallint", "int", "bigint", "boolean",
      "float", "double", "array", "map", "timestamp", "date",
      "char", "varchar")
HIVE_PRIMITIVE_TYPES = \
    ("string", "tinyint", "smallint", "int", "bigint", "boolean",
      "float", "double", "timestamp", "date", "char", "varchar")

class PartitionTypeForm(forms.Form):
  dependencies = [
    ("column_type", "char", "char_length"),
    ("column_type", "varchar", "varchar_length")
  ]
  column_name = common.HiveIdentifierField(required=True)
  column_type = forms.ChoiceField(required=True, choices=common.to_choices(HIVE_PRIMITIVE_TYPES))
  char_length = forms.IntegerField(required=False, initial=1,
                                   widget=NumberInput(attrs={'min': 1, 'max': 255}),
                                   validators=[MinValueValidator(1), MaxValueValidator(255)],
                                   help_text=_t("Specify if column_type is char"))
  varchar_length = forms.IntegerField(required=False, initial=1,
                                      widget=NumberInput(attrs={'min': 1, 'max': 65355}),
                                      validators=[MinValueValidator(1), MaxValueValidator(65355)],
                                      help_text=_t("Specify if column_is varchar"))

class ColumnTypeForm(DependencyAwareForm):
  """
  Form used to specify a column during table creation
  """
  dependencies = [
    ("column_type", "array", "array_type"),
    ("column_type", "map", "map_key_type"),
    ("column_type", "map", "map_value_type"),
    ("column_type", "char", "char_length"),
    ("column_type", "varchar", "varchar_length")
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
  char_length = forms.IntegerField(required=False, initial=1,
                                   widget=NumberInput(attrs={'min': 1, 'max': 255}),
                                   validators=[MinValueValidator(1), MaxValueValidator(255)],
                                   help_text=_t("Specify if column_type is char"))
  varchar_length = forms.IntegerField(required=False, initial=1,
                                      widget=NumberInput(attrs={'min': 1, 'max': 65355}),
                                      validators=[MinValueValidator(1), MaxValueValidator(65355)],
                                      help_text=_t("Specify if column_is varchar"))


ColumnTypeFormSet = simple_formset_factory(ColumnTypeForm, initial=[{}], add_label=_t("Add a column"))
# Default to no partitions
PartitionTypeFormSet = simple_formset_factory(PartitionTypeForm, add_label=_t("Add a partition"))


def _clean_databasename(name):
  try:
    if name in db.get_databases(): # Will always fail
      raise forms.ValidationError(_('Database "%(name)s" already exists.') % {'name': name})
  except Exception:
    return name


class CreateDatabaseForm(DependencyAwareForm):
  """
  Form used in the create database page
  """
  dependencies = []

  # Basic Data
  name = common.HiveIdentifierField(label=_t("Database Name"), required=True)
  comment = forms.CharField(label=_t("Description"), required=False)

  # External if not true
  use_default_location = forms.BooleanField(required=False, initial=True, label=_t("Use default location"))
  external_location = forms.CharField(required=False, help_text=_t("Path to HDFS directory or file of database data."))

  dependencies += [
    ("use_default_location", False, "external_location")
  ]

  def clean_name(self):
    return _clean_databasename(self.cleaned_data['name'])
