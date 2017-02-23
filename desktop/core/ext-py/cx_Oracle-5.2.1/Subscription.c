//-----------------------------------------------------------------------------
// Subscription.c
//   Defines the routines for handling Oracle subscription information.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// structures used for handling subscriptions
//-----------------------------------------------------------------------------
typedef struct {
    PyObject_HEAD
    OCISubscription *handle;
    udt_Connection *connection;
    PyObject *callback;
    ub4 namespace;
    ub4 protocol;
    ub4 port;
    ub4 timeout;
    ub4 operations;
    ub4 qos;
    ub4 cqqos;
    ub4 rowids;
    ub4 id;
} udt_Subscription;

typedef struct {
    PyObject_HEAD
    udt_Subscription *subscription;
    ub4 type;
    PyObject *dbname;
    PyObject *tables;
    PyObject *queries;
} udt_Message;

typedef struct {
    PyObject_HEAD
    PyObject *name;
    PyObject *rows;
    ub4 operation;
} udt_MessageTable;

typedef struct {
    PyObject_HEAD
    PyObject *rowid;
    ub4 operation;
} udt_MessageRow;

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
typedef struct {
    PyObject_HEAD
    ub8 id;
    ub4 operation;
    PyObject *tables;
} udt_MessageQuery;
#endif


//-----------------------------------------------------------------------------
// Declaration of subscription functions
//-----------------------------------------------------------------------------
static void Subscription_Free(udt_Subscription*);
static PyObject *Subscription_Repr(udt_Subscription*);
static PyObject *Subscription_RegisterQuery(udt_Subscription*, PyObject*);
static void Message_Free(udt_Message*);
static void MessageTable_Free(udt_MessageTable*);
static void MessageRow_Free(udt_MessageRow*);
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
static void MessageQuery_Free(udt_MessageQuery*);
#endif

//-----------------------------------------------------------------------------
// declaration of members for Python types
//-----------------------------------------------------------------------------
static PyMemberDef g_SubscriptionTypeMembers[] = {
    { "callback", T_OBJECT, offsetof(udt_Subscription, callback), READONLY },
    { "connection", T_OBJECT, offsetof(udt_Subscription, connection),
            READONLY },
    { "namespace", T_INT, offsetof(udt_Subscription, namespace), READONLY },
    { "protocol", T_INT, offsetof(udt_Subscription, protocol), READONLY },
    { "port", T_INT, offsetof(udt_Subscription, port), READONLY },
    { "timeout", T_INT, offsetof(udt_Subscription, timeout), READONLY },
    { "operations", T_INT, offsetof(udt_Subscription, operations), READONLY },
    { "qos", T_INT, offsetof(udt_Subscription, qos), READONLY },
    { "cqqos", T_INT, offsetof(udt_Subscription, cqqos), READONLY },
    { "rowids", T_BOOL, offsetof(udt_Subscription, rowids), READONLY },
    { "id", T_INT, offsetof(udt_Subscription, id), READONLY },
    { NULL }
};

static PyMemberDef g_MessageTypeMembers[] = {
    { "subscription", T_OBJECT, offsetof(udt_Message, subscription),
            READONLY },
    { "type", T_INT, offsetof(udt_Message, type), READONLY },
    { "dbname", T_OBJECT, offsetof(udt_Message, dbname), READONLY },
    { "tables", T_OBJECT, offsetof(udt_Message, tables), READONLY },
    { "queries", T_OBJECT, offsetof(udt_Message, queries), READONLY },
    { NULL }
};

static PyMemberDef g_MessageTableTypeMembers[] = {
    { "name", T_OBJECT, offsetof(udt_MessageTable, name), READONLY },
    { "rows", T_OBJECT, offsetof(udt_MessageTable, rows), READONLY },
    { "operation", T_INT, offsetof(udt_MessageTable, operation), READONLY },
    { NULL }
};

