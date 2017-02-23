//-----------------------------------------------------------------------------
// NumberVar.c
//   Defines the routines for handling numeric variables.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Number types
//-----------------------------------------------------------------------------
typedef struct {
    Variable_HEAD
    OCINumber *data;
} udt_NumberVar;


typedef struct {
    Variable_HEAD
    double *data;
} udt_NativeFloatVar;


//-----------------------------------------------------------------------------
// Declaration of number variable functions.
//-----------------------------------------------------------------------------
static int NumberVar_PreDefine(udt_NumberVar*, OCIParam*);
static int NumberVar_SetValue(udt_NumberVar*, unsigned, PyObject*);
static PyObject *NumberVar_GetValue(udt_NumberVar*, unsigned);
static int NativeFloatVar_SetValue(udt_NativeFloatVar*, unsigned, PyObject*);
static PyObject *NativeFloatVar_GetValue(udt_NativeFloatVar*, unsigned);


//-----------------------------------------------------------------------------
// Python type declaration
//-----------------------------------------------------------------------------
static PyTypeObject g_NumberVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.NUMBER",                 // tp_name
    sizeof(udt_NumberVar),              // tp_basicsize
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


static PyTypeObject g_NativeFloatVarType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "cx_Oracle.NATIVE_FLOAT",           // tp_name
    sizeof(udt_NativeFloatVar),         // tp_basicsize
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
static udt_VariableType vt_Float = {
    (InitializeProc) NULL,
    (FinalizeProc) NULL,
    (PreDefineProc) NumberVar_PreDefine,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) NumberVar_SetValue,
    (GetValueProc) NumberVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_NumberVarType,                   // Python type
    SQLT_VNU,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCINumber),                  // element length
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_NativeFloat = {
    (InitializeProc) NULL,
    (FinalizeProc) NULL,
    (PreDefineProc) NULL,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) NativeFloatVar_SetValue,
    (GetValueProc) NativeFloatVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_NativeFloatVarType,              // Python type
    SQLT_BDOUBLE,                       // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(double),                     // element length
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_Integer = {
    (InitializeProc) NULL,
    (FinalizeProc) NULL,
    (PreDefineProc) NumberVar_PreDefine,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) NumberVar_SetValue,
    (GetValueProc) NumberVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_NumberVarType,                   // Python type
    SQLT_VNU,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCINumber),                  // element length
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_LongInteger = {
    (InitializeProc) NULL,
    (FinalizeProc) NULL,
    (PreDefineProc) NumberVar_PreDefine,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) NumberVar_SetValue,
    (GetValueProc) NumberVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_NumberVarType,                   // Python type
    SQLT_VNU,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCINumber),                  // element length
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


static udt_VariableType vt_NumberAsString = {
    (InitializeProc) NULL,
    (FinalizeProc) NULL,
    (PreDefineProc) NumberVar_PreDefine,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) NumberVar_SetValue,
    (GetValueProc) NumberVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_NumberVarType,                   // Python type
    SQLT_VNU,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCINumber),                  // element length
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};


#if ORACLE_VERSION_HEX < ORACLE_VERSION(12, 1)
static udt_VariableType vt_Boolean = {
    (InitializeProc) NULL,
    (FinalizeProc) NULL,
    (PreDefineProc) NumberVar_PreDefine,
    (PostDefineProc) NULL,
    (PreFetchProc) NULL,
    (IsNullProc) NULL,
    (SetValueProc) NumberVar_SetValue,
    (GetValueProc) NumberVar_GetValue,
    (GetBufferSizeProc) NULL,
    &g_NumberVarType,                   // Python type
    SQLT_VNU,                           // Oracle type
    SQLCS_IMPLICIT,                     // charset form
    sizeof(OCINumber),                  // element length
    0,                                  // is character data
    0,                                  // is variable length
    1,                                  // can be copied
    1                                   // can be in array
};
#endif


