/* NodeGraph object implementation */

/* Pointer comparison macros
   Used for comparison of pointers that are not pointing
   into the same array. It would be formally undefined to 
   compare pointers directly according to standard C definition.
   This should get around it.

*/

#define PTR_LT(a, b)	((Py_uintptr_t)(a) < (Py_uintptr_t)(b))
#define PTR_EQ(a, b)	((Py_uintptr_t)(a) == (Py_uintptr_t)(b))

#define PTR_CMP(a,b)	(PTR_LT(a, b) ? -1 : (PTR_EQ(a, b) ? 0: 1))

/* NodeGraphIter objects */

typedef struct {
	PyObject_HEAD
	NyNodeGraphObject *nodegraph;
	int i;
	int oldsize;
} NyNodeGraphIterObject;

/* NodeGraphIter methods */

static void
ngiter_dealloc(NyNodeGraphIterObject *it)
{
	_PyObject_GC_UNTRACK(it);
	Py_XDECREF(it->nodegraph);
	PyObject_GC_Del(it);
}

static int
ngiter_traverse(NyNodeGraphIterObject *it, visitproc visit, void *arg)
{
    if (!it->nodegraph)
      return 0;
    return visit((PyObject *)it->nodegraph, arg);
}

static PyObject *
ngiter_iternext(NyNodeGraphIterObject *ngi)
{
    PyObject *ret;
    NyNodeGraphEdge *e;
    if (ngi->i >= ngi->nodegraph->used_size)
      return 0;
    ret = PyTuple_New(2);
    if (!ret)
      return 0;
    if (ngi->nodegraph->used_size != ngi->oldsize ||
	!ngi->nodegraph->is_sorted) {
	Py_DECREF(ret);
	PyErr_SetString(PyExc_RuntimeError, "nodegraph changed size during iteration");
	return 0;
    }
    e = &ngi->nodegraph->edges[ngi->i];
    Py_INCREF(e->src);
    PyTuple_SET_ITEM(ret, 0, e->src);
    Py_INCREF(e->tgt);
    PyTuple_SET_ITEM(ret, 1, e->tgt);
    ngi->i++;
    return ret;
}

/* NodeGraphIter type */

PyTypeObject NyNodeGraphIter_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"nodegraph-iterator",			/* tp_name */
	sizeof(NyNodeGraphIterObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)ngiter_dealloc, 		/* tp_dealloc */
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
 	(traverseproc)ngiter_traverse,		/* tp_traverse */
 	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	PyObject_SelfIter,			/* tp_iter */
	(iternextfunc)ngiter_iternext,		/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
};

/* NodeGraph methods */

void
NyNodeGraph_Clear(NyNodeGraphObject *ng)
{
    int N = ng->used_size;
    NyNodeGraphEdge *edges = ng->edges;
    int i;
    ng->edges = 0;
    ng->used_size = ng->allo_size = 0;
    for (i = 0; i < N; i++) {
	Py_DECREF(edges[i].src);
	Py_DECREF(edges[i].tgt);
    }
    PyMem_FREE(edges);
}

static int
ng_gc_clear(NyNodeGraphObject *ng)
{
    PyObject *hn = ng->_hiding_tag_;
    ng->_hiding_tag_ = 0;
    NyNodeGraph_Clear(ng);
    Py_XDECREF(hn);
    return 0;
}

static void
ng_dealloc(PyObject *v)
{
    NyNodeGraphObject *ng = (void *)v;
    int i;
    Py_TRASHCAN_SAFE_BEGIN(v)
    _PyObject_GC_UNTRACK(v);
    ng_gc_clear(ng);
    for (i = 0; i < ng->used_size; i++) {
	Py_DECREF(ng->edges[i].src);
	Py_DECREF(ng->edges[i].tgt);
    }
    PyMem_FREE(ng->edges);
    ng->ob_type->tp_free(v);
    Py_TRASHCAN_SAFE_END(v)
      
}

