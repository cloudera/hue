/*-----------------------------------------------------------------------------
 * SampleEnv.sql
 *   Sets up configuration for the SetupSamples.sql and DropSamples.sql
 * scripts. Change the values below if you would like to use something other
 * than the default values. Note that the environment variables noted below
 * will also need to be set, or the Python script SampleEnv.py will need to be
 * changed if non-default values are used.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * Copyright (c) 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

set echo off termout on feedback off verify off

define main_user = "pythonhol"         -- $CX_ORACLE_SAMPLES_MAIN_USER
define main_password = "welcome"       -- $CX_ORACLE_SAMPLES_MAIN_PASSWORD

prompt ************************************************************************
prompt                               CONFIGURATION
prompt ************************************************************************
prompt Main Schema: &main_user
prompt

set echo on verify on feedback on
