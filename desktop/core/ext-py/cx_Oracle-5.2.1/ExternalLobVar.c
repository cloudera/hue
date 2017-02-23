//-----------------------------------------------------------------------------
// ExternalLobVar.c
//   Defines the routines for handling LOB variables external to this module.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// external LOB type
//-----------------------------------------------------------------------------
typedef struct {
    PyObject_HEAD
    udt_LobVar *lobVar;
    unsigned pos;
    unsigned internalFetchNum;
} udt_ExternalLobVar;


//-----------------------------------------------------------------------------
// Declaration of external LOB variable functions.
//-----------------------------------------------------------------------------
static void ExternalLobVar_Free(udt_ExternalLobVar*);
static PyObject *ExternalLobVar_Str(udt_ExternalLobVar*);
static PyObject *ExternalLobVar_Size(udt_ExternalLobVar*, PyObject*);
static PyObject *ExternalLobVar_Open(udt_ExternalLobVar*, PyObject*);
static PyObject *ExternalLobVar_Close(udt_ExternalLobVar*, PyObject*);
static PyObject *ExternalLobVar_Read(udt_ExternalLobVar*, PyObject*,
        PyObject*);
static PyObject *ExternalLobVar_Write(udt_ExternalLobVar*, PyObject*,
        PyObject*);
static PyObject *ExternalLobVar_Trim(udt_ExternalLobVar*, PyObject*,
        PyObject*);
static PyObject *ExternalLobVar_GetChunkSize(udt_ExternalLobVar*, PyObject*);
static PyObject *ExternalLobVar_IsOpen(udt_ExternalLobVar*, PyObject*);
static PyObject *ExternalLobVar_GetFileName(udt_ExternalLobVar*, PyObject*);
static PyObject *ExternalLobVar_SetFileName(udt_ExternalLobVar*, PyObject*);
static PyObject *ExternalLobVar_FileExists(udt_ExternalLobVar*, PyObject*);
static PyObject *ExternalLobVar_Reduce(udt_ExternalLobVar*);


//-----------------------------------------------------------------------------
// declaration of methods for Python type "ExternalLOBVar"
//-----------------------------------------------------------------------------
static PyMethodDef g_ExternalLobVarMethods[] = {
    { "size", (PyCFunction) ExternalLobVar_Size, METH_NOARGS },
    { "open", (PyCFunction) ExternalLobVar_Open, METH_NOARGS },
    { "close", (PyCFunction) ExternalLobVar_Close, METH_NOARGS },
    { "read", (PyCFunction) ExternalLobVar_Read,
              METH_VARARGS  | METH_KEYWORDS },
    { "write", (PyCFunction) ExternalLobVar_Write,
              METH_VARARGS  | METH_KEYWORDS },
    { "trim", (PyCFunction) ExternalLobVar_Trim,
              METH_VARARGS  | METH_KEYWORDS },
    { "getchunksize", (PyCFunction) ExternalLobVar_GetChunkSize, METH_NOARGS },
    { "isopen", (PyCFunction) ExternalLobVar_IsOpen, METH_NOARGS },
    { "getfilename", (PyCFunction) ExternalLobVar_GetFileName, METH_NOARGS },
    { "setfilename", (PyCFunction) ExternalLobVar_SetFileName, METH_VARARGS },
    { "fileexists", (PyCFunction) ExternalLobVar_FileExists, METH_NOARGS },
    { "__reduce__", (PyCFunction) ExternalLobVar_Reduce, METH_NOARGS },
    { NULL, NULL }
};


//-----------------------------------------------------------------------------
// Python type declaration
//-----------------------------------------------------------------------------
static PyTypeObject g_ExternalLobVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.LOB",                    // tp_name
    sizeof(udt_ExternalLobVar),         // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) ExternalLobVar_Free,   // tp_dealloc
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
    (reprfunc) ExternalLobVar_Str,      // tp_str
    0,                                  // tp_getattro
    0,                                  // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    g_ExternalLobVarMethods,            // tp_methods
    0,                                  // tp_members
    0,                                  // tp_getset
    0,                                  // tp_base
    0,                                  // tp_dict
    0,                                  // tp_descr_get
    0,                                  // tp_descr_set
    0,                                  // tp_dictoffset
    0,                                  // tp_init
    0,                                  // tp_alloc
    0,                                  // tp_new
    0,                                  // tp_free
    0,                                  // tp_is_gc
    0                                   // tp_bases
};


