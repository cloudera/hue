//-----------------------------------------------------------------------------
// StringVar.c
//   Defines the routines specific to the string type.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// String type
//-----------------------------------------------------------------------------
typedef struct {
    Variable_HEAD
    char *data;
} udt_StringVar;


//-----------------------------------------------------------------------------
// Declaration of string variable functions.
//-----------------------------------------------------------------------------
static int StringVar_Initialize(udt_StringVar*, udt_Cursor*);
static int StringVar_SetValue(udt_StringVar*, unsigned, PyObject*);
static PyObject *StringVar_GetValue(udt_StringVar*, unsigned);
static int StringVar_PostDefine(udt_StringVar*);
static ub4 StringVar_GetBufferSize(udt_StringVar*);

//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
static PyTypeObject g_StringVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.STRING",                 // tp_name
    sizeof(udt_StringVar),              // tp_basicsize
    0,                                  // tp_itemsize
    0,                                  // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    0,                                  // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    0,                                  // tp_call
    0,                                  // tp_str
    0,                                  // tp_getattro
    0,                                  // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0                                   // tp_doc
};


static PyTypeObject g_NCharVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.NCHAR",                  // tp_name
    sizeof(udt_StringVar),              // tp_basicsize
    0,                                  // tp_itemsize
    0,                                  // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    0,                                  // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    0,                                  // tp_call
    0,                                  // tp_str
    0,                                  // tp_getattro
    0,                                  // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0                                   // tp_doc
};


static PyTypeObject g_FixedCharVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.FIXED_CHAR",             // tp_name
    sizeof(udt_StringVar),              // tp_basicsize
    0,                                  // tp_itemsize
    0,                                  // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    0,                                  // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    0,                                  // tp_call
    0,                                  // tp_str
    0,                                  // tp_getattro
    0,                                  // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0                                   // tp_doc
};


static PyTypeObject g_FixedNCharVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.FIXED_NCHAR",            // tp_name
    sizeof(udt_StringVar),              // tp_basicsize
    0,                                  // tp_itemsize
    0,                                  // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    0,                                  // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    0,                                  // tp_call
    0,                                  // tp_str
    0,                                  // tp_getattro
    0,                                  // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0                                   // tp_doc
};


static PyTypeObject g_RowidVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.ROWID",                  // tp_name
    sizeof(udt_StringVar),              // tp_basicsize
    0,                                  // tp_itemsize
    0,                                  // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    0,                                  // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    0,                                  // tp_call
    0,                                  // tp_str
    0,                                  // tp_getattro
    0,                                  // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0                                   // tp_doc
};


static PyTypeObject g_BinaryVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.BINARY",                 // tp_name
    sizeof(udt_StringVar),              // tp_basicsize
    0,                                  // tp_itemsize
    0,                                  // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    0,                                  // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    0,                                  // tp_call
    0,                                  // tp_str
    0,                                  // tp_getattro
    0,                                  // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0                                   // tp_doc
};


//-----------------------------------------------------------------------------
// variable type declarations
//-----------------------------------------------------------------------------
static udt_VariableType vt_String = {
    (InitializeProc) StringVar_Initialize,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) StringVar_SetValue,
    (GetValueProc) StringVar_GetValue,
    (GetBufferSizeProc) StringVar_GetBufferSize,
    &g_StringVarType,                   // Python type
    SQLT_CHR,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    4000,                               // element length (default)
    1,                                  // is character data
    1,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_NationalCharString = {
    (InitializeProc) StringVar_Initialize,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) StringVar_PostDefine,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) StringVar_SetValue,
    (GetValueProc) StringVar_GetValue,
    (GetBufferSizeProc) StringVar_GetBufferSize,
    &g_NCharVarType,                    // Python type
    SQLT_CHR,                           // Oracle type
    SQLCS_NCHAR,                        // charset form
    4000,                               // element length (default)
    1,                                  // is character data
    1,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_FixedChar = {
    (InitializeProc) StringVar_Initialize,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) StringVar_SetValue,
    (GetValueProc) StringVar_GetValue,
    (GetBufferSizeProc) StringVar_GetBufferSize,
    &g_FixedCharVarType,                // Python type
    SQLT_AFC,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    2000,                               // element length (default)
    1,                                  // is character data
    1,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_FixedNationalChar = {
    (InitializeProc) StringVar_Initialize,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) StringVar_PostDefine,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) StringVar_SetValue,
    (GetValueProc) StringVar_GetValue,
    (GetBufferSizeProc) StringVar_GetBufferSize,
    &g_FixedNCharVarType,               // Python type
    SQLT_AFC,                           // Oracle type
    SQLCS_NCHAR,                        // charset form
    2000,                               // element length (default)
    1,                                  // is character data
    1,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_Rowid = {
    (InitializeProc) StringVar_Initialize,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) StringVar_SetValue,
    (GetValueProc) StringVar_GetValue,
    (GetBufferSizeProc) StringVar_GetBufferSize,
    &g_RowidVarType,                    // Python type
    SQLT_CHR,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    18,                                 // element length (default)
    1,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_Binary = {
    (InitializeProc) StringVar_Initialize,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) StringVar_SetValue,
    (GetValueProc) StringVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_BinaryVarType,                   // Python type
    SQLT_BIN,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    4000,                               // element length (default)
    0,                                  // is character data
    1,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