static PyMemberDef g_MessageRowTypeMembers[] = {
    { "rowid", T_OBJECT, offsetof(udt_MessageRow, rowid), READONLY },
    { "operation", T_INT, offsetof(udt_MessageRow, operation), READONLY },
    { NULL }
};

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
static PyMemberDef g_MessageQueryTypeMembers[] = {
    { "id", T_INT, offsetof(udt_MessageQuery, id), READONLY },
    { "operation", T_INT, offsetof(udt_MessageQuery, operation), READONLY },
    { "tables", T_OBJECT, offsetof(udt_MessageQuery, tables), READONLY },
    { NULL }
};
#endif


//-----------------------------------------------------------------------------
// declaration of methods for Python types
//-----------------------------------------------------------------------------
static PyMethodDef g_SubscriptionTypeMethods[] = {
    { "registerquery", (PyCFunction) Subscription_RegisterQuery,
            METH_VARARGS },
    { NULL, NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
static PyTypeObject g_SubscriptionType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.Subscription",           // tp_name
    sizeof(udt_Subscription),           // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) Subscription_Free,     // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) Subscription_Repr,       // tp_repr
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
    g_SubscriptionTypeMethods,          // tp_methods
    g_SubscriptionTypeMembers,          // tp_members
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

static PyTypeObject g_MessageType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.Message",                // tp_name
    sizeof(udt_Message),                // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) Message_Free,          // tp_dealloc
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
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    0,                                  // tp_methods
    g_MessageTypeMembers,               // tp_members
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

static PyTypeObject g_MessageTableType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.MessageTable",           // tp_name
    sizeof(udt_MessageTable),           // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) MessageTable_Free,     // tp_dealloc
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
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    0,                                  // tp_methods
    g_MessageTableTypeMembers,          // tp_members
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


static PyTypeObject g_MessageRowType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.MessageRow",             // tp_name
    sizeof(udt_MessageRow),             // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) MessageRow_Free,       // tp_dealloc
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
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    0,                                  // tp_methods
    g_MessageRowTypeMembers,            // tp_members
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


#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
static PyTypeObject g_MessageQueryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.MessageQuery",           // tp_name
    sizeof(udt_MessageQuery),           // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) MessageQuery_Free,     // tp_dealloc
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
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    0,                                  // tp_methods
    g_MessageQueryTypeMembers,          // tp_members
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
#endif


//-----------------------------------------------------------------------------
// MessageRow_Initialize()
//   Initialize a new message row with the information from the descriptor.
//-----------------------------------------------------------------------------
static int MessageRow_Initialize(
    udt_MessageRow *self,               // object to initialize
    udt_Environment *env,               // environment to use
    dvoid *descriptor)                  // descriptor to get information from
{
    ub4 rowidLength;
    sword status;
    char *rowid;

    // determine operation
    status = OCIAttrGet(descriptor, OCI_DTYPE_ROW_CHDES, &self->operation,
            NULL, OCI_ATTR_CHDES_ROW_OPFLAGS, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "MessageRow_Initialize(): get operation") < 0)
        return -1;

    // determine table name
    status = OCIAttrGet(descriptor, OCI_DTYPE_ROW_CHDES, &rowid, &rowidLength,
            OCI_ATTR_CHDES_ROW_ROWID, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "MessageRow_Initialize(): get rowid") < 0)
        return -1;
    self->rowid = cxString_FromEncodedString(rowid, rowidLength,
            env->encoding);
    if (!self->rowid)
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// MessageTable_Initialize()
//   Initialize a new message table with the information from the descriptor.
//-----------------------------------------------------------------------------
static int MessageTable_Initialize(
    udt_MessageTable *self,             // object to initialize
    udt_Environment *env,               // environment to use
    dvoid *descriptor)                  // descriptor to get information from
{
    dvoid **rowDescriptor, *indicator;
    ub4 nameLength, i;
    udt_MessageRow *row;
    boolean exists;
    OCIColl *rows;
    sword status;
    sb4 numRows;
    char *name;

    // determine operation
    status = OCIAttrGet(descriptor, OCI_DTYPE_TABLE_CHDES, &self->operation,
            NULL, OCI_ATTR_CHDES_TABLE_OPFLAGS, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "MessageTable_Initialize(): get operation") < 0)
        return -1;

    // determine table name
    status = OCIAttrGet(descriptor, OCI_DTYPE_TABLE_CHDES, &name, &nameLength,
            OCI_ATTR_CHDES_TABLE_NAME, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "MessageTable_Initialize(): get table name") < 0)
        return -1;
    self->name = cxString_FromEncodedString(name, nameLength, env->encoding);
    if (!self->name)
        return -1;

    // if change invalidated all rows, nothing to do
    if (self->operation & OCI_OPCODE_ALLROWS)
        return 0;

    // determine rows collection
    status = OCIAttrGet(descriptor, OCI_DTYPE_TABLE_CHDES, &rows, NULL,
            OCI_ATTR_CHDES_TABLE_ROW_CHANGES, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "MessageTable_Initialize(): get rows collection") < 0)
        return -1;

    // determine number of rows in collection
    status = OCICollSize(env->handle, env->errorHandle, rows, &numRows);
    if (Environment_CheckForError(env, status,
            "MessageTable_Initialize(): get size of rows collection") < 0)
        return -1;

    // populate the rows attribute
    self->rows = PyList_New(numRows);
    if (!self->rows)
        return -1;
    for (i = 0; i < numRows; i++) {
        status = OCICollGetElem(env->handle, env->errorHandle, rows, i,
                &exists, (dvoid*) &rowDescriptor, &indicator);
        if (Environment_CheckForError(env, status,
                "MessageTable_Initialize(): get element from collection") < 0)
            return -1;
        row = (udt_MessageRow*)
                g_MessageRowType.tp_alloc(&g_MessageRowType, 0);
        if (!row)
            return -1;
        PyList_SET_ITEM(self->rows, i, (PyObject*) row);
        if (MessageRow_Initialize(row, env, *rowDescriptor) < 0)
            return -1;
    }

    return 0;
}


