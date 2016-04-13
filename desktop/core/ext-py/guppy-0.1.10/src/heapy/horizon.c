/* Implementation of the Horizon type */

char horizon_doc[]=
"Horizon(X:iterable)\n"
"\n"
"Create a new Horizon object from X. \n"
"\n"
"The objects in X will be used to initialize a set of objects within\n"
"the Horizon object. There are no official references to these objects,\n"
"but as some of these objects become deallocated, they will be removed\n"
"from the set of objects within the Horizon object. The objects within\n"
"the set of objects within the Horizon object can be compared to\n"
"another set of objects via the news() method. This can be used to see\n"
"what objects have been allocated but not deallocated since the Horizon\n"
"object was created.\n"
;



typedef struct _NyHorizonObject {
    PyObject_HEAD
    struct _NyHorizonObject *next;
    NyNodeSetObject *hs;
} NyHorizonObject;

/* Horizon Management
   The struct rm must be a static/global singleton, since it is intimately bound to patching
 */

static struct {
    NyHorizonObject *horizons;
    PyObject *types;
} rm;

static destructor
horizon_get_org_dealloc(PyTypeObject *t)
{
    PyObject *d = PyDict_GetItem(rm.types, (PyObject *)t);
    if (!d) {
	Py_FatalError("horizon_get_org_dealloc: no original destructor found");
    }
    return (destructor)PyInt_AsLong(d);
}

static void
horizon_remove(NyHorizonObject *v)
{
    NyHorizonObject **p;
    for (p = &rm.horizons; *p != v; p = &((*p)->next)) {
	if (!*p)
	  Py_FatalError("horizon_remove: no such horizon found");
    }
    *p = v->next;
    if (!rm.horizons && rm.types) {
	Py_ssize_t i = 0;
	PyObject *pk, *pv;
	while (PyDict_Next(rm.types, &i, &pk, &pv)) {
	    ((PyTypeObject *)pk)->tp_dealloc = (destructor) PyInt_AsLong(pv);
	}
	Py_DECREF(rm.types);
	rm.types = 0;
    }
}


static void
horizon_dealloc(NyHorizonObject *rg)
{
    horizon_remove(rg);
    Py_XDECREF(rg->hs);
    rg->ob_type->tp_free((PyObject *)rg);
}


static PyTypeObject *
horizon_base(PyObject *v)
{
    PyTypeObject *t = v->ob_type;
    while (t->tp_flags & Py_TPFLAGS_HEAPTYPE) {
	assert(t->tp_base);
	assert (t->ob_type == t->tp_base->ob_type);
	t = t->tp_base;
    }
    return t;
}


static void
horizon_patched_dealloc(PyObject *v)
{

    NyHorizonObject *r;
    for (r = rm.horizons; r; r = r->next) {
	if (NyNodeSet_clrobj(r->hs, v) == -1)
	  Py_FatalError("horizon_patched_dealloc: could not clear object in nodeset");
    }
    horizon_get_org_dealloc(horizon_base(v))(v);
}

static int
horizon_patch_dealloc(PyTypeObject *t)
{

    PyObject *org;
    if (!rm.types) {
	rm.types = PyDict_New();
	if (!rm.types)
	  return -1;
    }
    if (!(org = PyInt_FromLong((long)t->tp_dealloc)))
      return -1;
    if (PyDict_SetItem(rm.types, (PyObject *)t, org) == -1) {
	Py_DECREF(org);
	return -1;
    }
    t->tp_dealloc = horizon_patched_dealloc;
    Py_DECREF(org);
    return 0;
}

static int
horizon_update_trav(PyObject *obj, NyHorizonObject *ta) {
    int r;
    r = NyNodeSet_setobj(ta->hs, obj);
    if (!r) {
	PyTypeObject *t = horizon_base(obj);
	if (t->tp_dealloc != horizon_patched_dealloc) {
	    if (horizon_patch_dealloc(t) == -1) {
		return -1;
	    }
	}
    }
    if (r == -1)
      return -1;
    return 0;
}

PyObject *
horizon_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{

    PyObject *X;
    NyHorizonObject *hz = 0;
    static char *kwlist[] = {"X", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O:Horizon.__new__",
				     kwlist,
				     &X))
      goto err;
    hz = (NyHorizonObject *)type->tp_alloc(type, 1);
    if (!hz)
      goto err;
    hz->next = rm.horizons;
    rm.horizons = hz;
    hz->hs = NyMutNodeSet_NewFlags(0); /* I.E. not NS_HOLDOBJECTS */
    if (!hz->hs)
      goto err;
    if (iterable_iterate((PyObject *)X, (visitproc)horizon_update_trav, hz) == -1 ||
	horizon_update_trav((PyObject *)hz, hz) == -1)
      goto err;
    return (PyObject *)hz;
  err:
    Py_XDECREF(hz);
    return 0;
    
}

typedef struct {
    NyHorizonObject *rg;
    NyNodeSetObject *result;
} NewsTravArg;


static int
horizon_news_trav(PyObject *obj, NewsTravArg *ta)
{
    if (!(NyNodeSet_hasobj(ta->rg->hs, obj)))
      if (NyNodeSet_setobj(ta->result, obj) == -1)
	return -1;
    return 0;
}

static char news_doc[] =
"H.news(X:iterable) -> NodeSet\n"
"\n"
"Return the set of objects in X that is not in the set of objects of H.\n"
"\n"
"If H was created from the contents of the heap at a particular time,\n"
"H.news(X) will return the set of objects in X that were allocated\n"
"after H was created.\n"
;


static PyObject *
horizon_news(NyHorizonObject *self, PyObject *arg)
{
    NewsTravArg ta;
    ta.rg = self;
    ta.result = NyMutNodeSet_New();
    if (!(ta.result))
      goto err;
    if (iterable_iterate(arg, (visitproc)horizon_news_trav, &ta) == -1)
      goto err;
    return (PyObject *)ta.result;
  err:
    Py_XDECREF(ta.result);
    return 0;
}


static PyMethodDef horizon_methods[] = {
	{"news", (PyCFunction)horizon_news, METH_O, news_doc},
	{NULL,		NULL}		/* sentinel */
};

PyTypeObject NyHorizon_Type = {
	PyObject_HEAD_INIT(0)
	0,					/* ob_size */
	"guppy.heapy.heapyc.Horizon",		/* tp_name */
	sizeof(NyHorizonObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)horizon_dealloc, 		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	(hashfunc)0,				/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,			/* tp_flags */
 	horizon_doc,				/* tp_doc */
 	0,					/* tp_traverse */
 	0,					/* tp_clear */
	(richcmpfunc)0,				/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)0,				/* tp_iter */
	0,					/* tp_iternext */
	horizon_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)0,				/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	horizon_new,				/* tp_new */
	_PyObject_Del,				/* tp_free */

};



