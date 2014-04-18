/* Implementation of the HeapView type */

PyDoc_STRVAR(hv_doc,
"HeapView(root, heapdefs:tuple)\n"
"\n"
"Create a new HeapView object with arguments:\n"
"\n"
"    root        The initial value of the root member.\n"
"    heapdefs    Definitions of specially treated extension types.\n"
"\n"
"A HeapView object provides methods to get memory related information\n"
"about the system heap and about individual objects. \n"
"\n"
"It implements much of the low-level functionality for the Heapy\n"
"system. It is intended to provide what can not be done at all or would\n"
"be much slower if programmed directly in Python. It is not intended to\n"
"be used directly by a user, but to be wrapped in higher level objects.\n"
"\n"
"Some terms that are referred to in the method descriptions:\n"
"\n"
"Visible objects.\n"
"\n"
"The HeapView object attempts to restrict its view of the heap to only\n"
"the 'visible objects'. This is to make it possible to analyse the heap\n"
"via a Python library that inevitably itself is continually allocating\n"
"and deallocating objects. These should be hidden from the heap view\n"
"presented. This is primarily done via a special tag attribute, see\n"
"'_hiding_tag_' and 'register__hiding_tag__type'. Frames can be hidden\n"
"with another mechanism, see 'limitframe'. For hiding all objects of a\n"
"special type, 'register_hidden_exact_type' may be used. It is also\n"
"possible to use a separate interpreter and hide its root objects, see\n"
"'is_hiding_calling_interpreter'.\n"
"\n"
"Classifiers.\n"
"\n"
"The methods named cli_* are factory methods that create objects of\n"
"type ObjectClassifier. The principal difference between classifiers is\n"
"how a single object is classified. The single-object classification\n"
"function is available in classifier objects; it is the classify\n"
"method. There are also methods that operate on collections of objects,\n"
"namely partition and select. These eliminate the per-object\n"
"Python-level function call overhead that would occur if the classify\n"
"method were to be called from Python for each object in a collection.\n"
"See also the ObjectClassifier type.\n"
"\n"
"Individual size.\n"
"\n"
"The individual size of an object is its individually allocated memory size. \n"
"\n"
"It includes:\n"
"\n"
"o The basic object size, as can be found out in a standard way.\n"
"o The extra memory for variable size objects.\n"
"o For GC collected objects, the size of the GC information.\n"
"o An alignment to the next highest multiple of a pointer size.\n"
"o The size of any other memory allocated that belongs to the object.\n"
"\n"
"Some types of objects have extra memory allocated that can not be\n"
"accounted for in the standard way. This memory should nevertheless be\n"
"included in the individual size. To determine the size of these\n"
"objects, special functions are needed. These are defined for standard\n"
"builtin types, such as lists and dicts. Other types should be defined\n"
"via the heapdefs argument to the HeapView constructor.\n"
"\n"
"The individual size does not include:\n"
"\n"
"o Subobjects that are accounted for separately.\n"
"o Overhead for the memory allocation system. This varies depending\n"
"  on the kind of memory allocator, the requested size, etc.\n"
);




#define ALIGN  sizeof(void *)
#define ALIGN_MASK (ALIGN - 1)

#define XT_SIZE 1024
#define XT_MASK (XT_SIZE-1)

/* Forward declarations */

static PyObject *hv_heap(NyHeapViewObject *self, PyObject *args, PyObject *kwds);
PyObject **hv_cli_dictof_dictptr(PyObject *obj);

static ExtraType *hv_new_extra_type(NyHeapViewObject *hv, PyTypeObject *type);

int cli_cmp_as_int(PyObject *cmp);

/* HeapView methods */

static int
hv_gc_traverse(NyHeapViewObject *hv, visitproc visit, void *arg)
{
    int err;
    VISIT(hv->root);
    VISIT(hv->limitframe);
    VISIT(hv->static_types);
    VISIT(hv->weak_type_callback);

    if (hv->xt_table) {
	int i;
	for (i = 0; i < hv->xt_size; i++) {
	    ExtraType *xt;
	    for (xt = hv->xt_table[i]; xt; xt = xt->xt_next) {
		VISIT(xt->xt_weak_type);
	    }
	}
    }
    return 0;
}


void
xt_free_table(ExtraType **xt_table, int size)
{
    int i;
    if (!xt_table)
      return;
    for (i = 0; i < size; i++) {
	ExtraType *xt = xt_table[i];
	while (xt) {
	    ExtraType *xt_next = xt->xt_next;
	    Py_DECREF(xt->xt_weak_type);
	    PyMem_Del(xt);
	    xt = xt_next;
	}
    }
    PyMem_Del(xt_table);
}

static int
hv_gc_clear(NyHeapViewObject *hv)
{
    /* xxx Paranoid, clumsy, but recursion-safe variant? */
    PyObject *ro = hv->root;
    PyObject *lf = hv->limitframe;
    PyObject *he = hv->_hiding_tag_;
    PyObject *stob = hv->static_types;
    PyObject *wtc = hv->weak_type_callback;
    void *xt = hv->xt_table;

    hv->root = 0;
    hv->limitframe = 0;
    hv->_hiding_tag_ = 0;
    hv->static_types = 0;
    hv->weak_type_callback = 0;
    hv->xt_table = 0;

    xt_free_table(xt, hv->xt_size);


    Py_XDECREF(ro);
    Py_XDECREF(lf);

    Py_XDECREF(he);
    Py_XDECREF(stob);
    Py_XDECREF(wtc);
    return 0;
}

static int
hv_default_size(PyObject *obj)
{
    int z = obj->ob_type->tp_basicsize;
    if (obj->ob_type->tp_itemsize) {
	int itemsize = obj->ob_type->tp_itemsize;
	if (itemsize < 0)
	  itemsize = - itemsize; /* For (e.g.) long(Should we check? */
	z += ((PyVarObject *)obj)->ob_size * itemsize;
	z = (z + ALIGN_MASK) & ~ALIGN_MASK;
    }
    if (PyObject_IS_GC(obj))
      z += sizeof(PyGC_Head);
    return z;
}

static int
owht_relate(NyHeapRelate *r, PyTypeObject *type)
{
    PyObject *v = r->src;
    PyMemberDef *mp = type->tp_members;
    if (mp) {
	while (mp->name) {
	    if ((mp->type == T_OBJECT_EX || mp->type == T_OBJECT) &&
		*((PyObject **)((char *)v+mp->offset)) == r->tgt) {
		if (r->visit(NYHR_ATTRIBUTE, PyString_FromString(mp->name), r))
		  return 1;
	    }
	    mp++;
	}
    }
    return 0;
}


PyObject *
hv_default_classify(PyObject *obj)
{
    PyObject *c;
    if (PyInstance_Check(obj)) {
	c = (PyObject *)((PyInstanceObject *)obj)->in_class;
    } else {
	c = (PyObject *)obj->ob_type;
    }
    Py_INCREF(c);
    return c;
}

static NyHeapDef default_hd = {
    0,			/* flags */
    0,			/* type */
    hv_default_size,	/* size */
    0,			/* traverse */
    0,			/* relate */
};



static int
xt_error_size(PyObject *obj)
{
    return -1;
}

