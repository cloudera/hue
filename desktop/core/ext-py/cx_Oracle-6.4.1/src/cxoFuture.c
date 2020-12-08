//-----------------------------------------------------------------------------
// Copyright 2018, Oracle and/or its affiliates. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoFuture.c
//   Defines the object used for managing behavior changes. This object permits
// setting any attribute to any value but only tracks certain values.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// functions for the Python type "Object"
//-----------------------------------------------------------------------------
static void cxoFuture_free(cxoFuture*);
static PyObject *cxoFuture_getAttr(cxoFuture*, PyObject*);
static int cxoFuture_setAttr(cxoFuture*, PyObject*, PyObject*);


//-----------------------------------------------------------------------------
// Python type declaration
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeFuture = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.__future__",             // tp_name
    sizeof(cxoFuture),                  // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoFuture_free,        // tp_dealloc
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
    (getattrofunc) cxoFuture_getAttr,   // tp_getattro
    (setattrofunc) cxoFuture_setAttr,   // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT                  // tp_flags
};


//-----------------------------------------------------------------------------
// cxoFuture_free()
//   Free the future object and reset global.
//-----------------------------------------------------------------------------
static void cxoFuture_free(cxoFuture *obj)
{
    Py_TYPE(obj)->tp_free((PyObject*) obj);
    cxoFutureObj = NULL;
}


//-----------------------------------------------------------------------------
// cxoFuture_getAttr()
//   Retrieve an attribute on an object.
//-----------------------------------------------------------------------------
static PyObject *cxoFuture_getAttr(cxoFuture *obj, PyObject *nameObject)
{
    cxoBuffer buffer;
    PyObject *result;

    if (cxoBuffer_fromObject(&buffer, nameObject, NULL) < 0)
        return NULL;
    if (strncmp(buffer.ptr, "ctx_mgr_close", buffer.size) == 0)
        result = PyBool_FromLong(obj->contextManagerClose);
    else if (strncmp(buffer.ptr, "dml_ret_array_val", buffer.size) == 0)
        result = PyBool_FromLong(obj->dmlReturningArray);
    else {
        Py_INCREF(Py_None);
        result = Py_None;
    }
    cxoBuffer_clear(&buffer);
    return result;
}


//-----------------------------------------------------------------------------
// cxoFuture_setAttr()
//   Set an attribute on an object.
//-----------------------------------------------------------------------------
static int cxoFuture_setAttr(cxoFuture *obj, PyObject *nameObject,
        PyObject *value)
{
    cxoBuffer buffer;
    int result = 0;

    if (cxoBuffer_fromObject(&buffer, nameObject, NULL) < 0)
        return -1;
    if (strncmp(buffer.ptr, "ctx_mgr_close", buffer.size) == 0)
        result = cxoUtils_getBooleanValue(value, 0, &obj->contextManagerClose);
    else if (strncmp(buffer.ptr, "dml_ret_array_val", buffer.size) == 0)
        result = cxoUtils_getBooleanValue(value, 0, &obj->dmlReturningArray);
    cxoBuffer_clear(&buffer);
    return result;
}

