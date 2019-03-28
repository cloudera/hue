//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoSessionPool.c
//   Handles session pooling.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// functions for the Python type "SessionPool"
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_new(PyTypeObject*, PyObject*, PyObject*);
static int cxoSessionPool_init(cxoSessionPool*, PyObject*, PyObject*);
static void cxoSessionPool_free(cxoSessionPool*);
static PyObject *cxoSessionPool_acquire(cxoSessionPool*, PyObject*, PyObject*);
static PyObject *cxoSessionPool_close(cxoSessionPool*, PyObject*, PyObject*);
static PyObject *cxoSessionPool_drop(cxoSessionPool*, PyObject*);
static PyObject *cxoSessionPool_release(cxoSessionPool*, PyObject*, PyObject*);
static PyObject *cxoSessionPool_getBusyCount(cxoSessionPool*, void*);
static PyObject *cxoSessionPool_getGetMode(cxoSessionPool*, void*);
static PyObject *cxoSessionPool_getMaxLifetimeSession(cxoSessionPool*, void*);
static PyObject *cxoSessionPool_getOpenCount(cxoSessionPool*, void*);
static PyObject *cxoSessionPool_getStmtCacheSize(cxoSessionPool*, void*);
static PyObject *cxoSessionPool_getTimeout(cxoSessionPool*, void*);
static PyObject *cxoSessionPool_getWaitTimeout(cxoSessionPool*, void*);
static int cxoSessionPool_setGetMode(cxoSessionPool*, PyObject*, void*);
static int cxoSessionPool_setMaxLifetimeSession(cxoSessionPool*, PyObject*,
        void*);
static int cxoSessionPool_setStmtCacheSize(cxoSessionPool*, PyObject*, void*);
static int cxoSessionPool_setTimeout(cxoSessionPool*, PyObject*, void*);
static int cxoSessionPool_setWaitTimeout(cxoSessionPool*, PyObject*, void*);