static int
xt_default_relate(struct ExtraType *xt, NyHeapRelate *r)
{
    PyTypeObject *type = xt->xt_type;
    PyObject **dictptr;
    if (owht_relate(r, type))
      return 1;
    /* dictptr = _PyObject_GetDictPtr(r->src); */ 
    dictptr = hv_cli_dictof_dictptr(r->src);	/* I think this is better xxx verify? Apr 13 2005 */
    if (dictptr) {
	if (*dictptr == r->tgt) {
	    if (r->visit(NYHR_ATTRIBUTE, PyString_FromString("__dict__"), r))
	      return 1;
	}
	if (dict_relate_kv(r, *dictptr, NYHR_HASATTR, NYHR_ATTRIBUTE)) {
	    return 1;
	}
    }
    return 0;
}

static int
xt_hd_relate(struct ExtraType *xt, NyHeapRelate *r)
{
    return xt->xt_hd->relate(r);
}

static int
xt_inherited_relate(struct ExtraType *xt, NyHeapRelate *r)
{
    if (owht_relate(r, xt->xt_type))
      return 1;
    return xt->xt_base->xt_relate(xt->xt_base, r);
}

static int
xt_error_relate(struct ExtraType *xt, NyHeapRelate *r)
{
    return -1;
}

static int
xt_error_traverse(struct ExtraType *xt, PyObject *obj, visitproc visit, void *arg)
{
    return -1;
}

static int
xt_no_traverse(struct ExtraType *xt, PyObject *obj, visitproc visit, void *arg)
{
    return 0;
}


static int
xt_tp_traverse(struct ExtraType *xt, PyObject *obj, visitproc visit, void *arg)
{
    return obj->ob_type->tp_traverse(obj, visit, arg);
}


static int
xt_hd_traverse(struct ExtraType *xt, PyObject *obj, visitproc visit, void *arg)
{
    NyHeapTraverse ta;
    NyHeapViewObject *hv = (void *)xt->xt_hv;
    ta.flags = 0;
    ta.obj = obj;
    ta.visit = visit;
    ta.arg = arg;
    ta._hiding_tag_ = hv->_hiding_tag_;
    ta.hv = (PyObject *)hv;
    return xt->xt_hd->traverse(&ta);
}

static int
xt_he_traverse(struct ExtraType *xt, PyObject *obj, visitproc visit, void *arg)
{
    long offs = xt->xt_he_offs;
    NyHeapViewObject *hv = (void *)xt->xt_hv;
    PyObject **phe = (PyObject **)((char *)obj + offs);
    if (*phe == hv->_hiding_tag_) {
	return 0;
    }
    return xt->xt_he_traverse(xt, obj, visit, arg);
}


static ExtraType xt_error = {
    0,				/* xt_type */
    xt_error_size,		/* xt_size */
    xt_error_traverse,		/* xt_traverse */
    xt_error_relate,		/* xt_relate */

};

#define XT_ERROR	0
#define XT_HE 		1
#define XT_TP 		2
#define XT_NO 		3
#define XT_HD 		4
#define XT_HI 		5

#define XT_HASH(hv, type)	(((Py_uintptr_t)type >> 4) & XT_MASK)

void
xt_findout_size(ExtraType *xt)
{
    if (xt->xt_hd->size)
      xt->xt_size = xt->xt_hd->size;
    else
      xt->xt_size = hv_default_size;
	  
}

void
xt_findout_traverse(ExtraType *xt)
{
    if (xt->xt_hd->traverse) {
	xt->xt_traverse = xt_hd_traverse;
	xt->xt_trav_code = XT_HD;
	return;
    } else if (xt->xt_type->tp_traverse) {
	xt->xt_traverse = xt_tp_traverse;
	xt->xt_trav_code = XT_TP;
	return;
    } else {
	xt->xt_traverse = xt_no_traverse;
	xt->xt_trav_code = XT_NO;
	return;
    }
}

void
xt_findout_relate(ExtraType *xt)
{
    if (xt->xt_hd->relate)
      xt->xt_relate = xt_hd_relate;
    else
      xt->xt_relate = xt_default_relate;
}	  

static ExtraType *
hv_new_xt_for_type_at_xtp(NyHeapViewObject *hv, PyTypeObject *type, ExtraType **xtp)
{
    ExtraType *xt = PyMem_New(ExtraType, 1);
    if (!xt) {
	PyErr_NoMemory();
	return 0;
    }
    memset(xt, 0, sizeof(ExtraType));
    *xtp = xt;
    xt->xt_hv = (void *)hv;
    xt->xt_type = type;
    xt->xt_weak_type = PyWeakref_NewRef((PyObject *)type, hv->weak_type_callback);
    if (!xt->xt_weak_type) {
	PyMem_Del(xt);
	return 0;
    }
    return xt;
}

static ExtraType *
hv_new_xt_for_type(NyHeapViewObject *hv, PyTypeObject *type)
{
    int hash = XT_HASH(hv, type);
    ExtraType **xtp = &hv->xt_table[hash];
    ExtraType *xt;
    while ((xt = *xtp)) {
	if (xt->xt_type == type) {
	    PyErr_Format(PyExc_ValueError,
			 "Duplicate heap definition for type '%.50s'",
			 type->tp_name);
	    return 0;
	}
	xtp = &xt->xt_next;
    }
    return hv_new_xt_for_type_at_xtp(hv, type, xtp);

}

static void
xt_set_heapdef(ExtraType *xt, NyHeapDef *hd)
{
    xt->xt_hd = hd;
    xt_findout_traverse(xt);
    xt_findout_size(xt);
    xt_findout_relate(xt);
}

static ExtraType *
hv_extra_type(NyHeapViewObject *hv, PyTypeObject *type)
{
    int hash = XT_HASH(hv, type);
    ExtraType **xtp = &hv->xt_table[hash];
    ExtraType *xt;
#ifdef COUNT_COLL
    int i = 0;
#endif
    while ((xt = *xtp)) {
	if (xt->xt_type == type) {
#ifdef COUNT_COLL
	    if (i > maxcoll) {
		maxcoll = i;
		fprintf(stderr, "maxcoll %d\n", maxcoll);
	    }
#endif
	    return xt;
	}
	xtp = &xt->xt_next;
#ifdef COUNT_COLL
	i += 1;
#endif
    }
    xt = hv_new_extra_type(hv, type);
    if (!xt)
      xt = &xt_error;
    return xt;
}

static ExtraType *
hv_new_extra_type(NyHeapViewObject *hv, PyTypeObject *type)
{
    ExtraType *xt;
    if (!type->tp_base) {
	xt = hv_new_xt_for_type(hv, type);
	if (!xt)
	  return 0;
	xt_set_heapdef(xt, &default_hd);
    } else {
	ExtraType *base = hv_extra_type(hv, type->tp_base);
	if (base == &xt_error)
	  return 0;
	xt = hv_new_xt_for_type(hv, type);
	if (!xt)
	  return 0;
	xt->xt_base = base;
	xt->xt_hd = base->xt_hd;
	if (base->xt_trav_code == XT_HE) {
	    xt->xt_he_xt = base->xt_he_xt;
	    xt->xt_trav_code = base->xt_trav_code;
	    xt->xt_traverse = base->xt_traverse;
	    xt->xt_he_traverse = base->xt_he_traverse;
	    xt->xt_he_offs = base->xt_he_offs;
	} else {
	    xt_findout_traverse(xt); /* xxx ??? */
	}
	xt->xt_size = base->xt_size;
	xt->xt_relate = xt_inherited_relate;
    }
    return xt;
}

