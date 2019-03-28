//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoObject.c
//   Defines the routines for handling objects in Oracle.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// functions for the Python type "Object"
//-----------------------------------------------------------------------------
static void cxoObject_free(cxoObject*);
static PyObject *cxoObject_getAttr(cxoObject*, PyObject*);
static PyObject *cxoObject_repr(cxoObject*);
static int cxoObject_setAttr(cxoObject*, PyObject*, PyObject*);
static PyObject *cxoObject_append(cxoObject*, PyObject*);
static PyObject *cxoObject_asDict(cxoObject*, PyObject*);
static PyObject *cxoObject_asList(cxoObject*, PyObject*);
static PyObject *cxoObject_copy(cxoObject*, PyObject*);
static PyObject *cxoObject_delete(cxoObject*, PyObject*);
static PyObject *cxoObject_exists(cxoObject*, PyObject*);
static PyObject *cxoObject_extend(cxoObject*, PyObject*);
static PyObject *cxoObject_getElement(cxoObject*, PyObject*);
static PyObject *cxoObject_getFirstIndex(cxoObject*, PyObject*);
static PyObject *cxoObject_getLastIndex(cxoObject*, PyObject*);
static PyObject *cxoObject_getNextIndex(cxoObject*, PyObject*);
static PyObject *cxoObject_getPrevIndex(cxoObject*, PyObject*);
static PyObject *cxoObject_getSize(cxoObject*, PyObject*);
static PyObject *cxoObject_setElement(cxoObject*, PyObject*);
static PyObject *cxoObject_trim(cxoObject*, PyObject*);


//-----------------------------------------------------------------------------
// declaration of methods for Python type "Object"
//-----------------------------------------------------------------------------
static PyMethodDef cxoObjectMethods[] = {
    { "append", (PyCFunction) cxoObject_append, METH_O },
    { "asdict", (PyCFunction) cxoObject_asDict, METH_NOARGS },
    { "aslist", (PyCFunction) cxoObject_asList, METH_NOARGS },
    { "copy", (PyCFunction) cxoObject_copy, METH_NOARGS },
    { "delete", (PyCFunction) cxoObject_delete, METH_VARARGS },
    { "exists", (PyCFunction) cxoObject_exists, METH_VARARGS },
    { "extend", (PyCFunction) cxoObject_extend, METH_O },
    { "first", (PyCFunction) cxoObject_getFirstIndex, METH_NOARGS },
    { "getelement", (PyCFunction) cxoObject_getElement, METH_VARARGS },
    { "last", (PyCFunction) cxoObject_getLastIndex, METH_NOARGS },
    { "next", (PyCFunction) cxoObject_getNextIndex, METH_VARARGS },
    { "prev", (PyCFunction) cxoObject_getPrevIndex, METH_VARARGS },
    { "setelement", (PyCFunction) cxoObject_setElement, METH_VARARGS },
    { "size", (PyCFunction) cxoObject_getSize, METH_NOARGS },
    { "trim", (PyCFunction) cxoObject_trim, METH_VARARGS },
    { NULL, NULL }
};


