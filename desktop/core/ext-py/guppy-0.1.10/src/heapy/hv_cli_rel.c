/* Classify by 'relation', incoming (perhaps outcoming)

    inrel
    outrel
*/

PyDoc_STRVAR(hv_cli_inrel_doc, 

"HV.cli_inrel(referrers, memo) -> ObjectClassifier\n"
"\n"
"Return a classifier that classifes by \"incoming relations\".\n"
"\n"
"The classification of an object is the set of incoming relations.\n"
"\n"
"    referrers   A NodeGraph object used to\n"
"                map each object to its referrers.\n"
"\n"
"    memo        A dict object used to\n"
"                memoize the classification sets.\n"
);

PyDoc_STRVAR(rel_doc,
"");

static void
rel_dealloc(NyRelationObject *op)
{
    PyObject_GC_UnTrack(op);
    Py_TRASHCAN_SAFE_BEGIN(op)
    Py_XDECREF(op->relator);
    op->ob_type->tp_free(op);
    Py_TRASHCAN_SAFE_END(op)
}

PyObject *
NyRelation_SubTypeNew(PyTypeObject *type, int kind, PyObject *relator)
{
    NyRelationObject *rel = (NyRelationObject *)type->tp_alloc(type, 1);
    if (!rel)
      return 0;
    rel->kind = kind;
    if (!relator) {
	relator = Py_None;
    }
    rel->relator = relator;
    Py_INCREF(relator);
    return (PyObject *)rel;
}

NyRelationObject *
NyRelation_New(int kind, PyObject *relator)
{
    return (NyRelationObject *)NyRelation_SubTypeNew(&NyRelation_Type, kind, relator);
}

static PyObject *
rel_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    int kind;
    PyObject *relator;
    static char *kwlist[] = {"kind", "relator", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "iO:rel_new",kwlist,
				     &kind,
				     &relator))
      return NULL;
    if (! (0 < kind && kind < NYHR_LIMIT) ) {
	PyErr_Format(PyExc_ValueError,
		     "rel_new: Invalid relation kind: %d, must be > 0 and < %d.",
		     kind,
		     NYHR_LIMIT);
	return 0;
    }
    return NyRelation_SubTypeNew(type, kind, relator);
}


static int
rel_traverse(NyRelationObject *op, visitproc visit, void *arg)
{
    if (op->relator)
      return visit(op->relator, arg);
    return 0;
}

static int
rel_clear(NyRelationObject *op)
{
    Py_XDECREF(op->relator);
    op->relator = NULL;
    return 0;
}

static long
rel_hash(NyRelationObject *op)
{
    long x = PyObject_Hash(op->relator);
    if (x == -1)
      return -1;
    x ^= op->kind;
    if (x == -1)
      x = -2;
    return x;
}

static PyObject *
rel_richcompare(PyObject *v, PyObject *w, int op)
{
    NyRelationObject *vr, *wr;
    int vkind, wkind;
    if (! (NyRelation_Check(v) && NyRelation_Check(w))) {
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
    vr = (NyRelationObject *)v;
    wr = (NyRelationObject *)w;
    vkind = vr->kind;
    wkind = wr->kind;
    if (vkind != wkind) {
	PyObject *result;
	int cmp;
	switch (op) {
	  case Py_LT: cmp = vkind <  wkind; break;
	  case Py_LE: cmp = vkind <= wkind; break;
	  case Py_EQ: cmp = vkind == wkind; break;
	  case Py_NE: cmp = vkind != wkind; break;
	  case Py_GT: cmp = vkind >  wkind; break;
	  case Py_GE: cmp = vkind >= wkind; break;
	  default: return NULL; /* cannot happen */
	}
	result = cmp? Py_True:Py_False;
	Py_INCREF(result);
	return result;
    }
    return PyObject_RichCompare(vr->relator, wr->relator, op);
}
	
	    

static PyMethodDef rel_methods[] = {
    {NULL,		NULL}		/* sentinel */
};

#define OFF(x) offsetof(NyRelationObject, x)

static PyMemberDef rel_members[] = {
    {"kind", T_INT, OFF(kind), READONLY},
    {"relator", T_OBJECT, OFF(relator), READONLY},
    {NULL}  /* Sentinel */
};

#undef OFF

PyTypeObject NyRelation_Type = {
	PyObject_HEAD_INIT(NULL)
	0,
	"guppy.heapy.heapyc.Relation",		/* tp_name */
	sizeof(NyRelationObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	(destructor)rel_dealloc, 		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	(cmpfunc)0,				/* tp_compare */
	(reprfunc)0,				/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	(hashfunc)rel_hash,			/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,/* tp_flags */
 	rel_doc,				/* tp_doc */
 	(traverseproc)rel_traverse,		/* tp_traverse */
	(inquiry)rel_clear,			/* tp_clear */
	rel_richcompare,			/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)0,				/* tp_iter */
	0,					/* tp_iternext */
	rel_methods,				/* tp_methods */
	rel_members,				/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)0,				/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	rel_new,				/* tp_new */
	_PyObject_GC_Del,			/* tp_free */

};





