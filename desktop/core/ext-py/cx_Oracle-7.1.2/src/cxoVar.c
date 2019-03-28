//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoVar.c
//   Defines Python types for Oracle variables.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of common variable functions.
//-----------------------------------------------------------------------------
static void cxoVar_free(cxoVar*);
static PyObject *cxoVar_repr(cxoVar*);
static PyObject *cxoVar_externalCopy(cxoVar*, PyObject*);
static PyObject *cxoVar_externalSetValue(cxoVar*, PyObject*);
static PyObject *cxoVar_externalGetValue(cxoVar*, PyObject*, PyObject*);
static PyObject *cxoVar_externalGetActualElements(cxoVar*, void*);
static PyObject *cxoVar_externalGetValues(cxoVar*, void*);


//-----------------------------------------------------------------------------
// declaration of members for variables
//-----------------------------------------------------------------------------
static PyMemberDef cxoVarMembers[] = {
    { "bufferSize", T_INT, offsetof(cxoVar, bufferSize), READONLY },
    { "inconverter", T_OBJECT, offsetof(cxoVar, inConverter), 0 },
    { "numElements", T_INT, offsetof(cxoVar, allocatedElements),
            READONLY },
    { "outconverter", T_OBJECT, offsetof(cxoVar, outConverter), 0 },
    { "size", T_INT, offsetof(cxoVar, size), READONLY },
    { "type", T_OBJECT, offsetof(cxoVar, objectType), READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of calculated members for variables
//-----------------------------------------------------------------------------
static PyGetSetDef cxoVarCalcMembers[] = {
    { "actualElements", (getter) cxoVar_externalGetActualElements, 0, 0, 0 },
    { "values", (getter) cxoVar_externalGetValues, 0, 0, 0 },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of methods for variables
//-----------------------------------------------------------------------------
static PyMethodDef cxoVarMethods[] = {
    { "copy", (PyCFunction) cxoVar_externalCopy, METH_VARARGS },
    { "setvalue", (PyCFunction) cxoVar_externalSetValue, METH_VARARGS },
    { "getvalue", (PyCFunction) cxoVar_externalGetValue,
              METH_VARARGS  | METH_KEYWORDS },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of all variable types
//-----------------------------------------------------------------------------
#define DECLARE_VARIABLE_TYPE(INTERNAL_NAME, EXTERNAL_NAME) \
    PyTypeObject INTERNAL_NAME = { \
        PyVarObject_HEAD_INIT(NULL, 0) \
        "cx_Oracle." #EXTERNAL_NAME,        /* tp_name */ \
        sizeof(cxoVar),                     /* tp_basicsize */ \
        0,                                  /* tp_itemsize */ \
        (destructor) cxoVar_free,           /* tp_dealloc */ \
        0,                                  /* tp_print */ \
        0,                                  /* tp_getattr */ \
        0,                                  /* tp_setattr */ \
        0,                                  /* tp_compare */ \
        (reprfunc) cxoVar_repr,             /* tp_repr */ \
        0,                                  /* tp_as_number */ \
        0,                                  /* tp_as_sequence */ \
        0,                                  /* tp_as_mapping */ \
        0,                                  /* tp_hash */ \
        0,                                  /* tp_call */ \
        0,                                  /* tp_str */ \
        0,                                  /* tp_getattro */ \
        0,                                  /* tp_setattro */ \
        0,                                  /* tp_as_buffer */ \
        Py_TPFLAGS_DEFAULT,                 /* tp_flags */ \
        0,                                  /* tp_doc */ \
        0,                                  /* tp_traverse */ \
        0,                                  /* tp_clear */ \
        0,                                  /* tp_richcompare */ \
        0,                                  /* tp_weaklistoffset */ \
        0,                                  /* tp_iter */ \
        0,                                  /* tp_iternext */ \
        cxoVarMethods,                      /* tp_methods */ \
        cxoVarMembers,                      /* tp_members */ \
        cxoVarCalcMembers                   /* tp_getset */ \
    };

DECLARE_VARIABLE_TYPE(cxoPyTypeBfileVar, BFILE)
DECLARE_VARIABLE_TYPE(cxoPyTypeBinaryVar, BINARY)
DECLARE_VARIABLE_TYPE(cxoPyTypeBlobVar, BLOB)
DECLARE_VARIABLE_TYPE(cxoPyTypeBooleanVar, BOOLEAN)
DECLARE_VARIABLE_TYPE(cxoPyTypeClobVar, CLOB)
DECLARE_VARIABLE_TYPE(cxoPyTypeCursorVar, CURSOR)
DECLARE_VARIABLE_TYPE(cxoPyTypeDateTimeVar, DATETIME)
DECLARE_VARIABLE_TYPE(cxoPyTypeFixedCharVar, FIXED_CHAR)
DECLARE_VARIABLE_TYPE(cxoPyTypeFixedNcharVar, FIXED_NCHAR)
DECLARE_VARIABLE_TYPE(cxoPyTypeIntervalVar, INTERVAL)
DECLARE_VARIABLE_TYPE(cxoPyTypeLongBinaryVar, LONG_BINARY)
DECLARE_VARIABLE_TYPE(cxoPyTypeLongStringVar, LONG_STRING)
DECLARE_VARIABLE_TYPE(cxoPyTypeNativeFloatVar, NATIVE_FLOAT)
DECLARE_VARIABLE_TYPE(cxoPyTypeNativeIntVar, NATIVE_INT)
DECLARE_VARIABLE_TYPE(cxoPyTypeNcharVar, NCHAR)
DECLARE_VARIABLE_TYPE(cxoPyTypeNclobVar, NCLOB)
DECLARE_VARIABLE_TYPE(cxoPyTypeNumberVar, NUMBER)
DECLARE_VARIABLE_TYPE(cxoPyTypeObjectVar, OBJECT)
DECLARE_VARIABLE_TYPE(cxoPyTypeRowidVar, ROWID)
DECLARE_VARIABLE_TYPE(cxoPyTypeStringVar, STRING)
DECLARE_VARIABLE_TYPE(cxoPyTypeTimestampVar, TIMESTAMP)


//-----------------------------------------------------------------------------
// cxoVar_new()
//   Allocate a new variable.
//-----------------------------------------------------------------------------
cxoVar *cxoVar_new(cxoCursor *cursor, Py_ssize_t numElements, cxoVarType *type,
        Py_ssize_t size, int isArray, cxoObjectType *objType)
{
    dpiObjectType *typeHandle = NULL;
    dpiOracleTypeNum oracleTypeNum;
    dpiNativeTypeNum nativeTypeNum;
    cxoVar *var;

    // attempt to allocate the object
    var = (cxoVar*) type->pythonType->tp_alloc(type->pythonType, 0);
    if (!var)
        return NULL;

    // perform basic initialization
    Py_INCREF(cursor->connection);
    var->connection = cursor->connection;
    if (objType) {
        Py_INCREF(objType);
        var->objectType = objType;
        typeHandle = objType->handle;
    }
    if (numElements == 0)
        numElements = 1;
    var->allocatedElements = (uint32_t) numElements;
    var->type = type;
    var->size = (size == 0) ? type->size : (uint32_t) size;
    var->isArray = isArray;

    // acquire and initialize DPI variable
    cxoTransform_getTypeInfo(type->transformNum, &oracleTypeNum,
            &nativeTypeNum);
    if (dpiConn_newVar(cursor->connection->handle, oracleTypeNum,
            nativeTypeNum, var->allocatedElements, var->size, 0, isArray,
            typeHandle, &var->handle, &var->data) < 0) {
        cxoError_raiseAndReturnNull();
        Py_DECREF(var);
        return NULL;
    }

    // get buffer size for information
    if (dpiVar_getSizeInBytes(var->handle, &var->bufferSize) < 0) {
        cxoError_raiseAndReturnNull();
        Py_DECREF(var);
        return NULL;
    }

    return var;
}


//-----------------------------------------------------------------------------
// cxoVar_free()
//   Free an existing variable.
//-----------------------------------------------------------------------------
static void cxoVar_free(cxoVar *var)
{
    if (var->handle) {
        Py_BEGIN_ALLOW_THREADS
        dpiVar_release(var->handle);
        Py_END_ALLOW_THREADS
        var->handle = NULL;
    }
    if (var->encodingErrors)
        PyMem_Free((void*) var->encodingErrors);
    Py_CLEAR(var->connection);
    Py_CLEAR(var->inConverter);
    Py_CLEAR(var->outConverter);
    Py_CLEAR(var->objectType);
    Py_TYPE(var)->tp_free((PyObject*) var);
}


//-----------------------------------------------------------------------------
// cxoVar_check()
//   Returns a boolean indicating if the object is a variable.
//-----------------------------------------------------------------------------
int cxoVar_check(PyObject *object)
{
    PyTypeObject *objectType = Py_TYPE(object);

    return (objectType == &cxoPyTypeBfileVar ||
            objectType == &cxoPyTypeBinaryVar ||
            objectType == &cxoPyTypeBlobVar ||
            objectType == &cxoPyTypeBooleanVar ||
            objectType == &cxoPyTypeClobVar ||
            objectType == &cxoPyTypeCursorVar ||
            objectType == &cxoPyTypeDateTimeVar ||
            objectType == &cxoPyTypeFixedCharVar ||
            objectType == &cxoPyTypeFixedNcharVar ||
            objectType == &cxoPyTypeIntervalVar ||
            objectType == &cxoPyTypeLongBinaryVar ||
            objectType == &cxoPyTypeLongStringVar ||
            objectType == &cxoPyTypeNativeFloatVar ||
            objectType == &cxoPyTypeNativeIntVar ||
            objectType == &cxoPyTypeNcharVar ||
            objectType == &cxoPyTypeNclobVar ||
            objectType == &cxoPyTypeNumberVar ||
            objectType == &cxoPyTypeObjectVar ||
            objectType == &cxoPyTypeRowidVar ||
            objectType == &cxoPyTypeStringVar ||
            objectType == &cxoPyTypeTimestampVar);
}


//-----------------------------------------------------------------------------
// cxoVar_newByValue()
//   Allocate a new variable by looking at the type of the data.
//-----------------------------------------------------------------------------
cxoVar *cxoVar_newByValue(cxoCursor *cursor, PyObject *value,
        Py_ssize_t numElements)
{
    PyObject *result, *inputTypeHandler = NULL;
    cxoObjectType *objType = NULL;
    cxoVarType *varType;
    Py_ssize_t size;
    cxoObject *obj;
    int isArray;

    // determine if an input type handler should be used; an input type handler
    // defined on the cursor takes precedence over one defined on the
    // connection to which the cursor belongs; the input type handler should
    // return a variable or None; the value None implies that the default
    // processing should take place just as if no input type handler was
    // defined
    if (cursor->inputTypeHandler && cursor->inputTypeHandler != Py_None)
        inputTypeHandler = cursor->inputTypeHandler;
    else if (cursor->connection->inputTypeHandler &&
            cursor->connection->inputTypeHandler != Py_None)
        inputTypeHandler = cursor->connection->inputTypeHandler;
    if (inputTypeHandler) {
        result = PyObject_CallFunction(inputTypeHandler, "OOn", cursor, value,
                numElements);
        if (!result)
            return NULL;
        if (result != Py_None) {
            if (!cxoVar_check(result)) {
                Py_DECREF(result);
                PyErr_SetString(PyExc_TypeError,
                        "expecting variable from input type handler");
                return NULL;
            }
            return (cxoVar*) result;
        }
        Py_DECREF(result);
    }

    // default processing
    varType = cxoVarType_fromPythonValue(value,
            &isArray, &size, &numElements, cursor->stmtInfo.isPLSQL);
    if (!varType)
        return NULL;
    if (varType->transformNum == CXO_TRANSFORM_OBJECT) {
        obj = (cxoObject*) value;
        objType = obj->objectType;
    }
    return cxoVar_new(cursor, numElements, varType, size, isArray, objType);
}


//-----------------------------------------------------------------------------
// cxoVar_newArrayByType()
//   Allocate a new PL/SQL array by looking at the Python data type.
//-----------------------------------------------------------------------------
static cxoVar *cxoVar_newArrayByType(cxoCursor *cursor,
        PyObject *value)
{
    PyObject *typeObj, *numElementsObj;
    cxoObjectType *objType;
    cxoVarType *varType;
    uint32_t numElements;
    int ok;

    // validate parameters
    ok = (PyList_GET_SIZE(value) == 2);
    if (ok) {
        typeObj = PyList_GET_ITEM(value, 0);
        ok = PyType_Check(typeObj);
    }
    if (ok) {
        numElementsObj = PyList_GET_ITEM(value, 1);
        ok = PyInt_Check(numElementsObj);
    }
    if (!ok) {
        cxoError_raiseFromString(cxoProgrammingErrorException,
                "expecting an array of two elements [type, numelems]");
        return NULL;
    }

    // create variable
    varType = cxoVarType_fromPythonType(typeObj, &objType);
    if (!varType)
        return NULL;
    numElements = PyInt_AsLong(numElementsObj);
    if (PyErr_Occurred())
        return NULL;
    return cxoVar_new(cursor, numElements, varType, varType->size, 1, objType);
}


//-----------------------------------------------------------------------------
// cxoVar_newByType()
//   Allocate a new variable by looking at the Python data type.
//-----------------------------------------------------------------------------
cxoVar *cxoVar_newByType(cxoCursor *cursor, PyObject *value,
        uint32_t numElements)
{
    cxoObjectType *objType;
    cxoVarType *varType;
    long size;

    // passing an integer is assumed to be a string
    if (PyInt_Check(value)) {
        size = PyInt_AsLong(value);
        if (PyErr_Occurred())
            return NULL;
        varType = cxoVarType_fromPythonType((PyObject*) &cxoPyTypeString,
                &objType);
        return cxoVar_new(cursor, numElements, varType, size, 0, objType);
    }

    // passing an array of two elements to define an array
    if (PyList_Check(value))
        return cxoVar_newArrayByType(cursor, value);

    // handle directly bound variables
    if (cxoVar_check(value)) {
        Py_INCREF(value);
        return (cxoVar*) value;
    }

    // everything else ought to be a Python type or object type
    varType = cxoVarType_fromPythonType(value, &objType);
    if (!varType)
        return NULL;
    return cxoVar_new(cursor, numElements, varType, varType->size, 0, objType);
}


//-----------------------------------------------------------------------------
// cxoVar_bind()
//   Allocate a variable and bind it to the given statement.
//-----------------------------------------------------------------------------
int cxoVar_bind(cxoVar *var, cxoCursor *cursor, PyObject *name, uint32_t pos)
{
    cxoBuffer nameBuffer;
    int status;

    // perform the bind
    if (name) {
        if (cxoBuffer_fromObject(&nameBuffer, name,
                cursor->connection->encodingInfo.encoding) < 0)
            return -1;
        status = dpiStmt_bindByName(cursor->handle, (char*) nameBuffer.ptr,
                nameBuffer.size, var->handle);
        cxoBuffer_clear(&nameBuffer);
    } else {
        status = dpiStmt_bindByPos(cursor->handle, pos, var->handle);
    }
    if (status < 0)
        return cxoError_raiseAndReturnInt();

    // set flag if bound to a DML returning statement and no data set
    if (cursor->stmtInfo.isReturning && !var->isValueSet)
        var->getReturnedData = 1;

    return 0;
}


//-----------------------------------------------------------------------------
// cxoVar_getArrayValue()
//   Return the value of the variable as an array.
//-----------------------------------------------------------------------------
static PyObject *cxoVar_getArrayValue(cxoVar *var, uint32_t numElements,
        dpiData *data)
{
    PyObject *value, *singleValue;
    uint32_t i;

    value = PyList_New(numElements);
    if (!value)
        return NULL;

    for (i = 0; i < numElements; i++) {
        singleValue = cxoVar_getSingleValue(var, data, i);
        if (!singleValue) {
            Py_DECREF(value);
            return NULL;
        }
        PyList_SET_ITEM(value, i, singleValue);
    }

    return value;
}


//-----------------------------------------------------------------------------
// cxoVar_getSingleValue()
//   Return the value of the variable at the given position.
//-----------------------------------------------------------------------------
PyObject *cxoVar_getSingleValue(cxoVar *var, dpiData *data, uint32_t arrayPos)
{
    PyObject *value, *result;
    uint32_t numReturnedRows;
    dpiData *returnedData;

    // handle DML returning
    if (!data && var->getReturnedData) {
        if (dpiVar_getReturnedData(var->handle, arrayPos, &numReturnedRows,
                &returnedData) < 0)
            return cxoError_raiseAndReturnNull();
        return cxoVar_getArrayValue(var, numReturnedRows, returnedData);
    }

    // in all other cases, just get the value stored at specified position
    if (data)
        data = &data[arrayPos];
    else data = &var->data[arrayPos];
    if (data->isNull)
        Py_RETURN_NONE;
    value = cxoTransform_toPython(var->type->transformNum, var->connection,
            var->objectType, &data->value, var->encodingErrors);
    if (value) {
        switch (var->type->transformNum) {
            case CXO_TRANSFORM_BFILE:
            case CXO_TRANSFORM_BLOB:
            case CXO_TRANSFORM_CLOB:
            case CXO_TRANSFORM_NCLOB:
                dpiLob_addRef(data->value.asLOB);
                break;
            case CXO_TRANSFORM_OBJECT:
                dpiObject_addRef(data->value.asObject);
                break;
            default:
                break;
        }
        if (var->outConverter && var->outConverter != Py_None) {
            result = PyObject_CallFunctionObjArgs(var->outConverter, value,
                    NULL);
            Py_DECREF(value);
            return result;
        }
    }

    return value;
}


//-----------------------------------------------------------------------------
// cxoVar_getValue()
//   Return the value of the variable.
//-----------------------------------------------------------------------------
PyObject *cxoVar_getValue(cxoVar *var, uint32_t arrayPos)
{
    uint32_t numElements;

    if (var->isArray) {
        if (dpiVar_getNumElementsInArray(var->handle, &numElements) < 0)
            return cxoError_raiseAndReturnNull();
        return cxoVar_getArrayValue(var, numElements, var->data);
    }
    if (arrayPos >= var->allocatedElements && !var->getReturnedData) {
        PyErr_SetString(PyExc_IndexError,
                "cxoVar_getSingleValue: array size exceeded");
        return NULL;
    }
    return cxoVar_getSingleValue(var, NULL, arrayPos);
}


//-----------------------------------------------------------------------------
// cxoVar_setValueBytes()
//   Set a value in the variable from a byte string of some sort.
//-----------------------------------------------------------------------------
static int cxoVar_setValueBytes(cxoVar *var, uint32_t pos, dpiData *data,
        cxoBuffer *buffer)
{
    dpiData *tempVarData, *sourceData;
    dpiOracleTypeNum oracleTypeNum;
    dpiNativeTypeNum nativeTypeNum;
    uint32_t i, numElements;
    dpiVar *tempVarHandle;
    int status;

    if (buffer->size > var->bufferSize) {
        cxoTransform_getTypeInfo(var->type->transformNum, &oracleTypeNum,
                &nativeTypeNum);
        if (dpiConn_newVar(var->connection->handle, oracleTypeNum,
                nativeTypeNum, var->allocatedElements, buffer->size, 0,
                var->isArray, NULL, &tempVarHandle, &tempVarData) < 0)
            return cxoError_raiseAndReturnInt();
        if (var->isArray) {
            if (dpiVar_getNumElementsInArray(var->handle, &numElements) < 0) {
                cxoError_raiseAndReturnInt();
                dpiVar_release(tempVarHandle);
                return -1;
            }
            if (dpiVar_setNumElementsInArray(tempVarHandle, numElements) < 0) {
                cxoError_raiseAndReturnInt();
                dpiVar_release(tempVarHandle);
                return -1;
            }
        }
        for (i = 0; i < var->allocatedElements; i++) {
            sourceData = &var->data[i];
            if (i == pos || sourceData->isNull)
                continue;
            if (dpiVar_setFromBytes(tempVarHandle, i,
                    sourceData->value.asBytes.ptr,
                    sourceData->value.asBytes.length) < 0) {
                cxoError_raiseAndReturnInt();
                dpiVar_release(tempVarHandle);
                return -1;
            }
        }
        dpiVar_release(var->handle);
        var->handle = tempVarHandle;
        var->data = tempVarData;
        var->size = buffer->numCharacters;
        var->bufferSize = buffer->size;
    }
    status = dpiVar_setFromBytes(var->handle, pos, buffer->ptr, buffer->size);
    if (status < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoVar_setValueCursor()
//   Set the value of the variable (which is assumed to be a cursor).
//-----------------------------------------------------------------------------
static int cxoVar_setValueCursor(cxoVar *var, uint32_t pos, dpiData *data,
        PyObject *value)
{
    cxoCursor *cursor;
    dpiStmtInfo info;

    if (!PyObject_IsInstance(value, (PyObject*) &cxoPyTypeCursor)) {
        PyErr_SetString(PyExc_TypeError, "expecting cursor");
        return -1;
    }

    // if the cursor already has a handle, use it directly
    cursor = (cxoCursor *) value;
    if (cursor->handle) {
        if (dpiVar_setFromStmt(var->handle, pos, cursor->handle) < 0)
            return cxoError_raiseAndReturnInt();

    // otherwise, make use of the statement handle allocated by the variable
    // BUT, make sure the statement handle is still valid as it may have been
    // closed by some other code; the call to dpiStmt_getInfo() will ensure the
    // statement is still open; if an error occurs, this bind will be discarded
    // and a second attempt will be made with a new cursor
    } else {
        if (dpiStmt_getInfo(data->value.asStmt, &info) < 0)
            return cxoError_raiseAndReturnInt();
        cursor->handle = data->value.asStmt;
        dpiStmt_addRef(cursor->handle);
    }
    cursor->fixupRefCursor = 1;
    return 0;
}


//-----------------------------------------------------------------------------
// cxoVar_setSingleValue()
//   Set a single value in the variable.
//-----------------------------------------------------------------------------
static int cxoVar_setSingleValue(cxoVar *var, uint32_t arrayPos,
        PyObject *value)
{
    dpiDataBuffer tempDbValue, *dbValue;
    PyObject *convertedValue = NULL;
    cxoBuffer buffer;
    int result = 0;
    dpiData *data;

    // ensure we do not exceed the number of allocated elements
    if (arrayPos >= var->allocatedElements) {
        PyErr_SetString(PyExc_IndexError,
                "cxoVar_setSingleValue: array size exceeded");
        return -1;
    }

    // convert value, if necessary
    if (var->inConverter && var->inConverter != Py_None) {
        convertedValue = PyObject_CallFunctionObjArgs(var->inConverter, value,
                NULL);
        if (!convertedValue)
            return -1;
        value = convertedValue;
    }

    // tranform value from Python to value expected by ODPI-C
    data = &var->data[arrayPos];
    data->isNull = (value == Py_None);
    if (!data->isNull) {
        if (var->type->transformNum == CXO_TRANSFORM_CURSOR)
            result = cxoVar_setValueCursor(var, arrayPos, data, value);
        else {
            cxoBuffer_init(&buffer);
            if (var->type->size > 0)
                dbValue = &tempDbValue;
            else dbValue = &data->value;
            result = cxoTransform_fromPython(var->type->transformNum, value,
                    dbValue, &buffer, var->connection->encodingInfo.encoding,
                    var->connection->encodingInfo.nencoding, var, arrayPos);
            if (result == 0 && var->type->size > 0)
                result = cxoVar_setValueBytes(var, arrayPos, data, &buffer);
            cxoBuffer_clear(&buffer);
        }
    }
    Py_CLEAR(convertedValue);
    return result;
}


//-----------------------------------------------------------------------------
// cxoVar_setArrayValue()
//   Set all of the array values for the variable.
//-----------------------------------------------------------------------------
static int cxoVar_setArrayValue(cxoVar *var, PyObject *value)
{
    Py_ssize_t numElements, i;

    // ensure we have an array to set
    if (!PyList_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "expecting array data");
        return -1;
    }

    // set the number of actual elements
    numElements = PyList_GET_SIZE(value);
    if (dpiVar_setNumElementsInArray(var->handle, (uint32_t) numElements) < 0)
        return cxoError_raiseAndReturnInt();

    // set all of the values
    for (i = 0; i < numElements; i++) {
        if (cxoVar_setSingleValue(var, i, PyList_GET_ITEM(value, i)) < 0)
            return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoVar_setValue()
//   Set the value of the variable.
//-----------------------------------------------------------------------------
int cxoVar_setValue(cxoVar *var, uint32_t arrayPos, PyObject *value)
{
    var->isValueSet = 1;
    if (var->isArray) {
        if (arrayPos > 0) {
            cxoError_raiseFromString(cxoNotSupportedErrorException,
                    "arrays of arrays are not supported by the OCI");
            return -1;
        }
        return cxoVar_setArrayValue(var, value);
    }
    return cxoVar_setSingleValue(var, arrayPos, value);
}


//-----------------------------------------------------------------------------
// cxoVar_externalCopy()
//   Copy the contents of the source variable to the destination variable.
//-----------------------------------------------------------------------------
static PyObject *cxoVar_externalCopy(cxoVar *targetVar, PyObject *args)
{
    uint32_t sourcePos, targetPos;
    cxoVar *sourceVar;

    if (!PyArg_ParseTuple(args, "Oii", &sourceVar, &sourcePos, &targetPos))
        return NULL;
    if (Py_TYPE(targetVar) != Py_TYPE(sourceVar))
        return cxoError_raiseFromString(cxoProgrammingErrorException,
                "source and target variable type must match");
    if (dpiVar_copyData(targetVar->handle, targetPos, sourceVar->handle,
            sourcePos) < 0)
        return cxoError_raiseAndReturnNull();

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoVar_externalSetValue()
//   Set the value of the variable at the given position.
//-----------------------------------------------------------------------------
static PyObject *cxoVar_externalSetValue(cxoVar *var, PyObject *args)
{
    PyObject *value;
    uint32_t pos;

    if (!PyArg_ParseTuple(args, "iO", &pos, &value))
      return NULL;
    if (cxoVar_setValue(var, pos, value) < 0)
      return NULL;

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoVar_externalGetValue()
//   Return the value of the variable at the given position.
//-----------------------------------------------------------------------------
static PyObject *cxoVar_externalGetValue(cxoVar *var, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "pos", NULL };
    uint32_t pos = 0;

    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|i", keywordList,
            &pos))
        return NULL;
    return cxoVar_getValue(var, pos);
}


//-----------------------------------------------------------------------------
// cxoVar_externalGetActualElements()
//   Return the values of the variable at all positions as a list.
//-----------------------------------------------------------------------------
static PyObject *cxoVar_externalGetActualElements(cxoVar *var,
        void *unused)
{
    uint32_t numElements = var->allocatedElements;

    if (var->isArray &&
            dpiVar_getNumElementsInArray(var->handle, &numElements) < 0)
        return cxoError_raiseAndReturnNull();
    return PyInt_FromLong(numElements);
}


//-----------------------------------------------------------------------------
// cxoVar_externalGetValues()
//   Return the values of the variable at all positions as a list.
//-----------------------------------------------------------------------------
static PyObject *cxoVar_externalGetValues(cxoVar *var, void *unused)
{
    uint32_t numElements = var->allocatedElements;

    if (var->isArray &&
            dpiVar_getNumElementsInArray(var->handle, &numElements) < 0)
        return cxoError_raiseAndReturnNull();
    return cxoVar_getArrayValue(var, numElements, NULL);
}


//-----------------------------------------------------------------------------
// cxoVar_repr()
//   Return a string representation of the variable.
//-----------------------------------------------------------------------------
static PyObject *cxoVar_repr(cxoVar *var)
{
    PyObject *value, *module, *name, *result;
    uint32_t numElements;

    if (var->isArray) {
        if (dpiVar_getNumElementsInArray(var->handle, &numElements) < 0)
            return cxoError_raiseAndReturnNull();
        value = cxoVar_getArrayValue(var, numElements, var->data);
    } else if (var->allocatedElements == 1)
        value = cxoVar_getSingleValue(var, NULL, 0);
    else value = cxoVar_getArrayValue(var, var->allocatedElements, NULL);
    if (!value)
        return NULL;
    if (cxoUtils_getModuleAndName(Py_TYPE(var), &module, &name) < 0) {
        Py_DECREF(value);
        return NULL;
    }
    result = cxoUtils_formatString("<%s.%s with value %r>",
            PyTuple_Pack(3, module, name, value));
    Py_DECREF(module);
    Py_DECREF(name);
    Py_DECREF(value);
    return result;
}