//-----------------------------------------------------------------------------
// declaration of methods for Python type "SessionPool"
//-----------------------------------------------------------------------------
static PyMethodDef cxoSessionPoolMethods[] = {
    { "acquire", (PyCFunction) cxoSessionPool_acquire,
            METH_VARARGS | METH_KEYWORDS },
    { "close", (PyCFunction) cxoSessionPool_close,
            METH_VARARGS | METH_KEYWORDS },
    { "drop", (PyCFunction) cxoSessionPool_drop, METH_VARARGS },
    { "release", (PyCFunction) cxoSessionPool_release,
            METH_VARARGS | METH_KEYWORDS },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of members for Python type "SessionPool"
//-----------------------------------------------------------------------------
static PyMemberDef cxoSessionPoolMembers[] = {
    { "username", T_OBJECT, offsetof(cxoSessionPool, username), READONLY },
    { "dsn", T_OBJECT, offsetof(cxoSessionPool, dsn), READONLY },
    { "tnsentry", T_OBJECT, offsetof(cxoSessionPool, dsn), READONLY },
    { "name", T_OBJECT, offsetof(cxoSessionPool, name), READONLY },
    { "max", T_INT, offsetof(cxoSessionPool, maxSessions), READONLY },
    { "min", T_INT, offsetof(cxoSessionPool, minSessions), READONLY },
    { "increment", T_INT, offsetof(cxoSessionPool, sessionIncrement),
            READONLY },
    { "homogeneous", T_INT, offsetof(cxoSessionPool, homogeneous), READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of calculated members for Python type "SessionPool"
//-----------------------------------------------------------------------------
static PyGetSetDef cxoSessionPoolCalcMembers[] = {
    { "opened", (getter) cxoSessionPool_getOpenCount, 0, 0, 0 },
    { "busy", (getter) cxoSessionPool_getBusyCount, 0, 0, 0 },
    { "timeout", (getter) cxoSessionPool_getTimeout,
            (setter) cxoSessionPool_setTimeout, 0, 0 },
    { "getmode", (getter) cxoSessionPool_getGetMode,
            (setter) cxoSessionPool_setGetMode, 0, 0 },
    { "max_lifetime_session", (getter) cxoSessionPool_getMaxLifetimeSession,
            (setter) cxoSessionPool_setMaxLifetimeSession, 0, 0 },
    { "stmtcachesize", (getter) cxoSessionPool_getStmtCacheSize,
            (setter) cxoSessionPool_setStmtCacheSize, 0, 0 },
    { "wait_timeout", (getter) cxoSessionPool_getWaitTimeout,
            (setter) cxoSessionPool_setWaitTimeout, 0, 0 },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of Python type "SessionPool"
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeSessionPool = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.SessionPool",            // tp_name
    sizeof(cxoSessionPool),             // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoSessionPool_free,   // tp_dealloc
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
                                        // tp_flags
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    cxoSessionPoolMethods,              // tp_methods
    cxoSessionPoolMembers,              // tp_members
    cxoSessionPoolCalcMembers,          // tp_getset
    0,                                  // tp_base
    0,                                  // tp_dict
    0,                                  // tp_descr_get
    0,                                  // tp_descr_set
    0,                                  // tp_dictoffset
    (initproc) cxoSessionPool_init,        // tp_init
    0,                                  // tp_alloc
    (newfunc) cxoSessionPool_new,          // tp_new
    0,                                  // tp_free
    0,                                  // tp_is_gc
    0                                   // tp_bases
};


//-----------------------------------------------------------------------------
// cxoSessionPool_new()
//   Create a new session pool object.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_new(PyTypeObject *type, PyObject *args,
        PyObject *keywordArgs)
{
    return type->tp_alloc(type, 0);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_init()
//   Initialize the session pool object.
//-----------------------------------------------------------------------------
static int cxoSessionPool_init(cxoSessionPool *pool, PyObject *args,
        PyObject *keywordArgs)
{
    cxoBuffer userNameBuffer, passwordBuffer, dsnBuffer, editionBuffer;
    PyObject *threadedObj, *eventsObj, *homogeneousObj, *passwordObj;
    PyObject *usernameObj, *dsnObj, *sessionCallbackObj;
    uint32_t minSessions, maxSessions, sessionIncrement;
    PyObject *externalAuthObj, *editionObj;
    dpiCommonCreateParams dpiCommonParams;
    dpiPoolCreateParams dpiCreateParams;
    cxoBuffer sessionCallbackBuffer;
    PyTypeObject *connectionType;
    const char *encoding;
    int status, temp;

    // define keyword arguments
    static char *keywordList[] = { "user", "password", "dsn", "min", "max",
            "increment", "connectiontype", "threaded", "getmode", "events",
            "homogeneous", "externalauth", "encoding", "nencoding", "edition",
            "timeout", "waitTimeout", "maxLifetimeSession", "sessionCallback",
            NULL };

    // parse arguments and keywords
    usernameObj = passwordObj = dsnObj = editionObj = Py_None;
    externalAuthObj = sessionCallbackObj = NULL;
    threadedObj = eventsObj = homogeneousObj = passwordObj = NULL;
    connectionType = &cxoPyTypeConnection;
    minSessions = 1;
    maxSessions = 2;
    sessionIncrement = 1;
    if (cxoUtils_initializeDPI() < 0)
        return -1;
    if (dpiContext_initCommonCreateParams(cxoDpiContext, &dpiCommonParams) < 0)
        return cxoError_raiseAndReturnInt();
    dpiCommonParams.driverName = CXO_DRIVER_NAME;
    dpiCommonParams.driverNameLength =
            (uint32_t) strlen(dpiCommonParams.driverName);
    if (dpiContext_initPoolCreateParams(cxoDpiContext, &dpiCreateParams) < 0)
        return cxoError_raiseAndReturnInt();
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|OOOiiiOObOOOssOiiiO",
            keywordList, &usernameObj, &passwordObj, &dsnObj, &minSessions,
            &maxSessions, &sessionIncrement, &connectionType, &threadedObj,
            &dpiCreateParams.getMode, &eventsObj, &homogeneousObj,
            &externalAuthObj, &dpiCommonParams.encoding,
            &dpiCommonParams.nencoding, &editionObj, &dpiCreateParams.timeout,
            &dpiCreateParams.waitTimeout, &dpiCreateParams.maxLifetimeSession,
            &sessionCallbackObj))
        return -1;
    if (!PyType_Check(connectionType)) {
        cxoError_raiseFromString(cxoProgrammingErrorException,
                "connectiontype must be a type");
        return -1;
    }
    if (!PyType_IsSubtype(connectionType, &cxoPyTypeConnection)) {
        cxoError_raiseFromString(cxoProgrammingErrorException,
                "connectiontype must be a subclass of Connection");
        return -1;
    }
    if (cxoUtils_getBooleanValue(threadedObj, 0, &temp) < 0)
        return -1;
    if (temp)
        dpiCommonParams.createMode |= DPI_MODE_CREATE_THREADED;
    if (cxoUtils_getBooleanValue(eventsObj, 0, &temp) < 0)
        return -1;
    if (temp)
        dpiCommonParams.createMode |= DPI_MODE_CREATE_EVENTS;
    if (cxoUtils_getBooleanValue(externalAuthObj, 0,
            &dpiCreateParams.externalAuth) < 0)
        return -1;
    if (cxoUtils_getBooleanValue(homogeneousObj, 1,
            &dpiCreateParams.homogeneous) < 0)
        return -1;

    // initialize the object's members
    Py_INCREF(connectionType);
    pool->connectionType = connectionType;
    Py_INCREF(dsnObj);
    pool->dsn = dsnObj;
    Py_INCREF(usernameObj);
    pool->username = usernameObj;
    pool->minSessions = minSessions;
    pool->maxSessions = maxSessions;
    pool->sessionIncrement = sessionIncrement;
    pool->homogeneous = dpiCreateParams.homogeneous;
    pool->externalAuth = dpiCreateParams.externalAuth;
    Py_XINCREF(sessionCallbackObj);
    pool->sessionCallback = sessionCallbackObj;

    // populate parameters
    encoding = cxoUtils_getAdjustedEncoding(dpiCommonParams.encoding);
    cxoBuffer_init(&userNameBuffer);
    cxoBuffer_init(&passwordBuffer);
    cxoBuffer_init(&dsnBuffer);
    cxoBuffer_init(&editionBuffer);
    cxoBuffer_init(&sessionCallbackBuffer);
    if (sessionCallbackObj && !PyCallable_Check(sessionCallbackObj) &&
            cxoBuffer_fromObject(&sessionCallbackBuffer, sessionCallbackObj,
                    encoding) < 0)
        return -1;
    if (cxoBuffer_fromObject(&userNameBuffer, usernameObj, encoding) < 0 ||
            cxoBuffer_fromObject(&passwordBuffer, passwordObj, encoding) < 0 ||
            cxoBuffer_fromObject(&dsnBuffer, dsnObj, encoding) < 0 ||
            cxoBuffer_fromObject(&editionBuffer, editionObj, encoding) < 0) {
        cxoBuffer_clear(&userNameBuffer);
        cxoBuffer_clear(&passwordBuffer);
        cxoBuffer_clear(&dsnBuffer);
        cxoBuffer_clear(&sessionCallbackBuffer);
        return -1;
    }
    dpiCreateParams.minSessions = minSessions;
    dpiCreateParams.maxSessions = maxSessions;
    dpiCreateParams.sessionIncrement = sessionIncrement;
    dpiCreateParams.plsqlFixupCallback = sessionCallbackBuffer.ptr;
    dpiCreateParams.plsqlFixupCallbackLength = sessionCallbackBuffer.size;
    dpiCommonParams.edition = editionBuffer.ptr;
    dpiCommonParams.editionLength = editionBuffer.size;

    // create pool
    Py_BEGIN_ALLOW_THREADS
    status = dpiPool_create(cxoDpiContext, userNameBuffer.ptr,
            userNameBuffer.size, passwordBuffer.ptr, passwordBuffer.size,
            dsnBuffer.ptr, dsnBuffer.size, &dpiCommonParams, &dpiCreateParams,
            &pool->handle);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&userNameBuffer);
    cxoBuffer_clear(&passwordBuffer);
    cxoBuffer_clear(&dsnBuffer);
    cxoBuffer_clear(&editionBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnInt();

    // get encodings and name
    if (dpiPool_getEncodingInfo(pool->handle, &pool->encodingInfo) < 0)
        return cxoError_raiseAndReturnInt();
    pool->encodingInfo.encoding =
            cxoUtils_getAdjustedEncoding(pool->encodingInfo.encoding);
    pool->encodingInfo.nencoding =
            cxoUtils_getAdjustedEncoding(pool->encodingInfo.nencoding);
    pool->name = cxoPyString_fromEncodedString(dpiCreateParams.outPoolName,
            dpiCreateParams.outPoolNameLength, pool->encodingInfo.encoding,
            NULL);
    if (!pool->name)
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// cxoSessionPool_free()
//   Deallocate the session pool.
//-----------------------------------------------------------------------------
static void cxoSessionPool_free(cxoSessionPool *pool)
{
    if (pool->handle) {
        dpiPool_release(pool->handle);
        pool->handle = NULL;
    }
    Py_CLEAR(pool->username);
    Py_CLEAR(pool->dsn);
    Py_CLEAR(pool->name);
    Py_CLEAR(pool->sessionCallback);
    Py_TYPE(pool)->tp_free((PyObject*) pool);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_acquire()
//   Create a new connection within the session pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_acquire(cxoSessionPool *pool, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "user", "password", "cclass", "purity",
            "tag", "matchanytag", "shardingkey", "supershardingkey", NULL };
    PyObject *createKeywordArgs, *result, *cclassObj, *purityObj, *tagObj;
    PyObject *shardingKeyObj, *superShardingKeyObj;
    unsigned usernameLength, passwordLength;
    char *username, *password;
    PyObject *matchAnyTagObj;

    // parse arguments
    username = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|s#s#OOOOOO",
            keywordList, &username, &usernameLength, &password,
            &passwordLength, &cclassObj, &purityObj, &tagObj, &matchAnyTagObj,
            &shardingKeyObj, &superShardingKeyObj))
        return NULL;
    if (pool->homogeneous && username)
        return cxoError_raiseFromString(cxoProgrammingErrorException,
                "pool is homogeneous. Proxy authentication is not possible.");

    // create arguments
    if (keywordArgs)
        createKeywordArgs = PyDict_Copy(keywordArgs);
    else createKeywordArgs = PyDict_New();
    if (!createKeywordArgs)
        return NULL;
    if (PyDict_SetItemString(createKeywordArgs, "pool",
            (PyObject*) pool) < 0) {
        Py_DECREF(createKeywordArgs);
        return NULL;
    }

    // create the connection object
    result = PyObject_Call( (PyObject*) pool->connectionType, args,
            createKeywordArgs);
    Py_DECREF(createKeywordArgs);

    return result;
}