static int
ng_gc_traverse(NyNodeGraphObject *ng, visitproc visit, void *arg)
{
    int i;
    int err = 0;
    for (i = 0; i < ng->used_size; i++) {
	err = visit(ng->edges[i].src, arg) ;
	if (err) return err;
	err = visit(ng->edges[i].tgt, arg) ;
	if (err) return err;
    }
    if (ng->_hiding_tag_)
      err = visit(ng->_hiding_tag_, arg);
    return err;
}

int
NyNodeGraph_AddEdge(NyNodeGraphObject *ng, PyObject *src, PyObject *tgt)
{
    if (!ng->is_preserving_duplicates &&
	ng->used_size &&
	ng->edges[ng->used_size-1].src == src &&
	ng->edges[ng->used_size-1].tgt == tgt)
      return 0;


    assert(src->ob_refcnt < 0xa000000 && (Py_uintptr_t)src->ob_type > 0x1000);
    assert(tgt->ob_refcnt < 0xa000000 && (Py_uintptr_t)tgt->ob_type > 0x1000);

    if (ng->used_size >= ng->allo_size) {
	int allo = roundupsize(ng->used_size + 1);
	PyMem_RESIZE(ng->edges, NyNodeGraphEdge, allo);
	if (!ng->edges) {
	    ng->used_size = ng->allo_size = 0;
	    PyErr_NoMemory();
	    return -1;
	}
	ng->allo_size = allo;
    }
    Py_INCREF(src);
    Py_INCREF(tgt);
    ng->edges[ng->used_size].src = src;
    ng->edges[ng->used_size].tgt = tgt;
    ng->used_size ++;
    ng->is_sorted = 0;
    return 0;
}

static int
ng_compare(const void *x, const void *y)
{
    int c = PTR_CMP(((NyNodeGraphEdge *)x)->src, ((NyNodeGraphEdge *)y)->src);
    if (!c)
      c = PTR_CMP(((NyNodeGraphEdge *)x)->tgt, ((NyNodeGraphEdge *)y)->tgt);
    return c;
}

static int
ng_compare_src_only(const void *x, const void *y)
{
    int c = PTR_CMP(((NyNodeGraphEdge *)x)->src, ((NyNodeGraphEdge *)y)->src);
    return c;
}

static void
ng_sort(NyNodeGraphObject *ng)
{
    qsort(ng->edges, ng->used_size, sizeof(NyNodeGraphEdge),
	  ng->is_preserving_duplicates ? ng_compare_src_only : ng_compare);
}

static void
ng_remove_dups(NyNodeGraphObject *ng)
{
    NyNodeGraphEdge *dst, *src, *hi;
    if (ng->used_size <= 1)
      return;
    hi = ng->edges + ng->used_size;
    dst = ng->edges + 1;
    src = ng->edges + 1;
    while( src < hi )  {
	if (src[0].src == dst[-1].src && src[0].tgt == dst[-1].tgt) {
	    Py_DECREF(src[0].src);
	    Py_DECREF(src[0].tgt);
	    src++;
	} else {
	    if (src != dst)
	      dst[0] = src[0];
	    dst++;
	    src++;
	}
    }
    ng->used_size = dst - ng->edges;
}

static void
ng_trim(NyNodeGraphObject *ng)
{
    PyMem_RESIZE(ng->edges, NyNodeGraphEdge, ng->used_size);
    ng->allo_size = ng->used_size;
}

static void
ng_sortetc(NyNodeGraphObject *ng)
{
    ng_sort(ng);
    if (!ng->is_preserving_duplicates)
      ng_remove_dups(ng);
    ng_trim(ng);
    ng->is_sorted = 1;
}

static void
ng_maybesortetc(NyNodeGraphObject *ng)
{
    if (!ng->is_sorted)
      ng_sortetc(ng);
}

static char ng_add_edge_doc[] =
"NG.add_edge(source, target)\n\
\n\
Add to NG, an edge from source to target.";


