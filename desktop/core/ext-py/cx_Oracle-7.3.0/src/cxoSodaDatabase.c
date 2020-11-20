//-----------------------------------------------------------------------------
// Copyright (c) 2018, Oracle and/or its affiliates. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoSodaDatabase.c
//   Defines the routines for handling the SODA database.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of functions
//-----------------------------------------------------------------------------
static void cxoSodaDatabase_free(cxoSodaDatabase*);
static PyObject *cxoSodaDatabase_repr(cxoSodaDatabase*);
static PyObject *cxoSodaDatabase_createCollection(cxoSodaDatabase*,
        PyObject*, PyObject*);
static PyObject *cxoSodaDatabase_createDocument(cxoSodaDatabase*,
        PyObject*, PyObject*);
static PyObject *cxoSodaDatabase_getCollectionNames(cxoSodaDatabase*,
        PyObject*, PyObject*);
static PyObject *cxoSodaDatabase_openCollection(cxoSodaDatabase*, PyObject*);


//-----------------------------------------------------------------------------
// declaration of methods for Python type "SodaDatabase"
//-----------------------------------------------------------------------------
static PyMethodDef cxoMethods[] = {
    { "createCollection", (PyCFunction) cxoSodaDatabase_createCollection,
            METH_VARARGS | METH_KEYWORDS },
    { "createDocument", (PyCFunction) cxoSodaDatabase_createDocument,
            METH_VARARGS | METH_KEYWORDS },
    { "getCollectionNames", (PyCFunction) cxoSodaDatabase_getCollectionNames,
            METH_VARARGS | METH_KEYWORDS },
    { "openCollection", (PyCFunction) cxoSodaDatabase_openCollection, METH_O },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeSodaDatabase = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.SodaDatabase",           // tp_name
    sizeof(cxoSodaDatabase),            // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoSodaDatabase_free,  // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoSodaDatabase_repr,    // tp_repr
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
// cxoSodaDatabase_new()
//   Create a new SODA database object.
//-----------------------------------------------------------------------------
cxoSodaDatabase *cxoSodaDatabase_new(cxoConnection *connection)
{
    cxoSodaDatabase *db;
    PyObject *module;

    // load JSON dump/load functions, if needed
    if (!cxoJsonDumpFunction || !cxoJsonLoadFunction) {
        module = PyImport_ImportModule("json");
        if (!module)
            return NULL;
        if (!cxoJsonDumpFunction) {
            cxoJsonDumpFunction = PyObject_GetAttrString(module, "dumps");
            if (!cxoJsonDumpFunction)
                return NULL;
        }
        if (!cxoJsonLoadFunction) {
            cxoJsonLoadFunction = PyObject_GetAttrString(module, "loads");
            if (!cxoJsonLoadFunction)
                return NULL;
        }
    }

    // create SODA database object
    db = (cxoSodaDatabase*)
            cxoPyTypeSodaDatabase.tp_alloc(&cxoPyTypeSodaDatabase, 0);
    if (!db)
        return NULL;
    if (dpiConn_getSodaDb(connection->handle, &db->handle) < 0) {
        Py_DECREF(db);
        cxoError_raiseAndReturnNull();
        return NULL;
    }
    Py_INCREF(connection);
    db->connection = connection;

    return db;
}


//-----------------------------------------------------------------------------
// cxoSodaDatabase_free()
//   Free the memory associated with a SODA database.
//-----------------------------------------------------------------------------
static void cxoSodaDatabase_free(cxoSodaDatabase *db)
{
    if (db->handle) {
        dpiSodaDb_release(db->handle);
        db->handle = NULL;
    }
    Py_CLEAR(db->connection);
    Py_TYPE(db)->tp_free((PyObject*) db);
}


//-----------------------------------------------------------------------------
// cxoSodaDatabase_repr()
//   Return a string representation of a SODA database.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDatabase_repr(cxoSodaDatabase *db)
{
    PyObject *connectionRepr, *module, *name, *result;

    connectionRepr = PyObject_Repr((PyObject*) db->connection);
    if (!connectionRepr)
        return NULL;
    if (cxoUtils_getModuleAndName(Py_TYPE(db), &module, &name) < 0) {
        Py_DECREF(connectionRepr);
        return NULL;
    }
    result = cxoUtils_formatString("<%s.%s on %s>",
            PyTuple_Pack(3, module, name, connectionRepr));
    Py_DECREF(module);
    Py_DECREF(name);
    Py_DECREF(connectionRepr);
    return result;
}


//-----------------------------------------------------------------------------
// cxoSodaDatabase_createCollection()
//   Create a SODA collection and return it.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDatabase_createCollection(cxoSodaDatabase *db,
        PyObject *args, PyObject *keywordArgs)
{
    static char *keywordList[] = { "name", "metadata", "mapMode", NULL };
    PyObject *nameObj, *metadataObj, *mapModeObj;
    cxoBuffer nameBuffer, metadataBuffer;
    cxoSodaCollection *coll;
    const char *encoding;
    dpiSodaColl *handle;
    int status, mapMode;
    uint32_t flags;

    // parse arguments
    nameObj = metadataObj = mapModeObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O|OO", keywordList,
            &nameObj, &metadataObj, &mapModeObj))
        return NULL;
    encoding = db->connection->encodingInfo.encoding;
    if (cxoBuffer_fromObject(&nameBuffer, nameObj, encoding) < 0)
        return NULL;
    if (cxoUtils_processJsonArg(metadataObj, &metadataBuffer) < 0) {
        cxoBuffer_clear(&nameBuffer);
        return NULL;
    }
    if (cxoUtils_getBooleanValue(mapModeObj, 0, &mapMode) < 0) {
        cxoBuffer_clear(&nameBuffer);
        cxoBuffer_clear(&metadataBuffer);
        return NULL;
    }

    // create collection
    if (cxoConnection_getSodaFlags(db->connection, &flags) < 0)
        return NULL;
    if (mapMode)
        flags |= DPI_SODA_FLAGS_CREATE_COLL_MAP;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaDb_createCollection(db->handle, nameBuffer.ptr,
            nameBuffer.size, metadataBuffer.ptr, metadataBuffer.size, flags,
            &handle);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&nameBuffer);
    cxoBuffer_clear(&metadataBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    coll = cxoSodaCollection_new(db, handle);
    if (!coll) {
        dpiSodaColl_release(handle);
        return NULL;
    }

    return (PyObject*) coll;
}


