import cffi

ffi = cffi.FFI()

ffi.cdef("""int my_algo(int); extern "Python" int f(int);""")

ffi.set_source("_extern_python_cffi", """
    static int f(int);
    static int my_algo(int n) {
        int i, sum = 0;
        for (i = 0; i < n; i++)
            sum += f(i);
        return sum;
    }
""")

ffi.compile()


from _extern_python_cffi import ffi, lib

@ffi.def_extern()
def f(n):
    return n * n

assert lib.my_algo(10) == 0+1+4+9+16+25+36+49+64+81