PyObject *
ng_add_edge(NyNodeGraphObject *ng, PyObject *args)
{
    PyObject *src, *tgt;
    if (!PyArg_ParseTuple(args, "OO:",  &src, &tgt))
      return NULL;
    if (NyNodeGraph_AddEdge(ng, src, tgt) == -1)
      return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static char ng_add_edges_n1_doc[] =
"NG.add_edges_n1(srcs:iterable, tgt)\n\
\n\
Add to NG, for each src in srcs, an edge from src to tgt.";


typedef struct {
    NyNodeGraphObject *ng;
    PyObject *tgt;
} AETravArg;

static int
ng_add_edges_n1_trav(PyObject *obj, AETravArg *ta)
{
    if (NyNodeGraph_AddEdge(ta->ng, obj, ta->tgt) == -1)
      return -1;
    return 0;
}

PyObject *
ng_add_edges_n1(NyNodeGraphObject *ng, PyObject *args)
{
    AETravArg ta;
    PyObject *it;
    ta.ng = ng;
    if (!PyArg_ParseTuple(args, "OO:",  &it, &ta.tgt))
      return NULL;
    if (iterable_iterate(it, (visitproc)ng_add_edges_n1_trav, &ta) == -1)
      return 0;
    Py_INCREF(Py_None);
    return Py_None;
}


static char ng_as_flat_list_doc[] =
"NG.as_flat_list() -> list\n\
\n\
Return the edges of NG in the form [src0, tgt0, src1, tgt1 ...].";

PyObject *
ng_as_flat_list(NyNodeGraphObject *ng, PyObject *arg)
{
    PyObject *r = PyList_New(0);
    int i;
    if (!r)
      return 0;
    for (i = 0; i < ng->used_size; i++) {
	if ((PyList_Append(r, ng->edges[i].src) == -1) ||
	    (PyList_Append(r, ng->edges[i].tgt) == -1)) {
	    Py_DECREF(r);
	    return 0;
	}
    }
    return r;
}

static char ng_clear_doc[] =
"NG.clear()\n\
\n\
Remove all items from NG.";

PyObject *
ng_clear_method(NyNodeGraphObject *ng, PyObject *arg_notused)
{
    NyNodeGraph_Clear(ng);
    Py_INCREF(Py_None);
    return Py_None;
}

NyNodeGraphObject *
NyNodeGraph_SubtypeNew(PyTypeObject *type)
{
    NyNodeGraphObject *ng = (NyNodeGraphObject *)type->tp_alloc(type, 1);
    if (!ng)
      return NULL;
    ng->_hiding_tag_ = 0;
    ng->allo_size = ng->used_size = 0;
    ng->is_sorted = 0;
    ng->is_mapping = 0;
    ng->is_preserving_duplicates = 0;
    ng->edges = 0;
    return ng;
}

NyNodeGraphObject *
NyNodeGraph_SiblingNew(NyNodeGraphObject *ng)
{
    NyNodeGraphObject *cp = NyNodeGraph_SubtypeNew(ng->ob_type);
    PyObject *he;
    if (!cp)
      return 0;
    he = cp->_hiding_tag_;
    cp->_hiding_tag_ = ng->_hiding_tag_;
    Py_XINCREF(cp->_hiding_tag_);
    Py_XDECREF(he);
    cp->is_mapping = ng->is_mapping;
    return cp;
}

NyNodeGraphObject *
NyNodeGraph_Copy(NyNodeGraphObject *ng)
{
    NyNodeGraphObject *cp = NyNodeGraph_SiblingNew(ng);
    if (!cp)
      return 0;
    if (NyNodeGraph_Update(cp, (PyObject *)ng) == -1) {
	Py_DECREF(cp);
	return 0;
    }
    return cp;
}

static char ng_copy_doc[] =
"NG.copy() -> NodeGraph\n\
\n\
Return a copy of NG.";

PyObject *
ng_copy(NyNodeGraphObject *ng, PyObject *notused)
{
    return (PyObject *)NyNodeGraph_Copy(ng);
}


typedef struct {
    NyNodeGraphObject *ng;
    int ret;
} DCTravArg;

static int
ng_dc_trav(PyObject *obj, DCTravArg *ta)
{
    NyNodeGraphEdge *lo, *hi;
    if (NyNodeGraph_Region(ta->ng, obj, &lo, &hi) == -1) {
	return -1;
    }
    if (lo == hi) {
	ta->ret = 0;
	return 1;
    }
    return 0;
}


static char ng_domain_covers_doc[] =
"NG.domain_covers(X:iterable) -> bool\n\
\n\
Return True if each node in X is the source of some edge in NG, False otherwise.";

static PyObject *
ng_domain_covers(NyNodeGraphObject *ng, PyObject *X)
{
    DCTravArg ta;
    PyObject *result;
    ta.ng = ng;
    ta.ret = 1;
    if (iterable_iterate(X, (visitproc)ng_dc_trav, &ta) == -1) {
	return 0;
    }
    result = ta.ret? Py_True:Py_False;
    Py_INCREF(result);
    return result;
}


typedef struct {
    NyNodeGraphObject *ng, *ret;
} DRTravArg;

static int
ng_dr_trav(PyObject *obj, DRTravArg *ta)
{
    NyNodeGraphEdge *lo, *hi, *cur;
    if (NyNodeGraph_Region(ta->ng, obj, &lo, &hi) == -1) {
	return -1;
    }
    for (cur = lo; cur < hi; cur++) {
	if (NyNodeGraph_AddEdge(ta->ret, obj, cur->tgt) == -1)
	  return -1;
    }
    return 0;
}



static char ng_domain_restricted_doc[] =
"NG.domain_restricted(X:iterable) -> NodeGraph\n\
\n\
Return a new NodeGraph, containing those edges in NG that have source in X.";

static PyObject *
ng_domain_restricted(NyNodeGraphObject *ng, PyObject *X)
{
    DRTravArg ta;
    ta.ng = ng;
    ta.ret = NyNodeGraph_SiblingNew(ng);
    if (!ta.ret)
      return 0;
    if (iterable_iterate(X, (visitproc)ng_dr_trav, &ta) == -1) {
	Py_DECREF(ta.ret);
	return 0;
    }
    return (PyObject *)ta.ret;
}


static char ng_get_domain_doc[] =
"NG.get_domain() -> NodeSet\n\
\n\
Return the set of nodes that are the source of some edge in NG.";

static PyObject *
ng_get_domain(NyNodeGraphObject *ng, void *closure)
{
    NyNodeSetObject *ns = NyMutNodeSet_NewHiding(ng->_hiding_tag_);
    int i;
    if (!ns)
      return 0;
    for (i = 0; i < ng->used_size; i++) {
	if (NyNodeSet_setobj(ns, ng->edges[i].src) == -1) {
	    Py_DECREF(ns);
	    return 0;
	}
    }
    return (PyObject *)ns;
}

static char ng_get_range_doc[] =
"NG.get_range() -> NodeSet\n\
\n\
Return the set of nodes that are the target of some edge in NG.";

static PyObject *
ng_get_range(NyNodeGraphObject *ng, void *closure)
{
    NyNodeSetObject *ns = NyMutNodeSet_NewHiding(ng->_hiding_tag_);
    int i;
    if (!ns)
      return 0;
    for (i = 0; i < ng->used_size; i++) {
	if (NyNodeSet_setobj(ns, ng->edges[i].tgt) == -1) {
	    Py_DECREF(ns);
	    return 0;
	}
    }
    return (PyObject *)ns;
}

int
NyNodeGraph_Invert(NyNodeGraphObject *ng) {
    NyNodeGraphEdge *edge = ng->edges;
    int i;
    for (i = 0; i < ng->used_size; i++, edge++) {
	PyObject *t = edge->src;
	edge->src = edge->tgt;
	edge->tgt = t;
    }
    ng->is_sorted = 0;
    return 0;
}

static char ng_invert_doc[] =
"NG.invert()\n\
\n\
Invert the edges of NG.";

static PyObject *
ng_invert(NyNodeGraphObject *ng, void *notused)
{
    if (NyNodeGraph_Invert(ng) == -1)
      return 0;
    Py_INCREF(Py_None);
    return Py_None;
}

NyNodeGraphObject *
NyNodeGraph_Inverted(NyNodeGraphObject *ng)
{
    NyNodeGraphObject *ob;
    ob = NyNodeGraph_Copy(ng);
    if (!ob)
      return 0;
    if (NyNodeGraph_Invert(ob) == -1) {
	Py_DECREF(ob);
	return 0;
    }
    return ob;
    
}

static char ng_inverted_doc[] =
"NG.inverted() -> NodeGraph\n\
\n\
Return a copy of NG with the edges inverted.";

static PyObject *
ng_inverted(NyNodeGraphObject *ng, void *notused)
{
    return (PyObject *)NyNodeGraph_Inverted(ng);
}

PyObject *
ng_iter(NyNodeGraphObject *v)
{
    NyNodeGraphIterObject *iter = PyObject_GC_New(NyNodeGraphIterObject, &NyNodeGraphIter_Type);
    if (!v)
      return 0;
    iter->nodegraph = v;
    Py_INCREF(v);
    iter->i = 0;
    ng_maybesortetc(v);
    iter->oldsize = v->used_size;
    PyObject_GC_Track(iter);
    return (PyObject *)iter;
}

int
NyNodeGraph_Region(NyNodeGraphObject *ng, PyObject *key,
		   NyNodeGraphEdge **lop, NyNodeGraphEdge **hip)
{
    NyNodeGraphEdge *lo, *hi, *cur;
    ng_maybesortetc(ng);
    lo = ng->edges;
    hi = ng->edges + ng->used_size;
    if (lo >=  hi) {
	*lop = *hip = lo;
	return 0;
    }
    for (;;) {
	cur = lo + (hi - lo) / 2;
	if (cur->src == key) {
	    for (lo = cur; lo > ng->edges && (lo-1)->src == key; lo--)
	      ;
	    for (hi = cur + 1; hi < ng->edges + ng->used_size && hi->src == key;
		 hi++)
	      ;
	    *lop = lo;
	    *hip = hi;
	    return 0;
	} else if (cur == lo) {
	    *lop = *hip = lo;
	    return 0;
	} else if (PTR_LT(cur->src, key)) /* Make sure use same lt as in sort */
	  lo = cur;
	else
	  hi = cur;
    }
}

typedef struct {
    NyNodeGraphObject *ng;
    NyNodeSetObject *hs;
} RITravArg;

static int
ng_relimg_trav(PyObject *obj, RITravArg *ta)
{
    NyNodeGraphEdge *lo, *hi, *cur;
    if (NyNodeGraph_Region(ta->ng, obj, &lo, &hi) == -1) {
	return -1;
    }
    for (cur = lo; cur < hi; cur++) {
	if (NyNodeSet_setobj(ta->hs, cur->tgt) == -1)
	  return -1;
    }
    return 0;
}

static char ng_relimg_doc[] =
"NG.relimg(X:iterable) -> NodeSet\n\
\n\
Return the relational image of NG wrt X. That is, the set of nodes\n\
that are the target of some edge that have its source in X.";

static NyNodeSetObject *
ng_relimg(NyNodeGraphObject *ng, PyObject *S)
{
    RITravArg ta;
    ta.ng = ng;
    ta.hs = NyMutNodeSet_NewHiding(ng->_hiding_tag_);
    if (!ta.hs)
      return 0;
    ng_maybesortetc(ng);
    if (iterable_iterate(S, (visitproc)ng_relimg_trav, &ta) == -1)
      goto err;
    return ta.hs;
  err:
    Py_DECREF(ta.hs);
    return 0;
}

static int
ng_update_visit(PyObject *obj, NyNodeGraphObject *ng)
{
    if (!PyTuple_Check(obj) || PyTuple_GET_SIZE(obj) != 2) {
	PyErr_SetString(PyExc_TypeError, "update: right argument must be sequence of 2-tuples");
	return -1;
    }
    if (NyNodeGraph_AddEdge(ng,
			    PyTuple_GET_ITEM(obj, 0),
			    PyTuple_GET_ITEM(obj, 1)) == -1)
      return -1;
    return 0;
}


int
NyNodeGraph_Update(NyNodeGraphObject *a, PyObject *u)
{
    return iterable_iterate(u, (visitproc)ng_update_visit, a);
}


static char ng_update_doc[] =
"NG.update(X:iterable)\n\
\n\
Update NG with the edges from X,\n\
specified as pairs of the form (source, target).";


static PyObject *
ng_update(NyNodeGraphObject *ng, PyObject *arg)
{
    if (NyNodeGraph_Update(ng, arg) == -1)
      return 0;
    Py_INCREF(Py_None);
    return Py_None;
}

static char ng_updated_doc[] =
"NG.updated(X:iterable) -> NodeGraph\n\
\n\
Return a copy of NG updated with the edges from X,\n\
specified as pairs of the form (source, target).";

static PyObject *
ng_updated(NyNodeGraphObject *ng, PyObject *arg)
{
    ng = NyNodeGraph_Copy(ng);
    if (!ng)
      return 0;
    if (NyNodeGraph_Update(ng, arg) == -1) {
	Py_DECREF(ng);
	return 0;
    }
    return (PyObject *)ng;
}

static PyMethodDef ng_methods[] = {
    {"add_edge", (PyCFunction)ng_add_edge, METH_VARARGS, ng_add_edge_doc},
    {"add_edges_n1", (PyCFunction)ng_add_edges_n1, METH_VARARGS, ng_add_edges_n1_doc},
    {"as_flat_list", (PyCFunction)ng_as_flat_list, METH_NOARGS, ng_as_flat_list_doc},
    {"clear", (PyCFunction)ng_clear_method, METH_NOARGS, ng_clear_doc},
    {"copy", (PyCFunction)ng_copy, METH_NOARGS, ng_copy_doc},
    {"domain_covers", (PyCFunction)ng_domain_covers, METH_O, ng_domain_covers_doc},
    {"domain_restricted", (PyCFunction)ng_domain_restricted, METH_O, ng_domain_restricted_doc},
    {"get_domain", (PyCFunction)ng_get_domain, METH_NOARGS, ng_get_domain_doc},
    {"get_range", (PyCFunction)ng_get_range, METH_NOARGS, ng_get_range_doc},
    {"invert", (PyCFunction)ng_invert, METH_NOARGS, ng_invert_doc},
    {"inverted", (PyCFunction)ng_inverted, METH_NOARGS, ng_inverted_doc},
    {"relimg", (PyCFunction)ng_relimg, METH_O, ng_relimg_doc},
    {"update", (PyCFunction)ng_update, METH_O, ng_update_doc},
    {"updated", (PyCFunction)ng_updated, METH_O, ng_updated_doc},
    {NULL,		NULL}		/* sentinel */
};

static int
nodegraph_size(PyObject *obj) {
    int z = obj->ob_type->tp_basicsize +
      ((NyNodeGraphObject *)obj)->allo_size * sizeof(NyNodeGraphEdge);
    if (PyObject_IS_GC(obj))
	z += sizeof(PyGC_Head);
    return z;
}

static int
nodegraph_traverse(NyHeapTraverse *t)
{
    NyNodeGraphObject *ng = (void *)t->obj;
    if (t->_hiding_tag_ != ng->_hiding_tag_)
      return ng->ob_type->tp_traverse((PyObject *)ng, t->visit, t->arg);
    return 0;
}

static int
nodegraph_relate(NyHeapRelate *r)
{
    NyNodeGraphObject *ng = (void *)r->src;
    int i;
    char buf[100];
    for (i = 0; i < ng->used_size; i++) {
	if (r->tgt == ng->edges[i].src) {
	    sprintf(buf, "edges[%d].src",i);
	    if (r->visit(NYHR_INTERATTR, PyString_FromString(buf), r))
	      return 0;
	}
	if (r->tgt == ng->edges[i].tgt) {
	    sprintf(buf, "edges[%d].tgt",i);
	    if (r->visit(NYHR_INTERATTR, PyString_FromString(buf), r))
	      return 0;
	}
    }
    return 0;
}


static char ng_doc[] = 
"NodeGraph([iterable [,is_mapping]])\n\
\n\
Construct a new NodeGraph object. The arguments are:\n\
\n\
    iterable         An iterable object that will be used to\n\
                     initialize the new nodegraph. It should yield a\n\
                     sequence of edges of the form (source, target).\n\
\n\
    is_mapping       A boolean which, if True, will cause the nodegraph\n\
                     to be treated like a 'mapping'. It will then, for the\n\
                     purpose of indexing, be expected to contain a single\n\
                     target for each source node.\n\
\n\
A NodeGraph object contains pairs of nodes (edges) and can be indexed\n\
on the first node of the pair (the source of an edge) to find all\n\
second nodes of such pairs (the targets of those edges).\n\
\n\
NodeGraph objects are used internally in the heapy system, for example\n\
to record dict ownership and shortest-path graphs.\n\
\n\
They may be used generally for mapping and dict-like purposes, but\n\
differ in the following:\n\
\n\
o The mapping is based on object identity - no equality or hashing is\n\
  assumed, so any object can be used as a key. Only the address is used.\n\
  To distinguish this usage from that of ordinary dicts and sets, such\n\
  objects are called 'nodes'.\n\
\n\
o There may be any number of targets associated with each source.\n\
\n\
o Performance characteristics differ from dicts, in somewhat subtle ways.\n\
";


static PyGetSetDef ng_getset[] = {
    {0}
};

#define OFF(x) offsetof(NyNodeGraphObject, x)

static PyMemberDef ng_members[] = {
    {"_hiding_tag_",	 T_OBJECT_EX, OFF(_hiding_tag_), 0,
"The hiding tag: if it is the the same object as the hiding tag\n\
of a HeapView object, the nodegraph will be hidden from that view."},
    {"is_mapping", T_UBYTE, OFF(is_mapping), READONLY,
"NG.is_mapping : boolean kind, read only\n\
\n\
True if NG is a 'mapping'. Then, only one edge is allowed for each\n\
source; indexing returns the actual target object instead of a tuple\n\
of targets."},
    {"is_sorted", T_UBYTE, OFF(is_sorted), READONLY,
"NG.is_sorted : boolean kind, read only\n\
\n\
True if NG is sorted. It will become unsorted after any update. It\n\
will need to be sorted to make it possible to find edges\n\
(implementation uses binary search). Any indexing operation will\n\
automatically sort it if it was not already sorted.  The flag is\n\
currently used from Python to see if the nodegraph has been used at\n\
least once after update, so that it will not be cleared too early."},
    {NULL} /* Sentinel */

};

#undef OFF


static Py_ssize_t
ng_length(PyObject *_ng)
{
    NyNodeGraphObject *ng=(void*)_ng;
    ng_maybesortetc(ng);
    return ng->used_size;
}


static PyObject *
ng_subscript(NyNodeGraphObject *ng, PyObject *obj)
{
    NyNodeGraphEdge *lo, *hi;
    PyObject *ret;
    int i, size;
    ng_maybesortetc(ng);
    if (NyNodeGraph_Region(ng, obj, &lo, &hi) == -1) {
	return 0;
    }
    size = hi - lo;
    if (ng->is_mapping) {
	if (size == 0) {
	    PyErr_SetObject(PyExc_KeyError, obj);
	    return 0;
	} else if (size > 1) {
	    PyErr_SetString(PyExc_ValueError, "Ambiguos mapping");
	    return 0;
	}
	ret = lo->tgt;
	Py_INCREF(ret);
    } else {
	ret = PyTuple_New(size);
	if (!ret)
	  return 0;
	for (i = 0; i < size; i++, lo++) {
	    Py_INCREF(lo->tgt);
	    PyTuple_SET_ITEM(ret, i, lo->tgt);
	}
    }

    return ret;
    

}


static int
ng_ass_sub(NyNodeGraphObject *ng, PyObject *v, PyObject *w)
{
    NyNodeGraphEdge *lo, *hi;
    int i, regsize, tupsize;
    if (!w) {
	PyErr_SetString(PyExc_NotImplementedError,
			"Item deletion is not implemented for nodegraphs.");
	return -1;
    }
    ng_maybesortetc(ng);
    if (NyNodeGraph_Region(ng, v, &lo, &hi) == -1) {
	return 0;
    }
    regsize = hi - lo;
    if (ng->is_mapping) {
	if (regsize != 1) {
	    PyErr_SetString(PyExc_ValueError,
"ng_ass_sub: can not change number of edges (wants to always be fast);\n"
"consider using .add_edge() etc. instead.");
	    return -1;
	} else {
	    PyObject *old = lo->tgt;
	    lo->tgt = w;
	    Py_INCREF(w);
	    Py_DECREF(old);
	}
    } else {
	if (!PyTuple_Check(w)) {
	    PyErr_SetString(PyExc_TypeError, "ng_ass_sub: value to assign must be a tuple");
	    return -1;
	}
	tupsize = PyTuple_GET_SIZE(w);
	if (tupsize != regsize) {
	    PyErr_SetString(PyExc_ValueError,
"ng_ass_sub: can not change number of edges (wants to always be fast);\n"
"consider using .add_edge() etc. instead.");
	    return -1;
	}
	for (i = 0; i < regsize; i++) {
	    PyObject *old = lo[i].tgt;
	    lo[i].tgt = PyTuple_GET_ITEM(w, i);
	    Py_INCREF(lo->tgt);
	    Py_XDECREF(old);
	}
    }
    return 0;
}



static PyMappingMethods ng_as_mapping = {
    ng_length,		       /*mp_length*/
    (binaryfunc)ng_subscript, /*mp_subscript*/
    (objobjargproc)ng_ass_sub,/*mp_ass_subscript*/
};


static PyObject *
ng_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *iterable = 0;
    PyObject *is_mapping = 0;
    static char *kwlist[] = {"iterable", "is_mapping", 0};
    NyNodeGraphObject *ng;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OO:NodeGraph.__new__",
				     kwlist,
				     &iterable,
				     &is_mapping))
      return 0;
    ng = NyNodeGraph_SubtypeNew(type);
    if (!ng)
      return 0;
    if (is_mapping && PyObject_IsTrue(is_mapping)) {
	ng->is_mapping = 1;
    }
    if (iterable && iterable != Py_None && NyNodeGraph_Update(ng, iterable) == -1) {
	Py_DECREF(ng);
	return 0;
    }
    return (PyObject *)ng;
}


PyTypeObject NyNodeGraph_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.heapy.heapyc.NodeGraph",		/* tp_name */
	sizeof(NyNodeGraphObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)ng_dealloc, 		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	&ng_as_mapping,				/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
	  	Py_TPFLAGS_BASETYPE,		/* tp_flags */
 	ng_doc,					/* tp_doc */
 	(traverseproc)ng_gc_traverse,		/* tp_traverse */
 	(inquiry)ng_gc_clear,			/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)ng_iter,			/* tp_iter */
	0,					/* tp_iternext */
	ng_methods,				/* tp_methods */
	ng_members,				/* tp_members */
	ng_getset,				/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	ng_new,					/* tp_new */
	_PyObject_GC_Del,			/* tp_free */

};

NyNodeGraphObject *
NyNodeGraph_New(void)
{
    return NyNodeGraph_SubtypeNew(&NyNodeGraph_Type);
}

int
NyNodeGraph_init(void) {
    return 0;
}