#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
//-----------------------------------------------------------------------------
// MessageQuery_Initialize()
//   Initialize a new message query with the information from the descriptor.
//-----------------------------------------------------------------------------
static int MessageQuery_Initialize(
    udt_MessageQuery *self,             // object to initialize
    udt_Environment *env,               // environment to use
    dvoid *descriptor)                  // descriptor to get information from
{
    dvoid **tableDescriptor, *indicator;
    udt_MessageTable *table;
    ub4 i;
    OCIColl *tables;
    boolean exists;
    sb4 numTables;
    sword status;

    // determine query id
    status = OCIAttrGet(descriptor, OCI_DTYPE_CQDES, &self->id,
            NULL, OCI_ATTR_CQDES_QUERYID, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "MessageQuery_Initialize(): get query id") < 0)
        return -1;

    // determine operation
    status = OCIAttrGet(descriptor, OCI_DTYPE_CQDES, &self->operation,
            NULL, OCI_ATTR_CQDES_OPERATION, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "MessageQuery_Initialize(): get operation") < 0)
        return -1;

    // determine table collection
    status = OCIAttrGet(descriptor, OCI_DTYPE_CQDES, &tables, NULL,
            OCI_ATTR_CQDES_TABLE_CHANGES, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "MessageQuery_Initialize(): get tables collection") < 0)
        return -1;

    // determine number of tables
    if (!tables)
        numTables = 0;
    else {
        status = OCICollSize(env->handle, env->errorHandle, tables,
                &numTables);
        if (Environment_CheckForError(env, status,
                "MessageQuery_Initialize(): get size of collection") < 0)
            return -1;
    }

    // create list to hold results
    self->tables = PyList_New(numTables);
    if (!self->tables)
        return -1;

    // populate each entry with a message table instance
    for (i = 0; i < numTables; i++) {
        status = OCICollGetElem(env->handle, env->errorHandle, tables, i,
                &exists, (dvoid*) &tableDescriptor, &indicator);
        if (Environment_CheckForError(env, status,
                "MessageQuery_Initialize(): get element from collection") < 0)
            return -1;
        table = (udt_MessageTable*)
                g_MessageTableType.tp_alloc(&g_MessageTableType, 0);
        if (!table)
            return -1;
        PyList_SET_ITEM(self->tables, i, (PyObject*) table);
        if (MessageTable_Initialize(table, env, *tableDescriptor) < 0)
            return -1;
    }

    return 0;
}
#endif


