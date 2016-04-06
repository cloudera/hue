__author__ = "Israel Fruchter <israel.fruchter@gmail.com>"

import sys, os

if not sys.platform == 'win32':
    raise Exception("Windows-only demo")

try:
    from _winclipboard_cffi import ffi, lib
except ImportError:
    print 'run winclipboard_build first, then make sure the shared object is on sys.path'
    sys.exit(1)

# ffi "knows" about the declared variables and functions from the
#     cdef parts of the module _winclipboard_cffi created,
# lib "knows" how to call the functions from the set_source parts
#     of the module.

def CopyToClipboard(string):
    '''
        use win32 api to copy `string` to the clipboard
    '''
    hWnd = lib.GetConsoleWindow()
  
    if lib.OpenClipboard(hWnd):
        cstring = ffi.new("char[]", string)
        size = ffi.sizeof(cstring)
        
        # make it a moveable memory for other processes
        hGlobal = lib.GlobalAlloc(lib.GMEM_MOVEABLE, size)
        buffer = lib.GlobalLock(hGlobal)
        lib.memcpy(buffer, cstring, size)
        lib.GlobalUnlock(hGlobal)
        
        res = lib.EmptyClipboard()
        res = lib.SetClipboardData(lib.CF_TEXT, buffer)
 
        lib.CloseClipboard()
        
CopyToClipboard("hello world from cffi")
