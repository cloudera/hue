#------------------------------------------------------------------------------
# bind_sdo.py (Section 4.4)
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

# Create and populate Oracle objects
typeObj = con.gettype("MDSYS.SDO_GEOMETRY")
elementInfoTypeObj = con.gettype("MDSYS.SDO_ELEM_INFO_ARRAY")
ordinateTypeObj = con.gettype("MDSYS.SDO_ORDINATE_ARRAY")
obj = typeObj.newobject()
obj.SDO_GTYPE = 2003
obj.SDO_ELEM_INFO = elementInfoTypeObj.newobject()
obj.SDO_ELEM_INFO.extend([1, 1003, 3])
obj.SDO_ORDINATES = ordinateTypeObj.newobject()
obj.SDO_ORDINATES.extend([1, 1, 5, 7])

pointTypeObj = con.gettype("MDSYS.SDO_POINT_TYPE")
obj.SDO_POINT = pointTypeObj.newobject()
obj.SDO_POINT.X = 1
obj.SDO_POINT.Y = 2
obj.SDO_POINT.Z = 3

print("Created object", obj)

# Add a new row
print("Adding row to table...")
cur.execute("insert into testgeometry values (1, :objbv)", objbv = obj)
print("Row added!")

# (Change below here)

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
