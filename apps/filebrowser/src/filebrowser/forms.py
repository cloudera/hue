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
from django.forms import FileField, CharField, BooleanField, Textarea

from desktop.lib import i18n
from filebrowser.lib import rwx
from hadoop.fs import normpath
from django.contrib.auth.models import User, Group

import logging
logger = logging.getLogger(__name__)

class PathField(CharField):
  def __init__(self, label, help_text=None, **kwargs):
    kwargs.setdefault('required', True)
    kwargs.setdefault('min_length', 1)
    forms.CharField.__init__(self, label=label, help_text=help_text, **kwargs)
  
  def clean(self, value):
    return normpath(CharField.clean(self, value))

class EditorForm(forms.Form):
  path = PathField(label="File to edit")
  contents = CharField(widget=Textarea, label="Contents", required=False)
  encoding = CharField(label='Encoding', required=False)

  def clean_encoding(self):
    encoding = self.cleaned_data.get('encoding', '').strip()
    if not encoding:
      return i18n.get_site_encoding()
    return encoding

class RenameForm(forms.Form):
  op = "rename"
  src_path = CharField(label="File to rename", help_text="The file to rename.")
  dest_path = CharField(label="New name", help_text="Rename the file to:")

class UploadForm(forms.Form):
  op = "upload"
  # The "hdfs" prefix in "hdfs_file" triggers the HDFSfileUploadHandler
  hdfs_file = FileField(forms.Form, label="File to Upload")
  dest = PathField(label="Destination Path", help_text="Filename or directory to upload to.")

class RemoveForm(forms.Form):
  op = "remove"
  path = PathField(label="File to remove")

class RmDirForm(forms.Form):
  op = "rmdir"
  path = PathField(label="Directory to remove")

class RmTreeForm(forms.Form):
  op = "rmtree"
  path = PathField(label="Directory to remove (recursively)")

class MkDirForm(forms.Form):
  op = "mkdir"
  path = PathField(label="Path in which to create the directory")
  name = PathField(label="Directory Name")

class ChownForm(forms.Form):
  op = "chown"
  path = PathField(label="Path to change user/group ownership")
  # These could be "ChoiceFields", listing only users and groups
  # that the current user has permissions for.
  user = CharField(label="User", min_length=1)
  user_other = CharField(label="OtherUser", min_length=1, required=False)
  group = CharField(label="Group", min_length=1)
  group_other = CharField(label="OtherGroup", min_length=1, required=False)

  def __init__(self, *args, **kwargs):
    super(ChownForm, self).__init__(*args, **kwargs)

    self.all_groups = [ group.name for group in Group.objects.all() ]
    self.all_users = [ user.username for user in User.objects.all() ]

class ChmodForm(forms.Form):
  op = "chmod"
  path = PathField(label="Path to change permissions")

  # By default, BooleanField only validates when
  # it's checked.  Oy.
  user_read = BooleanField(required=False)
  user_write = BooleanField(required=False)
  user_execute = BooleanField(required=False)
  group_read = BooleanField(required=False)
  group_write = BooleanField(required=False)
  group_execute = BooleanField(required=False)
  other_read = BooleanField(required=False)
  other_write = BooleanField(required=False)
  other_execute = BooleanField(required=False)

  names = ("user_read", "user_write", "user_execute",
      "group_read", "group_write", "group_execute",
      "other_read", "other_write", "other_execute")

  def __init__(self, initial):
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
    forms.Form.__init__(self, initial)

  def is_valid(self):
    if forms.Form.is_valid(self):
      self.cleaned_data["mode"] = rwx.compress_mode(map(lambda name: self.cleaned_data[name], self.names))
      return True
    else:
      return False
