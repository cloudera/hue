//-----------------------------------------------------------------------------
// Error.c
//   Error handling.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// structure for the Python type
//-----------------------------------------------------------------------------
typedef struct {
    PyObject_HEAD
    sb4 code;
    ub2 offset;
    PyObject *message;
    const char *context;
} udt_Error;


//-----------------------------------------------------------------------------
// maximum size of error message string in bytes
//-----------------------------------------------------------------------------
#ifdef OCI_ERROR_MAXMSG_SIZE2
#define ERROR_BUF_SIZE                OCI_ERROR_MAXMSG_SIZE2
#else
#define ERROR_BUF_SIZE                OCI_ERROR_MAXMSG_SIZE
#endif


//-----------------------------------------------------------------------------
// forward declarations
//-----------------------------------------------------------------------------
static void Error_Free(udt_Error*);
static PyObject *Error_Str(udt_Error*);


//-----------------------------------------------------------------------------
// declaration of members
//-----------------------------------------------------------------------------
static PyMemberDef g_ErrorMembers[] = {
    { "code", T_INT, offsetof(udt_Error, code), READONLY },
    { "offset", T_INT, offsetof(udt_Error, offset), READONLY },
    { "message", T_OBJECT, offsetof(udt_Error, message), READONLY },
    { "context", T_STRING, offsetof(udt_Error, context), READONLY },
    { NULL }
};


//-----------------------------------------------------------------------------
// declaration of Python type
//-----------------------------------------------------------------------------
static PyTypeObject g_ErrorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle._Error",                 // tp_name
    sizeof(udt_Error),                  // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) Error_Free,            // tp_dealloc
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
    (reprfunc) Error_Str,               // tp_str
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
    g_ErrorMembers,                     // tp_members
    0                                   // tp_getset
};


//-----------------------------------------------------------------------------
// Error_New()
//   Create a new error object.
//-----------------------------------------------------------------------------
static udt_Error *Error_New(
    udt_Environment *environment,       // environment object
    const char *context,                // context in which error occurred
    ub4 handleType,                     // handle type
    dvoid* handle)                      // handle
{
    char errorText[ERROR_BUF_SIZE];
    udt_Error *self;
    sword status;
#if PY_MAJOR_VERSION >= 3
    Py_ssize_t len;
#endif

    self = (udt_Error*) g_ErrorType.tp_alloc(&g_ErrorType, 0);
    if (!self)
        return NULL;
    self->context = context;

    if (handle) {
        status = OCIErrorGet(handle, 1, 0, &self->code,
                (unsigned char*) errorText, sizeof(errorText), handleType);
        if (status != OCI_SUCCESS) {
            Py_DECREF(self);
            PyErr_SetString(g_InternalErrorException, "No Oracle error?");
            return NULL;
        }
#if PY_MAJOR_VERSION < 3
        self->message = PyBytes_FromString(errorText);
#else
        len = strlen(errorText);
        self->message = PyUnicode_Decode(errorText, len, environment->encoding,
                NULL);
#endif
        if (!self->message) {
            Py_DECREF(self);
            return NULL;
        }
    }

    return self;
}


//-----------------------------------------------------------------------------
// Error_Free()
//   Deallocate the environment, disconnecting from the database if necessary.
//-----------------------------------------------------------------------------
static void Error_Free(
    udt_Error *self)                    // error object
{
    Py_CLEAR(self->message);
    PyObject_Del(self);
}


//-----------------------------------------------------------------------------
// Error_Str()
//   Return a string representation of the error variable.
//-----------------------------------------------------------------------------
static PyObject *Error_Str(
    udt_Error *self)                    // variable to return the string for
{
    if (self->message) {
        Py_INCREF(self->message);
        return self->message;
    }
    return cxString_FromAscii("");
}


//-----------------------------------------------------------------------------
// Error_Raise()
//   Reads the error that was caused by the last Oracle statement and raise an
// exception for Python. Return -1 as a convenience to the caller.
//-----------------------------------------------------------------------------
static int Error_Raise(
    udt_Environment *environment,       // environment object
    const char *context,                // context in which error occurred
    OCIError* errorHandle)              // handle
{
    PyObject *exceptionType;
    udt_Error *error;

    error = Error_New(environment, context, OCI_HTYPE_ERROR, errorHandle);
    if (error) {
        switch (error->code) {
            case 1:
            case 1400:
            case 2290:
            case 2291:
            case 2292:
                exceptionType = g_IntegrityErrorException;
                break;
            case 22:
            case 378:
            case 602:
            case 603:
            case 604:
            case 609:
            case 1012:
            case 1013:
            case 1033:
            case 1034:
            case 1041:
            case 1043:
            case 1089:
            case 1090:
            case 1092:
            case 3113:
            case 3114:
            case 3122:
            case 3135:
            case 12153:
            case 12203:
            case 12500:
            case 12571:
            case 27146:
            case 28511:
                exceptionType = g_OperationalErrorException;
                break;
            default:
                exceptionType = g_DatabaseErrorException;
                break;
        }
        PyErr_SetObject(exceptionType, (PyObject*) error);
        Py_DECREF(error);
    }
    return -1;
}


//-----------------------------------------------------------------------------
// Error_Check()
//   Check for an error in the last call and if an error has occurred, raise a
// Python exception.
//-----------------------------------------------------------------------------
static int Error_Check(
    udt_Environment *environment,       // environment to raise error in
    sword status,                       // status of last call
    const char *context,                // context
    OCIError *errorHandle)              // error handle to use
{
    udt_Error *error;

    if (status != OCI_SUCCESS && status != OCI_SUCCESS_WITH_INFO) {
        if (status != OCI_INVALID_HANDLE)
            return Error_Raise(environment, context, errorHandle);
        error = Error_New(environment, context, 0, NULL);
        if (!error)
            return -1;
        error->code = 0;
        error->message = cxString_FromAscii("Invalid handle!");
        if (!error->message)
            Py_DECREF(error);
        else PyErr_SetObject(g_DatabaseErrorException, (PyObject*) error);
        return -1;
    }
    return 0;
}

