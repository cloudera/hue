-------------------------------------------------------------------------------
-- query_arraysize.sql (Section 3.5)
-------------------------------------------------------------------------------

/*-----------------------------------------------------------------------------
 * Copyright (c) 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

set echo on

@@db_config.sql
connect &user/&pw@&connect_string

begin
  execute immediate 'drop table bigtab';
exception
when others then
  if sqlcode not in (-00942) then
    raise;
  end if;
end;
/

create table bigtab (mycol varchar2(20));
begin
  for i in 1..20000
  loop
   insert into bigtab (mycol) values (dbms_random.string('A',20));
  end loop;
end;
/
show errors

commit;

exit