//-----------------------------------------------------------------------------
// ExternalLobVar_New()
//   Create a new external LOB variable.
//-----------------------------------------------------------------------------
PyObject *ExternalLobVar_New(
    udt_LobVar *var,                    // variable to encapsulate
    unsigned pos)                       // position in array to encapsulate
{
    udt_ExternalLobVar *self;

    self = (udt_ExternalLobVar*)
            g_ExternalLobVarType.tp_alloc(&g_ExternalLobVarType, 0);
    if (!self)
        return NULL;
    self->pos = pos;
    self->internalFetchNum = var->internalFetchNum;
    Py_INCREF(var);
    self->lobVar = var;

    return (PyObject*) self;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Free()
//   Free an external LOB variable.
//-----------------------------------------------------------------------------
static void ExternalLobVar_Free(
    udt_ExternalLobVar *self)           // variable to free
{
    Py_CLEAR(self->lobVar);
    Py_TYPE(self)->tp_free((PyObject*) self);
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Verify()
//   Verify that the external LOB var is still valid.
//-----------------------------------------------------------------------------
static int ExternalLobVar_Verify(
    udt_ExternalLobVar *var)            // variable to verify
{
    if (var->internalFetchNum != var->lobVar->internalFetchNum) {
        PyErr_SetString(g_ProgrammingErrorException,
                "LOB variable no longer valid after subsequent fetch");
        return -1;
    }
    return 0;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_InternalRead()
//   Return the size of the LOB variable for internal comsumption.
//-----------------------------------------------------------------------------
static int ExternalLobVar_InternalRead(
    udt_ExternalLobVar *var,            // variable to return the size of
    char *buffer,                       // buffer in which to put data
    oraub8 bufferSize,                  // size of buffer
    oraub8 *length,                     // length of data (IN/OUT)
    oraub8 offset)                      // offset
{
    oraub8 lengthInBytes, lengthInChars;
    ub2 charsetId;
    sword status;

    if (var->lobVar->type == &vt_NCLOB || var->lobVar->type == &vt_CLOB) {
        lengthInBytes = 0;
        lengthInChars = *length;
    } else {
        lengthInChars = 0;
        lengthInBytes = *length;
    }

    if (var->lobVar->isFile) {
        Py_BEGIN_ALLOW_THREADS
        status = OCILobFileOpen(var->lobVar->connection->handle,
                var->lobVar->environment->errorHandle,
                var->lobVar->data[var->pos], OCI_FILE_READONLY);
        Py_END_ALLOW_THREADS
        if (Environment_CheckForError(var->lobVar->environment, status,
                "ExternalLobVar_FileOpen()") < 0)
            return -1;
    }

    Py_BEGIN_ALLOW_THREADS
    if (var->lobVar->type == &vt_NCLOB)
        charsetId = OCI_UTF16ID;
    else charsetId = 0;
    status = OCILobRead2(var->lobVar->connection->handle,
            var->lobVar->environment->errorHandle, var->lobVar->data[var->pos],
            &lengthInBytes, &lengthInChars, offset, buffer, bufferSize,
            OCI_ONE_PIECE, NULL, NULL, charsetId,
            var->lobVar->type->charsetForm);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_LobRead()") < 0) {
        if (var->lobVar->isFile) {
            Py_BEGIN_ALLOW_THREADS
            OCILobFileClose(var->lobVar->connection->handle,
                    var->lobVar->environment->errorHandle,
                    var->lobVar->data[var->pos]);
            Py_END_ALLOW_THREADS
        }
        return -1;
    }
    *length = lengthInBytes;

    if (var->lobVar->isFile) {
        Py_BEGIN_ALLOW_THREADS
        status = OCILobFileClose(var->lobVar->connection->handle,
                var->lobVar->environment->errorHandle,
                var->lobVar->data[var->pos]);
        Py_END_ALLOW_THREADS
        if (Environment_CheckForError(var->lobVar->environment, status,
                "ExternalLobVar_FileClose()") < 0)
            return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_InternalSize()
//   Return the size of the LOB variable for internal comsumption.
//-----------------------------------------------------------------------------
static int ExternalLobVar_InternalSize(
    udt_ExternalLobVar *var,            // variable to return the size of
    oraub8 *length)                     // length to return
{
    sword status;

    Py_BEGIN_ALLOW_THREADS
    status = OCILobGetLength2(var->lobVar->connection->handle,
            var->lobVar->environment->errorHandle,
            var->lobVar->data[var->pos], length);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_InternalSize()") < 0)
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Value()
//   Return a portion (or all) of the data in the external LOB variable.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Value(
    udt_ExternalLobVar *var,            // variable to return the size of
    oraub8 offset,                      // offset into LOB
    oraub8 amount)                      // amount to read from LOB
{
    oraub8 length, bufferSize;
    PyObject *result;
    char *buffer;

    // modify the arguments
    if (amount == (oraub8)(-1)) {
        if (ExternalLobVar_InternalSize(var, &amount) < 0)
            return NULL;
        if (amount >= offset)
            amount = amount - offset + 1;
        else amount = 1;
    }
    length = amount;
    if (var->lobVar->type == &vt_CLOB)
        bufferSize = amount * var->lobVar->environment->maxBytesPerCharacter;
    else if (var->lobVar->type == &vt_NCLOB)
        bufferSize = amount * 2;
    else bufferSize = amount;

    // create a string for retrieving the value
    buffer = (char*) PyMem_Malloc(bufferSize);
    if (!buffer)
        return PyErr_NoMemory();
    if (ExternalLobVar_InternalRead(var, buffer, bufferSize, &length,
            offset) < 0) {
        PyMem_Free(buffer);
        return NULL;
    }

    // return the result
    if (var->lobVar->type == &vt_CLOB) {
        result = cxString_FromEncodedString(buffer, length,
                var->lobVar->environment->encoding);
    } else if (var->lobVar->type == &vt_NCLOB) {
        result = PyUnicode_DecodeUTF16(buffer, length, NULL, NULL);
    } else {
        result = PyBytes_FromStringAndSize(buffer, length);
    }
    PyMem_Free(buffer);
    return result;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Size()
//   Return the size of the data in the LOB variable.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Size(
    udt_ExternalLobVar *var,            // variable to return the size of
    PyObject *args)                     // arguments
{
    oraub8 length;

    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    if (ExternalLobVar_InternalSize(var, &length) < 0)
        return NULL;
    return PyLong_FromUnsignedLong(length);
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Open()
//   Open the LOB to speed further accesses.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Open(
    udt_ExternalLobVar *var,            // variable to return the size of
    PyObject *args)                     // arguments
{
    sword status;

    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = OCILobOpen(var->lobVar->connection->handle,
            var->lobVar->environment->errorHandle,
            var->lobVar->data[var->pos], OCI_LOB_READWRITE);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_Open()") < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Close()
//   Close the LOB.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Close(
    udt_ExternalLobVar *var,            // variable to return the size of
    PyObject *args)                     // arguments
{
    sword status;

    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = OCILobClose(var->lobVar->connection->handle,
            var->lobVar->environment->errorHandle,
            var->lobVar->data[var->pos]);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_Close()") < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Read()
//   Return a portion (or all) of the data in the external LOB variable.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Read(
    udt_ExternalLobVar *var,            // variable to return the size of
    PyObject *args,                     // arguments
    PyObject *keywordArgs)              // keyword arguments
{
    static char *keywordList[] = { "offset", "amount", NULL };
    oraub8 offset, amount;

    // offset and amount are expected, both optional
    offset = 1;
    amount = (oraub8)(-1);
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|KK", keywordList,
            &offset, &amount))
        return NULL;

    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    return ExternalLobVar_Value(var, offset, amount);
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Str()
//   Return all of the data in the external LOB variable.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Str(
    udt_ExternalLobVar *var)            // variable to return the string for
{
    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    return ExternalLobVar_Value(var, 1, (oraub8)(-1));
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Write()
//   Write a value to the LOB variable; return the number of bytes written.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Write(
    udt_ExternalLobVar *var,            // variable to perform write against
    PyObject *args,                     // arguments
    PyObject *keywordArgs)              // keyword arguments
{
    static char *keywordList[] = { "data", "offset", NULL };
    oraub8 amount, offset;
    PyObject *dataObj;

    // buffer is expected, offset is optional
    offset = 1;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O|K", keywordList,
            &dataObj, &offset))
        return NULL;

    // perform the write, if possible
    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    if (LobVar_Write(var->lobVar, var->pos, dataObj, offset, &amount) < 0)
        return NULL;

    // return the result
    return PyLong_FromUnsignedLong(amount);
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Trim()
//   Trim the LOB variable to the specified length.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Trim(
    udt_ExternalLobVar *var,            // variable to perform write against
    PyObject *args,                     // arguments
    PyObject *keywordArgs)              // keyword arguments
{
    static char *keywordList[] = { "newSize", NULL };
    oraub8 newSize;
    sword status;

    // buffer and offset are expected, offset is optional
    newSize = 0;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|K", keywordList,
            &newSize))
        return NULL;

    // create a string for retrieving the value
    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = OCILobTrim2(var->lobVar->connection->handle,
            var->lobVar->environment->errorHandle, var->lobVar->data[var->pos],
            newSize);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_Trim()") < 0)
        return NULL;

    // return the result
    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_Reduce()
