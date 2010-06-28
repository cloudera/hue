/*
 * A type which wraps a semaphore
 *
 * semaphore.c
 *
 * Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
 */

#include "processing.h"

enum { RECURSIVE_MUTEX, SEMAPHORE, BOUNDED_SEMAPHORE };

typedef struct {
    PyObject_HEAD
    SEM_HANDLE handle;
    long last_tid;
    int count;
    int maxvalue;
    int kind;
} SemLock;

#define ISMINE(o) (o->count > 0 && PyThread_get_thread_ident() == o->last_tid)


#ifdef MS_WINDOWS

/*
 * Windows definitions
 */

static SECURITY_ATTRIBUTES sa = { sizeof(SECURITY_ATTRIBUTES), NULL, TRUE };

#define SEM_FAILED NULL

#define SEM_CLEAR_ERROR() SetLastError(0)
#define SEM_GET_LAST_ERROR() GetLastError()
#define SEM_CREATE(name, val, max) CreateSemaphore(&sa, val, max, NULL)
#define SEM_CLOSE(sem) (CloseHandle(sem) ? 0 : -1)
#define SEM_GETVALUE(sem, pval) _SemLock_GetSemaphoreValue(sem, pval)
#define SEM_UNLINK(name) 0

static int
_SemLock_GetSemaphoreValue(HANDLE handle, long *value)
{
    long previous;

    switch (WaitForSingleObject(handle, 0)) {
    case WAIT_OBJECT_0:
        if (!ReleaseSemaphore(handle, 1, &previous))
            return STANDARD_ERROR;
        *value = previous + 1;
        return 0;
    case WAIT_TIMEOUT:
        *value = 0;
        return 0;
    default:
        return STANDARD_ERROR;
    }
}

static PyObject *
SemLock_acquire(SemLock *self, PyObject *args, PyObject *kwds)
{
    int blocking = 1;
    double timeout;
    PyObject *timeout_obj = Py_None;
    DWORD res, dwTimeout;
    
    static char *kwlist[] = {"block", "timeout", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|iO", kwlist,
                                     &blocking, &timeout_obj))
        return NULL;

    if (self->kind == RECURSIVE_MUTEX && ISMINE(self)) {
        ++self->count;
        Py_RETURN_TRUE;
    }

    /* work out timeout */
    if (!blocking) {
        dwTimeout = 0;
    } else if (timeout_obj == Py_None) {
        dwTimeout = INFINITE;
    } else {
        timeout = PyFloat_AsDouble(timeout_obj);
        if (PyErr_Occurred())
            return NULL;
        timeout *= 1000.0;      /* convert to millisecs */
        if (timeout < 0.0) {
            timeout = 0.0;
        } else if (timeout >= ((double)INFINITE - 0.5)) {
            PyErr_SetString(PyExc_OverflowError, "timeout is too large");
            return NULL;
        }
        dwTimeout = (DWORD)(timeout + 0.5);
    }
    
    /* do the wait */
    if (dwTimeout == 0) {
        res = WaitForSingleObject(self->handle, 0);
    } else if (main_thread == GetCurrentThreadId()) {
        res = WaitForSingleObject(self->handle, 0);
        if (res == WAIT_TIMEOUT) {
            HANDLE handles[2] = {self->handle, hInterruptEvent};
            ResetEvent(hInterruptEvent);
            Py_BEGIN_ALLOW_THREADS
            res = WaitForMultipleObjects(2, handles, FALSE, dwTimeout);
            Py_END_ALLOW_THREADS
        }
    } else {
        Py_BEGIN_ALLOW_THREADS
        res = WaitForSingleObject(self->handle, dwTimeout);
        Py_END_ALLOW_THREADS
    }
    
    /* handle result */
    switch (res) {
    case WAIT_TIMEOUT:
        Py_RETURN_FALSE;
    case WAIT_OBJECT_0:
        self->last_tid = GetCurrentThreadId();
        ++self->count;
        Py_RETURN_TRUE;
    case (WAIT_OBJECT_0 + 1):  /* we got SIGINT; do like in timemodule.c */
        Sleep(1);
        errno = EINTR;
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    case WAIT_FAILED:
        return PyErr_SetFromWindowsErr(0);
    default:
        PyErr_SetString(PyExc_RuntimeError, "WaitForSingleObject() or "
                        "WaitForMultipleObjects() gave unrecognized value");
        return NULL;
    }
}

