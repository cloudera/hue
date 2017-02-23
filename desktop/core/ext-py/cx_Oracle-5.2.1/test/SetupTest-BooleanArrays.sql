/*-----------------------------------------------------------------------------
 * SetupTest.sql
 *   Creates a user named "cx_Oracle" and populates its schema with the tables
 * and packages necessary for performing the test suite.
 *---------------------------------------------------------------------------*/

whenever sqlerror exit failure

-- drop existing users, if present
begin
  for r in
      ( select username
        from dba_users
        where username in ('CX_ORACLE', 'CX_ORACLE_PROXY')
      ) loop
    execute immediate 'drop user ' || r.username || ' cascade';
  end loop;
end;
/

alter session set nls_date_format = 'YYYY-MM-DD HH24:MI:SS';
alter session set nls_numeric_characters='.,';

create user cx_Oracle identified by dev
quota unlimited on users
default tablespace users;

create user cx_Oracle_proxy identified by dev;
alter user cx_Oracle_proxy grant connect through cx_Oracle;

grant create session to cx_Oracle_proxy;

grant
  create session,
  create table,
  create procedure,
  create type
to cx_Oracle;

-- create types
create type cx_Oracle.udt_Object as object (
  NumberValue           number,
  StringValue           varchar2(60),
  FixedCharValue        char(10),
  DateValue             date,
  TimestampValue        timestamp
);
/

create type cx_Oracle.udt_Array as varray(10) of number;
/

-- create tables
create table cx_Oracle.TestNumbers (
  IntCol                number(9) not null,
  NumberCol             number(9, 2) not null,
  FloatCol              float not null,
  UnconstrainedCol      number not null,
  NullableCol           number(38)
) tablespace users;

create table cx_Oracle.TestStrings (
  IntCol                number(9) not null,
  StringCol             varchar2(20) not null,
  RawCol                raw(30) not null,
  FixedCharCol          char(40) not null,
  NullableCol           varchar2(50)
) tablespace users;

create table cx_Oracle.TestUnicodes (
  IntCol                number(9) not null,
  UnicodeCol            nvarchar2(20) not null,
  FixedUnicodeCol       nchar(40) not null,
  NullableCol           nvarchar2(50)
) tablespace users;

create table cx_Oracle.TestDates (
  IntCol                number(9) not null,
  DateCol               date not null,
  NullableCol           date
) tablespace users;

create table cx_Oracle.TestCLOBs (
  IntCol                number(9) not null,
  CLOBCol               clob not null
) tablespace users;

create table cx_Oracle.TestNCLOBs (
  IntCol                number(9) not null,
  NCLOBCol              nclob not null
) tablespace users;

create table cx_Oracle.TestBLOBs (
  IntCol                number(9) not null,
  BLOBCol               blob not null
) tablespace users;

create table cx_Oracle.TestLongs (
  IntCol                number(9) not null,
  LongCol               long not null
) tablespace users;

create table cx_Oracle.TestLongRaws (
  IntCol                number(9) not null,
  LongRawCol            long raw not null
) tablespace users;

create table cx_Oracle.TestExecuteMany (
  IntCol                number(9) not null,
  StringCol             varchar2(100),
  constraint TestExecuteMany_pk primary key (IntCol)
      using index tablespace users
) tablespace users;

create table cx_Oracle.TestArrayDML (
  IntCol                number(9) not null,
  StringCol             varchar2(100),
  IntCol2               number(3),
  constraint TestArrayDML_pk primary key (IntCol)
      using index tablespace users
) tablespace users;

create table cx_Oracle.TestObjects (
  IntCol                number(9) not null,
  ObjectCol             cx_Oracle.udt_Object,
  ArrayCol              cx_Oracle.udt_Array
);

create table cx_Oracle.TestTimestamps (
  IntCol                number(9) not null,
  TimestampCol          timestamp not null,
  NullableCol           timestamp
) tablespace users;

create table cx_Oracle.TestIntervals (
  IntCol                number(9) not null,
  IntervalCol           interval day to second not null,
  NullableCol           interval day to second
) tablespace users;

-- populate tables
begin
  for i in 1..10 loop
    insert into cx_Oracle.TestNumbers
    values (i, i + i * 0.25, i + i * .75, i * i * i + i *.5,
        decode(mod(i, 2), 0, null, power(143, i)));
  end loop;
