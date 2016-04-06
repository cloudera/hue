==================================================
CPython C extension module produced by recompile()
==================================================

Global variable::

  _cffi_opcode_t _cffi_types[];

Every _cffi_types entry is initially an odd integer.  At runtime, it
is fixed to be a `CTypeDescrObject *` when the odd integer is
interpreted and turned into a real <ctype> object.

The generated C functions are listed in _cffi_globals, a sorted array
of entries which get turned lazily into real <builtin function
objects>.  Each entry in this array has an index in the _cffi_types
array, which describe the function type (OP_FUNCTION opcode, see
below).  We turn the odd integers describing argument and return types
into real CTypeDescrObjects at the point where the entry is turned
into a real builtin function object.

The odd integers are "opcodes" that contain a type info in the lowest
byte.  The remaining high bytes of the integer is an "arg" that depends
on the type info:

OP_PRIMITIVE
    the arg tells which primitive type it is (an index in some list)

OP_POINTER
    the arg is the index of the item type in the _cffi_types array.

OP_ARRAY
    the arg is the index of the item type in the _cffi_types array.
    followed by another opcode that contains (uintptr_t)length_of_array.

OP_OPEN_ARRAY
    for syntax like "int[]".  same as OP_ARRAY but without the length

OP_STRUCT_UNION
    the arg is the index of the struct/union in _cffi_structs_unions

OP_ENUM
    the arg is the index of the enum in _cffi_enums

OP_TYPENAME
    the arg is the index of the typename in _cffi_typenames

OP_FUNCTION
    the arg is the index of the result type in _cffi_types.
    followed by other opcodes for the arguments.
    terminated by OP_FUNCTION_END.

OP_FUNCTION_END
    the arg's lowest bit is set if there is a "..." argument.

OP_NOOP
    simple indirection: the arg is the index to look further in

There are other opcodes, used not inside _cffi_types but in other
individual ``type_op`` fields.  Most importantly, these are used
on _cffi_globals entries:

OP_CPYTHON_BLTN_*
    declare a function

OP_CONSTANT
    declare a non-integral constant

OP_CONSTANT_INT
    declare an int constant

OP_GLOBAL_VAR
    declare a global var
