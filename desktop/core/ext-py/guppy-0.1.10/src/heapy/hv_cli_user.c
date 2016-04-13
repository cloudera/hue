/* Implementation of user defined classifiers. */

PyDoc_STRVAR(hv_cli_user_defined_doc,
"\n"
);

typedef struct {
    /* Mimics a tuple */
    PyObject_VAR_HEAD
    NyObjectClassifierObject *cond_cli;
    PyObject *cond_kind;
    PyObject *classify;
    PyObject *memoized_kind;
    NyNodeGraphObject *rg;
    NyNodeSetObject *norefer;
    PyObject *dict;


} UserObject;

static PyObject *
hv_cli_user_memoized_kind(UserObject * self, PyObject *kind)
{
    if (self->memoized_kind != Py_None && kind != Py_None) {
	kind = PyObject_CallFunctionObjArgs(self->memoized_kind, kind, 0);
    } else {
	Py_INCREF(kind);
    }
    return kind;
}

static PyObject *
hv_cli_user_classify(UserObject * self, PyObject *obj)
{
    PyObject *kind;
    kind = self->cond_cli->def->classify(self->cond_cli->self, obj);
    if (!kind)
      return 0;
    if (kind != self->cond_kind) {
	Py_DECREF(kind);
	kind = Py_None;
	Py_INCREF(kind);
	return kind;
    } else {
	Py_DECREF(kind);
	return PyObject_CallFunctionObjArgs(self->classify, obj, 0);
    }
}

static NyObjectClassifierDef hv_cli_user_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_user_defined",
    "user defined classifier",
    (binaryfunc)hv_cli_user_classify,
    (binaryfunc)hv_cli_user_memoized_kind,
};



static PyObject *
hv_cli_user_defined(NyHeapViewObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"cond_cli", "cond_kind", "classify", "memoized_kind", 0};
    UserObject *s, tmp;
    PyObject *r;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!OOO:user_defined", kwlist,
				     &NyObjectClassifier_Type, &tmp.cond_cli,
				     &tmp.cond_kind,
				     &tmp.classify,
				     &tmp.memoized_kind
				     ))
      return 0;

    s = NYTUPLELIKE_NEW(UserObject);
    if (!s)
      return 0;

    s->cond_cli = tmp.cond_cli;
    Py_INCREF(s->cond_cli);
    s->cond_kind = tmp.cond_kind;
    Py_INCREF(s->cond_kind);
    s->classify = tmp.classify;
    Py_INCREF(s->classify);
    s->memoized_kind = tmp.memoized_kind;
    Py_INCREF(s->memoized_kind);
    r = NyObjectClassifier_New((PyObject *)s, &hv_cli_user_def);
    Py_DECREF(s);
    return r;
}
