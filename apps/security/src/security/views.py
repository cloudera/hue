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

import json

from beeswax.api import autocomplete
from desktop.lib.django_util import render


def _get_hadoop_groups(): # Mock for now, maybe pull from LDAP
  return ['romain', 'sambashare', 'cdrom', 'lpadmin', 'admin', 'adm', 'lp', 'dialout', 'plugdev']


def hive(request):
  assist = autocomplete(request, database=None, table=None)

  #  url(r'^api/autocomplete/$', 'autocomplete', name='api_autocomplete_databases'),
  #  url(r'^api/autocomplete/(?P<database>\w+)/$', 'autocomplete', name='api_autocomplete_tables'),
  #  url(r'^api/autocomplete/(?P<database>\w+)/(?P<table>\w+)$', 'autocomplete', name='api_autocomplete_columns'),

  return render("hive.mako", request, {
      'assist': assist,
      'initial': json.dumps({'hadoop_groups': _get_hadoop_groups()}),
  })


def hdfs(request):

  return render("hdfs.mako", request, {      
      'initial': json.dumps({'user': request.user.username}),
  })
