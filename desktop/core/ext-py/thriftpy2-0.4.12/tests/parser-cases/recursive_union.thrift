// https://github.com/Thriftpy/thriftpy2/issues/157
union Dynamic {
    1: bool boolean;
    2: i64 integer;
    3: double doubl;
    4: string str;
    5: list<Dynamic> arr;
    6: map<string, Dynamic> object;
}
