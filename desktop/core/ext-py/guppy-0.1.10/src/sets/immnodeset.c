/* Implementation of ImmNodeSet */

PyDoc_STRVAR(immnodeset_doc,
"ImmNodeSet([iterable])\n"
"\n"
"Return a new immutable nodeset with elements from iterable.\n"
"\n"
"An immutable nodeset inherits the operations defined for NodeSet.\n"
"It also supports the following operation:\n"
"\n"
"hash(x)    -> int\n"
"\n"
"Return a hash value based on the addresses of the elements."
);


/* NyImmNodeSetIter methods */

static PyObject *nodeset_ior(NyNodeSetObject *v, PyObject *w);

typedef struct {
	PyObject_HEAD
	int i;
	NyNodeSetObject *nodeset; /* Need to hold on to this 'cause it shouldn't decref
				     objects in set*/
} NyImmNodeSetIterObject;


static void
immnsiter_dealloc(NyImmNodeSetIterObject *it)
{
    _PyObject_GC_UNTRACK(it);
    Py_TRASHCAN_SAFE_BEGIN(it)
      Py_XDECREF(it->nodeset);
      PyObject_GC_Del(it);
    Py_TRASHCAN_SAFE_END(it)
}

static PyObject *
immnsiter_getiter(PyObject *it)
{
	Py_INCREF(it);
	return it;
}

static int
immnsiter_traverse(NyImmNodeSetIterObject *it, visitproc visit, void *arg)
{
	if (it->nodeset == NULL)
		return 0;
	return visit((PyObject *)it->nodeset, arg);
}



static PyObject *
immnsiter_iternext(NyImmNodeSetIterObject *it)
{
    if (it->nodeset && it->i < it->nodeset->ob_size) {
	PyObject *ret = it->nodeset->u.nodes[it->i];
	it->i += 1;
	Py_INCREF(ret);
	return ret;
    } else {
	Py_XDECREF(it->nodeset);
	it->nodeset = NULL;
	return NULL;
    }
}

PyTypeObject NyImmNodeSetIter_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"immnodeset-iterator",			/* tp_name */
	sizeof(NyImmNodeSetIterObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)immnsiter_dealloc, 		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,/* tp_flags */
 	0,					/* tp_doc */
 	(traverseproc)immnsiter_traverse,	/* tp_traverse */
 	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)immnsiter_getiter,		/* tp_iter */
	(iternextfunc)immnsiter_iternext,	/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
};




/* immnodeset specific methods */


NyNodeSetObject *
NyImmNodeSet_SubtypeNew(PyTypeObject *type, int size, PyObject *hiding_tag)
{
    NyNodeSetObject *v = (void *)type->tp_alloc(type, size);
    if (!v)
      return NULL;
    v->flags = NS_HOLDOBJECTS;
    v->_hiding_tag_ = hiding_tag;
    Py_XINCREF(hiding_tag);
    memset(v->u.nodes, 0, sizeof(*v->u.nodes) * size);
    return v;
}

NyNodeSetObject *
NyImmNodeSet_New(int size, PyObject *hiding_tag)
{
    return NyImmNodeSet_SubtypeNew(&NyImmNodeSet_Type, size, hiding_tag);
}


NyNodeSetObject *
NyImmNodeSet_NewSingleton(PyObject *element, PyObject *hiding_tag)
{
    NyNodeSetObject *s = NyImmNodeSet_New(1, hiding_tag);
    if (!s)
      return 0;
    s->u.nodes[0] = element;
    Py_INCREF(element);
    return s;
}     


typedef struct {
    NyNodeSetObject *ns;
    int i;
} NSISetArg;

static int
as_immutable_visit(PyObject *obj, NSISetArg *v)
{
    v->ns->u.nodes[v->i] = obj;
    Py_INCREF(obj);
    v->i += 1;
    return 0;
}

NyNodeSetObject *
NyImmNodeSet_SubtypeNewCopy(PyTypeObject *type, NyNodeSetObject *v)
{
    NSISetArg sa;
    sa.i = 0;
    sa.ns = NyImmNodeSet_SubtypeNew(type, v->ob_size, v->_hiding_tag_);
    if (!sa.ns)
      return 0;
    NyNodeSet_iterate(v, (visitproc)as_immutable_visit, &sa);
    return sa.ns;
}

