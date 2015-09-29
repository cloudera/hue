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

import logging
import sys


LOG = logging.getLogger(__name__)

try:
  from py4j.java_gateway import JavaGateway
except ImportError, e:
  LOG.exception('Failed to import py4j')


class Jdbc():

  def __init__(self, driver_name, url, username, password):
    if 'py4j' not in sys.modules:
      raise Exception('Required py4j module is not imported.')

    self.gateway = JavaGateway()

    self.jdbc_driver = driver_name
    self.db_url = url
    self.username = username
    self.password = password

    self.conn = None

  def connect(self):
    if self.conn is None:
      self.conn = self.gateway.jvm.java.sql.DriverManager.getConnection(self.db_url, self.username, self.password)

  def execute(self, statement):
    stmt = self.conn.createStatement()

    try:
      rs = stmt.executeQuery(statement)

      try:
        md = rs.getMetaData()

        rs_meta = [{
            'name': md.getColumnName(i + 1),
            'type': md.getColumnTypeName(i + 1),
            'length': md.getColumnDisplaySize(i + 1),
            'precision': md.getPrecision(i + 1),
          } for i in xrange(md.getColumnCount())]

        res = []
        while rs.next():
          row = []
          for c in xrange(md.getColumnCount()):
            row.append(rs.getString(c + 1))
          res.append(row)

        return res, rs_meta
      finally:
        rs.close()
    finally:
      stmt.close()

  def disconnect(self):
    if self.conn is not None:
      self.conn.close()
      self.conn = None
