struct Foo {
    1: optional string bar (go.tag = "json:\"bar\" db:\"id_text\"")
}

struct Baz {
    1: optional string bar = "foobarbaz" (go.tag = "json:\"bar\" db:\"id_text\"")
}
