import sys
#
# This is only a demo based on the GMP library.
# There is a rather more complete (but perhaps outdated) version available at:
# http://bazaar.launchpad.net/~tolot-solar-empire/+junk/gmpy_cffi/files
#

try:
    from _gmp_cffi import ffi, lib
except ImportError:
    print 'run gmp_build first, then make sure the shared object is on sys.path'
    sys.exit(1)

# ffi "knows" about the declared variables and functions from the
#     cdef parts of the module created from gmp_build
# lib "knows" how to call the functions from the set_source parts
#     of the module.

# ____________________________________________________________

a = ffi.new("mpz_t")
b = ffi.new("mpz_t")

if len(sys.argv) < 3:
    print 'call as %s bigint1, bigint2' % sys.argv[0]
    sys.exit(2)

lib.mpz_init_set_str(a, sys.argv[1], 10)	# Assume decimal integers
lib.mpz_init_set_str(b, sys.argv[2], 10)	# Assume decimal integers
lib.mpz_add(a, a, b)			# a=a+b

s = lib.mpz_get_str(ffi.NULL, 10, a)
print ffi.string(s)
