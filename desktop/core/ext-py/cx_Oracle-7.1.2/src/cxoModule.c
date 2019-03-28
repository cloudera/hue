//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//
// Licensed under BSD license (see LICENSE.txt).
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoModule.c
//   Implementation of cx_Oracle module.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

// define macro for adding integer constants
#define CXO_ADD_INT_CONSTANT(name, value) \
    if (PyModule_AddIntConstant(module, name, value) < 0) \
        return NULL;

// define macro for adding type objects
#define CXO_ADD_TYPE_OBJECT(name, type) \
    Py_INCREF(type); \
    if (PyModule_AddObject(module, name, (PyObject*) type) < 0) \
        return NULL;

// define macro for and making types ready
#define CXO_MAKE_TYPE_READY(type) \
    if (PyType_Ready(type) < 0) \
        return NULL;


//-----------------------------------------------------------------------------
// Globals
//-----------------------------------------------------------------------------
PyObject *cxoWarningException = NULL;
PyObject *cxoErrorException = NULL;
PyObject *cxoInterfaceErrorException = NULL;
PyObject *cxoDatabaseErrorException = NULL;
PyObject *cxoDataErrorException = NULL;
PyObject *cxoOperationalErrorException = NULL;
PyObject *cxoIntegrityErrorException = NULL;
PyObject *cxoInternalErrorException = NULL;
PyObject *cxoProgrammingErrorException = NULL;
PyObject *cxoNotSupportedErrorException = NULL;
PyObject *cxoJsonDumpFunction = NULL;
PyObject *cxoJsonLoadFunction = NULL;
cxoFuture *cxoFutureObj = NULL;
dpiContext *cxoDpiContext = NULL;
dpiVersionInfo cxoClientVersionInfo;

//-----------------------------------------------------------------------------
// cxoModule_setException()
//   Create an exception and set it in the provided dictionary.
//-----------------------------------------------------------------------------
static int cxoModule_setException(PyObject *module, PyObject **exception,
        char *name, PyObject *baseException)
{
    char buffer[100];

    sprintf(buffer, "cx_Oracle.%s", name);
    *exception = PyErr_NewException(buffer, baseException, NULL);
    if (!*exception)
        return -1;
    return PyModule_AddObject(module, name, *exception);
}


//-----------------------------------------------------------------------------
// cxoModule_makeDSN()
//   Make a data source name given the host port and SID.
//-----------------------------------------------------------------------------
static PyObject* cxoModule_makeDSN(PyObject* self, PyObject* args,
        PyObject* keywordArgs)
{
    static unsigned int numConnectDataArgs = 5;
    static char *keywordList[] = { "host", "port", "sid", "service_name",
            "region", "sharding_key", "super_sharding_key", NULL };
    PyObject *result, *connectData, *hostObj, *portObj;
    char connectDataFormat[72], *sourcePtr, *targetPtr;
    PyObject *connectDataArgs[5], *formatArgsArray;
    unsigned int i;

    // parse arguments
    for (i = 0; i < numConnectDataArgs; i++)
        connectDataArgs[i] = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "OO|OOOOO",
            keywordList, &hostObj, &portObj, &connectDataArgs[0],
            &connectDataArgs[1], &connectDataArgs[2], &connectDataArgs[3],
            &connectDataArgs[4]))
        return NULL;

    // create list for connect data format arguments
    formatArgsArray = PyList_New(0);
    if (!formatArgsArray)
        return NULL;

    // process each of the connect data arguments
    // build up a format string and a list of format arguments
    targetPtr = connectDataFormat;
    *targetPtr = '\0';
    for (i = 0; i < numConnectDataArgs; i++) {
        if (connectDataArgs[i]) {
            if (PyList_Append(formatArgsArray, connectDataArgs[i]) < 0) {
                Py_DECREF(formatArgsArray);
                return NULL;
            }
            sourcePtr = keywordList[i + 2];
            *targetPtr++ = '(';
            while (*sourcePtr)
                *targetPtr++ = toupper(*sourcePtr++);
            *targetPtr++ = '=';
            *targetPtr++ = '%';
            *targetPtr++ = 's';
            *targetPtr++ = ')';
            *targetPtr = '\0';
        }
    }

    // determine connect data
    connectData = cxoUtils_formatString(connectDataFormat,
            PyList_AsTuple(formatArgsArray));
    Py_DECREF(formatArgsArray);
    if (!connectData)
        return NULL;

    // perform overall format
    result = cxoUtils_formatString("(DESCRIPTION=(ADDRESS="
            "(PROTOCOL=TCP)(HOST=%s)(PORT=%s))(CONNECT_DATA=%s))",
            PyTuple_Pack(3, hostObj, portObj, connectData));
    Py_DECREF(connectData);
    return result;
}


