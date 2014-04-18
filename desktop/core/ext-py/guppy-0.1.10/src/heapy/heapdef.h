#ifndef Ny_HEAPDEF_H
#define Ny_HEAPDEF_H

/* NyHeapTraverse - argument to traverse
   Defined to avoid complicated function defs
*/

typedef struct {
    int flags;
    PyObject *hv; /* A HeapView object providing context to the traversal
		     function, if necessary. It is defined as a PyObject
		     rather than HeapView to avoid include file dependency. */
    PyObject *obj;  /* The object that is to be traversed */
    void *arg;   /* the argument to pass when visiting referred objects. */
    visitproc visit; /* The visit procedure to call */
    PyObject *_hiding_tag_; /* The hiding tag in use by current context. */


} NyHeapTraverse;

/* NyHeapRelate - argument to relate
   Defined to avoid complicated function defs
*/

typedef struct NyHeapRelate {
    int flags;		/* As yet unused */
    PyObject *hv;	/* Heap view object */
    PyObject *src;	/* Source of relation, and which is dispatched on */
    PyObject *tgt;	/* Target of relation */		

    	/* visit() should be called once for each unique pointer
	   from src to tgt.
	   The relation type is indicated by the relatype argument
	   and defined in the NYHR_ definitions below.
	   The relator argument is an object describing the relation
	   and should be newly allocated or INCREFED.
	   The arg argument should be the arg passed in NyHeapRelate
	   below.

	   Return value: non-zero, means the relate function should
	   not provide any more relations but should return. A zero
	   return value means visit may be called again.
       */

    int (*visit)(unsigned int relatype, PyObject *relator, struct NyHeapRelate *arg);
} NyHeapRelate;

/* Values for 'relatype' argument to be passed to visit callback in NyHeapRelate */


#define	NYHR_ATTRIBUTE	1	/* src.relator is tgt */
#define	NYHR_INDEXVAL	2	/* src[relator] is tgt */
#define	NYHR_INDEXKEY	3	/* src has key tgt */
#define	NYHR_INTERATTR	4	/* src->relator == tgt in C only */
#define NYHR_HASATTR	5	/* src has attribute tgt (stored as string) */
#define NYHR_LOCAL_VAR	6	/* src (a frame) has local variable named <relator> with value tgt */
#define NYHR_CELL	7	/* src has cell variable named <relator> containing value tgt */
#define NYHR_STACK	8	/* src has a stack entry numbered <relator> with value tgt */ 
#define NYHR_RELSRC	9	/* relator % src is tgt ; tgt is relator % src*/
#define NYHR_LIMIT	10	/* All others are < NYHR_LIMIT */

/* NyHeapDef - structure to define by external type providers to define themselves wrt heapy
*/

/* Definitions of its function types, useful for casting. */

typedef int (*NyHeapDef_SizeGetter) (PyObject *obj);
typedef int (*NyHeapDef_Traverser) (NyHeapTraverse *arg);
typedef int (*NyHeapDef_RelationGetter) (NyHeapRelate *r);

typedef struct {
    int flags;			/* As yet, only 0 */
    PyTypeObject *type;		/* The type it regards */
    NyHeapDef_SizeGetter size;
    NyHeapDef_Traverser traverse;
    NyHeapDef_RelationGetter relate;
    void *resv3, *resv4, *resv5; /* Reserved for future bin. comp. */
} NyHeapDef;

#endif /* Ny_HEAPDEF_H */
