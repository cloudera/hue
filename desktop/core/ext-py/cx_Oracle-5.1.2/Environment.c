//-----------------------------------------------------------------------------
// Environment.c
//   Environment handling.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// structure for the Python type
//-----------------------------------------------------------------------------
typedef struct {
    PyObject_HEAD
    OCIEnv *handle;
    OCIError *errorHandle;
    int maxBytesPerCharacter;
    int fixedWidth;
    char *encoding;
    char *nencoding;
    ub4 maxStringBytes;
    PyObject *cloneEnv;
    udt_Buffer numberToStringFormatBuffer;
    udt_Buffer numberFromStringFormatBuffer;
    udt_Buffer nlsNumericCharactersBuffer;
} udt_Environment;

//-----------------------------------------------------------------------------
// maximum number of characters/bytes applicable to strings/binaries
//-----------------------------------------------------------------------------
#define MAX_STRING_CHARS                4000
#define MAX_BINARY_BYTES                4000

//-----------------------------------------------------------------------------
// forward declarations
//-----------------------------------------------------------------------------
static void Environment_Free(udt_Environment*);
static int Environment_CheckForError(udt_Environment*, sword, const char*);

//-----------------------------------------------------------------------------
// declaration of Python type
//-----------------------------------------------------------------------------
static PyTypeObject g_EnvironmentType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "OracleEnvironment",                // tp_name
    sizeof(udt_Environment),            // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) Environment_Free,      // tp_dealloc
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


#include "Error.c"


//-----------------------------------------------------------------------------
// Environment_New()
//   Create a new environment object.
//-----------------------------------------------------------------------------
static udt_Environment *Environment_New(
    OCIEnv *handle)                     // handle to use
{
    udt_Environment *env;
    sword status;

    // create a new object for the Oracle environment
    env = (udt_Environment*) g_EnvironmentType.tp_alloc(&g_EnvironmentType, 0);
    if (!env)
        return NULL;
    env->handle = NULL;
    env->errorHandle = NULL;
    env->fixedWidth = 1;
    env->maxBytesPerCharacter = 1;
    env->maxStringBytes = MAX_STRING_CHARS;
    env->cloneEnv = NULL;
    cxBuffer_Init(&env->numberToStringFormatBuffer);
    cxBuffer_Init(&env->numberFromStringFormatBuffer);
    cxBuffer_Init(&env->nlsNumericCharactersBuffer);

    // create the error handle
    status = OCIHandleAlloc(handle, (dvoid**) &env->errorHandle,
            OCI_HTYPE_ERROR, 0, 0);
    if (Environment_CheckForError(env, status,
            "Environment_New(): create error handle") < 0) {
        Py_DECREF(env);
        return NULL;
    }

    env->handle = handle;
    return env;
}


//-----------------------------------------------------------------------------
// Environment_GetCharacterSetName()
//   Retrieve and store the IANA character set name for the attribute.
//-----------------------------------------------------------------------------
static int Environment_GetCharacterSetName(
    udt_Environment *self,              // environment object
    ub2 attribute,                      // attribute to fetch
    const char *overrideValue,          // override value, if specified
    char **result)                      // place to store result
{
    char charsetName[OCI_NLS_MAXBUFSZ], ianaCharsetName[OCI_NLS_MAXBUFSZ];
    ub2 charsetId;
    sword status;

    // if override value specified, use it
    if (overrideValue) {
        *result = PyMem_Malloc(strlen(overrideValue) + 1);
        if (!*result)
            return -1;
        strcpy(*result, overrideValue);
        return 0;
    }

    // get character set id
    status = OCIAttrGet(self->handle, OCI_HTYPE_ENV, &charsetId, NULL,
            attribute, self->errorHandle);
    if (Environment_CheckForError(self, status,
            "Environment_GetCharacterSetName(): get charset id") < 0)
        return -1;

    // get character set name
    status = OCINlsCharSetIdToName(self->handle, (text*) charsetName,
            OCI_NLS_MAXBUFSZ, charsetId);
    if (Environment_CheckForError(self, status,
            "Environment_GetCharacterSetName(): get Oracle charset name") < 0)
        return -1;

    // get IANA character set name
    status = OCINlsNameMap(self->handle, (oratext*) ianaCharsetName,
            OCI_NLS_MAXBUFSZ, (oratext*) charsetName, OCI_NLS_CS_ORA_TO_IANA);
    if (Environment_CheckForError(self, status,
            "Environment_GetCharacterSetName(): translate NLS charset") < 0)
        return -1;

    // store results
    *result = PyMem_Malloc(strlen(ianaCharsetName) + 1);
    if (!*result)
        return -1;
    strcpy(*result, ianaCharsetName);
    return 0;
}


