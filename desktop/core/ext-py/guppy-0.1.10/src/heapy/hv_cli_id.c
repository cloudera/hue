/* Implementation of the identity classifier */

PyDoc_STRVAR(hv_cli_id_doc,
"HV.cli_id() -> ObjectClassifier\n\
\n\
Return a classifier that classifies by identity.\n\
\n\
The classification of an object is the object itself.");

static PyObject *
hv_cli_id_classify(NyHeapViewObject *self, PyObject *arg)
{
    Py_INCREF(arg);
    return arg;
}

static int
hv_cli_id_le(PyObject * self, PyObject *a, PyObject *b)
{
    return a <= b;
}


static NyObjectClassifierDef hv_cli_id_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_id",
    "classifier returning the object itself",
    (binaryfunc)hv_cli_id_classify,
    (binaryfunc)0,
    hv_cli_id_le,
};

static PyObject *
hv_cli_id(NyHeapViewObject *self, PyObject *args)
{
    return NyObjectClassifier_New((PyObject *)self, &hv_cli_id_def);
}