//-----------------------------------------------------------------------------
// Message_Initialize()
//   Initialize a new message with the information from the descriptor.
//-----------------------------------------------------------------------------
static int Message_Initialize(
    udt_Message *self,                  // object to initialize
    udt_Environment *env,               // environment to use
    udt_Subscription *subscription,     // associated subscription for message
    dvoid *descriptor)                  // descriptor to get information from
{
    dvoid **tableDescriptor, *indicator;
    udt_MessageTable *table;
    ub4 dbnameLength, i;
    OCIColl *tables;
    boolean exists;
    sb4 numTables;
    char *dbname;
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    dvoid **queryDescriptor;
    udt_MessageQuery *query;
    OCIColl *queries;
    sb4 numQueries;
#endif
    sword status;

    // assign reference to associated subscription
    Py_INCREF(subscription);
    self->subscription = subscription;

    // determine type
    status = OCIAttrGet(descriptor, OCI_DTYPE_CHDES, &self->type, NULL,
            OCI_ATTR_CHDES_NFYTYPE, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "Message_Initialize(): get type") < 0)
        return -1;

    // determine database name
    status = OCIAttrGet(descriptor, OCI_DTYPE_CHDES, &dbname, &dbnameLength,
            OCI_ATTR_CHDES_DBNAME, env->errorHandle);
    if (Environment_CheckForError(env, status,
            "Message_Initialize(): get database name") < 0)
        return -1;
    self->dbname = cxString_FromEncodedString(dbname, dbnameLength,
            env->encoding);
    if (!self->dbname)
        return -1;

    if (self->type == OCI_EVENT_OBJCHANGE) {
        // determine table collection
        status = OCIAttrGet(descriptor, OCI_DTYPE_CHDES, &tables, NULL,
                OCI_ATTR_CHDES_TABLE_CHANGES, env->errorHandle);
        if (Environment_CheckForError(env, status,
                "Message_Initialize(): get tables collection") < 0)
            return -1;

        // determine number of tables
        if (!tables)
            numTables = 0;
        else {
            status = OCICollSize(env->handle, env->errorHandle, tables,
                    &numTables);
            if (Environment_CheckForError(env, status,
                    "Message_Initialize(): get size of collection") < 0)
                return -1;
        }

        // create list to hold results
        self->tables = PyList_New(numTables);
        if (!self->tables)
            return -1;

        // populate each entry with a message table instance
        for (i = 0; i < numTables; i++) {
            status = OCICollGetElem(env->handle, env->errorHandle, tables, i,
                    &exists, (dvoid*) &tableDescriptor, &indicator);
            if (Environment_CheckForError(env, status,
                    "Message_Initialize(): get element from collection") < 0)
                return -1;
            table = (udt_MessageTable*)
                    g_MessageTableType.tp_alloc(&g_MessageTableType, 0);
            if (!table)
                return -1;
            PyList_SET_ITEM(self->tables, i, (PyObject*) table);
            if (MessageTable_Initialize(table, env, *tableDescriptor) < 0)
                return -1;
        }
    }

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    if (self->type == OCI_EVENT_QUERYCHANGE) {
        // determine query collection
        status = OCIAttrGet(descriptor, OCI_DTYPE_CHDES, &queries, NULL,
                OCI_ATTR_CHDES_QUERIES, env->errorHandle);
        if (Environment_CheckForError(env, status,
                "Message_Initialize(): get queries collection") < 0)
            return -1;

        // determine number of queries
        if (!queries)
            numQueries = 0;
        else {
            status = OCICollSize(env->handle, env->errorHandle, queries,
                    &numQueries);
            if (Environment_CheckForError(env, status,
                    "Message_Initialize(): get size of collection") < 0)
                return -1;
        }

        // create list to hold results
        self->queries = PyList_New(numQueries);
        if (!self->queries)
            return -1;

        // populate each entry with a message query instance
        for (i = 0; i < numQueries; i++) {
            status = OCICollGetElem(env->handle, env->errorHandle, queries, i,
                    &exists, (dvoid*) &queryDescriptor, &indicator);
            if (Environment_CheckForError(env, status,
                    "Message_Initialize(): get element from collection") < 0)
                return -1;
            query = (udt_MessageQuery*)
                    g_MessageQueryType.tp_alloc(&g_MessageQueryType, 0);
            if (!query)
                return -1;
            PyList_SET_ITEM(self->queries, i, (PyObject*) query);
            if (MessageQuery_Initialize(query, env, *queryDescriptor) < 0)
                return -1;
        }
    }
