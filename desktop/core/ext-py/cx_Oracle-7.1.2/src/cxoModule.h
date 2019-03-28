//-----------------------------------------------------------------------------
// Copyright (c) 2018, 2019, Oracle and/or its affiliates. All rights reserved.
//
// Licensed under BSD license (see LICENSE.txt).
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoModule.h
//   Include file for all cx_Oracle source files.
//-----------------------------------------------------------------------------

#include <Python.h>
#include <structmember.h>
#include <time.h>
#include <dpi.h>

// define integer macros/methods for Python 3.x
#ifndef PyInt_Check
#define PyInt_Check                     PyLong_Check
#define PyInt_FromLong                  PyLong_FromLong
#define PyInt_AsLong                    PyLong_AsLong
#endif

// use the bytes methods in cx_Oracle and define them as the equivalent string
// type methods as is done in Python 2.6
#ifndef PyBytes_Check
    #define PyBytes_Type                PyString_Type
    #define PyBytes_AS_STRING           PyString_AS_STRING
    #define PyBytes_GET_SIZE            PyString_GET_SIZE
    #define PyBytes_Check               PyString_Check
    #define PyBytes_FromStringAndSize   PyString_FromStringAndSize
#endif

// define string/binary types and methods
#if PY_MAJOR_VERSION >= 3
    #define CXO_BASE_EXCEPTION          NULL
    #define cxoPyTypeBinary             PyBytes_Type
    #define cxoPyTypeString             PyUnicode_Type
    #define cxoPyString_fromAscii(str) \
        PyUnicode_DecodeASCII(str, strlen(str), NULL)
    #define cxoPyString_fromEncodedString(buffer, numBytes, encoding, errors) \
        PyUnicode_Decode(buffer, numBytes, encoding, errors)
#else
    #define CXO_BASE_EXCEPTION          PyExc_StandardError
    #define cxoPyTypeBinary             PyBuffer_Type
    #define cxoPyTypeString             PyString_Type
    #define cxoPyString_fromAscii(str) \
        PyBytes_FromString(str)
    #define cxoPyString_fromEncodedString(buffer, numBytes, encoding, errors) \
        PyBytes_FromStringAndSize(buffer, numBytes)
#endif

// define macros to get the build version as a string and the driver name
#define xstr(s)                         str(s)
#define str(s)                          #s
#define CXO_BUILD_VERSION_STRING        xstr(CXO_BUILD_VERSION)
#define CXO_DRIVER_NAME                 "cx_Oracle : "CXO_BUILD_VERSION_STRING

// define macro for clearing buffers
#define cxoBuffer_clear(buf)            Py_CLEAR((buf)->obj)


//-----------------------------------------------------------------------------
// Forward Declarations
//-----------------------------------------------------------------------------
typedef struct cxoBuffer cxoBuffer;
typedef struct cxoError cxoError;
typedef struct cxoConnection cxoConnection;
typedef struct cxoCursor cxoCursor;
typedef struct cxoDeqOptions cxoDeqOptions;
typedef struct cxoEnqOptions cxoEnqOptions;
typedef struct cxoFuture cxoFuture;
typedef struct cxoLob cxoLob;
typedef struct cxoMessage cxoMessage;
typedef struct cxoMessageQuery cxoMessageQuery;
typedef struct cxoMessageRow cxoMessageRow;
typedef struct cxoMessageTable cxoMessageTable;
typedef struct cxoMsgProps cxoMsgProps;
typedef struct cxoObject cxoObject;
typedef struct cxoObjectAttr cxoObjectAttr;
typedef struct cxoObjectType cxoObjectType;
typedef struct cxoSessionPool cxoSessionPool;
typedef struct cxoSodaCollection cxoSodaCollection;
typedef struct cxoSodaDatabase cxoSodaDatabase;
typedef struct cxoSodaDoc cxoSodaDoc;
typedef struct cxoSodaDocCursor cxoSodaDocCursor;
typedef struct cxoSodaOperation cxoSodaOperation;
typedef struct cxoSubscr cxoSubscr;
typedef struct cxoVar cxoVar;
typedef struct cxoVarType cxoVarType;


//-----------------------------------------------------------------------------
// Globals
//-----------------------------------------------------------------------------

