from cffi import FFI

ffi = FFI()
ffi.cdef("""

typedef ... Display;
typedef struct { ...; } Window;

typedef struct { int type; ...; } XEvent;

Display *XOpenDisplay(char *display_name);
Window DefaultRootWindow(Display *display);
int XMapRaised(Display *display, Window w);
Window XCreateSimpleWindow(Display *display, Window parent, int x, int y,
                           unsigned int width, unsigned int height,
                           unsigned int border_width, unsigned long border,
                           unsigned long background);
int XNextEvent(Display *display, XEvent *event_return);
""")
lib = ffi.verify("""
#include <X11/Xlib.h>
""", libraries=['X11'])

globals().update(lib.__dict__)

class XError(Exception):
    pass

def main():
    display = XOpenDisplay(ffi.NULL)
    if display == ffi.NULL:
        raise XError("cannot open display")
    w = XCreateSimpleWindow(display, DefaultRootWindow(display),
                            10, 10, 500, 350, 0, 0, 0)
    XMapRaised(display, w)
    event = ffi.new("XEvent *")
    XNextEvent(display, event)

if __name__ == '__main__':
    main()