#endif

    return 0;
}


//-----------------------------------------------------------------------------
// Subscription_CallbackHandler()
//   Routine that performs the actual call.
//-----------------------------------------------------------------------------
static int Subscription_CallbackHandler(
    udt_Subscription *self,             // subscription object
    udt_Environment *env,               // environment to use
    dvoid *descriptor)                  // descriptor to get information from
{
    PyObject *result, *args;
    udt_Message *message;

    // create the message
    message = (udt_Message*) g_MessageType.tp_alloc(&g_MessageType, 0);
    if (!message)
        return -1;
    if (Message_Initialize(message, env, self, descriptor) < 0) {
        Py_DECREF(message);
        return -1;
    }

    // create the arguments for the call
    args = PyTuple_Pack(1, message);
    Py_DECREF(message);
    if (!args)
        return -1;

    // make the actual call
    result = PyObject_Call(self->callback, args, NULL);
    Py_DECREF(args);
    if (!result)
        return -1;
    Py_DECREF(result);

    return 0;
}


//-----------------------------------------------------------------------------
// Subscription_Callback()
//   Routine that is called when a callback needs to be invoked.
//-----------------------------------------------------------------------------
static void Subscription_Callback(
    udt_Subscription *self,             // subscription object
    OCISubscription *handle,            // subscription handle
    dvoid *payload,                     // payload
    ub4 *payloadLength,                 // payload length
    dvoid *descriptor,                  // descriptor
    ub4 mode)                           // mode used
{
#ifdef WITH_THREAD
    PyGILState_STATE gstate = PyGILState_Ensure();
#endif
    udt_Environment *env;

    // perform the call
    env = Environment_NewFromScratch(0, 0, NULL, NULL);
    if (!env)
        PyErr_Print();
    else {
        if (Subscription_CallbackHandler(self, env, descriptor) < 0)
            PyErr_Print();
        Py_DECREF(env);
    }

    // restore thread state, if necessary
#ifdef WITH_THREAD
    PyGILState_Release(gstate);
#endif
}