//-----------------------------------------------------------------------------
// NumberVar_PreDefine()
//   Set the type of value (integer, float or string) that will be returned
// when values are fetched from this variable.
//-----------------------------------------------------------------------------
static int NumberVar_PreDefine(
    udt_NumberVar *var,                 // variable to initialize
    OCIParam *param)                    // parameter handle
{
    static int maxLongSafeDigits = sizeof(long) >= 8 ? 18 : 9;
    sb2 precision;
    sword status;
    sb1 scale;

    // if the return type has not already been specified, check to see if the
    // number can fit inside an integer by looking at the precision and scale
    if (var->type == &vt_Float) {
        scale = 0;
        precision = 0;
        status = OCIAttrGet(param, OCI_HTYPE_DESCRIBE, (dvoid*) &scale, 0,
                OCI_ATTR_SCALE, var->environment->errorHandle);
        if (Environment_CheckForError(var->environment, status,
                "NumberVar_PreDefine(): scale") < 0)
            return -1;
        status = OCIAttrGet(param, OCI_HTYPE_DESCRIBE, (dvoid*) &precision, 0,
                OCI_ATTR_PRECISION, var->environment->errorHandle);
        if (Environment_CheckForError(var->environment, status,
                "NumberVar_PreDefine(): precision") < 0)
            return -1;
        if (scale == 0 || (scale == -127 && precision == 0)) {
            var->type = &vt_LongInteger;
            if (precision > 0 && precision <= maxLongSafeDigits)
                var->type = &vt_Integer;
        }
    }

    return 0;
}


//-----------------------------------------------------------------------------
// NumberVar_SetValueFromBoolean()
//   Set the value of the variable from a Python boolean.
//-----------------------------------------------------------------------------
static int NumberVar_SetValueFromBoolean(
    udt_NumberVar *var,                 // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    long integerValue;
    sword status;

    integerValue = (value == Py_True);
    status = OCINumberFromInt(var->environment->errorHandle, &integerValue,
            sizeof(long), OCI_NUMBER_SIGNED, &var->data[pos]);
    return Environment_CheckForError(var->environment, status,
            "NumberVar_SetValueFromBoolean()");
}


#if PY_MAJOR_VERSION < 3
//-----------------------------------------------------------------------------
// NumberVar_SetValueFromInteger()
//   Set the value of the variable from a Python integer.
//-----------------------------------------------------------------------------
static int NumberVar_SetValueFromInteger(
    udt_NumberVar *var,                 // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    long integerValue;
    sword status;

    integerValue = PyInt_AS_LONG(value);
    status = OCINumberFromInt(var->environment->errorHandle, &integerValue,
            sizeof(long), OCI_NUMBER_SIGNED, &var->data[pos]);
    return Environment_CheckForError(var->environment, status,
            "NumberVar_SetValueFromInteger()");
}
#endif


//-----------------------------------------------------------------------------
// NumberVar_SetValueFromFloat()
//   Set the value of the variable from a Python float.
//-----------------------------------------------------------------------------
static int NumberVar_SetValueFromFloat(
    udt_NumberVar *var,                 // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    double doubleValue;
    sword status;

    doubleValue = PyFloat_AS_DOUBLE(value);
    status = OCINumberFromReal(var->environment->errorHandle, &doubleValue,
            sizeof(double), &var->data[pos]);
    return Environment_CheckForError(var->environment, status,
            "NumberVar_SetValueFromFloat()");
}


//-----------------------------------------------------------------------------
// NumberVar_SetValueFromLong()
//   Set the value of the variable from a Python long.
//-----------------------------------------------------------------------------
static int NumberVar_SetValueFromLong(
    udt_NumberVar *var,                 // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    udt_Buffer textBuffer;
    PyObject *textValue;
    sword status;

    textValue = PyObject_Str(value);
    if (!textValue)
        return -1;
    if (cxBuffer_FromObject(&textBuffer, textValue,
            var->environment->encoding) < 0)
        return -1;
    status = OCINumberFromText(var->environment->errorHandle,
            (text*) textBuffer.ptr, textBuffer.size,
            (text*) var->environment->numberFromStringFormatBuffer.ptr,
            var->environment->numberFromStringFormatBuffer.size, NULL, 0,
            &var->data[pos]);
    cxBuffer_Clear(&textBuffer);
    Py_DECREF(textValue);
    return Environment_CheckForError(var->environment, status,
            "NumberVar_SetValueFromLong()");
}


