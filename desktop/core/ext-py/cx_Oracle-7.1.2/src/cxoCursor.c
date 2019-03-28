//-----------------------------------------------------------------------------
// Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
//
// Portions Copyright 2007-2015, Anthony Tuininga. All rights reserved.
//
// Portions Copyright 2001-2007, Computronix (Canada) Ltd., Edmonton, Alberta,
// Canada. All rights reserved.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// cxoCursor.c
//   Definition of the Python type Cursor.
//-----------------------------------------------------------------------------

#include "cxoModule.h"

//-----------------------------------------------------------------------------
// functions for the Python type "Cursor"
//-----------------------------------------------------------------------------
static void cxoCursor_free(cxoCursor*);
static PyObject *cxoCursor_getIter(cxoCursor*);
static PyObject *cxoCursor_getNext(cxoCursor*);
static PyObject *cxoCursor_close(cxoCursor*, PyObject*);
static PyObject *cxoCursor_callFunc(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_callProc(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_execute(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_executeMany(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_executeManyPrepared(cxoCursor*, PyObject*);
static PyObject *cxoCursor_fetchOne(cxoCursor*, PyObject*);
static PyObject *cxoCursor_fetchMany(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_fetchAll(cxoCursor*, PyObject*);
static PyObject *cxoCursor_fetchRaw(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_parse(cxoCursor*, PyObject*);
static PyObject *cxoCursor_prepare(cxoCursor*, PyObject*);
static PyObject *cxoCursor_scroll(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_setInputSizes(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_setOutputSize(cxoCursor*, PyObject*);
static PyObject *cxoCursor_var(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_arrayVar(cxoCursor*, PyObject*);
static PyObject *cxoCursor_bindNames(cxoCursor*, PyObject*);
static PyObject *cxoCursor_getDescription(cxoCursor*, void*);
static PyObject *cxoCursor_new(PyTypeObject*, PyObject*, PyObject*);
static int cxoCursor_init(cxoCursor*, PyObject*, PyObject*);
static PyObject *cxoCursor_repr(cxoCursor*);
static PyObject* cxoCursor_getBatchErrors(cxoCursor*);
static PyObject *cxoCursor_getArrayDMLRowCounts(cxoCursor*);
static PyObject *cxoCursor_getImplicitResults(cxoCursor*);
static PyObject *cxoCursor_contextManagerEnter(cxoCursor*, PyObject*);
static PyObject *cxoCursor_contextManagerExit(cxoCursor*, PyObject*);
static int cxoCursor_performDefine(cxoCursor*, uint32_t);


//-----------------------------------------------------------------------------
// declaration of methods for Python type "Cursor"
//-----------------------------------------------------------------------------
static PyMethodDef cxoCursorMethods[] = {
    { "execute", (PyCFunction) cxoCursor_execute,
            METH_VARARGS | METH_KEYWORDS },
    { "fetchall", (PyCFunction) cxoCursor_fetchAll, METH_NOARGS },
    { "fetchone", (PyCFunction) cxoCursor_fetchOne, METH_NOARGS },
    { "fetchmany", (PyCFunction) cxoCursor_fetchMany,
              METH_VARARGS | METH_KEYWORDS },
    { "fetchraw", (PyCFunction) cxoCursor_fetchRaw,
              METH_VARARGS | METH_KEYWORDS },
    { "prepare", (PyCFunction) cxoCursor_prepare, METH_VARARGS },
    { "parse", (PyCFunction) cxoCursor_parse, METH_O },
    { "setinputsizes", (PyCFunction) cxoCursor_setInputSizes,
              METH_VARARGS | METH_KEYWORDS },
    { "executemany", (PyCFunction) cxoCursor_executeMany,
              METH_VARARGS | METH_KEYWORDS },
    { "callproc", (PyCFunction) cxoCursor_callProc,
              METH_VARARGS  | METH_KEYWORDS },
    { "callfunc", (PyCFunction) cxoCursor_callFunc,
              METH_VARARGS  | METH_KEYWORDS },
    { "executemanyprepared", (PyCFunction) cxoCursor_executeManyPrepared,
              METH_VARARGS },
    { "setoutputsize", (PyCFunction) cxoCursor_setOutputSize, METH_VARARGS },
    { "scroll", (PyCFunction) cxoCursor_scroll, METH_VARARGS | METH_KEYWORDS },
    { "var", (PyCFunction) cxoCursor_var, METH_VARARGS | METH_KEYWORDS },
    { "arrayvar", (PyCFunction) cxoCursor_arrayVar, METH_VARARGS },
    { "bindnames", (PyCFunction) cxoCursor_bindNames, METH_NOARGS },
    { "close", (PyCFunction) cxoCursor_close, METH_NOARGS },
    { "getbatcherrors", (PyCFunction) cxoCursor_getBatchErrors, METH_NOARGS },
    { "getarraydmlrowcounts", (PyCFunction) cxoCursor_getArrayDMLRowCounts,
              METH_NOARGS },
    { "getimplicitresults", (PyCFunction) cxoCursor_getImplicitResults,
              METH_NOARGS },
    { "__enter__", (PyCFunction) cxoCursor_contextManagerEnter, METH_NOARGS },
    { "__exit__", (PyCFunction) cxoCursor_contextManagerExit, METH_VARARGS },
    { NULL, NULL }
};


//-----------------------------------------------------------------------------
// declaration of members for Python type "Cursor"
//-----------------------------------------------------------------------------
static PyMemberDef cxoCursorMembers[] = {
    { "arraysize", T_UINT, offsetof(cxoCursor, arraySize), 0 },
    { "bindarraysize", T_UINT, offsetof(cxoCursor, bindArraySize), 0 },
    { "rowcount", T_ULONGLONG, offsetof(cxoCursor, rowCount), READONLY },
    { "statement", T_OBJECT, offsetof(cxoCursor, statement), READONLY },
    { "connection", T_OBJECT_EX, offsetof(cxoCursor, connection), READONLY },
    { "rowfactory", T_OBJECT, offsetof(cxoCursor, rowFactory), 0 },
    { "bindvars", T_OBJECT, offsetof(cxoCursor, bindVariables), READONLY },
    { "fetchvars", T_OBJECT, offsetof(cxoCursor, fetchVariables), READONLY },
    { "inputtypehandler", T_OBJECT, offsetof(cxoCursor, inputTypeHandler),
            0 },
    { "outputtypehandler", T_OBJECT, offsetof(cxoCursor, outputTypeHandler),
            0 },
    { "scrollable", T_BOOL, offsetof(cxoCursor, isScrollable), 0 },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of calculated members for Python type "Connection"
//-----------------------------------------------------------------------------
static PyGetSetDef cxoCursorCalcMembers[] = {
    { "description", (getter) cxoCursor_getDescription, 0, 0, 0 },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of Python type "Cursor"
//-----------------------------------------------------------------------------
PyTypeObject cxoPyTypeCursor = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.Cursor",                 // tp_name
    sizeof(cxoCursor),                  // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) cxoCursor_free,        // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_compare
    (reprfunc) cxoCursor_repr,          // tp_repr
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
    (getiterfunc) cxoCursor_getIter,    // tp_iter
    (iternextfunc) cxoCursor_getNext,   // tp_iternext
    cxoCursorMethods,                   // tp_methods
    cxoCursorMembers,                   // tp_members
    cxoCursorCalcMembers,               // tp_getset
    0,                                  // tp_base
    0,                                  // tp_dict
    0,                                  // tp_descr_get
    0,                                  // tp_descr_set
    0,                                  // tp_dictoffset
    (initproc) cxoCursor_init,          // tp_init
    0,                                  // tp_alloc
    cxoCursor_new,                      // tp_new
    0,                                  // tp_free
    0,                                  // tp_is_gc
    0                                   // tp_bases
};


//-----------------------------------------------------------------------------
// cxoCursor_new()
//   Create a new cursor object.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_new(PyTypeObject *type, PyObject *args,
        PyObject *keywordArgs)
{
    return type->tp_alloc(type, 0);
}


//-----------------------------------------------------------------------------
// cxoCursor_init()
//   Create a new cursor object.
//-----------------------------------------------------------------------------
static int cxoCursor_init(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "connection", "scrollable", NULL };
    cxoConnection *connection;
    PyObject *scrollableObj;

    // parse arguments
    scrollableObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O!|O", keywordList,
            &cxoPyTypeConnection, &connection, &scrollableObj))
        return -1;
    if (cxoUtils_getBooleanValue(scrollableObj, 0, &cursor->isScrollable) < 0)
        return -1;

    // initialize members
    Py_INCREF(connection);
    cursor->connection = connection;
    cursor->arraySize = 100;
    cursor->fetchArraySize = 100;
    cursor->bindArraySize = 1;
    cursor->isOpen = 1;

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_repr()
//   Return a string representation of the cursor.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_repr(cxoCursor *cursor)
{
    PyObject *connectionRepr, *module, *name, *result;

    connectionRepr = PyObject_Repr((PyObject*) cursor->connection);
    if (!connectionRepr)
        return NULL;
    if (cxoUtils_getModuleAndName(Py_TYPE(cursor), &module, &name) < 0) {
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
// cxoCursor_free()
//   Deallocate the cursor.
//-----------------------------------------------------------------------------
static void cxoCursor_free(cxoCursor *cursor)
{
    Py_CLEAR(cursor->statement);
    Py_CLEAR(cursor->statementTag);
    Py_CLEAR(cursor->bindVariables);
    Py_CLEAR(cursor->fetchVariables);
    if (cursor->handle) {
        dpiStmt_release(cursor->handle);
        cursor->handle = NULL;
    }
    Py_CLEAR(cursor->connection);
    Py_CLEAR(cursor->rowFactory);
    Py_CLEAR(cursor->inputTypeHandler);
    Py_CLEAR(cursor->outputTypeHandler);
    Py_TYPE(cursor)->tp_free((PyObject*) cursor);
}


//-----------------------------------------------------------------------------
// cxoCursor_isOpen()
//   Determines if the cursor object is open. Since the same cursor can be
// used to execute multiple statements, simply checking for the DPI statement
// handle is insufficient.
//-----------------------------------------------------------------------------
static int cxoCursor_isOpen(cxoCursor *cursor)
{
    if (!cursor->isOpen) {
        cxoError_raiseFromString(cxoInterfaceErrorException, "not open");
        return -1;
    }
    return cxoConnection_isConnected(cursor->connection);
}


//-----------------------------------------------------------------------------
// cxoCursor_verifyFetch()
//   Verify that fetching may happen from this cursor.
//-----------------------------------------------------------------------------
static int cxoCursor_verifyFetch(cxoCursor *cursor)
{
    uint32_t numQueryColumns;

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return -1;

    // fixup REF cursor, if applicable
    if (cursor->fixupRefCursor) {
        cursor->fetchArraySize = cursor->arraySize;
        if (dpiStmt_setFetchArraySize(cursor->handle,
                cursor->fetchArraySize) < 0)
            return cxoError_raiseAndReturnInt();
        if (dpiStmt_getNumQueryColumns(cursor->handle, &numQueryColumns) < 0)
            return cxoError_raiseAndReturnInt();
        if (cxoCursor_performDefine(cursor, numQueryColumns) < 0)
            return cxoError_raiseAndReturnInt();
        cursor->fixupRefCursor = 0;
    }

    // make sure the cursor is for a query
    if (!cursor->fetchVariables) {
        cxoError_raiseFromString(cxoInterfaceErrorException, "not a query");
        return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_fetchRow()
//   Fetch a single row from the cursor. Internally the number of rows left in
// the buffer is managed in order to minimize calls to Py_BEGIN_ALLOW_THREADS
// and Py_END_ALLOW_THREADS which have a significant overhead.
//-----------------------------------------------------------------------------
static int cxoCursor_fetchRow(cxoCursor *cursor, int *found,
        uint32_t *bufferRowIndex)
{
    int status;

    // if the number of rows in the fetch buffer is zero and there are more
    // rows to fetch, call DPI with threading enabled in order to perform any
    // fetch requiring a network round trip
    if (cursor->numRowsInFetchBuffer == 0 && cursor->moreRowsToFetch) {
        Py_BEGIN_ALLOW_THREADS
        status = dpiStmt_fetchRows(cursor->handle, cursor->fetchArraySize,
                &cursor->fetchBufferRowIndex, &cursor->numRowsInFetchBuffer,
                &cursor->moreRowsToFetch);
        Py_END_ALLOW_THREADS
        if (status < 0)
            return cxoError_raiseAndReturnInt();
    }

    // keep track of where we are in the fetch buffer
    if (cursor->numRowsInFetchBuffer == 0)
        *found = 0;
    else {
        *found = 1;
        *bufferRowIndex = cursor->fetchBufferRowIndex++;
        cursor->numRowsInFetchBuffer--;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_performDefine()
//   Perform the defines for the cursor. At this point it is assumed that the
// statement being executed is in fact a query.
//-----------------------------------------------------------------------------
static int cxoCursor_performDefine(cxoCursor *cursor, uint32_t numQueryColumns)
{
    PyObject *outputTypeHandler, *result;
    cxoObjectType *objectType;
    cxoVarType *varType;
    dpiQueryInfo queryInfo;
    uint32_t pos, size;
    cxoVar *var;

    // initialize fetching variables; these are used to reduce the number of
    // times that Py_BEGIN_ALLOW_THREADS/Py_END_ALLOW_THREADS is called as
    // there is a significant amount of overhead in making these calls
    cursor->numRowsInFetchBuffer = 0;
    cursor->moreRowsToFetch = 1;

    // if fetch variables already exist, nothing more to do (we are executing
    // the same statement and therefore all defines have already been
    // performed)
    if (cursor->fetchVariables)
        return 0;

    // create a list corresponding to the number of items
    cursor->fetchVariables = PyList_New(numQueryColumns);
    if (!cursor->fetchVariables)
        return -1;

    // create a variable for each of the query columns
    cursor->fetchArraySize = cursor->arraySize;
    for (pos = 1; pos <= numQueryColumns; pos++) {

        // get query information for the column position
        if (dpiStmt_getQueryInfo(cursor->handle, pos, &queryInfo) < 0)
            return cxoError_raiseAndReturnInt();
        if (queryInfo.typeInfo.sizeInChars)
            size = queryInfo.typeInfo.sizeInChars;
        else size = queryInfo.typeInfo.clientSizeInBytes;

        // determine object type, if applicable
        objectType = NULL;
        if (queryInfo.typeInfo.objectType) {
            objectType = cxoObjectType_new(cursor->connection,
                    queryInfo.typeInfo.objectType);
            if (!objectType)
                return -1;
        }

        // determine the default type 
        varType = cxoVarType_fromDataTypeInfo(&queryInfo.typeInfo);
        if (!varType)
            return -1;

        // see if an output type handler should be used
        var = NULL;
        outputTypeHandler = NULL;
        if (cursor->outputTypeHandler && cursor->outputTypeHandler != Py_None)
            outputTypeHandler = cursor->outputTypeHandler;
        else if (cursor->connection->outputTypeHandler &&
                cursor->connection->outputTypeHandler != Py_None)
            outputTypeHandler = cursor->connection->outputTypeHandler;

        // if using an output type handler, None implies default behavior
        if (outputTypeHandler) {
            result = PyObject_CallFunction(outputTypeHandler, "Os#Oiii",
                    cursor, queryInfo.name, queryInfo.nameLength,
                    varType->pythonType, size, queryInfo.typeInfo.precision,
                    queryInfo.typeInfo.scale);
            if (!result) {
                Py_XDECREF(objectType);
                return -1;
            } else if (result == Py_None)
                Py_DECREF(result);
            else if (!cxoVar_check(result)) {
                Py_DECREF(result);
                Py_XDECREF(objectType);
                PyErr_SetString(PyExc_TypeError,
                        "expecting variable from output type handler");
                return -1;
            } else {
                var = (cxoVar*) result;
                if (var->allocatedElements < cursor->fetchArraySize) {
                    Py_DECREF(result);
                    Py_XDECREF(objectType);
                    PyErr_SetString(PyExc_TypeError,
                            "expecting variable with array size large "
                            "enough for fetch");
                    return -1;
                }
            }
        }

        // if no variable created yet, use the database metadata
        if (!var) {
            var = cxoVar_new(cursor, cursor->fetchArraySize, varType, size, 0,
                    objectType);
            if (!var) {
                Py_XDECREF(objectType);
                return -1;
            }
        }

        // add the variable to the fetch variables and perform define
        Py_XDECREF(objectType);
        PyList_SET_ITEM(cursor->fetchVariables, pos - 1, (PyObject *) var);
        if (dpiStmt_define(cursor->handle, pos, var->handle) < 0)
            return cxoError_raiseAndReturnInt();

    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_itemDescription()
//   Return a tuple describing the item at the given position.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_itemDescription(cxoCursor *cursor, uint32_t pos)
{
    cxoVarType *varType;
    int displaySize, index;
    dpiQueryInfo queryInfo;
    PyObject *tuple, *temp;

    // get information about the column position
    if (dpiStmt_getQueryInfo(cursor->handle, pos, &queryInfo) < 0)
        return NULL;
    varType = cxoVarType_fromDataTypeInfo(&queryInfo.typeInfo);
    if (!varType)
        return NULL;

    // set display size based on data type
    switch (queryInfo.typeInfo.oracleTypeNum) {
        case DPI_ORACLE_TYPE_VARCHAR:
        case DPI_ORACLE_TYPE_NVARCHAR:
        case DPI_ORACLE_TYPE_CHAR:
        case DPI_ORACLE_TYPE_NCHAR:
        case DPI_ORACLE_TYPE_ROWID:
            displaySize = (int) queryInfo.typeInfo.sizeInChars;
            break;
        case DPI_ORACLE_TYPE_RAW:
            displaySize = (int) queryInfo.typeInfo.clientSizeInBytes;
            break;
        case DPI_ORACLE_TYPE_NATIVE_FLOAT:
        case DPI_ORACLE_TYPE_NATIVE_DOUBLE:
        case DPI_ORACLE_TYPE_NATIVE_INT:
        case DPI_ORACLE_TYPE_NUMBER:
            if (queryInfo.typeInfo.precision) {
                displaySize = queryInfo.typeInfo.precision + 1;
                if (queryInfo.typeInfo.scale > 0)
                    displaySize += queryInfo.typeInfo.scale + 1;
            }
            else displaySize = 127;
            break;
        case DPI_ORACLE_TYPE_DATE:
        case DPI_ORACLE_TYPE_TIMESTAMP:
            displaySize = 23;
            break;
        default:
            displaySize = 0;
    }

    // create the tuple and populate it
    tuple = PyTuple_New(7);
    if (!tuple)
        return NULL;

    // set each of the items in the tuple
    PyTuple_SET_ITEM(tuple, 0, cxoPyString_fromEncodedString(queryInfo.name,
            queryInfo.nameLength, cursor->connection->encodingInfo.encoding,
            NULL));
    Py_INCREF(varType->pythonType);
    PyTuple_SET_ITEM(tuple, 1, (PyObject*) varType->pythonType);
    if (displaySize)
        PyTuple_SET_ITEM(tuple, 2, PyInt_FromLong(displaySize));
    else {
        Py_INCREF(Py_None);
        PyTuple_SET_ITEM(tuple, 2, Py_None);
    }
    if (queryInfo.typeInfo.clientSizeInBytes)
        PyTuple_SET_ITEM(tuple, 3,
                PyInt_FromLong(queryInfo.typeInfo.clientSizeInBytes));
    else {
        Py_INCREF(Py_None);
        PyTuple_SET_ITEM(tuple, 3, Py_None);
    }
    if (queryInfo.typeInfo.precision || queryInfo.typeInfo.scale ||
            queryInfo.typeInfo.fsPrecision) {
        PyTuple_SET_ITEM(tuple, 4,
                PyInt_FromLong(queryInfo.typeInfo.precision));
        PyTuple_SET_ITEM(tuple, 5,
                PyInt_FromLong(queryInfo.typeInfo.scale +
                        queryInfo.typeInfo.fsPrecision));
    } else {
        Py_INCREF(Py_None);
        PyTuple_SET_ITEM(tuple, 4, Py_None);
        Py_INCREF(Py_None);
        PyTuple_SET_ITEM(tuple, 5, Py_None);
    }
    PyTuple_SET_ITEM(tuple, 6, PyInt_FromLong(queryInfo.nullOk != 0));

    // make sure the tuple is ok
    for (index = 0; index < 7; index++) {
        temp = PyTuple_GET_ITEM(tuple, index);
        if (!temp) {
            Py_DECREF(tuple);
            return NULL;
        } else if (temp == Py_None)
            Py_INCREF(temp);
    }

    return tuple;
}


//-----------------------------------------------------------------------------
// cxoCursor_getDescription()
//   Return a list of 7-tuples consisting of the description of the define
// variables.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_getDescription(cxoCursor *cursor, void *unused)
{
    uint32_t numQueryColumns, i;
    PyObject *results, *tuple;

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // determine the number of query columns; if not a query return None
    if (!cursor->handle)
        Py_RETURN_NONE;
    if (dpiStmt_getNumQueryColumns(cursor->handle, &numQueryColumns) < 0)
        return cxoError_raiseAndReturnNull();
    if (numQueryColumns == 0)
        Py_RETURN_NONE;

    // create a list of the required length
    results = PyList_New(numQueryColumns);
    if (!results)
        return NULL;

    // create tuples corresponding to the select-items
    for (i = 0; i < numQueryColumns; i++) {
        tuple = cxoCursor_itemDescription(cursor, i + 1);
        if (!tuple) {
            Py_DECREF(results);
            return NULL;
        }
        PyList_SET_ITEM(results, i, tuple);
    }

    return results;
}


//-----------------------------------------------------------------------------
// cxoCursor_close()
//   Close the cursor. Any action taken on this cursor from this point forward
// results in an exception being raised.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_close(cxoCursor *cursor, PyObject *args)
{
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;
    Py_CLEAR(cursor->bindVariables);
    Py_CLEAR(cursor->fetchVariables);
    if (cursor->handle) {
        if (dpiStmt_close(cursor->handle, NULL, 0) < 0)
            return cxoError_raiseAndReturnNull();
        dpiStmt_release(cursor->handle);
        cursor->handle = NULL;
    }
    cursor->isOpen = 0;

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_setBindVariableHelper()
//   Helper for setting a bind variable.
//-----------------------------------------------------------------------------
static int cxoCursor_setBindVariableHelper(cxoCursor *cursor,
        unsigned numElements, unsigned arrayPos, PyObject *value,
        cxoVar *origVar, cxoVar **newVar, int deferTypeAssignment)
{
    cxoVar *varToSet;
    int isValueVar;

    // initialization
    *newVar = NULL;
    isValueVar = cxoVar_check(value);

    // handle case where variable is already bound, either from a prior
    // execution or a call to setinputsizes()
    if (origVar) {

        // if the value is a variable object, rebind it if necessary
        if (isValueVar) {
            if ( (PyObject*) origVar != value) {
                Py_INCREF(value);
                *newVar = (cxoVar*) value;
            }

        // otherwise, attempt to set the value, but if this fails, simply
        // ignore the original bind variable and create a new one; this is
        // intended for cases where the type changes between executions of a
        // statement or where setinputsizes() has been called with the wrong
        // type (as mandated by the DB API)
        } else {
            varToSet = origVar;

            // first check to see if the variable transform is for None (which
            // can happen if all of the values in a previous invocation of
            // executemany() were None) and there is now a value; in this case,
            // discard the original variable and have a new one created
            if (origVar->type->transformNum == CXO_TRANSFORM_NONE &&
                    value != Py_None) {
                origVar = NULL;
                varToSet = NULL;

            // otherwise, if the number of elements has changed, create a new
            // variable this is only necessary for executemany() since
            // execute() always passes a value of 1 for the number of elements
            } else if (numElements > origVar->allocatedElements) {
                *newVar = cxoVar_new(cursor, numElements, origVar->type,
                        origVar->size, origVar->isArray, origVar->objectType);
                if (!*newVar)
                    return -1;
                varToSet = *newVar;
            }

            // attempt to set the value
            if (varToSet && cxoVar_setValue(varToSet, arrayPos, value) < 0) {

                // executemany() should simply fail after the first element
                if (arrayPos > 0)
                    return -1;

                // clear the exception and try to create a new variable
                PyErr_Clear();
                Py_CLEAR(*newVar);
                origVar = NULL;

            }

        }

    }

    // if no original variable used, create a new one
    if (!origVar) {

        // if the value is a variable object, bind it directly
        if (isValueVar) {
            Py_INCREF(value);
            *newVar = (cxoVar*) value;

        // otherwise, create a new variable, unless the value is None and
        // we wish to defer type assignment
        } else if (value != Py_None || !deferTypeAssignment) {
            *newVar = cxoVar_newByValue(cursor, value, numElements);
            if (!*newVar)
                return -1;
            if (cxoVar_setValue(*newVar, arrayPos, value) < 0) {
                Py_CLEAR(*newVar);
                return -1;
            }
        }

    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_setBindVariables()
//   Create or set bind variables.
//-----------------------------------------------------------------------------
int cxoCursor_setBindVariables(cxoCursor *cursor, PyObject *parameters,
        unsigned numElements, unsigned arrayPos, int deferTypeAssignment)
{
    uint32_t i, origBoundByPos, origNumParams, boundByPos, numParams;
    PyObject *key, *value, *origVar;
    cxoVar *newVar;
    Py_ssize_t pos, temp;

    // make sure positional and named binds are not being intermixed
    origNumParams = numParams = 0;
    boundByPos = PySequence_Check(parameters);
    if (boundByPos) {
        temp = PySequence_Size(parameters);
        if (temp < 0)
            return -1;
        numParams = (uint32_t) temp;
    }
    if (cursor->bindVariables) {
        origBoundByPos = PyList_Check(cursor->bindVariables);
        if (boundByPos != origBoundByPos) {
            cxoError_raiseFromString(cxoProgrammingErrorException,
                    "positional and named binds cannot be intermixed");
            return -1;
        }
        if (origBoundByPos)
            origNumParams = (uint32_t) PyList_GET_SIZE(cursor->bindVariables);

    // otherwise, create the list or dictionary if needed
    } else {
        if (boundByPos)
            cursor->bindVariables = PyList_New(numParams);
        else cursor->bindVariables = PyDict_New();
        if (!cursor->bindVariables)
            return -1;
        origNumParams = 0;
    }

    // handle positional binds
    if (boundByPos) {
        for (i = 0; i < numParams; i++) {
            value = PySequence_GetItem(parameters, i);
            if (!value)
                return -1;
            Py_DECREF(value);
            if (i < origNumParams) {
                origVar = PyList_GET_ITEM(cursor->bindVariables, i);
                if (origVar == Py_None)
                    origVar = NULL;
            } else origVar = NULL;
            if (cxoCursor_setBindVariableHelper(cursor, numElements, arrayPos,
                    value, (cxoVar*) origVar, &newVar,
                    deferTypeAssignment) < 0)
                return -1;
            if (newVar) {
                if (i < (uint32_t) PyList_GET_SIZE(cursor->bindVariables)) {
                    if (PyList_SetItem(cursor->bindVariables, i,
                            (PyObject*) newVar) < 0) {
                        Py_DECREF(newVar);
                        return -1;
                    }
                } else {
                    if (PyList_Append(cursor->bindVariables,
                            (PyObject*) newVar) < 0) {
                        Py_DECREF(newVar);
                        return -1;
                    }
                    Py_DECREF(newVar);
                }
            }
        }

    // handle named binds
    } else {
        pos = 0;
        while (PyDict_Next(parameters, &pos, &key, &value)) {
            origVar = PyDict_GetItem(cursor->bindVariables, key);
            if (cxoCursor_setBindVariableHelper(cursor, numElements, arrayPos,
                    value, (cxoVar*) origVar, &newVar,
                    deferTypeAssignment) < 0)
                return -1;
            if (newVar) {
                if (PyDict_SetItem(cursor->bindVariables, key,
                        (PyObject*) newVar) < 0) {
                    Py_DECREF(newVar);
                    return -1;
                }
                Py_DECREF(newVar);
            }
        }
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_performBind()
//   Perform the binds on the cursor.
//-----------------------------------------------------------------------------
int cxoCursor_performBind(cxoCursor *cursor)
{
    PyObject *key, *var;
    Py_ssize_t pos;
    int i;

    // ensure that input sizes are reset
    // this is done before binding is attempted so that if binding fails and
    // a new statement is prepared, the bind variables will be reset and
    // spurious errors will not occur
    cursor->setInputSizes = 0;

    // set values and perform binds for all bind variables
    if (cursor->bindVariables) {
        if (PyDict_Check(cursor->bindVariables)) {
            pos = 0;
            while (PyDict_Next(cursor->bindVariables, &pos, &key, &var)) {
                if (cxoVar_bind((cxoVar*) var, cursor, key, 0) < 0)
                    return -1;
            }
        } else {
            for (i = 0; i < PyList_GET_SIZE(cursor->bindVariables); i++) {
                var = PyList_GET_ITEM(cursor->bindVariables, i);
                if (var != Py_None) {
                    if (cxoVar_bind((cxoVar*) var, cursor, NULL,
                            i + 1) < 0)
                        return -1;
                }
            }
        }
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_createRow()
//   Create an object for the row. The object created is a tuple unless a row
// factory function has been defined in which case it is the result of the
// row factory function called with the argument tuple that would otherwise be
// returned.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_createRow(cxoCursor *cursor, uint32_t pos)
{
    PyObject *tuple, *item, *result;
    Py_ssize_t numItems, i;
    cxoVar *var;

    // bump row count as a new row has been found
    cursor->rowCount++;

    // create a new tuple
    numItems = PyList_GET_SIZE(cursor->fetchVariables);
    tuple = PyTuple_New(numItems);
    if (!tuple)
        return NULL;

    // acquire the value for each item
    for (i = 0; i < numItems; i++) {
        var = (cxoVar*) PyList_GET_ITEM(cursor->fetchVariables, i);
        item = cxoVar_getSingleValue(var, var->data, pos);
        if (!item) {
            Py_DECREF(tuple);
            return NULL;
        }
        PyTuple_SET_ITEM(tuple, i, item);
    }

    // if a row factory is defined, call it
    if (cursor->rowFactory && cursor->rowFactory != Py_None) {
        result = PyObject_CallObject(cursor->rowFactory, tuple);
        Py_DECREF(tuple);
        return result;
    }

    return tuple;
}


//-----------------------------------------------------------------------------
// cxoCursor_internalPrepare()
//   Internal method for preparing a statement for execution.
//-----------------------------------------------------------------------------
static int cxoCursor_internalPrepare(cxoCursor *cursor, PyObject *statement,
        PyObject *statementTag)
{
    cxoBuffer statementBuffer, tagBuffer;
    int status;

    // make sure we don't get a situation where nothing is to be executed
    if (statement == Py_None && !cursor->statement) {
        cxoError_raiseFromString(cxoProgrammingErrorException,
                "no statement specified and no prior statement prepared");
        return -1;
    }

    // nothing to do if the statement is identical to the one already stored
    // but go ahead and prepare anyway for create, alter and drop statments
    if (statement == Py_None || statement == cursor->statement) {
        if (cursor->handle && !cursor->stmtInfo.isDDL)
            return 0;
        statement = cursor->statement;
    }

    // keep track of the statement
    Py_XDECREF(cursor->statement);
    Py_INCREF(statement);
    cursor->statement = statement;

    // keep track of the tag
    Py_XDECREF(cursor->statementTag);
    Py_XINCREF(statementTag);
    cursor->statementTag = statementTag;

    // clear fetch and bind variables if applicable
    Py_CLEAR(cursor->fetchVariables);
    if (!cursor->setInputSizes)
        Py_CLEAR(cursor->bindVariables);

    // prepare statement
    if (cxoBuffer_fromObject(&statementBuffer, statement,
            cursor->connection->encodingInfo.encoding) < 0)
        return -1;
    if (cxoBuffer_fromObject(&tagBuffer, statementTag,
            cursor->connection->encodingInfo.encoding) < 0) {
        cxoBuffer_clear(&statementBuffer);
        return -1;
    }
    Py_BEGIN_ALLOW_THREADS
    if (cursor->handle)
        dpiStmt_release(cursor->handle);
    status = dpiConn_prepareStmt(cursor->connection->handle,
            cursor->isScrollable, (const char*) statementBuffer.ptr,
            statementBuffer.size, (const char*) tagBuffer.ptr, tagBuffer.size,
            &cursor->handle);
    Py_END_ALLOW_THREADS
    cxoBuffer_clear(&statementBuffer);
    cxoBuffer_clear(&tagBuffer);
    if (status < 0)
        return cxoError_raiseAndReturnInt();

    // get statement information
    if (dpiStmt_getInfo(cursor->handle, &cursor->stmtInfo) < 0)
        return cxoError_raiseAndReturnInt();

    // set the fetch array size, if applicable
    if (cursor->stmtInfo.statementType == DPI_STMT_TYPE_SELECT) {
        if (dpiStmt_setFetchArraySize(cursor->handle, cursor->arraySize) < 0)
            return cxoError_raiseAndReturnInt();
    }

    // clear row factory, if applicable
    Py_CLEAR(cursor->rowFactory);

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_parse()
//   Parse the statement without executing it. This also retrieves information
// about the select list for select statements.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_parse(cxoCursor *cursor, PyObject *statement)
{
    uint32_t mode, numQueryColumns;
    dpiStmtInfo stmtInfo;
    int status;

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // prepare the statement and get statement information
    if (cxoCursor_internalPrepare(cursor, statement, NULL) < 0)
        return NULL;
    if (dpiStmt_getInfo(cursor->handle, &stmtInfo) < 0)
        return cxoError_raiseAndReturnNull();

    // parse the statement
    if (stmtInfo.isQuery)
        mode = DPI_MODE_EXEC_DESCRIBE_ONLY;
    else mode = DPI_MODE_EXEC_PARSE_ONLY;
    Py_BEGIN_ALLOW_THREADS
    status = dpiStmt_execute(cursor->handle, mode, &numQueryColumns);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_prepare()
//   Prepare the statement for execution.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_prepare(cxoCursor *cursor, PyObject *args)
{
    PyObject *statement, *statementTag;

    // statement text and optional tag is expected
    statementTag = NULL;
    if (!PyArg_ParseTuple(args, "O|O", &statement, &statementTag))
        return NULL;

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // prepare the statement
    if (cxoCursor_internalPrepare(cursor, statement, statementTag) < 0)
        return NULL;

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_callCalculateSize()
//   Calculate the size of the statement that is to be executed.
//-----------------------------------------------------------------------------
static int cxoCursor_callCalculateSize(PyObject *name,
        cxoVar *returnValue, PyObject *listOfArguments,
        PyObject *keywordArguments, int *size)
{
    Py_ssize_t numPositionalArgs, numKeywordArgs;

    // set base size without any arguments
    *size = 17;

    // add any additional space required to handle the return value
    if (returnValue)
        *size += 6;

    // assume up to 9 characters for each positional argument
    // this allows up to four digits for the placeholder if the bind variale
    // is a boolean value (prior to Oracle 12.1)
    numPositionalArgs = 0;
    if (listOfArguments) {
        numPositionalArgs = PySequence_Size(listOfArguments);
        if (numPositionalArgs < 0)
            return -1;
        *size += (int) (numPositionalArgs * 9);
    }

    // assume up to 15 characters for each keyword argument
    // this allows up to four digits for the placeholder if the bind variable
    // is a boolean value (prior to Oracle 12.1)
    numKeywordArgs = 0;
    if (keywordArguments) {
        numKeywordArgs = PyDict_Size(keywordArguments);
        if (numKeywordArgs < 0)
            return -1;
        *size += (int) (numKeywordArgs * 15);
    }

    // the above assume a maximum of 10,000 arguments; check and raise an
    // error if the number of arguments exceeds this value; more than this
    // number would probably be unusable in any case!
    if (numPositionalArgs + numKeywordArgs > 10000) {
        cxoError_raiseFromString(cxoInterfaceErrorException,
                "too many arguments");
        return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_callBuildStatement()
//   Determine the statement and the bind variables to bind to the statement
// that is created for calling a stored procedure or function.
//-----------------------------------------------------------------------------
static int cxoCursor_callBuildStatement(PyObject *name,
        cxoVar *returnValue, PyObject *listOfArguments,
        PyObject *keywordArguments, char *statement, PyObject **statementObj,
        PyObject **bindVariables)
{
    PyObject *key, *value, *formatArgs, *positionalArgs;
    uint32_t i, argNum, numPositionalArgs;
    Py_ssize_t pos;
    char *ptr;

    // initialize the bind variables to the list of positional arguments
    if (listOfArguments)
        *bindVariables = PySequence_List(listOfArguments);
    else *bindVariables = PyList_New(0);
    if (!*bindVariables)
        return -1;

    // insert the return variable, if applicable
    if (returnValue) {
        if (PyList_Insert(*bindVariables, 0, (PyObject*) returnValue) < 0)
            return -1;
    }

    // initialize format arguments
    formatArgs = PyList_New(0);
    if (!formatArgs)
        return -1;
    if (PyList_Append(formatArgs, name) < 0) {
        Py_DECREF(formatArgs);
        return -1;
    }

    // begin building the statement
    argNum = 1;
    strcpy(statement, "begin ");
    if (returnValue) {
        strcat(statement, ":1 := ");
        argNum++;
    }
    strcat(statement, "%s");
    ptr = statement + strlen(statement);
    *ptr++ = '(';

    // include any positional arguments first
    if (listOfArguments) {
        positionalArgs = PySequence_Fast(listOfArguments,
                "expecting sequence of arguments");
        if (!positionalArgs) {
            Py_DECREF(formatArgs);
            return -1;
        }
        numPositionalArgs = (uint32_t) PySequence_Size(listOfArguments);
        for (i = 0; i < numPositionalArgs; i++) {
            if (i > 0)
                *ptr++ = ',';
            ptr += sprintf(ptr, ":%d", argNum++);
            if (cxoClientVersionInfo.versionNum < 12 &&
                    PyBool_Check(PySequence_Fast_GET_ITEM(positionalArgs, i)))
                ptr += sprintf(ptr, " = 1");
        }
        Py_DECREF(positionalArgs);
    }

    // next append any keyword arguments
    if (keywordArguments) {
        pos = 0;
        while (PyDict_Next(keywordArguments, &pos, &key, &value)) {
            if (PyList_Append(*bindVariables, value) < 0) {
                Py_DECREF(formatArgs);
                return -1;
            }
            if (PyList_Append(formatArgs, key) < 0) {
                Py_DECREF(formatArgs);
                return -1;
            }
            if ((argNum > 1 && !returnValue) || (argNum > 2 && returnValue))
                *ptr++ = ',';
            ptr += sprintf(ptr, "%%s => :%d", argNum++);
            if (cxoClientVersionInfo.versionNum < 12 &&
                    PyBool_Check(value))
                ptr += sprintf(ptr, " = 1");
        }
    }

    // create statement object
    strcpy(ptr, "); end;");
    *statementObj = cxoUtils_formatString(statement,
            PyList_AsTuple(formatArgs));
    Py_DECREF(formatArgs);
    if (!*statementObj)
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_call()
//   Call a stored procedure or function.
//-----------------------------------------------------------------------------
static int cxoCursor_call(cxoCursor *cursor, cxoVar *returnValue,
        PyObject *name, PyObject *listOfArguments, PyObject *keywordArguments)
{
    PyObject *bindVariables, *statementObj, *results;
    int statementSize;
    char *statement;

    // verify that the arguments are passed correctly
    if (listOfArguments) {
        if (!PySequence_Check(listOfArguments)) {
            PyErr_SetString(PyExc_TypeError, "arguments must be a sequence");
            return -1;
        }
    }
    if (keywordArguments) {
        if (!PyDict_Check(keywordArguments)) {
            PyErr_SetString(PyExc_TypeError,
                    "keyword arguments must be a dictionary");
            return -1;
        }
    }

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return -1;

    // determine the statement size
    if (cxoCursor_callCalculateSize(name, returnValue, listOfArguments,
            keywordArguments, &statementSize) < 0)
        return -1;

    // allocate a string for the statement
    statement = (char*) PyMem_Malloc(statementSize);
    if (!statement) {
        PyErr_NoMemory();
        return -1;
    }

    // determine the statement to execute and the argument to pass
    bindVariables = statementObj = NULL;
    if (cxoCursor_callBuildStatement(name, returnValue, listOfArguments,
            keywordArguments, statement, &statementObj, &bindVariables) < 0) {
        PyMem_Free(statement);
        Py_XDECREF(statementObj);
        Py_XDECREF(bindVariables);
        return -1;
    }
    PyMem_Free(statement);

    // execute the statement on the cursor
    results = PyObject_CallMethod( (PyObject*) cursor, "execute", "OO",
            statementObj, bindVariables);
    Py_DECREF(statementObj);
    Py_DECREF(bindVariables);
    if (!results)
        return -1;
    Py_DECREF(results);

    return 0;
}


//-----------------------------------------------------------------------------
// cxoCursor_callFunc()
//   Call a stored function and return the return value of the function.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_callFunc(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "name", "returnType", "parameters",
            "keywordParameters", NULL };
    PyObject *listOfArguments, *keywordArguments, *returnType, *results, *name;
    cxoVar *var;

    // parse arguments
    listOfArguments = keywordArguments = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "OO|OO", keywordList,
            &name, &returnType, &listOfArguments, &keywordArguments))
        return NULL;

    // create the return variable
    var = cxoVar_newByType(cursor, returnType, 1);
    if (!var)
        return NULL;

    // call the function
    if (cxoCursor_call(cursor, var, name, listOfArguments,
            keywordArguments) < 0)
        return NULL;

    // determine the results
    results = cxoVar_getValue(var, 0);
    Py_DECREF(var);
    return results;
}


//-----------------------------------------------------------------------------
// cxoCursor_callProc()
//   Call a stored procedure and return the (possibly modified) arguments.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_callProc(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "name", "parameters", "keywordParameters",
            NULL };
    PyObject *listOfArguments, *keywordArguments, *results, *var, *temp, *name;
    Py_ssize_t numArgs, i;

    // parse arguments
    listOfArguments = keywordArguments = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O|OO", keywordList,
            &name, &listOfArguments, &keywordArguments))
        return NULL;

    // call the stored procedure
    if (cxoCursor_call(cursor, NULL, name, listOfArguments,
            keywordArguments) < 0)
        return NULL;

    // create the return value
    numArgs = PyList_GET_SIZE(cursor->bindVariables);
    results = PyList_New(numArgs);
    if (!results)
        return NULL;
    for (i = 0; i < numArgs; i++) {
        var = PyList_GET_ITEM(cursor->bindVariables, i);
        temp = cxoVar_getValue((cxoVar*) var, 0);
        if (!temp) {
            Py_DECREF(results);
            return NULL;
        }
        PyList_SET_ITEM(results, i, temp);
    }

    return results;
}


//-----------------------------------------------------------------------------
// cxoCursor_execute()
//   Execute the statement.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_execute(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    PyObject *statement, *executeArgs;
    uint32_t numQueryColumns, mode;
    int status;

    executeArgs = NULL;
    if (!PyArg_ParseTuple(args, "O|O", &statement, &executeArgs))
        return NULL;
    if (executeArgs && keywordArgs) {
        if (PyDict_Size(keywordArgs) == 0)
            keywordArgs = NULL;
        else return cxoError_raiseFromString(cxoInterfaceErrorException,
                "expecting argument or keyword arguments, not both");
    }
    if (keywordArgs)
        executeArgs = keywordArgs;
    if (executeArgs) {
        if (!PyDict_Check(executeArgs) && !PySequence_Check(executeArgs)) {
            PyErr_SetString(PyExc_TypeError,
                    "expecting a dictionary, sequence or keyword args");
            return NULL;
        }
    }

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // prepare the statement, if applicable
    if (cxoCursor_internalPrepare(cursor, statement, NULL) < 0)
        return NULL;

    // perform binds
    if (executeArgs && cxoCursor_setBindVariables(cursor, executeArgs, 1, 0,
            0) < 0)
        return NULL;
    if (cxoCursor_performBind(cursor) < 0)
        return NULL;

    // execute the statement
    Py_BEGIN_ALLOW_THREADS
    mode = (cursor->connection->autocommit) ? DPI_MODE_EXEC_COMMIT_ON_SUCCESS :
            DPI_MODE_EXEC_DEFAULT;
    status = dpiStmt_execute(cursor->handle, mode, &numQueryColumns);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();

    // get the count of the rows affected
    if (dpiStmt_getRowCount(cursor->handle, &cursor->rowCount) < 0)
        return cxoError_raiseAndReturnNull();

    // for queries, return the cursor for convenience
    if (numQueryColumns > 0) {
        if (cxoCursor_performDefine(cursor, numQueryColumns) < 0) {
            Py_CLEAR(cursor->fetchVariables);
            return NULL;
        }
        Py_INCREF(cursor);
        return (PyObject*) cursor;
    }

    // for statements other than queries, simply return None
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_executeMany()
//   Execute the statement many times. The number of times is equivalent to the
// number of elements in the list of parameters, or the provided integer if no
// parameters are required.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_executeMany(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "statement", "parameters", "batcherrors",
            "arraydmlrowcounts", NULL };
    int arrayDMLRowCountsEnabled = 0, batchErrorsEnabled = 0;
    PyObject *arguments, *parameters, *statement;
    uint32_t mode, i, numRows;
    int status;

    // validate parameters
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "OO|ii", keywordList,
            &statement, &parameters, &batchErrorsEnabled,
            &arrayDMLRowCountsEnabled))
        return NULL;
    if (!PyList_Check(parameters) && !PyInt_Check(parameters)) {
        PyErr_SetString(PyExc_TypeError,
                "parameters should be a list of sequences/dictionaries "
                "or an integer specifying the number of times to execute "
                "the statement");
        return NULL;
    }

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // determine execution mode
    mode = (cursor->connection->autocommit) ? DPI_MODE_EXEC_COMMIT_ON_SUCCESS :
            DPI_MODE_EXEC_DEFAULT;
    if (batchErrorsEnabled)
        mode |= DPI_MODE_EXEC_BATCH_ERRORS;
    if (arrayDMLRowCountsEnabled)
        mode |= DPI_MODE_EXEC_ARRAY_DML_ROWCOUNTS;

    // prepare the statement
    if (cxoCursor_internalPrepare(cursor, statement, NULL) < 0)
        return NULL;

    // perform binds, as required
    if (PyInt_Check(parameters))
        numRows = (uint32_t) PyInt_AsLong(parameters);
    else {
        numRows = (uint32_t) PyList_GET_SIZE(parameters);
        for (i = 0; i < numRows; i++) {
            arguments = PyList_GET_ITEM(parameters, i);
            if (!PyDict_Check(arguments) && !PySequence_Check(arguments))
                return cxoError_raiseFromString(cxoInterfaceErrorException,
                        "expecting a list of dictionaries or sequences");
            if (cxoCursor_setBindVariables(cursor, arguments, numRows, i,
                    (i < numRows - 1)) < 0)
                return NULL;
        }
    }
    if (cxoCursor_performBind(cursor) < 0)
        return NULL;

    // execute the statement, but only if the number of rows is greater than
    // zero since Oracle raises an error otherwise
    if (numRows > 0) {
        Py_BEGIN_ALLOW_THREADS
        status = dpiStmt_executeMany(cursor->handle, mode, numRows);
        Py_END_ALLOW_THREADS
        if (status < 0) {
            cxoError_raiseAndReturnNull();
            dpiStmt_getRowCount(cursor->handle, &cursor->rowCount);
            return NULL;
        }
        if (dpiStmt_getRowCount(cursor->handle, &cursor->rowCount) < 0)
            return cxoError_raiseAndReturnNull();
    }

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_executeManyPrepared()
//   Execute the prepared statement the number of times requested. At this
// point, the statement must have been already prepared and the bind variables
// must have their values set.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_executeManyPrepared(cxoCursor *cursor,
        PyObject *args)
{
    int numIters, status;

    // expect number of times to execute the statement
    if (!PyArg_ParseTuple(args, "i", &numIters))
        return NULL;

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // perform binds
    if (cxoCursor_performBind(cursor) < 0)
        return NULL;

    // execute the statement
    Py_BEGIN_ALLOW_THREADS
    status = dpiStmt_executeMany(cursor->handle, DPI_MODE_EXEC_DEFAULT,
            numIters);
    Py_END_ALLOW_THREADS
    if (status < 0 || dpiStmt_getRowCount(cursor->handle,
            &cursor->rowCount) < 0)
        return cxoError_raiseAndReturnNull();

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_multiFetch()
//   Return a list consisting of the remaining rows up to the given row limit
// (if specified).
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_multiFetch(cxoCursor *cursor, int rowLimit)
{
    uint32_t bufferRowIndex = 0;
    PyObject *results, *row;
    int found, rowNum;

    // verify fetch can be performed
    if (cxoCursor_verifyFetch(cursor) < 0)
        return NULL;

    // create an empty list
    results = PyList_New(0);
    if (!results)
        return NULL;

    // fetch as many rows as possible
    for (rowNum = 0; rowLimit == 0 || rowNum < rowLimit; rowNum++) {
        if (cxoCursor_fetchRow(cursor, &found, &bufferRowIndex) < 0) {
            Py_DECREF(results);
            return NULL;
        }
        if (!found)
            break;
        row = cxoCursor_createRow(cursor, bufferRowIndex);
        if (!row) {
            Py_DECREF(results);
            return NULL;
        }
        if (PyList_Append(results, row) < 0) {
            Py_DECREF(row);
            Py_DECREF(results);
            return NULL;
        }
        Py_DECREF(row);
    }

    return results;
}


//-----------------------------------------------------------------------------
// cxoCursor_fetchOne()
//   Fetch a single row from the cursor.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_fetchOne(cxoCursor *cursor, PyObject *args)
{
    uint32_t bufferRowIndex = 0;
    int found = 0;

    if (cxoCursor_verifyFetch(cursor) < 0)
        return NULL;
    if (cxoCursor_fetchRow(cursor, &found, &bufferRowIndex) < 0)
        return NULL;
    if (found)
        return cxoCursor_createRow(cursor, bufferRowIndex);

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_fetchMany()
//   Fetch multiple rows from the cursor based on the arraysize.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_fetchMany(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "numRows", NULL };
    int rowLimit;

    // parse arguments -- optional rowlimit expected
    rowLimit = cursor->arraySize;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|i", keywordList,
            &rowLimit))
        return NULL;

    return cxoCursor_multiFetch(cursor, rowLimit);
}


//-----------------------------------------------------------------------------
// cxoCursor_fetchAll()
//   Fetch all remaining rows from the cursor.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_fetchAll(cxoCursor *cursor, PyObject *args)
{
    return cxoCursor_multiFetch(cursor, 0);
}


//-----------------------------------------------------------------------------
// cxoCursor_fetchRaw()
//   Perform raw fetch on the cursor; return the actual number of rows fetched.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_fetchRaw(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "numRows", NULL };
    uint32_t numRowsToFetch, numRowsFetched, bufferRowIndex;
    int moreRows;

    // expect an optional number of rows to retrieve
    numRowsToFetch = cursor->fetchArraySize;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|i", keywordList,
            &numRowsToFetch))
        return NULL;
    if (numRowsToFetch > cursor->fetchArraySize)
        return cxoError_raiseFromString(cxoInterfaceErrorException,
                "rows to fetch exceeds array size");

    // perform the fetch
    if (dpiStmt_fetchRows(cursor->handle, numRowsToFetch, &bufferRowIndex,
            &numRowsFetched, &moreRows) < 0)
        return cxoError_raiseAndReturnNull();
    cursor->rowCount += numRowsFetched;
    cursor->numRowsInFetchBuffer = 0;
    return PyInt_FromLong(numRowsFetched);
}


//-----------------------------------------------------------------------------
// cxoCursor_scroll()
//   Scroll the cursor using the value and mode specified.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_scroll(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "value", "mode", NULL };
    dpiFetchMode mode;
    int32_t offset;
    char *strMode;
    int status;

    // parse arguments
    offset = 0;
    strMode = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "|is", keywordList,
            &offset, &strMode))
        return NULL;

    // validate mode
    if (!strMode)
        mode = DPI_MODE_FETCH_RELATIVE;
    else if (strcmp(strMode, "relative") == 0)
        mode = DPI_MODE_FETCH_RELATIVE;
    else if (strcmp(strMode, "absolute") == 0)
        mode = DPI_MODE_FETCH_ABSOLUTE;
    else if (strcmp(strMode, "first") == 0)
        mode = DPI_MODE_FETCH_FIRST;
    else if (strcmp(strMode, "last") == 0)
        mode = DPI_MODE_FETCH_LAST;
    else return cxoError_raiseFromString(cxoInterfaceErrorException,
            "mode must be one of relative, absolute, first or last");

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // perform scroll and get new row count and number of rows in buffer
    Py_BEGIN_ALLOW_THREADS
    status = dpiStmt_scroll(cursor->handle, mode, offset,
            0 - cursor->numRowsInFetchBuffer);
    if (status == 0)
        status = dpiStmt_fetchRows(cursor->handle, cursor->fetchArraySize,
                &cursor->fetchBufferRowIndex, &cursor->numRowsInFetchBuffer,
                &cursor->moreRowsToFetch);
    if (status == 0)
        status = dpiStmt_getRowCount(cursor->handle, &cursor->rowCount);
    Py_END_ALLOW_THREADS
    if (status < 0)
        return cxoError_raiseAndReturnNull();
    cursor->rowCount -= cursor->numRowsInFetchBuffer;

    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_setInputSizes()
//   Set the sizes of the bind variables.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_setInputSizes(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    Py_ssize_t numPositionalArgs, numKeywordArgs = 0, i;
    PyObject *key, *value;
    cxoVar *var;

    // only expect keyword arguments or positional arguments, not both
    numPositionalArgs = PyTuple_Size(args);
    if (keywordArgs)
        numKeywordArgs = PyDict_Size(keywordArgs);
    if (numKeywordArgs > 0 && numPositionalArgs > 0)
        return cxoError_raiseFromString(cxoInterfaceErrorException,
                "expecting arguments or keyword arguments, not both");

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // eliminate existing bind variables
    Py_CLEAR(cursor->bindVariables);

    // if no values passed, do nothing further, but return an empty list or
    // dictionary as appropriate
    if (numKeywordArgs == 0 && numPositionalArgs == 0) {
        if (keywordArgs)
            return PyDict_New();
        return PyList_New(0);
    }

    // retain bind variables
    cursor->setInputSizes = 1;
    if (numKeywordArgs > 0)
        cursor->bindVariables = PyDict_New();
    else cursor->bindVariables = PyList_New(numPositionalArgs);
    if (!cursor->bindVariables)
        return NULL;

    // process each input
    if (numKeywordArgs > 0) {
        i = 0;
        while (PyDict_Next(keywordArgs, &i, &key, &value)) {
            var = cxoVar_newByType(cursor, value, cursor->bindArraySize);
            if (!var)
                return NULL;
            if (PyDict_SetItem(cursor->bindVariables, key,
                    (PyObject*) var) < 0) {
                Py_DECREF(var);
                return NULL;
            }
            Py_DECREF(var);
        }
    } else {
        for (i = 0; i < numPositionalArgs; i++) {
            value = PyTuple_GET_ITEM(args, i);
            if (value == Py_None) {
                Py_INCREF(Py_None);
                PyList_SET_ITEM(cursor->bindVariables, i, Py_None);
            } else {
                var = cxoVar_newByType(cursor, value, cursor->bindArraySize);
                if (!var)
                    return NULL;
                PyList_SET_ITEM(cursor->bindVariables, i, (PyObject*) var);
            }
        }
    }

    Py_INCREF(cursor->bindVariables);
    return cursor->bindVariables;
}


//-----------------------------------------------------------------------------
// cxoCursor_setOutputSize()
//   Does nothing as ODPI-C handles long columns dynamically without the need
// to specify a maximum length.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_setOutputSize(cxoCursor *cursor, PyObject *args)
{
    int outputSize, outputSizeColumn;

    if (!PyArg_ParseTuple(args, "i|i", &outputSize, &outputSizeColumn))
        return NULL;
    Py_RETURN_NONE;
}


//-----------------------------------------------------------------------------
// cxoCursor_var()
//   Create a bind variable and return it.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_var(cxoCursor *cursor, PyObject *args,
        PyObject *keywordArgs)
{
    static char *keywordList[] = { "type", "size", "arraysize",
            "inconverter", "outconverter", "typename", "encodingErrors",
            NULL };
    PyObject *inConverter, *outConverter, *typeNameObj;
    const char *encodingErrors;
    cxoObjectType *objType;
    cxoVarType *varType;
    int size, arraySize;
    PyObject *type;
    cxoVar *var;

    // parse arguments
    size = 0;
    encodingErrors = NULL;
    arraySize = cursor->bindArraySize;
    inConverter = outConverter = typeNameObj = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, keywordArgs, "O|iiOOOz",
            keywordList, &type, &size, &arraySize, &inConverter, &outConverter,
            &typeNameObj, &encodingErrors))
        return NULL;

    // determine the type of variable
    varType = cxoVarType_fromPythonType(type, &objType);
    if (!varType)
        return NULL;
    Py_XINCREF(objType);
    if (size == 0)
        size = varType->size;
    if (typeNameObj && typeNameObj != Py_None && !objType) {
        objType = cxoObjectType_newByName(cursor->connection, typeNameObj);
        if (!objType)
            return NULL;
    }

    // create the variable
    var = cxoVar_new(cursor, arraySize, varType, size, 0, objType);
    Py_XDECREF(objType);
    if (!var)
        return NULL;
    Py_XINCREF(inConverter);
    var->inConverter = inConverter;
    Py_XINCREF(outConverter);
    var->outConverter = outConverter;

    // assign encoding errors, if applicable
    if (encodingErrors) {
        var->encodingErrors = PyMem_Malloc(strlen(encodingErrors) + 1);
        if (!var->encodingErrors) {
            Py_DECREF(var);
            return NULL;
        }
        strcpy((char*) var->encodingErrors, encodingErrors);
    }

    return (PyObject*) var;
}


//-----------------------------------------------------------------------------
// cxoCursor_arrayVar()
//   Create an array bind variable and return it.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_arrayVar(cxoCursor *cursor, PyObject *args)
{
    uint32_t size, numElements;
    PyObject *type, *value;
    cxoObjectType *objType;
    cxoVarType *varType;
    cxoVar *var;

    // parse arguments
    size = 0;
    if (!PyArg_ParseTuple(args, "O!O|i", &PyType_Type, &type, &value, &size))
        return NULL;

    // determine the type of variable
    varType = cxoVarType_fromPythonType(type, &objType);
    if (!varType)
        return NULL;
    if (size == 0)
        size = varType->size;

    // determine the number of elements to create
    if (PyList_Check(value))
        numElements = (uint32_t) PyList_GET_SIZE(value);
    else if (PyInt_Check(value)) {
        numElements = (uint32_t) PyInt_AsLong(value);
        if (PyErr_Occurred())
            return NULL;
    } else {
        PyErr_SetString(PyExc_TypeError,
                "expecting integer or list of values");
        return NULL;
    }

    // create the variable
    var = cxoVar_new(cursor, numElements, varType, size, 1, objType);
    if (!var)
        return NULL;

    // set the value, if applicable
    if (PyList_Check(value)) {
        if (cxoVar_setValue(var, 0, value) < 0)
            return NULL;
    }

    return (PyObject*) var;
}


//-----------------------------------------------------------------------------
// cxoCursor_bindNames()
//   Return a list of bind variable names.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_bindNames(cxoCursor *cursor, PyObject *args)
{
    uint32_t numBinds, *nameLengths, i;
    PyObject *namesList, *temp;
    const char **names;

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // ensure that a statement has already been prepared
    if (!cursor->statement)
        return cxoError_raiseFromString(cxoProgrammingErrorException,
                "statement must be prepared first");

    // determine the number of binds
    if (dpiStmt_getBindCount(cursor->handle, &numBinds) < 0)
        return cxoError_raiseAndReturnNull();

    // if the number of binds is zero, nothing to do
    if (numBinds == 0)
        return PyList_New(0);

    // allocate memory for the bind names and their lengths
    names = (const char**) PyMem_Malloc(numBinds * sizeof(char*));
    if (!names)
        return PyErr_NoMemory();
    nameLengths = (uint32_t*) PyMem_Malloc(numBinds * sizeof(uint32_t));
    if (!nameLengths) {
        PyMem_Free((void*) names);
        return PyErr_NoMemory();
    }

    // get the bind names
    if (dpiStmt_getBindNames(cursor->handle, &numBinds, names,
            nameLengths) < 0) {
        PyMem_Free((void*) names);
        PyMem_Free(nameLengths);
        return cxoError_raiseAndReturnNull();
    }

    // populate list with the results
    namesList = PyList_New(numBinds);
    if (namesList) {
        for (i = 0; i < numBinds; i++) {
            temp = cxoPyString_fromEncodedString(names[i], nameLengths[i],
                    cursor->connection->encodingInfo.encoding, NULL);
            if (!temp) {
                Py_CLEAR(namesList);
                break;
            }
            PyList_SET_ITEM(namesList, i, temp);
        }
    }
    PyMem_Free((void*) names);
    PyMem_Free(nameLengths);
    return namesList;
}


//-----------------------------------------------------------------------------
// cxoCursor_getIter()
//   Return a reference to the cursor which supports the iterator protocol.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_getIter(cxoCursor *cursor)
{
    if (cxoCursor_verifyFetch(cursor) < 0)
        return NULL;
    Py_INCREF(cursor);
    return (PyObject*) cursor;
}


//-----------------------------------------------------------------------------
// cxoCursor_getNext()
//   Return a reference to the cursor which supports the iterator protocol.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_getNext(cxoCursor *cursor)
{
    uint32_t bufferRowIndex = 0;
    int found = 0;

    if (cxoCursor_verifyFetch(cursor) < 0)
        return NULL;
    if (cxoCursor_fetchRow(cursor, &found, &bufferRowIndex) < 0)
        return NULL;
    if (found)
        return cxoCursor_createRow(cursor, bufferRowIndex);

    // no more rows, return NULL without setting an exception
    return NULL;
}


//-----------------------------------------------------------------------------
// cxoCursor_getBatchErrors()
//    Returns a list of batch error objects.
//-----------------------------------------------------------------------------
static PyObject* cxoCursor_getBatchErrors(cxoCursor *cursor)
{
    uint32_t numErrors, i;
    dpiErrorInfo *errors;
    PyObject *result;
    cxoError *error;

    // determine the number of errors
    if (dpiStmt_getBatchErrorCount(cursor->handle, &numErrors) < 0)
        return cxoError_raiseAndReturnNull();
    if (numErrors == 0)
        return PyList_New(0);

    // allocate memory for the errors
    errors = PyMem_Malloc(numErrors * sizeof(dpiErrorInfo));
    if (!errors)
        return PyErr_NoMemory();

    // get error information
    if (dpiStmt_getBatchErrors(cursor->handle, numErrors, errors) < 0) {
        PyMem_Free(errors);
        return cxoError_raiseAndReturnNull();
    }

    // create result
    result = PyList_New(numErrors);
    if (result) {
        for (i = 0; i < numErrors; i++) {
            error = cxoError_newFromInfo(&errors[i]);
            if (!error) {
                Py_CLEAR(result);
                break;
            }
            PyList_SET_ITEM(result, i, (PyObject*) error);
        }
    }
    PyMem_Free(errors);
    return result;
}


//-----------------------------------------------------------------------------
// cxoCursor_getArrayDMLRowCounts
//    Populates the array dml row count list.
//-----------------------------------------------------------------------------
static PyObject* cxoCursor_getArrayDMLRowCounts(cxoCursor *cursor)
{
    PyObject *result, *element;
    uint32_t numRowCounts, i;
    uint64_t *rowCounts;

    // get row counts from DPI
    if (dpiStmt_getRowCounts(cursor->handle, &numRowCounts, &rowCounts) < 0)
        return cxoError_raiseAndReturnNull();

    // return array
    result = PyList_New(numRowCounts);
    if (!result)
        return NULL;
    for (i = 0; i < numRowCounts; i++) {
        element = PyLong_FromUnsignedLong((unsigned long) rowCounts[i]);
        if (!element) {
            Py_DECREF(result);
            return NULL;
        }
        PyList_SET_ITEM(result, i, element);
    }

    return result;
}


//-----------------------------------------------------------------------------
// cxoCursor_getImplicitResults
//   Return a list of cursors available implicitly after execution of a PL/SQL
// block or stored procedure. If none are available, an empty list is returned.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_getImplicitResults(cxoCursor *cursor)
{
    cxoCursor *childCursor;
    dpiStmt *childStmt;
    PyObject *result;

    // make sure the cursor is open
    if (cxoCursor_isOpen(cursor) < 0)
        return NULL;

    // make sure we have a statement executed (handle defined)
    if (!cursor->handle)
        return cxoError_raiseFromString(cxoInterfaceErrorException,
                "no statement executed");

    // create result
    result = PyList_New(0);
    if (!result)
        return NULL;
    while (1) {
        if (dpiStmt_getImplicitResult(cursor->handle, &childStmt) < 0)
            return cxoError_raiseAndReturnNull();
        if (!childStmt)
            break;
        childCursor = (cxoCursor*) PyObject_CallMethod(
                (PyObject*) cursor->connection, "cursor", NULL);
        if (!childCursor) {
            dpiStmt_release(childStmt);
            Py_DECREF(result);
            return NULL;
        }
        childCursor->handle = childStmt;
        childCursor->fixupRefCursor = 1;
        if (PyList_Append(result, (PyObject*) childCursor) < 0) {
            Py_DECREF(result);
            Py_DECREF(childCursor);
            return NULL;
        }
        Py_DECREF(childCursor);
    }

    return result;
}


//-----------------------------------------------------------------------------
// cxoCursor_contextManagerEnter()
//   Called when the cursor is used as a context manager and simply returns it
// to the caller.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_contextManagerEnter(cxoCursor *cursor,
        PyObject* args)
{
    Py_INCREF(cursor);
    return (PyObject*) cursor;
}


//-----------------------------------------------------------------------------
// cxoCursor_contextManagerExit()
//   Called when the cursor is used as a context manager and simply closes the
// cursor.
//-----------------------------------------------------------------------------
static PyObject *cxoCursor_contextManagerExit(cxoCursor *cursor,
        PyObject* args)
{
    PyObject *excType, *excValue, *excTraceback, *result;

    if (!PyArg_ParseTuple(args, "OOO", &excType, &excValue, &excTraceback))
        return NULL;
    result = cxoCursor_close(cursor, NULL);
    if (!result)
        return NULL;
    Py_DECREF(result);
    Py_INCREF(Py_False);
    return Py_False;
}

