#------------------------------------------------------------------------------
# soda.py (Section 11.2)
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

myDocs = [
    {'name': 'Gerald', 'age': 21, 'address': {'city': 'London'}},
    {'name': 'David', 'age': 28, 'address': {'city': 'Melbourne'}},
    {'name': 'Shawn', 'age': 20, 'address': {'city': 'San Francisco'}}
]
collection.insertMany(myDocs)

filterSpec = { "address.city": "Melbourne" }
myDocuments = collection.find().filter(filterSpec).getDocuments()

print('Melbourne people:')
for doc in myDocuments:
    print(doc.getContent()["name"])

filterSpec = {'age': {'$lt': 25}}
myDocuments = collection.find().filter(filterSpec).getDocuments()

print('Young people:')
for doc in myDocuments:
    print(doc.getContent()["name"])
