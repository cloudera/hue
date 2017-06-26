//-----------------------------------------------------------------------------
// cx_Oracle.c
//   Shared library for use by Python.
//-----------------------------------------------------------------------------

#include <Python.h>
#include <datetime.h>
#include <structmember.h>
#include <time.h>
#include <oci.h>
#include <orid.h>
#include <xa.h>

// define simple way to respresent Oracle version
#define ORACLE_VERSION(major, minor) \
        ((major << 8) | minor)

// define what version of Oracle we are building as 2 byte hex number
#if !defined(OCI_MAJOR_VERSION) && defined(OCI_ATTR_MODULE)
#define OCI_MAJOR_VERSION 10
#define OCI_MINOR_VERSION 1
#endif
#if defined(OCI_MAJOR_VERSION) && defined(OCI_MINOR_VERSION)
#define ORACLE_VERSION_HEX \
        ORACLE_VERSION(OCI_MAJOR_VERSION, OCI_MINOR_VERSION)
#else
#error Unsupported version of OCI.
#endif

// PY_LONG_LONG was called LONG_LONG before Python 2.3
#ifndef PY_LONG_LONG
#define PY_LONG_LONG LONG_LONG
#endif

// define Py_ssize_t for versions before Python 2.5
#if PY_VERSION_HEX < 0x02050000
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif

// define T_BOOL for versions before Python 2.5
#ifndef T_BOOL
#define T_BOOL                  T_INT
#endif

// define Py_TYPE for versions before Python 2.6
#ifndef Py_TYPE
#define Py_TYPE(ob)             (((PyObject*)(ob))->ob_type)
#endif

// define PyVarObject_HEAD_INIT for versions before Python 2.6
#ifndef PyVarObject_HEAD_INIT
#define PyVarObject_HEAD_INIT(type, size) \
        PyObject_HEAD_INIT(type) size,
#endif

// define PyInt_* macros for Python 3.x
#ifndef PyInt_Check
#define PyInt_Check             PyLong_Check
#define PyInt_FromLong          PyLong_FromLong
#define PyInt_AsLong            PyLong_AsLong
#define PyInt_Type              PyLong_Type
#endif

// use the bytes methods in cx_Oracle and define them as the equivalent string
// type methods as is done in Python 2.6
#ifndef PyBytes_Check
    #define PyBytes_Type                PyString_Type
    #define PyBytes_AS_STRING           PyString_AS_STRING
    #define PyBytes_GET_SIZE            PyString_GET_SIZE
    #define PyBytes_Check               PyString_Check
    #define PyBytes_Format              PyString_Format
    #define PyBytes_FromString          PyString_FromString
    #define PyBytes_FromStringAndSize   PyString_FromStringAndSize
#endif

// define types and methods for strings and binary data
#if PY_MAJOR_VERSION >= 3
    #define cxBinary_Type               PyBytes_Type
    #define cxBinary_Check              PyBytes_Check
    #define cxString_Type               &PyUnicode_Type
    #define cxString_Format             PyUnicode_Format
    #define cxString_Check              PyUnicode_Check
    #define cxString_GetSize            PyUnicode_GET_SIZE
#else
    #define cxBinary_Type               PyBuffer_Type
    #define cxBinary_Check              PyBuffer_Check
    #define cxString_Type               &PyBytes_Type
    #define cxString_Format             PyBytes_Format
    #define cxString_Check              PyBytes_Check
    #define cxString_GetSize            PyBytes_GET_SIZE
#endif

// define string type and methods
#if PY_MAJOR_VERSION >= 3
    #define cxString_FromAscii(str) \
        PyUnicode_DecodeASCII(str, strlen(str), NULL)
    #define cxString_FromEncodedString(buffer, numBytes, encoding) \
        PyUnicode_Decode(buffer, numBytes, encoding, NULL)
#else
    #define cxString_FromAscii(str) \
        PyBytes_FromString(str)
    #define cxString_FromEncodedString(buffer, numBytes, encoding) \
        PyBytes_FromStringAndSize(buffer, numBytes)
#endif

// define base exception
#if PY_MAJOR_VERSION >= 3
#define CXORA_BASE_EXCEPTION    NULL
#define CXORA_TYPE_ERROR        "expecting string or bytes object"
#else
#define CXORA_BASE_EXCEPTION    PyExc_StandardError
#define CXORA_TYPE_ERROR        "expecting string, unicode or buffer object"
#endif

