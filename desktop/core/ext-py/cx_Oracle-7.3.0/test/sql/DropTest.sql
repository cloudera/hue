/*-----------------------------------------------------------------------------
 * Copyright 2019, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * DropTest.sql
 *   Drops database objects used for cx_Oracle tests.
 *
 * Run this like:
 *   sqlplus sys/syspassword@hostname/servicename as sysdba @DropTest
 *---------------------------------------------------------------------------*/

whenever sqlerror exit failure

-- get parameters
set echo off termout on feedback off verify off
accept main_user char default pythontest -
        prompt "Name of main schema [pythontest]: "
accept proxy_user char default pythontestproxy -
        prompt "Name of proxy schema [pythontestproxy]: "
set feedback on

-- perform work
@@DropTestExec.sql

exit

