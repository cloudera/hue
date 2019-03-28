//-----------------------------------------------------------------------------
// Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoSodaOperation.c
//   Defines the routines for the various operations performed on SODA
// collections.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of functions
//-----------------------------------------------------------------------------
static void cxoSodaOperation_free(cxoSodaOperation*);
static PyObject *cxoSodaOperation_repr(cxoSodaOperation*);
static PyObject *cxoSodaOperation_filter(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_key(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_keys(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_limit(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_skip(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_version(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_count(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_getCursor(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_getDocuments(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_getOne(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_remove(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_replaceOne(cxoSodaOperation*, PyObject*);
static PyObject *cxoSodaOperation_replaceOneAndGet(cxoSodaOperation*,
        PyObject*);


//-----------------------------------------------------------------------------
// declaration of methods for Python type "SodaOperation"
//-----------------------------------------------------------------------------
static PyMethodDef cxoMethods[] = {
    { "filter", (PyCFunction) cxoSodaOperation_filter, METH_O },
    { "key", (PyCFunction) cxoSodaOperation_key, METH_O },
    { "keys", (PyCFunction) cxoSodaOperation_keys, METH_O },
    { "limit", (PyCFunction) cxoSodaOperation_limit, METH_O },
    { "skip", (PyCFunction) cxoSodaOperation_skip, METH_O },
    { "version", (PyCFunction) cxoSodaOperation_version, METH_O },
    { "count", (PyCFunction) cxoSodaOperation_count, METH_NOARGS },
    { "getCursor", (PyCFunction) cxoSodaOperation_getCursor, METH_NOARGS },
    { "getDocuments", (PyCFunction) cxoSodaOperation_getDocuments,
            METH_NOARGS },
    { "getOne", (PyCFunction) cxoSodaOperation_getOne, METH_NOARGS },
    { "remove", (PyCFunction) cxoSodaOperation_remove, METH_NOARGS },
    { "replaceOne", (PyCFunction) cxoSodaOperation_replaceOne, METH_O },
    { "replaceOneAndGet", (PyCFunction) cxoSodaOperation_replaceOneAndGet,
            METH_O },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeSodaOperation = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.SodaOperation",          // tp_name
    sizeof(cxoSodaOperation),           // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoSodaOperation_free, // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoSodaOperation_repr,   // tp_repr
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
// cxoSodaOperation_clearKeys()
//   Clear the keys set on the operation object, if applicable.
//-----------------------------------------------------------------------------
void cxoSodaOperation_clearKeys(cxoSodaOperation *op)
{
    uint32_t i;

    if (op->keyBuffers) {
        for (i = 0; i < op->numKeyBuffers; i++)
            cxoBuffer_clear(&op->keyBuffers[i]);
        PyMem_Free(op->keyBuffers);
        op->keyBuffers = NULL;
    }
    op->numKeyBuffers = 0;
    op->options.numKeys = 0;
    if (op->options.keys) {
        PyMem_Free(op->options.keys);
        op->options.keys = NULL;
    }
    if (op->options.keyLengths) {
        PyMem_Free(op->options.keyLengths);
        op->options.keyLengths = NULL;
    }
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_new()
//   Create a new SODA operation object.
//-----------------------------------------------------------------------------
cxoSodaOperation *cxoSodaOperation_new(cxoSodaCollection *coll)
{
    cxoSodaOperation *op;

    op = (cxoSodaOperation*)
            cxoPyTypeSodaOperation.tp_alloc(&cxoPyTypeSodaOperation, 0);
    if (!op)
        return NULL;
    if (dpiContext_initSodaOperOptions(cxoDpiContext, &op->options) < 0) {
        Py_DECREF(op);
        return NULL;
    }
    cxoBuffer_init(&op->keyBuffer);
    cxoBuffer_init(&op->versionBuffer);
    cxoBuffer_init(&op->filterBuffer);
    Py_INCREF(coll);
    op->coll = coll;

    return op;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_free()
//   Free the memory associated with a SODA operation object.
//-----------------------------------------------------------------------------
static void cxoSodaOperation_free(cxoSodaOperation *op)
{
    cxoSodaOperation_clearKeys(op);
    cxoBuffer_clear(&op->keyBuffer);
    cxoBuffer_clear(&op->versionBuffer);
    cxoBuffer_clear(&op->filterBuffer);
    Py_CLEAR(op->coll);
    Py_TYPE(op)->tp_free((PyObject*) op);
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_repr()
//   Return a string representation of a SODA operation object.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_repr(cxoSodaOperation *op)
{
    PyObject *collRepr, *module, *name, *result;

    collRepr = PyObject_Repr((PyObject*) op->coll);
    if (!collRepr)
        return NULL;
    if (cxoUtils_getModuleAndName(Py_TYPE(op), &module, &name) < 0) {
        Py_DECREF(collRepr);
        return NULL;
    }
    result = cxoUtils_formatString("<%s.%s on %s>",
            PyTuple_Pack(3, module, name, collRepr));
    Py_DECREF(module);
    Py_DECREF(name);
    Py_DECREF(collRepr);
    return result;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_filter()
//   Set the filter to be used for the operation.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_filter(cxoSodaOperation *op,
        PyObject *filterObj)
{
    cxoBuffer_clear(&op->filterBuffer);
    if (PyDict_Check(filterObj)) {
        filterObj = PyObject_CallFunctionObjArgs(cxoJsonDumpFunction,
                filterObj, NULL);
        if (!filterObj)
            return NULL;
    }
    if (cxoBuffer_fromObject(&op->filterBuffer, filterObj,
            op->coll->db->connection->encodingInfo.encoding) < 0)
        return NULL;
    op->options.filter = op->filterBuffer.ptr;
    op->options.filterLength = op->filterBuffer.size;
    Py_INCREF(op);
    return (PyObject*) op;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_key()
//   Set the key to be used for the operation.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_key(cxoSodaOperation *op,
        PyObject *keyObj)
{
    cxoBuffer_clear(&op->keyBuffer);
    if (cxoBuffer_fromObject(&op->keyBuffer, keyObj,
            op->coll->db->connection->encodingInfo.encoding) < 0)
        return NULL;
    op->options.key = op->keyBuffer.ptr;
    op->options.keyLength = op->keyBuffer.size;
    Py_INCREF(op);
    return (PyObject*) op;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_keys()
//   Set the keys to be used for the operation.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_keys(cxoSodaOperation *op,
        PyObject *keysObj)
{
    Py_ssize_t size, i;
    PyObject *element;

    // determine size of sequence passed to method
    size = PySequence_Size(keysObj);
    if (PyErr_Occurred())
        return NULL;

    // clear original keys, if applicable
    cxoSodaOperation_clearKeys(op);

    // zero-length arrays don't need any further processing
    if (size == 0) {
        Py_INCREF(op);
        return (PyObject*) op;
    }

    // initialize memory
    op->keyBuffers = PyMem_Malloc(size * sizeof(cxoBuffer));
    if (!op->keyBuffers)
        return NULL;
    op->numKeyBuffers = (uint32_t) size;
    for (i = 0; i < size; i++)
        cxoBuffer_init(&op->keyBuffers[i]);
    op->options.keys = PyMem_Malloc(size * sizeof(const char *));
    op->options.keyLengths = PyMem_Malloc(size * sizeof(uint32_t));
    if (!op->options.keys || !op->options.keyLengths) {
        cxoSodaOperation_clearKeys(op);
        return NULL;
    }
    op->options.numKeys = op->numKeyBuffers;

    // process each of the elements of the sequence
    for (i = 0; i < size; i++) {
        element = PySequence_GetItem(keysObj, i);
        if (!element) {
            cxoSodaOperation_clearKeys(op);
            return NULL;
        }
        if (cxoBuffer_fromObject(&op->keyBuffers[i], element,
                op->coll->db->connection->encodingInfo.encoding) < 0) {
            Py_DECREF(element);
            cxoSodaOperation_clearKeys(op);
            return NULL;
        }
        Py_DECREF(element);
        op->options.keys[i] = op->keyBuffers[i].ptr;
        op->options.keyLengths[i] = op->keyBuffers[i].size;
    }

    Py_INCREF(op);
    return (PyObject*) op;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_limit()
//   Set the limit value to be used for the operation.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_limit(cxoSodaOperation *op,
        PyObject *limitObj)
{
    op->options.limit = PyLong_AsUnsignedLong(limitObj);
    if (PyErr_Occurred())
        return NULL;
    Py_INCREF(op);
    return (PyObject*) op;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_skip()
//   Set the skip value to be used for the operation.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_skip(cxoSodaOperation *op,
        PyObject *skipObj)
{
    op->options.skip = PyLong_AsUnsignedLong(skipObj);
    if (PyErr_Occurred())
        return NULL;
    Py_INCREF(op);
    return (PyObject*) op;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_version()
//   Set the version to be used for the operation.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_version(cxoSodaOperation *op,
        PyObject *versionObj)
{
    cxoBuffer_clear(&op->versionBuffer);
    if (cxoBuffer_fromObject(&op->versionBuffer, versionObj,
            op->coll->db->connection->encodingInfo.encoding) < 0)
        return NULL;
    op->options.version = op->versionBuffer.ptr;
    op->options.versionLength = op->versionBuffer.size;
    Py_INCREF(op);
    return (PyObject*) op;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_count()
//   Returns the number of documents that match the criteria.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_count(cxoSodaOperation *op, PyObject *args)
{
    uint64_t count;
    uint32_t flags;
    int status;

    if (cxoConnection_getSodaFlags(op->coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_getDocCount(op->coll->handle, &op->options, flags,
            &count);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    return PyLong_FromUnsignedLongLong(count);
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_getCursor()
//   Returns a document cursor which can be used to iterate over the documents
// that match the criteria.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_getCursor(cxoSodaOperation *op,
        PyObject *args)
{
    dpiSodaDocCursor *handle;
    cxoSodaDocCursor *cursor;
    uint32_t flags;
    int status;

    if (cxoConnection_getSodaFlags(op->coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_find(op->coll->handle, &op->options, flags, &handle);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    cursor = cxoSodaDocCursor_new(op->coll->db, handle);
    if (!cursor)
        return NULL;
    return (PyObject*) cursor;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_getDocuments()
//   Returns a list of documents that match the criteria.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_getDocuments(cxoSodaOperation *op,
        PyObject *args)
{
    dpiSodaDocCursor *cursor;
    PyObject *docObj;
    dpiSodaDoc *doc;
    PyObject *list;
    uint32_t flags;
    int status;

    // acquire cursor
    if (cxoConnection_getSodaFlags(op->coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_find(op->coll->handle, &op->options, flags, &cursor);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    // iterate cursor and create array of documents
    list = PyList_New(0);
    if (!list) {
        dpiSodaDocCursor_release(cursor);
        return NULL;
    }
    while (1) {
        Py_BEGIN_ALLOW_THREADS
        status = dpiSodaDocCursor_getNext(cursor, flags, &doc);
        Py_END_ALLOW_THREADS
        if (status < 0) {
            cxoError_raiseAndReturnNull();
            dpiSodaDocCursor_release(cursor);
            return NULL;
        }
        if (!doc)
            break;
        docObj = (PyObject*) cxoSodaDoc_new(op->coll->db, doc);
        if (!docObj) {
            dpiSodaDocCursor_release(cursor);
            return NULL;
        }
        if (PyList_Append(list, docObj) < 0) {
            Py_DECREF(docObj);
            dpiSodaDocCursor_release(cursor);
            return NULL;
        }
        Py_DECREF(docObj);
    }
    dpiSodaDocCursor_release(cursor);

    return list;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_getOne()
//   Returns a single document that matches the criteria or None if no
// documents match the criteria.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_getOne(cxoSodaOperation *op, PyObject *args)
{
    dpiSodaDoc *handle;
    uint32_t flags;
    int status;

    if (cxoConnection_getSodaFlags(op->coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_findOne(op->coll->handle, &op->options, flags,
            &handle);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    if (handle)
        return (PyObject*) cxoSodaDoc_new(op->coll->db, handle);
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_remove()
//   Remove all of the documents that match the criteria.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_remove(cxoSodaOperation *op, PyObject *args)
{
    uint64_t count;
    uint32_t flags;
    int status;

    if (cxoConnection_getSodaFlags(op->coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_remove(op->coll->handle, &op->options, flags, &count);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    return PyLong_FromUnsignedLongLong(count);
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_replaceOne()
//   Replace a single document in the collection with the provided replacement.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_replaceOne(cxoSodaOperation *op,
        PyObject *arg)
{
    int status, replaced;
    cxoSodaDoc *doc;
    uint32_t flags;

    if (cxoConnection_getSodaFlags(op->coll->db->connection, &flags) < 0)
        return NULL;
    if (cxoUtils_processSodaDocArg(op->coll->db, arg, &doc) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_replaceOne(op->coll->handle, &op->options,
            doc->handle, flags, &replaced, NULL);
    Py_END_ALLOW_THREADS
    if (status < 0) {
        cxoError_raiseAndReturnNull();
        Py_DECREF(doc);
        return NULL;
    }
    Py_DECREF(doc);
    if (replaced)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


//-----------------------------------------------------------------------------
// cxoSodaOperation_replaceOneAndGet()
//   Replace a single document in the collection with the provided replacement
// and return a document (without the content) to the caller.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaOperation_replaceOneAndGet(cxoSodaOperation *op,
        PyObject *arg)
{
    dpiSodaDoc *replacedDoc;
    cxoSodaDoc *doc;
    uint32_t flags;
    int status;

    if (cxoConnection_getSodaFlags(op->coll->db->connection, &flags) < 0)
        return NULL;
    if (cxoUtils_processSodaDocArg(op->coll->db, arg, &doc) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_replaceOne(op->coll->handle, &op->options,
            doc->handle, flags, NULL, &replacedDoc);
    Py_END_ALLOW_THREADS
    if (status < 0) {
        cxoError_raiseAndReturnNull();
        Py_DECREF(doc);
        return NULL;
    }
    Py_DECREF(doc);
    if (replacedDoc)
        return (PyObject*) cxoSodaDoc_new(op->coll->db, replacedDoc);
    Py_RETURN_NONE;
}