NyNodeSetObject *
NyImmNodeSet_NewCopy(NyNodeSetObject *v)
{
    return NyImmNodeSet_SubtypeNewCopy(&NyImmNodeSet_Type, v);
}


NyNodeSetObject *
NyImmNodeSet_SubtypeNewIterable(PyTypeObject *type, PyObject *iterable, PyObject *hiding_tag)
{
    NyNodeSetObject *imms, *muts;
    muts = NyMutNodeSet_SubtypeNewIterable(&NyMutNodeSet_Type, iterable, hiding_tag);
    if (!muts)
      return 0;
    imms = NyImmNodeSet_SubtypeNewCopy(type, muts);
    Py_DECREF(muts);
    return imms;
}

int
NyNodeSet_be_immutable(NyNodeSetObject **nsp) {
    NyNodeSetObject *cp = NyImmNodeSet_NewCopy(*nsp);
    if (!cp)
      return -1;
    Py_DECREF(*nsp);
    *nsp = cp;
    return 0;
}


static PyObject *
immnodeset_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{

    PyObject *iterable = NULL;
    PyObject *hiding_tag = NULL;
    static char *kwlist[] = {"iterable", "hiding_tag", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OO:ImmNodeSet.__new__",kwlist,
				     &iterable,
				     &hiding_tag
				     ))
      return 0;
    if (type == &NyImmNodeSet_Type &&
	iterable &&
	iterable->ob_type == &NyImmNodeSet_Type &&
	((NyNodeSetObject *)iterable)->_hiding_tag_ == hiding_tag) {
	Py_INCREF(iterable);
	return iterable;
    }
    return (PyObject *)NyImmNodeSet_SubtypeNewIterable(type, iterable, hiding_tag);
}


static int
immnodeset_gc_clear(NyNodeSetObject *v)
{
    if (v->_hiding_tag_) {
	PyObject *x = v->_hiding_tag_;
	v->_hiding_tag_ = 0;
	Py_DECREF(x);
    }
    if (v->flags & NS_HOLDOBJECTS) {
	int i;
	for (i = 0; i < v->ob_size; i++) {
	    PyObject *x = v->u.nodes[i];
	    if (x) {
		v->u.nodes[i] = 0;
		Py_DECREF(x);
	    }
	}
    }
    return 0;
}

static void
immnodeset_dealloc(NyNodeSetObject *v)
{
    _PyObject_GC_UNTRACK(v);
    Py_TRASHCAN_SAFE_BEGIN(v)
    immnodeset_gc_clear(v);
    v->ob_type->tp_free((PyObject *)v);
    Py_TRASHCAN_SAFE_END(v)
}



static int
immnodeset_gc_traverse(NyNodeSetObject *v, visitproc visit, void *arg)
{
    int i, err;
    err = 0;
    if (v->flags & NS_HOLDOBJECTS) {
	for (i = 0; i < v->ob_size; i++) {
	    PyObject *x = v->u.nodes[i];
	    if (x) {
		err = visit(x, arg);
		if (err)
		  return err;
	    }
	}
    }
    if (v->_hiding_tag_) {
	err = visit(v->_hiding_tag_, arg);
    }
    return err;
}

static long
immnodeset_hash(NyNodeSetObject *v)
{
    int i;
    long x = 0x983714;
    for (i = 0; i < v->ob_size; i++)
      x ^= (long)v->u.nodes[i];
    if (x == -1)
      x = -2;
    return x;
}

#define OFF(x) offsetof(NyNodeSetObject, x)

static PyMemberDef immnodeset_members[] = {
    {"_hiding_tag_",	 T_OBJECT_EX, OFF(_hiding_tag_), READONLY},
    {NULL} /* Sentinel */
};

#undef OFF

static  PyGetSetDef immnodeset_getset[] = {
    {"is_immutable", (getter)nodeset_get_is_immutable, (setter)0,
"S.is_immutable == True\n"
"\n"
"True since S is immutable."},
  {0}

};

static PyObject *
immnodeset_iter(NyNodeSetObject *ns)
{
    NyImmNodeSetIterObject *it = PyObject_GC_New(NyImmNodeSetIterObject, &NyImmNodeSetIter_Type);
    if (!it)
      return 0;
    it->i = 0;
    it->nodeset = ns;
    Py_INCREF(ns);
    PyObject_GC_Track(it);
    return (PyObject *)it;
}