//   Method provided for pickling/unpickling of LOB variables.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_Reduce(
    udt_ExternalLobVar *self)           // variable to dump
{
    PyObject *result, *value;

    value = ExternalLobVar_Str(self);
    if (!value)
        return NULL;
    result = Py_BuildValue("(O(O))", Py_TYPE(value), value);
    Py_DECREF(value);
    return result;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_GetChunkSize()
//   Return the chunk size that should be used when reading/writing the LOB in
// chunks.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_GetChunkSize(
    udt_ExternalLobVar *var,            // variable to get chunk size for
    PyObject *args)                     // arguments
{
    ub4 chunkSize;
    sword status;

    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    status = OCILobGetChunkSize(var->lobVar->connection->handle,
            var->lobVar->environment->errorHandle, var->lobVar->data[var->pos],
            &chunkSize);
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_GetChunkSize()") < 0)
        return NULL;
    return PyInt_FromLong(chunkSize);
}


//-----------------------------------------------------------------------------
// ExternalLobVar_IsOpen()
//   Return a boolean indicating if the lob is open or not.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_IsOpen(
    udt_ExternalLobVar *var,            // variable to get chunk size for
    PyObject *args)                     // arguments
{
    boolean isOpen;
    sword status;

    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = OCILobIsOpen(var->lobVar->connection->handle,
            var->lobVar->environment->errorHandle, var->lobVar->data[var->pos],
            &isOpen);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_IsOpen()") < 0)
        return NULL;
    return PyBool_FromLong(isOpen);
}