// exception objects
extern PyObject *cxoWarningException;
extern PyObject *cxoErrorException;
extern PyObject *cxoInterfaceErrorException;
extern PyObject *cxoDatabaseErrorException;
extern PyObject *cxoDataErrorException;
extern PyObject *cxoOperationalErrorException;
extern PyObject *cxoIntegrityErrorException;
extern PyObject *cxoInternalErrorException;
extern PyObject *cxoProgrammingErrorException;
extern PyObject *cxoNotSupportedErrorException;

// type objects
extern PyTypeObject cxoPyTypeBfileVar;
extern PyTypeObject cxoPyTypeBinaryVar;
extern PyTypeObject cxoPyTypeBlobVar;
extern PyTypeObject cxoPyTypeBooleanVar;
extern PyTypeObject cxoPyTypeClobVar;
extern PyTypeObject cxoPyTypeConnection;
extern PyTypeObject cxoPyTypeCursor;
extern PyTypeObject cxoPyTypeCursorVar;
extern PyTypeObject cxoPyTypeDateTimeVar;
extern PyTypeObject cxoPyTypeDeqOptions;
extern PyTypeObject cxoPyTypeEnqOptions;
extern PyTypeObject cxoPyTypeError;
extern PyTypeObject cxoPyTypeFixedCharVar;
extern PyTypeObject cxoPyTypeFixedNcharVar;
extern PyTypeObject cxoPyTypeFuture;
extern PyTypeObject cxoPyTypeIntervalVar;
extern PyTypeObject cxoPyTypeLob;
extern PyTypeObject cxoPyTypeLongBinaryVar;
extern PyTypeObject cxoPyTypeLongStringVar;
extern PyTypeObject cxoPyTypeMsgProps;
extern PyTypeObject cxoPyTypeMessage;
extern PyTypeObject cxoPyTypeMessageQuery;
extern PyTypeObject cxoPyTypeMessageRow;
extern PyTypeObject cxoPyTypeMessageTable;
extern PyTypeObject cxoPyTypeNativeFloatVar;
extern PyTypeObject cxoPyTypeNativeIntVar;
extern PyTypeObject cxoPyTypeNcharVar;
extern PyTypeObject cxoPyTypeNclobVar;
extern PyTypeObject cxoPyTypeNumberVar;
extern PyTypeObject cxoPyTypeObject;
extern PyTypeObject cxoPyTypeObjectAttr;
extern PyTypeObject cxoPyTypeObjectType;
extern PyTypeObject cxoPyTypeObjectVar;
extern PyTypeObject cxoPyTypeRowidVar;
extern PyTypeObject cxoPyTypeSessionPool;
extern PyTypeObject cxoPyTypeSodaCollection;
extern PyTypeObject cxoPyTypeSodaDatabase;
extern PyTypeObject cxoPyTypeSodaDoc;
extern PyTypeObject cxoPyTypeSodaDocCursor;
extern PyTypeObject cxoPyTypeSodaOperation;
extern PyTypeObject cxoPyTypeStringVar;
extern PyTypeObject cxoPyTypeSubscr;
extern PyTypeObject cxoPyTypeTimestampVar;

// datetime types
extern PyTypeObject *cxoPyTypeDate;
extern PyTypeObject *cxoPyTypeDateTime;

// JSON dump and load functions for use with SODA
extern PyObject *cxoJsonDumpFunction;
extern PyObject *cxoJsonLoadFunction;

// ODPI-C context and version information
extern dpiContext *cxoDpiContext;
extern dpiVersionInfo cxoClientVersionInfo;

// future object
extern cxoFuture *cxoFutureObj;