static PyObject *
SemLock_release(SemLock *self, PyObject *args)
{
    if (self->kind == RECURSIVE_MUTEX) {
        if (!ISMINE(self)) {
            PyErr_SetString(PyExc_AssertionError, "attempt to release "
                            "recursive lock not owned by thread");
            return NULL;
        }
        if (self->count > 1) {
            --self->count;
            Py_RETURN_NONE;
        }
        assert(self->count == 1);
    }

    if (!ReleaseSemaphore(self->handle, 1, NULL)) {
        if (GetLastError() == ERROR_TOO_MANY_POSTS) {
            PyErr_SetString(PyExc_ValueError,
                            "semaphore or lock released too many times");
            return NULL;
        } else {
            return PyErr_SetFromWindowsErr(0);
        }
    }
    
    --self->count;
    Py_RETURN_NONE;
}

#else /* !MS_WINDOWS */

/*
 * Unix definitions
 */

#define SEM_CLEAR_ERROR()
#define SEM_GET_LAST_ERROR() 0
#define SEM_CREATE(name, val, max) sem_open(name, O_CREAT | O_EXCL, 0600, val)
#define SEM_CLOSE(sem) sem_close(sem)
#define SEM_GETVALUE(sem, pval) sem_getvalue(sem, pval)
#define SEM_UNLINK(name) sem_unlink(name)

#if HAVE_BROKEN_SEM_UNLINK
#  define sem_unlink(name) 0
#endif

#if !HAVE_SEM_TIMEDWAIT
#  define sem_timedwait(sem,deadline) sem_timedwait_save(sem,deadline,_save)

int
sem_timedwait_save(sem_t *sem, struct timespec *deadline, PyThreadState *_save)
{
    int res;
    unsigned long delay, difference;
    struct timeval now, tvdeadline, tvdelay;

    errno = 0;
    tvdeadline.tv_sec = deadline->tv_sec;
    tvdeadline.tv_usec = deadline->tv_nsec / 1000;

    for (delay = 0 ; ; delay += 1000) {
        /* poll */
        if (sem_trywait(sem) == 0)
            return 0;
        else if (errno != EAGAIN)
            return STANDARD_ERROR;
            
        /* get current time */
        if (gettimeofday(&now, NULL) < 0)
            return STANDARD_ERROR;
            
        /* check for timeout */
        if (tvdeadline.tv_sec < now.tv_sec || 
            (tvdeadline.tv_sec == now.tv_sec && 
             tvdeadline.tv_usec <= now.tv_usec)) {
            errno = ETIMEDOUT;
            return STANDARD_ERROR;
        }
        
        /* calculate how much time is left */
        difference = (tvdeadline.tv_sec - now.tv_sec) * 1000000 + 
            (tvdeadline.tv_usec - now.tv_usec);
            
        /* check delay not too long -- maximum is 20 msecs */
        if (delay > 20000)
            delay = 20000;
        if (delay > difference)
            delay = difference;
        
        /* sleep */
        tvdelay.tv_sec = delay / 1000000;
        tvdelay.tv_usec = delay % 1000000;
        if (select(0, NULL, NULL, NULL, &tvdelay) < 0)
            return STANDARD_ERROR;

        /* check for signals */
        Py_BLOCK_THREADS 
        res = PyErr_CheckSignals();
        Py_UNBLOCK_THREADS

        if (res) {
            errno = EINTR;
            return EXCEPTION_HAS_BEEN_SET;
        }
    }
}

#endif /* !HAVE_SEM_TIMEDWAIT */