#ifdef COUNT_COLL

int maxcoll = 0;

#endif

static int
xt_relate(ExtraType *xt, NyHeapRelate *hr)
{
    PyTypeObject *type = hr->src->ob_type;
    if (PyType_Ready(type) == -1)
      return -1;
    if ((PyObject *)type == hr->tgt) {
/*	if (hr->visit(NYHR_RELSRC, PyString_FromString("type(%s)"), hr)) */
	if (hr->visit(NYHR_INTERATTR, PyString_FromString("ob_type"), hr))
	
	  return 0;
    }
    return xt->xt_relate(xt, hr);
}


static int
xt_size(ExtraType *xt, PyObject *obj)
{
    return xt->xt_size(obj);
}


static int
xt_traverse(ExtraType *xt, PyObject *obj, visitproc visit, void *arg)
{
    if (xt->xt_trav_code == XT_NO)
      return 0;
    else if (xt->xt_trav_code == XT_TP)
      return obj->ob_type->tp_traverse(obj, visit, arg);
    else
      return xt->xt_traverse(xt, obj, visit, arg);
}

NyNodeSetObject *
hv_mutnodeset_new(NyHeapViewObject *hv)
{
    return NyMutNodeSet_NewHiding(hv->_hiding_tag_);
}

static int
hv_std_size(NyHeapViewObject *hv, PyObject *obj)
{
    return xt_size(hv_extra_type(hv, obj->ob_type), obj);
}

static int
hv_std_relate(NyHeapRelate *hr)
{
    return xt_relate(hv_extra_type((NyHeapViewObject *)hr->hv, hr->src->ob_type), hr);
}


static int
hv_std_traverse(NyHeapViewObject *hv,
	     PyObject *obj, visitproc visit, void *arg)
{
    return xt_traverse(hv_extra_type(hv, obj->ob_type), obj, visit, arg);
}



static PyObject *
hv_std_classify(NyHeapViewObject *hv, PyObject *obj)
{
    return hv_default_classify(obj);
}

typedef struct {
    NyHeapViewObject *hv;
    NyNodeSetObject *ns;
    PyObject *rm;
} CMSTravArg;

int
hv_is_obj_hidden(NyHeapViewObject *hv, PyObject *obj) 
{
    PyTypeObject *type = obj->ob_type;
    ExtraType *xt = hv_extra_type(hv, type);
    if (xt->xt_trav_code == XT_HE) {
	long offs = xt->xt_he_offs;
	PyObject **phe = (PyObject **)((char *)obj + offs);
	if (*phe == hv->_hiding_tag_) {
	    return 1;
	}
    } else if (xt->xt_trav_code == XT_HI) {
	return 1;
    } else if (PyInstance_Check(obj)) {
	PyInstanceObject *in = (void *)obj;
	if (PyDict_GetItem(in->in_dict, _hiding_tag__name) == hv->_hiding_tag_) {
	    return 1;
	}
    } else if (type == &NyRootState_Type) {
	/* Fixes a dominos confusion; see Notes Apr 20 2005 */
	return 1;
    }
    return 0;
}


static int
hv_cms_rec(PyObject *obj, CMSTravArg *ta)
{
    if (hv_is_obj_hidden(ta->hv, obj)) {
	if (PyList_Append(ta->rm, obj) == -1)
	  return -1;
    }
    return 0;
}


static int
hv_cleanup_mutset(NyHeapViewObject *hv, NyNodeSetObject *ns)
{
    CMSTravArg ta;
    int ret = -1;
    long i, size;
    ta.hv = hv;
    ta.ns = ns;
    ta.rm = PyList_New(0);
    if (!ta.rm)
      goto err;
    if (NyNodeSet_iterate(ta.ns, (visitproc)hv_cms_rec, &ta) == -1)
      goto err;
    size = PyList_Size(ta.rm);
    for (i = 0; i < size; i++) {
	PyObject *obj = PyList_GET_ITEM(ta.rm, i);
	if (NyNodeSet_clrobj(ta.ns, obj) == -1)
	  goto err;
    }
    ret = 0;
  err:
    Py_XDECREF(ta.rm);
    return ret;
}

static int
hv_add_heapdef(NyHeapViewObject *hv, NyHeapDef *hd)
{
    ExtraType *xt = hv_new_xt_for_type(hv, hd->type);
    if (!xt)
      return -1;
    xt_set_heapdef(xt, hd);
    return 0;
}

static int
hv_add_heapdefs_array(NyHeapViewObject *hv, NyHeapDef *hd)
{
    while (hd->type) {
	if (hv_add_heapdef(hv, hd) == -1)
	  return -1;
	hd++;
    }
    return 0;
}

static int
hv_add_heapdefs_tuple(NyHeapViewObject *hv, PyTupleObject *heapdefs)
{
    int i;
    for (i = 0; i < PyTuple_Size((PyObject *)heapdefs); i++) {
	NyHeapDef *hd = PyCObject_AsVoidPtr(PyTuple_GetItem((PyObject *)heapdefs, i));
	if (!hd)
	  return -1;
	if (hv_add_heapdefs_array(hv, hd) == -1)
	  return -1;
    }
    return 0;
}



PyObject *
NyHeapView_SubTypeNew(PyTypeObject *type, PyObject *root, PyTupleObject *heapdefs)
{
    NyHeapViewObject *hv = (NyHeapViewObject *)type->tp_alloc(type, 1);
    int i;
    if (!hv)
      return 0;
    Py_INCREF(root);
    hv->root = root;
    hv->limitframe = 0;
    hv->_hiding_tag_ = Py_None;
    Py_INCREF(Py_None);
    hv->static_types = 0;
    hv->xt_size = XT_SIZE;
    hv->xt_mask = XT_MASK;
    hv->weak_type_callback = 0;
    hv->xt_table = 0;

    /* The HeapView object hv is now initialized to some well-defined state --
       but we have waited to try allocation till now when all
       allocated members have been set (to 0 etc) so
       that hv now may be correctly deallocated. */

    hv->weak_type_callback = PyObject_GetAttrString((PyObject *)hv, "delete_extra_type");
    if (!(hv->weak_type_callback))
      goto err;

    hv->xt_table = PyMem_New(ExtraType *, hv->xt_size);
    if (!hv->xt_table)
      goto err;
    for (i = 0; i < hv->xt_size; i++)
      hv->xt_table[i] = 0;

    hv->static_types = (PyObject *)NyMutNodeSet_New();
    if (!(hv->static_types))
      goto err;

    /* Add standard and user-defined heap definitions */

    if (hv_add_heapdefs_array(hv, NyStdTypes_HeapDef) == -1)
      goto err;
    if (hv_add_heapdefs_array(hv, NyHvTypes_HeapDef) == -1)
      goto err;
    if (hv_add_heapdefs_tuple(hv, heapdefs) == -1)
      goto err;
    return (PyObject *)hv;

  err:
    Py_DECREF(hv);
    return 0;
}

