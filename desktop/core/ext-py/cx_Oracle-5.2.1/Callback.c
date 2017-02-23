//-----------------------------------------------------------------------------
// Callback.c
//   Definition of OCI callback functions.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Callback_NewVariable()
//   Return a new variable from a callback.
//-----------------------------------------------------------------------------
static udt_Variable *Callback_NewVariable(
    udt_Connection *connection,         // connection to use
    ub2 oracleType,                     // Oracle type of data
    ub4 bufferSize,                     // maximum length of elements
    void *data,                         // data pointer
    void *indicator,                    // indicator pointer
    ub2 *returnCode,                    // return code pointer
    ACTUAL_LENGTH_TYPE *actualLength)   // actual length pointer
{
    udt_VariableType *type;
    udt_Variable *var;

    // determine the type to use
    type = Variable_TypeByOracleDataType(oracleType, SQLCS_IMPLICIT);
    if (!type)
        return NULL;

    // attempt to allocate the object
    var = (udt_Variable*) type->pythonType->tp_alloc(type->pythonType, 0);
    if (!var)
        return NULL;

    // perform basic initialization
    // note that the number of allocated elements is set arbitrarily high
    // because the OCI doesn't give information about how many elements are
    // actually allocated; that has to be implied by the number of rows
    // passed to OCIStmtFetch and OCIStmtExecute
    Py_INCREF(connection->environment);
    var->environment = connection->environment;
    var->boundCursorHandle = NULL;
    var->bindHandle = NULL;
    var->defineHandle = NULL;
    var->boundName = NULL;
    var->allocatedElements = 2147483647;
    var->actualElements = 0;
    var->isArray = 0;
    var->isAllocatedInternally = 0;
    var->type = type;
    var->indicator = indicator;
    var->data = data;
    var->actualLength = actualLength;
    var->returnCode = returnCode;
    var->size = type->size;
    var->bufferSize = type->size;
    if (type->isVariableLength)
        var->bufferSize = bufferSize;

    return var;
}


//-----------------------------------------------------------------------------
// Callback_BindByNameArgs()
//   Return the arguments to be passed when OCIBindByName is called.
//-----------------------------------------------------------------------------
static PyObject *Callback_BindByNameArgs(
    udt_Connection *connection,         // connection to use
    va_list args)                       // arguments to OCI function
{
    ub4 nameLength, allocatedElements, *actualElements;
    ACTUAL_LENGTH_TYPE *actualLength;
    ub2 dataType, *returnCode;
    dvoid *indicator, *value;
    udt_Variable *var;
    PyObject *result;
    sb4 valueLength;
    OCIStmt *handle;
    text *name;

    handle = va_arg(args, OCIStmt*);
    va_arg(args, OCIBind**);
    va_arg(args, OCIError*);
    name = va_arg(args, text*);
    nameLength = va_arg(args, ub4);
    value = va_arg(args, dvoid*);
    valueLength = va_arg(args, sb4);
    dataType = va_arg(args, int);
    indicator = va_arg(args, dvoid*);
    actualLength = va_arg(args, ACTUAL_LENGTH_TYPE*);
    returnCode = va_arg(args, ub2*);
    allocatedElements = va_arg(args, ub4);
    actualElements = va_arg(args, ub4*);

    var = Callback_NewVariable(connection, dataType, valueLength, value,
            indicator, returnCode, actualLength);
    if (!var)
        return NULL;
    if (allocatedElements > 0) {
        var->isArray = 1;
        var->actualElements = *actualElements;
    }

    result = Py_BuildValue("ls#O", handle, name, nameLength, var);
    Py_DECREF(var);
    return result;
}


//-----------------------------------------------------------------------------
// Callback_DefineByPosArgs()
//   Return the arguments to be passed when OCIDefineByPos is called.
//-----------------------------------------------------------------------------
static PyObject *Callback_DefineByPosArgs(
    udt_Connection *connection,         // connection to use
    va_list args)                       // arguments to OCI function
{
    ACTUAL_LENGTH_TYPE *actualLength;
    ub2 dataType, *returnCode;
    dvoid *indicator, *value;
    udt_Variable *var;
    PyObject *result;
    OCIStmt *handle;
    sb4 valueLength;
    ub4 position;

    handle = va_arg(args, OCIStmt*);
    va_arg(args, OCIDefine**);
    va_arg(args, OCIError*);
    position = va_arg(args, ub4);
    value = va_arg(args, dvoid*);
    valueLength = va_arg(args, sb4);
    dataType = va_arg(args, int);
    indicator = va_arg(args, dvoid*);
    actualLength = va_arg(args, ACTUAL_LENGTH_TYPE*);
    returnCode = va_arg(args, ub2*);

    // create a variable
    var = Callback_NewVariable(connection, dataType, valueLength, value,
            indicator, returnCode, actualLength);
    if (!var)
        return NULL;

    result = Py_BuildValue("liO", handle, position, var);
    Py_DECREF(var);
    return result;
}


