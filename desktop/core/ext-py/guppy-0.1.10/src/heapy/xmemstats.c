/* Extra, low-level memory statistics functions.
   Some is system dependent,
   some require special Python compilation.
*/

static char hp_xmemstats_doc[] =
"xmemstats()\n"
"\n"
"Print extra memory statistics. What is printed depends on the system\n"
"configuration.  ";

#ifdef __GLIBC__

#include <malloc.h>

#endif

#ifdef WITH_MALLOC_HOOKS

int totalloc, totfree, reallocfree, reallocalloc, numalloc, numfree, numdiff;

void *(*org_alloc)(int size);
void *(*org_realloc)(void *p, int size);
void (*org_free)(void *p);

void
breakit(void *p, char c )
{
    /*fprintf(stderr, "breakit %p %c %d\n", p, c, malloc_usable_size(p));*/
}


void *
mallochook(int size) {
    void *o = __malloc_hook;
    void *p;
    int f;
    __malloc_hook = 0;
    p = org_alloc(size);
    f = malloc_usable_size(p);
    totalloc+= f;
    __malloc_hook = o;
    numalloc += 1;
    numdiff += 1;
    if (f > 265000) {
	breakit(p, 'm');
    }
    return p;
}

void *
reallochook(void *p, int size) {
    void *q;
    int f;
    void *o = __realloc_hook;
    if (p)
      f = malloc_usable_size(p);
    else
      f = 0;
    __realloc_hook = 0;
    q = org_realloc(p, size);
    if (alset) {
	NyNodeSetObject *a = alset;
	alset = 0;
	NyNodeSet_clrobj(a, p);
	NyNodeSet_setobj(a, q);
	alset = a;
    }
    if (q != p) {
	totfree += f;
	reallocfree += f;
	f = malloc_usable_size(q);
	totalloc += f;
	reallocalloc += f;
    } else {
	f = malloc_usable_size(q) - f;
	if (f > 0) {
	    totalloc += f;
	    reallocalloc += f;
	} else {
	    totfree -= f;
	    reallocfree -= f;
	}
    }
    __realloc_hook = o;
    if (f > 265000) {
	breakit(q, 'r');
    }
	
    return q;
}

void
freehook(void *p) {
    void *o = __free_hook;
    __free_hook = 0;
    totfree += malloc_usable_size(p);
    if (alset) {
	NyNodeSetObject *a = alset;
	alset = 0;
	NyNodeSet_clrobj(a, p);
	alset = a;
    }
    org_free(p);
    __free_hook = o;
    numfree -= 1;
    numdiff -= 1;
}

void
sethooks(void) {
    org_alloc = (void *)malloc;
    org_realloc = (void *)realloc;
    org_free = (void *)free;
    __malloc_hook = (void *)mallochook;
    __realloc_hook = (void *)reallochook;
    __free_hook = (void *)freehook;
}

#endif /* WITH_MALLOC_HOOKS */

static PyObject *
hp_xmemstats(PyObject *self, PyObject *args)
{
#ifdef __GLIBC__
    fprintf(stderr, "======================================================================\n");
    fprintf(stderr, "Output from malloc_stats\n\n");
    malloc_stats();
#endif

#ifdef PYMALLOC_DEBUG
    fprintf(stderr, "======================================================================\n");
    fprintf(stderr, "Output from _PyObject_DebugMallocStats()\n\n");
    _PyObject_DebugMallocStats();
#endif

#ifdef WITH_MALLOC_HOOKS
    fprintf(stderr, "======================================================================\n");
    fprintf(stderr, "Statistics gathered from hooks into malloc, realloc and free\n\n");

    fprintf(stderr, "Allocated bytes                    =         %12d\n", totalloc);
    fprintf(stderr, "Allocated - freed bytes            =         %12d\n", totalloc-totfree);
    fprintf(stderr, "Calls to malloc                    =         %12d\n", numalloc);
    fprintf(stderr, "Calls to malloc - calls to free    =         %12d\n", numdiff);
#endif

#if defined(Py_REF_DEBUG) || defined(Py_TRACE_REFS)
    fprintf(stderr, "======================================================================\n");
    fprintf(stderr, "Other statistics\n\n");
#endif
#ifdef Py_REF_DEBUG
    fprintf(stderr, "Total reference count              =         %12ld\n", _Py_RefTotal);
#endif
#ifdef Py_TRACE_REFS
    {
	PyObject *x; int i;
	for (i = 0, x = this_module->_ob_next; x != this_module; x = x->_ob_next, i++)
	  ;
    fprintf(stderr, "Total heap objects                 =         %12d\n", i);
    }
#endif
    fprintf(stderr, "======================================================================\n");

    Py_INCREF(Py_None);
    return Py_None;

}




