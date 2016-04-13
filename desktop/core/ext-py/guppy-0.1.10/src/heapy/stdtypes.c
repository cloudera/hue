#include "Python.h"
#include "structmember.h"
#include "compile.h"
#include "frameobject.h"
#include "unicodeobject.h"

/* Defining Py_ssize_t for backwards compatibility, from PEP 353 */

#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif


#include "heapdef.h"
#include "stdtypes.h"


#define ALIGNMENT  sizeof(void *)
#define ALIGN_MASK (ALIGNMENT - 1)
#define ALIGN(z)   ((z + ALIGN_MASK) & ~ALIGN_MASK)

#define VISIT(SLOT) \
	if (SLOT) { \
		err = visit((PyObject *)(SLOT), arg); \
		if (err) \
			return err; \
	}

#define ATTR(name) if ((PyObject *)v->name == r->tgt && \
		       (r->visit(NYHR_ATTRIBUTE, PyString_FromString(#name), r))) \
		return 1;

#define RENAMEATTR(name, newname) if ((PyObject *)v->name == r->tgt && \
		       (r->visit(NYHR_ATTRIBUTE, PyString_FromString(#newname), r))) \
		return 1;

#define INTERATTR(name) if ((PyObject *)v->name == r->tgt && \
		       (r->visit(NYHR_INTERATTR, PyString_FromString(#name), r))) \
		return 1;

extern PyObject *_hiding_tag__name;

static int
dict_size(PyObject *obj) {
    int z = obj->ob_type->tp_basicsize;
    PyDictObject *v = (void *)obj;
    if (v->ma_table != v->ma_smalltable)
      z += sizeof(PyDictEntry) * (v->ma_mask + 1);
    if (PyObject_IS_GC(obj))
	z += sizeof(PyGC_Head);
    return z;
}

 int
dict_relate_kv(NyHeapRelate *r, PyObject *dict, int k, int v)
{
    PyObject *pk, *pv;
    Py_ssize_t i = 0;
    int ix = 0;
    if (!dict)
      return 0;
    while (PyDict_Next(dict, &i, &pk, &pv)) {
	if (pk == r->tgt) {
	    if (r->visit(k, PyInt_FromLong(ix), r))
	      return 0;
	}
	if (pv == r->tgt) {
	    Py_INCREF(pk);
	    if (r->visit(v, pk, r))
	      return 0;
	}
	ix++;
    }
    return 0;
}

static int
dict_relate(NyHeapRelate *r)
{
    return dict_relate_kv(r, r->src, NYHR_INDEXKEY, NYHR_INDEXVAL);
}


static int
dictproxy_relate(NyHeapRelate *r)
{
    proxyobject *v = (void *)r->src;
    if (v->dict == r->tgt) {
	if (r->visit(NYHR_INTERATTR, PyString_FromString("dict"), r))
	  return 1;
    }
    return dict_relate_kv(r, v->dict, NYHR_INDEXKEY, NYHR_INDEXVAL);
}


/* From listobject.c */

static int
roundupsize(int n)
{
	unsigned int nbits = 0;
	unsigned int n2 = (unsigned int)n >> 5;

	/* Round up: 
	 * If n <       256, to a multiple of        8.
	 * If n <      2048, to a multiple of       64.
	 * If n <     16384, to a multiple of      512.
	 * If n <    131072, to a multiple of     4096.
	 * If n <   1048576, to a multiple of    32768.
	 * If n <   8388608, to a multiple of   262144.
	 * If n <  67108864, to a multiple of  2097152.
	 * If n < 536870912, to a multiple of 16777216.
	 * ...
	 * If n < 2**(5+3*i), to a multiple of 2**(3*i).
	 *
	 * This over-allocates proportional to the list size, making room
	 * for additional growth.  The over-allocation is mild, but is
	 * enough to give linear-time amortized behavior over a long
	 * sequence of appends() in the presence of a poorly-performing
	 * system realloc() (which is a reality, e.g., across all flavors
	 * of Windows, with Win9x behavior being particularly bad -- and
	 * we've still got address space fragmentation problems on Win9x
	 * even with this scheme, although it requires much longer lists to
	 * provoke them than it used to).
	 */
	do {
		n2 >>= 3;
		nbits += 3;
	} while (n2);
	return ((n >> nbits) + 1) << nbits;
 }

static int
list_size(PyObject *obj) {
    PyListObject *v = (void *)obj;
    int z = v->ob_type->tp_basicsize;
    if (v->ob_item) {
	z += sizeof(void *) * roundupsize(v->ob_size);
    }
    if (PyObject_IS_GC(obj))
	z += sizeof(PyGC_Head);
    return z;
}

static int
list_relate(NyHeapRelate *r)
{
    int len = PyList_Size(r->src);
    int i;
    for (i = 0; i < len; i++) {
	PyObject *o = PyList_GET_ITEM(r->src, i);
	if (o == r->tgt) {
	    PyObject *ix = PyInt_FromLong(i);
	    int x;
	    if (!ix)
	      return -1;
	    x = r->visit(NYHR_INDEXVAL, ix, r);
	    if (x)
	      return 0;
	}
    }
    return 0;
}

static int
tuple_relate(NyHeapRelate *r)
{
    int len = PyTuple_Size(r->src);
    int i;
    for (i = 0; i < len; i++) {
	PyObject *o = PyTuple_GetItem(r->src, i);
	if (o == r->tgt) {
	    PyObject *ix = PyInt_FromLong(i);
	    int x;
	    if (!ix)
	      return -1;
	    x = r->visit(NYHR_INDEXVAL, ix, r);
	    if (x)
	      return 0;
	}
    }
    return 0;
}


static int
instance_relate(NyHeapRelate *r)
{
    PyInstanceObject *in = (void *)r->src;
    if ((PyObject *)in->in_class == r->tgt) {
	if (r->visit(NYHR_ATTRIBUTE, PyString_FromString("__class__"), r))
	  return 0;
    }
    if ((PyObject *)in->in_dict == r->tgt) {
	if (r->visit(NYHR_ATTRIBUTE, PyString_FromString("__dict__"), r))
	  return 0;
    }
    return dict_relate_kv(r, in->in_dict, NYHR_HASATTR, NYHR_ATTRIBUTE);
}
    
static int
instance_traverse(NyHeapTraverse *ta) {
    PyInstanceObject *in = (void *)ta->obj;
    if (PyDict_GetItem(in->in_dict, _hiding_tag__name) == ta->_hiding_tag_)
      return 0;
    return in->ob_type->tp_traverse(ta->obj, ta->visit, ta->arg);
}

static int
class_relate(NyHeapRelate *r)
{
    PyClassObject *cl = (void *)r->src;
    if (cl->cl_bases == r->tgt &&
	(r->visit(NYHR_ATTRIBUTE, PyString_FromString("__bases__"), r)))
      return 1;
    if (cl->cl_dict == r->tgt &&
	(r->visit(NYHR_ATTRIBUTE, PyString_FromString("__dict__"), r)))
      return 1;
    if (cl->cl_name == r->tgt &&
	(r->visit(NYHR_ATTRIBUTE, PyString_FromString("__name__"), r)))
      return 1;
    return dict_relate_kv(r, cl->cl_dict, NYHR_HASATTR, NYHR_ATTRIBUTE);

}

static int
function_relate(NyHeapRelate *r)
{
    PyFunctionObject *v = (void *)r->src;
    ATTR(func_code)
    ATTR(func_globals)
    ATTR(func_defaults)
    ATTR(func_closure)
    ATTR(func_doc)
    ATTR(func_name)
    ATTR(func_dict)
    return dict_relate_kv(r, v->func_dict, NYHR_HASATTR, NYHR_ATTRIBUTE);
}

static int
module_relate(NyHeapRelate *r)
{
    PyModuleObject *v = (void *)r->src;
    if (v->md_dict == r->tgt &&
	(r->visit(NYHR_ATTRIBUTE, PyString_FromString("__dict__"), r)))
      return 1;
    return dict_relate_kv(r, v->md_dict, NYHR_HASATTR, NYHR_ATTRIBUTE);
}

static int
frame_locals(NyHeapRelate *r, PyObject *map, int start, int n, int deref)
{
    PyFrameObject *v = (void *)r->src;
    int i;
    for (i = start; i < start + n; i++) {
	if ((!deref && v->f_localsplus[i] == r->tgt) ||
	    (deref && PyCell_GET(v->f_localsplus[i]) == r->tgt)) {
	    PyObject *name;
	    if (PyTuple_Check(map) && (i - start) < PyTuple_Size(map)) {
		name = PyTuple_GetItem(map, i - start);
		Py_INCREF(name);
	    } else {
		name = PyString_FromString("?");
	    }
	    if (r->visit(deref? NYHR_CELL : NYHR_LOCAL_VAR, name, r))
	      return 1;
	}
    }
    return 0;
}

static int
frame_relate(NyHeapRelate *r)
{
    PyFrameObject *v = (void *)r->src;
    PyCodeObject *co = v->f_code;
    int ncells = PyTuple_GET_SIZE(co->co_cellvars);
    int nlocals = co->co_nlocals;
    int nfreevars = PyTuple_GET_SIZE(co->co_freevars);
    ATTR(f_back)
    ATTR(f_code)
    ATTR(f_builtins)
    ATTR(f_globals)
    ATTR(f_locals)
    ATTR(f_trace)
    ATTR(f_exc_type)
    ATTR(f_exc_value)
    ATTR(f_exc_traceback)

    /* locals */
    if (
      frame_locals(r, co->co_varnames, 0, nlocals, 0) ||
      frame_locals(r, co->co_cellvars, nlocals,  ncells, 0) ||
      frame_locals(r, co->co_cellvars, nlocals,  ncells, 1) ||
      frame_locals(r, co->co_freevars, nlocals + ncells, nfreevars, 0) ||
      frame_locals(r, co->co_freevars, nlocals + ncells, nfreevars, 1))
      return 1;

    /* stack */

    if (v->f_stacktop != NULL) {
	PyObject **p;
	for (p = v->f_valuestack; p < v->f_stacktop; p++) {
	    if (*p == r->tgt) {
		if (r->visit(NYHR_STACK, PyInt_FromLong(p-v->f_valuestack), r))
		  return 1;
	    }
	}
    }
    return 0;
}

static int
frame_traverse(NyHeapTraverse *ta) {
    PyFrameObject *v = (void *)ta->obj;
    PyCodeObject *co = v->f_code;
    int nlocals = co->co_nlocals;
    if (PyTuple_Check(co->co_varnames)) {
	int i;
	for (i = 0; i < nlocals; i++) {
	    PyObject *name = PyTuple_GET_ITEM(co->co_varnames, i);
	    if (strcmp(PyString_AsString(name), "_hiding_tag_") == 0) {
		if (v->f_localsplus[i] == ta->_hiding_tag_)
		  return 0;
		else
		  break;
	    }
	}
    }
    return v->ob_type->tp_traverse(ta->obj, ta->visit, ta->arg);
}


static int
traceback_relate(NyHeapRelate *r)
{
    PyTraceBackObject *v = (void *)r->src;
    ATTR(tb_next)
    ATTR(tb_frame)
    return 0;
}

static int
cell_relate(NyHeapRelate *r)
{
    PyCellObject *v = (void *)r->src;
    if (v->ob_ref == r->tgt &&
	r->visit(NYHR_INTERATTR, PyString_FromString("ob_ref"), r))
      return 1;
    return 0;
}

static int
array_size_23(PyObject *obj) {
    int z = obj->ob_type->tp_basicsize;
    PyArrayObject_23 *v = (void *)obj;
    if (v->ob_item) {
	z += v->ob_descr->itemsize * v->ob_size;
	z = ALIGN(z);
    }
    return z;
}

static int
array_size_24(PyObject *obj) {
    int z = obj->ob_type->tp_basicsize;
    PyArrayObject_24 *v = (void *)obj;
    if (v->ob_item) {
	z += v->ob_descr->itemsize * v->ob_size;
	z = ALIGN(z);
    }
    return z;
}


static int
meth_relate(NyHeapRelate *r)
{
#if 0	/* This may be for an Python version earlier than 2.3, I am not sure exactly which one */
    if (((PyCFunctionObject *)(r->src))->m_self == r->tgt)
      r->visit(NYHR_INTERATTR, PyString_FromString("m_self"), r);
    return 0;
#else
    PyCFunctionObject *v = (void *)r->src;
    RENAMEATTR(m_self, __self__);
    RENAMEATTR(m_module, __module__);
#endif
    return 0;
}

static int
code_traverse(NyHeapTraverse *ta) {
    int err = 0;
    PyCodeObject *co = (void *)ta->obj;
    visitproc visit = ta->visit;
    void *arg = ta->arg;
    VISIT(co->co_code);
    VISIT(co->co_consts);
    VISIT(co->co_names);
    VISIT(co->co_varnames);
    VISIT(co->co_freevars);
    VISIT(co->co_cellvars);
    VISIT(co->co_filename);
    VISIT(co->co_name);
    VISIT(co->co_lnotab);
    return 0;
}

/* type_traverse adapted from typeobject.c from 2.4.2
   except:
   * I removed the check for heap type
   * I added visit of tp_subclasses and slots
 */

static int
type_traverse(NyHeapTraverse *ta)
{
    PyTypeObject *type=(void *)ta->obj;
    visitproc visit = ta->visit;
    void *arg = ta->arg;

    int err;

    VISIT(type->tp_dict);
    VISIT(type->tp_cache);
    VISIT(type->tp_mro);
    VISIT(type->tp_bases);
    VISIT(type->tp_base);
    VISIT(type->tp_subclasses);

    if (!(type->tp_flags & Py_TPFLAGS_HEAPTYPE))
	return 0;
#if PY_VERSION_HEX >= 0x02050000
    VISIT(((PyHeapTypeObject *)type)->ht_slots ) ;
#else
    VISIT(((PyHeapTypeObject *)type)->slots ) ;
#endif
    return 0;
}




static int
type_relate(NyHeapRelate *r)
{
    PyTypeObject *type = (void *)r->src;
    PyHeapTypeObject *et;
#define v type
    RENAMEATTR(tp_dict, __dict__);
    INTERATTR(tp_cache);
    RENAMEATTR(tp_mro, __mro__);
    RENAMEATTR(tp_bases, __bases__);
    RENAMEATTR(tp_base, __base__);
    INTERATTR(tp_subclasses);
#undef v
    if (!(type->tp_flags & Py_TPFLAGS_HEAPTYPE))
      return 0;
    et = (PyHeapTypeObject *)type;
#define v et
#if PY_VERSION_HEX >= 0x02050000
    RENAMEATTR(ht_slots, __slots__);
#else
    RENAMEATTR(slots, __slots__);
#endif
    return 0;
#undef v
}

static int
unicode_size(PyObject *obj) {
    PyUnicodeObject *uc = (PyUnicodeObject *)obj;
    int size =  uc->ob_type->tp_basicsize + (uc->length + 1) * sizeof(PY_UNICODE_TYPE);
    size = ALIGN(size);
    if (uc->defenc) {
	size += uc->defenc->ob_type->tp_basicsize;
	size += ((PyStringObject *)uc->defenc)->ob_size * uc->defenc->ob_type->tp_itemsize;
	size = ALIGN(size);
    }
    return size;
}

NyHeapDef NyStdTypes_HeapDef[] = {
    {
	0,			/* flags */
	0,		/* type */
	dict_size,		/* size */
	0,			/* traverse */
	dict_relate		/* relate */
    },	  {
	0,			/* flags */
	0,		/* type */
	list_size,		/* size */
	0,			/* traverse */
	list_relate		/* relate */
    }, {
	0,			/* flags */
	0,		/* type */
	0,			/* size */
	0,			/* traverse */
	tuple_relate		/* relate */
    }, {
	0,			/* flags */
	0,	/* type */
	0,			/* size */
	instance_traverse,	/* traverse */
	instance_relate		/* relate */
    }, {
	0,			/* flags */
	0,		/* type */
	0,			/* size */
	0,			/* traverse */
	class_relate		/* relate */
    }, {
	0,			/* flags */
	0,	/* type */
	0,			/* size */
	0,			/* traverse */
	function_relate		/* relate */
    }, {
	0,			/* flags */
	0,		/* type */
	0,			/* size */
	0,			/* traverse */
	module_relate		/* relate */
    }, {
	0,			/* flags */
	0,		/* type */
	0,			/* size */
	frame_traverse,		/* traverse */
	frame_relate		/* relate */
    }, {
	0,			/* flags */
	0,	/* type */
	0,			/* size */
	0,			/* traverse */
	traceback_relate	/* relate */
    }, {
	0,			/* flags */
	0,		/* type */
	0,			/* size */
	0,			/* traverse */
	cell_relate		/* relate */
    }, {
	0,			/* flags */
        0,		/* type */ /* To be patched-in from an array ! */
	array_size_23,		/* size */
	0,			/* traverse */
	0			/* relate */
    }, {
	0,			/* flags */
	0,	/* type */
	0,			/* size */
	0,			/* traverse */
	meth_relate		/* relate */
    }, {
	0,			/* flags */
	0,		/* type */
	0,			/* size */
	code_traverse,		/* traverse */
	0			/* relate */
    }, {
	0,			/* flags */
	0,		/* type */
	0,			/* size */
	type_traverse,		/* traverse */
	type_relate		/* relate */
    }, {
	0,			/* flags */
	0,	/* type */
	unicode_size,		/* size */
	0,			/* traverse */
	0,			/* relate */
    }, {
	0,			/* flags */
	0,		/* type */ /* To be patched-in from a dictproxy ! */
	0,			/* size */
	0,			/* traverse */
	dictproxy_relate	/* relate */
    },	


/* End mark */
	  {
	0,			/* flags */
	0,			/* type */
	0,			/* size */
	0,			/* traverse */
	0			/* relate */
    }
};

void
NyStdTypes_init(void)
{
    /* Patch up the table for some types that were not directly accessible */
    PyObject *m, *c;
    NyHeapDef *hd = NyStdTypes_HeapDef;
    int x = 0;

    NyStdTypes_HeapDef[x++].type = &PyDict_Type;
    NyStdTypes_HeapDef[x++].type = &PyList_Type;
    NyStdTypes_HeapDef[x++].type = &PyTuple_Type;
    NyStdTypes_HeapDef[x++].type = &PyInstance_Type;
    NyStdTypes_HeapDef[x++].type = &PyClass_Type;
    NyStdTypes_HeapDef[x++].type = &PyFunction_Type;
    NyStdTypes_HeapDef[x++].type = &PyModule_Type;
    NyStdTypes_HeapDef[x++].type = &PyFrame_Type;
    NyStdTypes_HeapDef[x++].type = &PyTraceBack_Type;
    NyStdTypes_HeapDef[x++].type = &PyCell_Type;
    NyStdTypes_HeapDef[x++].type = (void *)1;
    NyStdTypes_HeapDef[x++].type = &PyCFunction_Type;
    NyStdTypes_HeapDef[x++].type = &PyCode_Type;
    NyStdTypes_HeapDef[x++].type = &PyType_Type;
    NyStdTypes_HeapDef[x++].type = &PyUnicode_Type;
    NyStdTypes_HeapDef[x++].type = (void *)1;

    for (;hd->type;hd++) {
	if (hd->size == array_size_23) {
	    /* Patch up array type - it is not statically accessible, may be optional */
	    if ((m = PyImport_ImportModule("array"))) {
		if ((c = PyObject_GetAttrString(m, "ArrayType"))) {
		    hd->type = (PyTypeObject *)c;
		    if (hd->type->tp_basicsize != sizeof(PyArrayObject_23)) {
			if (hd->type->tp_basicsize == sizeof(PyArrayObject_24)) {
			    hd->size = array_size_24;
			} else {
			    hd->size = NULL;
			    PyErr_Warn(PyExc_Warning,
"heapyc.NyStdtTypes_init: Can not size array objects in this Python version");
			}
		    }
		}
	    }
	}
	if (hd->relate == dictproxy_relate) {
	    PyObject *d = PyDict_New();
	    if (d) {
		PyObject *dp = PyDictProxy_New(d);
		if (dp) {
		    hd->type = (PyTypeObject *)dp->ob_type;
		    Py_DECREF(dp);
		}
		Py_DECREF(d);
	    }
	}
	/* Patch up other such types */
	    
    }
}