// define macro for adding OCI constants
#define ADD_OCI_CONSTANT(x) \
    if (PyModule_AddIntConstant(module, #x, OCI_ ##x) < 0) \
        return NULL;

// define macro for adding type objects
#define ADD_TYPE_OBJECT(name, type) \
    Py_INCREF(type); \
    if (PyModule_AddObject(module, name, (PyObject*) type) < 0) \
        return NULL;

// define macros for making types ready
#define MAKE_TYPE_READY(type) \
    if (PyType_Ready(type) < 0) \
        return NULL;
#define MAKE_VARIABLE_TYPE_READY(type) \
    (type)->tp_base = &g_BaseVarType;  \
    MAKE_TYPE_READY(type)

// define macros to get the build version as a string and the driver name
#define xstr(s)                 str(s)
#define str(s)                  #s
#define BUILD_VERSION_STRING    xstr(BUILD_VERSION)
#define DRIVER_NAME             "cx_Oracle-"BUILD_VERSION_STRING

#include "Buffer.c"

//-----------------------------------------------------------------------------
// Globals
//-----------------------------------------------------------------------------
static PyObject *g_WarningException = NULL;
static PyObject *g_ErrorException = NULL;
static PyObject *g_InterfaceErrorException = NULL;
static PyObject *g_DatabaseErrorException = NULL;
static PyObject *g_DataErrorException = NULL;
static PyObject *g_OperationalErrorException = NULL;
static PyObject *g_IntegrityErrorException = NULL;
static PyObject *g_InternalErrorException = NULL;
static PyObject *g_ProgrammingErrorException = NULL;
static PyObject *g_NotSupportedErrorException = NULL;
static PyTypeObject *g_DateTimeType = NULL;
static PyTypeObject *g_DecimalType = NULL;


//-----------------------------------------------------------------------------
// SetException()
//   Create an exception and set it in the provided dictionary.
//-----------------------------------------------------------------------------
static int SetException(
    PyObject *module,                   // module object
    PyObject **exception,               // exception to create
    char *name,                         // name of the exception
    PyObject *baseException)            // exception to base exception on
{
    char buffer[100];

    sprintf(buffer, "cx_Oracle.%s", name);
    *exception = PyErr_NewException(buffer, baseException, NULL);
    if (!*exception)
        return -1;
    return PyModule_AddObject(module, name, *exception);
}


//-----------------------------------------------------------------------------
// GetModuleAndName()
//   Return the module and name for the type.
//-----------------------------------------------------------------------------
static int GetModuleAndName(
    PyTypeObject *type,                 // type to get module/name for
    PyObject **module,                  // name of module
    PyObject **name)                    // name of type
{
    *module = PyObject_GetAttrString( (PyObject*) type, "__module__");
    if (!*module)
        return -1;
    *name = PyObject_GetAttrString( (PyObject*) type, "__name__");
    if (!*name) {
        Py_DECREF(*module);
        return -1;
    }
    return 0;
}


#include "Environment.c"
#include "SessionPool.c"


//-----------------------------------------------------------------------------
// MakeDSN()
//   Make a data source name given the host port and SID.
//-----------------------------------------------------------------------------
static PyObject* MakeDSN(
    PyObject* self,                     // passthrough argument
    PyObject* args,                     // arguments to function
    PyObject* keywordArgs)              // keyword arguments
{
    static char *keywordList[] = { "host", "port", "sid", "service_name",
            NULL };
    PyObject *hostObj, *portObj, *sidObj, *serviceNameObj, *connectDataObj;
    PyObject *format, *result, *formatArgs;

    // parse arguments
    sidObj = serviceNameObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "OO|OO", keywordList,
            &hostObj, &portObj, &sidObj, &serviceNameObj))
        return NULL;
    if (sidObj) {
        connectDataObj = sidObj;
        format = cxString_FromAscii("(DESCRIPTION=(ADDRESS_LIST=(ADDRESS="
                "(PROTOCOL=TCP)(HOST=%s)(PORT=%s)))(CONNECT_DATA=(SID=%s)))");
    } else {
        connectDataObj = serviceNameObj;
        format = cxString_FromAscii("(DESCRIPTION=(ADDRESS_LIST=(ADDRESS="
                "(PROTOCOL=TCP)(HOST=%s)(PORT=%s)))(CONNECT_DATA="
                "(SERVICE_NAME=%s)))");
    }
    if (!format)
        return NULL;
    formatArgs = PyTuple_Pack(3, hostObj, portObj, connectDataObj);
    if (!formatArgs) {
        Py_DECREF(format);
        return NULL;
    }
    result = cxString_Format(format, formatArgs);
    Py_DECREF(format);
    Py_DECREF(formatArgs);
    return result;
}


