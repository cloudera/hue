-------------------------------------------------------------------------------
-- bind_insert.sql (Section 4.2)
-------------------------------------------------------------------------------

/*-----------------------------------------------------------------------------
 * Copyright (c) 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

set echo on

@@db_config.sql
connect &user/&pw@&connect_string

begin
  execute immediate 'drop table mytab';
exception
when others then
  if sqlcode not in (-00942) then
    raise;
  end if;
end;
/

create table mytab (id number, data varchar2(20), constraint my_pk primary key (id));

exit
