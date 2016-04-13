#ifndef Ny_NODESETOBJECT_H
#define Ny_NODESETOBJECT_H

/* Flags for NyNodeSetObject */

#define NS_HOLDOBJECTS	1       /* Only to be cleared in special case with mutable nodeset. */

typedef struct {
    PyObject_VAR_HEAD
    int flags;
    PyObject *_hiding_tag_;
    union {
	PyObject *bitset;	/* If mutable type, a mutable bitset with addresses (divided). */
	PyObject *nodes[1];	/* If immutable type, the start of node array, in address order. */
    } u;
} NyNodeSetObject;

NyNodeSetObject *NyMutNodeSet_New(void);
NyNodeSetObject *NyMutNodeSet_NewFlags(int flags);
NyNodeSetObject *NyMutNodeSet_NewHiding(PyObject *hiding_tag);

int NyNodeSet_setobj(NyNodeSetObject *v, PyObject *obj);
int NyNodeSet_clrobj(NyNodeSetObject *v, PyObject *obj);
int NyNodeSet_hasobj(NyNodeSetObject *v, PyObject *obj);

int NyNodeSet_iterate(NyNodeSetObject *hs,
		      int (*visit)(PyObject *, void *),
		      void *arg);

NyNodeSetObject *NyImmNodeSet_NewCopy(NyNodeSetObject *v);
NyNodeSetObject *NyImmNodeSet_NewSingleton(PyObject *element, PyObject *hiding_tag);
int NyNodeSet_be_immutable(NyNodeSetObject **nsp);


typedef struct {
    int flags;
    int size;
    char *ident_and_version;
    PyTypeObject *type;
    NyNodeSetObject *(*newMut)(void);
    NyNodeSetObject *(*newMutHiding)(PyObject *tag);
    NyNodeSetObject *(*newMutFlags)(int flags);
    NyNodeSetObject *(*newImmCopy)(NyNodeSetObject *v);
    NyNodeSetObject *(*newImmSingleton)(PyObject *v, PyObject *hiding_tag);
    int (*be_immutable)(NyNodeSetObject **nsp);
    int (*setobj)(NyNodeSetObject *v, PyObject *obj);
    int (*clrobj)(NyNodeSetObject *v, PyObject *obj);
    int (*hasobj)(NyNodeSetObject *v, PyObject *obj);
    int (*iterate)(NyNodeSetObject *ns,
		   int (*visit)(PyObject *, void *),
		   void *arg);
} NyNodeSet_Exports;

#endif /* Ny_NODESETOBJECT_H */