static PyObject *
hv_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *heapdefs = NULL;
    PyObject *root = NULL;
    static char *kwlist[] = {"root", "heapdefs", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO!:hv_new",kwlist,
				     &root,
				     &PyTuple_Type, &heapdefs))
      return NULL;
    return NyHeapView_SubTypeNew(type, root, (PyTupleObject *)heapdefs);
}

static void
hv_dealloc(PyObject *v)
{
    PyObject_GC_UnTrack(v);
    Py_TRASHCAN_SAFE_BEGIN(v)
    hv_gc_clear((NyHeapViewObject *)v);
    v->ob_type->tp_free(v);
    Py_TRASHCAN_SAFE_END(v)
}

PyDoc_STRVAR(hv_delete_extra_type_doc,
"HV.delete_extra_type(weakref)\n\
\n\
Delete extra type information. For internal use as a weak-ref callback.");

/* hv_delete_extra_type will be called by the weak type callback on its type.
   I don't consider it time critical, because it wouldnt happen too often..
   so make it simple, allow to take time in the order of the total number of
   (extra) types.

 */

static PyObject *
hv_delete_extra_type(NyHeapViewObject *hv, PyObject *wr)
{

    int i;

    if (!PyWeakref_Check(wr)) {
	PyErr_Format(PyExc_TypeError,
		     "delete_extra_type: argument must be a weak ref, got '%.50s'",
		     wr->ob_type->tp_name);
	return 0;
    }
    for (i = 0; i < hv->xt_size; i++) {
	ExtraType *xt, **xtp;
	for (xtp = &hv->xt_table[i]; (xt = *xtp); xtp = &xt->xt_next) {
	    if (xt->xt_weak_type == wr) {
		*xtp = xt->xt_next;
#if 0
		fprintf(stderr, "Deleted type at %p\n", xt->xt_type);
		fprintf(stderr, "Deleted type name %s\n", xt->xt_type->tp_name);
#endif
		PyMem_Del(xt);
		Py_DECREF(wr);
		Py_INCREF(Py_None);
		return Py_None;
	    }
	}
    }
    PyErr_Format(PyExc_ValueError,
		 "delete_extra_type: reference object %p not found",
		 wr);
    return 0;
}

#include "hv_cli.c"

typedef struct {
    NyHeapViewObject *hv;
    NyNodeSetObject *hs;
    PyObject *arg;
    int (*visit)(PyObject *, void *);
} IterTravArg;

static int
iter_rec(PyObject *obj, IterTravArg *ta) {
    int r;
    if (obj->ob_refcnt > 1) {
	r = NyNodeSet_setobj(ta->hs, obj);
	if (r) {
	    if (r == -1)
	      return -1;
	    else
	      return 0;
	}
    }
    r = ta->visit(obj, ta->arg);
    if (!r) {
	r = hv_std_traverse(ta->hv, obj, (visitproc)iter_rec, ta);
    }
    return r;
}

int
NyHeapView_iterate(NyHeapViewObject *hv, int (*visit)(PyObject *, void *),
		void *arg)
{
    IterTravArg ta;
    int r;
    ta.hv = hv;
    ta.visit = visit;
    ta.arg = arg;
    ta.hs = hv_mutnodeset_new(hv);
    if (!ta.hs) {
	return -1;
    }
    r = iter_rec(ta.hv->root, &ta);
    Py_DECREF(ta.hs);
    return r;
}

PyDoc_STRVAR(hv_heap_doc,
"HV.heap() -> NodeSet\n\
\n\
Return a set containing all 'visible objects' in the heap view\n\
defined by HV. See also HeapView.__doc__.");

typedef struct {
    NyHeapViewObject *hv;
    NyNodeSetObject *visited;
} HeapTravArg;

static int
hv_heap_rec(PyObject *obj, HeapTravArg *ta) {
    int r;
    r = NyNodeSet_setobj(ta->visited, obj);
    if (r)
      return r < 0 ? r: 0;
    else {
	return hv_std_traverse(ta->hv, obj, (visitproc)hv_heap_rec, ta);
    }

}

static int
hv_update_static_types_visitor(PyObject *obj, NyHeapViewObject *hv) {
    if (PyType_Check(obj) &&
	!(((PyTypeObject *)obj)->tp_flags & Py_TPFLAGS_HEAPTYPE))
      return NyNodeSet_setobj((NyNodeSetObject *)(hv->static_types), obj);
    return 0;
}

static int
hv_update_static_types(NyHeapViewObject *hv, PyObject *it)
{
    return iterable_iterate(it, (visitproc)hv_update_static_types_visitor, hv);
}


static PyObject *
hv_heap(NyHeapViewObject *self, PyObject *args, PyObject *kwds)
{
    HeapTravArg ta;
    ta.hv = self;
    ta.visited = hv_mutnodeset_new(self);
    if (!ta.visited)
      goto err;
    if (hv_heap_rec(ta.hv->root, &ta) == -1)
      goto err;
    if (hv_cleanup_mutset(ta.hv, ta.visited) == -1)
      goto err;
    if (PyObject_Length(self->static_types) == 0) {
	if (hv_update_static_types(self, (PyObject *)ta.visited) == -1)
	  goto err;
    }
    return (PyObject *)ta.visited;
  err:
    Py_XDECREF(ta.visited);
    return 0;
}


typedef struct {
    NyHeapViewObject *hv;
    long sum;
} SalArg;

static int
hv_indisize_sum_rec(PyObject *obj, SalArg *ta)
{
    ta->sum += hv_std_size(ta->hv, obj);
    return 0;
}

PyDoc_STRVAR(hv_indisize_sum_doc,
"HV.indisize_sum(S:iterable) -> int\n\
\n\
Return the sum of the 'individual size' of the objects in S.\n\
See also HeapView.__doc.");

static PyObject *
hv_indisize_sum(NyHeapViewObject *self, PyObject *arg)
{
    SalArg ta;
    ta.sum = 0;
    ta.hv = self;
    if (iterable_iterate(arg, (visitproc)hv_indisize_sum_rec, &ta) == -1)
      return 0;
    return PyInt_FromLong(ta.sum);
}



typedef struct {
    NyHeapRelate hr;
    int err;
    PyObject *relas[NYHR_LIMIT];
} hv_relate_visit_arg;

static int
hv_relate_visit(unsigned int relatype, PyObject *relator, NyHeapRelate *arg_)
{
    hv_relate_visit_arg *arg = (void *)arg_;
    arg->err = -1;
    if (!relator) {
	if (PyErr_Occurred())
	  return -1;
	relator = Py_None;
	Py_INCREF(relator);
    }
    if (relatype >= NYHR_LIMIT) {
	PyErr_SetString(PyExc_SystemError, "conf_relate_visit: invalid relation type");
	goto ret;
    }
    if (!arg->relas[relatype]) {
	if (!(arg->relas[relatype] = PyList_New(0)))
	  goto ret;
    }
    arg->err = PyList_Append(arg->relas[relatype], relator);
  ret:
    Py_DECREF(relator);
    return arg->err;
}

typedef struct {
    NyHeapRelate hr;
    long ne;
    int err;
}
NETravArg;

#define NETRAV 1

#if NETRAV
static int
hv_ne_rec(PyObject *obj, NETravArg *ta)
{
    if (obj == ta->hr.tgt)
      ta->ne++;
    return 0;
}
#endif

