/*
 * Definition of a `Connection` type.  
 * Used by `socket_connection.c` and `pipe_connection.c`.
 *
 * connection.h
 *
 * Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
 */

#ifndef CONNECTION_H
#define CONNECTION_H

/*
 * Allocation and deallocation
 */

static PyObject *
Connection_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Connection *self;
    HANDLE handle;
    BOOL make_duplicate = TRUE, make_inheritable = TRUE;
    static char *kwlist[] = {"handle", "duplicate", "inheritable", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, F_HANDLE "|ii", kwlist, 
                                 &handle, &make_duplicate, &make_inheritable))
        return NULL;

    if (handle == INVALID_HANDLE_VALUE || (Py_ssize_t)handle < 0) {
        PyErr_Format(PyExc_IOError, "invalid handle %" PY_FORMAT_SIZE_T "d", 
                     (Py_ssize_t)handle);
        return NULL;
    }
    
    self = (Connection*)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;

    self->weakreflist = NULL;

    if (make_duplicate)
        self->handle = DUPLICATE(handle);
    else
        self->handle = handle;

    if (self->handle == INVALID_HANDLE_VALUE) {
        self->ob_type->tp_free((PyObject*)self);
        return SetException(PyExc_IOError, STANDARD_ERROR);
    }

#ifdef MS_WINDOWS
    if (make_inheritable) {
        if (!SetHandleInformation(self->handle, HANDLE_FLAG_INHERIT, 
                                  HANDLE_FLAG_INHERIT))
        {
            PyErr_SetExcFromWindowsErr(PyExc_IOError, 0);
            Py_BEGIN_ALLOW_THREADS
            CloseHandle(self->handle);
            Py_END_ALLOW_THREADS
            SetLastError(0);
            self->ob_type->tp_free((PyObject*)self);
            return NULL;
        }
    }
#endif
    
    return (PyObject*)self;
}

static void
Connection_dealloc(Connection* self)
{
    if (self->weakreflist != NULL)
        PyObject_ClearWeakRefs((PyObject*)self);

    if (self->handle != INVALID_HANDLE_VALUE) {
        Py_BEGIN_ALLOW_THREADS
        CLOSE(self->handle);
        Py_END_ALLOW_THREADS
    }
    self->ob_type->tp_free((PyObject*)self);
}

/*
 * Functions for transferring buffers
 */

static PyObject *
Connection_sendbytes(Connection* self, PyObject *args)
{
    char *buffer;
    Py_ssize_t length;
    int res;
    
    if (!PyArg_ParseTuple(args, "s#", &buffer, &length))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    res = conn_send_string(self, buffer, length);
    Py_END_ALLOW_THREADS

    if (res < 0)
        return SetException(PyExc_IOError, res);

    Py_RETURN_NONE;
}

static PyObject *
Connection_recvbytes(Connection *self) 
{
    char *freeme = NULL;
    Py_ssize_t nbytes;
    PyObject *result = NULL;

    Py_BEGIN_ALLOW_THREADS
    nbytes = conn_recv_string(self, self->buffer, BUFFER_SIZE, &freeme);
    Py_END_ALLOW_THREADS

    if (nbytes < 0) {
        SetException(PyExc_IOError, nbytes);
    } else {    
        if (freeme == NULL) {
            result = PyString_FromStringAndSize(self->buffer, nbytes);
        } else {
            result = PyString_FromStringAndSize(freeme, nbytes);
            PyMem_Free(freeme);
        }
    }
    
    return result;
}

