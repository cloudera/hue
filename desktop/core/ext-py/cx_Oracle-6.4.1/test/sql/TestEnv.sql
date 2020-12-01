/*-----------------------------------------------------------------------------
 * Copyright 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * TestEnv.sql
 *   Sets up configuration for the SetupTest.sql and DropTest.sql scripts.
 * Change the values below if you would like to use something other than the
 * default values. Note that the environment variables noted below will also
 * need to be set, or the Python script TestEnv.py will need to be changed if
 * non-default values are used.
 *---------------------------------------------------------------------------*/

set echo off termout on feedback off verify off

define main_user = "cx_Oracle"          -- $CX_ORACLE_TEST_MAIN_USER
define main_password = "welcome"        -- $CX_ORACLE_TEST_MAIN_PASSWORD
define proxy_user = "cx_Oracle_proxy"   -- $CX_ORACLE_TEST_PROXY_USER
define proxy_password = "welcome"       -- $CX_ORACLE_TEST_PROXY_PASSWORD

prompt ************************************************************************
prompt                               CONFIGURATION
prompt ************************************************************************
prompt Main Schema: &main_user
prompt Proxy Schema: &proxy_user
prompt

set echo on verify on feedback on