end;
/

declare

  t_RawValue            raw(30);

  function ConvertHexDigit(a_Value number) return varchar2 is
  begin
    if a_Value between 0 and 9 then
      return to_char(a_Value);
    end if;
    return chr(ascii('A') + a_Value - 10);
  end;

  function ConvertToHex(a_Value varchar2) return varchar2 is
    t_HexValue          varchar2(60);
    t_Digit             number;
  begin
    for i in 1..length(a_Value) loop
      t_Digit := ascii(substr(a_Value, i, 1));
      t_HexValue := t_HexValue ||
          ConvertHexDigit(trunc(t_Digit / 16)) ||
          ConvertHexDigit(mod(t_Digit, 16));
    end loop;
    return t_HexValue;
  end;

begin
  for i in 1..10 loop
    t_RawValue := hextoraw(ConvertToHex('Raw ' || to_char(i)));
    insert into cx_Oracle.TestStrings
    values (i, 'String ' || to_char(i), t_RawValue,
        'Fixed Char ' || to_char(i),
        decode(mod(i, 2), 0, null, 'Nullable ' || to_char(i)));
  end loop;
end;
/

begin
  for i in 1..10 loop
    insert into cx_Oracle.TestUnicodes
    values (i, 'Unicode ' || unistr('\3042') || ' ' || to_char(i),
        'Fixed Unicode ' || to_char(i),
        decode(mod(i, 2), 0, null, unistr('Nullable ') || to_char(i)));
  end loop;
end;
/

begin
  for i in 1..10 loop
    insert into cx_Oracle.TestDates
    values (i, to_date(20021209, 'YYYYMMDD') + i + i * .1,
        decode(mod(i, 2), 0, null,
        to_date(20021209, 'YYYYMMDD') + i + i + i * .15));
  end loop;
end;
/

begin
  for i in 1..10 loop
    insert into cx_Oracle.TestTimestamps
    values (i, to_timestamp('20021209', 'YYYYMMDD') +
            to_dsinterval(to_char(i) || ' 00:00:' || to_char(i * 2) || '.' ||
                    to_char(i * 50)),
        decode(mod(i, 2), 0, to_timestamp(null, 'YYYYMMDD'),
        to_timestamp('20021209', 'YYYYMMDD') +
            to_dsinterval(to_char(i + 1) || ' 00:00:' ||
                    to_char(i * 3) || '.' || to_char(i * 125))));
  end loop;
end;
/

begin
  for i in 1..10 loop
    insert into cx_Oracle.TestIntervals
    values (i, to_dsinterval(to_char(i) || ' ' || to_char(i) || ':' ||
            to_char(i * 2) || ':' || to_char(i * 3)),
            decode(mod(i, 2), 0, to_dsinterval(null),
            to_dsinterval(to_char(i + 5) || ' ' || to_char(i + 2) || ':' ||
            to_char(i * 2 + 5) || ':' || to_char(i * 3 + 5))));
  end loop;
end;
/

insert into cx_Oracle.TestObjects values (1,
    cx_Oracle.udt_Object(1, 'First row', 'First',
        to_date(20070306, 'YYYYMMDD'),
        to_timestamp('20080912 16:40:00', 'YYYYMMDD HH24:MI:SS')),
    cx_Oracle.udt_Array(5, 10, null, 20));

insert into cx_Oracle.TestObjects values (2, null,
    cx_Oracle.udt_Array(3, null, 9, 12, 15));

insert into cx_Oracle.TestObjects values (3,
    cx_Oracle.udt_Object(3, 'Third row', 'Third',
        to_date(20070621, 'YYYYMMDD'),
        to_timestamp('20071213 07:30:45', 'YYYYMMDD HH24:MI:SS')), null);

commit;

-- create procedures for testing callproc()
create procedure cx_Oracle.proc_Test (
  a_InValue             varchar2,
  a_InOutValue          in out number,
  a_OutValue            out number
) as
begin
  a_InOutValue := a_InOutValue * length(a_InValue);
  a_OutValue := length(a_InValue);
end;
/

create procedure cx_Oracle.proc_TestNoArgs as
begin
  null;
end;
/

-- create functions for testing callfunc()
create function cx_Oracle.func_Test (
  a_String              varchar2,
  a_ExtraAmount         number
) return number as
begin
  return length(a_String) + a_ExtraAmount;