//-----------------------------------------------------------------------------
// Declaration of members for Python type "Object".
//-----------------------------------------------------------------------------
static PyMemberDef cxoObjectMembers[] = {
    { "type", T_OBJECT, offsetof(cxoObject, objectType), READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declaration
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeObject = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.Object",                 // tp_name
    sizeof(cxoObject),                  // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoObject_free,        // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoObject_repr,          // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    0,                                  // tp_call
    0,                                  // tp_str
    (getattrofunc) cxoObject_getAttr,   // tp_getattro
    (setattrofunc) cxoObject_setAttr,   // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    cxoObjectMethods,                   // tp_methods
    cxoObjectMembers                    // tp_members
};


//-----------------------------------------------------------------------------
// cxoObject_new()
//   Create a new object.
//-----------------------------------------------------------------------------
PyObject *cxoObject_new(cxoObjectType *objectType, dpiObject *handle)
{
    cxoObject *obj;

    obj = (cxoObject*) cxoPyTypeObject.tp_alloc(&cxoPyTypeObject, 0);
    if (!obj)
        return NULL;
    Py_INCREF(objectType);
    obj->objectType = objectType;
    obj->handle = handle;
    return (PyObject*) obj;
}


//-----------------------------------------------------------------------------
// cxoObject_free()
//   Free an object.
//-----------------------------------------------------------------------------
static void cxoObject_free(cxoObject *obj)
{
    if (obj->handle) {
        dpiObject_release(obj->handle);
        obj->handle = NULL;
    }
    Py_CLEAR(obj->objectType);
    Py_TYPE(obj)->tp_free((PyObject*) obj);
}


//-----------------------------------------------------------------------------
// cxoObject_repr()
//   Return a string representation of the object.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_repr(cxoObject *obj)
{
    PyObject *module, *name, *result;

    if (cxoUtils_getModuleAndName(Py_TYPE(obj), &module, &name) < 0)
        return NULL;
    result = cxoUtils_formatString("<%s.%s %s.%s at %#x>",
            Py_BuildValue("(OOOOl)", module, name, obj->objectType->schema,
                    obj->objectType->name, obj));
    Py_DECREF(module);
    Py_DECREF(name);
    return result;
}


//-----------------------------------------------------------------------------
// cxoObject_convertFromPython()
//   Convert a Python value to an Oracle value.
//-----------------------------------------------------------------------------
static int cxoObject_convertFromPython(cxoObject *obj, PyObject *value,
        cxoTransformNum transformNum, dpiNativeTypeNum *nativeTypeNum,
        dpiData *data, cxoBuffer *buffer)
{
    dpiOracleTypeNum oracleTypeNum;

    // None is treated as null
    if (value == Py_None) {
        data->isNull = 1;
        return 0;
    }

    // convert the different Python types
    cxoTransform_getTypeInfo(transformNum, &oracleTypeNum, nativeTypeNum);
    if (cxoTransform_fromPython(transformNum, value, &data->value, buffer,
            obj->objectType->connection->encodingInfo.encoding,
            obj->objectType->connection->encodingInfo.nencoding, NULL, 0) < 0)
        return -1;
    data->isNull = 0;
    return 0;
}


//-----------------------------------------------------------------------------
// cxoObject_convertToPython()
//   Convert an Oracle value to a Python value.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_convertToPython(cxoObject *obj,
        cxoTransformNum transformNum, dpiData *data, cxoObjectType *objType)
{
    if (data->isNull)
        Py_RETURN_NONE;
    return cxoTransform_toPython(transformNum, obj->objectType->connection,
            objType, &data->value, NULL);
}


//-----------------------------------------------------------------------------
// cxoObject_getAttributeValue()
//   Retrieve an attribute on the object.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_getAttributeValue(cxoObject *obj,
        cxoObjectAttr *attribute)
{
    char numberAsStringBuffer[200], message[120];
    dpiOracleTypeNum oracleTypeNum;
    dpiNativeTypeNum nativeTypeNum;
    dpiData data;

    if (attribute->transformNum == CXO_TRANSFORM_UNSUPPORTED) {
        snprintf(message, sizeof(message), "Oracle type %d not supported.",
                attribute->oracleTypeNum);
        return cxoError_raiseFromString(cxoNotSupportedErrorException,
                message);
    }
    cxoTransform_getTypeInfo(attribute->transformNum, &oracleTypeNum,
            &nativeTypeNum);
    if (oracleTypeNum == DPI_ORACLE_TYPE_NUMBER &&
            nativeTypeNum == DPI_NATIVE_TYPE_BYTES) {
        data.value.asBytes.ptr = numberAsStringBuffer;
        data.value.asBytes.length = sizeof(numberAsStringBuffer);
        data.value.asBytes.encoding = NULL;
    }
    if (dpiObject_getAttributeValue(obj->handle, attribute->handle,
            nativeTypeNum, &data) < 0)
        return cxoError_raiseAndReturnNull();
    return cxoObject_convertToPython(obj, attribute->transformNum, &data,
            attribute->type);
}