//-----------------------------------------------------------------------------
// cxoSessionPool_close()
//   Close the session pool and make it unusable.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_close(cxoSessionPool *pool, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "force", NULL };
    PyObject *forceObj;
    uint32_t closeMode;
    int temp, status;

    // parse arguments
    forceObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|O", keywordList,
            &forceObj))
        return NULL;
    if (cxoUtils_getBooleanValue(forceObj, 0, &temp) < 0)
        return NULL;
    closeMode = (temp) ? DPI_MODE_POOL_CLOSE_FORCE :
            DPI_MODE_POOL_CLOSE_DEFAULT;

    // close pool
    Py_BEGIN_ALLOW_THREADS
    status = dpiPool_close(pool->handle, closeMode);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoSessionPool_drop()
//   Release a connection back to the session pool, dropping it so that a new
// connection will be created if needed.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_drop(cxoSessionPool *pool, PyObject *args)
{
    cxoConnection *connection;
    int status;

    // connection is expected
    if (!PyArg_ParseTuple(args, "O!", &cxoPyTypeConnection, &connection))
        return NULL;

    // release the connection
    Py_BEGIN_ALLOW_THREADS
    status = dpiConn_close(connection->handle, DPI_MODE_CONN_CLOSE_DROP, NULL,
            0);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    // mark connection as closed
    Py_CLEAR(connection->sessionPool);
    dpiConn_release(connection->handle);
    connection->handle = NULL;
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoSessionPool_release()
//   Release a connection back to the session pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_release(cxoSessionPool *pool, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "connection", "tag", NULL };
    cxoConnection *conn;
    cxoBuffer tagBuffer;
    PyObject *tagObj;
    uint32_t mode;
    int status;

    // parse arguments
    tagObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O!|O",
            keywordList, &cxoPyTypeConnection, &conn, &tagObj))
        return NULL;
    if (!tagObj)
        tagObj = conn->tag;
    if (cxoBuffer_fromObject(&tagBuffer, tagObj,
            pool->encodingInfo.encoding) < 0)
        return NULL;
    mode = DPI_MODE_CONN_CLOSE_DEFAULT;
    if (tagObj && tagObj != Py_None)
        mode |= DPI_MODE_CONN_CLOSE_RETAG;
    Py_BEGIN_ALLOW_THREADS
    status = dpiConn_close(conn->handle, mode, (char*) tagBuffer.ptr,
            tagBuffer.size);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&tagBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    // mark connection as closed
    Py_CLEAR(conn->sessionPool);
    dpiConn_release(conn->handle);
    conn->handle = NULL;
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoSessionPool_getAttribute()
//   Return the value for the attribute.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_getAttribute(cxoSessionPool *pool,
        int (*func)(dpiPool *pool, uint32_t *value))
{
    uint32_t value;

    if ((*func)(pool->handle, &value) < 0)
        return cxoError_raiseAndReturnNull();
#if PY_MAJOR_VERSION >= 3
    return PyLong_FromUnsignedLong(value);
#else
    return PyInt_FromLong(value);
#endif
}


