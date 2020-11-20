/*-----------------------------------------------------------------------------
 * Copyright (c) 2017, 2019, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * DropTestExec.sql
 *   This script performs the actual work of dropping the database schemas used
 * by the cx_Oracle test suite. It is called by the DropTest.sql and
 * SetupTest.sql scripts after acquiring the necessary parameters and also by
 * the Python script DropTest.py.
 *---------------------------------------------------------------------------*/

begin

    for r in
            ( select username
              from dba_users
              where username in (upper('&main_user'), upper('&proxy_user'))
            ) loop
        execute immediate 'drop user ' || r.username || ' cascade';
    end loop;

end;
/