static PyObject *
SemLock_acquire(SemLock *self, PyObject *args, PyObject *kwds)
{
    int blocking = 1, res;
    double timeout;
    PyObject *timeout_obj = Py_None;
    struct timespec deadline = {0};
    struct timeval now;
    long sec, nsec;
    
    static char *kwlist[] = {"block", "timeout", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|iO", kwlist,
                                     &blocking, &timeout_obj))
        return NULL;
        
    if (self->kind == RECURSIVE_MUTEX && ISMINE(self)) {
        ++self->count;
        Py_RETURN_TRUE;
    }
    
    if (timeout_obj != Py_None) {
        timeout = PyFloat_AsDouble(timeout_obj);
        if (PyErr_Occurred())
            return NULL;
        if (timeout < 0.0)
            timeout = 0.0;
            
        if (gettimeofday(&now, NULL) < 0) {
            PyErr_SetFromErrno(PyExc_OSError);
            return NULL;
        }
        sec = (long) timeout;
        nsec = (long) (1e9 * (timeout - sec) + 0.5);
        deadline.tv_sec = now.tv_sec + sec;
        deadline.tv_nsec = now.tv_usec * 1000 + nsec;
        deadline.tv_sec += (deadline.tv_nsec / 1000000000);
        deadline.tv_nsec %= 1000000000;
    }
    
    do {
        Py_BEGIN_ALLOW_THREADS
        if (blocking && timeout_obj == Py_None)
            res = sem_wait(self->handle);
        else if (!blocking)
            res = sem_trywait(self->handle);
        else
            res = sem_timedwait(self->handle, &deadline);
        Py_END_ALLOW_THREADS
        if (res == EXCEPTION_HAS_BEEN_SET)
            break;
    } while (res < 0 && errno == EINTR && !PyErr_CheckSignals());
    
    if (res < 0) {
        if (errno == EAGAIN || errno == ETIMEDOUT)
            Py_RETURN_FALSE;
        else if (errno == EINTR)
            return NULL;
        else
            return PyErr_SetFromErrno(PyExc_OSError);
    }
    
    ++self->count;
    self->last_tid = PyThread_get_thread_ident();
    
    Py_RETURN_TRUE;
}

static PyObject *
SemLock_release(SemLock *self, PyObject *args)
{
    switch (self->kind) {
    case RECURSIVE_MUTEX:
        if (!ISMINE(self)) {
            PyErr_SetString(PyExc_AssertionError, "attempt to release "
                            "recursive lock not owned by thread");
            return NULL;
        }
        if (self->count > 1) {
            --self->count;
            Py_RETURN_NONE;
        }
        assert(self->count == 1);
        break;
#if HAVE_BROKEN_SEM_GETVALUE
    case BOUNDED_SEMAPHORE:
        /* We will only check properly the Lock case (where maxvalue == 1) */
        if (self->maxvalue == 1) {
            /* make sure that already locked */
            if (sem_trywait(self->handle) < 0) {
                if (errno != EAGAIN)
                    return PyErr_SetFromErrno(PyExc_OSError);
                /* it is already locked as expected */
            } else {
                /* it was not locked -- so undo wait and raise error */
                if (sem_post(self->handle) < 0)
                    return PyErr_SetFromErrno(PyExc_OSError);
                PyErr_SetString(PyExc_ValueError, 
                                "semaphore or lock released too many times");
                return NULL;
            }
        }
#else
    case BOUNDED_SEMAPHORE:
        {
            int sval;

            /* This check is not an absolute guarantee that the semaphore
               does not rise above maxvalue. */
            if (sem_getvalue(self->handle, &sval) < 0) {
                return PyErr_SetFromErrno(PyExc_OSError);
            } else if (sval >= self->maxvalue) {
                PyErr_SetString(PyExc_ValueError, 
                                "semaphore or lock released too many times");
                return NULL;
            }
        }
#endif
    }
    
    if (sem_post(self->handle) < 0)
        return PyErr_SetFromErrno(PyExc_OSError);
    
    --self->count;
    Py_RETURN_NONE;
}

#endif /* !MS_WINDOWS */

/*
 * All platforms
 */

static PyObject *
_SemLock_create(PyTypeObject *type, SEM_HANDLE handle, int kind, int maxvalue)
{
    SemLock *self;

    self = (SemLock*)type->tp_alloc(type, 0);
    if (!self)
        return NULL;
    self->handle = handle;
    self->kind = kind;
    self->count = 0;
    self->last_tid = 0;
    self->maxvalue = maxvalue;
    return (PyObject*)self;
}

