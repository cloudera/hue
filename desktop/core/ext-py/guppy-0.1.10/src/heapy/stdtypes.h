#ifndef NY_STDDEFS_INCLUDED
#define NY_STDDEFS_INCLUDED

/*
	Definitions of type structure(s) that were not exported
	but were needed anyway.
	XXX dangerous, if Python changes this may break.
	Should be made officially exported.
	Or pull some from offset in tp_members, but that seems
	a too complicated workaround for now.

*/

typedef struct {
	PyObject_HEAD
	PyObject *md_dict;
} PyModuleObject;


typedef struct _tracebackobject {
	PyObject_HEAD
	struct _tracebackobject *tb_next;
	PyFrameObject *tb_frame;
	int tb_lasti;
	int tb_lineno;
} PyTraceBackObject;


/* There are two different versions of array obejct
   they differ incompatibly in 2.3 & 2.4

   Which one to use is determined by tp_size
   so the same heapy is binary compatible.

*/



/* This version is for 2.3: */

struct arrayobject_23; /* Forward */
struct arraydescr_23 {
	int typecode;
	int itemsize;
	PyObject * (*getitem)(struct arrayobject_23 *, int);
	int (*setitem)(struct arrayobject_23 *, int, PyObject *);
};

typedef struct arrayobject_23 {
	PyObject_VAR_HEAD
	char *ob_item;
	struct arraydescr_23 *ob_descr;
} PyArrayObject_23;

/* This version is for 2.4: */

struct arrayobject_24; /* Forward */
struct arraydescr_24 {
	int typecode;
	int itemsize;
	PyObject * (*getitem)(struct arrayobject_24 *, int);
	int (*setitem)(struct arrayobject_24 *, int, PyObject *);
};

typedef struct {
	PyObject_HEAD
	int ob_size;
	char *ob_item;
	int allocated;
	struct arraydescr_24 *ob_descr;
	PyObject *weakreflist; /* List of weak references */
} PyArrayObject_24;

typedef struct {
	PyObject_HEAD
	PyObject *dict;
} proxyobject;


#endif /* NY_STDDEFS_INCLUDED */

