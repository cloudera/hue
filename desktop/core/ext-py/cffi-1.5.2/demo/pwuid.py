import sys, os

# run pwuid_build first, then make sure the shared object is on sys.path
from _pwuid_cffi import ffi, lib


print ffi.string(lib.getpwuid(0).pw_name)