//-----------------------------------------------------------------------------
// NumberVar_GetFormatAndTextFromDecimal()
//   Return the number format and text to use for the Decimal object.
//-----------------------------------------------------------------------------
static int NumberVar_GetFormatAndTextFromDecimal(
    PyObject *tupleValue,               // decimal as_tuple() value
    PyObject **textObj,                 // text string for conversion
    PyObject **formatObj)               // format for conversion
{
    long numDigits, scale, i, sign, length, digit;
    char *textValue, *format, *textPtr, *formatPtr;
    PyObject *digits;

    // acquire basic information from the value tuple
    sign = PyInt_AsLong(PyTuple_GET_ITEM(tupleValue, 0));
    if (PyErr_Occurred())
        return -1;
    digits = PyTuple_GET_ITEM(tupleValue, 1);
    scale = PyInt_AsLong(PyTuple_GET_ITEM(tupleValue, 2));
    if (PyErr_Occurred())
        return -1;
    numDigits = PyTuple_GET_SIZE(digits);

    // allocate memory for the string and format to use in conversion
    length = numDigits + abs(scale) + 3;
    textValue = textPtr = PyMem_Malloc(length);
    if (!textValue) {
        PyErr_NoMemory();
        return -1;
    }
    format = formatPtr = PyMem_Malloc(length);
    if (!format) {
        PyMem_Free(textValue);
        PyErr_NoMemory();
        return -1;
    }

    // populate the string and format
    if (sign)
        *textPtr++ = '-';
    for (i = 0; i < numDigits + scale; i++) {
        *formatPtr++ = '9';
        if (i < numDigits) {
            digit = PyInt_AsLong(PyTuple_GetItem(digits, i));
            if (PyErr_Occurred()) {
                PyMem_Free(textValue);
                return -1;
            }
        }
        else digit = 0;
        *textPtr++ = '0' + (char) digit;
    }
    if (scale < 0) {
        *formatPtr++ = 'D';
        *textPtr++ = '.';
        for (i = scale; i < 0; i++) {
            *formatPtr++ = '9';
            if (numDigits + i < 0)
                digit = 0;
            else {
                digit = PyInt_AsLong(PyTuple_GetItem(digits, numDigits + i));
                if (PyErr_Occurred()) {
                    PyMem_Free(textValue);
                    return -1;
                }
            }
            *textPtr++ = '0' + (char) digit;
        }
    }
    *formatPtr = '\0';
    *textPtr = '\0';
    *textObj = cxString_FromAscii(textValue);
    PyMem_Free(textValue);
    if (!*textObj) {
        PyMem_Free(format);
        return -1;
    }
    *formatObj = cxString_FromAscii(format);
    PyMem_Free(format);
    if (!*formatObj) {
        Py_DECREF(*textObj);
        return -1;
    }

    return 0;
}


//-----------------------------------------------------------------------------
// NumberVar_SetValueFromDecimal()
//   Set the value of the variable from a Python decimal.Decimal object.
//-----------------------------------------------------------------------------
static int NumberVar_SetValueFromDecimal(
    udt_NumberVar *var,                 // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    PyObject *textValue, *format, *tupleValue;
    udt_Buffer textBuffer, formatBuffer;
    sword status;

    tupleValue = PyObject_CallMethod(value, "as_tuple", NULL);
    if (!tupleValue)
        return -1;
    if (NumberVar_GetFormatAndTextFromDecimal(tupleValue, &textValue,
            &format) < 0) {
        Py_DECREF(tupleValue);
        return -1;
    }
    Py_DECREF(tupleValue);
    if (cxBuffer_FromObject(&textBuffer, textValue,
            var->environment->encoding) < 0)
        return -1;
    if (cxBuffer_FromObject(&formatBuffer, format,
            var->environment->encoding) < 0) {
        cxBuffer_Clear(&textBuffer);
        return -1;
    }
    status = OCINumberFromText(var->environment->errorHandle,
            (text*) textBuffer.ptr, textBuffer.size, (text*) formatBuffer.ptr,
            formatBuffer.size,
            var->environment->nlsNumericCharactersBuffer.ptr,
            var->environment->nlsNumericCharactersBuffer.size,
            &var->data[pos]);
    cxBuffer_Clear(&textBuffer);
    cxBuffer_Clear(&formatBuffer);
    Py_DECREF(textValue);
    Py_DECREF(format);
    return Environment_CheckForError(var->environment, status,
            "NumberVar_SetValueFromDecimal()");
}