static PyObject *
SemLock_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    char buffer[256];
    SEM_HANDLE handle = SEM_FAILED;
    int kind, maxvalue, value;
    PyObject *result;
    static char *kwlist[] = {"kind", "value", NULL};
    static int counter = 0;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &kind, &value))
        return NULL;

    if (kind < RECURSIVE_MUTEX || kind > BOUNDED_SEMAPHORE) {
        PyErr_SetString(PyExc_ValueError, "unrecongnized blocker type");
        return NULL;
    }
    
    PyOS_snprintf(buffer, sizeof(buffer), "/pr%d-%d", getpid(), counter++);
    
    if (kind == BOUNDED_SEMAPHORE)
        maxvalue = value;
    else if (kind == RECURSIVE_MUTEX)
        maxvalue = 1;
    else 
        maxvalue = INT_MAX;

    SEM_CLEAR_ERROR();
    handle = SEM_CREATE(buffer, value, maxvalue);
    /* On Windows we should fail if GetLastError() == ERROR_ALREADY_EXISTS */
    if (handle == SEM_FAILED || SEM_GET_LAST_ERROR() != 0)
        goto failure;

    if (SEM_UNLINK(buffer) < 0)
        goto failure;

    result = _SemLock_create(type, handle, kind, maxvalue);
    if (!result)
        goto failure;

    return result;

 failure:
    if (handle != SEM_FAILED)
        SEM_CLOSE(handle);
    SetException(NULL, STANDARD_ERROR);
    return NULL;
}

static PyObject *
SemLock_rebuild(PyTypeObject *type, PyObject *args)
{
    SEM_HANDLE handle;
    int kind, maxvalue;

    if (!PyArg_ParseTuple(args, F_SEM_HANDLE "ii", &handle, &kind, &maxvalue))
        return NULL;

    return _SemLock_create(type, handle, kind, maxvalue);
}

static void
SemLock_dealloc(SemLock* self)
{
    if (self->handle != SEM_FAILED)
        SEM_CLOSE(self->handle);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
SemLock_count(SemLock *self)
{
    return PyInt_FromLong((long)self->count);
}

static PyObject *
SemLock_ismine(SemLock *self)
{
    /* only makes sense for a lock */
    return PyBool_FromLong(ISMINE(self));
}

static PyObject *
SemLock_getvalue(SemLock *self)
{
#if HAVE_BROKEN_SEM_GETVALUE
    PyErr_SetNone(PyExc_NotImplementedError);
    return NULL;
#else
    int sval;
    if (SEM_GETVALUE(self->handle, &sval) < 0)
        SetException(NULL, STANDARD_ERROR);
    return PyInt_FromLong((long)sval);
#endif
}

static PyObject *
SemLock_afterfork(SemLock *self)
{
    self->count = 0;
    Py_RETURN_NONE;
}

/*
 * Semaphore methods
 */

static PyMethodDef SemLock_methods[] = {
    {"acquire", (PyCFunction)SemLock_acquire, METH_KEYWORDS,
     "acquire the semaphore/lock"},
    {"release", (PyCFunction)SemLock_release, METH_NOARGS, 
     "release the semaphore/lock"},
    {"__enter__", (PyCFunction)SemLock_acquire, METH_KEYWORDS, 
     "enter the semaphore/lock"},
    {"__exit__", (PyCFunction)SemLock_release, METH_VARARGS, 
     "exit the semaphore/lock"},
    {"_count", (PyCFunction)SemLock_count, METH_NOARGS, 
     "number of `acquire()`s minus number of `release()`s for this process"},
    {"_isMine", (PyCFunction)SemLock_ismine, METH_NOARGS, 
     "whether the lock is owned by this thread"},
    {"_getValue", (PyCFunction)SemLock_getvalue, METH_NOARGS, 
     "get the value of the semaphore"}, 
    {"_rebuild", (PyCFunction)SemLock_rebuild, METH_VARARGS | METH_CLASS, 
     ""}, 
    {"_afterFork", (PyCFunction)SemLock_afterfork, METH_NOARGS,
     "rezero the net acquisition count after fork()"},
    {NULL}
};

/*
 * Member table
 */

static PyMemberDef SemLock_members[] = {
    {"handle", T_SEM_HANDLE, offsetof(SemLock, handle), READONLY, ""},
    {"kind", T_INT, offsetof(SemLock, kind), READONLY, ""},
    {"maxvalue", T_INT, offsetof(SemLock, maxvalue), READONLY, ""},
    {NULL}
};

/*
 * Semaphore type
 */

PyTypeObject SemLockType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /* ob_size */
    "_processing.SemLock",     /* tp_name */
    sizeof(SemLock),           /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)SemLock_dealloc,
                               /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_compare */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, 
                               /* tp_flags */
    "Semaphore/Mutex type",    /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    SemLock_methods,           /* tp_methods */
    SemLock_members,           /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    (newfunc)SemLock_new,      /* tp_new */
};
