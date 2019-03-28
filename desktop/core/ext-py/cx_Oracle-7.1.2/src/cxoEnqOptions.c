//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoEnqOptions.c
//   Implements the enqueue options objects used in Advanced Queuing.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of methods used for enqueue options
//-----------------------------------------------------------------------------
static void cxoEnqOptions_free(cxoEnqOptions*);
static PyObject *cxoEnqOptions_getTransformation(cxoEnqOptions*, void*);
static PyObject *cxoEnqOptions_getVisibility(cxoEnqOptions*, void*);
static int cxoEnqOptions_setDeliveryMode(cxoEnqOptions*, PyObject*, void*);
static int cxoEnqOptions_setTransformation(cxoEnqOptions*, PyObject*, void*);
static int cxoEnqOptions_setVisibility(cxoEnqOptions*, PyObject*, void*);


//-----------------------------------------------------------------------------
// declaration of calculated members for Python type "EnqOptions"
//-----------------------------------------------------------------------------
static PyGetSetDef cxoEnqOptionsCalcMembers[] = {
    { "deliverymode", 0, (setter) cxoEnqOptions_setDeliveryMode, 0, 0 },
    { "transformation", (getter) cxoEnqOptions_getTransformation,
            (setter) cxoEnqOptions_setTransformation, 0, 0 },
    { "visibility", (getter) cxoEnqOptions_getVisibility,
            (setter) cxoEnqOptions_setVisibility, 0, 0 },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeEnqOptions = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.EnqOptions",             // tp_name
    sizeof(cxoEnqOptions),              // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoEnqOptions_free,    // tp_dealloc
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
    0,                                  // tp_members
    cxoEnqOptionsCalcMembers,           // tp_getset
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
// cxoEnqOptions_new()
//   Create a new enqueue options object.
//-----------------------------------------------------------------------------
cxoEnqOptions *cxoEnqOptions_new(cxoConnection *connection)
{
    cxoEnqOptions *self;

    self = (cxoEnqOptions*)
            cxoPyTypeEnqOptions.tp_alloc(&cxoPyTypeEnqOptions, 0);
    if (!self)
        return NULL;
    if (dpiConn_newEnqOptions(connection->handle, &self->handle) < 0) {
        Py_DECREF(self);
        cxoError_raiseAndReturnNull();
        return NULL;
    }
    self->encoding = connection->encodingInfo.encoding;

    return self;
}


//-----------------------------------------------------------------------------
// cxoEnqOptions_free()
//   Free the memory associated with the enqueue options object.
//-----------------------------------------------------------------------------
static void cxoEnqOptions_free(cxoEnqOptions *self)
{
    if (self->handle) {
        dpiEnqOptions_release(self->handle);
        self->handle = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject*) self);
}


//-----------------------------------------------------------------------------
// cxoEnqOptions_getTransformation()
//   Get the value of the transformation option.
//-----------------------------------------------------------------------------
static PyObject *cxoEnqOptions_getTransformation(cxoEnqOptions *self,
        void *unused)
{
    uint32_t valueLength;
    const char *value;

    if (dpiEnqOptions_getTransformation(self->handle, &value,
            &valueLength) < 0)
        return cxoError_raiseAndReturnNull();
    if (!value)
        Py_RETURN_NONE;
    return cxoPyString_fromEncodedString(value, valueLength, self->encoding,
            NULL);
}


//-----------------------------------------------------------------------------
// cxoEnqOptions_getVisibility()
//   Get the value of the visibility option.
//-----------------------------------------------------------------------------
static PyObject *cxoEnqOptions_getVisibility(cxoEnqOptions *self, void *unused)
{
    dpiVisibility value;

    if (dpiEnqOptions_getVisibility(self->handle, &value) < 0)
        return cxoError_raiseAndReturnNull();
    return PyInt_FromLong(value);
}


//-----------------------------------------------------------------------------
// cxoEnqOptions_setDeliveryMode()
//   Set the value of the delivery mode option.
//-----------------------------------------------------------------------------
static int cxoEnqOptions_setDeliveryMode(cxoEnqOptions *self, PyObject *valueObj,
        void *unused)
{
    dpiMessageDeliveryMode value;

    value = PyInt_AsLong(valueObj);
    if (PyErr_Occurred())
        return -1;
    if (dpiEnqOptions_setDeliveryMode(self->handle, value) < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoEnqOptions_setTransformation()
//   Set the value of the transformation option.
//-----------------------------------------------------------------------------
static int cxoEnqOptions_setTransformation(cxoEnqOptions *self,
        PyObject *valueObj, void *unused)
{
    cxoBuffer buffer;
    int status;

    if (cxoBuffer_fromObject(&buffer, valueObj, self->encoding) < 0)
        return -1;
    status = dpiEnqOptions_setTransformation(self->handle, buffer.ptr,
            buffer.size);
    cxoBuffer_clear(&buffer);
    if (status < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoEnqOptions_setVisibility()
//   Set the value of the visibility option.
//-----------------------------------------------------------------------------
static int cxoEnqOptions_setVisibility(cxoEnqOptions *self,
        PyObject *valueObj, void *unused)
{
    dpiVisibility value;

    value = PyInt_AsLong(valueObj);
    if (PyErr_Occurred())
        return -1;
    if (dpiEnqOptions_setVisibility(self->handle, value) < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}