static NyNodeSetObject *
immnodeset_op(NyNodeSetObject *v, NyNodeSetObject *w, int op)
{
    int z;
    PyObject *pos;
    int bits, a, b;
    NyNodeSetObject *dst = 0;
    PyObject **zf, **vf, **wf, **ve, **we;
    ve = &v->u.nodes[v->ob_size];
    we = &w->u.nodes[w->ob_size];
    for (z = 0, zf = 0; ;) {
	for (vf = &v->u.nodes[0], wf = &w->u.nodes[0];;) {
	    if (vf < ve) {
		if (wf < we) {
		    if (*vf <= *wf) {
			pos = *vf;
			a = 1;
			if (*vf == *wf) {
			    b = 1;
			    wf++;
			} else {
			    b = 0;
			}
			vf++;
		    } else {		/* (*vf > *wf) { */
			pos = *wf;
			a = 0;
			b = 1;
			wf++;
		    }
		} else {
		    pos = *vf;
		    a = 1;
		    vf++;
		    b = 0;
		}
	    } else if (wf < we) { 
		pos = *wf;
		a = 0;
		b = 1;
		wf++;
	    } else
	      break;
	    switch(op) {
	      case NyBits_AND:		bits = a & b;		break;
	      case NyBits_OR:		bits = a | b;		break;
	      case NyBits_XOR:		bits = a ^ b;		break;
	      case NyBits_SUB:		bits = a & ~b;		break;
	      default:			bits = 0;	/* slicence undefined-warning */
					assert(0);
	    }
	    if (bits) {
		if (zf) {
		    *zf = pos;
		    Py_INCREF(pos);
		    zf++;
		} else {
		    z++;
		}
	    }
	}
	if (zf) {
	    return dst;
	} else {
	    dst = NyImmNodeSet_New(z, v->_hiding_tag_);
	    if (!dst)
	      return dst;
	    zf = &dst->u.nodes[0];
	}
    }



}

PyDoc_STRVAR(immnodeset_obj_at_doc,
"x.obj_at(address)\n"
"Return the object in x that is at a specified address, if any,\n"
"otherwise raise ValueError"
);	     


static PyObject *
immnodeset_obj_at(NyNodeSetObject *v, PyObject *obj)
{
    PyObject **lo;
    PyObject **hi;

    Py_uintptr_t addr =
#if SIZEOF_VOID_P <= SIZEOF_LONG
	PyInt_AsUnsignedLongMask(obj);
#else
        PyInt_AsUnsignedLongLongMask(obj);
#endif
    if (addr == (Py_uintptr_t) -1 && PyErr_Occurred())
	return 0;
    
    lo = &v->u.nodes[0];
    hi = &v->u.nodes[v->ob_size];
    while (lo < hi) {
	PyObject **cur = lo + (hi - lo) / 2;
	if ((Py_uintptr_t)(*cur) == addr) {
	    Py_INCREF(*cur);
	    return *cur;
	}
	else if ((Py_uintptr_t)*cur < addr)
	    lo = cur + 1;
	else
	    hi = cur;
    }
    PyErr_Format(PyExc_ValueError, "No object found at address %p\n",(void *)addr);
    return 0;
}


static PyMethodDef immnodeset_methods[] = {
	{"obj_at",	(PyCFunction)immnodeset_obj_at, METH_O, immnodeset_obj_at_doc},
	{NULL,		NULL}		/* sentinel */
};

  

PyTypeObject NyImmNodeSet_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.sets.setsc.ImmNodeSet",		/* tp_name */
	sizeof(NyNodeSetObject)-sizeof(PyObject *),/* tp_basicsize */
	sizeof(PyObject *),			/* tp_itemsize */
	/* methods */
	(destructor)immnodeset_dealloc,		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	(hashfunc)immnodeset_hash,		/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_CHECKTYPES |
		Py_TPFLAGS_BASETYPE,		/* tp_flags */
 	immnodeset_doc,				/* tp_doc */
 	(traverseproc)immnodeset_gc_traverse,	/* tp_traverse */
 	(inquiry)immnodeset_gc_clear,		/* tp_clear */
	(richcmpfunc)nodeset_richcompare,	/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)immnodeset_iter,		/* tp_iter */
	0,					/* tp_iternext */
	immnodeset_methods,			/* tp_methods */
	immnodeset_members,			/* tp_members */
	immnodeset_getset,			/* tp_getset */
	&NyNodeSet_Type,			/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	immnodeset_new,				/* tp_new */
	_PyObject_GC_Del,			/* tp_free */

};


