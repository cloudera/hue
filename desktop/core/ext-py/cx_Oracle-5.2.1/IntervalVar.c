//-----------------------------------------------------------------------------
// IntervalVar.c
//   Defines the routines for handling interval variables.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Interval type
//-----------------------------------------------------------------------------
typedef struct {
    Variable_HEAD
    OCIInterval **data;
} udt_IntervalVar;


//-----------------------------------------------------------------------------
// Declaration of interval variable functions.
//-----------------------------------------------------------------------------
static int IntervalVar_Initialize(udt_IntervalVar*, udt_Cursor*);
static void IntervalVar_Finalize(udt_IntervalVar*);
static int IntervalVar_SetValue(udt_IntervalVar*, unsigned, PyObject*);
static PyObject *IntervalVar_GetValue(udt_IntervalVar*, unsigned);


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
static PyTypeObject g_IntervalVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.INTERVAL",               // tp_name
    sizeof(udt_IntervalVar),            // tp_basicsize
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
static udt_VariableType vt_Interval = {
    (InitializeProc) IntervalVar_Initialize,
    (FinalizeProc) IntervalVar_Finalize,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) IntervalVar_SetValue,
    (GetValueProc) IntervalVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_IntervalVarType,                 // Python type
    SQLT_INTERVAL_DS,                   // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCIInterval*),               // element length (default)
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


//-----------------------------------------------------------------------------
// IntervalVar_Initialize()
//   Initialize the variable.
//-----------------------------------------------------------------------------
static int IntervalVar_Initialize(
    udt_IntervalVar *var,                    // variable to initialize
    udt_Cursor *cursor)                 // cursor created by
{
    sword status;
    ub4 i;

    // initialize the interval locators
    for (i = 0; i < var->allocatedElements; i++) {
        status = OCIDescriptorAlloc(var->environment->handle,
                (dvoid**) &var->data[i], OCI_DTYPE_INTERVAL_DS, 0, 0);
        if (Environment_CheckForError(var->environment, status,
                "IntervalVar_Initialize()") < 0)
            return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// IntervalVar_Finalize()
//   Prepare for variable destruction.
//-----------------------------------------------------------------------------
static void IntervalVar_Finalize(
    udt_IntervalVar *var)                    // variable to free
{
    ub4 i;

    for (i = 0; i < var->allocatedElements; i++) {
        if (var->data[i])
            OCIDescriptorFree(var->data[i], OCI_DTYPE_INTERVAL_DS);
    }
}


//-----------------------------------------------------------------------------
// IntervalVar_SetValue()
//   Set the value of the variable.
//-----------------------------------------------------------------------------
static int IntervalVar_SetValue(
    udt_IntervalVar *var,               // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    sb4 hours, minutes, seconds;
    PyDateTime_Delta *delta;
    sword status;

    if (!PyDelta_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "expecting timedelta data");
        return -1;
    }

    delta = (PyDateTime_Delta*) value;
    hours = (sb4) delta->seconds / 3600;
    seconds = delta->seconds - hours * 3600;
    minutes = (sb4) seconds / 60;
    seconds -= minutes * 60;
    status = OCIIntervalSetDaySecond(var->environment->handle,
            var->environment->errorHandle, delta->days, hours, minutes,
            seconds, delta->microseconds*1000, var->data[pos]);
    if (Environment_CheckForError(var->environment, status,
                "IntervalVar_SetValue()") < 0)
        return -1;

    return 0;
}


//-----------------------------------------------------------------------------
// IntervalVar_GetValue()
//   Returns the value stored at the given array position.
//-----------------------------------------------------------------------------
static PyObject *IntervalVar_GetValue(
    udt_IntervalVar *var,               // variable to determine value for
    unsigned pos)                       // array position
{
    return OracleIntervalToPythonDelta(var->environment, var->data[pos]);
}