static int
hv_ne_visit(unsigned int relatype, PyObject *relator, NyHeapRelate *arg_)
{
    NETravArg *ta = (void *)arg_;
    Py_XDECREF(relator);
    ta->ne++;
    return ta->err;
}

PyDoc_STRVAR(hv_numedges_doc,
"HV.numedges(src, tgt) -> int\n\
\n\
Return the number of edges from src to tgt.");

static PyObject *
hv_numedges(NyHeapViewObject *self, PyObject *args)
{
    NETravArg ta;
    if (!PyArg_ParseTuple(args, "OO:numedges", &ta.hr.src, &ta.hr.tgt))
      return NULL;
    ta.hr.flags = 0;
    ta.hr.hv = (void *)self;
    ta.hr.visit = hv_ne_visit;
    ta.err = 0;
    ta.ne = 0;
#if NETRAV
    if (hv_std_traverse(self, ta.hr.src, (visitproc)hv_ne_rec, &ta) == -1)
#else
    if (hv_std_relate(&ta.hr) == -1 || ta.err)
#endif
      return 0;
    return PyInt_FromLong(ta.ne);
}

typedef struct {
    NyHeapViewObject *hv;
    NyNodeSetObject *start, *avoid;
    NyNodeSetObject *visited;
} RATravArg;

static int
hv_ra_rec(PyObject *obj, RATravArg *ta)
{
    int r;
    if (NyNodeSet_hasobj(ta->avoid, obj))
      return 0;
    r = NyNodeSet_setobj(ta->visited, obj);
    if (r)
      return r < 0 ? r: 0;
    else
      return hv_std_traverse(ta->hv, obj, (visitproc)hv_ra_rec, ta);
}

PyDoc_STRVAR(hv_reachable_doc,
"HV.reachable(X:NodeSet, Y:NodeSet) -> NodeSet\n\
\n\
Return the set of objects reached via a path in the visible heap as\n\
defined by HV, from some object in X, avoiding any object in Y.");

static PyObject *
hv_reachable(NyHeapViewObject *self, PyObject *args, PyObject *kwds)
{
    RATravArg ta;
    static char *kwlist[] = {"start", "avoid", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!:reachable", kwlist,
				     NyNodeSet_TYPE, &ta.start,
				     NyNodeSet_TYPE, &ta.avoid))
      return 0;
    ta.hv = self;
    ta.visited = hv_mutnodeset_new(self);
    if (!ta.visited)
      goto err;
    if (NyNodeSet_iterate(ta.start, (visitproc)hv_ra_rec, &ta) == -1)
      goto err;
    if (hv_cleanup_mutset(ta.hv, ta.visited) == -1)
      goto err;
    return (PyObject *)ta.visited;
  err:
    Py_XDECREF(ta.visited);
    return 0;
}

static int
hv_ra_rec_e(PyObject *obj, RATravArg *ta)
{
    int r;
    r = NyNodeSet_setobj(ta->visited, obj);
    if (r)
      return r < 0 ? r: 0;
    else {
	if (NyNodeSet_hasobj(ta->avoid, obj))
	  return 0;
	return hv_std_traverse(ta->hv, obj, (visitproc)hv_ra_rec_e, ta);
    }
}

PyDoc_STRVAR(hv_reachable_x_doc,
"HV.reachable_x(X:NodeSet, Y:NodeSet) -> NodeSet\n\
\n\
Return the set of objects reached via a path in the visible heap as\n\
defined by HV, from some object in X, avoiding any object in Y except\n\
at the end of the path.");

static PyObject *
hv_reachable_x(NyHeapViewObject *self, PyObject *args, PyObject *kwds)
{
    RATravArg ta;
    static char *kwlist[] = {"start", "avoid", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!:reachable", kwlist,
				     NyNodeSet_TYPE, &ta.start,
				     NyNodeSet_TYPE, &ta.avoid))
      return 0;
    ta.hv = self;
    ta.visited = hv_mutnodeset_new(self);
    if (!ta.visited)
      goto err;
    if (NyNodeSet_iterate(ta.start, (visitproc)hv_ra_rec_e, &ta) == -1)
      goto err;
    if (hv_cleanup_mutset(ta.hv, ta.visited) == -1)
      goto err;
    return (PyObject *)ta.visited;
  err:
    Py_XDECREF(ta.visited);
    return 0;
}

static long
hv_get_member_offset(PyTypeObject *type, char *member_name)
{
    PyObject *mro = type->tp_mro;
    if (mro) {
	int i;
	for (i = 0; i < PyTuple_GET_SIZE(mro); i++) {
	    PyObject *t = PyTuple_GET_ITEM(mro, i);
	    if (PyType_Check(t)) {
		PyMemberDef *mp = ((PyTypeObject *)t)->tp_members;
		if (mp) {
		    while (mp->name) {
			if (strcmp(mp->name, member_name) == 0)
			  return mp->offset;
			mp++;
		    }
		}
	    }
	}
    }
    return -1;
}

PyDoc_STRVAR(hv_register__hiding_tag__type_doc,
"HV.register__hiding_tag__type(type)\n\
\n\
Register a type of objects that may be hidden from the heap view\n\
defined by HV. The type must have a slot named _hiding_tag_. An object\n\
that is an instance of the type, or of a subtype, is hidden when its\n\
_hiding_tag_ is HV._hiding_tag_.");

static PyObject *
hv_register__hiding_tag__type(NyHeapViewObject *hv, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"type", 0};
    PyTypeObject *type;
    ExtraType *xt;
    long offs;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!:register_hiding_type", kwlist,
				     &PyType_Type, &type))
      return NULL;
    offs = hv_get_member_offset(type, "_hiding_tag_");
    if (offs == -1) {
	PyErr_SetString(PyExc_ValueError,
			"register__hiding_tag__type: type has no '_hiding_tag_' slot");
	return 0;
    }

    xt = hv_extra_type(hv, type);
    if (xt == &xt_error)
      return 0;
    if (xt->xt_trav_code == XT_HE || xt->xt_trav_code == XT_HI) {
	PyErr_SetString(PyExc_ValueError,
			"register__hiding_tag__type: type is already registered");
	return 0;
    }
    xt->xt_he_traverse = xt->xt_traverse;
    xt->xt_he_xt = xt;
    xt->xt_he_offs = offs;
    xt->xt_traverse = xt_he_traverse;
    xt->xt_trav_code = XT_HE;
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(hv_register_hidden_exact_type_doc,
"HV.register_hidden_exact_type(type)\n\
\n\
Register a type of objects that should be hidden from the heap view\n\
defined by HV. Objects of the exact type registered -- not including\n\
subtypes -- will be hidden.\n\
\n\
See also: register__hiding_tag__type.");

static PyObject *
hv_register_hidden_exact_type(NyHeapViewObject *hv, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"type", 0};
    PyTypeObject *type;
    ExtraType *xt;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!:register_hiding_type", kwlist,
				     &PyType_Type, &type))
      return NULL;
    xt = hv_extra_type(hv, type);
    if (xt == &xt_error)
      return 0;
    if (xt->xt_trav_code == XT_HE || xt->xt_trav_code == XT_HI) {
	PyErr_SetString(PyExc_ValueError,
			"register_hidden_exact_type: type is already registered");
	return 0;
    }
    xt->xt_traverse = xt_no_traverse;
    xt->xt_trav_code = XT_HI;
    Py_INCREF(Py_None);
    return Py_None;
}



