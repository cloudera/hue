//-----------------------------------------------------------------------------
// CursorVar.c
//   Defines the routines specific to the cursor type.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Cursor variable type
//-----------------------------------------------------------------------------
typedef struct {
    Variable_HEAD
    OCIStmt **data;
    udt_Connection *connection;
    PyObject *cursors;
} udt_CursorVar;


//-----------------------------------------------------------------------------
// Declaration of cursor variable functions.
//-----------------------------------------------------------------------------
static int CursorVar_Initialize(udt_CursorVar*, udt_Cursor*);
static void CursorVar_Finalize(udt_CursorVar*);
static int CursorVar_SetValue(udt_CursorVar*, unsigned, PyObject*);
static PyObject *CursorVar_GetValue(udt_CursorVar*, unsigned);


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
static PyTypeObject g_CursorVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.CURSOR",                 // tp_name
    sizeof(udt_CursorVar),              // tp_basicsize
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
static udt_VariableType vt_Cursor = {
    (InitializeProc) CursorVar_Initialize,
    (FinalizeProc) CursorVar_Finalize,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) CursorVar_SetValue,
    (GetValueProc) CursorVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_CursorVarType,                   // Python type
    SQLT_RSET,                          // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCIStmt*),                   // element length
    0,                                  // is character data
    0,                                  // is variable length
    0,                                  // can be copied
    0                                   // can be in array
};


//-----------------------------------------------------------------------------
// CursorVar_Initialize()
//   Initialize the variable.
//-----------------------------------------------------------------------------
static int CursorVar_Initialize(
    udt_CursorVar *var,                 // variable to initialize
    udt_Cursor *cursor)                 // cursor created by
{
    udt_Cursor *tempCursor;
    ub4 i;

    Py_INCREF(cursor->connection);
    var->connection = cursor->connection;
    var->cursors = PyList_New(var->allocatedElements);
    if (!var->cursors)
        return -1;
    for (i = 0; i < var->allocatedElements; i++) {
        tempCursor = (udt_Cursor*) Connection_NewCursor(var->connection, NULL);
        if (!tempCursor) {
            Py_DECREF(var);
            return -1;
        }
        PyList_SET_ITEM(var->cursors, i, (PyObject*) tempCursor);
        if (Cursor_AllocateHandle(tempCursor) < 0) {
            Py_DECREF(var);
            return -1;
        }
        var->data[i] = tempCursor->handle;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// CursorVar_Finalize()
//   Prepare for variable destruction.
//-----------------------------------------------------------------------------
static void CursorVar_Finalize(
    udt_CursorVar *var)                 // variable to free
{
    Py_DECREF(var->connection);
    Py_XDECREF(var->cursors);
}


//-----------------------------------------------------------------------------
// CursorVar_SetValue()
//   Set the value of the variable.
//-----------------------------------------------------------------------------
static int CursorVar_SetValue(
    udt_CursorVar *var,                 // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    udt_Cursor *cursor;

    if (!PyObject_IsInstance(value, (PyObject*) &g_CursorType)) {
        PyErr_SetString(PyExc_TypeError, "expecting cursor");
        return -1;
    }

    Py_XDECREF(PyList_GET_ITEM(var->cursors, pos));
    Py_INCREF(value);
    PyList_SET_ITEM(var->cursors, pos, value);
    cursor = (udt_Cursor *) value;
    if (!cursor->isOwned) {
        if (Cursor_FreeHandle(cursor, 1) < 0)
            return -1;
        cursor->isOwned = 1;
        if (Cursor_AllocateHandle(cursor) < 0)
            return -1;
    }
    var->data[pos] = cursor->handle;
    cursor->statementType = -1;
    return 0;
}


//-----------------------------------------------------------------------------
// CursorVar_GetValue()
//   Set the value of the variable.
//-----------------------------------------------------------------------------
static PyObject *CursorVar_GetValue(
    udt_CursorVar *var,                 // variable to set value for
    unsigned pos)                       // array position to set
{
    PyObject *cursor;

    cursor = PyList_GET_ITEM(var->cursors, pos);
    ((udt_Cursor*) cursor)->statementType = -1;
    Py_INCREF(cursor);
    return cursor;
}

