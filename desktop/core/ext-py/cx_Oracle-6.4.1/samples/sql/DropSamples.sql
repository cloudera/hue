/*-----------------------------------------------------------------------------
 * Copyright 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * DropSamples.sql
 *   Drops database objects used for cx_Oracle samples.
 *
 * Run this like:
 *   sqlplus / as sysdba @DropSamples
 *
 * Note that the script SampleEnv.sql should be modified if you would like to
 * use something other than the default schemas and passwords.
 *---------------------------------------------------------------------------*/

whenever sqlerror exit failure

-- setup environment
@@SampleEnv.sql

begin

    for r in
            ( select username
              from dba_users
              where username in (upper('&main_user'), upper('&edition_user'))
            ) loop
        execute immediate 'drop user ' || r.username || ' cascade';
    end loop;

    for r in
            ( select edition_name
              from dba_editions
              where edition_name in (upper('&edition_name'))
            ) loop
        execute immediate 'drop edition ' || r.edition_name || ' cascade';
    end loop;

end;
/

