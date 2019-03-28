#------------------------------------------------------------------------------
# connect_drcp.py (Section 2.3 and 2.5)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

from __future__ import print_function

import cx_Oracle
import db_config

con = cx_Oracle.connect(db_config.user, db_config.pw, db_config.dsn + ":pooled",
                        cclass="PYTHONHOL", purity=cx_Oracle.ATTR_PURITY_SELF)
print("Database version:", con.version)