end;
/

create function cx_Oracle.func_TestNoArgs
return number as
begin
  return 712;
end;
/

-- create packages
create or replace package cx_Oracle.pkg_TestStringArrays as

  type udt_StringList is table of varchar2(100) index by binary_integer;

  function TestInArrays (
    a_StartingLength    number,
    a_Array             udt_StringList
  ) return number;

  procedure TestInOutArrays (
    a_NumElems          number,
    a_Array             in out nocopy udt_StringList
  );

  procedure TestOutArrays (
    a_NumElems          number,
    a_Array             out nocopy udt_StringList
  );

end;
/

create or replace package body cx_Oracle.pkg_TestStringArrays as

  function TestInArrays (
    a_StartingLength    number,
    a_Array             udt_StringList
  ) return number is
    t_Length            number;
  begin
    t_Length := a_StartingLength;
    for i in 1..a_Array.count loop
      t_Length := t_Length + length(a_Array(i));
    end loop;
    return t_Length;
  end;

  procedure TestInOutArrays (
    a_NumElems          number,
    a_Array             in out udt_StringList
  ) is
  begin
    for i in 1..a_NumElems loop
      a_Array(i) := 'Converted element # ' ||
          to_char(i) || ' originally had length ' ||
          to_char(length(a_Array(i)));
    end loop;
  end;

  procedure TestOutArrays (
    a_NumElems          number,
    a_Array             out udt_StringList
  ) is
  begin
    for i in 1..a_NumElems loop
      a_Array(i) := 'Test out element # ' || to_char(i);
    end loop;
  end;

end;
/

create or replace package cx_Oracle.pkg_TestUnicodeArrays as

  type udt_UnicodeList is table of nvarchar2(100) index by binary_integer;

  function TestInArrays (
    a_StartingLength    number,
    a_Array             udt_UnicodeList
  ) return number;

  procedure TestInOutArrays (
    a_NumElems          number,
    a_Array             in out nocopy udt_UnicodeList
  );

  procedure TestOutArrays (
    a_NumElems          number,
    a_Array             out nocopy udt_UnicodeList
  );

end;
/

create or replace package body cx_Oracle.pkg_TestUnicodeArrays as

  function TestInArrays (
    a_StartingLength    number,
    a_Array             udt_UnicodeList
  ) return number is
    t_Length            number;
  begin
    t_Length := a_StartingLength;
    for i in 1..a_Array.count loop
      t_Length := t_Length + length(a_Array(i));
    end loop;
    return t_Length;
  end;

  procedure TestInOutArrays (
    a_NumElems          number,
    a_Array             in out udt_UnicodeList
  ) is
  begin
    for i in 1..a_NumElems loop
      a_Array(i) := unistr('Converted element ' || unistr('\3042') ||
          ' # ') || to_char(i) || ' originally had length ' ||
          to_char(length(a_Array(i)));
    end loop;
  end;

  procedure TestOutArrays (
    a_NumElems          number,
    a_Array             out udt_UnicodeList
  ) is
  begin
    for i in 1..a_NumElems loop
      a_Array(i) := unistr('Test out element ') || unistr('\3042') || ' # ' ||
          to_char(i);
    end loop;
  end;

end;
/

create or replace package cx_Oracle.pkg_TestNumberArrays as

  type udt_NumberList is table of number index by binary_integer;

  function TestInArrays (
    a_StartingValue     number,
    a_Array             udt_NumberList
  ) return number;

  procedure TestInOutArrays (
    a_NumElems          number,
    a_Array             in out nocopy udt_NumberList
  );

  procedure TestOutArrays (
    a_NumElems          number,
    a_Array             out nocopy udt_NumberList
  );

end;
/

create or replace package body cx_Oracle.pkg_TestNumberArrays as

  function TestInArrays (
    a_StartingValue     number,
    a_Array             udt_NumberList
  ) return number is
    t_Value             number;
  begin
    t_Value := a_StartingValue;
    for i in 1..a_Array.count loop
      t_Value := t_Value + a_Array(i);
    end loop;
    return t_Value;
  end;

  procedure TestInOutArrays (
    a_NumElems          number,
    a_Array             in out udt_NumberList
  ) is
  begin
    for i in 1..a_NumElems loop
      a_Array(i) := a_Array(i) * 10;
    end loop;
  end;

  procedure TestOutArrays (
    a_NumElems          number,
    a_Array             out udt_NumberList
  ) is
  begin
    for i in 1..a_NumElems loop
      a_Array(i) := i * 100;
    end loop;
  end;

