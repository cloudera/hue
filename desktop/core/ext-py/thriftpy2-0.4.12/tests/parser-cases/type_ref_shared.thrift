enum Country {
    UK = 0,
    US = 1,
    CN = 2
}

struct Writer {
    1: string name,
    2: i32 age,
    3: Country country,
}

struct Book {
    1: string name,
    2: Writer writer,
}
