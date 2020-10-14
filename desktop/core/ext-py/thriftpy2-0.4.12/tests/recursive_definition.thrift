service PingPong {
    Foo echo(1:Foo param)
}

struct Foo {
    1: optional Bar test,
    2: optional SomeInt some_int,
}

struct Bar {
    1: optional Foo test,
}

const SomeInt SOME_INT = [1, 2, 3]

typedef list<i32> SomeInt