//-----------------------------------------------------------------------------
// Transforms
//-----------------------------------------------------------------------------
typedef enum {
    CXO_TRANSFORM_NONE = 0,
    CXO_TRANSFORM_BINARY,
    CXO_TRANSFORM_BFILE,
    CXO_TRANSFORM_BLOB,
    CXO_TRANSFORM_BOOLEAN,
    CXO_TRANSFORM_CLOB,
    CXO_TRANSFORM_CURSOR,
    CXO_TRANSFORM_DATE,
    CXO_TRANSFORM_DATETIME,
    CXO_TRANSFORM_DECIMAL,
    CXO_TRANSFORM_FIXED_CHAR,
    CXO_TRANSFORM_FIXED_NCHAR,
    CXO_TRANSFORM_FLOAT,
    CXO_TRANSFORM_INT,
    CXO_TRANSFORM_LONG_BINARY,
    CXO_TRANSFORM_LONG_STRING,
    CXO_TRANSFORM_NATIVE_DOUBLE,
    CXO_TRANSFORM_NATIVE_FLOAT,
    CXO_TRANSFORM_NATIVE_INT,
    CXO_TRANSFORM_NCLOB,
    CXO_TRANSFORM_NSTRING,
    CXO_TRANSFORM_OBJECT,
    CXO_TRANSFORM_ROWID,
    CXO_TRANSFORM_STRING,
    CXO_TRANSFORM_TIMEDELTA,
    CXO_TRANSFORM_TIMESTAMP,
    CXO_TRANSFORM_TIMESTAMP_LTZ,
    CXO_TRANSFORM_UNSUPPORTED
} cxoTransformNum;


//-----------------------------------------------------------------------------
// Structures
//-----------------------------------------------------------------------------
struct cxoBuffer {
    const char *ptr;
    uint32_t numCharacters;
    uint32_t size;
    PyObject *obj;
};

struct cxoError {
    PyObject_HEAD
    long code;
    unsigned offset;
    PyObject *message;
    PyObject *context;
    char isRecoverable;
};

struct cxoConnection {
    PyObject_HEAD
    dpiConn *handle;
    cxoSessionPool *sessionPool;
    PyObject *inputTypeHandler;
    PyObject *outputTypeHandler;
    PyObject *username;
    PyObject *dsn;
    PyObject *version;
    PyObject *tag;
    dpiEncodingInfo encodingInfo;
    int autocommit;
};

struct cxoCursor {
    PyObject_HEAD
    dpiStmt *handle;
    dpiStmtInfo stmtInfo;
    cxoConnection *connection;
    PyObject *statement;
    PyObject *statementTag;
    PyObject *bindVariables;
    PyObject *fetchVariables;
    PyObject *rowFactory;
    PyObject *inputTypeHandler;
    PyObject *outputTypeHandler;
    uint32_t arraySize;
    uint32_t bindArraySize;
    uint32_t fetchArraySize;
    int setInputSizes;
    uint64_t rowCount;
    uint32_t fetchBufferRowIndex;
    uint32_t numRowsInFetchBuffer;
    int moreRowsToFetch;
    int isScrollable;
    int fixupRefCursor;
    int isOpen;
};

struct cxoDeqOptions {
    PyObject_HEAD
    dpiDeqOptions *handle;
    const char *encoding;
};

struct cxoEnqOptions {
    PyObject_HEAD
    dpiEnqOptions *handle;
    const char *encoding;
};

struct cxoFuture {
    PyObject_HEAD
};

struct cxoLob {
    PyObject_HEAD
    cxoConnection *connection;
    dpiOracleTypeNum oracleTypeNum;
    dpiLob *handle;
};

struct cxoMessage {
    PyObject_HEAD
    cxoSubscr *subscription;
    dpiEventType type;
    PyObject *dbname;
    PyObject *txId;
    PyObject *tables;
    PyObject *queries;
    PyObject *queueName;
    PyObject *consumerName;
    int registered;
};

struct cxoMessageQuery {
    PyObject_HEAD
    uint64_t id;
    dpiOpCode operation;
    PyObject *tables;
};

struct cxoMessageRow {
    PyObject_HEAD
    PyObject *rowid;
    dpiOpCode operation;
};

struct cxoMessageTable {
    PyObject_HEAD
    PyObject *name;
    PyObject *rows;
    dpiOpCode operation;
};

struct cxoMsgProps {
    PyObject_HEAD
    dpiMsgProps *handle;
    const char *encoding;
};

struct cxoObject {
    PyObject_HEAD
    cxoObjectType *objectType;
    dpiObject *handle;
};

struct cxoObjectAttr {
    PyObject_HEAD
    PyObject *name;
    dpiObjectAttr *handle;
    dpiOracleTypeNum oracleTypeNum;
    cxoTransformNum transformNum;
    cxoObjectType *type;
};

