#define NyNodeSet_TYPE	(nodeset_exports->type)

#define NyNodeSet_Check(op) PyObject_TypeCheck(op, NyNodeSet_TYPE)

NyNodeSet_Exports *nodeset_exports;

/* Macro NODESET_EXPORTS where error (NULL) checking can be done */
#define NODESET_EXPORTS nodeset_exports

NyNodeSetObject *
NyMutNodeSet_New(void) {
    return NODESET_EXPORTS->newMut();
}

NyNodeSetObject *
NyMutNodeSet_NewHiding(PyObject *tag) {
    return NODESET_EXPORTS->newMutHiding(tag);
}

NyNodeSetObject *
NyMutNodeSet_NewFlags(int flags) {
    return NODESET_EXPORTS->newMutFlags(flags);
}

int
NyNodeSet_setobj(NyNodeSetObject *v, PyObject *obj) {
    return NODESET_EXPORTS->setobj(v, obj);
}

int
NyNodeSet_clrobj(NyNodeSetObject *v, PyObject *obj) {
    return NODESET_EXPORTS->clrobj(v, obj);
}


int
NyNodeSet_hasobj(NyNodeSetObject *v, PyObject *obj) {
    return NODESET_EXPORTS->hasobj(v, obj);
}

int NyNodeSet_iterate(NyNodeSetObject *ns,
		      int (*visit)(PyObject *, void *),
		      void *arg) {
    return NODESET_EXPORTS->iterate(ns, visit, arg);;
}


NyNodeSetObject *
NyNodeSet_NewImmCopy(NyNodeSetObject *v) {
    return NODESET_EXPORTS->newImmCopy(v);
}

NyNodeSetObject *
NyImmNodeSet_NewSingleton(PyObject *element, PyObject *hiding_tag) {
    return NODESET_EXPORTS->newImmSingleton(element, hiding_tag);
}

int
NyNodeSet_be_immutable(NyNodeSetObject **nsp) {
    return NODESET_EXPORTS->be_immutable(nsp);
}

static int
import_sets(void) 
{
    if (!nodeset_exports) {
	nodeset_exports= PyCObject_Import("guppy.sets.setsc",
					  "NyNodeSet_Exports");
	if (!nodeset_exports)
	  return -1;
    }
    return 0;
}

