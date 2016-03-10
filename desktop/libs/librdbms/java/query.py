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

from py4j.java_gateway import JavaGateway

gateway = JavaGateway()

jdbc_driver = 'com.mysql.jdb.Driver'
db_url = 'jdbc:mysql://localhost/hue'
username = 'root'
password = 'root'

conn = gateway.jvm.java.sql.DriverManager.getConnection(db_url, username, password)

try:
  stmt = conn.createStatement()
  try:
    rs = stmt.executeQuery('select username,email from auth_user')

    try:

      md = rs.getMetaData()

      for i in xrange(md.getColumnCount()):
        print md.getColumnTypeName(i + 1)

      while rs.next():
        username = rs.getString("username")
        email = rs.getString("email")
        print username, email
    finally:
      rs.close()
  finally:
    stmt.close()
finally:
  conn.close()
