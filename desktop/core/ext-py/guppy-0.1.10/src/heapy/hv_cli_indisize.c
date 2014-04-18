/* Implementation of the 'indisize' classifier */

typedef struct {
    PyObject_VAR_HEAD
    NyHeapViewObject *hv;
    PyObject *memo;
} IndisizeObject;



static PyObject *
hv_cli_indisize_memoized_kind(IndisizeObject *self, PyObject *size)
{
    PyObject *memoedsize = PyDict_GetItem(self->memo, size);
    if (!memoedsize) {
	if (PyDict_SetItem(self->memo, size, size) == -1) {
	    return 0;
	}
	memoedsize = size;
    }
    Py_INCREF(memoedsize);
    return memoedsize;
}

static PyObject *
hv_cli_indisize_classify(IndisizeObject *self, PyObject *obj)
{
    PyObject *size = PyInt_FromLong(hv_std_size(self->hv, obj));
    PyObject *memoedsize;
    if (!size)
      return size;
    memoedsize = hv_cli_indisize_memoized_kind(self, size);
    Py_DECREF(size);
    return memoedsize;
}

static int
hv_cli_indisize_le(PyObject * self, PyObject *a, PyObject *b)
{
    return PyObject_RichCompareBool(a, b, Py_LE);
}


static NyObjectClassifierDef hv_cli_indisize_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_type",
    "classifier returning object size",
    (binaryfunc)hv_cli_indisize_classify,
    (binaryfunc)hv_cli_indisize_memoized_kind,
    hv_cli_indisize_le,
};

static char hv_cli_indisize_doc[] =
"HV.cli_indisize(memo) -> ObjectClassifier\n"
"\n"
"Return a classifier that classifies by \"individual size\".\n"
"\n"
"The classification of each object is an int, containing the\n"
"object's individual memory size. The argument is:\n"
"\n"
"    memo        A dict used to memoize the classification objects.";

static PyObject *
hv_cli_indisize(NyHeapViewObject *self, PyObject *args)
{
    PyObject *r, *memo;
    IndisizeObject *s;
    if (!PyArg_ParseTuple(args, "O!:cli_indisize", 
			  &PyDict_Type, &memo))
      return NULL;
    s = NYTUPLELIKE_NEW(IndisizeObject);
    if (!s)
      return 0;
    s->hv = self;
    Py_INCREF(s->hv);
    s->memo = memo;
    Py_INCREF(memo);
    r = NyObjectClassifier_New((PyObject *)s, &hv_cli_indisize_def);
    Py_DECREF(s);
    return r;
}
