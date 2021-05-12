import cffi

ffi = cffi.FFI()

ffi.cdef("""
    int my_algo(int);
    typedef ... va_list;
    extern "Python" int f(int, va_list *);

    int fetch_int(va_list *);
    double fetch_double(va_list *);
    void *fetch_ptr(va_list *);
""")

ffi.set_source("_extern_python_cffi", """
    #include <stdarg.h>

    static int f(int, va_list *);

    static int f1(int n, ...)
    {
        va_list ap;
        va_start(ap, n);
        int res = f(n, &ap);
        va_end(ap);
        return res;
    }

    static int fetch_int(va_list *va) { return va_arg((*va), int); }
    static double fetch_double(va_list *va) { return va_arg((*va), double); }
    static void * fetch_ptr(va_list *va) { return va_arg((*va), void *); }
    
    static int my_algo(int n) {
        return f1(3, n, n+1, n+2) + f1(1, &n) + f1(2, 12.3, 45.6);
    }
""")

ffi.compile()


from _extern_python_cffi import ffi, lib

@ffi.def_extern()
def f(n, va):
    if n == 3:
        x = lib.fetch_int(va)
        y = lib.fetch_int(va)
        z = lib.fetch_int(va)
        print (x, y, z)
    elif n == 1:
        ptr = lib.fetch_ptr(va)
        print 'ptr to:', ffi.cast("int *", ptr)[0]
    elif n == 2:
        x = lib.fetch_double(va)
        y = lib.fetch_double(va)
        print (x, y)
    else:
        raise AssertionError(n)
    return 14

print lib.my_algo(10)
