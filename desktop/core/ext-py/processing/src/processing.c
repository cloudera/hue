/*
 * Extension module used by `processing` package
 *
 * processing.c
 *
 * Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
 */

#include "processing.h"

PyObject *create_win32_namespace(void);

PyObject *dumpsFunction, *loadsFunction, *protocol;
PyObject *ProcessError, *BufferTooShort;

/*
 * Function which raises exceptions based on error codes
 */

PyObject *
SetException(PyObject *Type, int num)
{
    switch (num) {
#ifdef MS_WINDOWS
    case STANDARD_ERROR: 
        if (Type == NULL)
            Type = PyExc_WindowsError;
        PyErr_SetExcFromWindowsErr(Type, 0);
        break;
    case WSA_ERROR:
        if (Type == NULL)
            Type = PyExc_WindowsError;
        PyErr_SetExcFromWindowsErr(Type, WSAGetLastError());
        break;
#else /* !MS_WINDOWS */
    case STANDARD_ERROR: 
        if (Type == NULL)
            Type = PyExc_OSError;
        PyErr_SetFromErrno(Type);
        break;
#endif /* !MS_WINDOWS */
    case MEMORY_ERROR:
        PyErr_NoMemory();
        break;
    case END_OF_FILE:
        PyErr_SetNone(PyExc_EOFError);
        break;
    case EARLY_END_OF_FILE:
        PyErr_SetString(PyExc_IOError, "got end of file during message");
        break;
    case BAD_MESSAGE_LENGTH:
        PyErr_SetString(PyExc_IOError, "bad message length");
        break;
    case EXCEPTION_HAS_BEEN_SET:
        return NULL;
    default:
        PyErr_Format(PyExc_RuntimeError, "unkown number: %d", num);
    }
    return NULL;
}


/*
 * Windows only
 */

#ifdef MS_WINDOWS

/* On Windows we set an event to signal Ctrl-C; compare with timemodule.c */

HANDLE hInterruptEvent = NULL;
long main_thread = 0;

static BOOL WINAPI
ProcessingCtrlHandler(DWORD dwCtrlType)
{
    SetEvent(hInterruptEvent);
    return FALSE;
}

/* Duplicate a handle -- also works on windows sockets */

HANDLE 
duplicate_handle(HANDLE h)
{
    HANDLE dup_h;
    BOOL success = DuplicateHandle(
        GetCurrentProcess(), h, GetCurrentProcess(), 
        &dup_h, 0, FALSE, DUPLICATE_SAME_ACCESS
        );
    return success ? dup_h : INVALID_HANDLE_VALUE;
}

/* On Windows we provide alternative to socket.fromfd() */

#if defined(MS_WINDOWS) && PY_VERSION_HEX < 0x02060000

typedef struct {
        PyObject_HEAD
        SOCKET sock_fd;
        int sock_family;
        int sock_type;
        int sock_proto;
        PyObject *(*errorhandler)(void);
        double sock_timeout;
} PySocketSockObject;

PyObject *
processing_changefd(PyObject *self, PyObject *args)
{
    PySocketSockObject *s;
    int family, type, proto=0;
    SOCKET fd, newfd;

    if (!PyArg_ParseTuple(args, "Oiii|i", &s, &fd, &family, &type, &proto))
        return NULL;

    /* Note INVALID_HANDLE_VALUE == INVALID_SOCKET == -1 (modulo casting) */
    newfd = (SOCKET)duplicate_handle((HANDLE)fd);
    if (newfd == INVALID_SOCKET) {
        PyErr_SetString(PyExc_OSError, "failed to duplicate socket handle");
        return NULL;
    }
    
    if (s->sock_fd != INVALID_SOCKET) {
        Py_BEGIN_ALLOW_THREADS
        CloseHandle((HANDLE)s->sock_fd);
        Py_END_ALLOW_THREADS
    }

    s->sock_fd = newfd;
    s->sock_family = family;
    s->sock_type = type;
    s->sock_proto = proto;
    
    Py_RETURN_NONE;
}

#endif /* defined(MS_WINDOWS) && PY_VERSION_HEX < 0x02060000 */

/*
 * Unix only
 */

#else /* !MS_WINDOWS */

#if HAVE_FD_TRANSFER

/* Functions for transferring file descriptors between processes.
   Reimplements some of the functionality of the `fdcred`
   module at `http://www.mca-ltd.com/resources/fdcred_1.tgz`. */