//-----------------------------------------------------------------------------
// cxoModule_clientVersion()
//   Return the version of the Oracle client being used as a 5-tuple.
//-----------------------------------------------------------------------------
static PyObject* cxoModule_clientVersion(PyObject* self, PyObject* args)
{
    if (cxoUtils_initializeDPI() < 0)
        return NULL;
    return Py_BuildValue("(iiiii)", cxoClientVersionInfo.versionNum,
            cxoClientVersionInfo.releaseNum, cxoClientVersionInfo.updateNum,
            cxoClientVersionInfo.portReleaseNum,
            cxoClientVersionInfo.portUpdateNum);
}


//-----------------------------------------------------------------------------
// cxoModule_time()
//   Returns a time value suitable for binding.
//-----------------------------------------------------------------------------
static PyObject* cxoModule_time(PyObject* self, PyObject* args)
{
    return cxoError_raiseFromString(cxoNotSupportedErrorException,
            "Oracle does not support time only variables");
}


//-----------------------------------------------------------------------------
// cxoModule_timeFromTicks()
//   Returns a time value suitable for binding.
//-----------------------------------------------------------------------------
static PyObject* cxoModule_timeFromTicks(PyObject* self, PyObject* args)
{
    return cxoError_raiseFromString(cxoNotSupportedErrorException,
            "Oracle does not support time only variables");
}


//-----------------------------------------------------------------------------
// cxoModule_dateFromTicks()
//   Returns a date value suitable for binding.
//-----------------------------------------------------------------------------
static PyObject* cxoModule_dateFromTicks(PyObject* self, PyObject* args)
{
    return cxoTransform_dateFromTicks(args);
}


//-----------------------------------------------------------------------------
// cxoModule_timestampFromTicks()
//   Returns a date value suitable for binding.
//-----------------------------------------------------------------------------
static PyObject* cxoModule_timestampFromTicks(PyObject* self, PyObject* args)
{
    return cxoTransform_timestampFromTicks(args);
}


//-----------------------------------------------------------------------------
//   Declaration of methods supported by this module
//-----------------------------------------------------------------------------
static PyMethodDef cxoModuleMethods[] = {
    { "makedsn", (PyCFunction) cxoModule_makeDSN,
            METH_VARARGS | METH_KEYWORDS },
    { "Time", (PyCFunction) cxoModule_time, METH_VARARGS },
    { "DateFromTicks", (PyCFunction) cxoModule_dateFromTicks, METH_VARARGS },
    { "TimeFromTicks", (PyCFunction) cxoModule_timeFromTicks, METH_VARARGS },
    { "TimestampFromTicks", (PyCFunction) cxoModule_timestampFromTicks,
            METH_VARARGS },
    { "clientversion", (PyCFunction) cxoModule_clientVersion, METH_NOARGS },
    { NULL }
};


#if PY_MAJOR_VERSION >= 3
//-----------------------------------------------------------------------------
//   Declaration of module definition for Python 3.x.
//-----------------------------------------------------------------------------
static struct PyModuleDef cxoModuleDef = {
    PyModuleDef_HEAD_INIT,
    "cx_Oracle",
    NULL,
    -1,
    cxoModuleMethods,                      // methods
    NULL,                                  // m_reload
    NULL,                                  // traverse
    NULL,                                  // clear
    NULL                                   // free
};
#endif


