# The following dictionary lists all names marked up as ``code`` in
# the rest documentation.  It specifies how it should be marked up in
# LaTeX.  Running mkpydoc.py writes missing entried into the
# 'missing.py' file, which should be used to update this specs:
codemarkup = {

    # types
    'c_char': 'class',
    'c_wchar': 'class',

    'c_byte': 'class',
    'c_ubyte': 'class',

    'c_short': 'class',
    'c_ushort': 'class',

    'c_int': 'class',
    'c_uint': 'class',
    'c_long': 'class',
    'c_ulong': 'class',
    'c_longlong': 'class',
    'c_ulonglong': 'class',

    'c_void_p': 'class',
    'c_char_p': 'class',
    'c_wchar_p': 'class',

    'c_float': 'class',
    'c_double': 'class',

    'LibraryLoader': 'class',

    'Structure': 'class',
    'BigEndianStructure': 'class',
    'BigEndianUnion': 'class',
    'LittleEndianStructure': 'class',
    'LittleEndianUnion': 'class',

    'Union': 'class',

    'HRESULT': 'class',

    'CDLL': 'class',
    'OleDLL': 'class',
    'PyDLL': 'class',
    'WinDLL': 'class',


    # instances
    'pythonapi': 'var',
    'windll': 'var',
    'cdll': 'var',
    'oledll': 'var',
    'pydll': 'var',

    # constants
    'RTLD_GLOBAL': 'var',
    'RTLD_LOCAL': 'var',

    # arguments (from inline code fragments)
    'dst': 'var',
    'init': 'var',
    'lib': 'var',
    'libname': 'var',
    'mode': 'var',
    'name': 'var',
    'iid': 'var',
    'index': 'var',
    'paramflags': 'var',
    'version': 'var',
    'outargs': 'var',
    'c': 'var',
    'count': 'var',
    'code': 'var',

    'library': 'var',

    # methods
    'LoadLibrary': 'method',
    'find': 'method',
    'load': 'method',
    'load_library': 'method',
    'load_version': 'method',

    'from_address': 'method',
    'from_param': 'method',
    'in_dll': 'method',

    '__getattr__': 'method',
    '__getitem__': 'method',

    # members
    'restype': 'member',
    'argtypes': 'member',
    'errcheck': 'member',

    '_fields_': 'member',
    '_pack_': 'member',
    '__ctype_be__': 'member',
    '__ctype_le__': 'member',
    '__ctypes_from_outparam__': 'member',
    '_as_parameter_': 'member',
    '_b_base_': 'member',
    '_b_needsfree_': 'member',

    '_handle': 'member',
    '_name': 'member',
    '_objects': 'member',
    '_type_': 'member',

    # functions
    'PyString_FromString': 'function',
    'PyString_FromStringAndSize': 'function',
    'PyUnicode_FromWideString': 'function',

    'DllCanUnloadNow()': 'function',
    'FormatError': 'function',
    'GetLastError()': 'function',

    'memmove': 'function',
    'memset': 'function',
    'qsort': 'function',

    'CFUNCTYPE': 'function',
    'WINFUNCTYPE': 'function',

    'byref': 'function',
    'create_string_buffer()': 'function',

    # random things
    'NULL': 'code',
    'None': 'code',
    '_': 'code',
    '__stdcall': 'code',
    'atoi': 'code',
    'c_int.__ctype_be__': 'code',
    'char': 'code',
    'dlopen': 'code',
    'dlopen()': 'code',
    'void': 'code',
    'wchar_t': 'code',
    'wcslen': 'code',
    'x': 'code',
    'y': 'code',

    'WindowsError': 'class',

}