PyDoc_STRVAR(hv_relate_doc,
"HV.relate(src, tgt) -> relation structure\n\
\n\
Return a description of the relation between src and tgt. This is used\n\
for descriptions of edges in paths.\n\
\n\
[The result is in a special format that I choose to not define here\n\
since it is for special low-level use and subject to change.]");

static PyObject *
hv_relate(NyHeapViewObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"src", "tgt", 0};
    hv_relate_visit_arg crva;
    int i;
    PyObject *res = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO:relate", kwlist,
				     &crva.hr.src,
				     &crva.hr.tgt))
      return NULL;
    crva.hr.flags = 0;
    crva.hr.hv = (void *)self;
    crva.hr.visit = hv_relate_visit;
    crva.err = 0;
    for (i = 0; i < NYHR_LIMIT; i++)
      crva.relas[i] = 0;
    if (hv_std_relate(&crva.hr) == -1 ||
		      crva.err ||
		      (!(res = PyTuple_New(NYHR_LIMIT)))) {
	goto retres;
    }
    for (i = 0; i < NYHR_LIMIT; i++) {
	PyObject *x;
	if (!crva.relas[i]) {
	    x =  PyTuple_New(0);
	} else {
	    x = PyList_AsTuple(crva.relas[i]);
	}
	if (!x) {
	    Py_DECREF(res);
	    res = 0;
	    goto retres;
	} else {
	    PyTuple_SetItem(res, i, x);
	}
    }
  retres:
    for (i = 0; i < NYHR_LIMIT; i++)
      Py_XDECREF(crva.relas[i]);
    return res;
}


typedef struct {
    NyHeapViewObject *hv;
    NyNodeSetObject *hs;
} HVRITravArg;



static int
hv_ss_visit(PyObject *obj, NyNodeSetObject *hs)
{
    if (NyNodeSet_setobj(hs, obj) == -1)
      return -1;
    return 0;
}

static int
hv_relimg_trav(PyObject *obj, HVRITravArg *ta)
{
    return hv_std_traverse(ta->hv, obj, (visitproc)hv_ss_visit, ta->hs);
}

PyDoc_STRVAR(hv_relimg_doc,
"HV.relimg(S:iterable) -> NodeSet\n\
\n\
Return the 'relational image of HV wrt S'. That is, the set of nodes\n\
that are directly referred to from the nodes in S via the visible heap\n\
reachability relation as defined by HV.");

static NyNodeSetObject *
hv_relimg(NyHeapViewObject *hv, PyObject *S)
{
    HVRITravArg ta;
    ta.hv = hv;
    ta.hs = hv_mutnodeset_new(hv);
    if (!ta.hs)
      return 0;
    if (iterable_iterate(S, (visitproc)hv_relimg_trav, &ta) == -1)
      goto err;
    if (hv_cleanup_mutset(ta.hv, ta.hs) == -1)
      goto err;
    return ta.hs;
  err:
    Py_DECREF(ta.hs);
    return 0;

}

typedef struct {
    NyHeapViewObject *hv;
    NyNodeSetObject *U, *S, *V;
    NyNodeGraphObject *P;
    NyNodeGraphObject *edgestoavoid;
    PyObject *u;
    int find_one_flag;
} ShPathTravArg;


static int
hv_shpath_inner(PyObject *v, ShPathTravArg *ta)
{
    int r;
    if (ta->edgestoavoid) {
	NyNodeGraphEdge *lo, *hi;
	if (NyNodeGraph_Region(ta->edgestoavoid, ta->u, &lo, &hi) == -1)
	  return -1;
	for (;lo < hi; lo++) {
	    if (lo->tgt == v)
	      return 0;
	}
    }
    r = NyNodeSet_hasobj(ta->S, v);
    if (r == -1)
      return r;
    if (r)
      return 0;
    r = NyNodeSet_setobj(ta->V, v);
    if (r == -1)
      return -1;
    if (!r || !ta->find_one_flag)
      if (NyNodeGraph_AddEdge(ta->P, v, ta->u) == -1)
	return -1;
    return 0;
}


static int
hv_shpath_outer(PyObject *u, ShPathTravArg *ta)
{
    if ((void *) u == ta->hv ||
	(void *) u == ta->S ||
	(void *) u == ta->V ||
	(void *) u == ta->P ||
	(void *) u == ta->edgestoavoid ||
	(void *) u == ta->U)
      return 0;
    ta->u = u;
    return hv_std_traverse(ta->hv, u, (visitproc)hv_shpath_inner, ta);
}

PyDoc_STRVAR(hv_shpathstep_doc,
"HV.shpathstep(G:NodeGraph, U:NodeSet, S:NodeSet\n"
"              [,AvoidEdges:NodeGraph [,find_one:bool]]) -> NodeSet\n"
"\n"
"This method implements one step of a shortest path algorithm.\n"
"The arguments are:\n"
"\n"
"    G           Updated by the method, with the edges from nodes in the\n"
"                source set to the new nodes visited.\n"
"    U           The source set for this step.\n"
"    S           The set of already visited nodes.\n"
"    AvoidEdges  Edges to avoid.\n"
"    find_one    If True, at most one edge will be found from each node\n"
"                in the source set. Normally, all edges will be found.\n"
"\n"
"Return value:   The new nodes visited. This may be used for the\n"
"                U argument the next time the method is called.\n"
"\n"
"See also: shpgraph_algorithm in Path.py.");

static PyObject *
hv_shpathstep(NyHeapViewObject *self, PyObject *args, PyObject *kwds)
{
    ShPathTravArg ta;
    static char *kwlist[] = {"G", "U", "S", "AvoidEdges", "find_one", 0};
    ta.find_one_flag = 0;
    ta.edgestoavoid = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O!O!|O!i:shpathstep", kwlist,
				     &NyNodeGraph_Type, &ta.P,
				     NyNodeSet_TYPE, &ta.U,
				     NyNodeSet_TYPE, &ta.S,
				     &NyNodeGraph_Type, &ta.edgestoavoid,
				     &ta.find_one_flag))
      return 0;
    ta.hv = self;
    if (ta.edgestoavoid && ta.edgestoavoid->used_size == 0)
      ta.edgestoavoid = 0;
    ta.V = hv_mutnodeset_new(self);
    if (!(ta.V))
      goto err;
    if (NyNodeSet_iterate(ta.U, (visitproc)hv_shpath_outer, &ta) == -1)
      goto err;
    return (PyObject *)ta.V;
  err:
    Py_XDECREF(ta.V);
    return 0;
}



PyDoc_STRVAR(hv_limitframe_doc,
"HV.limitframe : frame | None\n\
\n\
The traversal limiting frame.\n\
\n\
If limitframe is set to a frame object, the frames that are more\n\
recently entered than limitframe will be hidden when traversing the\n\
heap from the root RootState. It will start traversing from limitframe\n\
rather than from the most recent frame as it would otherwise do.");

