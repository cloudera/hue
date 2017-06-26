//-----------------------------------------------------------------------------
// Connection.c
//   Definition of the Python type OracleConnection.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// structure for the Python type "Connection"
//-----------------------------------------------------------------------------
typedef struct {
    PyObject_HEAD
    OCISvcCtx *handle;
    OCIServer *serverHandle;
    OCISession *sessionHandle;
    udt_Environment *environment;
    udt_SessionPool *sessionPool;
    PyObject *inputTypeHandler;
    PyObject *outputTypeHandler;
    PyObject *username;
    PyObject *dsn;
    PyObject *version;
    ub4 commitMode;
    int autocommit;
    int release;
    int attached;
} udt_Connection;


//-----------------------------------------------------------------------------
// constants for the OCI attributes
//-----------------------------------------------------------------------------
static ub4 gc_ClientIdentifierAttribute = OCI_ATTR_CLIENT_IDENTIFIER;
static ub4 gc_ModuleAttribute = OCI_ATTR_MODULE;
static ub4 gc_ActionAttribute = OCI_ATTR_ACTION;
static ub4 gc_ClientInfoAttribute = OCI_ATTR_CLIENT_INFO;

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
static ub4 gc_CurrentSchemaAttribute = OCI_ATTR_CURRENT_SCHEMA;
#endif


//-----------------------------------------------------------------------------
// functions for the Python type "Connection"
//-----------------------------------------------------------------------------
static void Connection_Free(udt_Connection*);
static PyObject *Connection_New(PyTypeObject*, PyObject*, PyObject*);
static int Connection_Init(udt_Connection*, PyObject*, PyObject*);
static PyObject *Connection_Repr(udt_Connection*);
static PyObject *Connection_Close(udt_Connection*, PyObject*);
static PyObject *Connection_Commit(udt_Connection*, PyObject*);
static PyObject *Connection_Begin(udt_Connection*, PyObject*);
static PyObject *Connection_Prepare(udt_Connection*, PyObject*);
static PyObject *Connection_Rollback(udt_Connection*, PyObject*);
static PyObject *Connection_NewCursor(udt_Connection*, PyObject*);
static PyObject *Connection_Cancel(udt_Connection*, PyObject*);
static PyObject *Connection_RegisterCallback(udt_Connection*, PyObject*);
static PyObject *Connection_UnregisterCallback(udt_Connection*, PyObject*);
static PyObject *Connection_GetVersion(udt_Connection*, void*);
static PyObject *Connection_GetEncoding(udt_Connection*, void*);
static PyObject *Connection_GetNationalEncoding(udt_Connection*, void*);
static PyObject *Connection_GetMaxBytesPerCharacter(udt_Connection*, void*);
static PyObject *Connection_ContextManagerEnter(udt_Connection*, PyObject*);
static PyObject *Connection_ContextManagerExit(udt_Connection*, PyObject*);
static PyObject *Connection_ChangePasswordExternal(udt_Connection*, PyObject*);
static PyObject *Connection_GetStmtCacheSize(udt_Connection*, void*);
static int Connection_SetStmtCacheSize(udt_Connection*, PyObject*, void*);
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
static PyObject *Connection_GetOCIAttr(udt_Connection*, ub4*);
#endif
static int Connection_SetOCIAttr(udt_Connection*, PyObject*, ub4*);
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
#if !defined(AIX5) || ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
static PyObject *Connection_Ping(udt_Connection*, PyObject*);
#endif
static PyObject *Connection_Shutdown(udt_Connection*, PyObject*, PyObject*);
static PyObject *Connection_Startup(udt_Connection*, PyObject*, PyObject*);
static PyObject *Connection_Subscribe(udt_Connection*, PyObject*, PyObject*);
#endif


