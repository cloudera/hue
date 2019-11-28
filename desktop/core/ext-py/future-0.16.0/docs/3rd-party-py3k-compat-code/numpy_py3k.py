"""
Python 3 compatibility tools.

"""

__all__ = ['bytes', 'asbytes', 'isfileobj', 'getexception', 'strchar',
           'unicode', 'asunicode', 'asbytes_nested', 'asunicode_nested',
           'asstr', 'open_latin1']

import sys

if sys.version_info[0] >= 3:
    import io
    bytes = bytes
    unicode = str

    def asunicode(s):
        if isinstance(s, bytes):
            return s.decode('latin1')
        return str(s)

    def asbytes(s):
        if isinstance(s, bytes):
            return s
        return str(s).encode('latin1')

    def asstr(s):
        if isinstance(s, bytes):
            return s.decode('latin1')
        return str(s)

    def isfileobj(f):
        return isinstance(f, (io.FileIO, io.BufferedReader))

    def open_latin1(filename, mode='r'):
        return open(filename, mode=mode, encoding='iso-8859-1')

    strchar = 'U'

else:
    bytes = str
    unicode = unicode
    asbytes = str
    asstr = str
    strchar = 'S'

    def isfileobj(f):
        return isinstance(f, file)

    def asunicode(s):
        if isinstance(s, unicode):
            return s
        return str(s).decode('ascii')

    def open_latin1(filename, mode='r'):
        return open(filename, mode=mode)

def getexception():
    return sys.exc_info()[1]

def asbytes_nested(x):
    if hasattr(x, '__iter__') and not isinstance(x, (bytes, unicode)):
        return [asbytes_nested(y) for y in x]
    else:
        return asbytes(x)

def asunicode_nested(x):
    if hasattr(x, '__iter__') and not isinstance(x, (bytes, unicode)):
        return [asunicode_nested(y) for y in x]
    else:
        return asunicode(x)
