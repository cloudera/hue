/* AND classifier implementation */

PyDoc_STRVAR(hv_cli_and_doc,
"HV.cli_and(classifiers, memo) -> ObjectClassifier\n"
"\n"
"Return a classifier that combines the classifications of other classifiers.\n"
"\n"
"The classification returned from the returned classifier is a tuple containing\n"
"the classifications from the classifiers in the classifiers argument.\n"
);

typedef struct {
    /* Mimics a tuple - xxx should perhaps make a proper object/use tuple macros?! */
    PyObject_VAR_HEAD
    PyObject *classifiers;
    PyObject *memo;
} CliAndObject;


PyDoc_STRVAR(nodetuple_doc,
"Tuple with comparison based on addresses on the elements.\n"
);

#define NyNodeTuple_Check(op) PyObject_TypeCheck(op, &NyNodeTuple_Type)

static PyObject *
NyNodeTuple_New(int size)
{
    PyTupleObject *op;
    op = PyObject_GC_NewVar(PyTupleObject, &NyNodeTuple_Type, size);
    if (op == NULL)
      return NULL;
    memset(op->ob_item, 0, sizeof(*op->ob_item) * size);
    PyObject_GC_Track(op);
    return (PyObject *) op;
}


static PyObject *
hv_cli_and_fast_memoized_kind(CliAndObject * self, PyObject *kind)
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
hv_cli_and_memoized_kind(CliAndObject * self, PyObject *kind)
{
    int i, size;
    PyObject *nt, *result;
    if (!PyTuple_Check(kind)) {
	PyErr_SetString(PyExc_TypeError,
			"cli_and_memoized_kind: argument must be a (subtype of) tuple.");
	return 0;
    }
    size = PyTuple_GET_SIZE(kind);
    if (size != PyTuple_GET_SIZE(self->classifiers)) {
	PyErr_SetString(PyExc_ValueError,
			"cli_and_memoized_kind: wrong length of argument.");
	return 0;
    }
    nt = NyNodeTuple_New(size);
    if (!nt)
      return 0;
    for (i = 0; i < size; i++) {
	PyObject *superkind = PyTuple_GET_ITEM(kind, i);
	NyObjectClassifierObject *cli = (void *)PyTuple_GET_ITEM(self->classifiers, i);
	if (cli->def->memoized_kind) {
	    superkind = cli->def->memoized_kind(cli->self, superkind);
	    if (!superkind) {
		Py_DECREF(nt);
		return 0;
	    }
	} else {
	    Py_INCREF(superkind);
	}
	PyTuple_SET_ITEM(nt, i, superkind);
    }
    result = hv_cli_and_fast_memoized_kind(self, nt);
    Py_DECREF(nt);
    return result;
}




static PyObject *
hv_cli_and_classify(CliAndObject * self, PyObject *obj)
{
    int i, n;
    PyObject *classifiers = self->classifiers;
    PyObject *kind, *result;
    n = PyTuple_GET_SIZE(classifiers);
    kind = NyNodeTuple_New(n);
    if (!kind)
      goto Err;
    for (i = 0; i < n; i++) {
	NyObjectClassifierObject *cli = (void *)PyTuple_GET_ITEM(classifiers, i);
	PyObject *superkind = cli->def->classify(cli->self, obj);
	if (!superkind) {
	    goto Err;
	}
	PyTuple_SET_ITEM(kind, i, superkind);
	/* superkind is incref'd already */
    }
    result = hv_cli_and_fast_memoized_kind(self, kind);
    Py_DECREF(kind);
    return result;
  Err:
    Py_XDECREF(kind);
    return 0;
}

static NyObjectClassifierDef hv_cli_and_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_and",
    "classifier based on a combination  of other subclassifiers",
    (binaryfunc)hv_cli_and_classify,
    (binaryfunc)hv_cli_and_memoized_kind
};