//-----------------------------------------------------------------------------
// ExternalLobVar_GetFileName()
//   Return the directory alias and file name for the BFILE lob.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_GetFileName(
    udt_ExternalLobVar *var,            // variable to get file name for
    PyObject *args)                     // arguments
{
    char dirAlias[120], name[1020];
    ub2 dirAliasLength, nameLength;
    PyObject *result, *temp;
    sword status;

    // determine the directory alias and name
    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    nameLength = sizeof(name);
    dirAliasLength = sizeof(dirAlias);
    status = OCILobFileGetName(var->lobVar->environment->handle,
            var->lobVar->environment->errorHandle, var->lobVar->data[var->pos],
            (text*) dirAlias, &dirAliasLength, (text*) name, &nameLength);
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_GetFileName()") < 0)
        return NULL;

    // create the two-tuple for returning
    result = PyTuple_New(2);
    if (!result)
        return NULL;
    temp = cxString_FromEncodedString(dirAlias, dirAliasLength,
            var->lobVar->environment->encoding);
    if (!temp) {
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 0, temp);
    temp = cxString_FromEncodedString(name, nameLength,
            var->lobVar->environment->encoding);
    if (!temp) {
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 1, temp);

    return result;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_SetFileName()
//   Set the directory alias and file name for the BFILE lob.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_SetFileName(
    udt_ExternalLobVar *var,            // variable to set file name for
    PyObject *args)                     // arguments
{
    int dirAliasLength, nameLength;
    char *dirAlias, *name;
    sword status;

    // get the directory alias and name as strings
    if (!PyArg_ParseTuple(args, "s#s#", &dirAlias, &dirAliasLength, &name,
            &nameLength))
        return NULL;

    // create a string for retrieving the value
    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    status = OCILobFileSetName(var->lobVar->environment->handle,
            var->lobVar->environment->errorHandle,
            &var->lobVar->data[var->pos], (text*) dirAlias,
            (ub2) dirAliasLength, (text*) name, (ub2) nameLength);
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_SetFileName()") < 0)
        return NULL;

    // return the result
    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// ExternalLobVar_FileExists()
//   Return a boolean indicating if the BFIILE lob exists.
//-----------------------------------------------------------------------------
static PyObject *ExternalLobVar_FileExists(
    udt_ExternalLobVar *var,            // variable to perform write against
    PyObject *args)                     // arguments
{
    PyObject *result;
    sword status;
    boolean flag;

    if (ExternalLobVar_Verify(var) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = OCILobFileExists(var->lobVar->connection->handle,
            var->lobVar->environment->errorHandle, var->lobVar->data[var->pos],
            &flag);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(var->lobVar->environment, status,
            "ExternalLobVar_FileExists()") < 0)
        return NULL;

    // return the result
    if (flag)
        result = Py_True;
    else result = Py_False;
    Py_INCREF(result);
    return result;
}

