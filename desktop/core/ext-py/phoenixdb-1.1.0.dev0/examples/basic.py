#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import phoenixdb

with phoenixdb.connect('http://localhost:8765/', autocommit=True) as connection:
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS test")
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, text VARCHAR)")
        cursor.executemany("UPSERT INTO test VALUES (?, ?)", [[1, 'hello'], [2, 'world']])
        cursor.execute("SELECT * FROM test ORDER BY id")
        for row in cursor:
            print(row)