static PyObject *
hv_cli_and(NyHeapViewObject *hv, PyObject *args)
{
    PyObject *r;
    CliAndObject *s, tmp;
    int i;
    if (!PyArg_ParseTuple(args, "O!O!:cli_and", 
			  &PyTuple_Type, &tmp.classifiers,
			  &PyDict_Type, &tmp.memo
			  )) {
	return 0;
    }
    if (PyType_Ready(&NyNodeTuple_Type) == -1)
      return 0;

    for (i = 0; i < PyTuple_GET_SIZE(tmp.classifiers); i++) {
	if (!PyObject_TypeCheck(PyTuple_GET_ITEM(tmp.classifiers, i),
				&NyObjectClassifier_Type)) {
	    PyErr_SetString(PyExc_TypeError,
			 "cli_and: classifiers argument must contain classifier objects.");
	    return 0;
	}
    }

    s = NYTUPLELIKE_NEW(CliAndObject);
    if (!s)
      return 0;
    s->classifiers = tmp.classifiers;
    Py_INCREF(s->classifiers);
    s->memo = tmp.memo;
    Py_INCREF(s->memo);
    r = NyObjectClassifier_New((PyObject *)s, &hv_cli_and_def);
    Py_DECREF(s);
    return r;
}

static long
nodetuple_hash(PyTupleObject *v)
{
	long x;
	int len = v->ob_size;
	PyObject **p;
	x = 0x436587L;
	p = v->ob_item;
	while (--len >= 0) {
		x = (1000003*x) ^ (long)p[0];
		p++;
	}
	x ^= v->ob_size;
	if (x == -1)
		x = -2;
	return x;

}

static int
nodetuple_traverse(PyObject *o, visitproc visit, void *arg)
{
    /* This is not automatically inherited!
       And the GC actually seg-faulted without it.
       */
    return PyTuple_Type.tp_traverse(o, visit, arg);
}


static PyObject *
nodetuple_richcompare(PyObject *v, PyObject *w, int op)
{
	PyTupleObject *vt, *wt;
	int i;
	int vlen, wlen;
	long vi=0, wi=0;
	int cmp;
	PyObject *res;

	if (!NyNodeTuple_Check(v) || !NyNodeTuple_Check(w)) {
		Py_INCREF(Py_NotImplemented);
		return Py_NotImplemented;
	}

	vt = (PyTupleObject *)v;
	wt = (PyTupleObject *)w;

	vlen = vt->ob_size;
	wlen = wt->ob_size;

	if (vlen != wlen) {
	    if (op == Py_EQ) { 
		/* Should be a common case, for dict lookup which is our primary intended usage. */
		Py_INCREF(Py_False); 
		return Py_False;
	    } else if (op == Py_NE) {
		Py_INCREF(Py_True); 
		return Py_True;
	    }
	}
	    

	/* Search for the first index where items are different.
	 */
	for (i = 0; i < vlen && i < wlen; i++) {
	    vi = (long)vt->ob_item[i];
	    wi = (long)vt->ob_item[i];
	    if (vi != wi)
	      break;
	}

	if (i < vlen && i < wlen) {
	    /* There is a final item to compare */
	    /* vi, wi has been set already */
	} else {
	    /* No more items to compare -- compare sizes */
	    vi = vlen;
	    wi = wlen;
	}
	switch (op) {
	  case Py_LT: cmp = vi <  wi; break;
	  case Py_LE: cmp = vi <= wi; break;
	  case Py_EQ: cmp = vi == wi; break;
	  case Py_NE: cmp = vi != wi; break;
	  case Py_GT: cmp = vi >  wi; break;
	  case Py_GE: cmp = vi >= wi; break;
	  default: return NULL; /* cannot happen */
	}
	if (cmp)
	  res = Py_True;
	else
	  res = Py_False;
	Py_INCREF(res);
	return res;
}




PyTypeObject NyNodeTuple_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"guppy.heapy.heapyc.NodeTuple",
	sizeof(PyTupleObject) - sizeof(PyObject *),
	sizeof(PyObject *),
	(destructor)0,				/* tp_dealloc */
	(printfunc)0,				/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	(reprfunc)0,				/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	(hashfunc)nodetuple_hash,		/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
		Py_TPFLAGS_BASETYPE,		/* tp_flags */
	nodetuple_doc,				/* tp_doc */
 	(traverseproc)nodetuple_traverse,	/* tp_traverse */
	0,					/* tp_clear */
	nodetuple_richcompare,			/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,		    			/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,				/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	0,					/* tp_new */
	PyObject_GC_Del,        		/* tp_free */
};

