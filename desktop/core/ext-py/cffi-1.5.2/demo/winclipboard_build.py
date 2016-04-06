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

ffi.set_source('_winclipboard_cffi', '''
    #include <windows.h>
''', libraries=["user32"])

if __name__ == '__main__':
    ffi.compile()