end;
/

create or replace package cx_Oracle.pkg_TestDateArrays as

  type udt_DateList is table of date index by binary_integer;

  function TestInArrays (
    a_StartingValue     number,
    a_BaseDate          date,
    a_Array             udt_DateList
  ) return number;

  procedure TestInOutArrays (
    a_NumElems          number,
    a_Array             in out nocopy udt_DateList
  );

  procedure TestOutArrays (
    a_NumElems          number,
    a_Array             out nocopy udt_DateList
  );

end;
/

create or replace package body cx_Oracle.pkg_TestDateArrays as

  function TestInArrays (
    a_StartingValue     number,
    a_BaseDate          date,
    a_Array             udt_DateList
  ) return number is
    t_Value             number;
  begin
    t_Value := a_StartingValue;
    for i in 1..a_Array.count loop
      t_Value := t_Value + a_Array(i) - a_BaseDate;
    end loop;
    return t_Value;
  end;

  procedure TestInOutArrays (
    a_NumElems          number,
    a_Array             in out udt_DateList
  ) is
  begin
    for i in 1..a_NumElems loop
      a_Array(i) := a_Array(i) + 7;
    end loop;
  end;

  procedure TestOutArrays (
    a_NumElems          number,
    a_Array             out udt_DateList
  ) is
  begin
    for i in 1..a_NumElems loop
      a_Array(i) := to_date(20021212, 'YYYYMMDD') + i * 1.2;
    end loop;
  end;

end;
/

create or replace package cx_Oracle.pkg_TestOutCursors as

  type udt_RefCursor is ref cursor;

  procedure TestOutCursor (
    a_MaxIntValue       number,
    a_Cursor            out udt_RefCursor
  );

end;
/

create or replace package body cx_Oracle.pkg_TestOutCursors as

  procedure TestOutCursor (
    a_MaxIntValue       number,
    a_Cursor            out udt_RefCursor
  ) is
  begin
    open a_Cursor for
      select
        IntCol,
        StringCol
      from TestStrings
      where IntCol <= a_MaxIntValue
      order by IntCol;
  end;

end;
/

create or replace package cx_Oracle.pkg_TestBooleans as

    type udt_BooleanList is table of boolean index by binary_integer;

    function GetStringRep (
        a_Value             boolean
    ) return varchar2;

    function IsLessThan10 (
        a_Value             number
    ) return boolean;

    function TestInArrays (
        a_Array             udt_BooleanList
    ) return number;

    procedure TestInOutArrays (
        a_NumElems          number,
        a_Array             in out nocopy udt_BooleanList
    );

    procedure TestOutArrays (
        a_NumElems          number,
        a_Array             out nocopy udt_BooleanList
    );

end;
/

create or replace package body cx_Oracle.pkg_TestBooleans as

    function GetStringRep (
        a_Value             boolean
    ) return varchar2 is
    begin
        if a_Value is null then
            return 'NULL';
        elsif a_Value then
            return 'TRUE';
        end if;
        return 'FALSE';
    end;

    function IsLessThan10 (
        a_Value             number
    ) return boolean is
    begin
        return a_Value < 10;
    end;

    function TestInArrays (
        a_Array             udt_BooleanList
    ) return number is
        t_Result            number;
    begin
        t_Result := 0;
        for i in 1..a_Array.count loop
            if a_Array(i) then
                t_Result := t_Result + 1;
            end if;
        end loop;
        return t_Result;
    end;

    procedure TestInOutArrays (
        a_NumElems          number,
        a_Array             in out nocopy udt_BooleanList
    ) is
    begin
        for i in 1..a_Array.count loop
            if i <= a_NumElems then
                a_Array(i) := not a_Array(i);
            else
                a_Array(i) := false;
            end if;
        end loop;
    end;

    procedure TestOutArrays (
        a_NumElems          number,
        a_Array             out nocopy udt_BooleanList
    ) is
    begin
        for i in 1..a_Array.count loop
            a_Array(i) := mod(i, a_NumElems) = 0;
        end loop;
    end;

end;
/

exit

