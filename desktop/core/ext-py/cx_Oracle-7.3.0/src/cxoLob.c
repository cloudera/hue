//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoLob.c
//   Defines the routines for handling LOB values.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of external LOB functions.
//-----------------------------------------------------------------------------
static void cxoLob_free(cxoLob*);
static PyObject *cxoLob_str(cxoLob*);
static PyObject *cxoLob_size(cxoLob*, PyObject*);
static PyObject *cxoLob_open(cxoLob*, PyObject*);
static PyObject *cxoLob_close(cxoLob*, PyObject*);
static PyObject *cxoLob_read(cxoLob*, PyObject*, PyObject*);
static PyObject *cxoLob_write(cxoLob*, PyObject*, PyObject*);
static PyObject *cxoLob_trim(cxoLob*, PyObject*, PyObject*);
static PyObject *cxoLob_getChunkSize(cxoLob*, PyObject*);
static PyObject *cxoLob_isOpen(cxoLob*, PyObject*);
static PyObject *cxoLob_getFileName(cxoLob*, PyObject*);
static PyObject *cxoLob_setFileName(cxoLob*, PyObject*);
static PyObject *cxoLob_fileExists(cxoLob*, PyObject*);
static PyObject *cxoLob_reduce(cxoLob*);


//-----------------------------------------------------------------------------
// declaration of methods for Python type "LOB"
//-----------------------------------------------------------------------------
static PyMethodDef cxoLobMethods[] = {
    { "size", (PyCFunction) cxoLob_size, METH_NOARGS },
    { "open", (PyCFunction) cxoLob_open, METH_NOARGS },
    { "close", (PyCFunction) cxoLob_close, METH_NOARGS },
    { "read", (PyCFunction) cxoLob_read, METH_VARARGS | METH_KEYWORDS },
    { "write", (PyCFunction) cxoLob_write, METH_VARARGS | METH_KEYWORDS },
    { "trim", (PyCFunction) cxoLob_trim, METH_VARARGS | METH_KEYWORDS },
    { "getchunksize", (PyCFunction) cxoLob_getChunkSize, METH_NOARGS },
    { "isopen", (PyCFunction) cxoLob_isOpen, METH_NOARGS },
    { "getfilename", (PyCFunction) cxoLob_getFileName, METH_NOARGS },
    { "setfilename", (PyCFunction) cxoLob_setFileName, METH_VARARGS },
    { "fileexists", (PyCFunction) cxoLob_fileExists, METH_NOARGS },
    { "__reduce__", (PyCFunction) cxoLob_reduce, METH_NOARGS },
    { NULL, NULL }
};


//-----------------------------------------------------------------------------
// Python type declaration
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeLob = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.LOB",                    // tp_name
    sizeof(cxoLob),                     // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoLob_free,           // tp_dealloc
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
    (reprfunc) cxoLob_str,              // tp_str
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
    cxoLobMethods,                      // tp_methods
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
// cxoLob_new()
//   Create a new LOB.
//-----------------------------------------------------------------------------
PyObject *cxoLob_new(cxoConnection *connection, dpiOracleTypeNum oracleTypeNum,
        dpiLob *handle)
{
    cxoLob *lob;

    lob = (cxoLob*) cxoPyTypeLob.tp_alloc(&cxoPyTypeLob, 0);
    if (!lob)
        return NULL;
    lob->handle = handle;
    lob->oracleTypeNum = oracleTypeNum;
    Py_INCREF(connection);
    lob->connection = connection;
    return (PyObject*) lob;
}


//-----------------------------------------------------------------------------
// cxoLob_free()
//   Free a LOB.
//-----------------------------------------------------------------------------
static void cxoLob_free(cxoLob *lob)
{
    if (lob->handle) {
        dpiLob_release(lob->handle);
        lob->handle = NULL;
    }
    Py_CLEAR(lob->connection);
    Py_TYPE(lob)->tp_free((PyObject*) lob);
}