#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
//-----------------------------------------------------------------------------
// ClientVersion()
//   Return the version of the Oracle client being used as a 5-tuple.
//-----------------------------------------------------------------------------
static PyObject* ClientVersion(
    PyObject* self,                     // passthrough argument
    PyObject* args)                     // arguments to function
{
    sword majorVersion, minorVersion, updateNum, patchNum, portUpdateNum;

    OCIClientVersion(&majorVersion, &minorVersion, &updateNum,
            &patchNum, &portUpdateNum);
    return Py_BuildValue("(iiiii)", majorVersion, minorVersion, updateNum,
            patchNum, portUpdateNum);
}
#endif


//-----------------------------------------------------------------------------
// Time()
//   Returns a time value suitable for binding.
//-----------------------------------------------------------------------------
static PyObject* Time(
    PyObject* self,                     // passthrough argument
    PyObject* args)                     // arguments to function
{
    PyErr_SetString(g_NotSupportedErrorException,
            "Oracle does not support time only variables");
    return NULL;
}


//-----------------------------------------------------------------------------
// TimeFromTicks()
//   Returns a time value suitable for binding.
//-----------------------------------------------------------------------------
static PyObject* TimeFromTicks(
    PyObject* self,                     // passthrough argument
    PyObject* args)                     // arguments to function
{
    PyErr_SetString(g_NotSupportedErrorException,
            "Oracle does not support time only variables");
    return NULL;
}


//-----------------------------------------------------------------------------
// DateFromTicks()
//   Returns a date value suitable for binding.
//-----------------------------------------------------------------------------
static PyObject* DateFromTicks(
    PyObject* self,                     // passthrough argument
    PyObject* args)                     // arguments to function
{
    return PyDate_FromTimestamp(args);
}


//-----------------------------------------------------------------------------
// TimestampFromTicks()
//   Returns a date value suitable for binding.
//-----------------------------------------------------------------------------
static PyObject* TimestampFromTicks(
    PyObject* self,                     // passthrough argument
    PyObject* args)                     // arguments to function
{
    return PyDateTime_FromTimestamp(args);
}


//-----------------------------------------------------------------------------
//   Declaration of methods supported by this module
//-----------------------------------------------------------------------------
static PyMethodDef g_ModuleMethods[] = {
    { "makedsn", (PyCFunction) MakeDSN, METH_VARARGS | METH_KEYWORDS },
    { "Time", (PyCFunction) Time, METH_VARARGS },
    { "DateFromTicks", (PyCFunction) DateFromTicks, METH_VARARGS },
    { "TimeFromTicks", (PyCFunction) TimeFromTicks, METH_VARARGS },
    { "TimestampFromTicks", (PyCFunction) TimestampFromTicks, METH_VARARGS },
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
    { "clientversion", (PyCFunction) ClientVersion, METH_NOARGS },
#endif
    { NULL }
};


#if PY_MAJOR_VERSION >= 3
//-----------------------------------------------------------------------------
//   Declaration of module definition for Python 3.x.
//-----------------------------------------------------------------------------
static struct PyModuleDef g_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    "cx_Oracle",
    NULL,
    -1,
    g_ModuleMethods,                       // methods
    NULL,                                  // m_reload
    NULL,                                  // traverse
    NULL,                                  // clear
    NULL                                   // free
};
#endif


