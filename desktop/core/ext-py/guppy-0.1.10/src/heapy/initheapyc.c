#include "Python.h"

#define INITFUNC initheapyc
#define MODNAME "heapyc"

extern int fsb_dx_nybitset_init(PyObject *m);

static PyMethodDef module_methods[] =
{
	{NULL, NULL}
};

int fsb_dx_addmethods(PyObject *m, PyMethodDef *methods, PyObject *passthrough) {
    PyObject *d, *v;
	PyMethodDef *ml;
	d = PyModule_GetDict(m);
	for (ml = methods; ml->ml_name != NULL; ml++) {
		v = PyCFunction_New(ml, passthrough);
		if (v == NULL)
			return -1;
		if (PyDict_SetItemString(d, ml->ml_name, v) != 0) {
			Py_DECREF(v);
			return -1;
		}
		Py_DECREF(v);
	}
    return 0;
}

DL_EXPORT (void)
INITFUNC (void)
{
    PyObject *m;
    m = Py_InitModule(MODNAME, module_methods);
    if (!m)
      goto Error;
    if (fsb_dx_nyhprof_init(m) == -1)
      goto Error;
    return;
  Error:
    if (PyErr_Occurred() == NULL)
      PyErr_SetString(PyExc_ImportError, "module initialization failed");
}
