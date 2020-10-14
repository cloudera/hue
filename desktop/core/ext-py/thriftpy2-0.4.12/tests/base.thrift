struct Hello {
    1: optional string name,
    2: optional string greet
}

enum Code {
    OK
    WARNING
    DANDER
    ERROR
    UNKNOWN
}

typedef list<Code> codelist
typedef map<Code, i64> codemap
typedef set<Code> codeset
typedef i64 timestamp
