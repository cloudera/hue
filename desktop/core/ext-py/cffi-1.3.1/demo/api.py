import cffi
from cffi import FFI

class PythonFFI(FFI):

    def __init__(self, backend=None):
        FFI.__init__(self, backend=backend)
        self._pyexports = {}

    def pyexport(self, signature):
        tp = self._typeof(signature, consider_function_as_funcptr=True)
        def decorator(func):
            name = func.__name__
            if name in self._pyexports:
                raise cffi.CDefError("duplicate pyexport'ed function %r"
                                     % (name,))
            callback_var = self.getctype(tp, name)
            self.cdef("%s;" % callback_var)
            self._pyexports[name] = _PyExport(tp, func)
        return decorator

    def verify(self, source='', **kwargs):
        extras = []
        pyexports = sorted(self._pyexports.items())
        for name, export in pyexports:
            callback_var = self.getctype(export.tp, name)
            extras.append("%s;" % callback_var)
        extras.append(source)
        source = '\n'.join(extras)
        lib = FFI.verify(self, source, **kwargs)
        for name, export in pyexports:
            cb = self.callback(export.tp, export.func)
            export.cb = cb
            setattr(lib, name, cb)
        return lib


class _PyExport(object):
    def __init__(self, tp, func):
        self.tp = tp
        self.func = func


if __name__ == '__main__':
    ffi = PythonFFI()

    @ffi.pyexport("int(int)")
    def add1(n):
        print n
        return n + 1

    ffi.cdef("""
        int f(int);
    """)

    lib = ffi.verify("""
        int f(int x) {
            return add1(add1(x));
        }
    """)

    assert lib.f(5) == 7