//-----------------------------------------------------------------------------
// Module_Initialize()
//   Initialization routine for the module.
//-----------------------------------------------------------------------------
static PyObject *Module_Initialize(void)
{
    PyObject *module;

#ifdef WITH_THREAD
    PyEval_InitThreads();
#endif

    // import the datetime module for datetime support
    PyDateTime_IMPORT;
    if (PyErr_Occurred())
        return NULL;

    // import the decimal module for decimal support
    module = PyImport_ImportModule("decimal");
    if (!module)
        return NULL;
    g_DecimalType = (PyTypeObject*) PyObject_GetAttrString(module, "Decimal");
    if (!g_DecimalType)
        return NULL;

    // prepare the types for use by the module
    MAKE_TYPE_READY(&g_ConnectionType);
    MAKE_TYPE_READY(&g_CursorType);
    MAKE_TYPE_READY(&g_ErrorType);
    MAKE_TYPE_READY(&g_SessionPoolType);
    MAKE_TYPE_READY(&g_EnvironmentType);
    MAKE_TYPE_READY(&g_ObjectTypeType);
    MAKE_TYPE_READY(&g_ObjectAttributeType);
    MAKE_TYPE_READY(&g_ExternalLobVarType);
    MAKE_TYPE_READY(&g_ExternalObjectVarType);
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
    MAKE_TYPE_READY(&g_SubscriptionType);
    MAKE_TYPE_READY(&g_MessageType);
    MAKE_TYPE_READY(&g_MessageTableType);
    MAKE_TYPE_READY(&g_MessageRowType);
#endif
#if ORACLE_VERSION_HEX > ORACLE_VERSION(11, 1)
    MAKE_TYPE_READY(&g_MessageQueryType);
#endif
    MAKE_VARIABLE_TYPE_READY(&g_StringVarType);
    MAKE_VARIABLE_TYPE_READY(&g_FixedCharVarType);
    MAKE_VARIABLE_TYPE_READY(&g_RowidVarType);
    MAKE_VARIABLE_TYPE_READY(&g_BinaryVarType);
    MAKE_VARIABLE_TYPE_READY(&g_LongStringVarType);
    MAKE_VARIABLE_TYPE_READY(&g_LongBinaryVarType);
    MAKE_VARIABLE_TYPE_READY(&g_NumberVarType);
    MAKE_VARIABLE_TYPE_READY(&g_DateTimeVarType);
    MAKE_VARIABLE_TYPE_READY(&g_TimestampVarType);
    MAKE_VARIABLE_TYPE_READY(&g_CLOBVarType);
    MAKE_VARIABLE_TYPE_READY(&g_BLOBVarType);
    MAKE_VARIABLE_TYPE_READY(&g_BFILEVarType);
    MAKE_VARIABLE_TYPE_READY(&g_CursorVarType);
    MAKE_VARIABLE_TYPE_READY(&g_ObjectVarType);
    MAKE_VARIABLE_TYPE_READY(&g_NCharVarType);
    MAKE_VARIABLE_TYPE_READY(&g_FixedNCharVarType);
    MAKE_VARIABLE_TYPE_READY(&g_LongNCharVarType);
    MAKE_VARIABLE_TYPE_READY(&g_NCLOBVarType);
    MAKE_VARIABLE_TYPE_READY(&g_NativeFloatVarType);
    MAKE_VARIABLE_TYPE_READY(&g_IntervalVarType);
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(12, 1)
    MAKE_VARIABLE_TYPE_READY(&g_BooleanVarType);
#endif

    // initialize module and retrieve the dictionary
#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&g_ModuleDef);
#else
    module = Py_InitModule("cx_Oracle", g_ModuleMethods);
#endif
    if (!module)
        return NULL;

    // create exception object and add it to the dictionary
    if (SetException(module, &g_WarningException,
            "Warning", CXORA_BASE_EXCEPTION) < 0)
        return NULL;
    if (SetException(module, &g_ErrorException,
            "Error", CXORA_BASE_EXCEPTION) < 0)
        return NULL;
    if (SetException(module, &g_InterfaceErrorException,
            "InterfaceError", g_ErrorException) < 0)
        return NULL;
    if (SetException(module, &g_DatabaseErrorException,
            "DatabaseError", g_ErrorException) < 0)
        return NULL;
    if (SetException(module, &g_DataErrorException,
            "DataError", g_DatabaseErrorException) < 0)
        return NULL;
    if (SetException(module, &g_OperationalErrorException,
            "OperationalError", g_DatabaseErrorException) < 0)
        return NULL;
    if (SetException(module, &g_IntegrityErrorException,
            "IntegrityError", g_DatabaseErrorException) < 0)
        return NULL;
    if (SetException(module, &g_InternalErrorException,
            "InternalError", g_DatabaseErrorException) < 0)
        return NULL;
    if (SetException(module, &g_ProgrammingErrorException,
            "ProgrammingError", g_DatabaseErrorException) < 0)
        return NULL;
    if (SetException(module, &g_NotSupportedErrorException,
            "NotSupportedError", g_DatabaseErrorException) < 0)
        return NULL;

    // set up the types that are available
    ADD_TYPE_OBJECT("Binary", &cxBinary_Type)
    ADD_TYPE_OBJECT("Connection", &g_ConnectionType)
    ADD_TYPE_OBJECT("Cursor", &g_CursorType)
    ADD_TYPE_OBJECT("Timestamp", PyDateTimeAPI->DateTimeType)
    ADD_TYPE_OBJECT("Date", PyDateTimeAPI->DateType)
    ADD_TYPE_OBJECT("SessionPool", &g_SessionPoolType)
    ADD_TYPE_OBJECT("_Error", &g_ErrorType)

    // the name "connect" is required by the DB API
    ADD_TYPE_OBJECT("connect", &g_ConnectionType)

    // create the basic data types for setting input sizes
    ADD_TYPE_OBJECT("BINARY", &g_BinaryVarType)
    ADD_TYPE_OBJECT("BFILE", &g_BFILEVarType)
    ADD_TYPE_OBJECT("BLOB", &g_BLOBVarType)
    ADD_TYPE_OBJECT("CLOB", &g_CLOBVarType)
    ADD_TYPE_OBJECT("CURSOR", &g_CursorVarType)
    ADD_TYPE_OBJECT("OBJECT", &g_ObjectVarType)
    ADD_TYPE_OBJECT("DATETIME", &g_DateTimeVarType)
    ADD_TYPE_OBJECT("FIXED_CHAR", &g_FixedCharVarType)
    ADD_TYPE_OBJECT("FIXED_NCHAR", &g_FixedNCharVarType)
    ADD_TYPE_OBJECT("FIXED_UNICODE", &g_FixedNCharVarType)
    ADD_TYPE_OBJECT("UNICODE", &g_NCharVarType)
    ADD_TYPE_OBJECT("LONG_UNICODE", &g_LongNCharVarType)
    ADD_TYPE_OBJECT("NCHAR", &g_NCharVarType)
    ADD_TYPE_OBJECT("LONG_NCHAR", &g_LongNCharVarType)
    ADD_TYPE_OBJECT("INTERVAL", &g_IntervalVarType)
    ADD_TYPE_OBJECT("LOB", &g_ExternalLobVarType)
    ADD_TYPE_OBJECT("LONG_BINARY", &g_LongBinaryVarType)
    ADD_TYPE_OBJECT("LONG_STRING", &g_LongStringVarType)
    ADD_TYPE_OBJECT("NCLOB", &g_NCLOBVarType)
    ADD_TYPE_OBJECT("NUMBER", &g_NumberVarType)
    ADD_TYPE_OBJECT("ROWID", &g_RowidVarType)
    ADD_TYPE_OBJECT("STRING", &g_StringVarType)
    ADD_TYPE_OBJECT("TIMESTAMP", &g_TimestampVarType)
    ADD_TYPE_OBJECT("NATIVE_FLOAT", &g_NativeFloatVarType)
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(12, 1)
    ADD_TYPE_OBJECT("BOOLEAN", &g_BooleanVarType)
#endif

    // create constants required by Python DB API 2.0
    if (PyModule_AddStringConstant(module, "apilevel", "2.0") < 0)
        return NULL;
    if (PyModule_AddIntConstant(module, "threadsafety", 2) < 0)
        return NULL;
    if (PyModule_AddStringConstant(module, "paramstyle", "named") < 0)
        return NULL;

    // add version and build time for easier support
    if (PyModule_AddStringConstant(module, "version",
            BUILD_VERSION_STRING) < 0)
        return NULL;
    if (PyModule_AddStringConstant(module, "__version__",
            BUILD_VERSION_STRING) < 0)
        return NULL;
    if (PyModule_AddStringConstant(module, "buildtime",
            __DATE__ " " __TIME__) < 0)
        return NULL;

    // add constants for registering callbacks
    ADD_OCI_CONSTANT(SYSDBA)
    ADD_OCI_CONSTANT(SYSOPER)
    ADD_OCI_CONSTANT(FNCODE_BINDBYNAME)
    ADD_OCI_CONSTANT(FNCODE_BINDBYPOS)
    ADD_OCI_CONSTANT(FNCODE_DEFINEBYPOS)
    ADD_OCI_CONSTANT(FNCODE_STMTEXECUTE)
    ADD_OCI_CONSTANT(FNCODE_STMTFETCH)
    ADD_OCI_CONSTANT(FNCODE_STMTPREPARE)
    ADD_OCI_CONSTANT(UCBTYPE_ENTRY)
    ADD_OCI_CONSTANT(UCBTYPE_EXIT)
    ADD_OCI_CONSTANT(UCBTYPE_REPLACE)
    ADD_OCI_CONSTANT(SPOOL_ATTRVAL_WAIT)
    ADD_OCI_CONSTANT(SPOOL_ATTRVAL_NOWAIT)
    ADD_OCI_CONSTANT(SPOOL_ATTRVAL_FORCEGET)
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
    ADD_OCI_CONSTANT(PRELIM_AUTH)
    ADD_OCI_CONSTANT(DBSHUTDOWN_ABORT)
    ADD_OCI_CONSTANT(DBSHUTDOWN_FINAL)
    ADD_OCI_CONSTANT(DBSHUTDOWN_IMMEDIATE)
    ADD_OCI_CONSTANT(DBSHUTDOWN_TRANSACTIONAL)
    ADD_OCI_CONSTANT(DBSHUTDOWN_TRANSACTIONAL_LOCAL)
    ADD_OCI_CONSTANT(EVENT_NONE)
    ADD_OCI_CONSTANT(EVENT_STARTUP)
    ADD_OCI_CONSTANT(EVENT_SHUTDOWN)
    ADD_OCI_CONSTANT(EVENT_SHUTDOWN_ANY)
    ADD_OCI_CONSTANT(EVENT_DEREG)
    ADD_OCI_CONSTANT(EVENT_OBJCHANGE)
    ADD_OCI_CONSTANT(OPCODE_ALLOPS)
    ADD_OCI_CONSTANT(OPCODE_ALLROWS)
    ADD_OCI_CONSTANT(OPCODE_INSERT)
    ADD_OCI_CONSTANT(OPCODE_UPDATE)
    ADD_OCI_CONSTANT(OPCODE_DELETE)
    ADD_OCI_CONSTANT(OPCODE_ALTER)
    ADD_OCI_CONSTANT(OPCODE_DROP)
    ADD_OCI_CONSTANT(SUBSCR_NAMESPACE_DBCHANGE)
    ADD_OCI_CONSTANT(SUBSCR_PROTO_OCI)
    ADD_OCI_CONSTANT(SUBSCR_PROTO_MAIL)
    ADD_OCI_CONSTANT(SUBSCR_PROTO_SERVER)
    ADD_OCI_CONSTANT(SUBSCR_PROTO_HTTP)
    ADD_OCI_CONSTANT(SUBSCR_QOS_RELIABLE)
    ADD_OCI_CONSTANT(SUBSCR_QOS_PAYLOAD)
    ADD_OCI_CONSTANT(SUBSCR_QOS_REPLICATE)
    ADD_OCI_CONSTANT(SUBSCR_QOS_SECURE)
    ADD_OCI_CONSTANT(SUBSCR_QOS_PURGE_ON_NTFN)
    ADD_OCI_CONSTANT(SUBSCR_QOS_MULTICBK)
#endif
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    ADD_OCI_CONSTANT(ATTR_PURITY_DEFAULT)
    ADD_OCI_CONSTANT(ATTR_PURITY_NEW)
    ADD_OCI_CONSTANT(ATTR_PURITY_SELF)
    ADD_OCI_CONSTANT(EVENT_QUERYCHANGE)
    ADD_OCI_CONSTANT(SUBSCR_CQ_QOS_QUERY)
    ADD_OCI_CONSTANT(SUBSCR_CQ_QOS_BEST_EFFORT)
    ADD_OCI_CONSTANT(SUBSCR_CQ_QOS_CLQRYCACHE)
    ADD_OCI_CONSTANT(SYSASM)
#endif
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 2)
    ADD_OCI_CONSTANT(SUBSCR_QOS_HAREG)
#endif

    return module;
}


//-----------------------------------------------------------------------------
// Start routine for the module.
//-----------------------------------------------------------------------------
#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_cx_Oracle(void)
{
    return Module_Initialize();
}
#else
void initcx_Oracle(void)
{
    Module_Initialize();
}
#endif

