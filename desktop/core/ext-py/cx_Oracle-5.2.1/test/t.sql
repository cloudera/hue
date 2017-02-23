create or replace package           pkg_TestBooleans as

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