static PyObject *
Connection_recvbytes_into(Connection *self, PyObject *args) 
{
    char *freeme = NULL, *buffer = NULL;
    Py_ssize_t nbytes, length, offset=0;
    PyObject *result = NULL;

    if (!PyArg_ParseTuple(args, "w#|" F_PY_SSIZE_T, &buffer, &length, &offset))
        return NULL;
    
    if (offset < 0) {
        PyErr_SetString(PyExc_ValueError, "negative offset");
        return NULL;
    }   

    if (offset > length) {
        PyErr_SetString(PyExc_ValueError, "offset too large");
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    nbytes = conn_recv_string(self, buffer+offset, length-offset, &freeme);
    Py_END_ALLOW_THREADS

    if (nbytes < 0) {
        SetException(PyExc_IOError, nbytes);
    } else {
        if (freeme == NULL) {
            result = PyInt_FromSsize_t(nbytes);
        } else {
            result = PyObject_CallFunction(BufferTooShort, 
                                           "s#", freeme, nbytes);
            PyMem_Free(freeme);
            PyErr_SetObject(BufferTooShort, result);
            Py_XDECREF(result);
            return NULL;
        }
    }
    
    return result;
}

/*
 * Functions for transferring objects
 */

static PyObject *
Connection_send_obj(Connection *self, PyObject *obj)
{
    char *buffer;
    int res;
    Py_ssize_t length;
    PyObject *pickled_string = NULL;

    pickled_string = PyObject_CallFunctionObjArgs(dumpsFunction, obj, 
                                                  protocol, NULL);
    if (!pickled_string)
        goto failure;

    if (PyString_AsStringAndSize(pickled_string, &buffer, &length) < 0)
        goto failure;

    if (TOO_LONG(length)) {
        PyErr_SetString(PyExc_ValueError, "string too long");
        goto failure;
    }

    Py_BEGIN_ALLOW_THREADS
    res = conn_send_string(self, buffer, (int)length);
    Py_END_ALLOW_THREADS
        
    if (res < 0) {
        SetException(PyExc_IOError, res);
        goto failure;
    }
    
    Py_XDECREF(pickled_string);
    Py_RETURN_NONE;

 failure:
    Py_XDECREF(pickled_string);
    return NULL;
}

static PyObject *
Connection_recv_obj(Connection *self)
{
    char *freeme = NULL;
    Py_ssize_t nbytes;
    PyObject *result = NULL;
    
    Py_BEGIN_ALLOW_THREADS
    nbytes = conn_recv_string(self, self->buffer, BUFFER_SIZE, &freeme);
    Py_END_ALLOW_THREADS
        
    if (nbytes < 0) {
        SetException(PyExc_IOError, nbytes);
    } else {    
        if (freeme == NULL) {
            result = PyObject_CallFunction(loadsFunction, "s#", 
                                           self->buffer, nbytes);
        } else {
            result = PyObject_CallFunction(loadsFunction, "s#", 
                                           freeme, nbytes);
            PyMem_Free(freeme);
        }
    }
    
    return result;
}

/*
 * Other functions
 */

static PyObject *
Connection_poll(Connection *self, PyObject *args)
{
    PyObject *timeout_obj = NULL;
    double timeout = 0.0;
    int res;
    
    if (!PyArg_ParseTuple(args, "|O", &timeout_obj))
        return NULL;

    if (timeout_obj == NULL) {
        timeout = 0.0;
    } else if (timeout_obj == Py_None) {
        timeout = -1.0;                         /* block forever */
    } else {
        timeout = PyFloat_AsDouble(timeout_obj);
        if (PyErr_Occurred())
            return NULL;
        if (timeout < 0.0)
            timeout = 0.0;
    }
    
    Py_BEGIN_ALLOW_THREADS
    res = conn_poll(self, timeout);
    Py_END_ALLOW_THREADS

    switch (res) {
    case TRUE:
        Py_RETURN_TRUE;
    case FALSE:
        Py_RETURN_FALSE;
    default:
        return SetException(PyExc_IOError, res);
    }
}

static PyObject *
Connection_fileno(Connection* self)
{
    if (self->handle == INVALID_HANDLE_VALUE) {
        PyErr_SetString(PyExc_IOError, "handle is invalid");
        return NULL;
    }
    return PyInt_FromLong((long)self->handle);
}

static PyObject *
Connection_close(Connection *self)
{
    if (self->handle != INVALID_HANDLE_VALUE) {
        Py_BEGIN_ALLOW_THREADS
        CLOSE(self->handle);
        Py_END_ALLOW_THREADS
        self->handle = INVALID_HANDLE_VALUE;
    }
    
    Py_RETURN_NONE;
}

static PyObject *
Connection_repr(Connection *self)
{
    return PyString_FromFormat("%s(handle=%" PY_FORMAT_SIZE_T "d)", 
                               CONNECTION_NAME, (Py_ssize_t)self->handle);
}

/*
 * Getters and setters
 */

static PyObject *
Connection_closed(Connection *self, void *closure)
{
    return PyBool_FromLong(self->handle == INVALID_HANDLE_VALUE);
}

/*
 * Method table
 */

static PyMethodDef Connection_methods[] = {

    {"sendBytes", (PyCFunction)Connection_sendbytes, METH_VARARGS, 
     "send the byte data from a readable buffer-like object"},
    {"recvBytes", (PyCFunction)Connection_recvbytes, METH_NOARGS, 
     "receive byte data as a string"},
    {"recvBytesInto", (PyCFunction)Connection_recvbytes_into, METH_VARARGS, 
     "receive byte data into a writeable buffer-like object\n"
     "returns the number of bytes read"},
    
    {"send", (PyCFunction)Connection_send_obj, METH_O, 
     "send a (picklable) object"},
    {"recv", (PyCFunction)Connection_recv_obj, METH_NOARGS, 
     "receive a (picklable) object"},

    {"poll", (PyCFunction)Connection_poll, METH_VARARGS, 
     "whether there is any input available to be read"},
    {"fileno", (PyCFunction)Connection_fileno, METH_NOARGS,
     "file descriptor or handle of the connection"},    
    {"close", (PyCFunction)Connection_close, METH_NOARGS,
     "close the connection"},

    /* deprecated names */
    {"sendbytes", (PyCFunction)Connection_sendbytes, METH_VARARGS, 
     "send the byte data from a readable buffer-like object"},
    {"recvbytes", (PyCFunction)Connection_recvbytes, METH_NOARGS, 
     "receive byte data as a string"},
    {"recvbytes_into", (PyCFunction)Connection_recvbytes_into, METH_VARARGS, 
     "receive byte data into a writeable buffer-like object\n"
     "returns the number of bytes read"},

    {NULL}  /* Sentinel */
};

/*
 * Member table
 */

static PyGetSetDef Connection_getsetters[] = {
    {"closed", (getter)Connection_closed, NULL, 
     "True if the connection is closed", NULL},
    {NULL}
};

/*
 * Connection type
 */

PyTypeObject CONNECTION_TYPE = {
    PyObject_HEAD_INIT(NULL)
    0,                         /* ob_size */
    "_processing." CONNECTION_NAME,
                               /* tp_name */
    sizeof(Connection),        /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)Connection_dealloc, 
                               /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_compare */
    (reprfunc)Connection_repr, /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_WEAKREFS, 
                               /* tp_flags */
    "Connection type whose constructor signature is\n\n"
    "    Connection(handle, duplicate=True, inheritable=True).\n\n"
    "If duplicate is true then the connection uses a copy of handle;\n"
    "otherwise the connection claims ownership of the handle.\n"
    "On Windows inheritable determines whether the handle is made\n"
    "inheritable; on Unix it is ignored.",
                               /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    offsetof(Connection, weakreflist),
                               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Connection_methods,        /* tp_methods */
    0,                         /* tp_members */
    Connection_getsetters,     /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */ 
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    (newfunc)Connection_new,   /* tp_new */
};

#endif /* CONNECTION_H */