//-----------------------------------------------------------------------------
// cxoSodaDatabase_createDocument()
//   Create a SODA document with the specified key, content and media type.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDatabase_createDocument(cxoSodaDatabase *db,
        PyObject *args, PyObject *keywordArgs)
{
    static char *keywordList[] = { "content", "key", "mediaType", NULL };
    cxoBuffer contentBuffer, keyBuffer, mediaTypeBuffer;
    PyObject *contentObj, *keyObj, *mediaTypeObj;
    const char *encoding;
    dpiSodaDoc *doc;
    int status;

    // parse arguments
    keyObj = mediaTypeObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O|OO", keywordList,
            &contentObj, &keyObj, &mediaTypeObj))
        return NULL;

    // content must be converted to string if it is a dictionary
    if (PyDict_Check(contentObj)) {
        contentObj = PyObject_CallFunctionObjArgs(cxoJsonDumpFunction,
                contentObj, NULL);
        if (!contentObj)
            return NULL;
    }

    // get buffers for each of the content, key and media type parameters
    if (cxoUtils_processJsonArg(contentObj, &contentBuffer) < 0)
        return NULL;
    encoding = db->connection->encodingInfo.encoding;
    if (cxoBuffer_fromObject(&keyBuffer, keyObj, encoding) < 0) {
        cxoBuffer_clear(&contentBuffer);
        return NULL;
    }
    if (cxoBuffer_fromObject(&mediaTypeBuffer, mediaTypeObj, encoding) < 0) {
        cxoBuffer_clear(&contentBuffer);
        cxoBuffer_clear(&keyBuffer);
        return NULL;
    }

    // create SODA document
    status = dpiSodaDb_createDocument(db->handle, keyBuffer.ptr,
            keyBuffer.size, contentBuffer.ptr, contentBuffer.size,
            mediaTypeBuffer.ptr, mediaTypeBuffer.size, DPI_SODA_FLAGS_DEFAULT,
            &doc);
    cxoBuffer_clear(&contentBuffer);
    cxoBuffer_clear(&keyBuffer);
    cxoBuffer_clear(&mediaTypeBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    return (PyObject*) cxoSodaDoc_new(db, doc);
}


//-----------------------------------------------------------------------------
// cxoSodaDatabase_getCollectionNames()
//   Return a list of the names of the collections found in the database.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDatabase_getCollectionNames(cxoSodaDatabase *db,
        PyObject *args, PyObject *keywordArgs)
{
    static char *keywordList[] = { "startName", "limit", NULL };
    PyObject *startName, *result, *temp;
    dpiSodaCollNames collNames;
    cxoBuffer startNameBuffer;
    uint32_t limit, i, flags;
    const char *encoding;
    int status;

    // parse arguments
    limit = 0;
    startName = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|Oi", keywordList,
            &startName, &limit))
        return NULL;

    // get collection names from the database
    encoding = db->connection->encodingInfo.encoding;
    if (cxoBuffer_fromObject(&startNameBuffer, startName, encoding) < 0)
        return NULL;
    if (cxoConnection_getSodaFlags(db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaDb_getCollectionNames(db->handle,
            (const char*) startNameBuffer.ptr, startNameBuffer.size, limit,
            flags, &collNames);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&startNameBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    // transform results into a Python list
    result = PyList_New(collNames.numNames);
    if (!result)
        return NULL;
    for (i = 0; i < collNames.numNames; i++) {
        temp = cxoPyString_fromEncodedString(collNames.names[i],
                collNames.nameLengths[i], encoding, NULL);
        if (!temp) {
            Py_DECREF(result);
            return NULL;
        }
        PyList_SET_ITEM(result, i, temp);
    }
    if (dpiSodaDb_freeCollectionNames(db->handle, &collNames) < 0) {
        Py_DECREF(result);
        return cxoError_raiseAndReturnNull();
    }

    return result;
}


//-----------------------------------------------------------------------------
// cxoSodaDatabase_openCollection()
//   Open a SODA collection and return it.
//-----------------------------------------------------------------------------
static PyObject *cxoSodaDatabase_openCollection(cxoSodaDatabase *db,
        PyObject *nameObj)
{
    cxoSodaCollection *coll;
    cxoBuffer nameBuffer;
    dpiSodaColl *handle;
    uint32_t flags;
    int status;

    // open collection
    if (cxoBuffer_fromObject(&nameBuffer, nameObj,
            db->connection->encodingInfo.encoding) < 0)
        return NULL;
    if (cxoConnection_getSodaFlags(db->connection, &flags) < 0)
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = dpiSodaDb_openCollection(db->handle, nameBuffer.ptr,
            nameBuffer.size, flags, &handle);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&nameBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    if (!handle)
        Py_RETURN_NONE;
    coll = cxoSodaCollection_new(db, handle);
    if (!coll) {
        dpiSodaColl_release(handle);
        return NULL;
    }

    return (PyObject*) coll;
}