//-----------------------------------------------------------------------------
// cxoModule_initialize()
//   Initialization routine for the module.
//-----------------------------------------------------------------------------
static PyObject *cxoModule_initialize(void)
{
    PyObject *module;

#ifdef WITH_THREAD
    PyEval_InitThreads();
#endif

    // initialize transforms
    if (cxoTransform_init() < 0)
        return NULL;

    // prepare the types for use by the module
    CXO_MAKE_TYPE_READY(&cxoPyTypeBfileVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeBinaryVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeBlobVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeBooleanVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeClobVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeConnection);
    CXO_MAKE_TYPE_READY(&cxoPyTypeCursor);
    CXO_MAKE_TYPE_READY(&cxoPyTypeCursorVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeDateTimeVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeDeqOptions);
    CXO_MAKE_TYPE_READY(&cxoPyTypeEnqOptions);
    CXO_MAKE_TYPE_READY(&cxoPyTypeError);
    CXO_MAKE_TYPE_READY(&cxoPyTypeFixedCharVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeFixedNcharVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeFuture);
    CXO_MAKE_TYPE_READY(&cxoPyTypeIntervalVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeLob);
    CXO_MAKE_TYPE_READY(&cxoPyTypeLongBinaryVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeLongStringVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeMsgProps);
    CXO_MAKE_TYPE_READY(&cxoPyTypeMessage);
    CXO_MAKE_TYPE_READY(&cxoPyTypeMessageQuery);
    CXO_MAKE_TYPE_READY(&cxoPyTypeMessageRow);
    CXO_MAKE_TYPE_READY(&cxoPyTypeMessageTable);
    CXO_MAKE_TYPE_READY(&cxoPyTypeNativeFloatVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeNativeIntVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeNcharVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeNclobVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeNumberVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeObjectAttr);
    CXO_MAKE_TYPE_READY(&cxoPyTypeObject);
    CXO_MAKE_TYPE_READY(&cxoPyTypeObjectType);
    CXO_MAKE_TYPE_READY(&cxoPyTypeObjectVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeRowidVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeSessionPool);
    CXO_MAKE_TYPE_READY(&cxoPyTypeSodaCollection);
    CXO_MAKE_TYPE_READY(&cxoPyTypeSodaDatabase);
    CXO_MAKE_TYPE_READY(&cxoPyTypeSodaDoc);
    CXO_MAKE_TYPE_READY(&cxoPyTypeSodaDocCursor);
    CXO_MAKE_TYPE_READY(&cxoPyTypeSodaOperation);
    CXO_MAKE_TYPE_READY(&cxoPyTypeStringVar);
    CXO_MAKE_TYPE_READY(&cxoPyTypeSubscr);
    CXO_MAKE_TYPE_READY(&cxoPyTypeTimestampVar);

    // initialize module and retrieve the dictionary
#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&cxoModuleDef);
#else
    module = Py_InitModule("cx_Oracle", cxoModuleMethods);
#endif
    if (!module)
        return NULL;

    // create exception object and add it to the dictionary
    if (cxoModule_setException(module, &cxoWarningException,
            "Warning", CXO_BASE_EXCEPTION) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoErrorException,
            "Error", CXO_BASE_EXCEPTION) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoInterfaceErrorException,
            "InterfaceError", cxoErrorException) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoDatabaseErrorException,
            "DatabaseError", cxoErrorException) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoDataErrorException,
            "DataError", cxoDatabaseErrorException) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoOperationalErrorException,
            "OperationalError", cxoDatabaseErrorException) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoIntegrityErrorException,
            "IntegrityError", cxoDatabaseErrorException) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoInternalErrorException,
            "InternalError", cxoDatabaseErrorException) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoProgrammingErrorException,
            "ProgrammingError", cxoDatabaseErrorException) < 0)
        return NULL;
    if (cxoModule_setException(module, &cxoNotSupportedErrorException,
            "NotSupportedError", cxoDatabaseErrorException) < 0)
        return NULL;

    // set up the types that are available
#if PY_MAJOR_VERSION >= 3
    CXO_ADD_TYPE_OBJECT("Binary", &PyBytes_Type)
