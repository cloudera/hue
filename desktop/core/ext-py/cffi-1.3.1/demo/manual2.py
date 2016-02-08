import _cffi_backend

ffi = _cffi_backend.FFI(b"manual2",
    _version = 0x2601,
    _types = b'\x00\x00\x01\x0D\x00\x00\x07\x01\x00\x00\x00\x0F\x00\x00\x00\x09\x00\x00\x00\x0B\x00\x00\x01\x03',
    _globals = (b'\xff\xff\xff\x0bAA',0,b'\xff\xff\xff\x0bBB',-1,b'\xff\xff\xff\x0bCC',2,b'\xff\xff\xff\x1fFOO',0x9999999999999999,b'\x00\x00\x00#close',0,b'\x00\x00\x05#stdout',0),
    _struct_unions = ((b'\x00\x00\x00\x03\x00\x00\x00\x00point_s',b'\x00\x00\x01\x11\xff\xff\xff\xffx',b'\x00\x00\x01\x11\xff\xff\xff\xffy'),),
    _enums = (b'\x00\x00\x00\x04\x00\x00\x00\x07myenum_e\x00AA,BB,CC',),
    _typenames = (b'\x00\x00\x00\x01myint_t',),
)



# trying it out
lib = ffi.dlopen(None)
assert lib.AA == 0
assert lib.BB == -1
assert lib.FOO == 0x9999999999999999
x = lib.close(-42)
assert x == -1

print lib.stdout

print ffi.new("struct point_s *")
print ffi.offsetof("struct point_s", "x")
print ffi.offsetof("struct point_s", "y")
print ffi.new("struct point_s[CC]")
assert ffi.sizeof("struct point_s[CC]") == 2 * ffi.sizeof("struct point_s")

print ffi.cast("enum myenum_e", 2)
print ffi.cast("myint_t", -2)
assert ffi.typeof("myint_t") == ffi.typeof("int")

del ffi, lib