//-----------------------------------------------------------------------------
// cxoLob_internalRead()
//   Return a portion (or all) of the data in the LOB.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_internalRead(cxoLob *lob, uint64_t offset,
        uint64_t amount)
{
    uint64_t bufferSize;
    PyObject *result;
    char *buffer;
    int status;

    // modify the arguments
    if (amount == (uint64_t)(-1)) {
        if (dpiLob_getSize(lob->handle, &amount) < 0)
            return cxoError_raiseAndReturnNull();
        if (amount >= offset)
            amount = amount - offset + 1;
        else amount = 1;
    }

    // create a buffer of the correct size
    if (dpiLob_getBufferSize(lob->handle, amount, &bufferSize) < 0)
        return cxoError_raiseAndReturnNull();
    buffer = (char*) PyMem_Malloc((Py_ssize_t) bufferSize);
    if (!buffer)
        return PyErr_NoMemory();

    // read the LOB
    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_readBytes(lob->handle, offset, amount, buffer,
            &bufferSize);
    Py_END_ALLOW_THREADS
    if (status < 0) {
        PyMem_Free(buffer);
        return cxoError_raiseAndReturnNull();
    }

    // return the result
    if (lob->oracleTypeNum == DPI_ORACLE_TYPE_NCLOB)
        result = PyUnicode_Decode(buffer, (Py_ssize_t) bufferSize,
                lob->connection->encodingInfo.nencoding, NULL);
    else if (lob->oracleTypeNum == DPI_ORACLE_TYPE_CLOB)
        result = cxoPyString_fromEncodedString(buffer, (Py_ssize_t) bufferSize,
                lob->connection->encodingInfo.encoding, NULL);
    else result = PyBytes_FromStringAndSize(buffer, (Py_ssize_t) bufferSize);
    PyMem_Free(buffer);
    return result;
}


//-----------------------------------------------------------------------------
// cxoLob_internalWrite()
//   Write the data in the Python object to the LOB.
//-----------------------------------------------------------------------------
static int cxoLob_internalWrite(cxoLob *lob, PyObject *dataObj,
        uint64_t offset)
{
    const char *encoding;
    cxoBuffer buffer;
    int status;

    if (lob->oracleTypeNum == DPI_ORACLE_TYPE_NCLOB)
        encoding = lob->connection->encodingInfo.nencoding;
    else encoding = lob->connection->encodingInfo.encoding;
    if (cxoBuffer_fromObject(&buffer, dataObj, encoding) < 0)
        return -1;
    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_writeBytes(lob->handle, offset,
            (char*) buffer.ptr, buffer.size);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&buffer);
    if (status < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoLob_size()
//   Return the size of the data in the LOB.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_size(cxoLob *lob, PyObject *args)
{
    uint64_t length;

    if (dpiLob_getSize(lob->handle, &length) < 0)
        return cxoError_raiseAndReturnNull();
    return PyLong_FromUnsignedLongLong(length);
}


//-----------------------------------------------------------------------------
// cxoLob_open()
//   Open the LOB to speed further accesses.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_open(cxoLob *lob, PyObject *args)
{
    int status;

    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_openResource(lob->handle);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoLob_close()
//   Close the LOB.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_close(cxoLob *lob, PyObject *args)
{
    int status;

    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_closeResource(lob->handle);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoLob_read()
//   Return a portion (or all) of the data in the LOB.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_read(cxoLob *lob, PyObject *args, PyObject *keywordArgs)
{
    static char *keywordList[] = { "offset", "amount", NULL };
    unsigned PY_LONG_LONG offset, amount;

    // offset and amount are expected, both optional
    offset = 1;
    amount = (unsigned PY_LONG_LONG)(-1);
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|KK", keywordList,
            &offset, &amount))
        return NULL;
    return cxoLob_internalRead(lob, (uint64_t) offset, (uint64_t) amount);
}


//-----------------------------------------------------------------------------
// cxoLob_str()
//   Return all of the data in the LOB.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_str(cxoLob *lob)
{
    return cxoLob_internalRead(lob, 1, (uint64_t)(-1));
}


//-----------------------------------------------------------------------------
// cxoLob_write()
//   Write a value to the LOB.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_write(cxoLob *lob, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "data", "offset", NULL };
    unsigned PY_LONG_LONG offset;
    PyObject *dataObj;

    offset = 1;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O|K", keywordList,
            &dataObj, &offset))
        return NULL;
    if (cxoLob_internalWrite(lob, dataObj, (uint64_t) offset) < 0)
        return NULL;
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoLob_trim()
//   Trim the LOB to the specified length.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_trim(cxoLob *lob, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "newSize", NULL };
    unsigned PY_LONG_LONG newSize;
    int status;

    newSize = 0;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|K", keywordList,
            &newSize))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_trim(lob->handle, (uint64_t) newSize);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoLob_reduce()
