/* Implementation of the 'clodo' classifier */

PyDoc_STRVAR(hv_cli_clodo_doc,
"HV.cli_clodo(owners, memo) -> ObjectClassifier\n\
\n\
Return a classifier, that classifies by \"Class Or Dict Owner\".\n\
\n\
The classification of an object is its class (as by cli_class),\n\
unless the object is a dict object that is 'owned' by some owner.\n\
If the object is such an owned dict, the classification will be a\n\
1-tuple containing the class (as by cli_class) of its owner.\n\
Arguments:\n\
\n\
    owners      A NodeGraph object used to map each dict object to\n\
                its owner, or to None if it has no owner. The\n\
                graph will be automatically updated, from heap\n\
                information defined by HV, whenever an attempt\n\
        	is made to classify a dict that maps to nothing.\n\
\n\
    memo        A dict object used to memoize the 1-tuples\n\
                generated when classifying owned dicts.");


/* This macro defines the definition of a 'dict' as far as
   the clodo classifier is concerned. So we don't bother about
   subtypes - they can't be 'owned' in any standard way can they (?)
*/
# define ClodoDict_Check(obj)	(obj->ob_type == &PyDict_Type)

typedef struct {
    PyObject_VAR_HEAD
    NyHeapViewObject *hv;
    NyNodeGraphObject *owners;
    PyObject *memo;
} ClodoObject;

typedef struct {
    NyHeapViewObject *hv;
    NyNodeGraphObject *rg;
    NyNodeSetObject *markset, *dictsowned, *dictsmaybenotowned;
    PyObject *retainer;
} DOTravArg;

/* Code for update_dictowners */

/* Code common for old and new method */

PyObject **
hv_cli_clodo_dictptr(PyObject *obj)
{
    PyObject **dp;
    if (PyInstance_Check(obj))
      dp = &((PyInstanceObject *)obj)->in_dict;
    else if (PyClass_Check(obj))
      dp = &((PyClassObject *)obj)->cl_dict;
    else if (PyType_Check(obj)) /* Doesnt work generally; Note Apr 8 2005 */
      dp = &((PyTypeObject *)obj)->tp_dict;
    else
      dp = _PyObject_GetDictPtr(obj);
    return dp;
}

/* Code for old method */

static int
hv_cli_clodo_isdictof(PyObject *dict, PyObject *obj)
{
    PyObject **dp = hv_cli_clodo_dictptr(obj);
    return (dp && *dp == dict);
}

static int
hv_cli_clodo_retadorec(PyObject *obj, DOTravArg *ta)
{
    int r;
    PyObject *oretainer;
    if (PyDict_Check(obj)) {
	if (hv_cli_clodo_isdictof(obj, ta->retainer)) {
	    if (NyNodeGraph_AddEdge(ta->rg, obj, ta->retainer) == -1)
	      return -1;
	    if (NyNodeSet_setobj(ta->dictsowned, obj) == -1)
	      return -1;
	} else {
	    if (NyNodeSet_setobj(ta->dictsmaybenotowned, obj) == -1)
	      return -1;
	}
    }
    if (obj->ob_refcnt > 1) {
	r = NyNodeSet_setobj(ta->markset, obj);
	if (r) {
	    if (r == -1)
	      return -1;
	  return 0;
	}
    }
    oretainer = ta->retainer;
    ta->retainer = obj;
    r = hv_std_traverse(ta->hv, obj, (visitproc)hv_cli_clodo_retadorec, ta);
    ta->retainer = oretainer;
    return r;
}

static int
hv_cli_clodo_setunowned(PyObject *obj, DOTravArg *ta) {
    if (!NyNodeSet_hasobj(ta->dictsowned, obj)) {
	if (NyNodeGraph_AddEdge(ta->rg, obj, Py_None) == -1)
	  return -1;
    }
    return 0;
}

static int
hv_cli_clodo_update_old_method(NyHeapViewObject *hv, NyNodeGraphObject *rg)
{
    DOTravArg ta;
    int r;
    ta.hv = hv;
    ta.rg = rg;
    ta.markset = NyNodeSet_New();
    ta.dictsowned = NyNodeSet_New();
    ta.dictsmaybenotowned = NyNodeSet_New();
    if (!(ta.markset && ta.dictsowned && ta.dictsmaybenotowned)) {
	r = -1;
	goto retr;
    }
    ta.retainer = ta.hv->root;
    NyNodeGraph_Clear(ta.rg);
    r = hv_std_traverse(ta.hv, ta.retainer, (visitproc)hv_cli_clodo_retadorec, &ta);
    if (r == -1)
      goto retr;
    r = iterable_iterate((PyObject *)ta.dictsmaybenotowned,
			 (visitproc)hv_cli_clodo_setunowned,
			 &ta);

  retr:
    Py_XDECREF(ta.markset);
    Py_XDECREF(ta.dictsowned);
    Py_XDECREF(ta.dictsmaybenotowned);
    return r;

}

/* Code for new dict-owner update method. Notes Apr 7 2005. */

static PyObject *
hv_get_static_types_list(NyHeapViewObject *hv) {
    if (PyObject_Length(hv->static_types) == 0) {
	PyObject *h = hv_heap(hv, Py_None, Py_None); /* It updates static_types */
	if (!h)
	  return 0;
	Py_DECREF(h);
    }
    return PySequence_List(hv->static_types);
}