static int
hv_set_limitframe(NyHeapViewObject *self, PyObject *arg, void *unused)
{
    PyObject *orf = self->limitframe;
    if (arg == Py_None) {
	self->limitframe = 0;
    } else if (PyFrame_Check(arg)) {
	self->limitframe = arg;
	Py_INCREF(arg);
    } else {
	PyErr_SetString(PyExc_TypeError, "set_limitframe: frame or None expected");
	return -1;
    }
    Py_XDECREF(orf);
    return 0;
}

static PyObject *
hv_get_limitframe(NyHeapViewObject *self, void *unused)
{
    PyObject *r = self->limitframe;
    if (!r)
      r = Py_None;
    Py_INCREF(r);
    return r;
}

PyDoc_STRVAR(hv_update_dictowners_doc,
"HV.update_dictowners(owners:NodeGraph)\n\
\n\
Update owners with ownership edges.\n\
\n\
The dict owners graph will be updated with an edge from each dict\n\
object in the heap, to either its owner or to None.");

PyObject *
hv_update_dictowners(NyHeapViewObject *self, PyObject *args)
{
    NyNodeGraphObject *rg;
    if (!PyArg_ParseTuple(args, "O!:update_dictowners",
			  &NyNodeGraph_Type, &rg))
      return NULL;
    if (hv_cli_dictof_update(self, rg) == -1)
      return 0;
    Py_INCREF(Py_None);
    return Py_None;
}

#define RG_STACK_MARK 0x8000000

static int
rg_is_on_stack(PyObject *obj)
{
    return obj->ob_refcnt & RG_STACK_MARK;
}

static void
rg_set_on_stack(PyObject *obj)
{
     obj->ob_refcnt |= RG_STACK_MARK;
}     

static void
rg_clr_on_stack(PyObject *obj)
{
     obj->ob_refcnt &= ~RG_STACK_MARK;
}     


/* Code specific for update ... */

typedef struct {
    NyHeapViewObject *hv;
    NyNodeSetObject *targetset, *markset, *outset;
    NyNodeGraphObject *rg;
    PyObject *retainer;
} RetaTravArg;

static int
rg_put_set_out(RetaTravArg *ta, PyObject *obj)
{
    if (NyNodeGraph_AddEdge(ta->rg, obj, ta->retainer) == -1)
      return -1;
    if (NyNodeSet_setobj(ta->outset, obj) == -1)
      return -1;
    return 0;
}

static int rg_retarec(PyObject *obj, RetaTravArg *ta);

static int
rg_traverec(PyObject *obj, RetaTravArg *ta)
{
    PyObject *oretainer = ta->retainer;
    int osize = ta->rg->used_size;
    int r;
    if (obj == (PyObject *)ta->rg)
      return 0;
    assert(obj->ob_refcnt < 0xa000000 && (Py_uintptr_t)obj->ob_type > 0x1000);
    ta->retainer = obj;
    r = hv_std_traverse(ta->hv, obj, (visitproc)rg_retarec, ta);
    ta->retainer = oretainer;
    if (r != -1)
      r = (osize < ta->rg->used_size ||
	   (!ta->targetset && obj != ta->hv->root) ||
	   (ta->targetset && NyNodeSet_hasobj(ta->targetset, obj)));
    return r;
}

static int
rg_retarec(PyObject *obj, RetaTravArg *ta) {
    int r;
    if (obj == ta->hv->root)
      r = 0;
    else if (rg_is_on_stack(obj)) {
	r = rg_put_set_out(ta, obj);
    } else if (obj->ob_refcnt == 1) {
	r = rg_traverec(obj, ta);
	if (r > 0)
	  r = NyNodeGraph_AddEdge(ta->rg, obj, ta->retainer);
    } else if (NyNodeSet_hasobj(ta->markset, obj)) {
	r = 0;
    } else if (NyNodeSet_hasobj(ta->outset, obj)) {
	r = NyNodeGraph_AddEdge(ta->rg, obj, ta->retainer);
    } else {
	rg_set_on_stack(obj);
	r = rg_traverec(obj, ta);
	rg_clr_on_stack(obj);
	if (r > 0)
	  r = rg_put_set_out(ta, obj);
	else if (r == 0)
	  r = NyNodeSet_setobj(ta->markset, obj);
    }
    return r;
}


PyDoc_STRVAR(hv_update_referrers_doc,
"HV.update_referrers(X:NodeGraph, Y:NodeSet)\n"
"\n"
"Update referrer graph X for Y.\n"
"\n"
"The visible heap defined by HV will be traversed from the root of HV\n"
"so that the edges of every path from the root to nodes in Y will be\n"
"represented, inverted, in X.");

PyObject *
hv_update_referrers(NyHeapViewObject *self, PyObject *args)
{
    RetaTravArg ta;
    int r;
    if (!PyArg_ParseTuple(args, "O!O!:update_referrers",
			  &NyNodeGraph_Type, &ta.rg,
			  NyNodeSet_TYPE, &ta.targetset))
      return NULL;

    ta.hv = self;
    ta.markset = hv_mutnodeset_new(self);
    ta.outset = hv_mutnodeset_new(self);
    if (!(ta.markset && ta.outset)) {
	Py_XDECREF(ta.markset);
	Py_XDECREF(ta.outset);
	return 0;
    }
    ta.retainer = 0;
    r = rg_traverec(ta.hv->root, &ta);
    Py_DECREF(ta.markset);
    Py_DECREF(ta.outset);
    if (r != -1) {
	Py_INCREF(Py_None);
	return Py_None;
    } else {
	return 0;
    }
}

PyDoc_STRVAR(hv_update_referrers_completely_doc,
"HV.update_referrers_completely(X:nodegraph)\n\
\n\
Update referrer graph X 'completely'.\n\
\n\
[Experimental algorithm that updates X with the referrers to all\n\
objects in the heap (of visible nodes as defined in HV). It is not\n\
normally used.]");

typedef struct {
    NyHeapViewObject *hv;
    NyNodeGraphObject *rg;
    PyObject *retainer;
    int num;
} URCOTravArg;

int dummy;

static int
urco_traverse(PyObject *obj, URCOTravArg *ta)
{
    if (hv_is_obj_hidden(ta->hv, obj))
	return 0;
    if (NyNodeGraph_AddEdge(ta->rg, obj, ta->retainer) == -1)
      return -1;
    ta->num++;
    return 0;
}


PyObject *
hv_update_referrers_completely(NyHeapViewObject *self, PyObject *args)
{
    URCOTravArg ta;
    PyObject *objects=0, *result=0, *_hiding_tag_=0;
    int len, i;
    ta.hv = self;
    _hiding_tag_ = self->_hiding_tag_;
    self->_hiding_tag_ = Py_None;
    if (!PyArg_ParseTuple(args, "O!:update_referrers_completely",
			  &NyNodeGraph_Type, &ta.rg))
      goto err;
    objects = gc_get_objects();
    if (!objects)
      goto err;
    len = PyList_Size(objects);
    if (len == -1)
      goto err;
    NyNodeGraph_Clear(ta.rg);
    for (i = 0; i < len; i++) {
	PyObject *retainer = PyList_GET_ITEM(objects, i);
	ta.num = 0;
	if (retainer == (void *)ta.rg)
	  continue;
	if (NyNodeGraph_Check(retainer))
	  continue; /* Note 22/11 2004 */
	else if ((NyNodeSet_Check(retainer) &&
		  ((NyNodeSetObject *)retainer)->_hiding_tag_ == _hiding_tag_))
	  ta.retainer = Py_None;
	else
	  ta.retainer = retainer;
	if (hv_std_traverse(ta.hv, retainer, (visitproc)urco_traverse, &ta) == -1)
	  goto err;
    }
    result = Py_None;
    Py_INCREF(result);
  err:
    self->_hiding_tag_ = _hiding_tag_;
    Py_XDECREF(objects);
    return result;
}