//-----------------------------------------------------------------------------
// Environment_SetBuffer()
//   Set the buffer in the environment from the specified string.
//-----------------------------------------------------------------------------
static int Environment_SetBuffer(
    udt_Buffer *buf,                    // buffer to set
    const char *value,                  // ASCII value to use
    const char *encoding)               // encoding to use
{
    PyObject *obj;

    obj = cxString_FromAscii(value);
    if (!obj)
        return -1;
    return cxBuffer_FromObject(buf, obj, encoding);
}


//-----------------------------------------------------------------------------
// Environment_NewFromScratch()
//   Create a new environment object from scratch.
//-----------------------------------------------------------------------------
static udt_Environment *Environment_NewFromScratch(
    int threaded,                       // use threaded mode?
    int events,                         // use events mode?
    char *encoding,                     // override value for encoding
    char *nencoding)                    // override value for nencoding
{
    udt_Environment *env;
    OCIEnv *handle;
    sword status;
    ub4 mode;

    // turn threading mode on, if desired
    mode = OCI_OBJECT;
    if (threaded)
        mode |= OCI_THREADED;
#ifdef OCI_EVENTS
    if (events)
        mode |= OCI_EVENTS;
#endif

    // create the new environment handle
    status = OCIEnvNlsCreate(&handle, mode, NULL, NULL, NULL, NULL, 0, NULL, 0,
            0);
    if (!handle ||
            (status != OCI_SUCCESS && status != OCI_SUCCESS_WITH_INFO)) {
        PyErr_SetString(g_InterfaceErrorException,
                "Unable to acquire Oracle environment handle");
        return NULL;
    }

    // create the environment object
    env = Environment_New(handle);
    if (!env) {
        OCIHandleFree(handle, OCI_HTYPE_ENV);
        return NULL;
    }

    // acquire max bytes per character
    status = OCINlsNumericInfoGet(env->handle, env->errorHandle,
            &env->maxBytesPerCharacter, OCI_NLS_CHARSET_MAXBYTESZ);
    if (Environment_CheckForError(env, status,
            "Environment_New(): get max bytes per character") < 0) {
        Py_DECREF(env);
        return NULL;
    }
    env->maxStringBytes = MAX_STRING_CHARS * env->maxBytesPerCharacter;

    // acquire whether character set is fixed width
    status = OCINlsNumericInfoGet(env->handle, env->errorHandle,
            &env->fixedWidth, OCI_NLS_CHARSET_FIXEDWIDTH);
    if (Environment_CheckForError(env, status,
            "Environment_New(): determine if charset fixed width") < 0) {
        Py_DECREF(env);
        return NULL;
    }

    // determine encodings to use for Unicode values
    if (Environment_GetCharacterSetName(env, OCI_ATTR_ENV_CHARSET_ID,
            encoding, &env->encoding) < 0)
        return NULL;
    if (Environment_GetCharacterSetName(env, OCI_ATTR_ENV_NCHARSET_ID,
            nencoding, &env->nencoding) < 0)
        return NULL;

    // fill buffers for number formats
    if (Environment_SetBuffer(&env->numberToStringFormatBuffer, "TM9",
            env->encoding) < 0)
        return NULL;
    if (Environment_SetBuffer(&env->numberFromStringFormatBuffer,
            "999999999999999999999999999999999999999999999999999999999999999",
            env->encoding) < 0)
        return NULL;
    if (Environment_SetBuffer(&env->nlsNumericCharactersBuffer,
            "NLS_NUMERIC_CHARACTERS='.,'", env->encoding) < 0)
        return NULL;

    return env;
}


