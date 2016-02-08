import sys
import cffi

#
# This is only a demo based on the GMP library.
# There is a rather more complete version available at:
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

lib = ffi.verify("#include <gmp.h>",
                 libraries=['gmp', 'm'])

# ____________________________________________________________

a = ffi.new("mpz_t")
b = ffi.new("mpz_t")

lib.mpz_init_set_str(a, sys.argv[1], 10)	# Assume decimal integers
lib.mpz_init_set_str(b, sys.argv[2], 10)	# Assume decimal integers
lib.mpz_add(a, a, b)			# a=a+b

s = lib.mpz_get_str(ffi.NULL, 10, a)
print ffi.string(s)
