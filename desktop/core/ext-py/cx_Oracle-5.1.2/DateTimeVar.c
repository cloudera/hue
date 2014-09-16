//-----------------------------------------------------------------------------
// DateTimeVar.c
//   Defines the routines for handling date (time) variables.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// DateTime type
//-----------------------------------------------------------------------------
typedef struct {
    Variable_HEAD
    OCIDate *data;
} udt_DateTimeVar;


//-----------------------------------------------------------------------------
// Declaration of date/time variable functions.
//-----------------------------------------------------------------------------
static int DateTimeVar_SetValue(udt_DateTimeVar*, unsigned, PyObject*);
static PyObject *DateTimeVar_GetValue(udt_DateTimeVar*, unsigned);


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
static PyTypeObject g_DateTimeVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.DATETIME",               // tp_name
    sizeof(udt_DateTimeVar),            // tp_basicsize
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
static udt_VariableType vt_DateTime = {
    (InitializeProc) NULL,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) DateTimeVar_SetValue,
    (GetValueProc) DateTimeVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_DateTimeVarType,                 // Python type
    SQLT_ODT,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCIDate),                    // element length (default)
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_Date = {
    (InitializeProc) NULL,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) DateTimeVar_SetValue,
    (GetValueProc) DateTimeVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_DateTimeVarType,                 // Python type
    SQLT_ODT,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCIDate),                    // element length (default)
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


//-----------------------------------------------------------------------------
// DateTimeVar_SetValue()
//   Set the value of the variable.
//-----------------------------------------------------------------------------
static int DateTimeVar_SetValue(
    udt_DateTimeVar *var,               // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    ub1 month, day, hour, minute, second;
    short year;

    if (PyDateTime_Check(value)) {
        year = (short) PyDateTime_GET_YEAR(value);
        month = PyDateTime_GET_MONTH(value);
        day = PyDateTime_GET_DAY(value);
        hour = PyDateTime_DATE_GET_HOUR(value);
        minute = PyDateTime_DATE_GET_MINUTE(value);
        second = PyDateTime_DATE_GET_SECOND(value);
    } else if (PyDate_Check(value)) {
        year = (short) PyDateTime_GET_YEAR(value);
        month = PyDateTime_GET_MONTH(value);
        day = PyDateTime_GET_DAY(value);
        hour = minute = second = 0;
    } else {
        PyErr_SetString(PyExc_TypeError, "expecting date data");
        return -1;
    }

    // store a copy of the value
    OCIDateSetDate(&var->data[pos], year, month, day);
    OCIDateSetTime(&var->data[pos], hour, minute, second);

    return 0;
}


//-----------------------------------------------------------------------------
// DateTimeVar_GetValue()
//   Returns the value stored at the given array position.
//-----------------------------------------------------------------------------
static PyObject *DateTimeVar_GetValue(
    udt_DateTimeVar *var,               // variable to determine value for
    unsigned pos)                       // array position
{
    return OracleDateToPythonDate(var->type, &var->data[pos]);
}