//-----------------------------------------------------------------------------
// StringVar_Initialize()
//   Initialize the variable.
//-----------------------------------------------------------------------------
static int StringVar_Initialize(
    udt_StringVar *var,                 // variable to initialize
    udt_Cursor *cursor)                 // cursor to use
{
    ub4 i;

    var->actualLength = (ACTUAL_LENGTH_TYPE *)
            PyMem_Malloc(var->allocatedElements * sizeof(ACTUAL_LENGTH_TYPE));
    if (!var->actualLength) {
        PyErr_NoMemory();
        return -1;
    }

    for (i = 0; i < var->allocatedElements; i++)
        var->actualLength[i] = 0;

    return 0;
}


//-----------------------------------------------------------------------------
// StringVar_SetValue()
//   Set the value of the variable.
//-----------------------------------------------------------------------------
static int StringVar_SetValue(
    udt_StringVar *var,                 // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    udt_Buffer buffer;
    char *encoding;

    // determine which encoding should be used
    if (var->type->charsetForm == SQLCS_NCHAR)
        encoding = var->environment->nencoding;
    else encoding = var->environment->encoding;

    // populate the buffer and confirm the maximum size is not exceeded
    if (cxBuffer_FromObject(&buffer, value, encoding) < 0)
        return -1;

    // ensure that the buffer is large enough
    if (buffer.size > var->bufferSize) {
        if (Variable_Resize( (udt_Variable*) var, buffer.numCharacters) < 0) {
            cxBuffer_Clear(&buffer);
            return -1;
        }
    }

    // keep a copy of the string
    var->actualLength[pos] = (ACTUAL_LENGTH_TYPE) buffer.size;
    if (buffer.size)
        memcpy(var->data + var->bufferSize * pos, buffer.ptr, buffer.size);
    cxBuffer_Clear(&buffer);

    return 0;
}


//-----------------------------------------------------------------------------
// StringVar_GetValue()
//   Returns the value stored at the given array position.
//-----------------------------------------------------------------------------
static PyObject *StringVar_GetValue(
    udt_StringVar *var,                 // variable to determine value for
    unsigned pos)                       // array position
{
    char *data;

    data = var->data + pos * var->bufferSize;
    if (var->type == &vt_Binary)
        return PyBytes_FromStringAndSize(data, var->actualLength[pos]);
    if (var->type == &vt_FixedNationalChar
            || var->type == &vt_NationalCharString)
        return PyUnicode_Decode(data, var->actualLength[pos],
                var->environment->nencoding, NULL);
    return cxString_FromEncodedString(data, var->actualLength[pos],
            var->environment->encoding);
}


//-----------------------------------------------------------------------------
// StringVar_PostDefine()
//   Set the character set information when values are fetched from this
// variable.
//-----------------------------------------------------------------------------
static int StringVar_PostDefine(
    udt_StringVar *var)                 // variable to initialize
{
    sword status;

    status = OCIAttrSet(var->defineHandle, OCI_HTYPE_DEFINE,
            &var->type->charsetForm, 0, OCI_ATTR_CHARSET_FORM,
            var->environment->errorHandle);
    if (Environment_CheckForError(var->environment, status,
            "StringVar_PostDefine(): setting charset form") < 0)
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// StringVar_GetBufferSize()
//   Returns the buffer size to use for the variable.
//-----------------------------------------------------------------------------
static ub4 StringVar_GetBufferSize(
    udt_StringVar* self)                // variable to get buffer size for
{
    if (self->type->isCharacterData)
        return self->size * self->environment->maxBytesPerCharacter;
    return self->size;
}

