Open Source Python/Oracle Utility - cx_Oracle
---------------------------------------------
cx_Oracle is a Python extension module that allows access to Oracle and 
conforms to the Python database API 2.0 specifications with a number of
additions. The method cursor.nextset() and the time data type are not
supported by Oracle and are therefore not implemented.

See http://www.python.org/topics/database/DatabaseAPI-2.0.html for more
information on the Python database API specification. See the included
documentation for additional information.

For feedback or patches, contact Anthony Tuininga at
anthony.tuininga@gmail.com. For help or to ask questions, please use the
mailing list at http://lists.sourceforge.net/lists/listinfo/cx-oracle-users.

Please note that an Oracle client (or server) installation is required in order
to use cx_Oracle. If you do not require the tools that come with a full client
installation, it is recommended to install the Instant Client which is far
easier to install.


Binary Install
--------------
Place the file cx_Oracle.pyd or cx_Oracle.so anywhere on your Python path.


Source Install
--------------
This module has been built with Oracle 10g, 11g and 12c on Linux and Windows.
Others have reported success with other platforms such as Mac OS X.

For simplified installation use pip

    pip install cx_Oracle

Otherwise, you can use the provided setup.py to build and install the module

    python setup.py build
    python setup.py install

See BUILD.txt for additional information.


Usage Example
-------------

import cx_Oracle

# connect via SQL*Net string or by each segment in a separate argument
#connection = cx_Oracle.connect("user/password@TNS")
connection = cx_Oracle.connect("user", "password", "TNS")

cursor = connection.cursor()
cursor.execute("""
        select Col1, Col2, Col3
        from SomeTable
        where Col4 = :arg_1
          and Col5 between :arg_2 and :arg_3""",
        arg_1 = "VALUE",
        arg_2 = 5,
        arg_3 = 15)
for column_1, column_2, column_3 in cursor:
    print "Values:", column_1, column_2, column_3


For more examples, please see the test suite in the test directory and the
samples in the samples directory. You can also look at the scripts in the
cx_OracleTools (http://cx-oracletools.sourceforge.net) and the modules in the
cx_PyOracleLib (http://cx-pyoraclelib.sourceforge.net) projects.

For further information see

http://cx_oracle.readthedocs.org

