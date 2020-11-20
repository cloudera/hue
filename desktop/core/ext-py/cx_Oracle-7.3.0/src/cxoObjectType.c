//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoObjectType.c
//   Defines the routines for handling Oracle type information.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of functions
//-----------------------------------------------------------------------------
static void cxoObjectType_free(cxoObjectType*);
static PyObject *cxoObjectType_repr(cxoObjectType*);
static PyObject *cxoObjectType_newObject(cxoObjectType*, PyObject*, PyObject*);


//-----------------------------------------------------------------------------
// declaration of methods for Python type "ObjectType"
//-----------------------------------------------------------------------------
static PyMethodDef cxoObjectTypeMethods[] = {
    { "newobject", (PyCFunction) cxoObjectType_newObject,
            METH_VARARGS | METH_KEYWORDS },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of members for Python type "ObjectType"
//-----------------------------------------------------------------------------
static PyMemberDef cxoObjectTypeMembers[] = {
    { "schema", T_OBJECT, offsetof(cxoObjectType, schema), READONLY },
    { "name", T_OBJECT, offsetof(cxoObjectType, name), READONLY },
    { "attributes", T_OBJECT, offsetof(cxoObjectType, attributes), READONLY },
    { "elementType", T_OBJECT, offsetof(cxoObjectType, elementType),
            READONLY },
    { "iscollection", T_BOOL, offsetof(cxoObjectType, isCollection),
            READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.ObjectType",             // tp_name
    sizeof(cxoObjectType),              // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoObjectType_free,    // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoObjectType_repr,      // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    (ternaryfunc) cxoObjectType_newObject, // tp_call
    0,                                  // tp_str
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
    cxoObjectTypeMethods,               // tp_methods
    cxoObjectTypeMembers,               // tp_members
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
// cxoObjectType_initialize()
//   Initialize the object type with the information that is required.
//-----------------------------------------------------------------------------
static int cxoObjectType_initialize(cxoObjectType *objType,
        cxoConnection *connection)
{
    dpiObjectAttr **attributes;
    dpiObjectTypeInfo info;
    cxoObjectAttr *attr;
    uint16_t i;

    // get object type information
    if (dpiObjectType_getInfo(objType->handle, &info) < 0)
        return cxoError_raiseAndReturnInt();
    Py_INCREF(connection);
    objType->connection = connection;
    objType->schema = cxoPyString_fromEncodedString(info.schema,
            info.schemaLength, connection->encodingInfo.encoding, NULL);
    if (!objType->schema)
        return -1;
    objType->name = cxoPyString_fromEncodedString(info.name, info.nameLength,
            connection->encodingInfo.encoding, NULL);
    if (!objType->name)
        return -1;
    objType->isCollection = info.isCollection;
    objType->elementOracleTypeNum = info.elementTypeInfo.oracleTypeNum;
    objType->elementTransformNum =
            cxoTransform_getNumFromDataTypeInfo(&info.elementTypeInfo);
    if (info.elementTypeInfo.objectType) {
        objType->elementType = (PyObject*) cxoObjectType_new(connection,
                info.elementTypeInfo.objectType);
        if (!objType->elementType)
            return -1;
    }

    // allocate the attribute list (temporary and permanent) and dictionary
    objType->attributes = PyList_New(info.numAttributes);
    if (!objType->attributes)
        return -1;
    objType->attributesByName = PyDict_New();
    if (!objType->attributesByName)
        return -1;

    // get the list of attributes from DPI
    attributes = PyMem_Malloc(sizeof(dpiObjectAttr*) * info.numAttributes);
    if (!attributes) {
        PyErr_NoMemory();
        return -1;
    }
    if (dpiObjectType_getAttributes(objType->handle, info.numAttributes,
            attributes) < 0) {
        PyMem_Free(attributes);
        return cxoError_raiseAndReturnInt();
    }

    // create attribute information for each attribute
    for (i = 0; i < info.numAttributes; i++) {
        attr = cxoObjectAttr_new(connection, attributes[i]);
        if (!attr) {
            PyMem_Free(attributes);
            return -1;
        }
        PyList_SET_ITEM(objType->attributes, i, (PyObject*) attr);
        if (PyDict_SetItem(objType->attributesByName, attr->name,
                (PyObject*) attr) < 0)
            return -1;
    }
    PyMem_Free(attributes);
    return 0;
}


//-----------------------------------------------------------------------------
// cxoObjectType_new()
//   Allocate a new object type.
//-----------------------------------------------------------------------------
cxoObjectType *cxoObjectType_new(cxoConnection *connection,
        dpiObjectType *handle)
{
    cxoObjectType *objType;

    objType = (cxoObjectType*)
            cxoPyTypeObjectType.tp_alloc(&cxoPyTypeObjectType, 0);
    if (!objType)
        return NULL;
    if (dpiObjectType_addRef(handle) < 0) {
        Py_DECREF(objType);
        cxoError_raiseAndReturnNull();
        return NULL;
    }
    objType->handle = handle;
    if (cxoObjectType_initialize(objType, connection) < 0) {
        Py_DECREF(objType);
        return NULL;
    }

    return objType;
}


//-----------------------------------------------------------------------------
// cxoObjectType_newByName()
//   Create a new object type given its name.
//-----------------------------------------------------------------------------
cxoObjectType *cxoObjectType_newByName(cxoConnection *connection,
        PyObject *name)
{
    cxoObjectType *objType;
    dpiObjectType *handle;
    cxoBuffer buffer;
    int status;

    if (cxoBuffer_fromObject(&buffer, name,
            connection->encodingInfo.encoding) < 0)
        return NULL;
    status = dpiConn_getObjectType(connection->handle, buffer.ptr,
            buffer.size, &handle);
    cxoBuffer_clear(&buffer);
    if (status < 0)
        return (cxoObjectType*) cxoError_raiseAndReturnNull();
    objType = cxoObjectType_new(connection, handle);
    dpiObjectType_release(handle);
    return objType;
}


//-----------------------------------------------------------------------------
// cxoObjectType_free()
//   Free the memory associated with an object type.
//-----------------------------------------------------------------------------
static void cxoObjectType_free(cxoObjectType *objType)
{
    if (objType->handle) {
        dpiObjectType_release(objType->handle);
        objType->handle = NULL;
    }
    Py_CLEAR(objType->connection);
    Py_CLEAR(objType->schema);
    Py_CLEAR(objType->name);
    Py_CLEAR(objType->attributes);
    Py_CLEAR(objType->attributesByName);
    Py_CLEAR(objType->elementType);
    Py_TYPE(objType)->tp_free((PyObject*) objType);
}


//-----------------------------------------------------------------------------
// cxoObjectType_repr()
//   Return a string representation of the object type.
//-----------------------------------------------------------------------------
static PyObject *cxoObjectType_repr(cxoObjectType *objType)
{
    PyObject *module, *name, *result;

    if (cxoUtils_getModuleAndName(Py_TYPE(objType), &module, &name) < 0)
        return NULL;
    result = cxoUtils_formatString("<%s.%s %s.%s>",
            PyTuple_Pack(4, module, name, objType->schema, objType->name));
    Py_DECREF(module);
    Py_DECREF(name);
    return result;
}


//-----------------------------------------------------------------------------
// cxoObjectType_newObject()
//   Factory function for creating objects of the type which can be bound.
//-----------------------------------------------------------------------------
static PyObject *cxoObjectType_newObject(cxoObjectType *objType,
        PyObject *args, PyObject *keywordArgs)
{
    static char *keywordList[] = { "value", NULL };
    PyObject *initialValue;
    dpiObject *handle;
    cxoObject *obj;

    // parse arguments
    initialValue = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|O", keywordList,
            &initialValue))
        return NULL;

    // get handle to newly created object
    if (dpiObjectType_createObject(objType->handle, &handle) < 0)
        return cxoError_raiseAndReturnNull();

    // create the object
    obj = (cxoObject*) cxoObject_new(objType, handle);
    if (!obj) {
        dpiObject_release(handle);
        return NULL;
    }

    // populate collection, if applicable
    if (initialValue) {
        if (cxoObject_internalExtend(obj, initialValue) < 0) {
            Py_DECREF(obj);
            return NULL;
        }
    }

    return (PyObject*) obj;
}