static PyObject *
processing_sendfd(PyObject *self, PyObject *args)
{
    int conn, fd, res;
    char dummy_char;
    char buf[CMSG_SPACE(sizeof(int))];
    struct msghdr msg = {0};
    struct iovec dummy_iov;
    struct cmsghdr *cmsg;

    if (!PyArg_ParseTuple(args, "ii", &conn, &fd))
        return NULL;
    
    dummy_iov.iov_base = &dummy_char;
    dummy_iov.iov_len = 1;
    msg.msg_control = buf;
    msg.msg_controllen = sizeof(buf);
    msg.msg_iov = &dummy_iov;
    msg.msg_iovlen = 1;
    cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    msg.msg_controllen = cmsg->cmsg_len;
    *(int*)CMSG_DATA(cmsg) = fd;

    Py_BEGIN_ALLOW_THREADS
    res = sendmsg(conn, &msg, 0);
    Py_END_ALLOW_THREADS

    if (res < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    Py_RETURN_NONE;
}

static PyObject *
processing_recvfd(PyObject *self, PyObject *args)
{
    int conn, fd, res;
    char dummy_char;
    char buf[CMSG_SPACE(sizeof(int))];
    struct msghdr msg = {0};
    struct iovec dummy_iov;
    struct cmsghdr *cmsg;
    
    if (!PyArg_ParseTuple(args, "i", &conn))
        return NULL;

    dummy_iov.iov_base = &dummy_char;
    dummy_iov.iov_len = 1;
    msg.msg_control = buf;
    msg.msg_controllen = sizeof(buf);
    msg.msg_iov = &dummy_iov;
    msg.msg_iovlen = 1;
    cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    msg.msg_controllen = cmsg->cmsg_len;

    Py_BEGIN_ALLOW_THREADS
    res = recvmsg(conn, &msg, 0);
    Py_END_ALLOW_THREADS

    if (res < 0)
        return PyErr_SetFromErrno(PyExc_OSError);

    fd = *(int*)CMSG_DATA(cmsg);
    return Py_BuildValue("i", fd);
}

#endif /* HAVE_FD_TRANSFER */

#endif /* !MS_WINDOWS */


/*
 * All platforms
 */

static PyObject*
processing_rwbuffer(PyObject *self, PyObject *args)
{
    PyObject *obj;
    Py_ssize_t offset = 0, size = Py_END_OF_BUFFER;
    
    if (!PyArg_ParseTuple(args, "O|" F_PY_SSIZE_T F_PY_SSIZE_T, 
                          &obj, &offset, &size))
        return NULL;

    return PyBuffer_FromReadWriteObject(obj, offset, size);
}

static PyObject*
processing_address_of_buffer(PyObject *self, PyObject *obj)
{
    void *buffer;
    Py_ssize_t buffer_len;
    
    if (PyObject_AsWriteBuffer(obj, &buffer, &buffer_len) < 0)
        return NULL;

    return Py_BuildValue("N" F_PY_SSIZE_T, 
                         PyLong_FromVoidPtr(buffer), buffer_len);
}


/*
 * Function table
 */

static PyMethodDef module_methods[] = {
    {"readWriteBuffer", processing_rwbuffer, METH_VARARGS, 
     "readWriteBuffer(obj [, offset[, size]]) -> buffer\n"
     "Create a writable view of obj assuming obj supports buffer inteface"},
    {"addressOfBuffer", processing_address_of_buffer, METH_O, 
     "addressOfBuffer(obj) -> integer\n" 
     "Return address of obj assuming obj supports buffer inteface"},
#if HAVE_FD_TRANSFER
    {"sendFd", processing_sendfd, METH_VARARGS, 
     "sendFd(sockfd, fd) -> None\n"
     "Send file descriptor given by fd over the unix domain socket\n"
     "whose file decriptor is sockfd"},
    {"recvFd", processing_recvfd, METH_VARARGS,
     "recvFd(sockfd) -> fd\n"
     "Receive a file descriptor over a unix domain socket\n"
     "whose file decriptor is sockfd"},
#endif
#if defined(MS_WINDOWS) && PY_VERSION_HEX < 0x02060000
    {"changeFd", (PyCFunction)processing_changefd, METH_VARARGS, 
     "changeFd(fd, family, type [, proto]) -> None\n"
     "Replace the file descriptor etc of an existing socket object\n"
     "the old fd is closed, and replaced with a duplicate of fd"},
#endif
    {NULL}
};


/*
 * Initialize
 */

PyMODINIT_FUNC
init_processing(void)
{
    PyObject *module, *temp;
    
    /* Initialize module */
    module = Py_InitModule("_processing", module_methods);
    if (!module)
        return;

    /* Get copy of objects from cPickle */
    temp = PyImport_ImportModule("cPickle");
    if (!temp)
        return;
    dumpsFunction = PyObject_GetAttrString(temp, "dumps");
    loadsFunction = PyObject_GetAttrString(temp, "loads");
    protocol = PyObject_GetAttrString(temp, "HIGHEST_PROTOCOL");
    Py_XDECREF(temp);

    /* Add ProcessError to module */
    ProcessError = PyErr_NewException("_processing.ProcessError", NULL, NULL);
    if (!ProcessError)
        return;
    Py_INCREF(ProcessError);
    PyModule_AddObject(module, "ProcessError", ProcessError);

    /* Add BufferTooShort to module */
    BufferTooShort = PyErr_NewException("_processing.BufferTooShort", 
                                        ProcessError, NULL);
    if (!BufferTooShort)
        return;
    Py_INCREF(BufferTooShort);
    PyModule_AddObject(module, "BufferTooShort", BufferTooShort);

    /* Add connection type to module */
    if (PyType_Ready(&ConnectionType) < 0)
        return;
    Py_INCREF(&ConnectionType);
    PyModule_AddObject(module, "Connection", (PyObject*)&ConnectionType);

#if defined(MS_WINDOWS) || HAVE_SEM_OPEN
    /* Add SemLock type to module */
    if (PyType_Ready(&SemLockType) < 0)
        return;
    Py_INCREF(&SemLockType);
    PyModule_AddObject(module, "SemLock", (PyObject*)&SemLockType);   
#endif

#ifdef MS_WINDOWS
    /* Add PipeConnection to module */
    if (PyType_Ready(&PipeConnectionType) < 0)
        return;
    Py_INCREF(&PipeConnectionType);
    PyModule_AddObject(module,"PipeConnection",(PyObject*)&PipeConnectionType);

    /* Initialize win32 class and add to processing */
    temp = create_win32_namespace();
    if (!temp)
        return;
    PyModule_AddObject(module, "win32", temp);

    /* Initialize the event handle used to signal Ctrl-C */
    main_thread = GetCurrentThreadId();  /* hope not imported by subthread */
    hInterruptEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    if (!hInterruptEvent) {
        PyErr_SetFromWindowsErr(0);
        return;
    }
    if (!SetConsoleCtrlHandler(ProcessingCtrlHandler, TRUE)) {
        PyErr_SetFromWindowsErr(0);
        return;
    }
    PyModule_AddObject(module, "_hInterruptEvent", 
                       Py_BuildValue(F_HANDLE, hInterruptEvent));
    PyModule_AddObject(module, "_main_thread_ident", 
                       Py_BuildValue(F_HANDLE, main_thread));

#endif

    /* Add configuration macros */
#ifdef HAVE_SEM_OPEN
    PyModule_AddObject(module, "HAVE_SEM_OPEN", 
                       Py_BuildValue("i", HAVE_SEM_OPEN));
#endif
#ifdef HAVE_SEM_TIMEDWAIT
    PyModule_AddObject(module, "HAVE_SEM_TIMEDWAIT", 
                       Py_BuildValue("i", HAVE_SEM_TIMEDWAIT));
#endif
#ifdef HAVE_FD_TRANSFER
    PyModule_AddObject(module, "HAVE_FD_TRANSFER", 
                       Py_BuildValue("i", HAVE_FD_TRANSFER));
#endif
#ifdef HAVE_BROKEN_SEM_GETVALUE
    PyModule_AddObject(module, "HAVE_BROKEN_SEM_GETVALUE", 
                       Py_BuildValue("i", HAVE_BROKEN_SEM_GETVALUE));
#endif
#ifdef HAVE_BROKEN_SEM_UNLINK
    PyModule_AddObject(module, "HAVE_BROKEN_SEM_UNLINK", 
                       Py_BuildValue("i", HAVE_BROKEN_SEM_UNLINK));
#endif
}
