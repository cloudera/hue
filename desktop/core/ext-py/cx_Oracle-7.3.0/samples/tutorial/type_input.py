#------------------------------------------------------------------------------
# type_input.py (Section 6.3)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn)
cur = con.cursor()

# Create table
cur.execute("""begin
                 execute immediate 'drop table testgeometry';
                 exception when others then
                   if sqlcode <> -942 then
                     raise;
                   end if;
               end;""")
cur.execute("""create table testgeometry (
               id number(9) not null,
               geometry MDSYS.SDO_GEOMETRY not null)""")

# Create a Python class for an SDO
class mySDO(object):

    def __init__(self, gtype, elemInfo, ordinates):
        self.gtype = gtype
        self.elemInfo = elemInfo
        self.ordinates = ordinates

# Get Oracle type information
objType = con.gettype("MDSYS.SDO_GEOMETRY")
elementInfoTypeObj = con.gettype("MDSYS.SDO_ELEM_INFO_ARRAY")
ordinateTypeObj = con.gettype("MDSYS.SDO_ORDINATE_ARRAY")

# Convert a Python object to MDSYS.SDO_GEOMETRY
def SDOInConverter(value):
    obj = objType.newobject()
    obj.SDO_GTYPE = value.gtype
    obj.SDO_ELEM_INFO = elementInfoTypeObj.newobject()
    obj.SDO_ELEM_INFO.extend(value.elemInfo)
    obj.SDO_ORDINATES = ordinateTypeObj.newobject()
    obj.SDO_ORDINATES.extend(value.ordinates)
    return obj

def SDOInputTypeHandler(cursor, value, numElements):
    if isinstance(value, mySDO):
        return cursor.var(cx_Oracle.OBJECT, arraysize = numElements,
                inconverter = SDOInConverter, typename = objType.name)

sdo = mySDO(2003, [1, 1003, 3], [1, 1, 5, 7])  # Python object
cur.inputtypehandler = SDOInputTypeHandler
cur.execute("insert into testgeometry values (:1, :2)", (1, sdo))

# Define a function to dump the contents of an Oracle object
def dumpobject(obj, prefix = "  "):
    if obj.type.iscollection:
        print(prefix, "[")
        for value in obj.aslist():
            if isinstance(value, cx_Oracle.Object):
                dumpobject(value, prefix + "  ")
            else:
                print(prefix + "  ", repr(value))
        print(prefix, "]")
    else:
        print(prefix, "{")
        for attr in obj.type.attributes:
            value = getattr(obj, attr.name)
            if isinstance(value, cx_Oracle.Object):
                print(prefix + "  " + attr.name + " :")
                dumpobject(value, prefix + "    ")
            else:
                print(prefix + "  " + attr.name + " :", repr(value))
        print(prefix, "}")

# Query the row
print("Querying row just inserted...")
cur.execute("select id, geometry from testgeometry")
for (id, obj) in cur:
    print("Id: ", id)
    dumpobject(obj)
