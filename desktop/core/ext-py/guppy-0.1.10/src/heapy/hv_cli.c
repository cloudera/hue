/* Classifier implementations */

#define NYTUPLELIKE_NEW(t) ((t *)PyTuple_New((sizeof(t) - sizeof(PyTupleObject)) / 4 + 1))

#include "hv_cli_and.c"
#include "hv_cli_dictof.c"
#include "hv_cli_id.c"
#include "hv_cli_idset.c"
#include "hv_cli_rcs.c"
#include "hv_cli_indisize.c"
#include "hv_cli_findex.c"
#include "hv_cli_rel.c"
#include "hv_cli_user.c"

static PyObject *
hv_cli_none_classify(NyHeapViewObject *self, PyObject *arg)
{
    Py_INCREF(Py_None);
    return Py_None;
}

static int
hv_cli_none_le(PyObject * self, PyObject *a, PyObject *b)
{
    return 1;
}
    

static NyObjectClassifierDef hv_cli_none_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_none",
    "classifier returning None",
    (binaryfunc)hv_cli_none_classify,
    (binaryfunc)0,
    hv_cli_none_le,
};

PyDoc_STRVAR(hv_cli_none_doc,
"HV.cli_none() -> ObjectClassifier\n\
\n\
Return a classifier that classifies all objects the same.\n\
\n\
The classification of each object is None.");

static PyObject *
hv_cli_none(NyHeapViewObject *self, PyObject *args)
{
    return NyObjectClassifier_New((PyObject *)self, &hv_cli_none_def);
}


static PyObject *
hv_cli_class_classify(NyHeapViewObject *self, PyObject *arg)
{
    return hv_std_classify(self, arg);
}

static int
hv_cli_class_le(PyObject * self, PyObject *a, PyObject *b)
{
    if (a == b)
      return 1;
    if (PyType_Check(a) && PyType_Check(b))
      return PyType_IsSubtype((PyTypeObject *)a, (PyTypeObject *)b);
    if (PyClass_Check(a) && PyClass_Check(b))
      return PyClass_IsSubclass(a, b);
    return 0;
}

static NyObjectClassifierDef hv_cli_class_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_class",
    "classifier returning object class",
    (binaryfunc)hv_cli_class_classify,
    (binaryfunc)0,
    hv_cli_class_le,

};


PyDoc_STRVAR(hv_cli_class_doc,
"HV.cli_class() -> ObjectClassifier\n\
\n\
Return a classifier that classifies by \"class\".\n\
\n\
If an object is of instance type, its classification will be its\n\
class, as given in its C-level member 'in_class', otherwise it will\n\
be its type, as given in 'ob_type'.\n\
\n\
[This is like classifying by the Python-level '__class__' attribute\n\
in newer versions of Python, except that even though the '__class__'\n\
attribute may be redefined via the class definition, the classification\n\
as made by cli_class isn't affected.]");

static PyObject *
hv_cli_class(NyHeapViewObject *self, PyObject *args)
{
    return NyObjectClassifier_New((PyObject *)self, &hv_cli_class_def);
}


static PyObject *
hv_cli_type_classify(NyHeapViewObject *hv, PyObject *obj)
{
    Py_INCREF(obj->ob_type);
    return (PyObject *)obj->ob_type;
}

static int
hv_cli_type_le(PyObject * self, PyObject *a, PyObject *b)
{
    return (a == b) || PyType_IsSubtype((PyTypeObject *)a, (PyTypeObject *)b);

}

static NyObjectClassifierDef hv_cli_type_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_type",
    "classifier returning object type",
    (binaryfunc)hv_cli_type_classify,
    (binaryfunc)0,
    hv_cli_type_le,
};

PyDoc_STRVAR(hv_cli_type_doc,
"HV.cli_type() -> ObjectClassifier\n\
\n\
Return a classifier that classifies by type.\n\
\n\
The classification of each object is the type, as given by its\n\
C-level member 'ob_type'. (This is the same as the type returned\n\
by the Python-level builtin 'type'.)");

static PyObject *
hv_cli_type(NyHeapViewObject *self, PyObject *args)
{
    return NyObjectClassifier_New((PyObject *)self, &hv_cli_type_def);
}

