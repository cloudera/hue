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

ffi.set_source('_xclient_cffi', """
            #include <X11/Xlib.h>
""", libraries=['X11'])

if __name__ == '__main__':
    ffi.compile(verbose=True)