//-----------------------------------------------------------------------------
// Environment_Clone()
//   Clone an existing environment which is used when acquiring a connection
// from a session pool, for example.
//-----------------------------------------------------------------------------
static udt_Environment *Environment_Clone(
    udt_Environment *cloneEnv)          // environment to clone
{
    udt_Environment *env;

    env = Environment_New(cloneEnv->handle);
    if (!env)
        return NULL;
    env->maxBytesPerCharacter = cloneEnv->maxBytesPerCharacter;
    env->maxStringBytes = cloneEnv->maxStringBytes;
    env->fixedWidth = cloneEnv->fixedWidth;
    Py_INCREF(cloneEnv);
    env->cloneEnv = (PyObject*) cloneEnv;
    env->encoding = cloneEnv->encoding;
    env->nencoding = cloneEnv->nencoding;
    cxBuffer_Copy(&env->numberToStringFormatBuffer,
            &cloneEnv->numberToStringFormatBuffer);
    cxBuffer_Copy(&env->numberFromStringFormatBuffer,
            &cloneEnv->numberFromStringFormatBuffer);
    cxBuffer_Copy(&env->nlsNumericCharactersBuffer,
            &cloneEnv->nlsNumericCharactersBuffer);
    return env;
}


//-----------------------------------------------------------------------------
// Environment_Free()
//   Deallocate the environment. Note that destroying the environment handle
// will automatically destroy any child handles that were created.
//-----------------------------------------------------------------------------
static void Environment_Free(
    udt_Environment *self)              // environment object
{
    if (self->errorHandle)
        OCIHandleFree(self->errorHandle, OCI_HTYPE_ERROR);
    if (self->handle && !self->cloneEnv)
        OCIHandleFree(self->handle, OCI_HTYPE_ENV);
    if (!self->cloneEnv) {
        if (self->encoding)
            PyMem_Free(self->encoding);
        if (self->nencoding)
            PyMem_Free(self->nencoding);
    }
    cxBuffer_Clear(&self->numberToStringFormatBuffer);
    cxBuffer_Clear(&self->numberFromStringFormatBuffer);
    cxBuffer_Clear(&self->nlsNumericCharactersBuffer);
    Py_CLEAR(self->cloneEnv);
    Py_TYPE(self)->tp_free((PyObject*) self);
}


//-----------------------------------------------------------------------------
// Environment_RaiseError()
//   Reads the error that was caused by the last Oracle statement and raise an
// exception for Python. At this point it is assumed that the Oracle
// environment is fully initialized.
//-----------------------------------------------------------------------------
static int Environment_RaiseError(
    udt_Environment *environment,       // environment to raise error for
    const char *context)                // context in which error occurred
{
    PyObject *exceptionType;
    udt_Error *error;

    error = Error_New(environment, context, 1);
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
// Environment_CheckForError()
//   Check for an error in the last call and if an error has occurred, raise a
// Python exception.
//-----------------------------------------------------------------------------
static int Environment_CheckForError(
    udt_Environment *environment,       // environment to raise error in
    sword status,                       // status of last call
    const char *context)                // context
{
    udt_Error *error;

    if (status != OCI_SUCCESS && status != OCI_SUCCESS_WITH_INFO) {
        if (status != OCI_INVALID_HANDLE)
            return Environment_RaiseError(environment, context);
        error = Error_New(environment, context, 0);
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

