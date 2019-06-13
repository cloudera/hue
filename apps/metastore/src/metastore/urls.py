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

from django.conf.urls import url
from metastore import views as metastore_views

urlpatterns = [
  url(r'^$', metastore_views.index, name='index'),

  url(r'^databases/?$', metastore_views.databases, name='databases'),
  url(r'^databases/drop/?$', metastore_views.drop_database, name='drop_database'),
  url(r'^databases/(?P<database>\w+)/alter$', metastore_views.alter_database, name='alter_database'),
  url(r'^databases/(?P<database>\w+)/metadata$', metastore_views.get_database_metadata, name='get_database_metadata'),

  url(r'^tables(?:/(?P<database>\w+))?/?$', metastore_views.show_tables, name='show_tables'),
  url(r'^tables/drop/(?P<database>\w+)$', metastore_views.drop_table, name='drop_table'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/?$', metastore_views.describe_table, name='describe_table'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/alter$', metastore_views.alter_table, name='alter_table'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/metadata$', metastore_views.get_table_metadata, name='get_table_metadata'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/load$', metastore_views.load_table, name='load_table'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/read$', metastore_views.read_table, name='read_table'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/queries$', metastore_views.table_queries, name='table_queries'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/partitions/?$', metastore_views.describe_partitions, name='describe_partitions'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/partitions/(?P<partition_spec>.+?)/read$', metastore_views.read_partition, name='read_partition'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/partitions/(?P<partition_spec>.+?)/browse$', metastore_views.browse_partition, name='browse_partition'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/partitions/drop$', metastore_views.drop_partition, name='drop_partition'),
  url(r'^table/(?P<database>\w+)/(?P<table>\w+)/alter_column$', metastore_views.alter_column, name='alter_column'),
]
