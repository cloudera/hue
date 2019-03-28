//-----------------------------------------------------------------------------
// Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoSodaDocCursor.c
//   Defines the routines for handling SODA document cursors. These cursors
// permit iterating over the documents that match the criteria that was
// specified by the user.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of functions
//-----------------------------------------------------------------------------
static void cxoSodaDocCursor_free(cxoSodaDocCursor*);
static PyObject *cxoSodaDocCursor_repr(cxoSodaDocCursor*);
static PyObject *cxoSodaDocCursor_getIter(cxoSodaDocCursor*);
static PyObject *cxoSodaDocCursor_getNext(cxoSodaDocCursor*);
static PyObject *cxoSodaDocCursor_close(cxoSodaDocCursor*, PyObject*);


//-----------------------------------------------------------------------------
// declaration of methods
//-----------------------------------------------------------------------------
static PyMethodDef cxoMethods[] = {
    { "close", (PyCFunction) cxoSodaDocCursor_close, METH_NOARGS },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeSodaDocCursor = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.SodaDocCursor",          // tp_name
    sizeof(cxoSodaDocCursor),           // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoSodaDocCursor_free, // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoSodaDocCursor_repr,   // tp_repr
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
    (getiterfunc) cxoSodaDocCursor_getIter,   // tp_iter
    (iternextfunc) cxoSodaDocCursor_getNext,  // tp_iternext
    cxoMethods,                         // tp_methods
    0,                                  // tp_members
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
// cxoSodaDocCursor_new()
//   Create a new SODA document cursor.
//-----------------------------------------------------------------------------
cxoSodaDocCursor *cxoSodaDocCursor_new(cxoSodaDatabase *db,
        dpiSodaDocCursor *handle)
{
    cxoSodaDocCursor *cursor;

    cursor = (cxoSodaDocCursor*)
            cxoPyTypeSodaDocCursor.tp_alloc(&cxoPyTypeSodaDocCursor, 0);
    if (!cursor) {
        dpiSodaDocCursor_release(handle);
        return NULL;
    }
    Py_INCREF(db);
    cursor->db = db;
    cursor->handle = handle;
    return cursor;
}


//-----------------------------------------------------------------------------
// cxoSodaDocCursor_free()
//   Free the memory associated with a SODA document cursor.
//-----------------------------------------------------------------------------
static void cxoSodaDocCursor_free(cxoSodaDocCursor *cursor)
{
    if (cursor->handle) {
        dpiSodaDocCursor_release(cursor->handle);
        cursor->handle = NULL;
    }
    Py_CLEAR(cursor->db);
    Py_TYPE(cursor)->tp_free((PyObject*) cursor);
}


//-----------------------------------------------------------------------------
// cxoSodaDocCursor_repr()
//   Return a string representation of a SODA document cursor.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDocCursor_repr(cxoSodaDocCursor *cursor)
{
    PyObject *module, *name, *result;

    if (cxoUtils_getModuleAndName(Py_TYPE(cursor), &module, &name) < 0)
        return NULL;
    result = cxoUtils_formatString("<%s.%s>", PyTuple_Pack(2, module, name));
    Py_DECREF(module);
    Py_DECREF(name);
    return result;
}


//-----------------------------------------------------------------------------
// cxoSodaDocCursor_close()
//   Create a SODA collection and return it.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDocCursor_close(cxoSodaDocCursor *cursor,
        PyObject *args)
{
    if (dpiSodaDocCursor_close(cursor->handle) < 0)
        return cxoError_raiseAndReturnNull();
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoSodaDocCursor_getIter()
//   Return a reference to the cursor which supports the iterator protocol.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDocCursor_getIter(cxoSodaDocCursor *cursor)
{
    Py_INCREF(cursor);
    return (PyObject*) cursor;
}


//-----------------------------------------------------------------------------
// cxoSodaDocCursor_getNext()
//   Return the next document from the cursor.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDocCursor_getNext(cxoSodaDocCursor *cursor)
{
    dpiSodaDoc *handle;
    cxoSodaDoc *doc;
    uint32_t flags;
    int status;

    if (cxoConnection_getSodaFlags(cursor->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaDocCursor_getNext(cursor->handle, flags, &handle);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    if (!handle)
        return NULL;
    doc = cxoSodaDoc_new(cursor->db, handle);
    if (!doc)
        return NULL;
    return (PyObject*) doc;
}

