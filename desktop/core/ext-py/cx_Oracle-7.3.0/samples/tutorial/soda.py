#------------------------------------------------------------------------------
# soda.py (Section 11.1)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2019, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)

soda = con.getSodaDatabase()

collection = soda.createCollection("friends")

content = {'name': 'Jared', 'age': 35, 'address': {'city': 'Melbourne'}}

doc = collection.insertOneAndGet(content)
key = doc.key

doc = collection.find().key(key).getOne()
content = doc.getContent()
print('Retrieved SODA document dictionary is:')
print(content)