//-----------------------------------------------------------------------------
// Subscription_Register()
//   Register the subscription.
//-----------------------------------------------------------------------------
static int Subscription_Register(
    udt_Subscription *self)             // subscription to register
{
    udt_Environment *env;
    sword status;

    // create the subscription handle
    env = self->connection->environment;
    status = OCIHandleAlloc(env->handle, (dvoid**) &self->handle,
            OCI_HTYPE_SUBSCRIPTION, 0, 0);
    if (Environment_CheckForError(env, status,
            "Subscription_Register(): allocate handle") < 0)
        return -1;

    // set the namespace
    status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
            (dvoid*) &self->namespace, sizeof(ub4), OCI_ATTR_SUBSCR_NAMESPACE,
            env->errorHandle);
    if (Environment_CheckForError(env, status,
            "Subscription_Register(): set namespace") < 0)
        return -1;

    // set the protocol
    status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
            (dvoid*) &self->protocol, sizeof(ub4), OCI_ATTR_SUBSCR_RECPTPROTO,
            env->errorHandle);
    if (Environment_CheckForError(env, status,
            "Subscription_Register(): set protocol") < 0)
        return -1;

    // set the timeout
    status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
            (dvoid*) &self->timeout, sizeof(ub4), OCI_ATTR_SUBSCR_TIMEOUT,
            env->errorHandle);
    if (Environment_CheckForError(env, status,
            "Subscription_Register(): set timeout") < 0)
        return -1;

    // set the TCP port used on client to listen for callback from DB server
    if (self->port > 0) {
        status = OCIAttrSet(env->handle, OCI_HTYPE_ENV,
                (dvoid*) &(self->port), (ub4) 0, OCI_ATTR_SUBSCR_PORTNO,
                env->errorHandle);
        if (Environment_CheckForError(env, status,
                "Subscription_Register(): set port") < 0)
            return -1;
    }

    // set the context for the callback
    status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
            (dvoid*) self, 0, OCI_ATTR_SUBSCR_CTX, env->errorHandle);
    if (Environment_CheckForError(env, status,
                "Subscription_Register(): set context") < 0)
        return -1;

    // set the callback, if applicable
    if (self->callback) {
        status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
                (dvoid*) Subscription_Callback, 0, OCI_ATTR_SUBSCR_CALLBACK,
                env->errorHandle);
        if (Environment_CheckForError(env, status,
                    "Subscription_Register(): set callback") < 0)
            return -1;
    }

    // set suscription QOS
    status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
            (dvoid*) &self->qos, sizeof(ub4), OCI_ATTR_SUBSCR_QOSFLAGS,
            env->errorHandle);
    if (Environment_CheckForError(env, status,
                "Subscription_Register(): set qos flags") < 0)
        return -1;

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    // set subscription change notification QOS flags
    status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
            (dvoid*) &self->cqqos, sizeof(ub4), OCI_ATTR_SUBSCR_CQ_QOSFLAGS,
            env->errorHandle);
    if (Environment_CheckForError(env, status,
                "Subscription_Register(): set cq qos flags") < 0)
        return -1;
#endif

    // set whether or not rowids are desired
    status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
            (dvoid*) &self->rowids, sizeof(ub4), OCI_ATTR_CHNF_ROWIDS,
            env->errorHandle);
    if (Environment_CheckForError(env, status,
                "Subscription_Register(): set rowids") < 0)
        return -1;

    // set which operations are desired
    status = OCIAttrSet(self->handle, OCI_HTYPE_SUBSCRIPTION,
            (dvoid*) &self->operations, sizeof(ub4), OCI_ATTR_CHNF_OPERATIONS,
            env->errorHandle);
    if (Environment_CheckForError(env, status,
                "Subscription_Register(): set operations") < 0)
        return -1;

    // register the subscription
    Py_BEGIN_ALLOW_THREADS
    status = OCISubscriptionRegister(self->connection->handle,
            &self->handle, 1, env->errorHandle, OCI_DEFAULT);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(env, status,
                "Subscription_Register(): register") < 0)
        return -1;

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    // get the registration id
    status = OCIAttrGet(self->handle, OCI_HTYPE_SUBSCRIPTION, &self->id,
              NULL, OCI_ATTR_SUBSCR_CQ_REGID, env->errorHandle);
    if (Environment_CheckForError(env, status,
                "Subscription_Register(): get registration id") < 0) {
        return -1;
    }
#endif

    return 0;
}


