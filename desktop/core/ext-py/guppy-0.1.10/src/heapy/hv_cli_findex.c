/* Implementation of the "findex" classifier (for lack of a better name)
   a generalization of biper (bipartitioner)
   as discussed in Notes Sep 21 2005.

*/

PyDoc_STRVAR(hv_cli_findex_doc,
"HV.cli_findex(tuple, memo) -> ObjectClassifier\n\
");


typedef struct {
    PyObject_VAR_HEAD
    PyObject *alts;
    PyObject *memo;
    PyObject *kinds;
    PyObject *cmps;
} FindexObject;

static PyObject *
hv_cli_findex_memoized_kind(FindexObject * self, PyObject *kind)
{
    PyObject *result = PyDict_GetItem(self->memo, kind);
    if (!result) {
	if (PyErr_Occurred())
	  goto Err;
	if (PyDict_SetItem(self->memo, kind, kind) == -1)
	  goto Err;
	result = kind;
    }
    Py_INCREF(result);
    return result;
  Err:
    return 0;
}


static PyObject *
hv_cli_findex_classify(FindexObject * self, PyObject *obj)
{
    int i, numalts;
    PyObject *kind, *ret, *index;
    numalts = PyTuple_GET_SIZE(self->alts);
    for (i = 0; i < numalts; i++) {
	PyObject *ckc = PyTuple_GET_ITEM(self->alts, i);
	NyObjectClassifierObject *cli = (void *)PyTuple_GET_ITEM(ckc, 0);
	PyObject *cmpkind = PyTuple_GET_ITEM(self->kinds, i);
	long cmp = PyInt_AS_LONG(PyTuple_GET_ITEM(self->cmps, i));
	kind = cli->def->classify(cli->self, obj);
	if (!kind)
	  return 0;
	cmp = NyObjectClassifier_Compare(cli, kind, cmpkind, cmp);
	Py_DECREF(kind);
	if (cmp == -1)
	  return 0;
	if (cmp)
	  break;
    }
    index = PyInt_FromLong(i);
    if (!index)
      return 0;
    ret = hv_cli_findex_memoized_kind(self, index);
    Py_DECREF(index);
    return ret;
}

static int
hv_cli_findex_le(PyObject * self, PyObject *a, PyObject *b)
{
    return PyObject_RichCompareBool(a, b, Py_LE);
}

static NyObjectClassifierDef hv_cli_findex_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_findex",
    "classifier returning index of matching kind",
    (binaryfunc)hv_cli_findex_classify,
    (binaryfunc)hv_cli_findex_memoized_kind,
    hv_cli_findex_le,
};

static PyObject *
hv_cli_findex(NyHeapViewObject *hv, PyObject *args)
{
    PyObject *r;
    FindexObject *s, tmp;
    int numalts;
    int i;
    if (!PyArg_ParseTuple(args, "O!O!:cli_findex", 
			  &PyTuple_Type, &tmp.alts,
			  &PyDict_Type, &tmp.memo)) {
	return 0;
    }
    numalts = PyTuple_GET_SIZE(tmp.alts);
    for (i = 0; i < numalts; i++) {
	PyObject *ckc = PyTuple_GET_ITEM(tmp.alts, i);
	if (!PyTuple_Check(ckc)) {
	    PyErr_SetString(PyExc_TypeError, "Tuple of TUPLES expected.");
	    return 0;
	}
	if (!PyTuple_GET_SIZE(ckc) == 3) {
	    PyErr_SetString(PyExc_TypeError, "Tuple of TRIPLES expected.");
	    return 0;
	}
	if (!NyObjectClassifier_Check(PyTuple_GET_ITEM(ckc, 0))) {
	    PyErr_SetString(PyExc_TypeError, "Tuple of triples with [0] a CLASSIFIER expected.");
	    return 0;
	}
	if (!PyString_Check(PyTuple_GET_ITEM(ckc, 2))) {
	    PyErr_SetString(PyExc_TypeError, "Tuple of triples with [2] a STRING expected.");
	    return 0;
	}
	if (cli_cmp_as_int(PyTuple_GET_ITEM(ckc, 2)) == -1) {
	    return 0;
	}
    }
    s = NYTUPLELIKE_NEW(FindexObject);
    if (!s)
      return 0;
    s->alts = tmp.alts;
    Py_INCREF(tmp.alts);
    s->memo = tmp.memo;
    Py_INCREF(tmp.memo);
    s->kinds = PyTuple_New(numalts);
    s->cmps = PyTuple_New(numalts);
    if (!s->kinds)
      goto Err;
    for (i = 0; i < numalts; i++) {
	PyObject *ckc = PyTuple_GET_ITEM(tmp.alts, i);
	NyObjectClassifierObject *cli = (void *)PyTuple_GET_ITEM(ckc, 0);
	PyObject *mk = PyTuple_GET_ITEM(ckc, 1);
	if (cli->def->memoized_kind) {
	    mk = cli->def->memoized_kind(cli->self, mk);
	    if (!mk)
	      goto Err;
	} else {
	    Py_INCREF(mk);
	}
	PyTuple_SET_ITEM(s->kinds, i, mk);
	mk = PyInt_FromLong(cli_cmp_as_int(PyTuple_GET_ITEM(ckc, 2)));
	if (!mk)
	  goto Err;
	PyTuple_SET_ITEM(s->cmps, i, mk);
					   
    }
    r = NyObjectClassifier_New((PyObject *)s, &hv_cli_findex_def);
    Py_DECREF(s);
    return r;
  Err:
    Py_DECREF(s);
    return 0;
}
