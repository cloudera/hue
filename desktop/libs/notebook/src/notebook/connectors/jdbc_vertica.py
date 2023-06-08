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

from __future__ import division
from librdbms.jdbc import query_and_fetch

from notebook.connectors.jdbc import JdbcApi
from notebook.connectors.jdbc import Assist
import time
import logging
import math


LOG = logging.getLogger()


class JdbcApiVertica(JdbcApi):
    def _createAssist(self, db):
        return VerticaAssist(db)


class VerticaAssist(Assist):
    cached_data = {}  # {key: {time: 123, result: some result}}
    freeze_time = 30  # sec
    cache_use_stat = {"query": 0, "cache": 0}

    def get_databases(self):
        cache_key = str(self.db.db_url)
        if (
            cache_key not in self.cached_data
            or time.time() - self.cached_data[cache_key]["time"] > self.freeze_time
        ):
            dbs, description = query_and_fetch(
                self.db,
                "select schema_name FROM v_catalog.schemata where is_system_schema=0 and schema_name not in ('v_func', 'v_txtindex') order by 1",
            )
            list_of_db = [db[0] and db[0].strip() for db in dbs]
            VerticaAssist.cached_data[cache_key] = {
                "time": time.time(),
                "result": list_of_db,
            }
            VerticaAssist.cache_use_stat["query"] += 1
        else:
            VerticaAssist.cache_use_stat["cache"] += 1
            if self.cache_use_stat["cache"] % 5 == 0:
                LOG.info(
                    "Autocomplete data, vertica: "
                    + str(self.cache_use_stat["query"])
                    + " cache: "
                    + str(self.cache_use_stat["cache"])
                    + ", cache is used in "
                    + "%.2f"
                    % (
                        math.floor(100
                        * float(self.cache_use_stat["cache"]) / (self.cache_use_stat["query"] + self.cache_use_stat["cache"]))
                    )
                    + "% cases"
                )
        return self.cached_data[cache_key]["result"]

    def get_tables_full(self, database, table_names=[]):
        cache_key = str(self.db.db_url) + str(database)
        if (
            cache_key not in self.cached_data
            or time.time() - self.cached_data[cache_key]["time"] > self.freeze_time
        ):
            tables, description = query_and_fetch(
                self.db,
                "SELECT table_name, '' FROM v_catalog.tables WHERE table_schema='%s' order by 1"
                % database,
            )
            list_of_tables = [
                {
                    "comment": table[1] and table[1].strip(),
                    "type": "Table",
                    "name": table[0] and table[0].strip(),
                }
                for table in tables
            ]
            VerticaAssist.cached_data[cache_key] = {
                "time": time.time(),
                "result": list_of_tables,
            }
            VerticaAssist.cache_use_stat["query"] += 1
        else:
            VerticaAssist.cache_use_stat["cache"] += 1
        return self.cached_data[cache_key]["result"]

    def get_columns_full(self, database, table):
        cache_key = str(self.db.db_url) + str(database) + str(table)
        if (
            cache_key not in self.cached_data
            or time.time() - self.cached_data[cache_key]["time"] > self.freeze_time
        ):
            columns, description = query_and_fetch(
                self.db,
                "select column_name, data_type, '' from v_catalog.columns where table_schema='%s' and table_name='%s' order by 1"
                % (database, table),
            )
            list_of_columns = [
                {
                    "comment": col[2] and col[2].strip(),
                    "type": col[1],
                    "name": col[0] and col[0].strip(),
                }
                for col in columns
            ]
            VerticaAssist.cached_data[cache_key] = {
                "time": time.time(),
                "result": list_of_columns,
            }
            VerticaAssist.cache_use_stat["query"] += 1
        else:
            VerticaAssist.cache_use_stat["cache"] += 1
        return VerticaAssist.cached_data[cache_key]["result"]

    def get_sample_data(self, database, table, column=None):
        column = column or "*"
        return query_and_fetch(
            self.db, "SELECT %s FROM %s.%s limit 10" % (column, database, table)
        )
