//-----------------------------------------------------------------------------
// TimestampVar.c
//   Defines the routines for handling timestamp variables.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Timestamp type
//-----------------------------------------------------------------------------
typedef struct {
    Variable_HEAD
    OCIDateTime **data;
} udt_TimestampVar;


//-----------------------------------------------------------------------------
// Declaration of date/time variable functions.
//-----------------------------------------------------------------------------
static int TimestampVar_Initialize(udt_TimestampVar*, udt_Cursor*);
static void TimestampVar_Finalize(udt_TimestampVar*);
static int TimestampVar_SetValue(udt_TimestampVar*, unsigned, PyObject*);
static PyObject *TimestampVar_GetValue(udt_TimestampVar*, unsigned);


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
static PyTypeObject g_TimestampVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.TIMESTAMP",              // tp_name
    sizeof(udt_TimestampVar),           // tp_basicsize
    0,                                  // tp_itemsize
    0,                                  // tp_dealloc
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
    0                                   // tp_doc
};


//-----------------------------------------------------------------------------
// variable type declarations
//-----------------------------------------------------------------------------
static udt_VariableType vt_Timestamp = {
    (InitializeProc) TimestampVar_Initialize,
    (FinalizeProc) TimestampVar_Finalize,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) TimestampVar_SetValue,
    (GetValueProc) TimestampVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_TimestampVarType,                // Python type
    SQLT_TIMESTAMP,                     // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCIDateTime*),               // element length (default)
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


//-----------------------------------------------------------------------------
// TimestampVar_Initialize()
//   Initialize the variable.
//-----------------------------------------------------------------------------
static int TimestampVar_Initialize(
    udt_TimestampVar *var,              // variable to initialize
    udt_Cursor *cursor)                 // cursor variable associated with
{
    sword status;
    ub4 i;

    // initialize the LOB locators
    for (i = 0; i < var->allocatedElements; i++) {
        status = OCIDescriptorAlloc(var->environment->handle,
                (dvoid**) &var->data[i], OCI_DTYPE_TIMESTAMP, 0, 0);
        if (Environment_CheckForError(var->environment, status,
                "TimestampVar_Initialize()") < 0)
            return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// TimestampVar_Finalize()
//   Prepare for variable destruction.
//-----------------------------------------------------------------------------
static void TimestampVar_Finalize(
    udt_TimestampVar *var)              // variable to free
{
    ub4 i;

    for (i = 0; i < var->allocatedElements; i++) {
        if (var->data[i])
            OCIDescriptorFree(var->data[i], OCI_DTYPE_TIMESTAMP);
    }
}


//-----------------------------------------------------------------------------
// TimestampVar_SetValue()
//   Set the value of the variable.
//-----------------------------------------------------------------------------
static int TimestampVar_SetValue(
    udt_TimestampVar *var,              // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    sword status;
    uword valid;

    // make sure a timestamp is being bound
    if (!PyDateTime_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "expecting timestamp data");
        return -1;
    }

    // store a copy of the value
    status = OCIDateTimeConstruct(var->environment->handle,
            var->environment->errorHandle, var->data[pos],
            (sb2) PyDateTime_GET_YEAR(value),
            PyDateTime_GET_MONTH(value),
            PyDateTime_GET_DAY(value),
            PyDateTime_DATE_GET_HOUR(value),
            PyDateTime_DATE_GET_MINUTE(value),
            PyDateTime_DATE_GET_SECOND(value),
            PyDateTime_DATE_GET_MICROSECOND(value) * 1000, NULL, 0);
    if (Environment_CheckForError(var->environment, status,
            "TimestampVar_SetValue(): create structure") < 0)
        return -1;
    status = OCIDateTimeCheck(var->environment->handle,
            var->environment->errorHandle, var->data[pos], &valid);
    if (Environment_CheckForError(var->environment, status,
            "TimestampVar_SetValue()") < 0)
        return -1;
    if (valid != 0) {
        PyErr_SetString(g_DataErrorException, "invalid date");
        return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// TimestampVar_GetValue()
//   Returns the value stored at the given array position.
//-----------------------------------------------------------------------------
static PyObject *TimestampVar_GetValue(
    udt_TimestampVar *var,              // variable to determine value for
    unsigned pos)                       // array position
{
    return OracleTimestampToPythonDate(var->environment, var->data[pos]);
}