//-----------------------------------------------------------------------------
// NumberVar_SetValue()
//   Set the value of the variable.
//-----------------------------------------------------------------------------
static int NumberVar_SetValue(
    udt_NumberVar *var,                 // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
#if PY_MAJOR_VERSION < 3
    if (PyInt_Check(value))
        return NumberVar_SetValueFromInteger(var, pos, value);
#endif
    if (PyBool_Check(value))
        return NumberVar_SetValueFromBoolean(var, pos, value);
    if (PyLong_Check(value))
        return NumberVar_SetValueFromLong(var, pos, value);
    if (PyFloat_Check(value))
        return NumberVar_SetValueFromFloat(var, pos, value);
    if (Py_TYPE(value) == g_DecimalType)
        return NumberVar_SetValueFromDecimal(var, pos, value);
    PyErr_SetString(PyExc_TypeError, "expecting numeric data");
    return -1;
}


//-----------------------------------------------------------------------------
// NumberVar_GetValue()
//   Returns the value stored at the given array position.
//-----------------------------------------------------------------------------
static PyObject *NumberVar_GetValue(
    udt_NumberVar *var,                 // variable to determine value for
    unsigned pos)                       // array position
{
    PyObject *result, *stringObj;
    char stringValue[200];
    long integerValue;
    ub4 stringLength;
    sword status;

    if (var->type == &vt_Boolean || var->type == &vt_Integer) {
        status = OCINumberToInt(var->environment->errorHandle, &var->data[pos],
                sizeof(long), OCI_NUMBER_SIGNED, (dvoid*) &integerValue);
        if (Environment_CheckForError(var->environment, status,
                "NumberVar_GetValue(): as integer") < 0)
            return NULL;

        if (var->type == &vt_Boolean)
            return PyBool_FromLong(integerValue);
#if PY_MAJOR_VERSION >= 3
        return PyLong_FromLong(integerValue);
#else
        return PyInt_FromLong(integerValue);
#endif
    }

    if (var->type == &vt_NumberAsString || var->type == &vt_LongInteger) {
        stringLength = sizeof(stringValue);
        status = OCINumberToText(var->environment->errorHandle,
                &var->data[pos],
                (text*) var->environment->numberToStringFormatBuffer.ptr,
                var->environment->numberToStringFormatBuffer.size, NULL, 0,
                &stringLength, (unsigned char*) stringValue);
        if (Environment_CheckForError(var->environment, status,
                "NumberVar_GetValue(): as string") < 0)
            return NULL;
        stringObj = cxString_FromEncodedString(stringValue, stringLength,
                var->environment->encoding);
        if (!stringObj)
            return NULL;
        if (var->type == &vt_NumberAsString)
            return stringObj;
#if PY_MAJOR_VERSION >= 3
        result = PyNumber_Long(stringObj);
#else
        result = PyNumber_Int(stringObj);
#endif
        Py_DECREF(stringObj);
        if (result || !PyErr_ExceptionMatches(PyExc_ValueError))
            return result;
        PyErr_Clear();
    }

    return OracleNumberToPythonFloat(var->environment, &var->data[pos]);
}


//-----------------------------------------------------------------------------
// NativeFloatVar_GetValue()
//   Returns the value stored at the given array position as a float.
//-----------------------------------------------------------------------------
static PyObject *NativeFloatVar_GetValue(
    udt_NativeFloatVar *var,            // variable to determine value for
    unsigned pos)                       // array position
{
    return PyFloat_FromDouble(var->data[pos]);
}


//-----------------------------------------------------------------------------
// NativeFloatVar_SetValue()
//   Set the value of the variable which should be a native double.
//-----------------------------------------------------------------------------
static int NativeFloatVar_SetValue(
    udt_NativeFloatVar *var,            // variable to set value for
    unsigned pos,                       // array position to set
    PyObject *value)                    // value to set
{
    if (!PyFloat_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "expecting float");
        return -1;
    }
    var->data[pos] = PyFloat_AS_DOUBLE(value);
    return 0;
}