//-----------------------------------------------------------------------------
// cxoSessionPool_setAttribute()
//   Set the value of the OCI attribute.
//-----------------------------------------------------------------------------
static int cxoSessionPool_setAttribute(cxoSessionPool *pool, PyObject *value,
        int (*func)(dpiPool *pool, uint32_t value))
{
    uint32_t cValue;

    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "value must be an integer");
        return -1;
    }
#if PY_MAJOR_VERSION >= 3
    cValue = PyLong_AsUnsignedLong(value);
#else
    cValue = PyInt_AsLong(value);
#endif
    if (PyErr_Occurred())
        return -1;
    if ((*func)(pool->handle, cValue) < 0)
        return cxoError_raiseAndReturnInt();

    return 0;
}


//-----------------------------------------------------------------------------
// cxoSessionPool_getBusyCount()
//   Return the number of busy connections in the session pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_getBusyCount(cxoSessionPool *pool,
        void *unused)
{
    return cxoSessionPool_getAttribute(pool, dpiPool_getBusyCount);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_getGetMode()
//   Return the "get" mode for connections in the session pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_getGetMode(cxoSessionPool *pool, void *unused)
{
    dpiPoolGetMode value;

    if (dpiPool_getGetMode(pool->handle, &value) < 0)
        return cxoError_raiseAndReturnNull();
    return PyInt_FromLong(value);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_getMaxLifetimeSession()
//   Return the maximum lifetime session of connections in the session pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_getMaxLifetimeSession(cxoSessionPool *pool,
        void *unused)
{
    return cxoSessionPool_getAttribute(pool, dpiPool_getMaxLifetimeSession);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_getOpenCount()
//   Return the number of open connections in the session pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_getOpenCount(cxoSessionPool *pool, void *unused)
{
    return cxoSessionPool_getAttribute(pool, dpiPool_getOpenCount);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_getStmtCacheSize()
//   Return the size of the statement cache to use in connections that are
// acquired from the pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_getStmtCacheSize(cxoSessionPool *pool,
        void *unused)
{
    return cxoSessionPool_getAttribute(pool, dpiPool_getStmtCacheSize);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_getTimeout()
//   Return the timeout for connections in the session pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_getTimeout(cxoSessionPool *pool, void *unused)
{
    return cxoSessionPool_getAttribute(pool, dpiPool_getTimeout);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_getWaitTimeout()
//   Return the wait timeout for connections in the session pool.
//-----------------------------------------------------------------------------
static PyObject *cxoSessionPool_getWaitTimeout(cxoSessionPool *pool,
        void *unused)
{
    return cxoSessionPool_getAttribute(pool, dpiPool_getWaitTimeout);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_setGetMode()
//   Set the "get" mode for connections in the session pool.
//-----------------------------------------------------------------------------
static int cxoSessionPool_setGetMode(cxoSessionPool *pool, PyObject *value,
        void *unused)
{
    dpiPoolGetMode cValue;

    cValue = PyInt_AsLong(value);
    if (PyErr_Occurred())
        return -1;
    if (dpiPool_setGetMode(pool->handle, cValue) < 0)
        return cxoError_raiseAndReturnInt();

    return 0;
}


//-----------------------------------------------------------------------------
// cxoSessionPool_setMaxLifetimeSession()
//   Set the maximum lifetime for connections in the session pool.
//-----------------------------------------------------------------------------
static int cxoSessionPool_setMaxLifetimeSession(cxoSessionPool *pool,
        PyObject *value, void *unused)
{
    return cxoSessionPool_setAttribute(pool, value,
            dpiPool_setMaxLifetimeSession);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_setStmtCacheSize()
//   Set the default size of the statement cache used for connections that are
// acquired from the pool.
//-----------------------------------------------------------------------------
static int cxoSessionPool_setStmtCacheSize(cxoSessionPool *pool,
        PyObject *value, void *unused)
{
    return cxoSessionPool_setAttribute(pool, value, dpiPool_setStmtCacheSize);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_setTimeout()
//   Set the timeout for connections in the session pool.
//-----------------------------------------------------------------------------
static int cxoSessionPool_setTimeout(cxoSessionPool *pool, PyObject *value,
        void *unused)
{
    return cxoSessionPool_setAttribute(pool, value, dpiPool_setTimeout);
}


//-----------------------------------------------------------------------------
// cxoSessionPool_setWaitTimeout()
//   Set the wait timeout for connections in the session pool.
//-----------------------------------------------------------------------------
static int cxoSessionPool_setWaitTimeout(cxoSessionPool *pool, PyObject *value,
        void *unused)
{
    return cxoSessionPool_setAttribute(pool, value, dpiPool_setWaitTimeout);
}

