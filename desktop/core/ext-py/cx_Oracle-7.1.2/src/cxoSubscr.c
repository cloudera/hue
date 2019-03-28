//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoSubscr.c
//   Defines the routines for handling Oracle subscription information.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// Declaration of subscription functions
//-----------------------------------------------------------------------------
static void cxoSubscr_free(cxoSubscr*);
static PyObject *cxoSubscr_repr(cxoSubscr*);
static PyObject *cxoSubscr_registerQuery(cxoSubscr*, PyObject*);
static void cxoMessage_free(cxoMessage*);
static void cxoMessageTable_free(cxoMessageTable*);
static void cxoMessageRow_free(cxoMessageRow*);
static void cxoMessageQuery_free(cxoMessageQuery*);

//-----------------------------------------------------------------------------
// declaration of members for Python types
//-----------------------------------------------------------------------------
static PyMemberDef cxoSubscrTypeMembers[] = {
    { "callback", T_OBJECT, offsetof(cxoSubscr, callback), READONLY },
    { "connection", T_OBJECT, offsetof(cxoSubscr, connection),
            READONLY },
    { "namespace", T_UINT, offsetof(cxoSubscr, namespace), READONLY },
    { "name", T_OBJECT, offsetof(cxoSubscr, name), READONLY },
    { "protocol", T_UINT, offsetof(cxoSubscr, protocol), READONLY },
    { "ipAddress", T_OBJECT, offsetof(cxoSubscr, ipAddress), READONLY },
    { "port", T_UINT, offsetof(cxoSubscr, port), READONLY },
    { "timeout", T_UINT, offsetof(cxoSubscr, timeout), READONLY },
    { "operations", T_UINT, offsetof(cxoSubscr, operations), READONLY },
    { "qos", T_UINT, offsetof(cxoSubscr, qos), READONLY },
    { "id", T_ULONG, offsetof(cxoSubscr, id), READONLY },
    { NULL }
};

static PyMemberDef cxoMessageTypeMembers[] = {
    { "subscription", T_OBJECT, offsetof(cxoMessage, subscription),
            READONLY },
    { "type", T_INT, offsetof(cxoMessage, type), READONLY },
    { "dbname", T_OBJECT, offsetof(cxoMessage, dbname), READONLY },
    { "txid", T_OBJECT, offsetof(cxoMessage, txId), READONLY },
    { "tables", T_OBJECT, offsetof(cxoMessage, tables), READONLY },
    { "queries", T_OBJECT, offsetof(cxoMessage, queries), READONLY },
    { "queueName", T_OBJECT, offsetof(cxoMessage, queueName), READONLY },
    { "consumerName", T_OBJECT, offsetof(cxoMessage, consumerName), READONLY },
    { "registered", T_BOOL, offsetof(cxoMessage, registered), READONLY },
    { NULL }
};

static PyMemberDef cxoMessageTableTypeMembers[] = {
    { "name", T_OBJECT, offsetof(cxoMessageTable, name), READONLY },
    { "rows", T_OBJECT, offsetof(cxoMessageTable, rows), READONLY },
    { "operation", T_INT, offsetof(cxoMessageTable, operation), READONLY },
    { NULL }
};

static PyMemberDef cxoMessageRowTypeMembers[] = {
    { "rowid", T_OBJECT, offsetof(cxoMessageRow, rowid), READONLY },
    { "operation", T_INT, offsetof(cxoMessageRow, operation), READONLY },
    { NULL }
};

