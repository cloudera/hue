/* Implementation of the NodeSet, ImmNodeSet, and MutNodeSet types */

#include "Python.h"
#include "structmember.h"

#include "../include/guppy.h"
#include "../heapy/heapdef.h"
#include "sets_internal.h"

PyDoc_STRVAR(nodeset_doc, 
"The class NodeSet is the base class for ImmNodeSet and MutNodeSet.\n"
"A nodeset is a set of objects with equality based on heap address.\n"
"The following operations are defined for both mutable and immutable\n"
"nodesets.\n"
"\n"
"------------------------------------------\n"
"Binary operations.\n"
"\n"
"The following operations all return an immutable nodeset.\n"
"The left argument must be a nodeset. The right argument\n"
"can be any iterable object.\n"
"\n"
"x & y    -> Intersection: the set of\n"
"            objects that are in both x and y.\n"
"\n"
"x | y    -> Union: the set of\n"
"            objects that are in either x or y.\n"
"\n"
"x ^ y    -> Symmetric difference: the set of\n"
"            objects that are in exactly one of x and y.\n"
"\n"
"x - y    -> Difference: the set of\n"
"            objects that are in x but not in y.\n"
"\n"
"------------------------------------------\n"
"In-place binary operations.\n"
"\n"
"The left argument can be mutable or immutable.\n"
"If it is mutable, it is updated in place and returned.\n"
"If it is immutable, the result is a new immutable nodeset.\n"
"The right argument can be any iterable object.\n"
"\n"
"x &= y    -> Intersection\n"
"\n"
"x |= y    -> Union\n"
"\n"
"x ^= y    -> Symmetric difference\n"
"\n"
"x -= y    -> Difference\n"
"\n"
"------------------------------------------\n"
"Inclusion test.\n"
"\n"
"The left argument can be any object.\n"
"The right argument is a nodeset.\n"
"\n"
"x in y    -> bool\n"
"             True if x is an element of y, False otherwise.\n"
"\n"
"------------------------------------------\n"
"Relational operations.\n"
"\n"
"These return a boolean value.\n"
"The left argument is a nodeset.\n"
"The right argument is a nodeset.\n"
"If the right argument is another type, TypeError will be raised.\n"
"(This may be relaxed in future.)\n"
"\n"
"x == y    -> Equal:\n"
"             x and y contain the same elements.\n"
"\n"
"x != y    -> Not equal:\n"
"             x and y do not contain the same elements.\n"
"\n"
"x <= y    -> Subset, non-strict:\n"
"             all elements in x are also in y.\n"
"\n"
"x < y     -> Subset, strict:\n"
"             all elements in x are also in y,\n"
"             and y contains some element not in x.\n"
"\n"
"x >= y    -> Superset, non-strict:\n"
"             all elements in y are also in x.\n"
"\n"
"x > y     -> Superset, strict:\n"
"             all elements in y are also in x,\n"
"             and x contains some element not in y.\n"
"\n"
"------------------------------------------\n"
"Iteration.\n"
"\n"
"iter(x)    -> iterator\n"
"\n"
"The iterator yields the elements of x.\n"
"\n"
"[The order is implementation dependent.]\n"
" \n"
"\n"
"------------------------------------------\n"
"Length.\n"
"\n"
"len(x)    -> int\n"
"\n"
"Return the number of elements in x.\n"
"\n"
"------------------------------------------\n"
"Truth-value testing.\n"
"\n"
"bool(x)    -> bool\n"
"\n"
"Return True if x is not empty, False otherwise.\n"
);

PyDoc_STRVAR(mutnodeset_doc,
"MutNodeSet([iterable])\n"
"\n"
"Return a new mutable nodeset with elements from iterable.\n"
"\n"
"A mutable nodeset inherits the operations defined for NodeSet.\n"
"It also supports the following methods:\n"
"\n"
"    add, append, clear, discard, pop, remove, tac, tas.\n"
);

#define ALIGN  sizeof(void *)
#define ALIGN_MASK (ALIGN - 1)

/* Forward decls */

static PyObject * nodeset_bitno_to_obj(NyBit bitno);
PyTypeObject NyImmNodeSet_Type;
PyTypeObject NyMutNodeSet_Type;

NyNodeSetObject *
NyImmNodeSet_SubtypeOfNodeSetDecRef(PyTypeObject *type, NyNodeSetObject *v);
NyNodeSetObject *
NyImmNodeSet_New(int size, PyObject *hiding_tag);

static NyNodeSetObject *
immnodeset_op(NyNodeSetObject *v, NyNodeSetObject *w, int op);


/* */

/* general utilities */

