/*
 * util.h
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * Export utility functions and macros.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 *
 * @(#) $Id: util.h,v 1.8 2002/08/16 10:08:09 martin Exp $
 */
#ifndef PyOpenSSL_UTIL_H_
#define PyOpenSSL_UTIL_H_

#include <Python.h>
#include <openssl/err.h>

/*
 * pymemcompat written by Michael Hudson and lets you program to the
 * Python 2.3 memory API while keeping backwards compatibility.
 */
#include "pymemcompat.h"

/*
 * py3k defines macros that help with Python 2.x/3.x compatibility.
 */
#include "py3k.h"


extern  PyObject *error_queue_to_list(void);
extern void exception_from_error_queue(PyObject *the_Error);
extern  void      flush_error_queue(void);

/*
 * These are needed because there is no "official" way to specify
 * WHERE to save the thread state.
 */
#ifdef WITH_THREAD

/*
 * Get the current Python threadstate and put it somewhere any code running
 * in this thread can get it, if it needs to restore the threadstate to run
 * some Python.
 */
#  define MY_BEGIN_ALLOW_THREADS(ignored)                               \
    PyThread_delete_key_value(_pyOpenSSL_tstate_key);			\
    PyThread_set_key_value(_pyOpenSSL_tstate_key, PyEval_SaveThread());

/*
 * Get the previous Python threadstate and restore it.
 */
#  define MY_END_ALLOW_THREADS(ignored)                                 \
    PyEval_RestoreThread(PyThread_get_key_value(_pyOpenSSL_tstate_key));

#else
#  define MY_BEGIN_ALLOW_THREADS(st)
#  define MY_END_ALLOW_THREADS(st)      { st = NULL; }
#endif

#if !defined(PY_MAJOR_VERSION) || PY_VERSION_HEX < 0x02000000
static int
PyModule_AddObject(PyObject *m, char *name, PyObject *o)
{
    PyObject *dict;
    if (!PyModule_Check(m) || o == NULL)
        return -1;
    dict = PyModule_GetDict(m);
    if (dict == NULL)
        return -1;
    if (PyDict_SetItemString(dict, name, o))
        return -1;
    Py_DECREF(o);
    return 0;
}

static int
PyModule_AddIntConstant(PyObject *m, char *name, long value)
{
    return PyModule_AddObject(m, name, PyInt_FromLong(value));
}

static int PyObject_AsFileDescriptor(PyObject *o)
{
    int fd;
    PyObject *meth;

    if (PyInt_Check(o)) {
        fd = PyInt_AsLong(o);
    }
    else if (PyLong_Check(o)) {
        fd = PyLong_AsLong(o);
    }
    else if ((meth = PyObject_GetAttrString(o, "fileno")) != NULL)
    {
        PyObject *fno = PyEval_CallObject(meth, NULL);
        Py_DECREF(meth);
        if (fno == NULL)
            return -1;

        if (PyInt_Check(fno)) {
            fd = PyInt_AsLong(fno);
            Py_DECREF(fno);
        }
        else if (PyLong_Check(fno)) {
            fd = PyLong_AsLong(fno);
            Py_DECREF(fno);
        }
        else {
            PyErr_SetString(PyExc_TypeError, "fileno() returned a non-integer");
            Py_DECREF(fno);
            return -1;
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "argument must be an int, or have a fileno() method.");
        return -1;
    }

    if (fd < 0) {
        PyErr_Format(PyExc_ValueError, "file descriptor cannot be a negative integer (%i)", fd);
        return -1;
    }
    return fd;
}
#endif

#if !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif

#if (PY_VERSION_HEX < 0x02600000)
extern PyObject* PyOpenSSL_LongToHex(PyObject *o);
#else
#define PyOpenSSL_LongToHex(o) PyNumber_ToBase(o, 16)
#endif

#endif
