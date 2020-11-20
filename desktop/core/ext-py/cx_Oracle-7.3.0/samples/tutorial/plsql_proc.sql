-------------------------------------------------------------------------------
-- plsql_proc.sql (Section 5.2)
-------------------------------------------------------------------------------

/*-----------------------------------------------------------------------------
 * Copyright (c) 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

set echo on

@@db_config.sql
connect &user/&pw@&connect_string

create or replace procedure myproc(v1_p in number, v2_p out number) as
begin
  v2_p := v1_p * 2;
end;
/
show errors

exit
