#ifndef SETS_INTERNAL_H
#define SETS_INTERNAL_H

#include "sets.h"

/* BitSet */

extern PyTypeObject NyImmBitSet_Type;
extern PyTypeObject NyImmBitSetIter_Type;
extern PyTypeObject NyCplBitSet_Type;
extern PyTypeObject NyMutBitSet_Type;
extern PyTypeObject NyUnion_Type;

#define NyImmBitSet_Check(op) PyObject_TypeCheck(op, &NyImmBitSet_Type)
#define NyCplBitSet_Check(op) PyObject_TypeCheck(op, &NyCplBitSet_Type)
#define NyMutBitSet_Check(op) PyObject_TypeCheck(op, &NyMutBitSet_Type)

NyImmBitSetObject *NyImmBitSet_New(NyBit size);
NyCplBitSetObject *NyCplBitSet_New(NyImmBitSetObject *v);
NyMutBitSetObject *NyMutBitSet_New(void);

typedef int (*NySetVisitor)(NyBit, void *) ;

typedef int (*NyIterableVisitor)(PyObject *, void *);


extern int NyAnyBitSet_iterate(PyObject *v,
		   NySetVisitor visit,
		   void *arg);


extern int NyAnyBitSet_length(PyObject *v);

/* The predefined empty set */

extern NyImmBitSetObject _NyImmBitSet_EmptyStruct;
#define NyImmBitSet_Empty (&_NyImmBitSet_EmptyStruct)

/* The predefined set of all bits */

extern NyCplBitSetObject _NyImmBitSet_OmegaStruct;
#define NyImmBitSet_Omega (&_NyImmBitSet_OmegaStruct)


extern PyObject *NyMutBitSet_AsImmBitSet(NyMutBitSetObject *v);
extern int NyMutBitSet_clrbit(NyMutBitSetObject *v, NyBit bit);
extern int NyMutBitSet_setbit(NyMutBitSetObject *v, NyBit bit);
extern int NyMutBitSet_hasbit(NyMutBitSetObject *v, NyBit bit);
extern int NyImmBitSet_hasbit(NyImmBitSetObject *v, NyBit bit);

extern int NyMutBitSet_clear(NyMutBitSetObject *v);
extern long NyMutBitSet_pop(NyMutBitSetObject *v, NyBit i);

int cplbitset_traverse(NyHeapTraverse *ta);
int mutbitset_indisize(NyMutBitSetObject *v);
int anybitset_indisize(PyObject *obj);
int generic_indisize(PyObject *v);

/* NodeSet */

int nodeset_indisize(PyObject *v);
int nodeset_traverse(NyHeapTraverse *ta);
int nodeset_relate(NyHeapRelate *r);

extern PyTypeObject NyNodeSet_Type;
extern PyTypeObject NyMutNodeSet_Type;
extern PyTypeObject NyImmNodeSet_Type;

#define NyNodeSet_Check(op) PyObject_TypeCheck(op, &NyNodeSet_Type)
#define NyMutNodeSet_Check(op) PyObject_TypeCheck(op, &NyMutNodeSet_Type)
#define NyImmNodeSet_Check(op) PyObject_TypeCheck(op, &NyImmNodeSet_Type)


extern int fsb_dx_addmethods
	(PyObject *m, PyMethodDef *methods, PyObject *passthrough);


#endif /* SETS_INTERNAL_H */

