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

from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import range
import logging
import urllib.request, urllib.parse, urllib.error

from django import forms
from django.contrib.auth.models import User, Group
from django.forms import FileField, CharField, BooleanField, Textarea
from django.forms.formsets import formset_factory, BaseFormSet

from aws.s3 import S3A_ROOT, normpath as s3_normpath
from desktop.lib import i18n
from hadoop.fs import normpath
from filebrowser.lib import rwx

from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger(__name__)


class FormSet(BaseFormSet):
  def __init__(self, data=None, prefix=None, *args, **kwargs):
    self.prefix = prefix or self.get_default_prefix()
    if data:
      self.data = {}
      # Add management field info
      # This is hard coded given that none of these keys or info is exportable
      # This could be a problem point if the management form changes in later releases
      self.data['%s-TOTAL_FORMS' % self.prefix] = len(data)
      self.data['%s-INITIAL_FORMS' % self.prefix] = len(data)
      self.data['%s-MAX_NUM_FORMS' % self.prefix] = 0

      # Add correct data
      for i in range(0, len(data)):
        prefix = self.add_prefix(i)
        for field in data[i]:
          self.data['%s-%s' % (prefix, field)] = data[i][field]
    BaseFormSet.__init__(self, self.data, self.prefix, *args, **kwargs)


class PathField(CharField):
  def __init__(self, label, help_text=None, **kwargs):
    kwargs.setdefault('required', True)
    kwargs.setdefault('min_length', 1)
    forms.CharField.__init__(self, label=label, help_text=help_text, **kwargs)

  def clean(self, value):
    cleaned_path = CharField.clean(self, value)
    if value.lower().startswith(S3A_ROOT):
      cleaned_path = s3_normpath(cleaned_path)
    else:
      cleaned_path = normpath(cleaned_path)
    return cleaned_path


class EditorForm(forms.Form):
  path = PathField(label=_("File to edit"))
  contents = CharField(widget=Textarea, label=_("Contents"), required=False)
  encoding = CharField(label=_('Encoding'), required=False)

  def clean_path(self):
    return urllib.parse.unquote(self.cleaned_data.get('path', ''))

  def clean_contents(self):
    return self.cleaned_data.get('contents', '').replace('\r\n', '\n')

  def clean_encoding(self):
    encoding = self.cleaned_data.get('encoding', '').strip()
    if not encoding:
      return i18n.get_site_encoding()
    return encoding

class RenameForm(forms.Form):
  op = "rename"
  src_path = CharField(label=_("File to rename"), help_text=_("The file to rename."))
  dest_path = CharField(label=_("New name"), help_text=_("Rename the file to:"))

class BaseRenameFormSet(FormSet):
  op = "rename"

RenameFormSet = formset_factory(RenameForm, formset=BaseRenameFormSet, extra=0)

class CopyForm(forms.Form):
  op = "copy"
  src_path = CharField(label=_("File to copy"), help_text=_("The file to copy."))
  dest_path = CharField(label=_("Destination location"), help_text=_("Copy the file to:"))

class BaseCopyFormSet(FormSet):
  op = "copy"

CopyFormSet = formset_factory(CopyForm, formset=BaseCopyFormSet, extra=0)

class SetReplicationFactorForm(forms.Form):
  op = "setreplication"
  src_path = CharField(label=_("File to set replication factor"), help_text=_("The file to set replication factor."))
  replication_factor = CharField(label=_("Value of replication factor"), help_text=_("The value of replication factor."))

class UploadFileForm(forms.Form):
  op = "upload"
  # The "hdfs" prefix in "hdfs_file" triggers the HDFSfileUploadHandler
  hdfs_file = FileField(forms.Form, label=_("File to Upload"))
  dest = PathField(label=_("Destination Path"), help_text=_("Filename or directory to upload to."))
  extract_archive = BooleanField(required=False)