//-----------------------------------------------------------------------------
// declaration of methods for Python type "Connection"
//-----------------------------------------------------------------------------
static PyMethodDef g_ConnectionMethods[] = {
    { "cursor", (PyCFunction) Connection_NewCursor, METH_NOARGS },
    { "commit", (PyCFunction) Connection_Commit, METH_NOARGS },
    { "rollback", (PyCFunction) Connection_Rollback, METH_NOARGS },
    { "begin", (PyCFunction) Connection_Begin, METH_VARARGS },
    { "prepare", (PyCFunction) Connection_Prepare, METH_NOARGS },
    { "close", (PyCFunction) Connection_Close, METH_NOARGS },
    { "cancel", (PyCFunction) Connection_Cancel, METH_NOARGS },
    { "register", (PyCFunction) Connection_RegisterCallback, METH_VARARGS },
    { "unregister", (PyCFunction) Connection_UnregisterCallback, METH_VARARGS },
    { "__enter__", (PyCFunction) Connection_ContextManagerEnter, METH_NOARGS },
    { "__exit__", (PyCFunction) Connection_ContextManagerExit, METH_VARARGS },
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
#if !defined(AIX5) || ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    { "ping", (PyCFunction) Connection_Ping, METH_NOARGS },
#endif
    { "shutdown", (PyCFunction) Connection_Shutdown,
            METH_VARARGS | METH_KEYWORDS},
    { "startup", (PyCFunction) Connection_Startup,
            METH_VARARGS | METH_KEYWORDS},
    { "subscribe", (PyCFunction) Connection_Subscribe,
            METH_VARARGS | METH_KEYWORDS},
#endif
    { "changepassword", (PyCFunction) Connection_ChangePasswordExternal,
            METH_VARARGS },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of members for Python type "Connection"
//-----------------------------------------------------------------------------
static PyMemberDef g_ConnectionMembers[] = {
    { "username", T_OBJECT, offsetof(udt_Connection, username), READONLY },
    { "dsn", T_OBJECT, offsetof(udt_Connection, dsn), READONLY },
    { "tnsentry", T_OBJECT, offsetof(udt_Connection, dsn), READONLY },
    { "autocommit", T_INT, offsetof(udt_Connection, autocommit), 0 },
    { "inputtypehandler", T_OBJECT,
            offsetof(udt_Connection, inputTypeHandler), 0 },
    { "outputtypehandler", T_OBJECT,
            offsetof(udt_Connection, outputTypeHandler), 0 },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of calculated members for Python type "Connection"
//-----------------------------------------------------------------------------
static PyGetSetDef g_ConnectionCalcMembers[] = {
    { "version", (getter) Connection_GetVersion, 0, 0, 0 },
    { "encoding", (getter) Connection_GetEncoding, 0, 0, 0 },
    { "nencoding", (getter) Connection_GetNationalEncoding, 0, 0, 0 },
    { "maxBytesPerCharacter", (getter) Connection_GetMaxBytesPerCharacter,
            0, 0, 0 },
    { "stmtcachesize", (getter) Connection_GetStmtCacheSize,
            (setter) Connection_SetStmtCacheSize, 0, 0 },
    { "module", 0, (setter) Connection_SetOCIAttr, 0, &gc_ModuleAttribute },
    { "action", 0, (setter) Connection_SetOCIAttr, 0, &gc_ActionAttribute },
    { "clientinfo", 0, (setter) Connection_SetOCIAttr, 0,
            &gc_ClientInfoAttribute },
    { "client_identifier", 0, (setter) Connection_SetOCIAttr, 0,
            &gc_ClientIdentifierAttribute },
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
    { "current_schema", (getter) Connection_GetOCIAttr,
            (setter) Connection_SetOCIAttr, 0, &gc_CurrentSchemaAttribute },
#endif
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of Python type "Connection"
//-----------------------------------------------------------------------------
static PyTypeObject g_ConnectionType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.Connection",             // tp_name
    sizeof(udt_Connection),             // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) Connection_Free,       // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) Connection_Repr,         // tp_repr
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
    g_ConnectionMethods,                // tp_methods
    g_ConnectionMembers,                // tp_members
    g_ConnectionCalcMembers,            // tp_getset
    0,                                  // tp_base
    0,                                  // tp_dict
    0,                                  // tp_descr_get
    0,                                  // tp_descr_set
    0,                                  // tp_dictoffset
    (initproc) Connection_Init,         // tp_init
    0,                                  // tp_alloc
    (newfunc) Connection_New,           // tp_new
    0,                                  // tp_free
    0,                                  // tp_is_gc
    0                                   // tp_bases
};


//-----------------------------------------------------------------------------
// Connection_IsConnected()
//   Determines if the connection object is connected to the database. If not,
// a Python exception is raised.
//-----------------------------------------------------------------------------
static int Connection_IsConnected(
    udt_Connection *self)               // connection to check
{
    if (!self->handle) {
        PyErr_SetString(g_InterfaceErrorException, "not connected");
        return -1;
    }
    return 0;
}


//-----------------------------------------------------------------------------
// Connection_GetConnection()
//   Get a connection using the OCISessionGet() interface rather than using
// the low level interface for connecting.
//-----------------------------------------------------------------------------
static int Connection_GetConnection(
    udt_Connection *self,               // connection
    udt_SessionPool *pool,              // pool to acquire connection from
    PyObject *passwordObj,              // password
    PyObject *cclassObj,                // connection class (DRCP)
    ub4 purity)                         // purity (DRCP)
{
    udt_Environment *environment;
    int externalAuth, proxyAuth;
    udt_Buffer buffer;
    OCIAuthInfo *authInfo;
    PyObject *dbNameObj;
    boolean found;
    sword status;
    ub4 mode;

    // set things up for the call to acquire a session
    authInfo = NULL;
    externalAuth = proxyAuth = 0;
    if (pool) {
        environment = pool->environment;
        dbNameObj = pool->name;
        mode = OCI_SESSGET_SPOOL;
        externalAuth = pool->externalAuth;
        if (!pool->homogeneous && pool->username && self->username) {
            proxyAuth = PyObject_RichCompareBool(self->username,
                    pool->username, Py_NE);
            if (proxyAuth < 0)
                return -1;
            mode = mode | OCI_SESSGET_CREDPROXY;
        }
    } else {
        environment = self->environment;
        dbNameObj = self->dsn;
        mode = OCI_SESSGET_STMTCACHE;
    }

    // set up authorization handle, if needed
    if (!pool || cclassObj || proxyAuth) {

        // create authorization handle
        status = OCIHandleAlloc(environment->handle, (dvoid*) &authInfo,
                OCI_HTYPE_AUTHINFO, 0, NULL);
        if (Environment_CheckForError(environment, status,
                "Connection_GetConnection(): allocate handle") < 0)
            return -1;

        // set the user name, if applicable
        externalAuth = 1;
        if (cxBuffer_FromObject(&buffer, self->username,
                self->environment->encoding) < 0)
            return -1;
        if (buffer.size > 0) {
            externalAuth = 0;
            status = OCIAttrSet(authInfo, OCI_HTYPE_AUTHINFO,
                    (text*) buffer.ptr, buffer.size, OCI_ATTR_USERNAME,
                    environment->errorHandle);
            if (Environment_CheckForError(environment, status,
                    "Connection_GetConnection(): set user name") < 0) {
                cxBuffer_Clear(&buffer);
                return -1;
            }
        }
        cxBuffer_Clear(&buffer);

        // set the password, if applicable
        if (cxBuffer_FromObject(&buffer, passwordObj,
                self->environment->encoding) < 0)
            return -1;
        if (buffer.size > 0) {
            externalAuth = 0;
            status = OCIAttrSet(authInfo, OCI_HTYPE_AUTHINFO,
                    (text*) buffer.ptr, buffer.size, OCI_ATTR_PASSWORD,
                    environment->errorHandle);
            if (Environment_CheckForError(environment, status,
                    "Connection_GetConnection(): set password") < 0) {
                cxBuffer_Clear(&buffer);
                return -1;
            }
        }
        cxBuffer_Clear(&buffer);

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
        // set the connection class, if applicable
        if (cxBuffer_FromObject(&buffer, cclassObj,
                self->environment->encoding) < 0)
            return -1;
        if (buffer.size > 0) {
            status = OCIAttrSet(authInfo, OCI_HTYPE_AUTHINFO,
                    (text*) buffer.ptr, buffer.size, OCI_ATTR_CONNECTION_CLASS,
                    environment->errorHandle);
            if (Environment_CheckForError(environment, status,
                    "Connection_GetConnection(): set connection class") < 0) {
                cxBuffer_Clear(&buffer);
                return -1;
            }
        }
        cxBuffer_Clear(&buffer);

        // set the purity, if applicable
        if (purity != OCI_ATTR_PURITY_DEFAULT) {
            status = OCIAttrSet(authInfo, OCI_HTYPE_AUTHINFO, &purity,
                    sizeof(purity), OCI_ATTR_PURITY,
                    environment->errorHandle);
            if (Environment_CheckForError(environment, status,
                    "Connection_GetConnection(): set purity") < 0)
                return -1;
        }
#endif
    }

    // external auth requested (no username/password or specified via pool)
    if (externalAuth)
        mode |= OCI_SESSGET_CREDEXT;

    // acquire the new session
    if (cxBuffer_FromObject(&buffer, dbNameObj,
            self->environment->encoding) < 0)
        return -1;
    Py_BEGIN_ALLOW_THREADS
    status = OCISessionGet(environment->handle, environment->errorHandle,
            &self->handle, authInfo, (text*) buffer.ptr, buffer.size, NULL, 0,
            NULL, NULL, &found, mode);
    Py_END_ALLOW_THREADS
    cxBuffer_Clear(&buffer);
    if (Environment_CheckForError(environment, status,
            "Connection_GetConnection(): get connection") < 0)
        return -1;

    // eliminate the authorization handle immediately, if applicable
    if (authInfo)
        OCIHandleFree(authInfo, OCI_HTYPE_AUTHINFO);

    // copy members in the case where a pool is being used
    if (pool) {
        if (!proxyAuth) {
            Py_INCREF(pool->username);
            self->username = pool->username;
        }
        Py_INCREF(pool->dsn);
        self->dsn = pool->dsn;
        Py_INCREF(pool);
        self->sessionPool = pool;
    }

    self->release = 1;
    return 0;
}


#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
//-----------------------------------------------------------------------------
// Connection_GetOCIAttr()
//   Get the value of the OCI attribute.
//-----------------------------------------------------------------------------
static PyObject *Connection_GetOCIAttr(
    udt_Connection *self,               // connection to set
    ub4 *attribute)                     // OCI attribute type
{
    OCISession *sessionHandle;
    udt_Buffer buffer;
    ub4 bufferSize;
    sword status;

    // make sure connection is connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // acquire the session handle
    status = OCIAttrGet(self->handle, OCI_HTYPE_SVCCTX,
            (dvoid**) &sessionHandle, 0, OCI_ATTR_SESSION,
            self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_GetOCIAttr(): determine session handle") < 0)
        return NULL;

    // get the value from the OCI
    status = OCIAttrGet(sessionHandle, OCI_HTYPE_SESSION,
            (text**) &buffer.ptr, &bufferSize, *attribute,
            self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_GetOCIAttr()") < 0)
        return NULL;

    buffer.size = bufferSize;
    return cxString_FromEncodedString(buffer.ptr, buffer.size,
            self->environment->encoding);
}
#endif


//-----------------------------------------------------------------------------
// Connection_SetOCIAttr()
//   Set the value of the OCI attribute.
//-----------------------------------------------------------------------------
static int Connection_SetOCIAttr(
    udt_Connection *self,               // connection to set
    PyObject *value,                    // value to set
    ub4 *attribute)                     // OCI attribute type
{
    OCISession *sessionHandle;
    udt_Buffer buffer;
    sword status;

    // make sure connection is connected
    if (Connection_IsConnected(self) < 0)
        return -1;

    // acquire the session handle
    status = OCIAttrGet(self->handle, OCI_HTYPE_SVCCTX,
            (dvoid**) &sessionHandle, 0, OCI_ATTR_SESSION,
            self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_SetOCIAttr(): determine session handle") < 0)
        return -1;

    // set the value in the OCI
    if (cxBuffer_FromObject(&buffer, value, self->environment->encoding))
        return -1;
    status = OCIAttrSet(sessionHandle, OCI_HTYPE_SESSION, (text*) buffer.ptr,
            buffer.size, *attribute, self->environment->errorHandle);
    cxBuffer_Clear(&buffer);
    if (Environment_CheckForError(self->environment, status,
            "Connection_SetOCIAttr(): set value") < 0)
        return -1;
    return 0;
}


//-----------------------------------------------------------------------------
// Connection_Attach()
//   Attach to an existing connection.
//-----------------------------------------------------------------------------
static int Connection_Attach(
    udt_Connection *self,               // connection
    OCISvcCtx *handle)                  // handle of connection to attach to
{
    OCISession *sessionHandle;
    OCIServer *serverHandle;
    sword status;

    // acquire the server handle
    status = OCIAttrGet(handle, OCI_HTYPE_SVCCTX, (dvoid**) &serverHandle, 0,
            OCI_ATTR_SERVER, self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Attach(): determine server handle") < 0)
        return -1;

    // acquire the session handle
    status = OCIAttrGet(handle, OCI_HTYPE_SVCCTX, (dvoid**) &sessionHandle, 0,
            OCI_ATTR_SESSION, self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Attach(): determine session handle") < 0)
        return -1;

    // allocate the service context handle
    status = OCIHandleAlloc(self->environment->handle,
            (dvoid*) &self->handle, OCI_HTYPE_SVCCTX, 0, 0);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Attach(): allocate service context handle") < 0)
        return -1;

    // set attribute for server handle
    status = OCIAttrSet(self->handle, OCI_HTYPE_SVCCTX, serverHandle, 0,
            OCI_ATTR_SERVER, self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Attach(): set server handle") < 0)
        return -1;

    // set attribute for session handle
    status = OCIAttrSet(self->handle, OCI_HTYPE_SVCCTX, sessionHandle, 0,
            OCI_ATTR_SESSION, self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Attach(): set session handle") < 0)
        return -1;

    self->attached = 1;
    return 0;
}


//-----------------------------------------------------------------------------
// Connection_ChangePassword()
//   Change the password for the given connection.
//-----------------------------------------------------------------------------
static int Connection_ChangePassword(
    udt_Connection *self,               // connection
    PyObject *oldPasswordObj,           // old password
    PyObject *newPasswordObj)           // new password
{
    udt_Buffer usernameBuffer, oldPasswordBuffer, newPasswordBuffer;
    sword status;

    if (cxBuffer_FromObject(&usernameBuffer, self->username,
            self->environment->encoding) < 0)
        return -1;
    if (cxBuffer_FromObject(&oldPasswordBuffer, oldPasswordObj,
            self->environment->encoding) < 0) {
        cxBuffer_Clear(&usernameBuffer);
        return -1;
    }
    if (cxBuffer_FromObject(&newPasswordBuffer, newPasswordObj,
            self->environment->encoding) < 0) {
        cxBuffer_Clear(&usernameBuffer);
        cxBuffer_Clear(&oldPasswordBuffer);
        return -1;
    }

    // begin the session
    Py_BEGIN_ALLOW_THREADS
    status = OCIPasswordChange(self->handle, self->environment->errorHandle,
            (text*) usernameBuffer.ptr, usernameBuffer.size,
            (text*) oldPasswordBuffer.ptr, oldPasswordBuffer.size,
            (text*) newPasswordBuffer.ptr, newPasswordBuffer.size,
            OCI_AUTH);
    Py_END_ALLOW_THREADS
    cxBuffer_Clear(&usernameBuffer);
    cxBuffer_Clear(&oldPasswordBuffer);
    cxBuffer_Clear(&newPasswordBuffer);
    if (Environment_CheckForError(self->environment, status,
            "Connection_ChangePassword(): change password") < 0)
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// Connection_ChangePasswordExternal()
//   Change the password for the given connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_ChangePasswordExternal(
    udt_Connection *self,               // connection
    PyObject *args)                     // arguments
{
    PyObject *oldPasswordObj, *newPasswordObj;

    // parse the arguments
    if (!PyArg_ParseTuple(args, "O!O!", cxString_Type, &oldPasswordObj,
            cxString_Type, &newPasswordObj))
        return NULL;

    if (Connection_ChangePassword(self, oldPasswordObj, newPasswordObj) < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_Connect()
//   Create a new connection object by connecting to the database.
//-----------------------------------------------------------------------------
static int Connection_Connect(
    udt_Connection *self,               // connection
    ub4 mode,                           // mode to connect as
    int twophase,                       // allow two phase commit?
    PyObject *passwordObj,              // password
    PyObject *newPasswordObj,           // new password (if desired)
    PyObject *moduleObj,                // session "module" value
    PyObject *actionObj,                // session "action" value
    PyObject *clientinfoObj)            // session "clientinfo" value
{
    ub4 credentialType = OCI_CRED_EXT;
    udt_Buffer buffer;
    sword status;

    // allocate the server handle
    status = OCIHandleAlloc(self->environment->handle,
            (dvoid**) &self->serverHandle, OCI_HTYPE_SERVER, 0, 0);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Connect(): allocate server handle") < 0)
        return -1;

    // attach to the server
    if (cxBuffer_FromObject(&buffer, self->dsn,
            self->environment->encoding) < 0)
        return -1;
    Py_BEGIN_ALLOW_THREADS
    status = OCIServerAttach(self->serverHandle,
            self->environment->errorHandle, (text*) buffer.ptr, buffer.size,
            OCI_DEFAULT);
    Py_END_ALLOW_THREADS
    cxBuffer_Clear(&buffer);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Connect(): server attach") < 0)
        return -1;

    // allocate the service context handle
    status = OCIHandleAlloc(self->environment->handle,
            (dvoid**) &self->handle, OCI_HTYPE_SVCCTX, 0, 0);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Connect(): allocate service context handle") < 0)
        return -1;

    // set attribute for server handle
    status = OCIAttrSet(self->handle, OCI_HTYPE_SVCCTX, self->serverHandle, 0,
            OCI_ATTR_SERVER, self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Connect(): set server handle") < 0)
        return -1;

    // set the internal and external names; these are needed for global
    // transactions but are limited in terms of the lengths of the strings
    if (twophase) {
        status = OCIAttrSet(self->serverHandle, OCI_HTYPE_SERVER,
                (dvoid*) "cx_Oracle", 0, OCI_ATTR_INTERNAL_NAME,
                self->environment->errorHandle);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Connect(): set internal name") < 0)
            return -1;
        status = OCIAttrSet(self->serverHandle, OCI_HTYPE_SERVER,
                (dvoid*) "cx_Oracle", 0, OCI_ATTR_EXTERNAL_NAME,
                self->environment->errorHandle);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Connect(): set external name") < 0)
            return -1;
    }

    // allocate the session handle
    status = OCIHandleAlloc(self->environment->handle,
            (dvoid**) &self->sessionHandle, OCI_HTYPE_SESSION, 0, 0);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Connect(): allocate session handle") < 0)
        return -1;

    // set user name in session handle
    if (cxBuffer_FromObject(&buffer, self->username,
            self->environment->encoding) < 0)
        return -1;
    if (buffer.size > 0) {
        credentialType = OCI_CRED_RDBMS;
        status = OCIAttrSet(self->sessionHandle, OCI_HTYPE_SESSION,
                (text*) buffer.ptr, buffer.size, OCI_ATTR_USERNAME,
                self->environment->errorHandle);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Connect(): set user name") < 0) {
            cxBuffer_Clear(&buffer);
            return -1;
        }
    }
    cxBuffer_Clear(&buffer);

    // set password in session handle
    if (cxBuffer_FromObject(&buffer, passwordObj,
            self->environment->encoding) < 0)
        return -1;
    if (buffer.size > 0) {
        credentialType = OCI_CRED_RDBMS;
        status = OCIAttrSet(self->sessionHandle, OCI_HTYPE_SESSION,
                (text*) buffer.ptr, buffer.size, OCI_ATTR_PASSWORD,
                self->environment->errorHandle);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Connect(): set password") < 0) {
            cxBuffer_Clear(&buffer);
            return -1;
        }
    }
    cxBuffer_Clear(&buffer);

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11,1)
    status = OCIAttrSet(self->sessionHandle, OCI_HTYPE_SESSION,
            (text*) DRIVER_NAME, strlen(DRIVER_NAME), OCI_ATTR_DRIVER_NAME,
            self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Connect(): set driver name") < 0)
        return -1;

#endif

    // set the session handle on the service context handle
    status = OCIAttrSet(self->handle, OCI_HTYPE_SVCCTX,
            self->sessionHandle, 0, OCI_ATTR_SESSION,
            self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Connect(): set session handle") < 0)
        return -1;

    if (moduleObj) {
        if (cxBuffer_FromObject(&buffer, moduleObj,
                self->environment->encoding))
            return -1;
        status = OCIAttrSet(self->sessionHandle, OCI_HTYPE_SESSION,
                (text*) buffer.ptr, buffer.size, OCI_ATTR_MODULE,
                self->environment->errorHandle);
        cxBuffer_Clear(&buffer);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Connect(): set module") < 0)
            return -1;
    }

    if (actionObj) {
        if (cxBuffer_FromObject(&buffer, actionObj,
                self->environment->encoding))
            return -1;
        status = OCIAttrSet(self->sessionHandle, OCI_HTYPE_SESSION,
                (text*) buffer.ptr, buffer.size, OCI_ATTR_ACTION,
                self->environment->errorHandle);
        cxBuffer_Clear(&buffer);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Connect(): set action") < 0)
            return -1;
    }

    if (clientinfoObj) {
        if (cxBuffer_FromObject(&buffer, clientinfoObj,
                self->environment->encoding))
            return -1;
        status = OCIAttrSet(self->sessionHandle, OCI_HTYPE_SESSION,
                (text*) buffer.ptr, buffer.size, OCI_ATTR_CLIENT_INFO,
                self->environment->errorHandle);
        cxBuffer_Clear(&buffer);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Connect(): set clientinfo") < 0)
            return -1;
    }

    // if a new password has been specified, change it which will also
    // establish the session
    if (newPasswordObj)
        return Connection_ChangePassword(self, passwordObj, newPasswordObj);

    // begin the session
    Py_BEGIN_ALLOW_THREADS
    status = OCISessionBegin(self->handle, self->environment->errorHandle,
            self->sessionHandle, credentialType, mode);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(self->environment, status,
            "Connection_Connect(): begin session") < 0) {
        self->sessionHandle = NULL;
        return -1;
    }

    return 0;
}


#include "Cursor.c"
#include "Callback.c"
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
#include "Subscription.c"
#endif


//-----------------------------------------------------------------------------
// Connection_New()
//   Create a new connection object and return it.
//-----------------------------------------------------------------------------
static PyObject* Connection_New(
    PyTypeObject *type,                 // type object
    PyObject *args,                     // arguments
    PyObject *keywordArgs)              // keyword arguments
{
    udt_Connection *self;

    // create the object
    self = (udt_Connection*) type->tp_alloc(type, 0);
    if (!self)
        return NULL;
    self->commitMode = OCI_DEFAULT;
    self->environment = NULL;

    return (PyObject*) self;
}


//-----------------------------------------------------------------------------
// Connection_SplitComponent()
//   Split the component out of the source and replace the source with the
// characters up to the split string and put the characters after the split
// string in to the target.
//-----------------------------------------------------------------------------
static int Connection_SplitComponent(
    PyObject **sourceObj,               // source object to split
    PyObject **targetObj,               // target object (for component)
    const char *splitString)            // split string (assume one character)
{
    PyObject *temp, *posObj;
    Py_ssize_t size, pos;

    if (!*sourceObj || *targetObj)
        return 0;
    posObj = PyObject_CallMethod(*sourceObj, "find", "s", splitString);
    if (!posObj)
        return -1;
    pos = PyInt_AsLong(posObj);
    Py_DECREF(posObj);
    if (PyErr_Occurred())
        return -1;
    if (pos >= 0) {
        size = PySequence_Size(*sourceObj);
        if (PyErr_Occurred())
            return -1;
        *targetObj = PySequence_GetSlice(*sourceObj, pos + 1, size);
        if (!*targetObj)
            return -1;
        temp = PySequence_GetSlice(*sourceObj, 0, pos);
        if (!temp)
            return -1;
        *sourceObj = temp;
    }
    return 0;
}


//-----------------------------------------------------------------------------
// Connection_Init()
//   Initialize the connection members.
//-----------------------------------------------------------------------------
static int Connection_Init(
    udt_Connection *self,               // connection
    PyObject *args,                     // arguments
    PyObject *keywordArgs)              // keyword arguments
{
    PyObject *threadedObj, *twophaseObj, *eventsObj, *newPasswordObj;
    PyObject *usernameObj, *passwordObj, *dsnObj, *cclassObj;
    PyObject *moduleObj, *actionObj, *clientinfoObj;
    int threaded, twophase, events;
    char *encoding, *nencoding;
    ub4 connectMode, purity;
    udt_SessionPool *pool;
    OCISvcCtx *handle;

    // define keyword arguments
    static char *keywordList[] = { "user", "password", "dsn", "mode",
            "handle", "pool", "threaded", "twophase", "events", "cclass",
            "purity", "newpassword", "encoding", "nencoding", "module",
            "action", "clientinfo", NULL };

    // parse arguments
    pool = NULL;
    handle = NULL;
    connectMode = OCI_DEFAULT;
    usernameObj = passwordObj = dsnObj = cclassObj = NULL;
    threadedObj = twophaseObj = eventsObj = newPasswordObj = NULL;
    moduleObj = actionObj = clientinfoObj = NULL;
    threaded = twophase = events = purity = 0;
    encoding = nencoding = NULL;
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    purity = OCI_ATTR_PURITY_DEFAULT;
#endif
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs,
            "|OOOiiO!OOOOiOssOOO", keywordList, &usernameObj, &passwordObj,
            &dsnObj, &connectMode, &handle, &g_SessionPoolType, &pool,
            &threadedObj, &twophaseObj, &eventsObj, &cclassObj, &purity,
            &newPasswordObj, &encoding, &nencoding, &moduleObj, &actionObj,
            &clientinfoObj))
        return -1;
    if (threadedObj) {
        threaded = PyObject_IsTrue(threadedObj);
        if (threaded < 0)
            return -1;
    }
    if (twophaseObj) {
        twophase = PyObject_IsTrue(twophaseObj);
        if (twophase < 0)
            return -1;
    }
    if (eventsObj) {
        events = PyObject_IsTrue(eventsObj);
        if (events < 0)
            return -1;
    }

    // set up the environment
    if (pool)
        self->environment = Environment_Clone(pool->environment);
    else self->environment = Environment_NewFromScratch(threaded, events,
            encoding, nencoding);
    if (!self->environment)
        return -1;

    // keep a copy of the credentials
    Py_XINCREF(usernameObj);
    self->username = usernameObj;
    Py_XINCREF(dsnObj);
    self->dsn = dsnObj;

    // perform some parsing, if necessary
    if (Connection_SplitComponent(&self->username, &passwordObj, "/") < 0)
        return -1;
    if (Connection_SplitComponent(&passwordObj, &self->dsn, "@") < 0)
        return -1;

    // handle the different ways of initializing the connection
    if (handle)
        return Connection_Attach(self, handle);
    if (pool || cclassObj)
        return Connection_GetConnection(self, pool, passwordObj, cclassObj,
                purity);
    return Connection_Connect(self, connectMode, twophase, passwordObj,
            newPasswordObj, moduleObj, actionObj, clientinfoObj);
}


//-----------------------------------------------------------------------------
// Connection_Free()
//   Deallocate the connection, disconnecting from the database if necessary.
//-----------------------------------------------------------------------------
static void Connection_Free(
    udt_Connection *self)               // connection object
{
    if (self->release) {
        Py_BEGIN_ALLOW_THREADS
        OCITransRollback(self->handle, self->environment->errorHandle,
                OCI_DEFAULT);
        OCISessionRelease(self->handle, self->environment->errorHandle, NULL,
                0, OCI_DEFAULT);
        Py_END_ALLOW_THREADS
    } else if (!self->attached) {
        if (self->sessionHandle) {
            Py_BEGIN_ALLOW_THREADS
            OCITransRollback(self->handle, self->environment->errorHandle,
                    OCI_DEFAULT);
            OCISessionEnd(self->handle, self->environment->errorHandle,
                    self->sessionHandle, OCI_DEFAULT);
            Py_END_ALLOW_THREADS
        }
        if (self->serverHandle)
            OCIServerDetach(self->serverHandle,
                    self->environment->errorHandle, OCI_DEFAULT);
    }
    Py_CLEAR(self->environment);
    Py_CLEAR(self->sessionPool);
    Py_CLEAR(self->username);
    Py_CLEAR(self->dsn);
    Py_CLEAR(self->version);
    Py_CLEAR(self->inputTypeHandler);
    Py_CLEAR(self->outputTypeHandler);
    Py_TYPE(self)->tp_free((PyObject*) self);
}


//-----------------------------------------------------------------------------
// Connection_Repr()
//   Return a string representation of the connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_Repr(
    udt_Connection *connection)         // connection to return the string for
{
    PyObject *module, *name, *result, *format, *formatArgs = NULL;

    if (GetModuleAndName(Py_TYPE(connection), &module, &name) < 0)
        return NULL;
    if (connection->username && connection->username != Py_None &&
            connection->dsn && connection->dsn != Py_None) {
        format = cxString_FromAscii("<%s.%s to %s@%s>");
        if (format)
            formatArgs = PyTuple_Pack(4, module, name, connection->username,
                    connection->dsn);
    } else if (connection->username && connection->username != Py_None) {
        format = cxString_FromAscii("<%s.%s to user %s@local>");
        if (format)
            formatArgs = PyTuple_Pack(3, module, name, connection->username);
    } else {
        format = cxString_FromAscii("<%s.%s to externally identified user>");
        if (format)
            formatArgs = PyTuple_Pack(2, module, name);
    }
    Py_DECREF(module);
    Py_DECREF(name);
    if (!format)
        return NULL;
    if (!formatArgs) {
        Py_DECREF(format);
        return NULL;
    }
    result = cxString_Format(format, formatArgs);
    Py_DECREF(format);
    Py_DECREF(formatArgs);
    return result;
}


//-----------------------------------------------------------------------------
// Connection_GetStmtCacheSize()
//   Return the Oracle statement cache size.
//-----------------------------------------------------------------------------
static PyObject *Connection_GetStmtCacheSize(
    udt_Connection* self,               // connection object
    void* arg)                          // optional argument (ignored)
{
    ub4 cacheSize;
    sword status;

    if (Connection_IsConnected(self) < 0)
        return NULL;
    status = OCIAttrGet(self->handle, OCI_HTYPE_SVCCTX,
            (dvoid**) &cacheSize, 0, OCI_ATTR_STMTCACHESIZE,
            self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_GetStmtCacheSize()") < 0)
        return NULL;
    return PyInt_FromLong(cacheSize);
}


//-----------------------------------------------------------------------------
// Connection_SetStmtCacheSize()
//   Set the Oracle statement cache size.
//-----------------------------------------------------------------------------
static int Connection_SetStmtCacheSize(
    udt_Connection* self,               // connection object
    PyObject *value,                    // value to set it to
    void* arg)                          // optional argument (ignored)
{
    ub4 valueToSet;
    sword status;

    if (Connection_IsConnected(self) < 0)
        return -1;
    if (!PyInt_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "value must be an integer");
        return -1;
    }
    valueToSet = (ub4) PyInt_AsLong(value);
    if (PyErr_Occurred())
        return -1;
    status = OCIAttrSet(self->handle, OCI_HTYPE_SVCCTX, (dvoid*) &valueToSet,
            0, OCI_ATTR_STMTCACHESIZE, self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_SetStmtCacheSize()") < 0)
        return -1;
    return 0;
}


//-----------------------------------------------------------------------------
// Connection_GetVersion()
//   Retrieve the version of the database and return it. Note that this
// function also places the result in the associated dictionary so it is only
// calculated once.
//-----------------------------------------------------------------------------
static PyObject *Connection_GetVersion(
    udt_Connection *self,               // connection object
    void *arg)                          // optional argument (ignored)
{
    PyObject *procName, *listOfArguments;
    udt_Variable *versionVar, *compatVar;
    udt_Cursor *cursor;

    // if version has already been determined, no need to determine again
    if (self->version) {
        Py_INCREF(self->version);
        return self->version;
    }

    // allocate a cursor to retrieve the version
    cursor = (udt_Cursor*) Connection_NewCursor(self, NULL);
    if (!cursor)
        return NULL;

    // allocate version variable
    versionVar = Variable_New(cursor, cursor->arraySize, &vt_String,
            vt_String.size);
    if (!versionVar) {
        Py_DECREF(cursor);
        return NULL;
    }

    // allocate compatibility variable
    compatVar = Variable_New(cursor, cursor->arraySize, &vt_String,
            vt_String.size);
    if (!compatVar) {
        Py_DECREF(versionVar);
        Py_DECREF(cursor);
        return NULL;
    }

    // create the list of arguments
    listOfArguments = PyList_New(2);
    if (!listOfArguments) {
        Py_DECREF(versionVar);
        Py_DECREF(compatVar);
        Py_DECREF(cursor);
        return NULL;
    }
    PyList_SET_ITEM(listOfArguments, 0, (PyObject*) versionVar);
    PyList_SET_ITEM(listOfArguments, 1, (PyObject*) compatVar);

    // create the string variable
    procName = cxString_FromAscii("dbms_utility.db_version");
    if (!procName) {
        Py_DECREF(listOfArguments);
        Py_DECREF(cursor);
        return NULL;
    }

    // call stored procedure
    if (Cursor_Call(cursor, NULL, procName, listOfArguments, NULL) < 0) {
        Py_DECREF(procName);
        Py_DECREF(listOfArguments);
        Py_DECREF(cursor);
        return NULL;
    }
    Py_DECREF(procName);

    // retrieve value
    self->version = Variable_GetValue(versionVar, 0);
    Py_DECREF(listOfArguments);
    Py_DECREF(cursor);
    Py_XINCREF(self->version);
    return self->version;
}


//-----------------------------------------------------------------------------
// Connection_GetEncoding()
//   Return the encoding associated with the environment of the connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_GetEncoding(
    udt_Connection *self,               // connection object
    void *arg)                          // optional argument (ignored)
{
    return cxString_FromAscii(self->environment->encoding);
}


//-----------------------------------------------------------------------------
// Connection_GetNationalEncoding()
//   Return the national encoding associated with the environment of the
// connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_GetNationalEncoding(
    udt_Connection *self,               // connection object
    void *arg)                          // optional argument (ignored)
{
    return cxString_FromAscii(self->environment->nencoding);
}


//-----------------------------------------------------------------------------
// Connection_GetMaxBytesPerCharacter()
//   Return the maximum number of bytes per character.
//-----------------------------------------------------------------------------
static PyObject *Connection_GetMaxBytesPerCharacter(
    udt_Connection *self,               // connection object
    void *arg)                          // optional argument (ignored)
{
    return PyInt_FromLong(self->environment->maxBytesPerCharacter);
}


//-----------------------------------------------------------------------------
// Connection_Close()
//   Close the connection, disconnecting from the database.
//-----------------------------------------------------------------------------
static PyObject *Connection_Close(
    udt_Connection *self,               // connection to close
    PyObject *args)                     // arguments
{
    sword status;

    // make sure we are actually connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // perform a rollback
    Py_BEGIN_ALLOW_THREADS
    status = OCITransRollback(self->handle, self->environment->errorHandle,
            OCI_DEFAULT);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(self->environment, status,
            "Connection_Close(): rollback") < 0)
        return NULL;

    // logoff of the server
    if (self->release) {
        Py_BEGIN_ALLOW_THREADS
        status = OCISessionRelease(self->handle,
                self->environment->errorHandle, NULL, 0, OCI_DEFAULT);
        Py_END_ALLOW_THREADS
        if (Environment_CheckForError(self->environment, status,
                "Connection_Close(): release session") < 0)
            return NULL;
        self->release = 0;
    }
    else {
        if (self->sessionHandle) {
            Py_BEGIN_ALLOW_THREADS
            status = OCISessionEnd(self->handle,
                    self->environment->errorHandle, self->sessionHandle,
                    OCI_DEFAULT);
            Py_END_ALLOW_THREADS
            if (Environment_CheckForError(self->environment, status,
                    "Connection_Close(): end session") < 0)
                return NULL;
            OCIHandleFree(self->sessionHandle, OCI_HTYPE_SESSION);
            self->sessionHandle = NULL;
            OCIHandleFree(self->handle, OCI_HTYPE_SVCCTX);
        }

        if (self->serverHandle) {
            status = OCIServerDetach(self->serverHandle,
                self->environment->errorHandle, OCI_DEFAULT);
            if (Environment_CheckForError(self->environment, status,
                "Connection_Close(): server detach") < 0)
                return NULL;
            OCIHandleFree(self->serverHandle, OCI_HTYPE_SERVER);
            self->serverHandle = NULL;
        }
    }
    self->handle = NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_Commit()
//   Commit the transaction on the connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_Commit(
    udt_Connection *self,               // connection to commit
    PyObject *args)                     // arguments
{
    sword status;

    // make sure we are actually connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // perform the commit
    Py_BEGIN_ALLOW_THREADS
    status = OCITransCommit(self->handle, self->environment->errorHandle,
            self->commitMode);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(self->environment, status,
            "Connection_Commit()") < 0)
        return NULL;
    self->commitMode = OCI_DEFAULT;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_Begin()
//   Begin a new transaction on the connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_Begin(
    udt_Connection *self,               // connection to commit
    PyObject *args)                     // arguments
{
    unsigned transactionIdLength, branchIdLength;
    const char *transactionId, *branchId;
    OCITrans *transactionHandle;
    int formatId;
    sword status;
    XID xid;

    // parse the arguments
    formatId = -1;
    transactionIdLength = branchIdLength = 0;
    if (!PyArg_ParseTuple(args, "|is#s#", &formatId, &transactionId,
            &transactionIdLength,  &branchId, &branchIdLength))
        return NULL;
    if (transactionIdLength > MAXGTRIDSIZE) {
        PyErr_SetString(PyExc_ValueError, "transaction id too large");
        return NULL;
    }
    if (branchIdLength > MAXBQUALSIZE) {
        PyErr_SetString(PyExc_ValueError, "branch id too large");
        return NULL;
    }

    // make sure we are actually connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // determine if a transaction handle was previously allocated
    status = OCIAttrGet(self->handle, OCI_HTYPE_SVCCTX,
            (dvoid**) &transactionHandle, 0, OCI_ATTR_TRANS,
            self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Begin(): find existing transaction handle") < 0)
        return NULL;

    // create a new transaction handle, if necessary
    if (!transactionHandle) {
        status = OCIHandleAlloc(self->environment->handle,
                (dvoid**) &transactionHandle, OCI_HTYPE_TRANS, 0, 0);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Begin(): allocate transaction handle") < 0)
            return NULL;
    }

    // set the XID for the transaction, if applicable
    if (formatId != -1) {
        xid.formatID = formatId;
        xid.gtrid_length = transactionIdLength;
        xid.bqual_length = branchIdLength;
        if (transactionIdLength > 0)
            strncpy(xid.data, transactionId, transactionIdLength);
        if (branchIdLength > 0)
            strncpy(&xid.data[transactionIdLength], branchId, branchIdLength);
        OCIAttrSet(transactionHandle, OCI_HTYPE_TRANS, &xid, sizeof(XID),
                OCI_ATTR_XID, self->environment->errorHandle);
        if (Environment_CheckForError(self->environment, status,
                "Connection_Begin(): set XID") < 0)
            return NULL;
    }

    // associate the transaction with the connection
    OCIAttrSet(self->handle, OCI_HTYPE_SVCCTX, transactionHandle, 0,
            OCI_ATTR_TRANS, self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Begin(): associate transaction") < 0)
        return NULL;

    // start the transaction
    Py_BEGIN_ALLOW_THREADS
    status = OCITransStart(self->handle, self->environment->errorHandle, 0,
            OCI_TRANS_NEW);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(self->environment, status,
            "Connection_Begin(): start transaction") < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_Prepare()
//   Commit the transaction on the connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_Prepare(
    udt_Connection *self,               // connection to commit
    PyObject *args)                     // arguments
{
    sword status;

    // make sure we are actually connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // perform the prepare
    Py_BEGIN_ALLOW_THREADS
    status = OCITransPrepare(self->handle, self->environment->errorHandle,
            OCI_DEFAULT);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(self->environment, status,
            "Connection_Prepare()") < 0)
        return NULL;

    // if nothing available to prepare, return False in order to allow for
    // avoiding the call to commit() which will fail with ORA-24756
    // (transaction does not exist)
    if (status == OCI_SUCCESS_WITH_INFO) {
        Py_INCREF(Py_False);
        return Py_False;
    }
    self->commitMode = OCI_TRANS_TWOPHASE;
    Py_INCREF(Py_True);
    return Py_True;
}


//-----------------------------------------------------------------------------
// Connection_Rollback()
//   Rollback the transaction on the connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_Rollback(
    udt_Connection *self,               // connection to rollback
    PyObject *args)                     // arguments
{
    sword status;

    // make sure we are actually connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // perform the rollback
    Py_BEGIN_ALLOW_THREADS
    status = OCITransRollback(self->handle, self->environment->errorHandle,
            OCI_DEFAULT);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(self->environment, status,
            "Connection_Rollback()") < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_NewCursor()
//   Create a new cursor (statement) referencing the connection.
//-----------------------------------------------------------------------------
static PyObject *Connection_NewCursor(
    udt_Connection *self,               // connection to create cursor on
    PyObject *args)                     // arguments
{
    PyObject *createArgs, *result;

    createArgs = PyTuple_New(1);
    if (!createArgs)
        return NULL;
    Py_INCREF(self);
    PyTuple_SET_ITEM(createArgs, 0, (PyObject*) self);
    result = PyObject_Call( (PyObject*) &g_CursorType, createArgs, NULL);
    Py_DECREF(createArgs);
    return result;
}


//-----------------------------------------------------------------------------
// Connection_Cancel()
//   Execute an OCIBreak() to cause an immediate (asynchronous) abort of any
// currently executing OCI function.
//-----------------------------------------------------------------------------
static PyObject *Connection_Cancel(
    udt_Connection *self,               // connection to cancel
    PyObject *args)                     // arguments
{
    sword status;

    // make sure we are actually connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // perform the break
    status = OCIBreak(self->handle, self->environment->errorHandle);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Cancel()") < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_RegisterCallback()
//   Register a callback for the OCI function.
//-----------------------------------------------------------------------------
static PyObject *Connection_RegisterCallback(
    udt_Connection *self,               // connection to register callback on
    PyObject *args)                     // arguments
{
    PyObject *callback, *tuple;
    int functionCode, when;
    sword status;

    // parse the arguments
    if (!PyArg_ParseTuple(args, "iiO", &functionCode, &when, &callback))
        return NULL;

    // create a tuple for passing through to the callback handler
    tuple = Py_BuildValue("OO", self, callback);
    if (!tuple)
        return NULL;

    // make sure we are actually connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // register the callback with the OCI
    status = OCIUserCallbackRegister(self->environment->handle, OCI_HTYPE_ENV,
            self->environment->errorHandle, (OCIUserCallback) Callback_Handler,
            tuple, functionCode, when, NULL);
    if (Environment_CheckForError(self->environment, status,
            "Connection_RegisterCallback()") < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

//-----------------------------------------------------------------------------
// Connection_UnregisterCallback()
//   Unregister a callback for the OCI function, if one has been registered.
// No error is raised if a callback has not been registered.
//-----------------------------------------------------------------------------
static PyObject *Connection_UnregisterCallback(
    udt_Connection *self,               // connection to unregister callback on
    PyObject *args)                     // arguments
{
    OCIUserCallback callback;
    int functionCode, when;
    PyObject *tuple;
    sword status;

    // parse the arguments
    if (!PyArg_ParseTuple(args, "ii", &functionCode, &when))
        return NULL;

    // make sure we are actually connected
    if (Connection_IsConnected(self) < 0)
        return NULL;

    // find out if a callback has been registered
    status = OCIUserCallbackGet(self->environment->handle, OCI_HTYPE_ENV,
            self->environment->errorHandle, functionCode, when, &callback,
            (dvoid**) &tuple, NULL);
    if (Environment_CheckForError(self->environment, status,
            "Connection_UnregisterCallback(): get") < 0)
        return NULL;

    // if a callback was registered, clear it
    if (callback) {
        Py_DECREF(tuple);
        status = OCIUserCallbackRegister(self->environment->handle,
                OCI_HTYPE_ENV, self->environment->errorHandle, NULL,
                NULL, functionCode, when, NULL);
        if (Environment_CheckForError(self->environment, status,
                "Connection_UnregisterCallback(): clear") < 0)
            return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_ContextManagerEnter()
//   Called when the connection is used as a context manager and simply returns
// itself as a convenience to the caller.
//-----------------------------------------------------------------------------
static PyObject *Connection_ContextManagerEnter(
    udt_Connection *self,               // connection
    PyObject* args)                     // arguments
{
    Py_INCREF(self);
    return (PyObject*) self;
}


//-----------------------------------------------------------------------------
// Connection_ContextManagerExit()
//   Called when the connection is used as a context manager and if any
// exception a rollback takes place; otherwise, a commit takes place.
//-----------------------------------------------------------------------------
static PyObject *Connection_ContextManagerExit(
    udt_Connection *self,               // connection
    PyObject* args)                     // arguments
{
    PyObject *excType, *excValue, *excTraceback, *result;
    char *methodName;

    if (!PyArg_ParseTuple(args, "OOO", &excType, &excValue, &excTraceback))
        return NULL;
    if (excType == Py_None && excValue == Py_None && excTraceback == Py_None)
        methodName = "commit";
    else methodName = "rollback";
    result = PyObject_CallMethod((PyObject*) self, methodName, "");
    if (!result)
        return NULL;
    Py_DECREF(result);

    Py_INCREF(Py_False);
    return Py_False;
}


#if ORACLE_VERSION_HEX >= ORACLE_VERSION(10, 2)
#if !defined(AIX5) || ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
//-----------------------------------------------------------------------------
// Connection_Ping()
//   Makes a round trip call to the server to confirm that the connection and
// server are active.
//-----------------------------------------------------------------------------
static PyObject *Connection_Ping(
    udt_Connection *self,               // connection
    PyObject* args)                     // arguments
{
    sword status;

    if (Connection_IsConnected(self) < 0)
        return NULL;
    status = OCIPing(self->handle, self->environment->errorHandle,
            OCI_DEFAULT);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Ping()") < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}
#endif


//-----------------------------------------------------------------------------
// Connection_Shutdown()
//   Shuts down the database. Note that this must be done in two phases except
// in the situation where the instance is aborted.
//-----------------------------------------------------------------------------
static PyObject *Connection_Shutdown(
    udt_Connection *self,               // connection
    PyObject* args,                     // arguments
    PyObject* keywordArgs)              // keyword arguments
{
    static char *keywordList[] = { "mode", NULL };
    sword status;
    ub4 mode;

    // parse arguments
    mode = OCI_DEFAULT;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|i", keywordList,
            &mode))
        return NULL;

    // perform the work
    if (Connection_IsConnected(self) < 0)
        return NULL;
    status = OCIDBShutdown(self->handle, self->environment->errorHandle, NULL,
            mode);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Shutdown()") < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_Startup()
//   Starts up the database, equivalent to "startup nomount" in SQL*Plus.
//-----------------------------------------------------------------------------
static PyObject *Connection_Startup(
    udt_Connection *self,               // connection
    PyObject* args,                     // arguments
    PyObject* keywordArgs)              // keyword arguments
{
    static char *keywordList[] = { "force", "restrict", NULL };
    PyObject *forceObj, *restrictObj;
    int flagTemp;
    sword status;
    ub4 flags;

    // parse arguments
    forceObj = restrictObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|OO", keywordList,
            &forceObj, &restrictObj))
        return NULL;

    // set the flags to use during startup
    flags = 0;
    if (forceObj) {
        flagTemp = PyObject_IsTrue(forceObj);
        if (flagTemp < 0)
            return NULL;
        if (flagTemp)
            flags |= OCI_DBSTARTUPFLAG_FORCE;
    }
    if (restrictObj) {
        flagTemp = PyObject_IsTrue(restrictObj);
        if (flagTemp < 0)
            return NULL;
        if (flagTemp)
            flags |= OCI_DBSTARTUPFLAG_RESTRICT;
    }

    // perform the work
    if (Connection_IsConnected(self) < 0)
        return NULL;
    status = OCIDBStartup(self->handle, self->environment->errorHandle, NULL,
            OCI_DEFAULT, flags);
    if (Environment_CheckForError(self->environment, status,
            "Connection_Startup()") < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Connection_Subscribe()
//   Create a subscription to events that take place in the database.
//-----------------------------------------------------------------------------
static PyObject *Connection_Subscribe(
    udt_Connection *self,               // connection
    PyObject* args,                     // arguments
    PyObject* keywordArgs)              // keyword arguments
{
    static char *keywordList[] = { "namespace", "protocol", "callback",
            "timeout", "operations", "rowids", "port", "qos", "cqqos", NULL };
    ub4 namespace, protocol, port, timeout, rowids, operations, qos, cqqos;
    PyObject *rowidsObj, *callback;
    int temp;

    // parse arguments
    timeout = rowids = port = qos = cqqos = 0;
    rowidsObj = callback = NULL;
    namespace = OCI_SUBSCR_NAMESPACE_DBCHANGE;
    protocol = OCI_SUBSCR_PROTO_OCI;
    operations = OCI_OPCODE_ALLOPS;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|iiOiiOiii", keywordList,
            &namespace, &protocol, &callback, &timeout, &operations,
            &rowidsObj, &port, &qos, &cqqos))
        return NULL;

    // set the value for rowids
    if (rowidsObj) {
        temp = PyObject_IsTrue(rowidsObj);
        if (temp < 0)
            return NULL;
        if (temp)
            rowids = 1;
    }

    return (PyObject*) Subscription_New(self, namespace, protocol, port,
            callback, timeout, operations, qos, cqqos, rowids);
}
#endif

