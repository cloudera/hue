-------------------------------------------------------------------------------
-- drcp_query.sql (Section 2.4 and 2.5)
-------------------------------------------------------------------------------

/*-----------------------------------------------------------------------------
 * Copyright (c) 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

set echo on

-- Connect to the CDB to see pool statistics
connect sys/oracle@localhost/orcl as sysdba

col cclass_name format a30

-- Some DRCP pool statistics
select cclass_name, num_requests, num_hits, num_misses from v$cpool_cc_stats;

exit
