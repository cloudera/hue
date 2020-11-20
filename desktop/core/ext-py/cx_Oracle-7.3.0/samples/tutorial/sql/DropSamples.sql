/*-----------------------------------------------------------------------------
 * DropSamples.sql
 *   Drops database objects used for cx_Oracle HOL samples.
 *
 * Run this like:
 *   sqlplus / as sysdba @DropSamples <user>
 *
 * Note that the script SampleEnv.sql should be modified if you would like to
 * use something other than the default schemas and passwords.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * Copyright (c) 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

whenever sqlerror exit failure

-- setup environment
@@SampleEnv.sql

begin
  dbms_aqadm.stop_queue('BOOKS');
  dbms_aqadm.drop_queue('BOOKS');
  dbms_aqadm.drop_queue_table('BOOK_QUEUE_TABLE');
  exception when others then
    if sqlcode <> -24010 then
      raise;
    end if;
  end;
/

begin

    for r in
            ( select username
              from dba_users
              where username in (upper('&main_user'))
            ) loop
        execute immediate 'drop user ' || r.username || ' cascade';
    end loop;
end;
/
