/*
 * Win32 functions used by `processing` package
 *
 * win_functions.c
 *
 * Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
 */

#include "processing.h"


#define WIN32_FUNCTION(func) \
    {#func, (PyCFunction)win32_ ## func, METH_VARARGS | METH_STATIC, ""}

#define WIN32_CONSTANT(fmt, con) \
    PyDict_SetItemString(Win32Type.tp_dict, #con, Py_BuildValue(fmt, con))


static PyObject *
win32_CloseHandle(PyObject *self, PyObject *args)
{
    HANDLE hObject;
    BOOL success;
    
    if (!PyArg_ParseTuple(args, F_HANDLE, &hObject))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = CloseHandle(hObject); 
    Py_END_ALLOW_THREADS

    if (!success)
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_ConnectNamedPipe(PyObject *self, PyObject *args)
{
    HANDLE hNamedPipe;
    LPOVERLAPPED lpOverlapped;
    BOOL success;

    if (!PyArg_ParseTuple(args, F_HANDLE F_POINTER, 
                          &hNamedPipe, &lpOverlapped))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = ConnectNamedPipe(hNamedPipe, lpOverlapped);
    Py_END_ALLOW_THREADS

    if (!success)
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_CreateFile(PyObject *self, PyObject *args)
{
    LPCTSTR lpFileName;
    DWORD dwDesiredAccess;
    DWORD dwShareMode;
    LPSECURITY_ATTRIBUTES lpSecurityAttributes;
    DWORD dwCreationDisposition;
    DWORD dwFlagsAndAttributes;
    HANDLE hTemplateFile;
    HANDLE handle;

    if (!PyArg_ParseTuple(args, "s" F_DWORD F_DWORD F_POINTER 
                          F_DWORD F_DWORD F_HANDLE,
                          &lpFileName, &dwDesiredAccess, &dwShareMode, 
                          &lpSecurityAttributes, &dwCreationDisposition, 
                          &dwFlagsAndAttributes, &hTemplateFile))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    handle = CreateFile(lpFileName, dwDesiredAccess, dwShareMode, 
                        lpSecurityAttributes, dwCreationDisposition, 
                        dwFlagsAndAttributes, hTemplateFile);
    Py_END_ALLOW_THREADS

    if (handle == INVALID_HANDLE_VALUE)
        return PyErr_SetFromWindowsErr(0);
    
    return Py_BuildValue(F_HANDLE, handle);
}

static PyObject *
win32_CreateNamedPipe(PyObject *self, PyObject *args)
{
    LPCTSTR lpName;
    DWORD dwOpenMode;
    DWORD dwPipeMode;
    DWORD nMaxInstances;
    DWORD nOutBufferSize;
    DWORD nInBufferSize;
    DWORD nDefaultTimeOut;
    LPSECURITY_ATTRIBUTES lpSecurityAttributes;
    HANDLE handle;

    if (!PyArg_ParseTuple(args, "s" F_DWORD F_DWORD F_DWORD 
                          F_DWORD F_DWORD F_DWORD F_POINTER,
                          &lpName, &dwOpenMode, &dwPipeMode, &nMaxInstances, 
                          &nOutBufferSize, &nInBufferSize, &nDefaultTimeOut,
                          &lpSecurityAttributes))
        return NULL;
    
    Py_BEGIN_ALLOW_THREADS
    handle = CreateNamedPipe(lpName, dwOpenMode, dwPipeMode, nMaxInstances, 
                             nOutBufferSize, nInBufferSize, nDefaultTimeOut,
                             lpSecurityAttributes);
    Py_END_ALLOW_THREADS
        
    if (handle == INVALID_HANDLE_VALUE)
        return PyErr_SetFromWindowsErr(0);

    return Py_BuildValue(F_HANDLE, handle);
}

static PyObject *
win32_ExitProcess(PyObject *self, PyObject *args)
{
    UINT uExitCode;

    if (!PyArg_ParseTuple(args, "I", &uExitCode))
        return NULL;

    ExitProcess(uExitCode);

    return NULL;
}

static PyObject *
win32_GenerateConsoleCtrlEvent(PyObject *self, PyObject *args)
{
    DWORD dwCtrlEvent;
    DWORD dwProcessGroupId;

    if (!PyArg_ParseTuple(args, F_DWORD F_DWORD, 
                          &dwCtrlEvent, &dwProcessGroupId))
        return NULL;

    if (!GenerateConsoleCtrlEvent(dwCtrlEvent, dwProcessGroupId))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_GetExitCodeProcess(PyObject *self, PyObject *args)
{
    HANDLE hProcess;
    DWORD dwExitCode;

    if (!PyArg_ParseTuple(args, F_HANDLE, &hProcess))
        return NULL;
    
    if (!GetExitCodeProcess(hProcess, &dwExitCode))
        return PyErr_SetFromWindowsErr(0);

    return Py_BuildValue(F_DWORD, dwExitCode);
}

static PyObject *
win32_GetHandleInformation(PyObject *self, PyObject *args)
{
    HANDLE hObject;
    DWORD dwFlags;

    if (!PyArg_ParseTuple(args, F_HANDLE, &hObject))
        return NULL;
    
    if (!GetHandleInformation(hObject, &dwFlags))
        return PyErr_SetFromWindowsErr(0);

    return Py_BuildValue(F_DWORD, dwFlags);
}

static PyObject *
win32_GetLastError(PyObject *self, PyObject *args)
{
    return Py_BuildValue(F_DWORD, GetLastError());
}

static PyObject *
win32_OpenProcess(PyObject *self, PyObject *args)
{
    DWORD dwDesiredAccess;
    BOOL bInheritHandle;
    DWORD dwProcessId;
    HANDLE handle;

    if (!PyArg_ParseTuple(args, F_DWORD "i" F_DWORD, 
                          &dwDesiredAccess, &bInheritHandle, &dwProcessId))
        return NULL;
    
    handle = OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId);    
    if (handle == NULL)
        return PyErr_SetFromWindowsErr(0);
    
    return Py_BuildValue(F_HANDLE, handle);
}

static PyObject *
win32_ResetEvent(PyObject *self, PyObject *args)
{
    HANDLE hEvent;
    BOOL success;

    if (!PyArg_ParseTuple(args, F_HANDLE, &hEvent))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = ResetEvent(hEvent);
    Py_END_ALLOW_THREADS

    if (!success)
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_SetConsoleCtrlHandler(PyObject *self, PyObject *args)
{
    PHANDLER_ROUTINE HandlerRoutine;
    BOOL Add;

    if (!PyArg_ParseTuple(args, F_POINTER "i", &HandlerRoutine, &Add))
        return NULL;
    
    if (!SetConsoleCtrlHandler(HandlerRoutine, Add))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_SetHandleInformation(PyObject *self, PyObject *args)
{
    HANDLE hObject;
    DWORD dwMask;
    DWORD dwFlags;

    if (!PyArg_ParseTuple(args, F_HANDLE F_DWORD F_DWORD, 
                          &hObject, &dwMask, &dwFlags))
        return NULL;
    
    if (!SetHandleInformation(hObject, dwMask, dwFlags))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_SetNamedPipeHandleState(PyObject *self, PyObject *args)
{
    HANDLE hNamedPipe;
    PyObject *oArgs[3];
    DWORD dwArgs[3], *pArgs[3] = {NULL, NULL, NULL};
    int i;

    if (!PyArg_ParseTuple(args, F_HANDLE "OOO", 
                          &hNamedPipe, &oArgs[0], &oArgs[1], &oArgs[2]))
        return NULL;

    PyErr_Clear();

    for (i = 0 ; i < 3 ; i++) {
        if (oArgs[i] != Py_None) {
            dwArgs[i] = PyInt_AsUnsignedLongMask(oArgs[i]);
            if (PyErr_Occurred())
                return NULL;
            pArgs[i] = &dwArgs[i];
        }
    }

    if (!SetNamedPipeHandleState(hNamedPipe, pArgs[0], pArgs[1], pArgs[2]))
        return PyErr_SetFromWindowsErr(0);
    
    Py_RETURN_NONE;
}

static PyObject *
win32_TerminateProcess(PyObject *self, PyObject *args)
{
    HANDLE hProcess;
    UINT uExitCode;

    if (!PyArg_ParseTuple(args, F_HANDLE "I", &hProcess, &uExitCode))
        return NULL;
    
    if (!TerminateProcess(hProcess, uExitCode))
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyObject *
win32_WaitForMultipleObjects(PyObject *self, PyObject *args)
{
    DWORD nCount;
    PyObject *oHandles;
    BOOL bWaitAll;
    DWORD dwMilliseconds;

    DWORD res, i;
    HANDLE *handle_array = NULL;
    PyObject *obj;

    if (!PyArg_ParseTuple(args, F_DWORD "Oi" F_DWORD, 
                          &nCount, &oHandles, &bWaitAll, &dwMilliseconds))
        return NULL;
    
    if (!PySequence_Check(oHandles)) {
        PyErr_SetString(PyExc_TypeError, "expected a sequence");
        return NULL;
    }
    
    if (nCount != (DWORD)PySequence_Length(oHandles)) {
        PyErr_SetString(PyExc_ValueError, "sequence has unexpected length");
        return NULL;
    }

    handle_array = PyMem_Malloc(nCount * sizeof(HANDLE));
    if (!handle_array)
        return PyErr_NoMemory();

    PyErr_Clear();

    for (i = 0 ; i < nCount ; i++) {
        obj = PySequence_GetItem(oHandles, (Py_ssize_t)i);
        handle_array[i] = (HANDLE)PyLong_AsVoidPtr(obj);
        if (PyErr_Occurred()) {
            PyMem_Free(handle_array);
            return NULL;
        }
    }

    Py_BEGIN_ALLOW_THREADS
    res = WaitForMultipleObjects(nCount, handle_array, 
                                 bWaitAll, dwMilliseconds);
    Py_END_ALLOW_THREADS

    PyMem_Free(handle_array);

    if (res == WAIT_FAILED)
        return PyErr_SetFromWindowsErr(0);

    return Py_BuildValue(F_DWORD, res);
}

static PyObject *
win32_WaitNamedPipe(PyObject *self, PyObject *args)
{
    LPCTSTR lpNamedPipeName;
    DWORD nTimeOut;
    BOOL success;

    if (!PyArg_ParseTuple(args, "s" F_DWORD, &lpNamedPipeName, &nTimeOut))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    success = WaitNamedPipe(lpNamedPipeName, nTimeOut);
    Py_END_ALLOW_THREADS

    if (!success)
        return PyErr_SetFromWindowsErr(0);

    Py_RETURN_NONE;
}

static PyMethodDef win32_methods[] = {
    WIN32_FUNCTION(CloseHandle),
    WIN32_FUNCTION(ConnectNamedPipe),
    WIN32_FUNCTION(CreateFile),
    WIN32_FUNCTION(CreateNamedPipe),
    WIN32_FUNCTION(ExitProcess),
    WIN32_FUNCTION(GenerateConsoleCtrlEvent),
    WIN32_FUNCTION(GetExitCodeProcess),
    WIN32_FUNCTION(GetHandleInformation),
    WIN32_FUNCTION(GetLastError),
    WIN32_FUNCTION(OpenProcess),
    WIN32_FUNCTION(ResetEvent),
    WIN32_FUNCTION(SetConsoleCtrlHandler),
    WIN32_FUNCTION(SetHandleInformation),
    WIN32_FUNCTION(SetNamedPipeHandleState),
    WIN32_FUNCTION(TerminateProcess),
    WIN32_FUNCTION(WaitForMultipleObjects),
    WIN32_FUNCTION(WaitNamedPipe),
    {NULL}
};


PyTypeObject Win32Type = {
    PyObject_HEAD_INIT(NULL)
};


PyObject *
create_win32_namespace(void)
{
    Win32Type.tp_name = "_processing.win32";
    Win32Type.tp_methods = win32_methods;

    if (PyType_Ready(&Win32Type) < 0)
        return NULL;
    Py_INCREF(&Win32Type);

    WIN32_CONSTANT(F_DWORD, ERROR_ALREADY_EXISTS);
    WIN32_CONSTANT(F_DWORD, ERROR_PIPE_BUSY);
    WIN32_CONSTANT(F_DWORD, ERROR_PIPE_CONNECTED);
    WIN32_CONSTANT(F_DWORD, ERROR_SEM_TIMEOUT);
    WIN32_CONSTANT(F_DWORD, GENERIC_READ);
    WIN32_CONSTANT(F_DWORD, GENERIC_WRITE);
    WIN32_CONSTANT(F_DWORD, HANDLE_FLAG_INHERIT);
    WIN32_CONSTANT(F_DWORD, INFINITE);
    WIN32_CONSTANT(F_DWORD, NMPWAIT_WAIT_FOREVER);
    WIN32_CONSTANT(F_DWORD, OPEN_EXISTING);
    WIN32_CONSTANT(F_DWORD, PIPE_ACCESS_DUPLEX);
    WIN32_CONSTANT(F_DWORD, PIPE_ACCESS_INBOUND);
    WIN32_CONSTANT(F_DWORD, PIPE_READMODE_MESSAGE);
    WIN32_CONSTANT(F_DWORD, PIPE_TYPE_MESSAGE);
    WIN32_CONSTANT(F_DWORD, PIPE_UNLIMITED_INSTANCES);
    WIN32_CONSTANT(F_DWORD, PIPE_WAIT);
    WIN32_CONSTANT(F_DWORD, PROCESS_ALL_ACCESS);
    WIN32_CONSTANT(F_DWORD, WAIT_OBJECT_0);
    WIN32_CONSTANT(F_DWORD, WAIT_TIMEOUT);
    
    WIN32_CONSTANT(F_POINTER, NULL);

    return (PyObject*)&Win32Type;
}
