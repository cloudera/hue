from cffi import FFI
ffi = FFI()
ffi.cdef("""     // some declarations from the man page
    struct passwd {
        char *pw_name;
        ...; 
    };
    struct passwd *getpwuid(int uid);
""")

ffi.set_source('_pwuid_cffi', """   // passed to the real C compiler
#include <sys/types.h>
#include <pwd.h>
""")


if __name__ == '__main__':
    ffi.compile()
