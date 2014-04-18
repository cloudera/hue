/* Implementation of the 'dictof' classifier
   It is like clodo but classifies non-dicts to None.
   And has an argument that classifies the owners.
 */

PyDoc_STRVAR(hv_cli_dictof_doc,
"HV.cli_dictof(owners, ownerclassifier, notdictkind, notownedkind) -> ObjectClassifier\n"
"\n"
"Return a classifier, that classifies by \"Dict Owner\".\n"
"\n"
"The classification of an object is the notdictkind,\n"
"unless the object is a dict object.  If the dict is 'owned' by some owner,\n"
"the classification will be \n"
"the class (as by the ownerclass argument ) of its owner.\n"
"If it is not owned, the returned kind will be notowned argument.\n"
"Arguments:\n"
"\n"
"    owners      A NodeGraph object used to map each dict object to\n"
"                its owner, or to None if it has no owner. The\n"
"                graph will be automatically updated, from heap\n"
"                information defined by HV, whenever an attempt\n"
"        	is made to classify a dict that maps to nothing.\n"
"\n"
"\n"
"    ownerclassifier\n"
"    notdictkind\n"
"    notownedkind\n"
);


/* This macro defines the definition of a 'dict' as far as
   the dictof classifier is concerned. So we don't bother about
   subtypes - they can't be 'owned' in any standard way can they (?)
*/
# define DictofDict_Check(obj)	(obj->ob_type == &PyDict_Type)

typedef struct {
    PyObject_VAR_HEAD
    NyHeapViewObject *hv;
    NyNodeGraphObject *owners;
    NyObjectClassifierObject *ownerclassifier;
    PyObject *notdictkind;
    PyObject *notownedkind;
} DictofObject;

/* Code for update_dictowners */

PyObject **
hv_cli_dictof_dictptr(PyObject *obj)
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

/* Code for new dict-owner update method. Notes Apr 7 2005. */

static PyObject *
hv_cli_dictof_get_static_types_list(NyHeapViewObject *hv) {
    if (PyObject_Length(hv->static_types) == 0) {
	PyObject *h = hv_heap(hv, Py_None, Py_None); /* It updates static_types */
	if (!h)
	  return 0;
	Py_DECREF(h);
    }
    return PySequence_List(hv->static_types);
}

static PyObject *
hv_get_objects(NyHeapViewObject *hv) {
    PyObject *p = hv_heap(hv, Py_None, Py_None);
    PyObject *r;
    if (!p)
	goto err;
    r = PySequence_List(p);
    Py_DECREF(p);
    return r;
    err:
    return 0;
}

static int
hv_cli_dictof_update_new_method(NyHeapViewObject *hv, NyNodeGraphObject *rg)
{
    NyNodeSetObject *dictsowned = 0;
    PyObject **dp;
    int i, k, len;
    int result = -1;
    PyObject *lists[2] = {0, 0};
    
    /* These 2 lines are to avoid a leak in certain cases noted 30 Sep-3 Oct 2005. */
    NyNodeGraph_Clear(rg);
    PyGC_Collect();

    if (!(dictsowned = NyMutNodeSet_New())) goto err;
    if (!(lists[0] = hv_cli_dictof_get_static_types_list(hv))) goto err;
    if (!(lists[1] = hv_get_objects(hv))) goto err;
    for (k = 0; k < 2; k++) {
	PyObject *objects = lists[k];
	len = PyList_Size(objects);
	if (len == -1) /* catches eg type error */
	  goto err;
	for (i = 0; i < len; i++) {
	    PyObject *obj = PyList_GET_ITEM(objects, i);
	    dp = hv_cli_dictof_dictptr(obj);
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
	    if (DictofDict_Check(obj) && !NyNodeSet_hasobj(dictsowned, obj)) {
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
hv_cli_dictof_update(NyHeapViewObject *hv, NyNodeGraphObject *rg)
{
    return hv_cli_dictof_update_new_method(hv, rg);
}


static PyObject *
hv_cli_dictof_classify(DictofObject *self, PyObject *obj)
{
    if (!DictofDict_Check(obj)) {
	Py_INCREF(self->notdictkind);
	return self->notdictkind;
    } else {
	NyNodeGraphEdge *lo, *hi;
	if (NyNodeGraph_Region(self->owners, obj, &lo, &hi) == -1) {
	    return 0;
	}
	if (!(lo < hi)) {
	    NyNodeGraph_Clear(self->owners);
	    if (hv_cli_dictof_update(self->hv, self->owners) == -1)
	      return 0;
	    if (NyNodeGraph_Region(self->owners, obj, &lo, &hi) == -1) {
		return 0;
	    }
	}
	if (lo < hi && lo->tgt != Py_None) {
	    PyObject *ownerkind = self->ownerclassifier->def->classify
	      (self->ownerclassifier->self, lo->tgt);
	    return ownerkind;
	} else {
	    Py_INCREF(self->notownedkind);
	    return self->notownedkind;
	}
    }
    
}

static PyObject *
hv_cli_dictof_memoized_kind(DictofObject *self, PyObject *obj)
{
    if (self->ownerclassifier->def->memoized_kind)
      return self->ownerclassifier->def->memoized_kind(self->ownerclassifier->self, obj);
    else {
	Py_INCREF(obj);
	return obj;
    }
}

static NyObjectClassifierDef hv_cli_dictof_def = {
    0,
    sizeof(NyObjectClassifierDef),
    "cli_dictof",
    "classifier returning ...",
    (binaryfunc)hv_cli_dictof_classify,
    (binaryfunc)hv_cli_dictof_memoized_kind,
};

static PyObject *
hv_cli_dictof(NyHeapViewObject *self, PyObject *args)
{
    PyObject *r;
    DictofObject *s, tmp;
    if (!PyArg_ParseTuple(args, "O!O!OO:cli_dictof", 
			  &NyNodeGraph_Type, &tmp.owners,
			  &NyObjectClassifier_Type,&tmp.ownerclassifier,
			  &tmp.notdictkind,
			  &tmp.notownedkind
			  ))
      return 0;

    s = NYTUPLELIKE_NEW(DictofObject);
    if (!s)
      return 0;
    s->hv = self;
    Py_INCREF(s->hv);

    s->owners = tmp.owners;
    Py_INCREF(s->owners);


    s->ownerclassifier = tmp.ownerclassifier;
    Py_INCREF(s->ownerclassifier);

    s->notdictkind = tmp.notdictkind;
    Py_INCREF(s->notdictkind);

    s->notownedkind = tmp.notownedkind;
    Py_INCREF(s->notownedkind);

    r = NyObjectClassifier_New((PyObject *)s, &hv_cli_dictof_def);
    Py_DECREF(s);
    return r;
}

