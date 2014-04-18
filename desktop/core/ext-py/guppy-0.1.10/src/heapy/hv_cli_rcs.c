/* Implementation of the 'rcs' classifier */

PyDoc_STRVAR(hv_cli_rcs_doc,
"HV.cli_rcs(referrers, classifier, memo) -> ObjectClassifier\n\
\n\
Return a classifier that classifies by \"Referrer Classification Set\".\n\
\n\
The classification of an object is the classifications of its\n\
referrers, collected in an immutable NodeSet object. Arguments:\n\
\n\
    referrers   A NodeGraph object used to\n\
                map each object to its referrers.\n\
\n\
    classifier  A ObjectClassifier object used to\n\
                classify each referrer.\n\
\n\
    memo        A dict object used to\n\
                memoize the classification sets.\n\
");


typedef struct {
    /* Mimics a tuple - xxx should perhaps make a proper object/use tuple macros?! */
    PyObject_VAR_HEAD
    NyHeapViewObject *hv;
    NyObjectClassifierObject *cli;
    NyNodeGraphObject *rg;
    NyNodeSetObject *norefer;
    PyObject *memo;
} RetclasetObject;

static PyObject *
hv_cli_rcs_fast_memoized_kind(RetclasetObject * self, PyObject *kind)
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

typedef struct {
    NyObjectClassifierObject *cli;
    NyNodeSetObject *ns;
} MemoRcsArg;

static int
rcs_visit_memoize_sub(PyObject *obj, MemoRcsArg *arg)
{
    obj = arg->cli->def->memoized_kind(arg->cli->self, obj);
    if (!obj)
	return -1;
    if (NyNodeSet_setobj(arg->ns, obj) == -1) {
	Py_DECREF(obj);
	return -1;
    }
    Py_DECREF(obj);
    return 0;
}

static PyObject *
hv_cli_rcs_memoized_kind(RetclasetObject * self, PyObject *kind)
{
    if (!NyNodeSet_Check(kind)) {
	PyErr_SetString(PyExc_TypeError,
			"hv_cli_rcs_memoized_kind: nodeset object (immutable) expected.");
	return 0;
    }
    if (!self->cli->def->memoized_kind) {
	return hv_cli_rcs_fast_memoized_kind(self, kind);
    } else {
	MemoRcsArg arg;
	PyObject *result;
	arg.cli = self->cli;
	arg.ns = hv_mutnodeset_new(self->hv);
	if (!arg.ns)
	  return 0;
	if (iterable_iterate(kind, (visitproc)rcs_visit_memoize_sub, &arg) == -1)
	  goto Err;
	if (NyNodeSet_be_immutable(&arg.ns) == -1)
	  goto Err;
	result = hv_cli_rcs_fast_memoized_kind(self, (PyObject *)arg.ns);
      Ret:
	Py_DECREF(arg.ns);
	return result;
      Err:
	result = 0;
	goto Ret;
    }
}




static PyObject *
hv_cli_rcs_classify(RetclasetObject * self, PyObject *obj)
{
    NyNodeGraphEdge *lo, *hi, *cur;
    PyObject *kind = 0;
    NyNodeSetObject *Ri = hv_mutnodeset_new(self->hv);
    if (!Ri)
      goto Err;
    if (NyNodeGraph_Region(self->rg, obj, &lo, &hi) == -1) {
	goto Err;
    }
    for (cur = lo; cur < hi; cur++) {
	if (cur->tgt == Py_None)
	  continue;
	kind = self->cli->def->classify(self->cli->self, cur->tgt);
	if (!kind)
	  goto Err;
	if (NyNodeSet_setobj(Ri, kind) == -1)
	  goto Err;
	Py_DECREF(kind);
    }
    if (NyNodeSet_be_immutable(&Ri) == -1)
      goto Err;
    kind = hv_cli_rcs_fast_memoized_kind(self, (PyObject *)Ri);
    Py_DECREF(Ri);
    return kind;
    
  Err:
    Py_XDECREF(kind);
    Py_XDECREF(Ri);
    return 0;
}

static int
hv_cli_rcs_le(PyObject * self, PyObject *a, PyObject *b)
{
    return PyObject_RichCompareBool(a, b, Py_LE);
}

static NyObjectClassifierDef hv_cli_rcs_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "hv_cli_rcs",
    "classifier returning ...",
    (binaryfunc)hv_cli_rcs_classify,
    (binaryfunc)hv_cli_rcs_memoized_kind,
    hv_cli_rcs_le
};


static PyObject *
hv_cli_rcs(NyHeapViewObject *hv, PyObject *args)
{
    PyObject *r;
    RetclasetObject *s, tmp;
    if (!PyArg_ParseTuple(args, "O!O!O!:cli_rcs", 
			  &NyNodeGraph_Type, &tmp.rg,
			  &NyObjectClassifier_Type, &tmp.cli,
			  &PyDict_Type, &tmp.memo)) {
	return 0;
    }
    s = NYTUPLELIKE_NEW(RetclasetObject);
    if (!s)
      return 0;

    s->hv = hv;
    Py_INCREF(hv);
    s->rg = tmp.rg;
    Py_INCREF(tmp.rg);
    s->cli = tmp.cli;
    Py_INCREF(tmp.cli);
    s->memo = tmp.memo;
    Py_INCREF(tmp.memo);
    r = NyObjectClassifier_New((PyObject *)s, &hv_cli_rcs_def);
    Py_DECREF(s);
    return r;
}