//   Method provided for pickling/unpickling of LOBs.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_reduce(cxoLob *lob)
{
    PyObject *result, *value;

    value = cxoLob_str(lob);
    if (!value)
        return NULL;
    result = Py_BuildValue("(O(O))", Py_TYPE(value), value);
    Py_DECREF(value);
    return result;
}


//-----------------------------------------------------------------------------
// cxoLob_getChunkSize()
//   Return the chunk size that should be used when reading/writing the LOB in
// chunks.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_getChunkSize(cxoLob *lob, PyObject *args)
{
    uint32_t size;

    if (dpiLob_getChunkSize(lob->handle, &size) < 0)
        return cxoError_raiseAndReturnNull();
    return PyInt_FromLong(size);
}


//-----------------------------------------------------------------------------
// cxoLob_isOpen()
//   Return a boolean indicating if the lob is open or not.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_isOpen(cxoLob *lob, PyObject *args)
{
    int isOpen, status;

    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_getIsResourceOpen(lob->handle, &isOpen);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    return PyBool_FromLong(isOpen);
}


//-----------------------------------------------------------------------------
// cxoLob_getFileName()
//   Return the directory alias and file name for the BFILE lob.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_getFileName(cxoLob *lob, PyObject *args)
{
    uint32_t directoryAliasLength, fileNameLength;
    const char *directoryAlias, *fileName;
    PyObject *result, *temp;
    int status;

    // get the information from the LOB
    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_getDirectoryAndFileName(lob->handle, &directoryAlias,
            &directoryAliasLength, &fileName, &fileNameLength);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    // create the two-tuple for returning
    result = PyTuple_New(2);
    if (!result)
        return NULL;
    temp = cxoPyString_fromEncodedString(directoryAlias, directoryAliasLength,
            lob->connection->encodingInfo.encoding, NULL);
    if (!temp) {
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 0, temp);
    temp = cxoPyString_fromEncodedString(fileName, fileNameLength,
            lob->connection->encodingInfo.encoding, NULL);
    if (!temp) {
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 1, temp);

    return result;
}


//-----------------------------------------------------------------------------
// cxoLob_setFileName()
//   Set the directory alias and file name for the BFILE lob.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_setFileName(cxoLob *lob, PyObject *args)
{
    cxoBuffer directoryAliasBuffer, fileNameBuffer;
    PyObject *directoryAliasObj, *fileNameObj;
    int status;

    // get the directory alias and file name
    if (!PyArg_ParseTuple(args, "OO", &directoryAliasObj, &fileNameObj))
        return NULL;
    if (cxoBuffer_fromObject(&directoryAliasBuffer, directoryAliasObj,
            lob->connection->encodingInfo.encoding) < 0)
        return NULL;
    if (cxoBuffer_fromObject(&fileNameBuffer, fileNameObj,
            lob->connection->encodingInfo.encoding) < 0) {
        cxoBuffer_clear(&directoryAliasBuffer);
        return NULL;
    }

    // perform the work
    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_setDirectoryAndFileName(lob->handle,
            (char*) directoryAliasBuffer.ptr, directoryAliasBuffer.size,
            (char*) fileNameBuffer.ptr, fileNameBuffer.size);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&directoryAliasBuffer);
    cxoBuffer_clear(&fileNameBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoLob_fileExists()
//   Return a boolean indicating if the BFIILE lob exists.
//-----------------------------------------------------------------------------
static PyObject *cxoLob_fileExists(cxoLob *lob, PyObject *args)
{
    int status, exists;

    Py_BEGIN_ALLOW_THREADS
    status = dpiLob_getFileExists(lob->handle, &exists);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    if (exists)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