struct cxoObjectType {
    PyObject_HEAD
    dpiObjectType *handle;
    PyObject *schema;
    PyObject *name;
    PyObject *attributes;
    PyObject *attributesByName;
    cxoConnection *connection;
    dpiOracleTypeNum elementOracleTypeNum;
    cxoTransformNum elementTransformNum;
    PyObject *elementType;
    char isCollection;
};

struct cxoSessionPool {
    PyObject_HEAD
    dpiPool *handle;
    uint32_t minSessions;
    uint32_t maxSessions;
    uint32_t sessionIncrement;
    uint32_t cacheSize;
    dpiEncodingInfo encodingInfo;
    int homogeneous;
    int externalAuth;
    PyObject *username;
    PyObject *dsn;
    PyObject *name;
    PyObject *sessionCallback;
    PyTypeObject *connectionType;
};

struct cxoSodaCollection {
    PyObject_HEAD
    dpiSodaColl *handle;
    cxoSodaDatabase *db;
    PyObject *name;
};

struct cxoSodaDatabase {
    PyObject_HEAD
    dpiSodaDb *handle;
    cxoConnection *connection;
};

struct cxoSodaDoc {
    PyObject_HEAD
    cxoSodaDatabase *db;
    dpiSodaDoc *handle;
};

struct cxoSodaDocCursor {
    PyObject_HEAD
    cxoSodaDatabase *db;
    dpiSodaDocCursor *handle;
};

struct cxoSodaOperation {
    PyObject_HEAD
    cxoSodaCollection *coll;
    dpiSodaOperOptions options;
    uint32_t numKeyBuffers;
    cxoBuffer *keyBuffers;
    cxoBuffer keyBuffer;
    cxoBuffer versionBuffer;
    cxoBuffer filterBuffer;
};


struct cxoSubscr {
    PyObject_HEAD
    dpiSubscr *handle;
    cxoConnection *connection;
    PyObject *callback;
    uint32_t namespace;
    PyObject *name;
    uint32_t protocol;
    PyObject *ipAddress;
    uint32_t port;
    uint32_t timeout;
    uint32_t operations;
    uint32_t qos;
    uint8_t groupingClass;
    uint32_t groupingValue;
    uint8_t groupingType;
    uint64_t id;
};

struct cxoVar {
    PyObject_HEAD
    dpiVar *handle;
    dpiData *data;
    cxoConnection *connection;
    PyObject *inConverter;
    PyObject *outConverter;
    cxoObjectType *objectType;
    const char *encodingErrors;
    uint32_t allocatedElements;
    uint32_t size;
    uint32_t bufferSize;
    int isArray;
    int isValueSet;
    int getReturnedData;
    cxoVarType *type;
};

struct cxoVarType {
    cxoTransformNum transformNum;
    PyTypeObject *pythonType;
    uint32_t size;
};


//-----------------------------------------------------------------------------
// Functions
//-----------------------------------------------------------------------------
int cxoBuffer_fromObject(cxoBuffer *buf, PyObject *obj, const char *encoding);
int cxoBuffer_init(cxoBuffer *buf);

int cxoConnection_getSodaFlags(cxoConnection *conn, uint32_t *flags);
int cxoConnection_isConnected(cxoConnection *conn);

int cxoCursor_performBind(cxoCursor *cursor);
int cxoCursor_setBindVariables(cxoCursor *cursor, PyObject *parameters,
        unsigned numElements, unsigned arrayPos, int deferTypeAssignment);

cxoDeqOptions *cxoDeqOptions_new(cxoConnection *connection);

cxoEnqOptions *cxoEnqOptions_new(cxoConnection *connection);

cxoError *cxoError_newFromInfo(dpiErrorInfo *errorInfo);
int cxoError_raiseAndReturnInt(void);
PyObject *cxoError_raiseAndReturnNull(void);
int cxoError_raiseFromInfo(dpiErrorInfo *errorInfo);
PyObject *cxoError_raiseFromString(PyObject *exceptionType,
        const char *message);

PyObject *cxoLob_new(cxoConnection *connection, dpiOracleTypeNum oracleTypeNum,
        dpiLob *handle);