static int
iterable_iterate(PyObject *v, NyIterableVisitor visit,
		void *arg)
{
    if (NyNodeSet_Check(v)) {
	return NyNodeSet_iterate((NyNodeSetObject *)v, visit, arg);
    } else {
	PyObject *it = PyObject_GetIter(v);
	int r;
	if (it == NULL)
	  goto Err;
	/* Run iterator to exhaustion. */
	for (;;) {
	    PyObject *item = PyIter_Next(it);
	    if (item == NULL) {
		if (PyErr_Occurred())
		  goto Err;
		break;
	    }
	    r = visit(item, arg);
	    Py_DECREF(item);
	    if (r == -1)
	      goto Err;
	}
	Py_DECREF(it);
	return 0;
      Err:
	Py_XDECREF(it);
	return -1;
    }
}

static PyObject *
bool_from_int(int res)
{
    PyObject *ret;
    if (res == -1)
      ret = 0;
    else {
	ret = res ? Py_True:Py_False;
	Py_INCREF(ret);
    }
     return ret;
}



/* NyMutNodeSetIter methods */

static PyObject *nodeset_ior(NyNodeSetObject *v, PyObject *w);

typedef struct {
	PyObject_HEAD
	PyObject *bitset_iter;
	NyNodeSetObject *nodeset; /* Need to hold on to this 'cause it shouldn't decref
				     objects in set*/
} NyMutNodeSetIterObject;


static void
mutnsiter_dealloc(NyMutNodeSetIterObject *v)
{
	Py_DECREF(v->bitset_iter);
	Py_DECREF(v->nodeset);
	PyObject_DEL(v);
}

static PyObject *
mutnsiter_getiter(PyObject *it)
{
	Py_INCREF(it);
	return it;
}

static PyObject *
mutnsiter_iternext(NyMutNodeSetIterObject *hi)
{
    PyObject *bitobj =  hi->bitset_iter->ob_type->tp_iternext(hi->bitset_iter);
    PyObject *ret;
    NyBit bitno;
    if (!bitobj)
      return 0;
    bitno = PyInt_AsLong(bitobj);
    if (bitno == -1 && PyErr_Occurred())
      return 0;
    ret = nodeset_bitno_to_obj(bitno);
    Py_DECREF(bitobj);
    if (hi->nodeset->flags & NS_HOLDOBJECTS) {
	Py_INCREF(ret);
    } else {
	ret = PyInt_FromLong((Py_intptr_t)ret);
    }
    return ret;
}

PyTypeObject NyMutNodeSetIter_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"nodeset-iterator",			/* tp_name */
	sizeof(NyMutNodeSetIterObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)mutnsiter_dealloc, 		/* tp_dealloc */
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
	Py_TPFLAGS_DEFAULT,			/* tp_flags */
 	0,					/* tp_doc */
 	0,					/* tp_traverse */
 	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)mutnsiter_getiter,		/* tp_iter */
	(iternextfunc)mutnsiter_iternext,		/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
};



/* NodeSet methods */

NyNodeSetObject *
NyMutNodeSet_SubtypeNewFlags(PyTypeObject *type, int flags, PyObject *hiding_tag)
{
    NyNodeSetObject *v = (void *)type->tp_alloc(type, 0);
    if (!v)
      return NULL;
    /*assert (flags & NS_HOLDOBJECTS); */
    v->flags = flags;
    v->ob_size = 0;
    v->u.bitset = (PyObject *)NyMutBitSet_New();
    if (!v->u.bitset) {
	Py_DECREF(v);
	return 0;
    }
    v->_hiding_tag_ = hiding_tag;
    Py_XINCREF(hiding_tag);
    return v;
}

NyNodeSetObject *
NyMutNodeSet_SubtypeNewIterable(PyTypeObject *type, PyObject *iterable, PyObject *hiding_tag)
{
    NyNodeSetObject *ns = NyMutNodeSet_SubtypeNewFlags(type, NS_HOLDOBJECTS, hiding_tag);
    if (!ns)
      return 0;
    if (iterable) {
	PyObject *r = nodeset_ior(ns, iterable);
	if (!r) {
	    Py_DECREF(ns);
	    return 0;
	}
	Py_DECREF(r);
    }
    return ns;
}

NyNodeSetObject *
NyMutNodeSet_NewFlags(int flags)
{
    return NyMutNodeSet_SubtypeNewFlags(&NyMutNodeSet_Type, flags, 0);
}

NyNodeSetObject *
NyMutNodeSet_New(void)
{
    return NyMutNodeSet_NewFlags(NS_HOLDOBJECTS);
}

NyNodeSetObject *
NyMutNodeSet_NewHiding(PyObject *hiding_tag) {
    return NyMutNodeSet_SubtypeNewFlags(&NyMutNodeSet_Type, NS_HOLDOBJECTS, hiding_tag);
}



