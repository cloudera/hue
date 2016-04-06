import sys, os

# run xclient_build first, then make sure the shared object is on sys.path
from _xclient_cffi import ffi, lib


# ffi "knows" about the declared variables and functions from the
#     cdef parts of the module xclient_build created,
# lib "knows" how to call the functions from the set_source parts
#     of the module.


class XError(Exception):
    pass

def main():
    display = lib.XOpenDisplay(ffi.NULL)
    if display == ffi.NULL:
        raise XError("cannot open display")
    w = lib.XCreateSimpleWindow(display, lib.DefaultRootWindow(display),
                            10, 10, 500, 350, 0, 0, 0)
    lib.XMapRaised(display, w)
    event = ffi.new("XEvent *")
    lib.XNextEvent(display, event)

if __name__ == '__main__':
    main()