class UploadArchiveForm(forms.Form):
  op = "upload"
  archive = FileField(forms.Form, label=_("Archive to Upload"))
  dest = PathField(label=_("Destination Path"), help_text=_("Archive to upload to."))

class RemoveForm(forms.Form):
  op = "remove"
  path = PathField(label=_("File to remove"))

class RmDirForm(forms.Form):
  op = "rmdir"
  path = PathField(label=_("Directory to remove"))

class RmTreeForm(forms.Form):
  op = "rmtree"
  path = PathField(label=_("Directory to remove (recursively)"))

class BaseRmTreeFormset(FormSet):
  op = "rmtree"

RmTreeFormSet = formset_factory(RmTreeForm, formset=BaseRmTreeFormset, extra=0)

class RestoreForm(forms.Form):
  op = "rmtree"
  path = PathField(label=_("Path to restore"))

class BaseRestoreFormset(FormSet):
  op = "restore"

RestoreFormSet = formset_factory(RestoreForm, formset=BaseRestoreFormset, extra=0)

class TrashPurgeForm(forms.Form):
  op = "purge_trash"

class MkDirForm(forms.Form):
  op = "mkdir"
  path = PathField(label=_("Path in which to create the directory"))
  name = PathField(label=_("Directory Name"))

class TouchForm(forms.Form):
  op = "touch"
  path = PathField(label=_("Path in which to create the file"))
  name = PathField(label=_("File Name"))

class ChownForm(forms.Form):
  op = "chown"
  path = PathField(label=_("Path to change user/group ownership"))
  # These could be "ChoiceFields", listing only users and groups
  # that the current user has permissions for.
  user = CharField(label=_("User"), min_length=1)
  user_other = CharField(label=_("OtherUser"), min_length=1, required=False)
  group = CharField(label=_("Group"), min_length=1)
  group_other = CharField(label=_("OtherGroup"), min_length=1, required=False)
  recursive = BooleanField(label=_("Recursive"), required=False)

  def __init__(self, *args, **kwargs):
    super(ChownForm, self).__init__(*args, **kwargs)

    self.all_groups = [ group.name for group in Group.objects.all() ]
    self.all_users = [ user.username for user in User.objects.all() ]

class BaseChownFormSet(FormSet):
  op = "chown"

ChownFormSet = formset_factory(ChownForm, formset=BaseChownFormSet, extra=0)

class ChmodForm(forms.Form):
  op = "chmod"
  path = PathField(label=_("Path to change permissions"))

  # By default, BooleanField only validates when
  # it's checked.
  user_read = BooleanField(required=False)
  user_write = BooleanField(required=False)
  user_execute = BooleanField(required=False)
  group_read = BooleanField(required=False)
  group_write = BooleanField(required=False)
  group_execute = BooleanField(required=False)
  other_read = BooleanField(required=False)
  other_write = BooleanField(required=False)
  other_execute = BooleanField(required=False)
  sticky = BooleanField(required=False)
  recursive = BooleanField(required=False)

  names = ("user_read", "user_write", "user_execute",
      "group_read", "group_write", "group_execute",
      "other_read", "other_write", "other_execute",
      "sticky")

  def __init__(self, initial, *args, **kwargs):
    logging.info(dir(self))
    logging.info(dir(type(self)))
    # Convert from string representation.
    mode = initial.get("mode")
    if mode is not None:
      mode = int(mode, 8)
      bools = rwx.expand_mode(mode)
      for name, b in zip(self.names, bools):
        initial[name] = b
    logging.debug(initial)
    kwargs['initial'] = initial
    forms.Form.__init__(self, *args, **kwargs)

  def full_clean(self):
    forms.Form.full_clean(self)
    if hasattr(self, "cleaned_data"):
      self.cleaned_data["mode"] = rwx.compress_mode([self.cleaned_data[name] for name in self.names])

class BaseChmodFormSet(FormSet):
  op = "chmod"

ChmodFormSet = formset_factory(ChmodForm, formset=BaseChmodFormSet, extra=0)
