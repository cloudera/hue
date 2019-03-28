//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoMsgProps.c
//   Implements the message properties object used in Advanced Queuing.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of methods used for message properties
//-----------------------------------------------------------------------------
static void cxoMsgProps_free(cxoMsgProps*);
static PyObject *cxoMsgProps_getNumAttempts(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getCorrelation(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getDelay(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getDeliveryMode(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getEnqTime(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getExceptionQ(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getExpiration(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getOriginalMsgId(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getPriority(cxoMsgProps*, void*);
static PyObject *cxoMsgProps_getState(cxoMsgProps*, void*);
static int cxoMsgProps_setCorrelation(cxoMsgProps*, PyObject*, void*);
static int cxoMsgProps_setDelay(cxoMsgProps*, PyObject*, void*);
static int cxoMsgProps_setExceptionQ(cxoMsgProps*, PyObject*, void*);
static int cxoMsgProps_setExpiration(cxoMsgProps*, PyObject*, void*);
static int cxoMsgProps_setOriginalMsgId(cxoMsgProps*, PyObject*, void*);
static int cxoMsgProps_setPriority(cxoMsgProps*, PyObject*, void*);


//-----------------------------------------------------------------------------
// declaration of calculated members for Python type "MessageProperties"
//-----------------------------------------------------------------------------
static PyGetSetDef cxoMsgPropsCalcMembers[] = {
    { "attempts", (getter) cxoMsgProps_getNumAttempts, 0, 0, 0 },
    { "correlation", (getter) cxoMsgProps_getCorrelation,
            (setter) cxoMsgProps_setCorrelation, 0, 0 },
    { "delay", (getter) cxoMsgProps_getDelay, (setter) cxoMsgProps_setDelay, 0,
            0 },
    { "deliverymode", (getter) cxoMsgProps_getDeliveryMode, 0, 0, 0 },
    { "enqtime", (getter) cxoMsgProps_getEnqTime, 0, 0, 0 },
    { "exceptionq", (getter) cxoMsgProps_getExceptionQ,
            (setter) cxoMsgProps_setExceptionQ, 0, 0 },
    { "expiration", (getter) cxoMsgProps_getExpiration,
            (setter) cxoMsgProps_setExpiration, 0, 0 },
    { "msgid", (getter) cxoMsgProps_getOriginalMsgId,
            (setter) cxoMsgProps_setOriginalMsgId, 0, 0 },
    { "priority", (getter) cxoMsgProps_getPriority,
            (setter) cxoMsgProps_setPriority, 0, 0 },
    { "state", (getter) cxoMsgProps_getState, 0, 0, 0 },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeMsgProps = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.MessageProperties",      // tp_name
    sizeof(cxoMsgProps),                // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoMsgProps_free,      // tp_dealloc
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
    cxoMsgPropsCalcMembers,             // tp_getset
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
// cxoMsgProps_new()
//   Create a new message properties object.
//-----------------------------------------------------------------------------
cxoMsgProps *cxoMsgProps_new(cxoConnection *connection)
{
    cxoMsgProps *props;

    props = (cxoMsgProps*) cxoPyTypeMsgProps.tp_alloc(&cxoPyTypeMsgProps, 0);
    if (!props)
        return NULL;
    if (dpiConn_newMsgProps(connection->handle, &props->handle) < 0) {
        Py_DECREF(props);
        cxoError_raiseAndReturnNull();
        return NULL;
    }
    props->encoding = connection->encodingInfo.encoding;

    return props;
}


//-----------------------------------------------------------------------------
// cxoMsgProps_free()
//   Free the memory associated with the message properties object.
//-----------------------------------------------------------------------------
static void cxoMsgProps_free(cxoMsgProps *props)
{
    if (props->handle) {
        dpiMsgProps_release(props->handle);
        props->handle = NULL;
    }
    Py_TYPE(props)->tp_free((PyObject*) props);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getAttrInt32()
//   Get the value of the attribute as a 32-bit integer.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getAttrInt32(cxoMsgProps *props,
        int (*func)(dpiMsgProps *props, int32_t *value))
{
    int32_t value;

    if ((*func)(props->handle, &value) < 0)
        return cxoError_raiseAndReturnNull();
    return PyInt_FromLong(value);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_setAttrInt32()
//   Set the value of the attribute as a 32-bit integer.
//-----------------------------------------------------------------------------
static int cxoMsgProps_setAttrInt32(cxoMsgProps *props, PyObject *valueObj,
        int (*func)(dpiMsgProps *props, int32_t value))
{
    int32_t value;

    value = PyInt_AsLong(valueObj);
    if (PyErr_Occurred())
        return -1;
    if ((*func)(props->handle, value) < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getNumAttempts()
//   Get the value of the attempts property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getNumAttempts(cxoMsgProps *props, void *unused)
{
    return cxoMsgProps_getAttrInt32(props, dpiMsgProps_getNumAttempts);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getCorrelation()
//   Get the value of the correlation property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getCorrelation(cxoMsgProps *props, void *unused)
{
    uint32_t valueLength;
    const char *value;

    if (dpiMsgProps_getCorrelation(props->handle, &value, &valueLength) < 0)
        return cxoError_raiseAndReturnNull();
    if (!value)
        Py_RETURN_NONE;
    return cxoPyString_fromEncodedString(value, valueLength, props->encoding,
            NULL);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getDelay()
//   Get the value of the delay property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getDelay(cxoMsgProps *props, void *unused)
{
    return cxoMsgProps_getAttrInt32(props, dpiMsgProps_getDelay);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getDeliveryMode()
//   Get the value of the delivery mode property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getDeliveryMode(cxoMsgProps *props, void *unused)
{
    dpiMessageDeliveryMode value;

    if (dpiMsgProps_getDeliveryMode(props->handle, &value) < 0)
        return cxoError_raiseAndReturnNull();
    return PyInt_FromLong(value);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getEnqTime()
//   Get the value of the enqueue time property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getEnqTime(cxoMsgProps *props, void *unused)
{
    dpiDataBuffer buffer;

    if (dpiMsgProps_getEnqTime(props->handle, &buffer.asTimestamp) < 0)
        return cxoError_raiseAndReturnNull();
    return cxoTransform_toPython(CXO_TRANSFORM_DATETIME, NULL, NULL, &buffer,
            NULL);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getExceptionQ()
//   Get the value of the exception queue property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getExceptionQ(cxoMsgProps *props, void *unused)
{
    uint32_t valueLength;
    const char *value;

    if (dpiMsgProps_getExceptionQ(props->handle, &value, &valueLength) < 0)
        return cxoError_raiseAndReturnNull();
    if (!value)
        Py_RETURN_NONE;
    return cxoPyString_fromEncodedString(value, valueLength, props->encoding,
            NULL);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getExpiration()
//   Get the value of the expiration property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getExpiration(cxoMsgProps *props, void *unused)
{
    return cxoMsgProps_getAttrInt32(props, dpiMsgProps_getExpiration);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getOriginalMsgId()
//   Get the value of the expiration property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getOriginalMsgId(cxoMsgProps *props, void *unused)
{
    uint32_t valueLength;
    const char *value;

    if (dpiMsgProps_getOriginalMsgId(props->handle, &value, &valueLength) < 0)
        return cxoError_raiseAndReturnNull();
    if (!value)
        Py_RETURN_NONE;
    return PyBytes_FromStringAndSize(value, valueLength);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getPriority()
//   Get the value of the priority property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getPriority(cxoMsgProps *props, void *unused)
{
    return cxoMsgProps_getAttrInt32(props, dpiMsgProps_getPriority);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_getState()
//   Get the value of the state property.
//-----------------------------------------------------------------------------
static PyObject *cxoMsgProps_getState(cxoMsgProps *props, void *unused)
{
    dpiMessageState value;

    if (dpiMsgProps_getState(props->handle, &value) < 0)
        return cxoError_raiseAndReturnNull();
    return PyInt_FromLong(value);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_setCorrelation()
//   Set the value of the correlation property.
//-----------------------------------------------------------------------------
static int cxoMsgProps_setCorrelation(cxoMsgProps *props, PyObject *valueObj,
        void *unused)
{
    cxoBuffer buffer;
    int status;

    if (cxoBuffer_fromObject(&buffer, valueObj, props->encoding))
        return -1;
    status = dpiMsgProps_setCorrelation(props->handle, buffer.ptr,
            buffer.size);
    cxoBuffer_clear(&buffer);
    if (status < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoMsgProps_setDelay()
//   Set the value of the delay property.
//-----------------------------------------------------------------------------
static int cxoMsgProps_setDelay(cxoMsgProps *props, PyObject *valueObj,
        void *unused)
{
    return cxoMsgProps_setAttrInt32(props, valueObj, dpiMsgProps_setDelay);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_setExceptionQ()
//   Set the value of the exception queue property.
//-----------------------------------------------------------------------------
static int cxoMsgProps_setExceptionQ(cxoMsgProps *props, PyObject *valueObj,
        void *unused)
{
    cxoBuffer buffer;
    int status;

    if (cxoBuffer_fromObject(&buffer, valueObj, props->encoding))
        return -1;
    status = dpiMsgProps_setExceptionQ(props->handle, buffer.ptr, buffer.size);
    cxoBuffer_clear(&buffer);
    if (status < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoMsgProps_setExpiration()
//   Set the value of the expiration property.
//-----------------------------------------------------------------------------
static int cxoMsgProps_setExpiration(cxoMsgProps *props, PyObject *valueObj,
        void *unused)
{
    return cxoMsgProps_setAttrInt32(props, valueObj, dpiMsgProps_setExpiration);
}


//-----------------------------------------------------------------------------
// cxoMsgProps_setOriginalMsgId()
//   Set the value of the original message id property.
//-----------------------------------------------------------------------------
static int cxoMsgProps_setOriginalMsgId(cxoMsgProps *props, PyObject *valueObj,
        void *unused)
{
    Py_ssize_t valueLength;
    char *value;

    if (PyBytes_AsStringAndSize(valueObj, &value, &valueLength) < 0)
        return -1;
    if (dpiMsgProps_setOriginalMsgId(props->handle, value,
            (uint32_t) valueLength) < 0)
        return cxoError_raiseAndReturnInt();
    return 0;
}


//-----------------------------------------------------------------------------
// cxoMsgProps_setPriority()
//   Set the value of the expiration property.
//-----------------------------------------------------------------------------
static int cxoMsgProps_setPriority(cxoMsgProps *props, PyObject *valueObj,
        void *unused)
{
    return cxoMsgProps_setAttrInt32(props, valueObj, dpiMsgProps_setPriority);
}

