/*-----------------------------------------------------------------------------
 * Copyright 2019, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * SetupTest.sql
 *   Creates and populates schemas with the database objects used by the
 * cx_Oracle test suite.
 *
 * Run this like:
 *   sqlplus sys/syspassword@hostname/servicename as sysdba @SetupTest
 *---------------------------------------------------------------------------*/

whenever sqlerror exit failure

-- get parameters
set echo off termout on feedback off verify off
accept main_user char default pythontest -
        prompt "Name of main schema [pythontest]: "
accept main_password char prompt "Password for &main_user: " HIDE
accept proxy_user char default pythontestproxy -
        prompt "Name of edition schema [pythontestproxy]: "
accept proxy_password char prompt "Password for &proxy_user: " HIDE
set feedback on

-- perform work
@@DropTestExec.sql
@@SetupTestExec.sql

exit