static PyMemberDef cxoMessageQueryTypeMembers[] = {
    { "id", T_INT, offsetof(cxoMessageQuery, id), READONLY },
    { "operation", T_INT, offsetof(cxoMessageQuery, operation), READONLY },
    { "tables", T_OBJECT, offsetof(cxoMessageQuery, tables), READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of methods for Python types
//-----------------------------------------------------------------------------
static PyMethodDef cxoSubscrTypeMethods[] = {
    { "registerquery", (PyCFunction) cxoSubscr_registerQuery,
            METH_VARARGS },
    { NULL, NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeSubscr = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.Subscription",           // tp_name
    sizeof(cxoSubscr),                  // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoSubscr_free,        // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoSubscr_repr,          // tp_repr
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
    cxoSubscrTypeMethods,               // tp_methods
    cxoSubscrTypeMembers,               // tp_members
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

PyTypeObject cxoPyTypeMessage = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.Message",                // tp_name
    sizeof(cxoMessage),                 // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoMessage_free,       // tp_dealloc
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
    cxoMessageTypeMembers,              // tp_members
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

PyTypeObject cxoPyTypeMessageTable = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.MessageTable",           // tp_name
    sizeof(cxoMessageTable),            // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoMessageTable_free,  // tp_dealloc
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
    cxoMessageTableTypeMembers,         // tp_members
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


PyTypeObject cxoPyTypeMessageRow = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.MessageRow",             // tp_name
    sizeof(cxoMessageRow),              // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoMessageRow_free,    // tp_dealloc
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
    cxoMessageRowTypeMembers,           // tp_members
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


PyTypeObject cxoPyTypeMessageQuery = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.MessageQuery",           // tp_name
    sizeof(cxoMessageQuery),            // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoMessageQuery_free,  // tp_dealloc
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
    cxoMessageQueryTypeMembers,         // tp_members
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
// cxoMessageRow_initialize()
//   Initialize a new message row with the information from the descriptor.
//-----------------------------------------------------------------------------
static int cxoMessageRow_initialize(cxoMessageRow *rowObj,
        const char *encoding, dpiSubscrMessageRow *row)
{
    rowObj->operation = row->operation;
    rowObj->rowid = cxoPyString_fromEncodedString(row->rowid, row->rowidLength,
            encoding, NULL);
    if (!rowObj->rowid)
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// cxoMessageTable_initialize()
//   Initialize a new message table with the information from the descriptor.
//-----------------------------------------------------------------------------
static int cxoMessageTable_initialize(cxoMessageTable *tableObj,
        const char *encoding, dpiSubscrMessageTable *table)
{
    cxoMessageRow *row;
    uint32_t i;

    tableObj->operation = table->operation;
    tableObj->name = cxoPyString_fromEncodedString(table->name,
            table->nameLength, encoding, NULL);
    tableObj->rows = PyList_New(table->numRows);
    if (!tableObj->rows)
        return -1;
    for (i = 0; i < table->numRows; i++) {
        row = (cxoMessageRow*)
                cxoPyTypeMessageRow.tp_alloc(&cxoPyTypeMessageRow, 0);
        if (!row)
            return -1;
        PyList_SET_ITEM(tableObj->rows, i, (PyObject*) row);
        if (cxoMessageRow_initialize(row, encoding, &table->rows[i]) < 0)
            return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoMessageQuery_initialize()
//   Initialize a new message query with the information from the descriptor.
//-----------------------------------------------------------------------------
static int cxoMessageQuery_initialize(cxoMessageQuery *queryObj,
        const char *encoding, dpiSubscrMessageQuery *query)
{
    cxoMessageTable *table;
    uint32_t i;

    queryObj->id = query->id;
    queryObj->operation = query->operation;
    queryObj->tables = PyList_New(query->numTables);
    if (!queryObj->tables)
        return -1;
    for (i = 0; i < query->numTables; i++) {
        table = (cxoMessageTable*)
                cxoPyTypeMessageTable.tp_alloc(&cxoPyTypeMessageTable, 0);
        if (!table)
            return -1;
        PyList_SET_ITEM(queryObj->tables, i, (PyObject*) table);
        if (cxoMessageTable_initialize(table, encoding, &query->tables[i]) < 0)
            return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoMessage_initialize()
//   Initialize a new message with the information from the descriptor.
//-----------------------------------------------------------------------------
static int cxoMessage_initialize(cxoMessage *messageObj,
        cxoSubscr *subscription, dpiSubscrMessage *message)
{
    cxoMessageTable *table;
    cxoMessageQuery *query;
    const char *encoding;
    uint32_t i;

    Py_INCREF(subscription);
    messageObj->subscription = subscription;
    encoding = subscription->connection->encodingInfo.encoding;
    messageObj->type = message->eventType;
    messageObj->registered = message->registered;
    messageObj->dbname = cxoPyString_fromEncodedString(message->dbName,
            message->dbNameLength, encoding, NULL);
    if (!messageObj->dbname)
        return -1;
    if (message->txId) {
        messageObj->txId = PyBytes_FromStringAndSize(message->txId,
                message->txIdLength);
        if (!messageObj->txId)
            return -1;
    }
    if (message->queueName) {
        messageObj->queueName = cxoPyString_fromEncodedString(
                message->queueName, message->queueNameLength, encoding, NULL);
        if (!messageObj->queueName)
            return -1;
    }
    if (message->consumerName) {
        messageObj->consumerName = cxoPyString_fromEncodedString(
                message->consumerName, message->consumerNameLength, encoding,
                NULL);
        if (!messageObj->consumerName)
            return -1;
    }
    switch (message->eventType) {
        case DPI_EVENT_OBJCHANGE:
            messageObj->tables = PyList_New(message->numTables);
            if (!messageObj->tables)
                return -1;
            for (i = 0; i < message->numTables; i++) {
                table = (cxoMessageTable*)
                        cxoPyTypeMessageTable.tp_alloc(&cxoPyTypeMessageTable,
                                0);
                if (!table)
                    return -1;
                PyList_SET_ITEM(messageObj->tables, i, (PyObject*) table);
                if (cxoMessageTable_initialize(table, encoding,
                        &message->tables[i]) < 0)
                    return -1;
            }
            break;
        case DPI_EVENT_QUERYCHANGE:
            messageObj->queries = PyList_New(message->numQueries);
            if (!messageObj->queries)
                return -1;
            for (i = 0; i < message->numQueries; i++) {
                query = (cxoMessageQuery*)
                        cxoPyTypeMessageQuery.tp_alloc(&cxoPyTypeMessageQuery,
                                0);
                if (!query)
                    return -1;
                PyList_SET_ITEM(messageObj->queries, i, (PyObject*) query);
                if (cxoMessageQuery_initialize(query, encoding,
                        &message->queries[i]) < 0)
                    return -1;
            }
            break;
        default:
            break;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoSubscr_callbackHandler()
//   Routine that performs the actual call.
//-----------------------------------------------------------------------------
static int cxoSubscr_callbackHandler(cxoSubscr *subscr,
        dpiSubscrMessage *message)
{
    PyObject *result, *args;
    cxoMessage *messageObj;

    // create the message
    messageObj = (cxoMessage*) cxoPyTypeMessage.tp_alloc(&cxoPyTypeMessage, 0);
    if (!messageObj)
        return -1;
    if (cxoMessage_initialize(messageObj, subscr, message) < 0) {
        Py_DECREF(messageObj);
        return -1;
    }

    // create the arguments for the call
    args = PyTuple_Pack(1, messageObj);
    Py_DECREF(messageObj);
    if (!args)
        return -1;

    // make the actual call
    result = PyObject_Call(subscr->callback, args, NULL);
    Py_DECREF(args);
    if (!result)
        return -1;
    Py_DECREF(result);

    return 0;
}


//-----------------------------------------------------------------------------
// cxoSubscr_callback()
//   Routine that is called when a callback needs to be invoked.
//-----------------------------------------------------------------------------
void cxoSubscr_callback(cxoSubscr *subscr, dpiSubscrMessage *message)
{
#ifdef WITH_THREAD
    PyGILState_STATE gstate = PyGILState_Ensure();
#endif

    if (message->errorInfo) {
        cxoError_raiseFromInfo(message->errorInfo);
        PyErr_Print();
    } else if (cxoSubscr_callbackHandler(subscr, message) < 0)
        PyErr_Print();

#ifdef WITH_THREAD
    PyGILState_Release(gstate);
#endif
}


//-----------------------------------------------------------------------------
// cxoSubscr_free()
//   Free the memory associated with a subscription.
//-----------------------------------------------------------------------------
static void cxoSubscr_free(cxoSubscr *subscr)
{
    if (subscr->handle) {
        dpiSubscr_release(subscr->handle);
        subscr->handle = NULL;
    }
    Py_CLEAR(subscr->connection);
    Py_CLEAR(subscr->callback);
    Py_CLEAR(subscr->name);
    Py_CLEAR(subscr->ipAddress);
    Py_TYPE(subscr)->tp_free((PyObject*) subscr);
}


//-----------------------------------------------------------------------------
// cxoSubscr_repr()
//   Return a string representation of the subscription.
//-----------------------------------------------------------------------------
static PyObject *cxoSubscr_repr(cxoSubscr *subscription)
{
    PyObject *connectionRepr, *module, *name, *result;

    connectionRepr = PyObject_Repr((PyObject*) subscription->connection);
    if (!connectionRepr)
        return NULL;
    if (cxoUtils_getModuleAndName(Py_TYPE(subscription), &module, &name) < 0) {
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
// cxoSubscr_registerQuery()
//   Register a query for database change notification.
//-----------------------------------------------------------------------------
static PyObject *cxoSubscr_registerQuery(cxoSubscr *subscr,
        PyObject *args)
{
    PyObject *statement, *executeArgs;
    cxoBuffer statementBuffer;
    uint32_t numQueryColumns;
    cxoCursor *cursor;
    uint64_t queryId;
    int status;

    // parse arguments
    executeArgs = NULL;
    if (!PyArg_ParseTuple(args, "O|O", &statement, &executeArgs))
        return NULL;
    if (executeArgs) {
        if (!PyDict_Check(executeArgs) && !PySequence_Check(executeArgs)) {
            PyErr_SetString(PyExc_TypeError,
                    "expecting a dictionary or sequence");
            return NULL;
        }
    }

    // create cursor to perform query
    cursor = (cxoCursor*) PyObject_CallMethod((PyObject*) subscr->connection,
            "cursor", NULL);
    if (!cursor)
        return NULL;

    // prepare the statement for execution
    if (cxoBuffer_fromObject(&statementBuffer, statement,
            subscr->connection->encodingInfo.encoding) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }
    status = dpiSubscr_prepareStmt(subscr->handle, statementBuffer.ptr,
            statementBuffer.size, &cursor->handle);
    cxoBuffer_clear(&statementBuffer);
    if (status < 0) {
        cxoError_raiseAndReturnNull();
        Py_DECREF(cursor);
        return NULL;
    }

    // perform binds
    if (executeArgs && cxoCursor_setBindVariables(cursor, executeArgs, 1, 0,
            0) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }
    if (cxoCursor_performBind(cursor) < 0) {
        Py_DECREF(cursor);
        return NULL;
    }

    // perform the execute (which registers the query)
    Py_BEGIN_ALLOW_THREADS
    status = dpiStmt_execute(cursor->handle, DPI_MODE_EXEC_DEFAULT,
            &numQueryColumns);
    Py_END_ALLOW_THREADS
    if (status < 0) {
        cxoError_raiseAndReturnNull();
        Py_DECREF(cursor);
        return NULL;
    }

    // return the query id, if applicable
    if (subscr->qos & DPI_SUBSCR_QOS_QUERY) {
        if (dpiStmt_getSubscrQueryId(cursor->handle, &queryId) < 0) {
            cxoError_raiseAndReturnNull();
            Py_DECREF(cursor);
            return NULL;
        }
        Py_DECREF(cursor);
        return PyInt_FromLong((long) queryId);
    }

    Py_DECREF(cursor);
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoMessage_free()
//   Free the memory associated with a message.
//-----------------------------------------------------------------------------
static void cxoMessage_free(cxoMessage *message)
{
    Py_CLEAR(message->subscription);
    Py_CLEAR(message->dbname);
    Py_CLEAR(message->txId);
    Py_CLEAR(message->tables);
    Py_CLEAR(message->queries);
    Py_CLEAR(message->queueName);
    Py_CLEAR(message->consumerName);
    Py_TYPE(message)->tp_free((PyObject*) message);
}


//-----------------------------------------------------------------------------
// cxoMessageQuery_free()
//   Free the memory associated with a query in a message.
//-----------------------------------------------------------------------------
static void cxoMessageQuery_free(cxoMessageQuery *query)
{
    Py_CLEAR(query->tables);
    Py_TYPE(query)->tp_free((PyObject*) query);
}


//-----------------------------------------------------------------------------
// cxoMessageRow_free()
//   Free the memory associated with a row in a message.
//-----------------------------------------------------------------------------
static void cxoMessageRow_free(cxoMessageRow *row)
{
    Py_CLEAR(row->rowid);
    Py_TYPE(row)->tp_free((PyObject*) row);
}


//-----------------------------------------------------------------------------
// cxoMessageTable_free()
//   Free the memory associated with a table in a message.
//-----------------------------------------------------------------------------
static void cxoMessageTable_free(cxoMessageTable *table)
{
    Py_CLEAR(table->name);
    Py_CLEAR(table->rows);
    Py_TYPE(table)->tp_free((PyObject*) table);
}