#else
    CXO_ADD_TYPE_OBJECT("Binary", &PyBuffer_Type)
#endif
    CXO_ADD_TYPE_OBJECT("Connection", &cxoPyTypeConnection)
    CXO_ADD_TYPE_OBJECT("Cursor", &cxoPyTypeCursor)
    CXO_ADD_TYPE_OBJECT("Timestamp", cxoPyTypeDateTime)
    CXO_ADD_TYPE_OBJECT("Date", cxoPyTypeDate)
    CXO_ADD_TYPE_OBJECT("SessionPool", &cxoPyTypeSessionPool)
    CXO_ADD_TYPE_OBJECT("_Error", &cxoPyTypeError)
    CXO_ADD_TYPE_OBJECT("Object", &cxoPyTypeObject)
    CXO_ADD_TYPE_OBJECT("ObjectType", &cxoPyTypeObjectType)
    CXO_ADD_TYPE_OBJECT("EnqOptions", &cxoPyTypeEnqOptions)
    CXO_ADD_TYPE_OBJECT("DeqOptions", &cxoPyTypeDeqOptions)
    CXO_ADD_TYPE_OBJECT("MessageProperties", &cxoPyTypeMsgProps)
    CXO_ADD_TYPE_OBJECT("SodaCollection", &cxoPyTypeSodaCollection)
    CXO_ADD_TYPE_OBJECT("SodaDatabase", &cxoPyTypeSodaDatabase)
    CXO_ADD_TYPE_OBJECT("SodaDoc", &cxoPyTypeSodaDoc)
    CXO_ADD_TYPE_OBJECT("SodaDocCursor", &cxoPyTypeSodaDocCursor)
    CXO_ADD_TYPE_OBJECT("SodaOperation", &cxoPyTypeSodaOperation)

    // the name "connect" is required by the DB API
    CXO_ADD_TYPE_OBJECT("connect", &cxoPyTypeConnection)

    // create the basic data types for setting input sizes
    CXO_ADD_TYPE_OBJECT("BINARY", &cxoPyTypeBinaryVar)
    CXO_ADD_TYPE_OBJECT("BFILE", &cxoPyTypeBfileVar)
    CXO_ADD_TYPE_OBJECT("BLOB", &cxoPyTypeBlobVar)
    CXO_ADD_TYPE_OBJECT("CLOB", &cxoPyTypeClobVar)
    CXO_ADD_TYPE_OBJECT("CURSOR", &cxoPyTypeCursorVar)
    CXO_ADD_TYPE_OBJECT("OBJECT", &cxoPyTypeObjectVar)
    CXO_ADD_TYPE_OBJECT("DATETIME", &cxoPyTypeDateTimeVar)
    CXO_ADD_TYPE_OBJECT("FIXED_CHAR", &cxoPyTypeFixedCharVar)
    CXO_ADD_TYPE_OBJECT("FIXED_NCHAR", &cxoPyTypeFixedNcharVar)
    CXO_ADD_TYPE_OBJECT("NCHAR", &cxoPyTypeNcharVar)
    CXO_ADD_TYPE_OBJECT("INTERVAL", &cxoPyTypeIntervalVar)
    CXO_ADD_TYPE_OBJECT("LOB", &cxoPyTypeLob)
    CXO_ADD_TYPE_OBJECT("LONG_BINARY", &cxoPyTypeLongBinaryVar)
    CXO_ADD_TYPE_OBJECT("LONG_STRING", &cxoPyTypeLongStringVar)
    CXO_ADD_TYPE_OBJECT("NCLOB", &cxoPyTypeNclobVar)
    CXO_ADD_TYPE_OBJECT("NUMBER", &cxoPyTypeNumberVar)
    CXO_ADD_TYPE_OBJECT("ROWID", &cxoPyTypeRowidVar)
    CXO_ADD_TYPE_OBJECT("STRING", &cxoPyTypeStringVar)
    CXO_ADD_TYPE_OBJECT("TIMESTAMP", &cxoPyTypeTimestampVar)
    CXO_ADD_TYPE_OBJECT("NATIVE_INT", &cxoPyTypeNativeIntVar)
    CXO_ADD_TYPE_OBJECT("NATIVE_FLOAT", &cxoPyTypeNativeFloatVar)
    CXO_ADD_TYPE_OBJECT("BOOLEAN", &cxoPyTypeBooleanVar)

    // create constants required by Python DB API 2.0
    if (PyModule_AddStringConstant(module, "apilevel", "2.0") < 0)
        return NULL;
    if (PyModule_AddIntConstant(module, "threadsafety", 2) < 0)
        return NULL;
    if (PyModule_AddStringConstant(module, "paramstyle", "named") < 0)
        return NULL;

    // add version and build time for easier support
    if (PyModule_AddStringConstant(module, "version",
            CXO_BUILD_VERSION_STRING) < 0)
        return NULL;
    if (PyModule_AddStringConstant(module, "__version__",
            CXO_BUILD_VERSION_STRING) < 0)
        return NULL;
    if (PyModule_AddStringConstant(module, "buildtime",
            __DATE__ " " __TIME__) < 0)
        return NULL;

    // create and initialize future object
    cxoFutureObj = (cxoFuture*) cxoPyTypeFuture.tp_alloc(&cxoPyTypeFuture, 0);
    if (!cxoFutureObj)
        return NULL;
    if (PyModule_AddObject(module, "__future__", (PyObject*) cxoFutureObj) < 0)
        return NULL;

    // add constants for authorization modes
    CXO_ADD_INT_CONSTANT("SYSASM", DPI_MODE_AUTH_SYSASM)
    CXO_ADD_INT_CONSTANT("SYSBKP", DPI_MODE_AUTH_SYSBKP)
    CXO_ADD_INT_CONSTANT("SYSDBA", DPI_MODE_AUTH_SYSDBA)
    CXO_ADD_INT_CONSTANT("SYSDGD", DPI_MODE_AUTH_SYSDGD)
    CXO_ADD_INT_CONSTANT("SYSKMT", DPI_MODE_AUTH_SYSKMT)
    CXO_ADD_INT_CONSTANT("SYSOPER", DPI_MODE_AUTH_SYSOPER)
    CXO_ADD_INT_CONSTANT("SYSRAC", DPI_MODE_AUTH_SYSRAC)
    CXO_ADD_INT_CONSTANT("PRELIM_AUTH", DPI_MODE_AUTH_PRELIM)

    // add constants for session pool get modes
    CXO_ADD_INT_CONSTANT("SPOOL_ATTRVAL_WAIT", DPI_MODE_POOL_GET_WAIT)
    CXO_ADD_INT_CONSTANT("SPOOL_ATTRVAL_NOWAIT", DPI_MODE_POOL_GET_NOWAIT)
    CXO_ADD_INT_CONSTANT("SPOOL_ATTRVAL_FORCEGET", DPI_MODE_POOL_GET_FORCEGET)
    CXO_ADD_INT_CONSTANT("SPOOL_ATTRVAL_TIMEDWAIT",
            DPI_MODE_POOL_GET_TIMEDWAIT)

    // add constants for database shutdown modes
    CXO_ADD_INT_CONSTANT("DBSHUTDOWN_ABORT", DPI_MODE_SHUTDOWN_ABORT)
    CXO_ADD_INT_CONSTANT("DBSHUTDOWN_FINAL", DPI_MODE_SHUTDOWN_FINAL)
    CXO_ADD_INT_CONSTANT("DBSHUTDOWN_IMMEDIATE", DPI_MODE_SHUTDOWN_IMMEDIATE)
    CXO_ADD_INT_CONSTANT("DBSHUTDOWN_TRANSACTIONAL",
            DPI_MODE_SHUTDOWN_TRANSACTIONAL)
    CXO_ADD_INT_CONSTANT("DBSHUTDOWN_TRANSACTIONAL_LOCAL",
            DPI_MODE_SHUTDOWN_TRANSACTIONAL_LOCAL)

    // add constants for purity
    CXO_ADD_INT_CONSTANT("ATTR_PURITY_DEFAULT", DPI_PURITY_DEFAULT)
    CXO_ADD_INT_CONSTANT("ATTR_PURITY_NEW", DPI_PURITY_NEW)
    CXO_ADD_INT_CONSTANT("ATTR_PURITY_SELF", DPI_PURITY_SELF)

    // add constants for subscription protocols
    CXO_ADD_INT_CONSTANT("SUBSCR_PROTO_OCI", DPI_SUBSCR_PROTO_CALLBACK)
    CXO_ADD_INT_CONSTANT("SUBSCR_PROTO_MAIL", DPI_SUBSCR_PROTO_MAIL)
    CXO_ADD_INT_CONSTANT("SUBSCR_PROTO_SERVER", DPI_SUBSCR_PROTO_PLSQL)
    CXO_ADD_INT_CONSTANT("SUBSCR_PROTO_HTTP", DPI_SUBSCR_PROTO_HTTP)

    // add constants for subscription quality of service
    CXO_ADD_INT_CONSTANT("SUBSCR_QOS_RELIABLE", DPI_SUBSCR_QOS_RELIABLE)
    CXO_ADD_INT_CONSTANT("SUBSCR_QOS_DEREG_NFY", DPI_SUBSCR_QOS_DEREG_NFY)
    CXO_ADD_INT_CONSTANT("SUBSCR_QOS_ROWIDS", DPI_SUBSCR_QOS_ROWIDS)
    CXO_ADD_INT_CONSTANT("SUBSCR_QOS_QUERY", DPI_SUBSCR_QOS_QUERY)
    CXO_ADD_INT_CONSTANT("SUBSCR_QOS_BEST_EFFORT", DPI_SUBSCR_QOS_BEST_EFFORT)

    // add constants for subscription namespaces
    CXO_ADD_INT_CONSTANT("SUBSCR_NAMESPACE_AQ", DPI_SUBSCR_NAMESPACE_AQ)
    CXO_ADD_INT_CONSTANT("SUBSCR_NAMESPACE_DBCHANGE",
            DPI_SUBSCR_NAMESPACE_DBCHANGE)

    // add constants for subscription grouping classes
    CXO_ADD_INT_CONSTANT("SUBSCR_GROUPING_CLASS_TIME",
            DPI_SUBSCR_GROUPING_CLASS_TIME)

    // add constants for subscription grouping types
    CXO_ADD_INT_CONSTANT("SUBSCR_GROUPING_TYPE_SUMMARY",
            DPI_SUBSCR_GROUPING_TYPE_SUMMARY)
    CXO_ADD_INT_CONSTANT("SUBSCR_GROUPING_TYPE_LAST",
            DPI_SUBSCR_GROUPING_TYPE_LAST)

    // add constants for event types
    CXO_ADD_INT_CONSTANT("EVENT_NONE", DPI_EVENT_NONE)
    CXO_ADD_INT_CONSTANT("EVENT_STARTUP", DPI_EVENT_STARTUP)
    CXO_ADD_INT_CONSTANT("EVENT_SHUTDOWN", DPI_EVENT_SHUTDOWN)
    CXO_ADD_INT_CONSTANT("EVENT_SHUTDOWN_ANY", DPI_EVENT_SHUTDOWN_ANY)
    CXO_ADD_INT_CONSTANT("EVENT_DEREG", DPI_EVENT_DEREG)
    CXO_ADD_INT_CONSTANT("EVENT_OBJCHANGE", DPI_EVENT_OBJCHANGE)
    CXO_ADD_INT_CONSTANT("EVENT_QUERYCHANGE", DPI_EVENT_QUERYCHANGE)
    CXO_ADD_INT_CONSTANT("EVENT_AQ", DPI_EVENT_AQ)

    // add constants for opcodes
    CXO_ADD_INT_CONSTANT("OPCODE_ALLOPS", DPI_OPCODE_ALL_OPS)
    CXO_ADD_INT_CONSTANT("OPCODE_ALLROWS", DPI_OPCODE_ALL_ROWS)
    CXO_ADD_INT_CONSTANT("OPCODE_INSERT", DPI_OPCODE_INSERT)
    CXO_ADD_INT_CONSTANT("OPCODE_UPDATE", DPI_OPCODE_UPDATE)
    CXO_ADD_INT_CONSTANT("OPCODE_DELETE", DPI_OPCODE_DELETE)
    CXO_ADD_INT_CONSTANT("OPCODE_ALTER", DPI_OPCODE_ALTER)
    CXO_ADD_INT_CONSTANT("OPCODE_DROP", DPI_OPCODE_DROP)

    // add constants for AQ dequeue modes
    CXO_ADD_INT_CONSTANT("DEQ_BROWSE", DPI_MODE_DEQ_BROWSE)
    CXO_ADD_INT_CONSTANT("DEQ_LOCKED", DPI_MODE_DEQ_LOCKED)
    CXO_ADD_INT_CONSTANT("DEQ_REMOVE", DPI_MODE_DEQ_REMOVE)
    CXO_ADD_INT_CONSTANT("DEQ_REMOVE_NODATA", DPI_MODE_DEQ_REMOVE_NO_DATA)

    // add constants for AQ dequeue navigation
    CXO_ADD_INT_CONSTANT("DEQ_FIRST_MSG", DPI_DEQ_NAV_FIRST_MSG)
    CXO_ADD_INT_CONSTANT("DEQ_NEXT_TRANSACTION", DPI_DEQ_NAV_NEXT_TRANSACTION)
    CXO_ADD_INT_CONSTANT("DEQ_NEXT_MSG", DPI_DEQ_NAV_NEXT_MSG)

    // add constants for AQ dequeue visibility
    CXO_ADD_INT_CONSTANT("DEQ_IMMEDIATE", DPI_VISIBILITY_IMMEDIATE)
    CXO_ADD_INT_CONSTANT("DEQ_ON_COMMIT", DPI_VISIBILITY_ON_COMMIT)

    // add constants for AQ dequeue wait
    CXO_ADD_INT_CONSTANT("DEQ_NO_WAIT", DPI_DEQ_WAIT_NO_WAIT)
    CXO_ADD_INT_CONSTANT("DEQ_WAIT_FOREVER", DPI_DEQ_WAIT_FOREVER)

    // add constants for AQ enqueue visibility
    CXO_ADD_INT_CONSTANT("ENQ_IMMEDIATE", DPI_VISIBILITY_IMMEDIATE)
    CXO_ADD_INT_CONSTANT("ENQ_ON_COMMIT", DPI_VISIBILITY_ON_COMMIT)

    // add constants for AQ table purge mode (message)
    CXO_ADD_INT_CONSTANT("MSG_PERSISTENT", DPI_MODE_MSG_PERSISTENT)
    CXO_ADD_INT_CONSTANT("MSG_BUFFERED", DPI_MODE_MSG_BUFFERED)
    CXO_ADD_INT_CONSTANT("MSG_PERSISTENT_OR_BUFFERED",
            DPI_MODE_MSG_PERSISTENT_OR_BUFFERED)

    // add constants for AQ message state
    CXO_ADD_INT_CONSTANT("MSG_EXPIRED", DPI_MSG_STATE_EXPIRED)
    CXO_ADD_INT_CONSTANT("MSG_READY", DPI_MSG_STATE_READY)
    CXO_ADD_INT_CONSTANT("MSG_PROCESSED", DPI_MSG_STATE_PROCESSED)
    CXO_ADD_INT_CONSTANT("MSG_WAITING", DPI_MSG_STATE_WAITING)

    // add special constants for AQ delay/expiration
    CXO_ADD_INT_CONSTANT("MSG_NO_DELAY", 0)
    CXO_ADD_INT_CONSTANT("MSG_NO_EXPIRATION", -1)

    return module;
}


//-----------------------------------------------------------------------------
// Start routine for the module.
//-----------------------------------------------------------------------------
#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_cx_Oracle(void)
{
    return cxoModule_initialize();
}
#else
void initcx_Oracle(void)
{
    cxoModule_initialize();
}
#endif

