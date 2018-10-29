import cffi

ffibuilder = cffi.FFI()

ffibuilder.embedding_api("""
    int add(int, int);
""")

ffibuilder.embedding_init_code("""
    from _embedding_cffi import ffi
    print("preparing")   # printed once

    @ffi.def_extern()
    def add(x, y):
        print("adding %d and %d" % (x, y))
        return x + y
""")

ffibuilder.set_source("_embedding_cffi", "")

ffibuilder.compile(verbose=True)
