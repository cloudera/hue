//-----------------------------------------------------------------------------
// Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoUtils.c
//   Utility functions used in cx_Oracle.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// cxoUtils_formatString()
//   Return a Python string formatted using the given format string and
// arguments. The arguments have a reference taken from them after they have
// been used (which should mean that they are destroyed).
//-----------------------------------------------------------------------------
PyObject *cxoUtils_formatString(const char *format, PyObject *args)
{
    PyObject *formatObj, *result;

    // assume that a NULL value for arguments implies building the arguments
    // failed and a Python exception has already been raised
    if (!args)
        return NULL;

    // convert string format to Python object
#if PY_MAJOR_VERSION >= 3
    formatObj = PyUnicode_DecodeASCII(format, strlen(format), NULL);
#else
    formatObj = PyString_FromString(format);
#endif
    if (!formatObj) {
        Py_DECREF(args);
        return NULL;
    }

    // create formatted result
#if PY_MAJOR_VERSION >= 3
    result = PyUnicode_Format(formatObj, args);
#else
    result = PyString_Format(formatObj, args);
#endif
    Py_DECREF(args);
    Py_DECREF(formatObj);
    return result;
}


//-----------------------------------------------------------------------------
// cxoUtils_getAdjustedEncoding()
//   Return the adjusted encoding to use when encoding and decoding strings
// that are passed to and from the Oracle database. The Oracle client interface
// does not support the inclusion of a BOM in the encoded string but assumes
// native endian order for UTF-16. Python generates a BOM at the beginning of
// the encoded string if plain UTF-16 is specified. For this reason, the
// correct byte order must be determined and used inside Python so that the
// Oracle client receives the data it expects.
//-----------------------------------------------------------------------------
const char *cxoUtils_getAdjustedEncoding(const char *encoding)
{
    static const union {
        unsigned char bytes[4];
        uint32_t value;
    } hostOrder = { { 0, 1, 2, 3 } };

    if (!encoding || strcmp(encoding, "UTF-16") != 0)
        return encoding;
    return (hostOrder.value == 0x03020100) ? "UTF-16LE" : "UTF-16BE";
}


//-----------------------------------------------------------------------------
// cxoUtils_getBooleanValue()
//   Get a boolean value from a Python object.
//-----------------------------------------------------------------------------
int cxoUtils_getBooleanValue(PyObject *obj, int defaultValue, int *value)
{
    if (!obj)
        *value = defaultValue;
    else {
        *value = PyObject_IsTrue(obj);
        if (*value < 0)
            return -1;
    }
    return 0;
}


//-----------------------------------------------------------------------------
// cxoUtils_getModuleAndName()
//   Return the module and name for the type.
//-----------------------------------------------------------------------------
int cxoUtils_getModuleAndName(PyTypeObject *type, PyObject **module,
        PyObject **name)
{
    *module = PyObject_GetAttrString( (PyObject*) type, "__module__");
    if (!*module)
        return -1;
    *name = PyObject_GetAttrString( (PyObject*) type, "__name__");
    if (!*name) {
        Py_DECREF(*module);
        return -1;
    }
    return 0;
}


//-----------------------------------------------------------------------------
// cxoUtils_initializeDPI()
//   Initialize the ODPI-C library. This is done when the first standalone
// connection or session pool is created, rather than when the module is first
// imported so that manipulating environment variables such as NLS_LANG will
// work as expected. It also has the additional benefit of reducing the number
// of errors that can take place when the module is imported.
//-----------------------------------------------------------------------------
int cxoUtils_initializeDPI(void)
{
    dpiErrorInfo errorInfo;
    dpiContext *context;

    if (!cxoDpiContext) {
        if (dpiContext_create(DPI_MAJOR_VERSION, DPI_MINOR_VERSION,
                &context, &errorInfo) < 0)
            return cxoError_raiseFromInfo(&errorInfo);
        if (dpiContext_getClientVersion(context, &cxoClientVersionInfo) < 0)
            return cxoError_raiseAndReturnInt();
        cxoDpiContext = context;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoUtils_processJsonArg()
//   Process the argument which is expected to be either a string or bytes, or
// a dictionary or list which is converted to a string via the json.dumps()
// method. All strings are encoded to UTF-8 which is what SODA expects.
//-----------------------------------------------------------------------------
int cxoUtils_processJsonArg(PyObject *arg, cxoBuffer *buffer)
{
    int converted = 0;

    if (arg && (PyDict_Check(arg) || PyList_Check(arg))) {
        arg = PyObject_CallFunctionObjArgs(cxoJsonDumpFunction, arg, NULL);
        if (!arg)
            return -1;
        converted = 1;
    }
    if (cxoBuffer_fromObject(buffer, arg, "UTF-8") < 0)
        return -1;
    if (converted)
        Py_DECREF(arg);

    return 0;
}


//-----------------------------------------------------------------------------
// cxoUtils_processSodaDocArg()
//   Process a SODA document argument. This is expectd to be an actual SODA
// document object or a dictionary. If the argument refers to a dictionary or
// list, a new SODA document will be created with the given content and without
// a key or media type specified.
//-----------------------------------------------------------------------------
int cxoUtils_processSodaDocArg(cxoSodaDatabase *db, PyObject *arg,
        cxoSodaDoc **doc)
{
    dpiSodaDoc *handle;
    cxoBuffer buffer;

    if (PyObject_TypeCheck(arg, &cxoPyTypeSodaDoc)) {
        Py_INCREF(arg);
        *doc = (cxoSodaDoc*) arg;
    } else if (PyDict_Check(arg) || PyList_Check(arg)) {
        arg = PyObject_CallFunctionObjArgs(cxoJsonDumpFunction, arg, NULL);
        if (!arg)
            return -1;
        if (cxoBuffer_fromObject(&buffer, arg, "UTF-8") < 0) {
            Py_DECREF(arg);
            return -1;
        }
        Py_DECREF(arg);
        if (dpiSodaDb_createDocument(db->handle, NULL, 0, buffer.ptr,
                buffer.size, NULL, 0, DPI_SODA_FLAGS_DEFAULT, &handle) < 0) {
            cxoError_raiseAndReturnNull();
            cxoBuffer_clear(&buffer);
            return -1;
        }
        cxoBuffer_clear(&buffer);
        *doc = cxoSodaDoc_new(db, handle);
        if (!*doc)
            return -1;
    } else {
        PyErr_SetString(PyExc_TypeError,
                "value must be a SODA document or dictionary");
        return -1;
    }

    return 0;
}

