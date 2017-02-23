//-----------------------------------------------------------------------------
// ObjectVar.c
//   Defines the routines for handling Oracle object variables.
//-----------------------------------------------------------------------------

#include "ObjectType.c"
#include "ExternalObjectVar.c"

//-----------------------------------------------------------------------------
// Object type
//-----------------------------------------------------------------------------
typedef struct {
    Variable_HEAD
    dvoid **data;
    dvoid **objectIndicator;
    udt_Connection *connection;
    udt_ObjectType *objectType;
} udt_ObjectVar;

//-----------------------------------------------------------------------------
// Declaration of object variable functions.
//-----------------------------------------------------------------------------
static int ObjectVar_Initialize(udt_ObjectVar*, udt_Cursor*);
static void ObjectVar_Finalize(udt_ObjectVar*);
static PyObject *ObjectVar_GetValue(udt_ObjectVar*, unsigned);
static int ObjectVar_PreDefine(udt_ObjectVar*, OCIParam*);
static int ObjectVar_PostDefine(udt_ObjectVar*);
static int ObjectVar_IsNull(udt_ObjectVar*, unsigned);

//-----------------------------------------------------------------------------
// declaration of members for Oracle objects
//-----------------------------------------------------------------------------
static PyMemberDef g_ObjectVarMembers[] = {
    { "type", T_OBJECT, offsetof(udt_ObjectVar, objectType), READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// Python type declarations
//-----------------------------------------------------------------------------
static PyTypeObject g_ObjectVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.OBJECTVAR",              // tp_name
    sizeof(udt_ObjectVar),              // tp_basicsize
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
    0,                                  // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    0,                                  // tp_iter
    0,                                  // tp_iternext
    0,                                  // tp_methods
    g_ObjectVarMembers                 // tp_members
};


//-----------------------------------------------------------------------------
// variable type declarations
//-----------------------------------------------------------------------------
static udt_VariableType vt_Object = {
    (InitializeProc) ObjectVar_Initialize,
    (FinalizeProc) ObjectVar_Finalize,
    (PreDefineProc) ObjectVar_PreDefine,
    (PostDefineProc) ObjectVar_PostDefine,
    (PreFetchProc) NULL,
    (IsNullProc) ObjectVar_IsNull,
    (SetValueProc) NULL,
    (GetValueProc) ObjectVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_ObjectVarType,                   // Python type
    SQLT_NTY,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(dvoid*),                     // element length
    0,                                  // is character data
    0,                                  // is variable length
    0,                                  // can be copied
    0                                   // can be in array
};


//-----------------------------------------------------------------------------
// ObjectVar_Initialize()
//   Initialize the variable.
//-----------------------------------------------------------------------------
static int ObjectVar_Initialize(
    udt_ObjectVar *self,                // variable to initialize
    udt_Cursor *cursor)                 // cursor to use
{
    int i;

    Py_INCREF(cursor->connection);
    self->connection = cursor->connection;
    self->objectType = NULL;
    self->objectIndicator =
            PyMem_Malloc(self->allocatedElements * sizeof(dvoid*));
    if (!self->objectIndicator) {
        PyErr_NoMemory();
        return -1;
    }
    for (i = 0; i < self->allocatedElements; i++) {
        self->data[i] = NULL;
        self->objectIndicator[i] = NULL;
    }
    return 0;
}


//-----------------------------------------------------------------------------
// ObjectVar_Finalize()
//   Prepare for variable destruction.
//-----------------------------------------------------------------------------
static void ObjectVar_Finalize(
    udt_ObjectVar *self)                // variable to free
{
    int i;

    for (i = 0; i < self->allocatedElements; i++) {
        if (self->data[i])
            OCIObjectFree(self->environment->handle,
                    self->environment->errorHandle, self->data[i],
                    OCI_OBJECTFREE_FORCE);
    }
    Py_DECREF(self->connection);
    Py_XDECREF(self->objectType);
    if (self->objectIndicator)
        PyMem_Free(self->objectIndicator);
}


//-----------------------------------------------------------------------------
// ObjectVar_PreDefine()
//   Performs additional steps required for defining objects.
//-----------------------------------------------------------------------------
static int ObjectVar_PreDefine(
    udt_ObjectVar *self,                // variable to set up
    OCIParam *param)                    // parameter being defined
{
    self->objectType = ObjectType_New(self->connection, param,
            OCI_ATTR_TYPE_NAME);
    if (!self->objectType)
        return -1;
    return 0;
}


//-----------------------------------------------------------------------------
// ObjectVar_PostDefine()
//   Performs additional steps required for defining objects.
//-----------------------------------------------------------------------------
static int ObjectVar_PostDefine(
    udt_ObjectVar *self)                // variable to set up
{
    sword status;

    status = OCIDefineObject(self->defineHandle,
            self->environment->errorHandle, self->objectType->tdo, self->data,
            0, self->objectIndicator, 0);
    return Environment_CheckForError(self->environment, status,
            "ObjectVar_PostDefine(): define object");
}


//-----------------------------------------------------------------------------
// ObjectVar_IsNull()
//   Returns a boolean indicating if the variable is null or not.
//-----------------------------------------------------------------------------
static int ObjectVar_IsNull(
    udt_ObjectVar *self,                // variable to set up
    unsigned pos)                       // position to check
{
    if (!self->objectIndicator[pos])
        return 1;
    return (*((OCIInd*) self->objectIndicator[pos]) == OCI_IND_NULL);
}


//-----------------------------------------------------------------------------
// ObjectVar_GetValue()
//   Returns the value stored at the given array position.
//-----------------------------------------------------------------------------
static PyObject *ObjectVar_GetValue(
    udt_ObjectVar *self,                // variable to determine value for
    unsigned pos)                       // array position
{
    PyObject *var;

    // only allowed to get the value once (for now)
    if (!self->data[pos]) {
        PyErr_SetString(g_ProgrammingErrorException,
                "variable value can only be acquired once");
        return NULL;
    }

    // for collections, return the list rather than the object
    if (self->objectType->isCollection)
        return ExternalObjectVar_ConvertCollection(self->environment,
                self->data[pos], (PyObject*) self, self->objectType);

    // for objects, return a representation of the object
    var = ExternalObjectVar_New((PyObject*) self, self->objectType,
            self->data[pos], self->objectIndicator[pos], 1);
    if (!var)
        return NULL;
    self->data[pos] = NULL;
    self->objectIndicator[pos] = NULL;
    return var;
}

