/*-----------------------------------------------------------------------------
 * Copyright 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * DropTest.sql
 *   Drops database objects used for testing.
 *
 * Run this like:
 *   sqlplus / as sysdba @DropTest
 *
 * Note that the script TestEnv.sql should be modified if you would like to
 * use something other than the default schemas and passwords.
 *---------------------------------------------------------------------------*/

whenever sqlerror exit failure

-- setup environment
@@TestEnv.sql

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