static int
hv_cli_clodo_update_new_method(NyHeapViewObject *hv, NyNodeGraphObject *rg)
{
    NyNodeSetObject *dictsowned = 0;
    PyObject **dp;
    int i, k, len;
    int result = -1;
    PyObject *lists[2] = {0, 0};
    
    if (!(dictsowned = NyNodeSet_New())) goto err;
    if (!(lists[0] = hv_get_static_types_list(hv))) goto err;
    if (!(lists[1] = gc_get_objects())) goto err;
    for (k = 0; k < 2; k++) {
	PyObject *objects = lists[k];
	len = PyList_Size(objects);
	if (len == -1) /* catches eg type error */
	  goto err;
	for (i = 0; i < len; i++) {
	    PyObject *obj = PyList_GET_ITEM(objects, i);
	    dp = hv_cli_clodo_dictptr(obj);
	    if (dp && *dp) {
		if (NyNodeGraph_AddEdge(rg, *dp, obj) == -1)
		  goto err;
		if (NyNodeSet_setobj(dictsowned, *dp) == -1)
		  goto err;
	    }
	}
    }
    for (k = 0; k < 2; k++) {
	PyObject *objects = lists[k];
	len = PyList_Size(objects);
	for (i = 0; i < len; i++) {
	    PyObject *obj = PyList_GET_ITEM(objects, i);
	    if (ClodoDict_Check(obj) && !NyNodeSet_hasobj(dictsowned, obj)) {
		if (NyNodeGraph_AddEdge(rg, obj, Py_None) == -1)
		  goto err;
	    }
	}
    }
    result = 0;
  err:
    Py_XDECREF(dictsowned);
    Py_XDECREF(lists[0]);
    Py_XDECREF(lists[1]);
    return result;
}


static int
hv_cli_clodo_update(NyHeapViewObject *hv, NyNodeGraphObject *rg)
{
    if (hv->is_using_traversing_owner_update)
      return hv_cli_clodo_update_old_method(hv, rg);
    else
      return hv_cli_clodo_update_new_method(hv, rg);
}


static PyObject *
hv_cli_clodo_ownerkind(ClodoObject *self, PyObject *t)
{
    PyObject *dt = PyDict_GetItem(self->memo, t);
    if (!dt) {
	dt = PyTuple_New(1);
	if (!dt)
	  return 0;
	PyTuple_SetItem(dt, 0, t);
	Py_INCREF(t);
	if (PyDict_SetItem(self->memo, t, dt) == -1) {
	    Py_DECREF(dt);
	    return 0;
	}
    } else {
	Py_INCREF(dt);
    }
    return dt;
}

static PyObject *
hv_cli_clodo_classify(ClodoObject *self, PyObject *obj)
{
    if (!ClodoDict_Check(obj))
      return hv_std_classify(self->hv, obj);
    else {
	NyNodeGraphEdge *lo, *hi;
	if (NyNodeGraph_Region(self->owners, obj, &lo, &hi) == -1) {
	    return 0;
	}
	if (!(lo < hi)) {
	    NyNodeGraph_Clear(self->owners);
	    if (hv_cli_clodo_update(self->hv, self->owners) == -1)
	      return 0;
	    if (NyNodeGraph_Region(self->owners, obj, &lo, &hi) == -1) {
		return 0;
	    }
	}
	if (lo < hi && lo->tgt != Py_None) {
	    PyObject *ownerkind = hv_std_classify(self->hv, lo->tgt);
	    PyObject *kind =  hv_cli_clodo_ownerkind(self, ownerkind);
	    Py_DECREF(ownerkind);
	    return kind;
	} else {
	    Py_INCREF(obj->ob_type);
	    return (PyObject *)obj->ob_type;
	}
    }
    
}


static PyObject *
hv_cli_clodo_memoized_kind(ClodoObject *self, PyObject *kind)
{
    if (PyTuple_Check(kind))
      return hv_cli_clodo_ownerkind(self, PyTuple_GET_ITEM(kind, 0) );
    else {
	Py_INCREF(kind);
	return kind;
    }
}


static NyObjectClassifierDef hv_cli_clodo_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_clodo",
    "classifier returning ...",
    (binaryfunc)hv_cli_clodo_classify,
    (binaryfunc)hv_cli_clodo_memoized_kind
};

static PyObject *
hv_cli_clodo(NyHeapViewObject *self, PyObject *args)
{
    PyObject *r;
    ClodoObject *s;
    s = NYTUPLELIKE_NEW(ClodoObject);
    if (!s)
      return 0;
    s->hv = self;
    if (!PyArg_ParseTuple(args, "O!O!:cli_clodo", 
			  &NyNodeGraph_Type, &s->owners,
			  &PyDict_Type, &s->memo))
      {
	  s->owners = 0;
	  s->memo = 0;
	  s->hv = 0;
	  Py_DECREF(s);
	  return NULL;
      }
    Py_INCREF(s->hv);
    Py_INCREF(s->owners);
    Py_INCREF(s->memo);
    r = NyObjectClassifier_New((PyObject *)s, &hv_cli_clodo_def);
    Py_DECREF(s);
    return r;
}

