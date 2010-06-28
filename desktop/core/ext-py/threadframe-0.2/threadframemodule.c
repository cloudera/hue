/*
 * module to access the stack frame of all Python interpreter threads
 *
 * works on Solaris and OS X, portability to other OSes unknown
 *
 * Fazal Majid, 2002-10-11
 *
 * with contributions from Bob Ippolito (http://bob.pycs.net/)
 *
 * Copyright (c) 2002-2004 Kefta Inc.
 * All rights reserved
 *
 */

#include "Python.h"
#include "compile.h"
#include "frameobject.h"
#include "patchlevel.h"

static PyObject *
threadframe_threadframe(PyObject *self, PyObject *args) {
  PyInterpreterState *interp;
  PyThreadState *tstate;
  PyFrameObject *frame;
  PyListObject *frames;

  frames = (PyListObject*) PyList_New(0);
  if (! frames) return NULL;

  /* Walk down the interpreters and threads until we find the one
     matching the supplied thread ID. */
  for (interp = PyInterpreterState_Head(); interp != NULL;
       interp = interp->next) {
    for(tstate = interp->tstate_head; tstate != NULL;
	tstate = tstate->next) {
      frame = tstate->frame;
      if (! frame) continue;
      Py_INCREF(frame);
      PyList_Append((PyObject*) frames, (PyObject*) frame);
    }
  }
  return (PyObject*) frames;
}

/* the PyThreadState gained a thread_id member only in 2.3rc1 */
static PyObject *
threadframe_dict(PyObject *self, PyObject *args) {
#if PY_VERSION_HEX < 0x02030000
  PyErr_SetString(PyExc_NotImplementedError,
		  "threadframe.dict() requires Python 2.3 or later");
  return NULL;
#else
  PyInterpreterState *interp;
  PyThreadState *tstate;
  PyFrameObject *frame;
  PyObject *frames;

  frames = (PyObject*) PyDict_New();
  if (! frames) return NULL;

  /* Walk down the interpreters and threads until we find the one
     matching the supplied thread ID. */
  for (interp = PyInterpreterState_Head(); interp != NULL;
       interp = interp->next) {
    for(tstate = interp->tstate_head; tstate != NULL;
	tstate = tstate->next) {
      PyObject *thread_id;
      frame = tstate->frame;
      if (! frame) continue;
      thread_id = PyInt_FromLong(tstate->thread_id);
      PyDict_SetItem(frames, thread_id, (PyObject*)frame);
      Py_DECREF(thread_id);
    }
  }
  return frames;
#endif
}

static char threadframe_doc[] =
"Returns a list of frame objects for all threads.\n"
"(equivalent to dict().values() on 2.3 and later).";

static char threadframe_dict_doc[] =
"Returns a dictionary, mapping for all threads the thread ID\n"
"(as returned by thread.get_ident() or by the keys to threading._active)\n"
"to the corresponding frame object.\n"
"Raises NotImplementedError on Python 2.2.";

/* List of functions defined in the module */

static PyMethodDef threadframe_methods[] = {
  {"threadframe", threadframe_threadframe, METH_VARARGS, threadframe_doc},
  {"dict",        threadframe_dict, METH_VARARGS, threadframe_dict_doc},
  {NULL,	  NULL}	/* sentinel */
};


/* Initialization function for the module (*must* be called initthreadframe) */

static char module_doc[] =
"Debugging module to extract stack frames for all Python interpreter heads.\n"
"Useful in conjunction with traceback.print_stack().\n";

DL_EXPORT(void)
initthreadframe(void)
{
  PyObject *m;

  /* Create the module and add the functions */
  m = Py_InitModule3("threadframe", threadframe_methods, module_doc);
}
