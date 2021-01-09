//-----------------------------------------------------------------------------
// Copyright 2018, Oracle and/or its affiliates. All rights reserved.
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

