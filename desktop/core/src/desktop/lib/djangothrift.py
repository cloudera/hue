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
#
# Utilities for dealing with Thrift and Django.
#
# See also 
# * http://docs.djangoproject.com/en/dev/howto/custom-model-fields/#howto-custom-model-fields 
# * http://www.davidcramer.net/code/181/custom-fields-in-django.html
# * JSONField: http://www.djangosnippets.org/snippets/377/
#
# Note that this class does not work with Django's JSON serialization,
# but works fine with the XML version.  The documentation suggests
# setting up a __unicode__() object: http://docs.djangoproject.com/en/dev/howto/custom-model-fields/
#   Put a __str__() or __unicode__() method on the class you're wrapping up
#   as a field. There are a lot of places where the default behavior of the
#   field code is to call force_unicode() on the value. (In our examples in
#   this document, value would be a Hand instance, not a HandField). So if
#   your __unicode__() method automatically converts to the string form of
#   your Python object, you can save yourself a lot of work.
# This is frustrating visually, since the JSON ends up double-quoted.
# It also means that you have to dirty your object with an extra __unicode__
# field.  You can do it, like so:
#   tft.__unicode__ = lambda: json.dumps(thrift_util.thrift2json(tft))
# but then your field is no longer equal to a Thrift object that hasn't
# been through this dirtying, and that's bad.
# So, don't use JSON serialization, and use XML serialization instead.

import json

import thrift_util

from django.db import models

class ThriftField(models.TextField):
  """
  Django field storing a Thrift item.

  See http://docs.djangoproject.com/en/dev/howto/custom-model-fields/#howto-custom-model-fields

  This stores the JSON representation of the Thrift data.
  An alternative approach is to store the bytes, but the
  JSON representation is nicer for loading up readable initial data.
  """

  def __init__(self, thrift_class, *args, **kwargs):
    self.thrift_class = thrift_class
    super(ThriftField, self).__init__(args, kwargs)

  def to_python(self, value):
    if value is None or value == "": 
      return self.thrift_class()

    if not isinstance(value, basestring): 
      return value

    jsonable = json.loads(value)
    tft = thrift_util.jsonable2thrift(jsonable, self.thrift_class)
    return tft

  def get_db_prep_save(self, value, *args, **kwargs):
    if value is None: 
      return None
    jsonable = thrift_util.thrift2json(value)
    return json.dumps(jsonable)

  def value_to_string(self, obj):
    """
    Used by XML serialization.
    """
    return json.dumps(thrift_util.thrift2json(self._get_val_from_obj(obj)))
