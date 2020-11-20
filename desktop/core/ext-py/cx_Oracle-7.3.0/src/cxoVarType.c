//-----------------------------------------------------------------------------
// Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoVarType.c
//   Defines variable types for various transformations.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

// define variable types for each of the supported transforms
static cxoVarType cxoAllVarTypes[] = {
    {
        CXO_TRANSFORM_NONE,
        &cxoPyTypeStringVar,
        1
    },
    {
        CXO_TRANSFORM_BINARY,
        &cxoPyTypeBinaryVar,
        4000
    },
    {
        CXO_TRANSFORM_BFILE,
        &cxoPyTypeBfileVar,
        0
    },
    {
        CXO_TRANSFORM_BLOB,
        &cxoPyTypeBlobVar,
        0
    },
    {
        CXO_TRANSFORM_BOOLEAN,
        &cxoPyTypeBooleanVar,
        0
    },
    {
        CXO_TRANSFORM_CLOB,
        &cxoPyTypeClobVar,
        0
    },
    {
        CXO_TRANSFORM_CURSOR,
        &cxoPyTypeCursorVar,
        0
    },
    {
        CXO_TRANSFORM_DATE,
        &cxoPyTypeDateTimeVar,
        0
    },
    {
        CXO_TRANSFORM_DATETIME,
        &cxoPyTypeDateTimeVar,
        0
    },
    {
        CXO_TRANSFORM_DECIMAL,
        &cxoPyTypeNumberVar,
        1000
    },
    {
        CXO_TRANSFORM_FIXED_CHAR,
        &cxoPyTypeFixedCharVar,
        2000
    },
    {
        CXO_TRANSFORM_FIXED_NCHAR,
        &cxoPyTypeFixedNcharVar,
        2000
    },
    {
        CXO_TRANSFORM_FLOAT,
        &cxoPyTypeNumberVar,
        1000
    },
    {
        CXO_TRANSFORM_INT,
        &cxoPyTypeNumberVar,
        1000
    },
    {
        CXO_TRANSFORM_LONG_BINARY,
        &cxoPyTypeLongBinaryVar,
        128 * 1024
    },
    {
        CXO_TRANSFORM_LONG_STRING,
        &cxoPyTypeLongStringVar,
        128 * 1024
    },
    {
        CXO_TRANSFORM_NATIVE_DOUBLE,
        &cxoPyTypeNativeFloatVar,
        0
    },
    {
        CXO_TRANSFORM_NATIVE_FLOAT,
        &cxoPyTypeNativeFloatVar,
        0
    },
    {
        CXO_TRANSFORM_NATIVE_INT,
        &cxoPyTypeNativeIntVar,
        0
    },
    {
        CXO_TRANSFORM_NCLOB,
        &cxoPyTypeNclobVar,
        0
    },
    {
        CXO_TRANSFORM_NSTRING,
        &cxoPyTypeNcharVar,
        4000
    },
    {
        CXO_TRANSFORM_OBJECT,
        &cxoPyTypeObjectVar,
        0
    },
    {
        CXO_TRANSFORM_ROWID,
        &cxoPyTypeRowidVar,
        0
    },
    {
        CXO_TRANSFORM_STRING,
        &cxoPyTypeStringVar,
        4000
    },
    {
        CXO_TRANSFORM_TIMEDELTA,
        &cxoPyTypeIntervalVar,
        0
    },
    {
        CXO_TRANSFORM_TIMESTAMP,
        &cxoPyTypeTimestampVar,
        0
    },
    {
        CXO_TRANSFORM_TIMESTAMP_LTZ,
        &cxoPyTypeTimestampVar,
        0
    }
};


//-----------------------------------------------------------------------------
// cxoVarType_fromDataTypeInfo()
//   Return a variable type given query metadata, or NULL indicating that the
// data indicated by the query metadata is not supported.
//-----------------------------------------------------------------------------
cxoVarType *cxoVarType_fromDataTypeInfo(dpiDataTypeInfo *info)
{
    cxoTransformNum transformNum;
    char message[120];

    transformNum = cxoTransform_getNumFromDataTypeInfo(info);
    if (transformNum == CXO_TRANSFORM_UNSUPPORTED) {
        snprintf(message, sizeof(message), "Oracle type %d not supported.",
                info->oracleTypeNum);
        cxoError_raiseFromString(cxoNotSupportedErrorException, message);
        return NULL;
    }
    return &cxoAllVarTypes[transformNum];
}


