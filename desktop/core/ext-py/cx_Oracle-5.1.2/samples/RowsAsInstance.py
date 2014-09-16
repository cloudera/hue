#------------------------------------------------------------------------------
# RowsAsInstance.py
#   Returns rows as instances instead of tuples. See the ceDatabase.Row class
# in the cx_PyGenLib project (http://cx-pygenlib.sourceforge.net) for a more
# advanced example.
#------------------------------------------------------------------------------

import cx_Oracle

class Test(object):

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

connection = cx_Oracle.Connection("cx_Oracle/password")
cursor = connection.cursor()

# change this to True if you want to create the table, or create it using
# SQL*Plus instead; populate it with the data of your choice
if False:
    cursor.execute("""
            create table TestInstances (
              a varchar2(60) not null,
              b number(9) not null,
              c date not null
            )""")
    cursor.execute("insert into TestInstances values ('First', 5, sysdate)")
    cursor.execute("insert into TestInstances values ('Second', 25, sysdate)")
    connection.commit()

# retrieve the data and display it
cursor.execute("select * from TestInstances")
cursor.rowfactory = Test
print "Rows:"
for row in cursor:
    print "a = %s, b = %s, c = %s" % (row.a, row.b, row.c)

