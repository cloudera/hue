const bool tbool = true
const bool tboolint = 1
const byte tbyte = 3
const i8 int8 = 3
const i16 int16 = 3
const i32 int32 = 800
const i64 int64 = 123456789
const string tstr = "hello world"
const double tdouble = 1.3
typedef i32 Integer32
const Integer32 integer32 = 900
const list<i32> tlist = [1, 2, 3]
const set<i32> tset = [1, 2, 3]
const map<string, string> tmap1 = {"key": "val"}
const map<string, Integer32> tmap2 = {"key": 32}

# https://github.com/Thriftpy/thriftpy2/pull/69
enum Country {
    US = 1,
    UK = 2,
    CA = 3,
    CN = 4
}

const Country my_country = Country.CN;

struct Person {
    1: string name,
    2: Country country = Country.US
}

const Person tom = {"name": "tom"}

# https://github.com/Thriftpy/thriftpy2/issues/75
const map<Country, string> country_map = {
    Country.US: "US", Country.UK: "UK", Country.CA: "CA", Country.CN: "CN"}
