# Based on http://cocoawithlove.com/2010/09/minimalist-cocoa-programming.html
# by Juraj Sukop.  This demo was eventually expanded into a more complete
# Cocoa library available at https://bitbucket.org/sukop/nspython .

from cffi import FFI

ffi = FFI()
ffi.cdef('''
    
    typedef signed char BOOL;
    
    typedef long NSInteger;
    typedef unsigned long NSUInteger;
    typedef NSInteger NSApplicationActivationPolicy;
    typedef NSUInteger NSBackingStoreType;
    typedef NSUInteger NSStringEncoding;
    
    typedef double CGFloat;
    struct CGPoint {
        CGFloat x;
        CGFloat y;
    };
    typedef struct CGPoint CGPoint;
    struct CGSize {
        CGFloat width;
        CGFloat height;
    };
    typedef struct CGSize CGSize;
    struct CGRect {
        CGPoint origin;
        CGSize size;
    };
    typedef struct CGRect CGRect;
    
    typedef CGPoint NSPoint;
    typedef CGSize NSSize;
    typedef CGRect NSRect;
    
    typedef struct objc_class *Class;
    typedef struct objc_object {
        Class isa;
    } *id;
    typedef struct objc_selector *SEL;

    SEL sel_registerName(const char *str);
    id objc_getClass(const char *name);
    id objc_msgSend(id theReceiver, SEL theSelector, ...);
    
''')

objc = ffi.dlopen('objc')
appkit = ffi.dlopen('AppKit')

nil = ffi.NULL
YES = ffi.cast('BOOL', 1)
NO = ffi.cast('BOOL', 0)

NSASCIIStringEncoding = ffi.cast('NSStringEncoding', 1)
NSApplicationActivationPolicyRegular = ffi.cast('NSApplicationActivationPolicy', 0)
NSTitledWindowMask = ffi.cast('NSUInteger', 1)
NSBackingStoreBuffered = ffi.cast('NSBackingStoreType', 2)

NSMakePoint = lambda x, y: ffi.new('NSPoint *', (x, y))[0]
NSMakeRect = lambda x, y, w, h: ffi.new('NSRect *', ((x, y), (w, h)))[0]

get, send, sel = objc.objc_getClass, objc.objc_msgSend, objc.sel_registerName
at = lambda s: send(
    get('NSString'),
    sel('stringWithCString:encoding:'),
    ffi.new('char[]', s), NSASCIIStringEncoding)

send(get('NSAutoreleasePool'), sel('new'))
app = send(get('NSApplication'), sel('sharedApplication'))
send(app, sel('setActivationPolicy:'), NSApplicationActivationPolicyRegular)

menubar = send(send(get('NSMenu'), sel('new')), sel('autorelease'))
appMenuItem = send(send(get('NSMenuItem'), sel('new')), sel('autorelease'))
send(menubar, sel('addItem:'), appMenuItem)
send(app, sel('setMainMenu:'), menubar)

appMenu = send(send(get('NSMenu'), sel('new')), sel('autorelease'))
appName = send(send(get('NSProcessInfo'), sel('processInfo')), sel('processName'))
quitTitle = send(at('Quit '), sel('stringByAppendingString:'), appName)
quitMenuItem = send(send(send(
            get('NSMenuItem'), sel('alloc')),
        sel('initWithTitle:action:keyEquivalent:'),
        quitTitle, sel('terminate:'), at('q')),
    sel('autorelease'))
send(appMenu, sel('addItem:'), quitMenuItem)
send(appMenuItem, sel('setSubmenu:'), appMenu)

window = send(send(send(
            get('NSWindow'), sel('alloc')),
        sel('initWithContentRect:styleMask:backing:defer:'),
        NSMakeRect(0, 0, 200, 200), NSTitledWindowMask, NSBackingStoreBuffered, NO),
    sel('autorelease'))
send(window, sel('cascadeTopLeftFromPoint:'), NSMakePoint(20, 20))
send(window, sel('setTitle:'), appName)
send(window, sel('makeKeyAndOrderFront:'), nil)

send(app, sel('activateIgnoringOtherApps:'), YES)
send(app, sel('run'))
