//-----------------------------------------------------------------------------
// Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoObjectAttr.c
//   Defines the routines for handling attributes of Oracle types.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of functions
//-----------------------------------------------------------------------------
static void cxoObjectAttr_free(cxoObjectAttr*);
static PyObject *cxoObjectAttr_repr(cxoObjectAttr*);


//-----------------------------------------------------------------------------
// declaration of members for Python type "ObjectAttribute"
//-----------------------------------------------------------------------------
static PyMemberDef cxoObjectAttrMembers[] = {
    { "name", T_OBJECT, offsetof(cxoObjectAttr, name), READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declaration
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeObjectAttr = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.ObjectAttribute",        // tp_name
    sizeof(cxoObjectAttr),              // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoObjectAttr_free,    // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoObjectAttr_repr,      // tp_repr
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
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    0,                                  // tp_methods
    cxoObjectAttrMembers,               // tp_members
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
// cxoObjectAttr_initialize()
//   Initialize the new object attribute.
//-----------------------------------------------------------------------------
static int cxoObjectAttr_initialize(cxoObjectAttr *attr,
        cxoConnection *connection)
{
    dpiObjectAttrInfo info;

    if (dpiObjectAttr_getInfo(attr->handle, &info) < 0)
        return cxoError_raiseAndReturnInt();
    attr->transformNum = cxoTransform_getNumFromDataTypeInfo(&info.typeInfo);
    attr->oracleTypeNum = info.typeInfo.oracleTypeNum;
    attr->name = cxoPyString_fromEncodedString(info.name, info.nameLength,
            connection->encodingInfo.encoding, NULL);
    if (!attr->name)
        return -1;
    if (info.typeInfo.objectType) {
        attr->type = cxoObjectType_new(connection,
                info.typeInfo.objectType);
        if (!attr->type)
            return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoObjectAttr_new()
//   Allocate a new object attribute.
//-----------------------------------------------------------------------------
cxoObjectAttr *cxoObjectAttr_new(cxoConnection *connection,
        dpiObjectAttr *handle)
{
    cxoObjectAttr *attr;

    attr = (cxoObjectAttr*)
            cxoPyTypeObjectAttr.tp_alloc(&cxoPyTypeObjectAttr, 0);
    if (!attr) {
        dpiObjectAttr_release(handle);
        return NULL;
    }
    attr->handle = handle;
    if (cxoObjectAttr_initialize(attr, connection) < 0) {
        Py_DECREF(attr);
        return NULL;
    }

    return attr;
}


//-----------------------------------------------------------------------------
// cxoObjectAttr_free()
//   Free the memory associated with an object attribute.
//-----------------------------------------------------------------------------
static void cxoObjectAttr_free(cxoObjectAttr *attr)
{
    if (attr->handle) {
        dpiObjectAttr_release(attr->handle);
        attr->handle = NULL;
    }
    Py_CLEAR(attr->name);
    Py_CLEAR(attr->type);
    Py_TYPE(attr)->tp_free((PyObject*) attr);
}


//-----------------------------------------------------------------------------
// cxoObjectAttr_repr()
//   Return a string representation of the object attribute.
//-----------------------------------------------------------------------------
static PyObject *cxoObjectAttr_repr(cxoObjectAttr *attr)
{
    PyObject *module, *name, *result;

    if (cxoUtils_getModuleAndName(Py_TYPE(attr), &module, &name) < 0)
        return NULL;
    result = cxoUtils_formatString("<%s.%s %s>",
            PyTuple_Pack(3, module, name, attr->name));
    Py_DECREF(module);
    Py_DECREF(name);
    return result;
}

