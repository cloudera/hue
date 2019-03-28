//-----------------------------------------------------------------------------
// Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoSodaCollection.c
//   Defines the routines for handling the SODA collection.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// declaration of functions
//-----------------------------------------------------------------------------
static void cxoSodaCollection_free(cxoSodaCollection*);
static PyObject *cxoSodaCollection_repr(cxoSodaCollection*);
static PyObject *cxoSodaCollection_createIndex(cxoSodaCollection*, PyObject*);
static PyObject *cxoSodaCollection_drop(cxoSodaCollection*, PyObject*);
static PyObject *cxoSodaCollection_dropIndex(cxoSodaCollection*, PyObject*,
        PyObject*);
static PyObject *cxoSodaCollection_find(cxoSodaCollection*, PyObject*);
static PyObject *cxoSodaCollection_getDataGuide(cxoSodaCollection*, PyObject*);
static PyObject *cxoSodaCollection_insertOne(cxoSodaCollection*, PyObject*);
static PyObject *cxoSodaCollection_insertOneAndGet(cxoSodaCollection*,
        PyObject*);
static PyObject *cxoSodaCollection_getMetadata(cxoSodaCollection*, PyObject*);


//-----------------------------------------------------------------------------
// declaration of methods
//-----------------------------------------------------------------------------
static PyMethodDef cxoMethods[] = {
    { "createIndex", (PyCFunction) cxoSodaCollection_createIndex, METH_O },
    { "drop", (PyCFunction) cxoSodaCollection_drop, METH_NOARGS },
    { "dropIndex", (PyCFunction) cxoSodaCollection_dropIndex,
            METH_VARARGS | METH_KEYWORDS },
    { "find", (PyCFunction) cxoSodaCollection_find, METH_NOARGS },
    { "getDataGuide", (PyCFunction) cxoSodaCollection_getDataGuide,
            METH_NOARGS },
    { "insertOne", (PyCFunction) cxoSodaCollection_insertOne, METH_O },
    { "insertOneAndGet", (PyCFunction) cxoSodaCollection_insertOneAndGet,
            METH_O },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of members
//-----------------------------------------------------------------------------
static PyMemberDef cxoMembers[] = {
    { "name", T_OBJECT, offsetof(cxoSodaCollection, name), READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of calculated members
//-----------------------------------------------------------------------------
static PyGetSetDef cxoCalcMembers[] = {
    { "metadata", (getter) cxoSodaCollection_getMetadata, 0, 0, 0 },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeSodaCollection = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.SodaCollection",         // tp_name
    sizeof(cxoSodaCollection),          // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoSodaCollection_free,// tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoSodaCollection_repr,  // tp_repr
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
    cxoMembers,                         // tp_members
    cxoCalcMembers,                     // tp_getset
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
// cxoSodaCollection_initialize()
//   Initialize a new collection with its attributes.
//-----------------------------------------------------------------------------
static int cxoSodaCollection_initialize(cxoSodaCollection *coll,
        cxoSodaDatabase *db, const char *encoding, dpiSodaColl *handle)
{
    uint32_t nameLength;
    const char *name;

    // get name from ODPI-C
    if (dpiSodaColl_getName(handle, &name, &nameLength) < 0)
        return cxoError_raiseAndReturnInt();
    coll->name = cxoPyString_fromEncodedString(name, nameLength, encoding,
            NULL);
    if (!coll->name)
        return -1;

    // set base attributes (handle should not be added until there is no
    // possibility of further failure)
    coll->handle = handle;
    Py_INCREF(db);
    coll->db = db;

    return 0;
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_new()
//   Create a new SODA collection object.
//-----------------------------------------------------------------------------
cxoSodaCollection *cxoSodaCollection_new(cxoSodaDatabase *db,
        dpiSodaColl *handle)
{
    cxoSodaCollection *coll;

    coll = (cxoSodaCollection*)
            cxoPyTypeSodaCollection.tp_alloc(&cxoPyTypeSodaCollection, 0);
    if (!coll)
        return NULL;
    if (cxoSodaCollection_initialize(coll, db,
            db->connection->encodingInfo.encoding, handle) < 0) {
        Py_DECREF(coll);
        return NULL;
    }

    return coll;
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_free()
//   Free the memory associated with a SODA collection.
//-----------------------------------------------------------------------------
static void cxoSodaCollection_free(cxoSodaCollection *coll)
{
    if (coll->handle) {
        dpiSodaColl_release(coll->handle);
        coll->handle = NULL;
    }
    Py_CLEAR(coll->db);
    Py_CLEAR(coll->name);
    Py_TYPE(coll)->tp_free((PyObject*) coll);
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_repr()
//   Return a string representation of a SODA collection.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_repr(cxoSodaCollection *coll)
{
    PyObject *module, *name, *result;

    if (cxoUtils_getModuleAndName(Py_TYPE(coll), &module, &name) < 0)
        return NULL;
    result = cxoUtils_formatString("<%s.%s %s>",
            PyTuple_Pack(3, module, name, coll->name));
    Py_DECREF(module);
    Py_DECREF(name);
    return result;
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_createIndex()
//   Create an index on a SODA collection.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_createIndex(cxoSodaCollection *coll,
        PyObject *specObj)
{
    cxoBuffer specBuffer;
    uint32_t flags;
    int status;

    if (cxoUtils_processJsonArg(specObj, &specBuffer) < 0)
        return NULL;
    if (cxoConnection_getSodaFlags(coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_createIndex(coll->handle, specBuffer.ptr,
            specBuffer.size, flags);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&specBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_drop()
//   Create a SODA collection and return it.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_drop(cxoSodaCollection *coll,
        PyObject *args)
{
    uint32_t flags;
    int isDropped;

    if (cxoConnection_getSodaFlags(coll->db->connection, &flags) < 0)
        return NULL;
    if (dpiSodaColl_drop(coll->handle, flags, &isDropped) < 0)
        return cxoError_raiseAndReturnNull();
    if (isDropped)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_dropIndex()
//   Drop an index on a SODA collection.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_dropIndex(cxoSodaCollection *coll,
        PyObject *args, PyObject *keywordArgs)
{
    static char *keywordList[] = { "name", "force", NULL };
    int status, isDropped, force;
    PyObject *nameObj, *forceObj;
    cxoBuffer nameBuffer;
    uint32_t flags;

    // parse arguments
    forceObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O|O", keywordList,
            &nameObj, &forceObj))
        return NULL;
    if (cxoUtils_getBooleanValue(forceObj, 0, &force) < 0)
        return NULL;

    // drop index
    if (cxoConnection_getSodaFlags(coll->db->connection, &flags) < 0)
        return NULL;
    if (force)
        flags |= DPI_SODA_FLAGS_INDEX_DROP_FORCE;
    if (cxoBuffer_fromObject(&nameBuffer, nameObj,
            coll->db->connection->encodingInfo.encoding) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_dropIndex(coll->handle, nameBuffer.ptr,
            nameBuffer.size, flags, &isDropped);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&nameBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    if (isDropped)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_find()
//   Creates an operation options object which can be used to perform a number
// of operations on the collection using the criteria set on the object.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_find(cxoSodaCollection *coll,
        PyObject *args)
{
    return (PyObject*) cxoSodaOperation_new(coll);
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_getDataGuide()
//   Return the data guide associated with the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_getDataGuide(cxoSodaCollection *coll,
        PyObject *args)
{
    dpiSodaDoc *handle;
    cxoSodaDoc *doc;
    uint32_t flags;
    int status;

    if (cxoConnection_getSodaFlags(coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_getDataGuide(coll->handle, flags, &handle);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    if (handle) {
        doc = cxoSodaDoc_new(coll->db, handle);
        if (!doc)
            return NULL;
        return (PyObject*) doc;
    }
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_insertOne()
//   Insert a single document into the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_insertOne(cxoSodaCollection *coll,
        PyObject *arg)
{
    cxoSodaDoc *doc;
    uint32_t flags;
    int status;

    if (cxoUtils_processSodaDocArg(coll->db, arg, &doc) < 0)
        return NULL;
    if (cxoConnection_getSodaFlags(coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_insertOne(coll->handle, doc->handle, flags, NULL);
    Py_END_ALLOW_THREADS
    if (status < 0) {
        cxoError_raiseAndReturnNull();
        Py_DECREF(doc);
        return NULL;
    }
    Py_DECREF(doc);
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_insertOneAndGet()
//   Insert a single document into the collection and return a document
// containing all but the content itself.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_insertOneAndGet(cxoSodaCollection *coll,
        PyObject *arg)
{
    dpiSodaDoc *returnedDoc;
    cxoSodaDoc *doc;
    uint32_t flags;
    int status;

    if (cxoUtils_processSodaDocArg(coll->db, arg, &doc) < 0)
        return NULL;
    if (cxoConnection_getSodaFlags(coll->db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaColl_insertOne(coll->handle, doc->handle, flags,
            &returnedDoc);
    Py_END_ALLOW_THREADS
    if (status < 0) {
        cxoError_raiseAndReturnNull();
        Py_DECREF(doc);
        return NULL;
    }
    Py_DECREF(doc);
    return (PyObject*) cxoSodaDoc_new(coll->db, returnedDoc);
}


//-----------------------------------------------------------------------------
// cxoSodaCollection_getMetadata()
//   Retrieve the metadata for the collection.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaCollection_getMetadata(cxoSodaCollection *coll,
        PyObject *unused)
{
    PyObject *str, *result;
    uint32_t valueLength;
    const char *value;

    if (dpiSodaColl_getMetadata(coll->handle, &value, &valueLength) < 0)
        return cxoError_raiseAndReturnNull();
    str = PyUnicode_Decode(value, valueLength,
            coll->db->connection->encodingInfo.encoding, NULL);
    if (!str)
        return NULL;
    result = PyObject_CallFunctionObjArgs(cxoJsonLoadFunction, str, NULL);
    Py_DECREF(str);
    return result;
}