typedef struct {
    /* Mimics a tuple - xxx should perhaps make a proper object/use tuple macros?! */
    PyObject_VAR_HEAD
    NyHeapViewObject *hv;
    NyNodeGraphObject *rg;
    NyRelationObject *rel;
    PyObject *memokind, *memorel;
} InRelObject;

typedef struct {
    PyObject *memorel;
    NyNodeSetObject *ns;
} MemoRelArg;

static int
inrel_visit_memoize_relation(PyObject *obj, MemoRelArg *arg)
{
    PyObject *mrel;
    if (!NyRelation_Check(obj)) {
	PyErr_Format(PyExc_TypeError,
	       "inrel_visit_memoize_relation: can only memoize relation (not \"%.200s\")",
	       obj->ob_type->tp_name);
	return -1;
    }
    mrel = PyDict_GetItem(arg->memorel, obj);
    if (!mrel) {
	if (PyErr_Occurred())
	  return -1;
	if (PyDict_SetItem(arg->memorel, obj, obj) == -1)
	  return -1;
	mrel = obj;
    }
    if (NyNodeSet_setobj(arg->ns, mrel) == -1)
      return -1;
    return 0;
}

static PyObject *
inrel_fast_memoized_kind(InRelObject * self, PyObject *kind)
     /* When the elements are already memoized */
{
    PyObject *result = PyDict_GetItem(self->memokind, kind);
    if (!result) {
	if (PyErr_Occurred())
	  goto Err;
	if (PyDict_SetItem(self->memokind, kind, kind) == -1)
	  goto Err;
	result = kind;
    }
    Py_INCREF(result);
    return result;
  Err:
    return 0;
}


static PyObject *
hv_cli_inrel_memoized_kind(InRelObject * self, PyObject *kind)
{
    MemoRelArg arg;
    PyObject *result;
    arg.memorel = self->memorel;
    arg.ns = hv_mutnodeset_new(self->hv);
    if (!arg.ns)
      return 0;
    if (iterable_iterate(kind, (visitproc)inrel_visit_memoize_relation, &arg) == -1)
      goto Err;
    if (NyNodeSet_be_immutable(&arg.ns) == -1)
      goto Err;
    result = inrel_fast_memoized_kind(self, (PyObject *)arg.ns);
  Ret:
    Py_DECREF(arg.ns);
    return result;
  Err:
    result = 0;
    goto Ret;
}

typedef struct {
    NyHeapRelate hr;
    int err;
    NyNodeSetObject *relset;
    NyRelationObject *rel;
    PyObject *memorel;
} hv_cli_inrel_visit_arg;