//-----------------------------------------------------------------------------
// Callback_ExecuteArgs()
//   Return the arguments to be passed when OCIStmtExecute is called.
//-----------------------------------------------------------------------------
static PyObject *Callback_ExecuteArgs(
    va_list args)                       // arguments to OCI function
{
    ub4 iters, rowoff;
    OCIStmt *handle;

    va_arg(args, OCISvcCtx*);
    handle = va_arg(args, OCIStmt*);
    va_arg(args, OCIError*);
    iters = va_arg(args, ub4);
    rowoff = va_arg(args, ub4);

    return Py_BuildValue("lii", handle, iters, rowoff);
}


//-----------------------------------------------------------------------------
// Callback_FetchArgs()
//   Return the arguments to be passed when OCIStmtFetch is called.
//-----------------------------------------------------------------------------
static PyObject *Callback_FetchArgs(
    udt_Connection *connection,         // connection to use
    va_list args)                       // arguments to OCI function
{
    ub4 numRows, rowCount;
    OCIStmt *handle;
    sword status;

    handle = va_arg(args, OCIStmt*);
    va_arg(args, OCIError*);
    numRows = va_arg(args, ub4);

    status = OCIAttrGet(handle, OCI_HTYPE_STMT, &rowCount, 0,
            OCI_ATTR_ROW_COUNT, connection->environment->errorHandle);
    if (Environment_CheckForError(connection->environment, status,
            "Callback_FetchArgs()") < 0)
        return NULL;

    return Py_BuildValue("lii", handle, numRows, rowCount);
}


//-----------------------------------------------------------------------------
// Callback_PrepareArgs()
//   Return the arguments to be passed when OCIStmtPrepare is called.
//-----------------------------------------------------------------------------
static PyObject *Callback_PrepareArgs(
    va_list args)                       // arguments to OCI function
{
    ub4 statementLength;
    OCIStmt *handle;
    text *statement;

    handle = va_arg(args, OCIStmt*);
    va_arg(args, OCIError*);
    statement = va_arg(args, text *);
    statementLength = va_arg(args, ub4);

    return Py_BuildValue("ls#", handle, statement, statementLength);
}


//-----------------------------------------------------------------------------
// Callback_GetArgs()
//   Return the arguments to be passed to the Python callback method.
//-----------------------------------------------------------------------------
static PyObject *Callback_GetArgs(
    udt_Connection *connection,         // connection to use
    ub4 functionCode,                   // function code
    va_list args)                       // OCI function arguments
{
    switch (functionCode) {
        case OCI_FNCODE_BINDBYNAME:
            return Callback_BindByNameArgs(connection, args);
        case OCI_FNCODE_DEFINEBYPOS:
            return Callback_DefineByPosArgs(connection, args);
        case OCI_FNCODE_STMTEXECUTE:
            return Callback_ExecuteArgs(args);
        case OCI_FNCODE_STMTFETCH:
            return Callback_FetchArgs(connection, args);
        case OCI_FNCODE_STMTPREPARE:
            return Callback_PrepareArgs(args);
    }

    return PyTuple_New(0);
}


//-----------------------------------------------------------------------------
// Callback_Call()
//   Actually make the call to the Python function.
//-----------------------------------------------------------------------------
static sword Callback_Call(
    PyObject *tuple,                    // tuple containing connection/callback
    ub4 functionCode,                   // function code
    va_list args)                       // arguments
{
    PyObject *callback, *callbackArgs, *result;
    udt_Connection *connection;

    // determine the connection and callback
    connection = (udt_Connection*) PyTuple_GET_ITEM(tuple, 0);
    callback = PyTuple_GET_ITEM(tuple, 1);

    // determine the arguments to pass to the function
    callbackArgs = Callback_GetArgs(connection, functionCode, args);
    if (!callbackArgs)
        return OCI_ERROR;

    // actually make the call to the method
    result = PyEval_CallObject(callback, callbackArgs);
    Py_DECREF(callbackArgs);
    if (!result)
        return OCI_ERROR;

    Py_DECREF(result);
    return OCI_SUCCESS;
}


//-----------------------------------------------------------------------------
// Callback_Handler()
//   Callback handler for calling Python code within an OCI callback.
//-----------------------------------------------------------------------------
static sword Callback_Handler(
    PyObject *tuple,                    // tuple containing connection/callback
    dvoid *handle,                      // pointer to handle
    ub4 handleType,                     // handle type
    ub4 functionCode,                   // function code
    ub1 when,                           // when being called
    sword returnCode,                   // return code
    ub4 *errorCode,                     // error code (IN/OUT)
    va_list args)                       // arguments
{
#ifdef WITH_THREAD
    PyGILState_STATE gstate = PyGILState_Ensure();
#endif
    sword result;

    // perform the call
    result = Callback_Call(tuple, functionCode, args);
    if (result != OCI_CONTINUE)
        PyErr_Print();

    // restore thread state, if necessary
#ifdef WITH_THREAD
    PyGILState_Release(gstate);
#endif

    return result;
}