static PyObject *
mutnodeset_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{

    PyObject *iterable = NULL;
    static char *kwlist[] = {"iterable", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O:MutNodeSet.__new__",kwlist, &iterable))
      return 0;
    return (PyObject *)NyMutNodeSet_SubtypeNewIterable(type, iterable, 0);
}

static NyBit
nodeset_obj_to_bitno(PyObject *obj)
{
    return (unsigned long) obj / ALIGN;
}

static PyObject *
nodeset_bitno_to_obj(NyBit bitno)
{
    return (PyObject *)(bitno * ALIGN);
}

static PyObject *
nodeset_bitset(NyNodeSetObject *v) {
    if (NyMutNodeSet_Check(v)) {
	Py_INCREF(v->u.bitset);
	return v->u.bitset;
    } else {
	int i;
	NyMutBitSetObject *bitset = NyMutBitSet_New();
	if (!bitset)
	  return 0;
	for (i = 0; i < v->ob_size; i++) {
	    int r = NyMutBitSet_setbit(bitset, nodeset_obj_to_bitno(v->u.nodes[i]));
	    if (r == -1) {
		Py_DECREF(bitset);
		return 0;
	    }
	}
	return (PyObject *)bitset;
    }
}





static int
nodeset_dealloc_iter(PyObject *obj, void *v)
{
    Py_DECREF(obj);
    return 0;
}

static int
mutnodeset_gc_clear(NyNodeSetObject *v)
{
    if (v->u.bitset) {
	PyObject *x = v->u.bitset;
	if (v->flags & NS_HOLDOBJECTS) {
	    NyNodeSet_iterate(v, nodeset_dealloc_iter, v);
	}
	v->u.bitset = 0;
	Py_DECREF(x);
    }
    if (v->_hiding_tag_) {
	PyObject *x = v->_hiding_tag_;
	v->_hiding_tag_ = 0;
	Py_DECREF(x);
    }
    return 0;
}

static void
mutnodeset_dealloc(NyNodeSetObject *v)
{
    _PyObject_GC_UNTRACK(v);
    Py_TRASHCAN_SAFE_BEGIN(v)
    mutnodeset_gc_clear(v);
    v->ob_type->tp_free((PyObject *)v);
    Py_TRASHCAN_SAFE_END(v)
}

int
nodeset_indisize(PyObject *v)
{
    NyNodeSetObject *ns = (void *)v;
    int r = generic_indisize(v);
    if (NyMutNodeSet_Check(v))
	r += anybitset_indisize(ns->u.bitset);
    return r;
}


int
nodeset_traverse(NyHeapTraverse *ta)
{
    NyNodeSetObject *v = (void *)ta->obj;
    int err = 0;
    if (ta->_hiding_tag_ != v->_hiding_tag_) {
	err = v->ob_type->tp_traverse(ta->obj, ta->visit, ta->arg);
    }
    return err;
}

typedef struct {
    NyHeapRelate *r;
    int i;
} RelateTravArg;

static int
nodeset_relate_visit(PyObject *obj, RelateTravArg *ta)
{
    NyHeapRelate *r = ta->r;

    if (r->tgt == obj) {
	char buf[100];
	sprintf(buf, "list(%%s)[%d]",ta->i);
	r->visit(NYHR_RELSRC, PyString_FromString(buf), r);
	return 1;
    }
    ta->i++;
    return 0;
}

int
nodeset_relate(NyHeapRelate *r)
{
    RelateTravArg ta;
    ta.r = r;
    ta.i = 0;
    return NyNodeSet_iterate((NyNodeSetObject *)r->src, (visitproc)nodeset_relate_visit, &ta);
}


static int
mutnodeset_gc_traverse(NyNodeSetObject *v, visitproc visit, void *arg)
{
    int err = 0;
    if (v->flags & NS_HOLDOBJECTS) {
	err = NyNodeSet_iterate(v, visit, arg);
	if (err)
	  return err;
    }
    if (v->_hiding_tag_) {
	err = visit(v->_hiding_tag_, arg);
    }
    return err;
}

typedef struct {
    NyNodeSetObject *ns;
    void *arg;
    int (*visit)(PyObject *, void *);
} nodeset_iterate_visit_arg;


static int
mutnodeset_iterate_visit(NyBit bitno, nodeset_iterate_visit_arg *arg)
{
    PyObject *obj = nodeset_bitno_to_obj(bitno);
    if (arg->ns->flags & NS_HOLDOBJECTS)
      return arg->visit(obj, arg->arg);
    else {
	PyObject *addr = PyInt_FromLong((Py_intptr_t)obj);
	if (addr) {
	    int r = arg->visit(addr, arg->arg);
	    Py_DECREF(addr);
	    return r;
	} else
	  return -1;
    }
}


int
NyNodeSet_iterate(NyNodeSetObject *ns, int (*visit)(PyObject *, void *),
		void *arg)
{
    nodeset_iterate_visit_arg hia;
#if 1
    if (!(ns->flags & NS_HOLDOBJECTS)) {
	PyErr_SetString(PyExc_ValueError,
	"NyNodeSet_iterate: can not iterate because not owning element nodes");
	return -1;
    }
#endif
    hia.ns = ns;
    hia.arg = arg;
    hia.visit = visit;
    if (NyMutNodeSet_Check(ns)) {
	return NyAnyBitSet_iterate(ns->u.bitset,
				   (NySetVisitor)mutnodeset_iterate_visit,
				   &hia);
    } else {
	int i;
	for (i = 0; i < ns->ob_size; i++) {
	    if (visit(ns->u.nodes[i], arg) == -1)
	      return -1;
	}
	return 0;
    }
}

PyObject *
mutnodeset_iter(NyNodeSetObject *v)
{
    PyObject *bitset_iter;
    NyMutNodeSetIterObject *iter;
#if 0
    if (!(v->flags & NS_HOLDOBJECTS)) {
	PyErr_SetString(PyExc_ValueError,
	"nodeset_iter: can not iterate because not owning element nodes");
	return 0;;
    }
#endif
    bitset_iter = v->u.bitset->ob_type->tp_iter(v->u.bitset);
    if (!bitset_iter)
      return 0;
    iter = PyObject_New(NyMutNodeSetIterObject, &NyMutNodeSetIter_Type);
    if (!iter) {
	Py_DECREF(bitset_iter);
	return 0;
    }
    iter->bitset_iter = bitset_iter;
    iter->nodeset = v;
    Py_INCREF(v);
    return (PyObject *)iter;
}



static PyObject *
nodeset_richcompare(NyNodeSetObject *v, NyNodeSetObject *w, int op)
{
    if (!NyNodeSet_Check(v) || !NyNodeSet_Check(w)) {
	if (op == Py_EQ) {
	    Py_INCREF(Py_False);
	    return Py_False;
	} else if (op == Py_NE) {
	    Py_INCREF(Py_True);
	    return Py_True;
	}
	    
	PyErr_SetString(PyExc_TypeError, "nodeset_richcompare: some nodeset expected");
	return 0;
/*	We might consider NotImplemented but ... we might want
	to implement it and then we would get a compatibility problem!
	See also Notes May 19 2005.

	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
*/
    } else {
	PyObject *bsv = nodeset_bitset(v);
	PyObject *bsw = nodeset_bitset(w);
	PyObject *ret;
	if (!(bsv && bsw)) {
	    Py_XDECREF(bsv);
	    Py_XDECREF(bsw);
	    return 0;
	}
	ret = PyObject_RichCompare(bsv, bsw, op);
	Py_DECREF(bsv);
	Py_DECREF(bsw);
	return ret;
    }
}


int
NyNodeSet_hasobj(NyNodeSetObject *v, PyObject *obj)
{
    if (NyImmNodeSet_Check(v)) {
	int lo, hi;
	lo = 0;
	hi = v->ob_size;
	while (hi > lo) {
	    int i = (hi + lo) / 2;
	    PyObject *node = v->u.nodes[i];
	    if (node == obj)
	      return 1;
	    else if ((Py_uintptr_t)node < (Py_uintptr_t)obj)
	      lo = i + 1;
	    else
	      hi = i;
	}
	return 0;
	
    } else {
	NyBit bitno = nodeset_obj_to_bitno(obj);
	return NyMutBitSet_hasbit((NyMutBitSetObject *)v->u.bitset, bitno);
    }
}


int
NyNodeSet_setobj(NyNodeSetObject *v, PyObject *obj)
{
    if (NyMutNodeSet_Check(v)) {
	NyBit bitno = nodeset_obj_to_bitno(obj);
	int r = NyMutBitSet_setbit((NyMutBitSetObject *)v->u.bitset, bitno);
	if (r == -1)
	  return -1;
	if (!r) {
	    v->ob_size++;
	    if (v->flags & NS_HOLDOBJECTS) {
		Py_INCREF(obj);
	    }
	}
	return r;
    } else {
	PyErr_Format(PyExc_ValueError,
		     "mutable nodeset required");
	return -1;
    }
}

int
NyNodeSet_clear(NyNodeSetObject *v)
{
    if (NyMutNodeSet_Check(v) && v->u.bitset) {
	if (v->flags & NS_HOLDOBJECTS) {
	    NyNodeSet_iterate(v, nodeset_dealloc_iter, v);
	}
	if (NyMutBitSet_clear((NyMutBitSetObject *)v->u.bitset) == -1)
	  return -1;
	v->ob_size = 0;
    } else {
	PyErr_Format(PyExc_ValueError,
		     "mutable nodeset required");
	return -1;
    }
    return 0;
}


int
NyNodeSet_clrobj(NyNodeSetObject *v, PyObject *obj)
{
    if (NyMutNodeSet_Check(v)) {
	NyBit bitno = nodeset_obj_to_bitno(obj);
	int r = NyMutBitSet_clrbit((NyMutBitSetObject *)v->u.bitset, bitno);
	if (r == -1)
	  return -1;
	if (r) {
	    v->ob_size--;
	    if (v->flags & NS_HOLDOBJECTS) {
		Py_DECREF(obj);
	    }
	}
	return r;
    } else {
	PyErr_Format(PyExc_ValueError,
		     "immutable nodeset");
	return -1;
    }
}

int
NyNodeSet_invobj(NyNodeSetObject *v, PyObject *obj)
{
    if (NyMutNodeSet_Check(v)) {
	if (NyNodeSet_hasobj(v, obj))
	  return NyNodeSet_clrobj(v, obj);
	else
	  return NyNodeSet_setobj(v, obj);
    } else {
	PyErr_Format(PyExc_ValueError,
		     "immutable nodeset");
	return -1;
    }
}

static char add_doc[] =
"S.add(e)\n"
"\n"
"Add e to S; no effect if e was already in S.";

static PyObject *
nodeset_add(NyNodeSetObject *v, PyObject *obj)
{
    if (NyNodeSet_setobj(v, obj) == -1)
      return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static char append_doc[] =
"S.append(e)\n"
"\n"
"Add e to S, or raise ValueError if e was already in S.";

static PyObject *
nodeset_append(NyNodeSetObject *v, PyObject *obj)
{
    int r = NyNodeSet_setobj(v, obj);
    if (r == -1)
      return NULL;
    if (r) {
	PyErr_SetString(PyExc_ValueError, "S.append(e): e is already in S");
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static char clear_doc[] =
"S.clear()\n"
"\n"
"Remove all elements from S, and compact its storage.";

static PyObject *
nodeset_clear(NyNodeSetObject *v, PyObject *notused)
{
    if (NyNodeSet_clear(v) == -1)
      return 0;
    Py_INCREF(Py_None);
    return Py_None;

}

static char discard_doc[] =
"S.discard(e)\n"
"\n"
"Remove e from S; no effect if e was not in S.";

static PyObject *
nodeset_discard(NyNodeSetObject *v, PyObject *obj)
{
    if (NyNodeSet_clrobj(v, obj) == -1)
      return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static char pop_doc[] =
"S.pop() -> object\n"
"\n"
"Remove and return some object from S, or raise ValueError if S was empty.";

static PyObject *
nodeset_pop(NyNodeSetObject *v, PyObject *argnotused)
{
    if (!(NyMutNodeSet_Check(v))) {
	PyErr_SetString(PyExc_TypeError, "pop: argument must be mutable");
	return 0;
    } else {
	long bitno = NyMutBitSet_pop((NyMutBitSetObject *)v->u.bitset, 0);
	if (bitno == -1 && PyErr_Occurred())
	  return 0;
	return nodeset_bitno_to_obj(bitno);
    }
}

static char remove_doc[] =
"S.remove(e)\n"
"\n"
"Remove e from S, or raise ValueError if e was not in S.";

static PyObject *
nodeset_remove(NyNodeSetObject *v, PyObject *obj)
{
    int r = NyNodeSet_clrobj(v, obj);
    if (r == -1)
      return NULL;
    if (!r) {
	PyErr_SetString(PyExc_ValueError, "S.remove(e): e not in S");
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static char tas_doc[] =
"S.tas(e) -> bool\n"
"\n"
"Test and Set.\n"
"If e is in S return True,\n"
"else add e to S and return False.";


static PyObject *
nodeset_tas(NyNodeSetObject *v, PyObject *obj)
{
    return bool_from_int(NyNodeSet_setobj(v, obj));
}


static char tac_doc[] =
"S.tac(e) -> bool\n"
"\n"
"Test and Clear.\n"
"If e is in S, remove e from S and return True,\n"
"else return False.";


static PyObject *
nodeset_tac(NyNodeSetObject *v, PyObject *obj)
{
    return bool_from_int(NyNodeSet_clrobj(v, obj));
}

typedef struct {
    NyNodeSetObject *ns;
    int i;
} NSOPARG;

static int
nodeset_op_set(NyBit bitno, NSOPARG *arg)
{
    PyObject *obj = nodeset_bitno_to_obj(bitno);
    arg->ns->u.nodes[arg->i] = obj;
    Py_INCREF(obj);
    arg->i += 1;
    return 0;
}



static PyObject *
nodeset_op(PyObject *vv, PyObject *ww, int op)
{
    if (NyImmNodeSet_Check(vv) && NyImmNodeSet_Check(ww)) {
	return (PyObject *)immnodeset_op((NyNodeSetObject *)vv, (NyNodeSetObject *)ww, op);
    } else {
	NyNodeSetObject *v = (void *)vv;
	NyNodeSetObject *w = 0;
	NyNodeSetObject *ret=0;
	PyObject *bs = 0, *bsv = 0, *bsw = 0;
	long length;
	NSOPARG nsa;
	if (!NyNodeSet_Check(v)) {
	    PyErr_SetString(PyExc_TypeError, "left argument must be a NodeSet");
	    return 0;
	}
	if (!NyNodeSet_Check(ww)) {
	    PyObject *p;
	    w = NyMutNodeSet_New();
	    if (!w)
	      goto err;
	    p = nodeset_ior(w, ww);
	    if (!p)
	      goto err;
	    else
	      Py_DECREF(p);
	} else {
	    w = (void *)ww;
	    Py_INCREF(w);
	    if (w->_hiding_tag_ != v->_hiding_tag_) {
		PyErr_SetString(PyExc_ValueError, "nodeset_op: mismatching '_hiding_tag_' attributes");
		goto err;
	    }
	}
	bsv = nodeset_bitset(v);
	if (!bsv)
	  goto err;
	bsw = nodeset_bitset(w);
	if (!bsw)
	  goto err;
	switch(op) {
	  case NyBits_AND:
	    bs = PyNumber_And(bsv, bsw);
	    break;
	  case NyBits_OR:
	    bs = PyNumber_Or(bsv, bsw);
	    break;
	  case NyBits_XOR:
	    bs = PyNumber_Xor(bsv, bsw);
	    break;
	  case NyBits_SUB:
	    bs = PyNumber_Subtract(bsv, bsw);
	    break;
	  default:
	    PyErr_SetString(PyExc_ValueError, "Invalid internal operation");
	    bs = 0;
	}
	if (!bs)
	  goto err;
	
	length = NyAnyBitSet_length(bs);
	if (length == -1)
	  goto err;
	ret = NyImmNodeSet_New(length, v->_hiding_tag_);
	if (!ret)
	  goto err;
	nsa.ns = ret;
	nsa.i = 0;
	if (NyAnyBitSet_iterate(bs, (NySetVisitor)nodeset_op_set, &nsa) == -1)
	  goto err;
	Py_DECREF(w);
	Py_DECREF(bs);
	Py_DECREF(bsv);
	Py_DECREF(bsw);
	return (void *)ret;
      err:
	Py_XDECREF(w);
	Py_XDECREF(bs);
	Py_XDECREF(bsv);
	Py_XDECREF(bsw);
	Py_XDECREF(ret);
	return 0;
    }
}

static PyObject *
nodeset_sub(PyObject *v, PyObject *w)
{
    return nodeset_op(v, w, NyBits_SUB);
}

static PyObject *
nodeset_and(PyObject *v, PyObject *w)
{
    return nodeset_op(v, w, NyBits_AND);
}

static PyObject *
nodeset_or(PyObject *v, PyObject *w)
{
    return nodeset_op(v, w, NyBits_OR);
}


static PyObject *
nodeset_xor(PyObject *v, PyObject *w)
{
    return nodeset_op(v, w, NyBits_XOR);
}

typedef struct {
    NyNodeSetObject *ns;
    int (*visit)(NyNodeSetObject *, PyObject *);
} IOPTravArg;


static int
nodeset_iop_iterable_visit(PyObject *obj, IOPTravArg *ta)
{
    if (ta->visit(ta->ns, obj) == -1)
      return -1;
    return 0;
}

static PyObject *
nodeset_iop_chk_iterable(NyNodeSetObject *v, PyObject *w,
			 int (*visit)(NyNodeSetObject *, PyObject *)) {
    IOPTravArg ta;
    ta.ns = v;
    ta.visit = visit;
    if (!(NyMutNodeSet_Check(v))) {
	PyErr_SetString(PyExc_TypeError, "iop: left argument must be mutable");
	return 0;
    }
    if (iterable_iterate((PyObject *)w,
			 (NyIterableVisitor) nodeset_iop_iterable_visit, &ta) == -1)
      return 0;
    Py_INCREF(v);
    return (PyObject *)v;
}



typedef struct {
    NyNodeSetObject *v, *w;
} IANDTravArg;




static int
nodeset_iand_visit(PyObject *obj, IANDTravArg *ta)
{
    if (!NyNodeSet_hasobj(ta->w, obj)) {
	if (NyNodeSet_clrobj(ta->v, obj) == -1)
	  return -1;
    }
    return 0;
}

static PyObject *
nodeset_iand(NyNodeSetObject *v, PyObject *w)

{
    IANDTravArg ta;
    if (!(NyMutNodeSet_Check(v))) {
	return nodeset_and((PyObject *)v, w);
    }
    ta.v = v;
    ta.w = (NyNodeSetObject *)w;
    if (!NyNodeSet_Check(w)) {
	PyObject *p;
	ta.w = NyMutNodeSet_New();
	if (!ta.w)
	  return 0;
	p = nodeset_ior(ta.w, w);
	if (!p)
	  goto err;
	Py_DECREF(p);
    }
    if (NyNodeSet_iterate(v, (NyIterableVisitor) nodeset_iand_visit, &ta) == -1)
      goto err;
    Py_INCREF(v);
  ret:
    if (ta.w != (void *)w) {
	Py_XDECREF(ta.w);
    }
    return (PyObject *)v;
  err:
    v = 0;
    goto ret;

}

static PyObject *
nodeset_isub(NyNodeSetObject *v, PyObject *w)
{
    if (!(NyMutNodeSet_Check(v)))
      return nodeset_sub((PyObject *)v, w);
    else
      return nodeset_iop_chk_iterable(v, w, NyNodeSet_clrobj);
}

static PyObject *
nodeset_ixor(NyNodeSetObject *v, PyObject *w)
{
    if (!(NyMutNodeSet_Check(v)))
      return nodeset_xor((PyObject *)v, w);
    else
      return nodeset_iop_chk_iterable(v, w, NyNodeSet_invobj);
}

static PyObject *
nodeset_ior(NyNodeSetObject *v, PyObject *w)
{
    if (!(NyMutNodeSet_Check(v)))
      return nodeset_or((PyObject *)v, w);
    else
      return nodeset_iop_chk_iterable(v, w, NyNodeSet_setobj);
}



static Py_ssize_t
nodeset_length(PyObject *_v)
{
    NyNodeSetObject *v=(void*)_v;
    return v->ob_size;
}

static int
nodeset_nonzero(NyNodeSetObject *v)
{
    return v->ob_size != 0;
}

static PyNumberMethods nodeset_as_number = {
        (binaryfunc)	0,		/*nb_add*/
	(binaryfunc)	nodeset_sub,	/*nb_subtract*/
	(binaryfunc)	0,		/*nb_multiply*/
	(binaryfunc)	0,		/*nb_divide*/
	(binaryfunc)	0,		/*nb_remainder*/
	(binaryfunc)	0,		/*nb_divmod*/
	(ternaryfunc)	0,		/*nb_power*/
	(unaryfunc) 	0,		/*nb_negative*/
	(unaryfunc) 	0,		/*tp_positive*/
	(unaryfunc) 	0,		/*tp_absolute*/
	(inquiry)	nodeset_nonzero,/*tp_nonzero*/
	(unaryfunc)	0,		/*nb_invert*/
	(binaryfunc)	0,		/*nb_lshift*/
	(binaryfunc)	0,		/*nb_rshift*/
	(binaryfunc)	nodeset_and,	/*nb_and*/
	(binaryfunc)	nodeset_xor,	/*nb_xor*/
	(binaryfunc)	nodeset_or,	/*nb_or*/
	(coercion)	0,		/*nb_coerce*/
	(unaryfunc)	0,		/*nb_int*/
	(unaryfunc)	0,		/*nb_long*/
	(unaryfunc)	0,		/*nb_float*/
	(unaryfunc)	0,		/*nb_oct*/
	(unaryfunc)	0,		/*nb_hex*/
	0,				/* nb_inplace_add */
	(binaryfunc)nodeset_isub,	/* nb_inplace_subtract */
	0,				/* nb_inplace_multiply */
	0,				/* nb_inplace_divide */
	0,				/* nb_inplace_remainder */
	0,				/* nb_inplace_power */
	0,				/* nb_inplace_lshift */
	0,				/* nb_inplace_rshift */
	(binaryfunc)nodeset_iand,	/* nb_inplace_and */
	(binaryfunc)nodeset_ixor,	/* nb_inplace_xor */
	(binaryfunc)nodeset_ior,	/* nb_inplace_or */
	0,				/* nb_floor_divide */
	0,				/* nb_true_divide */
	0,				/* nb_inplace_floor_divide */
	0,				/* nb_inplace_true_divide */
};

static PyMappingMethods nodeset_as_mapping = {
	nodeset_length,		      /*mp_length*/
	(binaryfunc)0, 		      /*mp_subscript*/
	(objobjargproc)0,	      /*mp_ass_subscript*/
};



/* Implement "obj in nodeset" */

static PySequenceMethods nodeset_as_sequence = {
	0,/* NOT USED - don't want auto-calling this */	/* sq_length */
	0,					/* sq_concat */
	0,					/* sq_repeat */
	0,					/* sq_item */
	0,					/* sq_slice */
	0,					/* sq_ass_item */
	0,					/* sq_ass_slice */
	(objobjproc)NyNodeSet_hasobj,		/* sq_contains */
	0,					/* sq_inplace_concat */
	0,					/* sq_inplace_repeat */
};

static PyMethodDef mutnodeset_methods[] = {
	{"add",		(PyCFunction)nodeset_add, METH_O, add_doc},
	{"append",	(PyCFunction)nodeset_append, METH_O, append_doc},
	{"clear",	(PyCFunction)nodeset_clear, METH_NOARGS, clear_doc},
	{"discard",	(PyCFunction)nodeset_discard, METH_O, discard_doc},
	{"pop",		(PyCFunction)nodeset_pop, METH_NOARGS, pop_doc},
	{"remove",	(PyCFunction)nodeset_remove, METH_O, remove_doc},
	{"tas",		(PyCFunction)nodeset_tas, METH_O, tas_doc},
	{"tac", 	(PyCFunction)nodeset_tac, METH_O, tac_doc},
	{NULL,		NULL}		/* sentinel */
};

#define OFF(x) offsetof(NyNodeSetObject, x)

static PyMemberDef mutnodeset_members[] = {
    {"_hiding_tag_",	 T_OBJECT_EX, OFF(_hiding_tag_)},
    {NULL} /* Sentinel */
};

#undef OFF

PyObject *
nodeset_get_is_immutable(NyNodeSetObject *self, void *unused)
{
    return bool_from_int((NyImmNodeSet_Check(self)));
}

static  PyGetSetDef nodeset_getset[] = {
    {"is_immutable", (getter)nodeset_get_is_immutable, (setter)0,
"S.is_immutable : bool\n"
"\n"
"True if S is immutable, else False."},
  {0}

};

static  PyGetSetDef mutnodeset_getset[] = {
    {"is_immutable", (getter)nodeset_get_is_immutable, (setter)0,
"S.is_immutable == False\n"
"\n"
"False since S is not immmutable."},
  {0}

};

PyTypeObject NyNodeSet_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.sets.setsc.NodeSet",		/* tp_name */
	sizeof(NyNodeSetObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)0,		 		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	&nodeset_as_number,			/* tp_as_number */
	&nodeset_as_sequence,			/* tp_as_sequence */
	&nodeset_as_mapping,			/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_CHECKTYPES |
		Py_TPFLAGS_BASETYPE,		/* tp_flags */
 	nodeset_doc,				/* tp_doc */
 	(traverseproc)mutnodeset_gc_traverse,	/* tp_traverse */
 	(inquiry)mutnodeset_gc_clear,		/* tp_clear */
	(richcmpfunc)nodeset_richcompare,	/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	nodeset_getset,				/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	0,					/* tp_new */
	_PyObject_GC_Del,			/* tp_free */

};


#include "immnodeset.c"

PyTypeObject NyMutNodeSet_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.sets.setsc.MutNodeSet",		/* tp_name */
	sizeof(NyNodeSetObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)mutnodeset_dealloc,		/* tp_dealloc */
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
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_CHECKTYPES |
		Py_TPFLAGS_BASETYPE,		/* tp_flags */
 	mutnodeset_doc,				/* tp_doc */
 	(traverseproc)mutnodeset_gc_traverse,	/* tp_traverse */
 	(inquiry)mutnodeset_gc_clear,		/* tp_clear */
	(richcmpfunc)nodeset_richcompare,	/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)mutnodeset_iter,		/* tp_iter */
	0,					/* tp_iternext */
	mutnodeset_methods,			/* tp_methods */
	mutnodeset_members,			/* tp_members */
	mutnodeset_getset,			/* tp_getset */
	&NyNodeSet_Type,			/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	mutnodeset_new,				/* tp_new */
	_PyObject_GC_Del,			/* tp_free */

};


static NyNodeSet_Exports nynodeset_exports = {
    0,
    sizeof(NyNodeSet_Exports),
    "NyNodeSet_Exports v1.0",
    &NyNodeSet_Type,
    NyMutNodeSet_New,
    NyMutNodeSet_NewHiding,
    NyMutNodeSet_NewFlags,
    NyImmNodeSet_NewCopy,
    NyImmNodeSet_NewSingleton,
    NyNodeSet_be_immutable,
    NyNodeSet_setobj,
    NyNodeSet_clrobj,
    NyNodeSet_hasobj,
    NyNodeSet_iterate,
    
    
};

int fsb_dx_nynodeset_init(PyObject *m)
{
    PyObject *d;

    NYFILL(NyMutNodeSetIter_Type);
    NYFILL(NyNodeSet_Type);
    NYFILL(NyImmNodeSetIter_Type);
    NYFILL(NyImmNodeSet_Type);
    NYFILL(NyMutNodeSet_Type);

    d = PyModule_GetDict(m);

    if (PyDict_SetItemString(d,
			 "NyNodeSet_Exports",
			 PyCObject_FromVoidPtrAndDesc(
						      &nynodeset_exports,
						      "NyNodeSet_Exports v1.0",
						      0)
			 ) == -1) goto Error;

    if (PyType_Ready(&NyNodeSet_Type) == -1)
      goto Error;
    if (PyDict_SetItemString(d, "NodeSet",
			 (PyObject *)&NyNodeSet_Type) == -1)
      goto Error;
    if (PyType_Ready(&NyMutNodeSet_Type) == -1)
      goto Error;
    if (PyDict_SetItemString(d, "MutNodeSet",
			 (PyObject *)&NyMutNodeSet_Type) == -1)
      goto Error;
    if (PyType_Ready(&NyImmNodeSet_Type) == -1)
      goto Error;
    if (PyDict_SetItemString(d, "ImmNodeSet",
			 (PyObject *)&NyImmNodeSet_Type) == -1)
      goto Error;
    return 0;
  Error:
    return -1;
}
