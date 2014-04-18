/* Module guppy.sets.setsc */

char sets_doc[] =
"This module implements two specialized kinds of sets, 'bitsets' and\n"
"'nodesets'. Bitsets are sets of 'bits' -- here meaning integers in a\n"
"particular range -- and designed to be efficient with dense as well as\n"
"sparse distributions.  Nodesets are sets of 'nodes', i.e. objects with\n"
"equality based on their address; this makes inclusion test work with\n"
"any combination of objects independently from how equality or hashing\n"
"has been defined for the objects involved.\n"
"\n"
"Summary of module content.\n"
"\n"
"Classes\n"
"    BitSet              Abstract bitset base class.\n"
"        CplBitSet       Complemented immutable bitset.\n"
"        ImmBitSet       Immutable bitset, non-complemented.\n"
"        MutBitSet       Mutable bitset, complemented or not.\n"
"    NodeSet             Abstract nodeset base class.\n"
"        ImmNodeSet      Immutable nodeset.\n"
"        MutNodeSet      Mutable nodeset.\n"
"    \n"
"Functions\n"
"    immbit              Immutable bitset singleton constructor.\n"
"    immbitrange         Immutable bitset range constructor.\n"
"    immbitset           Immutable bitset constructor.\n"
"\n"
"Data\n"
"    NyBitSet_Exports,\n"
"    NyNodeSet_Exports   C-level exported function tables.\n";


#include "Python.h"

#include "../heapy/heapdef.h"
#include "../heapy/heapy.h"
#include "sets_internal.h"

#define INITFUNC initsetsc
#define MODNAME "setsc"

extern int fsb_dx_nybitset_init(PyObject *m);
extern int fsb_dx_nynodeset_init(PyObject *m);

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

static NyHeapDef nysets_heapdefs[] = {
    {0, 0, (NyHeapDef_SizeGetter) mutbitset_indisize},
    {0, 0, 0, cplbitset_traverse},
    {0, 0, nodeset_indisize,  nodeset_traverse, nodeset_relate},
    {0}
};



DL_EXPORT (void)
INITFUNC (void)
{
    PyObject *m;
    PyObject *d;

    nysets_heapdefs[0].type = &NyMutBitSet_Type;
    nysets_heapdefs[1].type = &NyCplBitSet_Type;
    nysets_heapdefs[2].type = &NyNodeSet_Type;

    m = Py_InitModule(MODNAME, module_methods);
    if (!m)
      goto Error;
    d = PyModule_GetDict(m);
    if (fsb_dx_nybitset_init(m) == -1)
      goto Error;
    if (fsb_dx_nynodeset_init(m) == -1)
      goto Error;
    if (PyDict_SetItemString(d, "__doc__", PyString_FromString(sets_doc)) == -1)
      goto Error;
    if (PyDict_SetItemString(d,
			 "_NyHeapDefs_",
			 PyCObject_FromVoidPtrAndDesc(
						      &nysets_heapdefs,
						      "NyHeapDef[] v1.0",
						      0)
			 ) == -1)
      goto Error;
    return;
  Error:
    if (PyErr_Occurred() == NULL)
      PyErr_SetString(PyExc_ImportError, "module initialization failed");
}