//-----------------------------------------------------------------------------
// Subscription_New()
//   Allocate a new subscription object.
//-----------------------------------------------------------------------------
static udt_Subscription *Subscription_New(
    udt_Connection *connection,         // connection object
    ub4 namespace,                      // namespace to use
    ub4 protocol,                       // protocol to use
    ub4 port,                           // client port for callbacks
    PyObject *callback,                 // callback routine
    ub4 timeout,                        // timeout (in seconds)
    ub4 operations,                     // operations to notify
    ub4 qos,                            // QOS flags
    ub4 cqqos,                          // change notification QOS flags
    int rowids)                         // retrieve rowids?
{
    udt_Subscription *self;

    self = (udt_Subscription*)
            g_SubscriptionType.tp_alloc(&g_SubscriptionType, 0);
    if (!self)
        return NULL;
    Py_INCREF(connection);
    self->connection = connection;
    Py_XINCREF(callback);
    self->callback = callback;
    self->namespace = namespace;
    self->protocol = protocol;
    self->port = port;
    self->timeout = timeout;
    self->rowids = rowids;
    self->operations = operations;
    self->qos = qos;
    self->cqqos = cqqos;
    self->handle = NULL;
    self->id = 0;
    if (Subscription_Register(self) < 0) {
        Py_DECREF(self);
        return NULL;
    }

    return self;
}


//-----------------------------------------------------------------------------
// Subscription_Free()
//   Free the memory associated with a subscription.
//-----------------------------------------------------------------------------
static void Subscription_Free(
    udt_Subscription *self)               // subscription to free
{
    if (self->handle)
        OCISubscriptionUnRegister(self->connection->handle,
                self->handle, self->connection->environment->errorHandle,
                OCI_DEFAULT);
    Py_CLEAR(self->connection);
    Py_CLEAR(self->callback);
    Py_TYPE(self)->tp_free((PyObject*) self);
}


