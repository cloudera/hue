__author__ = "Israel Fruchter <israel.fruchter@gmail.com>"

from cffi import FFI

ffi = FFI()
ffi.cdef('''
    typedef void * HANDLE;
    typedef HANDLE HWND;
    typedef int BOOL;
    typedef unsigned int UINT;
    typedef int SIZE_T;
    typedef char * LPTSTR;
    typedef HANDLE HGLOBAL;
    typedef HANDLE LPVOID;

    HWND GetConsoleWindow(void);

    LPVOID GlobalLock( HGLOBAL hMem );
    BOOL GlobalUnlock( HGLOBAL hMem );
    HGLOBAL GlobalAlloc(UINT uFlags, SIZE_T dwBytes);

    BOOL  OpenClipboard(HWND hWndNewOwner);
    BOOL  CloseClipboard(void);
    BOOL  EmptyClipboard(void);
    HANDLE  SetClipboardData(UINT uFormat, HANDLE hMem);

    #define CF_TEXT ...
    #define GMEM_MOVEABLE ...

    void * memcpy(void * s1, void * s2, int n);
    ''')

lib = ffi.verify('''
    #include <windows.h>
''', libraries=["user32"])

globals().update(lib.__dict__)

def CopyToClipboard(string):
    '''
        use win32 api to copy `string` to the clipboard
    '''
    hWnd = GetConsoleWindow()
  
    if OpenClipboard(hWnd):
        cstring = ffi.new("char[]", string)
        size = ffi.sizeof(cstring)
        
        # make it a moveable memory for other processes
        hGlobal = GlobalAlloc(GMEM_MOVEABLE, size)
        buffer = GlobalLock(hGlobal)
        memcpy(buffer, cstring, size)
        GlobalUnlock(hGlobal)
        
        res = EmptyClipboard()
        res = SetClipboardData(CF_TEXT, buffer)
 
        CloseClipboard()
        
CopyToClipboard("hello world from cffi")
