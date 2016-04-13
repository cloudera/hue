import cffi

#
# This is only a demo based on the GMP library.
# There is a rather more complete (but perhaps outdated) version available at:
# http://bazaar.launchpad.net/~tolot-solar-empire/+junk/gmpy_cffi/files
#

ffi = cffi.FFI()

ffi.cdef("""

    typedef struct { ...; } MP_INT;
    typedef MP_INT mpz_t[1];

    int mpz_init_set_str (MP_INT *dest_integer, char *src_cstring, int base);
    void mpz_add (MP_INT *sum, MP_INT *addend1, MP_INT *addend2);
    char * mpz_get_str (char *string, int base, MP_INT *integer);

""")

ffi.set_source('_gmp_cffi', "#include <gmp.h>",
                 libraries=['gmp', 'm'])

if __name__ == '__main__':
    ffi.compile()