static PyMethodDef hv_methods[] = {
    {"cli_and", (PyCFunction)hv_cli_and, METH_VARARGS, hv_cli_and_doc},
    {"cli_class", (PyCFunction)hv_cli_class, METH_NOARGS, hv_cli_class_doc},
    {"cli_dictof", (PyCFunction)hv_cli_dictof, METH_VARARGS, hv_cli_dictof_doc},
    {"cli_findex", (PyCFunction)hv_cli_findex, METH_VARARGS, hv_cli_findex_doc},
    {"cli_id", (PyCFunction)hv_cli_id, METH_VARARGS, hv_cli_id_doc},
    {"cli_idset", (PyCFunction)hv_cli_idset, METH_VARARGS, hv_cli_idset_doc},
    {"cli_indisize", (PyCFunction)hv_cli_indisize, METH_VARARGS, hv_cli_indisize_doc},
    {"cli_inrel", (PyCFunction)hv_cli_inrel, METH_VARARGS, hv_cli_inrel_doc},
    {"cli_none", (PyCFunction)hv_cli_none, METH_NOARGS, hv_cli_none_doc},
    {"cli_rcs", (PyCFunction)hv_cli_rcs, METH_VARARGS, hv_cli_rcs_doc},
    {"cli_type", (PyCFunction)hv_cli_type, METH_NOARGS, hv_cli_type_doc},
    {"cli_user_defined", (PyCFunction)hv_cli_user_defined, METH_KEYWORDS, hv_cli_user_defined_doc},
    {"delete_extra_type", (PyCFunction)hv_delete_extra_type, METH_O, hv_delete_extra_type_doc},
    {"indisize_sum", (PyCFunction)hv_indisize_sum, METH_O, hv_indisize_sum_doc},
    {"heap", (PyCFunction)hv_heap, METH_NOARGS, hv_heap_doc},
    {"numedges", (PyCFunction)hv_numedges, METH_VARARGS, hv_numedges_doc},
    {"reachable", (PyCFunction)hv_reachable, METH_KEYWORDS, hv_reachable_doc},
    {"reachable_x", (PyCFunction)hv_reachable_x, METH_KEYWORDS, hv_reachable_x_doc},
    {"register_hidden_exact_type", (PyCFunction)hv_register_hidden_exact_type, METH_KEYWORDS,
       hv_register_hidden_exact_type_doc},
    {"register__hiding_tag__type", (PyCFunction)hv_register__hiding_tag__type, METH_KEYWORDS,
       hv_register__hiding_tag__type_doc},
    {"relate", (PyCFunction)hv_relate, METH_KEYWORDS, hv_relate_doc},
    {"relimg", (PyCFunction)hv_relimg, METH_O, hv_relimg_doc},
    {"shpathstep", (PyCFunction)hv_shpathstep, METH_KEYWORDS, hv_shpathstep_doc},
    {"update_dictowners", (PyCFunction)hv_update_dictowners, METH_VARARGS,
       hv_update_dictowners_doc},
    {"update_referrers", (PyCFunction)hv_update_referrers, METH_VARARGS,
       hv_update_referrers_doc},
    {"update_referrers_completely", (PyCFunction)hv_update_referrers_completely, METH_VARARGS,
       hv_update_referrers_completely_doc},
    
    {NULL,		NULL}		/* sentinel */
};

#define OFF(x) offsetof(NyHeapViewObject, x)


static PyMemberDef hv_members[] = {
    {"_hiding_tag_",	 T_OBJECT, OFF(_hiding_tag_), 0,
"HV._hiding_tag_\n\
\n\
The hiding tag defining what objects are hidden from the view defined\n\
by HV. Objects that contain a _hiding_tag_ object which is identical\n\
to HV._hiding_tag_, will be hidden from view, in the following cases:\n\
\n\
o The object is of a type that has been registered for hiding\n\
  via _hiding_tag, or is of a subtype of such a type.\n\
\n\
o The object is of instance type. Such an object will be checked\n\
  for a _hiding_tag_ item in its __dict__.\n\
"},
    {"is_hiding_calling_interpreter", T_UBYTE, OFF(is_hiding_calling_interpreter), 0,
"HV.is_hiding_calling_interpreter : boolean kind\n\
\n\
If True, the data of the interpreter using the HV will be hidden from\n\
the heap view as seen from RootState.\n\
\n\
This is used when multiple Python interpreters are used. One\n\
interpreter will be monitoring the operation of the other\n\
interpreter(s). It would set is_hiding_calling_interpreter to True in\n\
the HV it is using. Its own data will then be hidden from view, making\n\
memory leak detection more practical."},

    {"is_using_traversing_owner_update", T_UBYTE, OFF(is_hiding_calling_interpreter), 0,
"HV.is_using_traversing_owner_update : boolean kind\n\
\n\
True if update_dictowners is using a recursive traversal algorithm to\n\
find the dicts in the heap. When False, the normal case, it will use the\n\
dicts found in the gc collection structure, by gc.get_objects(). This was\n\
found to be much faster in usual cases, but the old version is available\n\
by setting this flag. -- It may be removed in a later release! --"},


    {"root",	 T_OBJECT, OFF(root), 0, 
"HV.root\n\
\n\
An object that is used as the starting point when traversing the\n\
heap. It is normally set to the special RootState object, which has\n\
special functionality for finding the objects in the internals of the\n\
Python interpreter structures. It can be set to any other object,\n\
especially for test purposes.\n\
\n\
See also: RootState"},
    {"static_types",	 T_OBJECT , OFF(static_types), READONLY,
"HV.static_types : NodeSet, read only\n\
\n\
The 'static types' that have been found.\n\
\n\
The static types are the type objects that are not heap allocated, but\n\
are defined directly in C code. HeapView searches for these among all\n\
reachable objects (at a suitable time or as needed)."},


    {NULL} /* Sentinel */
};

#undef OFF

static  PyGetSetDef hv_getset[] = {
    {"limitframe", (getter)hv_get_limitframe, (setter)hv_set_limitframe, hv_limitframe_doc},
    {0}
};


PyTypeObject NyHeapView_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.heapy.heapyc.HeapView",		/* tp_name */
	sizeof(NyHeapViewObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)hv_dealloc, 		/* tp_dealloc */
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
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
	  	Py_TPFLAGS_BASETYPE,		/* tp_flags */
 	hv_doc,					/* tp_doc */
 	(traverseproc)hv_gc_traverse,		/* tp_traverse */
 	(inquiry)hv_gc_clear,			/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)0,				/* tp_iter */
	0,					/* tp_iternext */
	hv_methods,				/* tp_methods */
	hv_members,				/* tp_members */
	hv_getset,				/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)0,				/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	hv_new,					/* tp_new */
	_PyObject_GC_Del,			/* tp_free */
};


