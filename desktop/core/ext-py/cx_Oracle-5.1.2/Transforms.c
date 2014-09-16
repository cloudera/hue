//-----------------------------------------------------------------------------
// Transforms.c
//   Provides methods for transforming Oracle data to Python objects or for
// setting Oracle data from Python objects.
//-----------------------------------------------------------------------------

static udt_VariableType vt_Date;

//-----------------------------------------------------------------------------
// OracleDateToPythonDate()
//   Return a Python date object given an Oracle date.
//-----------------------------------------------------------------------------
static PyObject *OracleDateToPythonDate(
    udt_VariableType *varType,          // variable type
    OCIDate* value)                     // value to convert
{
    ub1 hour, minute, second, month, day;
    sb2 year;

    OCIDateGetDate(value, &year, &month, &day);
    OCIDateGetTime(value, &hour, &minute, &second);

    if (varType == &vt_Date)
        return PyDate_FromDate(year, month, day);
    return PyDateTime_FromDateAndTime(year, month, day, hour, minute, second,
            0);
}


//-----------------------------------------------------------------------------
// OracleIntervalToPythonDelta()
//   Return a Python delta object given an Oracle interval.
//-----------------------------------------------------------------------------
static PyObject *OracleIntervalToPythonDelta(
    udt_Environment *environment,       // environment
    OCIInterval *value)                 // value to convert
{
    sb4 days, hours, minutes, seconds, fseconds;
    sword status;

    status = OCIIntervalGetDaySecond(environment->handle,
            environment->errorHandle, &days, &hours, &minutes, &seconds,
            &fseconds, value);
    if (Environment_CheckForError(environment, status,
            "OracleIntervalToPythonDelta()") < 0)
        return NULL;
    seconds = hours * 60 * 60 + minutes * 60 + seconds;
    return PyDelta_FromDSU(days, seconds, fseconds / 1000);
}


//-----------------------------------------------------------------------------
// OracleTimestampToPythonDate()
//   Return a Python date object given an Oracle timestamp.
//-----------------------------------------------------------------------------
static PyObject *OracleTimestampToPythonDate(
    udt_Environment *environment,       // environment
    OCIDateTime* value)                 // value to convert
{
    ub1 hour, minute, second, month, day;
    sword status;
    ub4 fsecond;
    sb2 year;

    status = OCIDateTimeGetDate(environment->handle, environment->errorHandle,
            value, &year, &month, &day);
    if (Environment_CheckForError(environment, status,
            "OracleTimestampToPythonDate(): date portion") < 0)
        return NULL;
    status = OCIDateTimeGetTime(environment->handle, environment->errorHandle,
            value, &hour, &minute, &second, &fsecond);
    if (Environment_CheckForError(environment, status,
            "OracleTimestampToPythonDate(): time portion") < 0)
        return NULL;
    return PyDateTime_FromDateAndTime(year, month, day, hour, minute, second,
            fsecond / 1000);
}


//-----------------------------------------------------------------------------
// OracleNumberToPythonFloat()
//   Return a Python date object given an Oracle date.
//-----------------------------------------------------------------------------
static PyObject *OracleNumberToPythonFloat(
    udt_Environment *environment,       // environment
    OCINumber* value)                   // value to convert
{
    double doubleValue;
    sword status;

    status = OCINumberToReal(environment->errorHandle,
            value, sizeof(double), (dvoid*) &doubleValue);
    if (Environment_CheckForError(environment, status,
            "OracleNumberToPythonFloat()") < 0)
        return NULL;
    return PyFloat_FromDouble(doubleValue);
}

