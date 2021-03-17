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

import sys

from metastore import views as metastore_views

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  re_path(r'^$', metastore_views.index, name='index'),

  re_path(r'^databases/?$', metastore_views.databases, name='databases'),
  re_path(r'^databases/drop/?$', metastore_views.drop_database, name='drop_database'),
  re_path(r'^databases/(?P<database>[^/?]*)/alter$', metastore_views.alter_database, name='alter_database'),
  re_path(r'^databases/(?P<database>[^/?]*)/metadata$', metastore_views.get_database_metadata, name='get_database_metadata'),

  re_path(r'^tables(?:/(?P<database>[^/?]*))?/?$', metastore_views.show_tables, name='show_tables'),
  re_path(r'^tables/drop/(?P<database>[^/?]*)$', metastore_views.drop_table, name='drop_table'),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/?$', metastore_views.describe_table, name='describe_table'),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/alter$', metastore_views.alter_table, name='alter_table'),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/metadata$', metastore_views.get_table_metadata, name='get_table_metadata'),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/load$', metastore_views.load_table, name='load_table'),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/read$', metastore_views.read_table, name='read_table'),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/queries$', metastore_views.table_queries, name='table_queries'),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/partitions/?$', metastore_views.describe_partitions, name='describe_partitions'),
  re_path(
    r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/partitions/(?P<partition_spec>.+?)/read$',
    metastore_views.read_partition,
    name='read_partition'
  ),
  re_path(
    r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/partitions/(?P<partition_spec>.+?)/browse$',
    metastore_views.browse_partition,
    name='browse_partition'
  ),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/partitions/drop$', metastore_views.drop_partition, name='drop_partition'),
  re_path(r'^table/(?P<database>[^/?]*)/(?P<table>\w+)/alter_column$', metastore_views.alter_column, name='alter_column'),
]