//-----------------------------------------------------------------------------
// Subscription_Repr()
//   Return a string representation of the subscription.
//-----------------------------------------------------------------------------
static PyObject *Subscription_Repr(
    udt_Subscription *subscription)     // subscription to repr
{
    PyObject *connectionRepr, *module, *name, *result, *format, *formatArgs;

    format = cxString_FromAscii("<%s.%s on %s>");
    if (!format)
        return NULL;
    connectionRepr = PyObject_Repr((PyObject*) subscription->connection);
    if (!connectionRepr) {
        Py_DECREF(format);
        return NULL;
    }
    if (GetModuleAndName(Py_TYPE(subscription), &module, &name) < 0) {
        Py_DECREF(format);
        Py_DECREF(connectionRepr);
        return NULL;
    }
    formatArgs = PyTuple_Pack(3, module, name, connectionRepr);
    Py_DECREF(module);
    Py_DECREF(name);
    Py_DECREF(connectionRepr);
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
// Subscription_RegisterQuery()
//   Register a query for database change notification.
//-----------------------------------------------------------------------------
static PyObject *Subscription_RegisterQuery(
    udt_Subscription *self,             // subscription to use
    PyObject *args)                     // arguments
{
    PyObject *statement, *executeArgs;
    udt_Buffer statementBuffer;
    udt_Environment *env;
    udt_Cursor *cursor;
#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    ub8 queryid;
#endif
    sword status;

    // parse arguments
    executeArgs = NULL;
    if (!PyArg_ParseTuple(args, "O!|O", cxString_Type, &statement,
            &executeArgs))
        return NULL;
    if (executeArgs) {
        if (!PyDict_Check(executeArgs) && !PySequence_Check(executeArgs)) {
            PyErr_SetString(PyExc_TypeError,
                    "expecting a dictionary or sequence");
            return NULL;
        }
    }

    // create cursor to perform query
    env = self->connection->environment;
    cursor = (udt_Cursor*) Connection_NewCursor(self->connection, NULL);
    if (!cursor)
        return NULL;

    // allocate the handle so the subscription handle can be set
    if (Cursor_AllocateHandle(cursor) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }

    // prepare the statement for execution
    if (cxBuffer_FromObject(&statementBuffer, statement,
            env->encoding) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }
    status = OCIStmtPrepare(cursor->handle, env->errorHandle,
            (text*) statementBuffer.ptr, statementBuffer.size, OCI_NTV_SYNTAX,
            OCI_DEFAULT);
    cxBuffer_Clear(&statementBuffer);
    if (Environment_CheckForError(env, status,
            "Subscription_RegisterQuery(): prepare statement") < 0) {
        Py_DECREF(cursor);
        return NULL;
    }

    // perform binds
    if (executeArgs && Cursor_SetBindVariables(cursor, executeArgs, 1, 0,
            0) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }
    if (Cursor_PerformBind(cursor) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }

    // parse the query in order to get the defined variables
    Py_BEGIN_ALLOW_THREADS
    status = OCIStmtExecute(self->connection->handle, cursor->handle,
            env->errorHandle, 0, 0, 0, 0, OCI_DESCRIBE_ONLY);
    Py_END_ALLOW_THREADS
    if (Environment_CheckForError(env, status,
            "Subscription_RegisterQuery(): parse statement") < 0) {
        Py_DECREF(cursor);
        return NULL;
    }

    // perform define as needed
    if (Cursor_PerformDefine(cursor) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }

    // set the subscription handle
    status = OCIAttrSet(cursor->handle, OCI_HTYPE_STMT, self->handle, 0,
            OCI_ATTR_CHNF_REGHANDLE, env->errorHandle);
    if (Environment_CheckForError(env, status,
                "Subscription_RegisterQuery(): set subscription handle") < 0) {
        Py_DECREF(cursor);
        return NULL;
    }

    // execute the query which registers it
    if (Cursor_InternalExecute(cursor, 0, 0) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    if (self->cqqos & OCI_SUBSCR_CQ_QOS_QUERY) {
        // get the query id
        status = OCIAttrGet(cursor->handle, OCI_HTYPE_STMT, &queryid, NULL,
                OCI_ATTR_CQ_QUERYID, env->errorHandle);
        if (Environment_CheckForError(env, status,
                    "Subscription_RegisterQuery(): get query id") < 0) {
            Py_DECREF(cursor);
            return NULL;
        }
    }
#endif

    Py_DECREF(cursor);

#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
    if (self->cqqos & OCI_SUBSCR_CQ_QOS_QUERY)
        return PyInt_FromLong(queryid);
#endif

    Py_INCREF(Py_None);
    return Py_None;
}


//-----------------------------------------------------------------------------
// Message_Free()
//   Free the memory associated with a message.
//-----------------------------------------------------------------------------
static void Message_Free(
    udt_Message *self)                  // object to free
{
    Py_CLEAR(self->subscription);
    Py_CLEAR(self->dbname);
    Py_CLEAR(self->tables);
    Py_CLEAR(self->queries);
    Py_TYPE(self)->tp_free((PyObject*) self);
}


//-----------------------------------------------------------------------------
// MessageTable_Free()
//   Free the memory associated with a table in a message.
//-----------------------------------------------------------------------------
static void MessageTable_Free(
    udt_MessageTable *self)             // object to free
{
    Py_CLEAR(self->name);
    Py_CLEAR(self->rows);
    Py_TYPE(self)->tp_free((PyObject*) self);
}


//-----------------------------------------------------------------------------
// MessageRow_Free()
//   Free the memory associated with a row in a message.
//-----------------------------------------------------------------------------
static void MessageRow_Free(
    udt_MessageRow *self)               // object to free
{
    Py_CLEAR(self->rowid);
    Py_TYPE(self)->tp_free((PyObject*) self);
}


#if ORACLE_VERSION_HEX >= ORACLE_VERSION(11, 1)
//-----------------------------------------------------------------------------
// MessageQuery_Free()
//   Free the memory associated with a query in a message.
//-----------------------------------------------------------------------------
static void MessageQuery_Free(
    udt_MessageQuery *self)               // object to free
{
    Py_CLEAR(self->tables);
    Py_TYPE(self)->tp_free((PyObject*) self);
}
#endif