//-----------------------------------------------------------------------------
// cxoObject_setAttributeValue()
//   Set an attribute on the object.
//-----------------------------------------------------------------------------
static int cxoObject_setAttributeValue(cxoObject *obj,
        cxoObjectAttr *attribute, PyObject *value)
{
    dpiNativeTypeNum nativeTypeNum = 0;
    cxoBuffer buffer;
    dpiData data;
    int status;

    cxoBuffer_init(&buffer);
    if (cxoObject_convertFromPython(obj, value, attribute->transformNum,
            &nativeTypeNum, &data, &buffer) < 0)
        return -1;
    status = dpiObject_setAttributeValue(obj->handle, attribute->handle,
            nativeTypeNum, &data);
    cxoBuffer_clear(&buffer);
    if (status < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoObject_getAttr()
//   Retrieve an attribute on an object.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_getAttr(cxoObject *obj, PyObject *nameObject)
{
    cxoObjectAttr *attribute;

    attribute = (cxoObjectAttr*)
            PyDict_GetItem(obj->objectType->attributesByName, nameObject);
    if (attribute)
        return cxoObject_getAttributeValue(obj, attribute);

    return PyObject_GenericGetAttr( (PyObject*) obj, nameObject);
}


//-----------------------------------------------------------------------------
// cxoObject_setAttr()
//   Set an attribute on an object.
//-----------------------------------------------------------------------------
static int cxoObject_setAttr(cxoObject *obj, PyObject *nameObject,
        PyObject *value)
{
    cxoObjectAttr *attribute;

    attribute = (cxoObjectAttr*)
            PyDict_GetItem(obj->objectType->attributesByName, nameObject);
    if (attribute)
        return cxoObject_setAttributeValue(obj, attribute, value);

    return PyObject_GenericSetAttr( (PyObject*) obj, nameObject, value);
}


//-----------------------------------------------------------------------------
// cxoObject_internalAppend()
//   Append an item to the collection.
//-----------------------------------------------------------------------------
static int cxoObject_internalAppend(cxoObject *obj, PyObject *value)
{
    dpiNativeTypeNum nativeTypeNum = 0;
    cxoBuffer buffer;
    dpiData data;
    int status;

    cxoBuffer_init(&buffer);
    if (cxoObject_convertFromPython(obj, value,
            obj->objectType->elementTransformNum, &nativeTypeNum, &data,
            &buffer) < 0)
        return -1;
    status = dpiObject_appendElement(obj->handle, nativeTypeNum, &data);
    cxoBuffer_clear(&buffer);
    if (status < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoObject_internalExtend()
//   Extend the collection by appending each of the items in the sequence.
//-----------------------------------------------------------------------------
int cxoObject_internalExtend(cxoObject *obj, PyObject *sequence)
{
    PyObject *fastSequence, *element;
    Py_ssize_t size, i;

    fastSequence = PySequence_Fast(sequence, "expecting sequence");
    if (!fastSequence)
        return -1;
    size = PySequence_Fast_GET_SIZE(fastSequence);
    for (i = 0; i < size; i++) {
        element = PySequence_Fast_GET_ITEM(fastSequence, i);
        if (cxoObject_internalAppend(obj, element) < 0) {
            Py_DECREF(fastSequence);
            return -1;
        }
    }
    Py_DECREF(fastSequence);
    
    return 0;
}


//-----------------------------------------------------------------------------
// cxoObject_append()
//   Append an item to the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_append(cxoObject *obj, PyObject *value)
{
    if (cxoObject_internalAppend(obj, value) < 0)
        return NULL;
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoObject_internalGetElementByIndex()
//   Internal method used for getting an element value for a particular index.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_internalGetElementByIndex(cxoObject *obj,
        int32_t index)
{
    char numberAsStringBuffer[200], message[120];
    dpiOracleTypeNum oracleTypeNum;
    dpiNativeTypeNum nativeTypeNum;
    dpiData data;

    if (obj->objectType->elementTransformNum == CXO_TRANSFORM_UNSUPPORTED) {
        snprintf(message, sizeof(message), "Oracle type %d not supported.",
                obj->objectType->elementOracleTypeNum);
        return cxoError_raiseFromString(cxoNotSupportedErrorException,
                message);
    }
    cxoTransform_getTypeInfo(obj->objectType->elementTransformNum,
            &oracleTypeNum, &nativeTypeNum);
    if (oracleTypeNum == DPI_ORACLE_TYPE_NUMBER &&
            nativeTypeNum == DPI_NATIVE_TYPE_BYTES) {
        data.value.asBytes.ptr = numberAsStringBuffer;
        data.value.asBytes.length = sizeof(numberAsStringBuffer);
        data.value.asBytes.encoding = NULL;
    }
    if (dpiObject_getElementValueByIndex(obj->handle, index, nativeTypeNum,
                &data) < 0)
        return cxoError_raiseAndReturnNull();
    return cxoObject_convertToPython(obj, obj->objectType->elementTransformNum,
            &data, (cxoObjectType*) obj->objectType->elementType);
}


//-----------------------------------------------------------------------------
// cxoObject_asDict()
//   Returns a collection as a dictionary. If the object is not a collection,
// an error is returned.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_asDict(cxoObject *obj, PyObject *args)
{
    PyObject *dict, *key, *value;
    int32_t index, nextIndex;
    int exists;

    // create the result dictionary
    dict = PyDict_New();
    if (!dict)
        return NULL;

    // populate it with each of the elements in the collection
    if (dpiObject_getFirstIndex(obj->handle, &index, &exists) < 0) {
        Py_DECREF(dict);
        return cxoError_raiseAndReturnNull();
    }
    while (exists) {
        value = cxoObject_internalGetElementByIndex(obj, index);
        if (!value) {
            Py_DECREF(dict);
            return NULL;
        }
        key = PyInt_FromLong(index);
        if (!key) {
            Py_DECREF(value);
            Py_DECREF(dict);
            return NULL;
        }
        if (PyDict_SetItem(dict, key, value) < 0) {
            Py_DECREF(key);
            Py_DECREF(value);
            Py_DECREF(dict);
            return NULL;
        }
        Py_DECREF(key);
        Py_DECREF(value);
        if (dpiObject_getNextIndex(obj->handle, index, &nextIndex,
                &exists) < 0) {
            Py_DECREF(dict);
            return cxoError_raiseAndReturnNull();
        }
        index = nextIndex;
    }

    return dict;
}


//-----------------------------------------------------------------------------
// cxoObject_asList()
//   Returns a collection as a list of elements. If the object is not a
// collection, an error is returned.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_asList(cxoObject *obj, PyObject *args)
{
    PyObject *list, *elementValue;
    int32_t index, nextIndex;
    int exists;

    // create the result list
    list = PyList_New(0);
    if (!list)
        return NULL;

    // populate it with each of the elements in the list
    if (dpiObject_getFirstIndex(obj->handle, &index, &exists) < 0) {
        Py_DECREF(list);
        return cxoError_raiseAndReturnNull();
    }
    while (exists) {
        elementValue = cxoObject_internalGetElementByIndex(obj, index);
        if (!elementValue) {
            Py_DECREF(list);
            return NULL;
        }
        if (PyList_Append(list, elementValue) < 0) {
            Py_DECREF(elementValue);
            Py_DECREF(list);
            return NULL;
        }
        Py_DECREF(elementValue);
        if (dpiObject_getNextIndex(obj->handle, index, &nextIndex,
                &exists) < 0) {
            Py_DECREF(list);
            return cxoError_raiseAndReturnNull();
        }
        index = nextIndex;
    }

    return list;
}


//-----------------------------------------------------------------------------
// cxoObject_copy()
//   Return a copy of the object.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_copy(cxoObject *obj, PyObject *args)
{
    PyObject *copiedObj;
    dpiObject *handle;

    if (dpiObject_copy(obj->handle, &handle) < 0)
        return cxoError_raiseAndReturnNull();
    copiedObj = cxoObject_new(obj->objectType, handle);
    if (!copiedObj) {
        dpiObject_release(handle);
        return NULL;
    }
    return copiedObj;
}


//-----------------------------------------------------------------------------
// cxoObject_delete()
//   Delete the element at the specified index in the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_delete(cxoObject *obj, PyObject *args)
{
    int32_t index;

    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    if (dpiObject_deleteElementByIndex(obj->handle, index) < 0)
        return cxoError_raiseAndReturnNull();
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoObject_exists()
//   Return true or false indicating if an element exists in the collection at
// the specified index.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_exists(cxoObject *obj, PyObject *args)
{
    int32_t index;
    int exists;

    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    if (dpiObject_getElementExistsByIndex(obj->handle, index, &exists) < 0)
        return cxoError_raiseAndReturnNull();
    if (exists)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


//-----------------------------------------------------------------------------
// cxoObject_extend()
//   Extend the collection by appending each of the items in the sequence.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_extend(cxoObject *obj, PyObject *sequence)
{
    if (cxoObject_internalExtend(obj, sequence) < 0)
        return NULL;
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoObject_getElement()
//   Return the element at the given position in the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_getElement(cxoObject *obj, PyObject *args)
{
    int32_t index;

    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    return cxoObject_internalGetElementByIndex(obj, index);
}


//-----------------------------------------------------------------------------
// cxoObject_getFirstIndex()
//   Return the index of the first entry in the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_getFirstIndex(cxoObject *obj, PyObject *args)
{
    int32_t index;
    int exists;

    if (dpiObject_getFirstIndex(obj->handle, &index, &exists) < 0)
        return cxoError_raiseAndReturnNull();
    if (exists)
        return PyInt_FromLong(index);
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoObject_getLastIndex()
//   Return the index of the last entry in the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_getLastIndex(cxoObject *obj, PyObject *args)
{
    int32_t index;
    int exists;

    if (dpiObject_getLastIndex(obj->handle, &index, &exists) < 0)
        return cxoError_raiseAndReturnNull();
    if (exists)
        return PyInt_FromLong(index);
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoObject_getNextIndex()
//   Return the index of the next entry in the collection following the index
// specified. If there is no next entry, None is returned.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_getNextIndex(cxoObject *obj, PyObject *args)
{
    int32_t index, nextIndex;
    int exists;

    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    if (dpiObject_getNextIndex(obj->handle, index, &nextIndex, &exists) < 0)
        return cxoError_raiseAndReturnNull();
    if (exists)
        return PyInt_FromLong(nextIndex);
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoObject_getPrevIndex()
//   Return the index of the previous entry in the collection preceding the
// index specified. If there is no previous entry, None is returned.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_getPrevIndex(cxoObject *obj, PyObject *args)
{
    int32_t index, prevIndex;
    int exists;

    if (!PyArg_ParseTuple(args, "i", &index))
        return NULL;
    if (dpiObject_getPrevIndex(obj->handle, index, &prevIndex, &exists) < 0)
        return cxoError_raiseAndReturnNull();
    if (exists)
        return PyInt_FromLong(prevIndex);
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoObject_getSize()
//   Return the size of a collection. If the object is not a collection, an
// error is returned.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_getSize(cxoObject *obj, PyObject *args)
{
    int32_t size;

    if (dpiObject_getSize(obj->handle, &size) < 0)
        return cxoError_raiseAndReturnNull();
    return PyInt_FromLong(size);
}


//-----------------------------------------------------------------------------
// cxoObject_setElement()
//   Set the element at the specified location to the given value.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_setElement(cxoObject *obj, PyObject *args)
{
    dpiNativeTypeNum nativeTypeNum = 0;
    cxoBuffer buffer;
    PyObject *value;
    int32_t index;
    dpiData data;
    int status;

    if (!PyArg_ParseTuple(args, "iO", &index, &value))
        return NULL;
    cxoBuffer_init(&buffer);
    if (cxoObject_convertFromPython(obj, value,
            obj->objectType->elementTransformNum, &nativeTypeNum, &data,
            &buffer) < 0)
        return NULL;
    status = dpiObject_setElementValueByIndex(obj->handle, index,
            nativeTypeNum, &data);
    cxoBuffer_clear(&buffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoObject_trim()
//   Trim a number of elements from the end of the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoObject_trim(cxoObject *obj, PyObject *args)
{
    int32_t numToTrim;

    if (!PyArg_ParseTuple(args, "i", &numToTrim))
        return NULL;
    if (dpiObject_trim(obj->handle, numToTrim) < 0)
        return cxoError_raiseAndReturnNull();
    Py_RETURN_NONE;
}