//-----------------------------------------------------------------------------
// cxoVarType_fromPythonType()
//   Return a variable type given a Python type object or NULL if the Python
// type does not have a corresponding variable type. If the type provided is an
// object type, return that as well.
//-----------------------------------------------------------------------------
cxoVarType *cxoVarType_fromPythonType(PyObject *type, cxoObjectType **objType)
{
    cxoTransformNum transformNum;
    PyTypeObject *pyType;
    char message[250];

    if (Py_TYPE(type) == &cxoPyTypeObjectType) {
        transformNum = CXO_TRANSFORM_OBJECT;
        *objType = (cxoObjectType*) type;
    } else if (Py_TYPE(type) != &PyType_Type) {
        PyErr_SetString(PyExc_TypeError, "expecting type");
        return NULL;
    } else {
        *objType = NULL;
        pyType = (PyTypeObject*) type;
        transformNum = cxoTransform_getNumFromType(pyType);
        if (transformNum == CXO_TRANSFORM_UNSUPPORTED) {
            snprintf(message, sizeof(message), "Python type %s not supported.",
                    pyType->tp_name);
            cxoError_raiseFromString(cxoNotSupportedErrorException, message);
            return NULL;
        }
    }
    return &cxoAllVarTypes[transformNum];
}


//-----------------------------------------------------------------------------
// cxoVarType_calculateSize()
//   Calculate the size to use with the specified transform and Python value.
// This function is only called by cxoVarType_fromPythonValue() and no attempt
// is made to verify the value further.
//-----------------------------------------------------------------------------
static Py_ssize_t cxoVarType_calculateSize(PyObject *value,
        cxoTransformNum transformNum)
{
    Py_ssize_t size = 0;
#if PY_MAJOR_VERSION < 3
    const void *ptr;
#endif

    switch (transformNum) {
        case CXO_TRANSFORM_NONE:
            return 1;
        case CXO_TRANSFORM_BINARY:
#if PY_MAJOR_VERSION >= 3
            return PyBytes_GET_SIZE(value);
#else
            PyObject_AsReadBuffer(value, &ptr, &size);
            return size;
#endif
        case CXO_TRANSFORM_NSTRING:
            size = PyUnicode_GET_SIZE(value);
            return (size == 0) ? 1 : size;
        case CXO_TRANSFORM_STRING:
#if PY_MAJOR_VERSION >= 3
            size = PyUnicode_GET_SIZE(value);
#else
            size = PyString_GET_SIZE(value);
#endif
            return (size == 0) ? 1 : size;
        default:
            break;
    }
    return 0;
}


//-----------------------------------------------------------------------------
// cxoVarType_fromPythonValue()
//   Return a variable type given a Python object or NULL if the Python object
// does not have a corresponding variable type.
//-----------------------------------------------------------------------------
cxoVarType *cxoVarType_fromPythonValue(PyObject *value, int *isArray,
        Py_ssize_t *size, Py_ssize_t *numElements, int plsql)
{
    cxoTransformNum transformNum, tempTransformNum;
    PyObject *elementValue;
    Py_ssize_t i, tempSize;
    char message[250];

    // initialization (except numElements which always has a valid value and is
    // only overridden when a an array is encountered)
    *size = 0;
    *isArray = 0;

    // handle arrays
    if (PyList_Check(value)) {
        transformNum = CXO_TRANSFORM_NONE;
        for (i = 0; i < PyList_GET_SIZE(value); i++) {
            elementValue = PyList_GET_ITEM(value, i);
            tempTransformNum = cxoTransform_getNumFromValue(elementValue, 1);
            if (tempTransformNum == CXO_TRANSFORM_UNSUPPORTED) {
                snprintf(message, sizeof(message),
                        "element %u value is unsupported", (unsigned) i);
                cxoError_raiseFromString(cxoNotSupportedErrorException,
                        message);
                return NULL;
            } else if (transformNum == CXO_TRANSFORM_NONE) {
                transformNum = tempTransformNum;
            } else if (transformNum != tempTransformNum) {
                snprintf(message, sizeof(message),
                        "element %u value is not the same type as previous "
                        "elements", (unsigned) i);
                cxoError_raiseFromString(cxoNotSupportedErrorException,
                        message);
                return NULL;
            }
            tempSize = cxoVarType_calculateSize(elementValue,
                    tempTransformNum);
            if (tempSize > *size)
                *size = tempSize;
        }
        *isArray = 1;
        *numElements = PyList_GET_SIZE(value);
        return &cxoAllVarTypes[transformNum];
    }

    // handle scalar values
    transformNum = cxoTransform_getNumFromValue(value, plsql);
    if (transformNum == CXO_TRANSFORM_UNSUPPORTED) {
        snprintf(message, sizeof(message),
                "Python value of type %s not supported.",
                Py_TYPE(value)->tp_name);
        cxoError_raiseFromString(cxoNotSupportedErrorException, message);
        return NULL;
    }
    *size = cxoVarType_calculateSize(value, transformNum);
    return &cxoAllVarTypes[transformNum];
}

