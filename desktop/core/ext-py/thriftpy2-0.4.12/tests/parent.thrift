include "base.thrift"

struct Greet {
    1: optional base.Hello hello,
    2: optional base.timestamp date,
    3: optional base.Code code
    4: optional base.codelist codelist
    5: optional base.codeset codeset
    6: optional base.codemap codemap
}