static int
hv_cli_inrel_visit(unsigned int kind, PyObject *relator, NyHeapRelate *arg_)
{
    hv_cli_inrel_visit_arg *arg = (void *)arg_;
    PyObject *rel;
    arg->err = -1;

    if (!relator) {
	if (PyErr_Occurred())
	  return -1;
	relator = Py_None;
	Py_INCREF(relator);
    }

    arg->rel->kind = kind;
    arg->rel->relator = relator;

    rel = PyDict_GetItem(arg->memorel, (PyObject *)arg->rel);
    if (!rel) {
	rel = (PyObject *)NyRelation_New(kind, relator);
	if (!rel)
	  goto ret;
	if (PyDict_SetItem(arg->memorel, rel, rel) == -1) {
	    Py_DECREF(rel);
	    goto ret;
	}
	Py_DECREF(rel);
    }
    if (NyNodeSet_setobj(arg->relset, rel) != -1)
      arg->err = 0;
  ret:
    Py_DECREF(relator);
    return arg->err;
}



static PyObject *
hv_cli_inrel_classify(InRelObject * self, PyObject *obj)
{
    NyNodeGraphEdge *lo, *hi, *cur;
    PyObject *result;
    ExtraType *xt;
    hv_cli_inrel_visit_arg crva;
    crva.hr.flags = 0;
    crva.hr.hv = (PyObject *)self->hv;
    crva.hr.tgt = obj;
    crva.hr.visit = hv_cli_inrel_visit;
    crva.err = 0;
    crva.memorel = self->memorel;
    assert(self->rel->relator == Py_None); /* This will be restored, w/o incref, at return. */
    crva.rel = self->rel;
    crva.relset = hv_mutnodeset_new(self->hv);
    if (!crva.relset)
      return 0;

    if (NyNodeGraph_Region(self->rg, obj, &lo, &hi) == -1) {
	goto Err;
    }

    for (cur = lo; cur < hi; cur++) {
	if (cur->tgt == Py_None)
	  continue;
	crva.hr.src = cur->tgt;
	xt = hv_extra_type(self->hv, crva.hr.src->ob_type);
	assert (xt->xt_hv == self->hv);
	assert(self->hv == (void *)crva.hr.hv);
	
	if (xt->xt_relate(xt, &crva.hr) == -1 || crva.err) {
	    /* fprintf(stderr, "xt 0x%x\n", xt); */
	    goto Err;
	}
    }

    if (NyNodeSet_be_immutable(&crva.relset) == -1)
      goto Err;
    result = inrel_fast_memoized_kind(self, (PyObject *)crva.relset);
  Ret:
    Py_DECREF(crva.relset);
    self->rel->relator = Py_None;
    return result;
  Err:
    result = 0;
    goto Ret;

}


static int
hv_cli_inrel_le(PyObject * self, PyObject *a, PyObject *b)
{
    return PyObject_RichCompareBool(a, b, Py_LE);
}


static NyObjectClassifierDef hv_cli_inrel_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "hv_cli_rcs",
    "classifier returning ...",
    (binaryfunc)hv_cli_inrel_classify,
    (binaryfunc)hv_cli_inrel_memoized_kind,
    hv_cli_inrel_le
};


static PyObject *
hv_cli_inrel(NyHeapViewObject *hv, PyObject *args)
{
    PyObject *r;
    InRelObject *s, tmp;
    if (!PyArg_ParseTuple(args, "O!O!O!:cli_inrel", 
			  &NyNodeGraph_Type, &tmp.rg,
			  &PyDict_Type, &tmp.memokind,
			  &PyDict_Type, &tmp.memorel
			  )) {
	return NULL;
    }
    s = NYTUPLELIKE_NEW(InRelObject);
    if (!s)
      return 0;
    s->hv = hv;
    Py_INCREF(s->hv);
    s->rg = tmp.rg;
    Py_INCREF(s->rg);
    s->memokind = tmp.memokind;
    Py_INCREF(s->memokind);
    s->memorel = tmp.memorel;
    Py_INCREF(s->memorel);
    /* Init a relation object used for lookup, to save an allocation per relation. */
    s->rel = NyRelation_New(1, Py_None); /* kind & relator will be changed  */
    if (!s->rel) {
	Py_DECREF(s);
	return 0;
    }
    r = NyObjectClassifier_New((PyObject *)s, &hv_cli_inrel_def);
    Py_DECREF(s);
    return r;
}





