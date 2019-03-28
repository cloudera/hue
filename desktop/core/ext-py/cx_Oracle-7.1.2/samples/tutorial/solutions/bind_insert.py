#------------------------------------------------------------------------------
# bind_insert.py (Section 4.3)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)
cur = con.cursor()

rows = [ (1, "First" ), (2, "Second" ),
         (3, "Third" ), (4, "Fourth" ),
         (5, "Fifth" ), (6, "Sixth" ),
         (6, "Duplicate" ),
         (7, "Seventh" ) ]

cur.executemany("insert into mytab(id, data) values (:1, :2)", rows, batcherrors = True)

for error in cur.getbatcherrors():
    print("Error", error.message.rstrip(), "at row offset", error.offset)

# Now query the results back

cur2 = con.cursor()
cur2.execute('select * from mytab')
res = cur2.fetchall()
print(res)