cxoMsgProps *cxoMsgProps_new(cxoConnection*);

int cxoObject_internalExtend(cxoObject *obj, PyObject *sequence);
PyObject *cxoObject_new(cxoObjectType *objectType, dpiObject *handle);

cxoObjectAttr *cxoObjectAttr_new(cxoConnection *connection,
        dpiObjectAttr *handle);

cxoObjectType *cxoObjectType_new(cxoConnection *connection,
        dpiObjectType *handle);
cxoObjectType *cxoObjectType_newByName(cxoConnection *connection,
        PyObject *name);

cxoSodaCollection *cxoSodaCollection_new(cxoSodaDatabase *db,
        dpiSodaColl *handle);

cxoSodaDatabase *cxoSodaDatabase_new(cxoConnection *connection);

cxoSodaDoc *cxoSodaDoc_new(cxoSodaDatabase *db, dpiSodaDoc *handle);

cxoSodaDocCursor *cxoSodaDocCursor_new(cxoSodaDatabase *db,
        dpiSodaDocCursor *handle);

cxoSodaOperation *cxoSodaOperation_new(cxoSodaCollection *collection);

void cxoSubscr_callback(cxoSubscr *subscr, dpiSubscrMessage *message);

PyObject *cxoTransform_dateFromTicks(PyObject *args);
int cxoTransform_fromPython(cxoTransformNum transformNum, PyObject *pyValue,
        dpiDataBuffer *dbValue, cxoBuffer *buffer, const char *encoding,
        const char *nencoding, cxoVar *var, uint32_t arrayPos);
cxoTransformNum cxoTransform_getNumFromDataTypeInfo(dpiDataTypeInfo *info);
cxoTransformNum cxoTransform_getNumFromType(PyTypeObject *type);
cxoTransformNum cxoTransform_getNumFromValue(PyObject *value, int plsql);
void cxoTransform_getTypeInfo(cxoTransformNum transformNum,
        dpiOracleTypeNum *oracleTypeNum, dpiNativeTypeNum *nativeTypeNum);
int cxoTransform_init(void);
PyObject *cxoTransform_timestampFromTicks(PyObject *args);
PyObject *cxoTransform_toPython(cxoTransformNum transformNum, 
        cxoConnection *connection, cxoObjectType *objType,
        dpiDataBuffer *dbValue, const char *encodingErrors);

PyObject *cxoUtils_formatString(const char *format, PyObject *args);
const char *cxoUtils_getAdjustedEncoding(const char *encoding);
int cxoUtils_getBooleanValue(PyObject *obj, int defaultValue, int *value);
int cxoUtils_getModuleAndName(PyTypeObject *type, PyObject **module,
        PyObject **name);
int cxoUtils_initializeDPI(void);
int cxoUtils_processJsonArg(PyObject *arg, cxoBuffer *buffer);
int cxoUtils_processSodaDocArg(cxoSodaDatabase *db, PyObject *arg,
        cxoSodaDoc **doc);

cxoVarType *cxoVarType_fromDataTypeInfo(dpiDataTypeInfo *info);
cxoVarType *cxoVarType_fromPythonType(PyObject *type, cxoObjectType **objType);
cxoVarType *cxoVarType_fromPythonValue(PyObject *value, int *isArray,
        Py_ssize_t *size, Py_ssize_t *numElements, int plsql);

int cxoVar_bind(cxoVar *var, cxoCursor *cursor, PyObject *name, uint32_t pos);
int cxoVar_check(PyObject *object);
PyObject *cxoVar_getSingleValue(cxoVar *var, dpiData *data, uint32_t arrayPos);
PyObject *cxoVar_getValue(cxoVar *var, uint32_t arrayPos);
cxoVar *cxoVar_new(cxoCursor *cursor, Py_ssize_t numElements, cxoVarType *type,
        Py_ssize_t size, int isArray, cxoObjectType *objType);
cxoVar *cxoVar_newByType(cxoCursor *cursor, PyObject *value,
        uint32_t numElements);
cxoVar *cxoVar_newByValue(cxoCursor *cursor, PyObject *value,
        Py_ssize_t numElements);
int cxoVar_setValue(cxoVar *var, uint32_t arrayPos, PyObject *value);

