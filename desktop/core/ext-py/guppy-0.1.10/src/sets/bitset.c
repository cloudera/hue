/* BitSet implementation */

#include "Python.h"
#include "structmember.h"
#include "longintrepr.h"

#include "../include/guppy.h"
#include "../heapy/heapdef.h"
#include "sets_internal.h"

/* Docstrings */

char bitset_doc[] =


"The class BitSet is the base class for all bitset classes.\n"
"\n"
"A bitset is a set of 'bits'. Bits are integers, in a range that is\n"
"typically [-2**31 .. 2**31-1] or the range of the builtin Python int\n"
"type. The implementation of bitsets is such that it handles dense sets\n"
"the most efficiently while sparse sets are handled reasonably well.\n"
"\n"
"Bitsets can be either mutable or immutable. Mutable bitsets have\n"
"various operations to add and remove bits in-place. Immutable bitsets\n"
"have hashing so they can be used as keys in dicts. Both kinds of\n"
"bitsets have several operations in common. Sometimes an operand can be\n"
"either a bitset or a 'convertible', which means it is one of the\n"
"following kinds.\n"
"\n"
"iterable\n"
"    An iterable argument is convertible to a bitset if each object yielded\n"
"    is an integer (int or long) in the range of an int.\n"
"\n"
"int, long\n"
"    A positive argument, x, of one of these types will be converted\n"
"    to a bitset with the same bits as the binary representation of x.\n"
"\n"
"    A negative argument will be converted to a complemented bitset,\n"
"    equivalent to the following expression:\n"
"\n"
"        ~immbitset(~x)\n"
"\n"
"    This corresponds to the bits in the 2-complement binary representation\n"
"    of x, except that the result conceptually has all negative bits set.\n"
"    The difference shows (only) when shifting a complemented bitset.\n"
"\n"
"The following operations are common for mutable and immutable bitsets.\n"
"\n"
"------------------------------------------\n"
"Standard binary operations.\n"
"\n"
"In the usual case the left argument is some kind of bitset, and the\n"
"right argument is a bitset or a 'convertible' as defined above. The\n"
"return value is then an immutable bitset.\n"
"\n"
"x & y    -> Intersection: the set of\n"
"            bits that are in both x and y.\n"
"\n"
"x | y    -> Union: the set of\n"
"            bits that are in either x or y.\n"
"\n"
"x ^ y    -> Symmetric difference: the set of\n"
"            bits that are in exactly one of x and y.\n"
"\n"
"x - y    -> Difference: the set of\n"
"            bits that are in x but not in y.\n"
"\n"
"If the right argument is a bitset but not the left argument, the\n"
"result will be an immutable bitset if only the left argument is a\n"
"convertible that does not define the same operation; otherwise the\n"
"result is what is returned by the operation of the left argument or a\n"
"TypeError will be raised. The following table gives the result for the\n"
"different kinds of arguments.\n"
"\n"
"  Left argument          Right argument    Result\n"
"  - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n"
"  bitset                 bitset            immutable bitset\n"
"  bitset                 convertible       immutable bitset\n"
"  bitset                 other             TypeError\n"
"\n"
"  defining the same op   bitset            handled by left argument\n"
"  convertible            bitset            immutable bitset\n"
"  other                  bitset            TypeError\n"
"\n"
"\n"
"\n"
"------------------------------------------\n"
"In-place binary operations.\n"
"\n"
"The left argument must be a bitset.\n"
"If it is mutable, it is updated in place and returned.\n"
"If it is immutable, the result is a new immutable bitset.\n"
"The right argument is a bitset or a convertible.\n"
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
"Complement operation.\n"
"\n"
"~x	  -> immutable bitset\n"
"\n"
"Return the complement of x. This is a bitset that, conceptually,\n"
"contains all bits in the universe except the ones in x.\n"
"\n"
"[ Subtle\n"
"\n"
" If x is not already complemented, ~x will return a special\n"
" complemented kind of set. This can be used like other bitsets except\n"
" for two operations that are not supported: it is not possible to\n"
" iterate over, or take the length of a complemented bitset. If x is a\n"
" complemented bitset, ~x returns a non-complemented bitset.\n"
"\n"
" Mutable bitsets may become complemented in-place if given a\n"
" complemented argument to a suitable in-place operation. This is\n"
" represented by a flag. Immutable complemented bitsets are represented\n"
" by a special type, but this is to be considered an implementation\n"
" detail, it could as well be using a flag.  ]\n"
"\n"
"------------------------------------------\n"
"Shift operation.\n"
"\n"
"x << y    -> immutable bitset\n"
"\n"
"Return the set of bits of x, with the integer y added to each one.\n"
"Raise OverflowError if some bit would exceed the range of an int. \n"
"\n"
"[ Subtle\n"
"\n"
" For non-complemented x and positive y, the result is what one would\n"
" expect if x was a number in binary representation. But when x is\n"
" complemented, the result will equal\n"
"\n"
"    ~((~x) << y)\n"
"\n"
" which is different from what one would expect from binary number\n"
" shifting, since 1's are shifted in from the right.\n"
"\n"
" The operation allows both positive or negative y values, unlike the\n"
" shift for integer objects. For negative y's, the operation will shift\n"
" bits to the right but not quite in the same way as a binary integer\n"
" right-shift operation would do it, because the low bits will not\n"
" disappear but be shifted towards negative bits.  ]\n"
"\n"
"------------------------------------------\n"
"Inclusion test.\n"
"\n"
"The left argument is an integer in the range of an int.\n"
"The right argument is a bitset.\n"
"\n"
"x in y    -> bool\n"
"             True if x is an element of y, False otherwise.\n"
"\n"
"------------------------------------------\n"
"Relational operations.\n"
"\n"
"These return a boolean value.\n"
"The left argument is a bitset.\n"
"The right argument is a bitset.\n"
"If the right argument is another type, TypeError will be raised.\n"
"(This restriction may be reconsidered in the future.)\n"
"\n"
"x == y    -> Equal:\n"
"             x and y contain the same bits.\n"
"\n"
"x != y    -> Not equal:\n"
"             x and y do not contain the same bits.\n"
"\n"
"x <= y    -> Subset, non-strict:\n"
"             all bits in x are also in y.\n"
"\n"
"x < y     -> Subset, strict:\n"
"             all bits in x are also in y,\n"
"             and y contains some bits not in x.\n"
"\n"
"x >= y    -> Superset, non-strict:\n"
"             all bits in y are also in x.\n"
"\n"
"x > y     -> Superset, strict:\n"
"             all bits in y are also in x,\n"
"             and x contains some bit not in y.\n"
"\n"
"------------------------------------------\n"
"Iteration.\n"
"\n"
"iter(x)    -> iterator\n"
"\n"
"The iterator yields the bits of x.\n"
"\n"
"Raises TypeError if x is complemented.\n"
"\n"
"[The order is implementation dependent.]\n"
"\n"
"------------------------------------------\n"
"Length.\n"
"\n"
"len(x)    -> int\n"
"\n"
"Return the number of bits in x.\n"
"\n"
"Raises TypeError if x is complemented.\n"
"\n"
"------------------------------------------\n"
"Truth-value testing.\n"
"\n"
"bool(x)    -> bool\n"
"\n"
"Return True if x is not empty, False otherwise.\n"
"\n"
"------------------------------------------\n"
"Conversions.\n"
"\n"
"int(x)    -> int\n"
"long(x)   -> long\n"
"\n"
"Return an integer having the same binary representation as the bits of\n"
"x, or raise an exception if the bitset can not be represented in the\n"
"choosen type. When no exception is raised, the bitset x can be exactly\n"
"recreated and the following invariants will hold.\n"
"\n"
"    immbitset(int(x)) == x\n"
"    immbitset(long(x)) == x\n"
"\n"
"The exception OverflowError will be raised if it is found that x can\n"
"not be represented. Note that for a sparse bitset with high bit\n"
"numbers, long(x) may create a very big object since it allocates\n"
"storage for all the low bits up to the highest bit number set, unlike\n"
"bitsets that use a sparse representation. Creating such big objects\n"
"may run out of storage which may raise a MemoryError or cause some\n"
"other malfunction depending on the system.\n"
"\n"
"------------------------------------------\n"
"Mutable copy\n"
"\n"
"S.mutcopy() -> mutable bitset\n"
"\n"
"Return a mutable copy of S.\n"
;


static char ImmBitSet_doc[] = 
"ImmBitSet()         -> empty immutable bitset\n"
"ImmBitSet(bitset)   -> immutable bitset with bitset's bits\n"
"ImmBitSet(iterable) -> immutable bitset with iterable's bits (int items)\n"
"ImmBitSet(integer)  -> immutable bitset with integer's bits (binary 2-complement)\n"
"\n"
"The result can only be non-complemented; TypeError is raised\n"
"otherwise.  (The function immbitset() can be used to create both\n"
"complemented and non-complemented bitsets.)\n"
"\n"
"An immutable bitset provides the operations common for all bitsets as\n"
"described for the BitSet base class. It also defines the following:\n"
"\n"
"hash(x)    -> int\n"
"\n"
"Return a hash value based on the bit numbers of the elements.\n"
;

static char cplbitset_doc[] =

"CplBitSet(x:ImmBitSet) -> complemented immutable bitset.\n"
"\n"
"If the argument is an instance of ImmBitSet, this is the same as ~x,\n"
"otherwise TypeError is raised.\n"
"\n"
"A complemented immutable bitset provides the same operations as\n"
"non-complemented immutable bitsets, except for len() and iter().\n"
;

static char mutbitset_doc[] = 
"MutBitSet()         -> new empty mutable bitset\n"
"MutBitSet(bitset)   -> new mutable bitset with bitset's bits\n"
"MutBitSet(iterable) -> new mutable bitset with iterable's bits (int items)\n"
"MutBitSet(integer)  -> new mutable bitset with integer's bits (binary 2-complement)\n"
"\n"
"A mutable bitset has operations common for all bitsets as described\n"
"for the BitSet base class. It also defines the following methods:\n"
"\n"
"    add, append, clear, discard, pop, remove, tac, tas\n"
;

static char add_doc[] =
"S.add(e)\n"
"\n"
"Add e to S; no effect if e was already in S\n"
;

static char append_doc[] =
"S.append(e)\n"
"\n"
"Add e to S, or raise ValueError if e was already in S.";

static char discard_doc[] =
"S.discard(e)\n"
"\n"
"Remove e from S; no effect if e was not in S.";

static char pop_doc[] =
"S.pop([index]) -> int\n"
"\n"
"Remove and return a bit, or raise ValueError if there is no bit to pop.\n"
"\n"
"The index must be -1 (default) to pop the highest bit or 0 to pop the\n"
"lowest bit; otherwise IndexError will be raised.";

static char remove_doc[] =
"S.remove(e)\n"
"\n"
"Remove e from S, or raise ValueError if e was not in S.";

static char clear_doc[] =
"S.clear()\n"
"\n"
"Remove all elements from S, and compact its storage.";


static char tasbit_doc[] =
"S.tas(e) -> bool\n"
"\n"
"Test and Set.\n"
"If e is in S return True,\n"
"else add e to S and return False.";

static char tacbit_doc[] =
"S.tac(e) -> bool\n"
"\n"
"Test and Clear.\n"
"If e is in S, remove e from S and return True,\n"
"else return False.";

static char mutable_copy_doc[] =
"S.mutcopy() -> mutable bitset\n"
"\n"
"Return a mutable copy of S.\n"
;

static char bitsingle_doc[] =
"immbit(bit) -> immutable bitset\n"
"\n"
"Return an immutable bitset containing the single bit specified.\n"
"The bit must be an integer in the range of an int.";

static char bitrange_doc[] =
"immbitrange([start,] stop[, step]) -> immutable bitset\n"
"\n"
"Return an immutable bitset containing an arithmetic progression of integers.\n"
"immbitrange(i, j) equals immbitset([i, i+1, i+2, ..., j-1]).\n"
"Start defaults to 0. If step is given, it specifies a positive increment.\n"
"For example, immbitrange(3) equals immbitset([0, 1, 2]).";

static char bitform_doc[] =
"_bs(flags, data) -> some kind of bitset\n"
"\n"
"Internal function used to form a bitset when unpickling.\n"
"It is designed to be 'safe' with any data but may give strange results\n"
"if given something else than what x.__reduce__() generated.";

/* Forward declarations */

static void anybitset_classify(PyObject *v, int *vt);
static PyObject *anybitset_convert(PyObject *v, int *vt);

static PyObject *immbitset_complement(NyImmBitSetObject *v);


static PyObject *mutbitset_as_immbitset_and_cpl(NyMutBitSetObject *v, int cpl);
static PyObject *mutbitset_as_immbitset_and_del(NyMutBitSetObject *v);
static NyImmBitSetObject *mutbitset_as_noncomplemented_immbitset_subtype(
    NyMutBitSetObject *v, PyTypeObject *type);
static NyBitField *mutbitset_findpos_ins(NyMutBitSetObject *v, NyBit pos);
static NyBitField *mutbitset_findpos(NyMutBitSetObject *v, NyBit pos);
static NySetField *mutbitset_getrange_mut(NyMutBitSetObject *v, NySetField **shi);
static int mutbitset_iop_iterable(NyMutBitSetObject *ms, int op, PyObject *v);
static NyMutBitSetObject *mutbitset_new_from_arg(PyObject *arg);
static int mutbitset_reset(NyMutBitSetObject *v, NyImmBitSetObject *set);

static NySetField *root_ins1(NyMutBitSetObject *v, NySetField *sf, NyBit pos);
static NyImmBitSetObject *immbitset_realloc(NyImmBitSetObject *self, NyBit size);


static int mutbitset_ior_field(NyMutBitSetObject *v, NyBitField *w);

static int mutbitset_iop_PyLongObject(NyMutBitSetObject *ms, int op, PyObject *v);

static PyObject *NyBitSet_FormMethod;

static NyImmBitSetObject * cplbitset_cpl(NyCplBitSetObject*v);

NyImmBitSetObject *sf_slice(NySetField *ss, NySetField *se, NyBit ilow, NyBit ihigh);

/* NyBitSet_Type -- Base type with no operations, just a doc string */

PyTypeObject NyBitSet_Type = {
        PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.sets.setsc.BitSet",		/* tp_name */
	0,
	  					/* tp_basicsize */
	0,					/* tp_itemsize */
	(destructor)0,				/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	(cmpfunc)0,				/* tp_compare */
	(reprfunc)0,				/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	(hashfunc)0,				/* tp_hash */
        0,              			/* tp_call */
        (reprfunc)0,				/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES | Py_TPFLAGS_BASETYPE,
	  					/* tp_flags */
	bitset_doc,				/* tp_doc */
};


/* */

#define NOSET  0
#define BITSET  1
#define CPLSET  2
#define MUTSET  3

#define NyForm_CPL	1
#define NyForm_MUT	2

/* Predefined no-bits and all-bits sets */

NyImmBitSetObject _NyImmBitSet_EmptyStruct = {
    PyObject_HEAD_INIT(NULL)
    0	/* ob_size */
};

NyCplBitSetObject _NyImmBitSet_OmegaStruct = {
    PyObject_HEAD_INIT(NULL)
    &_NyImmBitSet_EmptyStruct	/* ob_val */
};

/* Counting bits for len() is optimized by looking up lengths of
   bit segments. The segment size is defined by this shift.  Larger
   values than 8, eg 16, can make len() some 30% faster at some tests,
   but use exponentially more table space. 11 can be a compromise.
   Experimental data can be found in notes per 5/6 -03.
*/

#define LEN_TAB_SHIFT	8	/*  8 is a memory/cache conservation setting. */

#define LEN_TAB_SIZE	(1<<LEN_TAB_SHIFT)

static int len_tab[LEN_TAB_SIZE];	/* helper for len() */

static int n_immbitset, n_cplbitset, n_mutbitset;

/* Check if an object looks like it can return an iterator
   via PyObject_GetIter, except that no iterator is created and checked.
   This is to be able to more cleanly return NotImplemented when
   doing mixed-type operations, separating not having an iterator
   from errors like returning an invalid iterator.
*/

static int
NyIterable_Check(PyObject *o)
{
    PyTypeObject *t = o->ob_type;
    return ((PyType_HasFeature(t, Py_TPFLAGS_HAVE_ITER) && t->tp_iter) ||
	    PySequence_Check(o));
}

static NyBit
bitno_modiv(NyBit bitno, NyBit *div) {
    /* We need divmod a'la Python: using algo from intobject.c */
    long xdivy = bitno / NyBits_N;
    long xmody = bitno - xdivy * NyBits_N;
    /* If the signs of x and y differ, and the remainder is non-0,
     * C89 doesn't define whether xdivy is now the floor or the
     * ceiling of the infinitely precise quotient.  We want the floor,
     * and we have it iff the remainder's sign matches y's.
     */
    if (xmody < 0) /* i.e. and signs differ */ {
	xmody += NyBits_N;
	--xdivy;
	assert(xmody && ((NyBits_N ^ xmody) >= 0));
    }
    *div = xdivy;
    return xmody;
}



static void
bitno_to_field(NyBit bitno, NyBitField *f) {
    f->bits = 1l<<bitno_modiv(bitno, &f->pos);
}

/* Find the first (lowest) or last (highest) bit set

 Only to be used when some bit is set.

 Hardcoded for 64 or 32 bit fields

*/

static int
bits_first(NyBits bits)
{
    int i = 0;
    assert(bits);

#if (NyBits_N==64)
    if (!(bits & 0xffffffff)) {
	i += 32;
	bits = bits >> 32;
    }
#elif (NyBits_N==32)
/* Nothing */
#else
#error "Unsupported NyBits_N"
#endif
    if (!(bits & 0xffff)) {
	i += 16;
	bits = bits >> 16;
    }
    if (!(bits & 0xff)) {
	i += 8;
	bits = bits >> 8;
    }
    if (!(bits & 0xf)) {
	i += 4;
	bits = bits >> 4;
    }
    if (!(bits & 0x3)) {
	i += 2;
	bits = bits >> 2;
    }
    if (!(bits & 0x1)) {
	i += 1;
	bits = bits >> 1;
    }
    assert(bits & 0x1);
    return i;
}

static int
bits_last(NyBits bits)
{
    int i = NyBits_N-1;
    assert(bits);
#if (NyBits_N==64)
    if (!(bits & 0xffffffff00000000)) {
	i -= 32;
	bits = bits << 32;
    }
    if (!(bits & 0xffff000000000000)) {
	i -= 16;
	bits = bits << 16;
    }
    if (!(bits & 0xff00000000000000)) {
	i -= 8;
	bits = bits << 8;
    }
    if (!(bits & 0xf000000000000000)) {
	i -= 4;
	bits = bits << 4;
    }
    if (!(bits & 0xc000000000000000)) {
	i -= 2;
	bits = bits << 2;
    }
    if (!(bits & 0x8000000000000000)) {
	i -= 1;
    }
#elif (NyBits_N==32)
    if (!(bits & 0xffff0000)) {
	i -= 16;
	bits = bits << 16;
    }
    if (!(bits & 0xff000000)) {
	i -= 8;
	bits = bits << 8;
    }
    if (!(bits & 0xf0000000)) {
	i -= 4;
	bits = bits << 4;
    }
    if (!(bits & 0xc0000000)) {
	i -= 2;
	bits = bits << 2;
    }
    if (!(bits & 0x80000000)) {
	i -= 1;
    }
#else
#error "Unsupported NyBits_N"
#endif
    return i;
}

static int
bits_length(NyBits bits) {
    int n = 0;
    while (bits) {
	n += len_tab[bits & (LEN_TAB_SIZE-1)];
	bits >>= LEN_TAB_SHIFT;
    }
    return n;
    
}

static NyBit
field_first(NyBitField *f)
{
    return bits_first(f->bits) + f->pos * NyBits_N;
}

static NyBit
field_last(NyBitField *f)
{
    return bits_last(f->bits) + f->pos * NyBits_N;
}

/* Quoting listobject.c */

static NyBit
roundupsize(NyBit n)
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

static NyBit
bitno_from_object(PyObject *arg)
{
    /* Get a bit number from a Python object.
       This is somewhat restrictive, but it is easier to explain,
       and nicer to later change to less restrictive but the other way around. */
    if (PyInt_Check(arg)) {
	return PyInt_AS_LONG((PyIntObject*) arg);
    } else if (PyLong_Check(arg)) {
	return PyLong_AsLong(arg); // xxx should really use Py_ssize_t or something..
    } else {
	PyErr_SetString(PyExc_TypeError, "bitno_from_object: an int or long was expected");
	return -1;
    }
}

NyImmBitSetObject *
NyImmBitSet_SubtypeNew(PyTypeObject *type, NyBit size)
{
    if (!size && type == &NyImmBitSet_Type) {
	Py_INCREF(NyImmBitSet_Empty);
	return NyImmBitSet_Empty;
    } else {
	NyImmBitSetObject *r = (void *)type->tp_alloc(type, size);
	if (r) {
	    /* Mark length as not-calculated */
	    r->ob_length = -1;
	    /* Note: the other fields are cleared by tp_alloc. */
	    n_immbitset++;
	}
	return r;
    }
}


NyImmBitSetObject *
NyImmBitSet_New(NyBit size)
{
    return NyImmBitSet_SubtypeNew(&NyImmBitSet_Type, size);
}


static NyImmBitSetObject *
NyImmBitSet_SubtypeFromIterable(PyTypeObject *type, PyObject *v)
{
    NyMutBitSetObject *ms;
    NyImmBitSetObject *ret;
    ms = NyMutBitSet_New();
    if (!ms) return 0;
    if (mutbitset_iop_iterable(ms, NyBits_OR, v) == -1) {
	Py_DECREF(ms);
	return 0;
    }
    ret = mutbitset_as_noncomplemented_immbitset_subtype(ms, type);
    Py_DECREF(ms);
    return ret;
}

static NyImmBitSetObject *
NyImmBitSet_FromIterable(PyObject *v)
{
    return NyImmBitSet_SubtypeFromIterable(&NyImmBitSet_Type, v);
}


NyImmBitSetObject *
NyImmBitSet_SubtypeNewArg(PyTypeObject *type, PyObject *v)
{
    int vt;
    NyMutBitSetObject *ms;
    NyImmBitSetObject *ret;
    if (!v) {
	return NyImmBitSet_SubtypeNew(type, 0);
    }
    anybitset_classify(v, &vt);
    if (vt == BITSET) {
	NyImmBitSetObject *bs = (NyImmBitSetObject *)v;
	NyImmBitSetObject *ret = NyImmBitSet_SubtypeNew(type, bs->ob_size);
	memcpy(ret->ob_field, bs->ob_field, sizeof(NyBitField) * bs->ob_size);
	return ret;
    }
    if (vt == MUTSET) {
	ms = (NyMutBitSetObject *)v;
	Py_INCREF(ms);
    } else {
	ms = mutbitset_new_from_arg(v);
    }
    if (!ms)
      return 0;
    if (ms->cpl) {
	PyErr_SetString(PyExc_TypeError, "ImmBitSet.__new__ : complemented arg not supported");
	Py_DECREF(ms);
	return 0;
	}
    ret = mutbitset_as_noncomplemented_immbitset_subtype(ms, type);
    Py_DECREF(ms);
    return ret;
}




static NyImmBitSetObject *
NyImmBitSet_Singleton(PyObject *arg)
{
    long bit = bitno_from_object(arg);
    if (bit == -1 && PyErr_Occurred())
      return NULL;
    else {
	NyImmBitSetObject *p = NyImmBitSet_New(1);
	if (p) {
	    bitno_to_field(bit, &p->ob_field[0]);
	}
	return p;
    }
}

static PyObject *
NyImmBitSet_FromLong(long v)
{
    if (v > 0) {
	NyImmBitSetObject *p = NyImmBitSet_New(1);
	if (!p) return 0;
	p->ob_field[0].pos = 0;
	p->ob_field[0].bits = v;
	return (PyObject *)p;
    } else if (v == 0) {
	Py_INCREF(NyImmBitSet_Empty);
	return (PyObject *)NyImmBitSet_Empty;
    } else if (v == -1) {
	Py_INCREF(NyImmBitSet_Omega);
	return (PyObject *)NyImmBitSet_Omega;
    } else {
	NyImmBitSetObject *q = (NyImmBitSetObject *)NyImmBitSet_FromLong(~v);
	PyObject *p;
	if (!q) return 0;
	p = immbitset_complement(q);
	Py_DECREF(q);
	return p;
    }
}    


static PyObject *
NyImmBitSet_FromPyIntObject(PyObject *v)
{
    long val = PyInt_AsLong(v);
    if (val == -1 && PyErr_Occurred())
      return 0;
    return NyImmBitSet_FromLong(val);
}

static PyObject *
NyImmBitSet_FromPyLongObject(PyObject  *v)
{
    NyMutBitSetObject *ms = NyMutBitSet_New();
    if (!ms) return 0;
    if (mutbitset_iop_PyLongObject(ms, NyBits_OR, v) == -1) {
	Py_DECREF(ms);
	return 0;
    }
    return mutbitset_as_immbitset_and_del(ms);
}

static int
mutbitset_initset(NyMutBitSetObject *v, NyImmBitSetObject *set)
{
    /* Requires state to be as after mutset_clear() */

    NySetField *sf = root_ins1(v, &v->fst_root.ob_field[0], NyPos_MIN);
    if (!sf)
      return -1;
    if (set) {
	sf->set = set;
	Py_INCREF(set);
	sf->lo = set->ob_field;
	sf->hi = set->ob_field + set->ob_size;
    } else {
	sf->set = immbitset_realloc(0, 1);
	sf->lo = sf->hi = sf->set->ob_field;
	if (!sf->set)
	  return -1;
    }
    return 0;
}

NyMutBitSetObject *
NyMutBitSet_SubtypeNew(PyTypeObject *type, NyImmBitSetObject *set, NyUnionObject *root)
{
    NyMutBitSetObject *v = (NyMutBitSetObject *)type->tp_alloc(type, 0);
    if (v) {
	v->cur_field = 0;
	v->cpl = 0;
	v->splitting_size = 500/*1000*/;
	v->fst_root.ob_refcnt = 1;
	v->fst_root.ob_size = 0;
	v->fst_root.cur_size = 0;
	if (!root) {
	    v->root = &v->fst_root;
	    if (mutbitset_initset(v, set) == -1) {
		Py_DECREF(v);
		return 0;
	    }
	} else {
	    assert(!set);
	    v->root = root;
	    Py_INCREF(root);
	}
	n_mutbitset++;
    }
    return v;
}

NyMutBitSetObject *
NyMutBitSet_New()
{
    return NyMutBitSet_SubtypeNew(&NyMutBitSet_Type, 0, 0);
}

static void
fp_move(NyBitField *dst, NyBitField *src, NyBit n) {
    memmove(dst, src, n * sizeof(NyBitField));
}

static void
sfp_move(NySetField *dst, NySetField *src, NyBit n) {
    memmove(dst, src, n * sizeof(NySetField));
}

static NyBitField *
bitfield_binsearch(NyBitField *lo, NyBitField *hi, NyBit pos)
{
    for (;;) {
	NyBitField *cur = lo + (hi - lo) / 2;
	if (cur == lo) {
	    if (lo < hi && lo->pos >= pos)
	      return lo;
	    else
	      return hi;
	}
	else if (cur->pos == pos)
	  return cur;
	else if (cur->pos < pos)
	  lo = cur;
	else
	  hi = cur;
    }
}

static NySetField *
setfield_binsearch(NySetField *lo, NySetField *hi, NyBit pos)
{
    for (;;) {
	NySetField *cur = lo + (hi - lo) / 2;
	if (cur == lo)
	  return lo;
	else if (cur->pos == pos)
	  return cur;
	else if (cur->pos < pos)
	  lo = cur;
	else
	  hi = cur;
    }
}

static void
union_dealloc(NyUnionObject *v)
{
    NyBit i;
    for (i = 0; i < v->cur_size; i++)
      Py_XDECREF(v->ob_field[i].set);
    PyObject_Del(v);
}

static NyUnionObject *
union_realloc(NyUnionObject *self, NyBit size)
{
    /* Changes the allocated size to make room for up-rounded size items */
    size = roundupsize(size);
    if (!self)
      return PyObject_NewVar(NyUnionObject, &NyUnion_Type, size);
    else {
	NyUnionObject *ret;
	assert(self->ob_refcnt == 1);
	_Py_ForgetReference((PyObject *)self);
	_Py_DEC_REFTOTAL;
	ret = PyObject_Realloc(self,
	 self->ob_type->tp_basicsize + self->ob_type->tp_itemsize * size);
	ret = (void *) PyObject_InitVar((void *)ret, ret->ob_type, size);
	return ret;
    }
}

static NySetField *
root_ins1(NyMutBitSetObject *v, NySetField *sf, NyBit pos)
{
    NyUnionObject *bs = v->root;
    NyBit where = sf - &bs->ob_field[0];
    NyBit cur_size = bs->cur_size;
    if (cur_size >= bs->ob_size) {
	if (bs == &v->fst_root) {
	    if (cur_size >= NyUnion_MINSIZE) {
		assert(cur_size == NyUnion_MINSIZE);
		bs = union_realloc(0, cur_size + 1);
		if (!bs) return 0;
		sfp_move(&bs->ob_field[0], &v->fst_root.ob_field[0], cur_size);
	    } else {
		bs->ob_size = cur_size + 1;
	    }
	} else {
	    bs = union_realloc(bs, cur_size + 1);
	    if (!bs) return 0;
	}
	assert (cur_size < bs->ob_size);
	v->root = bs;
	sf = &bs->ob_field[where];
    }
    assert(where <= cur_size);
    if (where < cur_size) {
	assert (sf + 1 + cur_size - where <= &bs->ob_field[bs->ob_size]);
	sfp_move(sf+1, sf, cur_size - where);
    }
    bs->cur_size = cur_size + 1;
    sf->pos = pos;
    sf->set = 0;
    return sf;
}

static NyImmBitSetObject *
immbitset_realloc(NyImmBitSetObject *self, NyBit size)
{
    NyImmBitSetObject *ret;
    /* Changes the allocated size to make room for up-rounded size items
       Allocates a new object if self == 0,
     */
    NyBit upsize = roundupsize(size);
    if (!self) {
	ret = NyImmBitSet_New(upsize);
	return ret;
    } else {
	assert(self->ob_refcnt == 1);
	_Py_ForgetReference((PyObject *)self);
	_Py_DEC_REFTOTAL;
	ret = PyObject_Realloc(self,
          self->ob_type->tp_basicsize + self->ob_type->tp_itemsize * upsize);
	ret = (void *) PyObject_InitVar((void *)ret, ret->ob_type, upsize);
	return ret;
    }
}

static NyBitField *
sf_getrange(NySetField *v, NyBitField **shi)
{
    *shi = v->hi;
    return v->lo;
}


static NyBitField *
sf_getrange_mut(NySetField *sf, NyBitField **shi)
{
    if (sf->set->ob_refcnt > 1) {
	NyImmBitSetObject *oset = sf->set;
	long lo = sf->lo - oset->ob_field;
	long hi = sf->hi - oset->ob_field;
	NyImmBitSetObject *set = NyImmBitSet_New(oset->ob_size?oset->ob_size:8);
	if (!set)
	  return 0;
	fp_move(set->ob_field, oset->ob_field, oset->ob_size);
	sf->lo = set->ob_field + lo;
	sf->hi = set->ob_field + hi;
	sf->set = set;
	Py_DECREF(oset);
    }
    *shi = sf->hi;
    return sf->lo;
}

static int
sf_realloc(NySetField *v, NyBit size)
{
    if (!v->set) {
	v->set = immbitset_realloc(0, size);
	if (!v->set)
	  return -1;
	v->lo = v->hi = v->set->ob_field + v->set->ob_size/2;
    } else {
	NyBitField *ofield = &v->set->ob_field[0];
	NyImmBitSetObject *bs = immbitset_realloc(v->set, size);
	if (!bs)
	  return -1;
	v->lo = &bs->ob_field[0] + (v->lo - ofield);
	v->hi = &bs->ob_field[0] + (v->hi - ofield);
	v->set = bs;
	assert(bs->ob_field <= v->hi && v->hi <= bs->ob_field+bs->ob_size);
	assert(bs->ob_field <= v->lo && v->lo < bs->ob_field+bs->ob_size);
    }
    return 0;
}

static NyBitField *
sf_ins1(NySetField *sf, NyBitField *f, NyBit pos)
{
    NyBitField *lo_tot = sf->set->ob_field;
    NyBitField *hi_tot = sf->set->ob_field + sf->set->ob_size;
    long lo_size = f - sf->lo;
    long hi_size = sf->hi - f;
    long tot_size = sf->hi - sf->lo;

    if (hi_size <= lo_size && sf->hi < hi_tot)      goto MOVE_HI;
    if (lo_size <= hi_size && sf->lo > lo_tot)      goto MOVE_LO;
    if (hi_size <= lo_size * 3 && sf->hi < hi_tot)  goto MOVE_HI;
    if (lo_size <= hi_size * 3 && sf->lo > lo_tot)  goto MOVE_LO;

    if (tot_size * 8 < sf->set->ob_size * 7) {
	/* Not extremely filled. May pay to center it. */
	NyBit move = ((hi_tot - sf->hi) - (sf->lo - lo_tot)) / 2;
	fp_move(sf->lo + move, sf->lo, tot_size);
	f += move;
	sf->lo += move;
	sf->hi += move;
	if (hi_size <= lo_size && sf->hi < hi_tot)      goto MOVE_HI;
	if (lo_size <= hi_size && sf->lo > lo_tot)      goto MOVE_LO;
	assert(0);
	
    }

    if (sf_realloc(sf, sf->hi + 1 - lo_tot) == -1)
      return 0;
    f = sf->lo + lo_size;

    hi_tot = sf->set->ob_field + sf->set->ob_size;
    lo_tot = sf->set->ob_field;
    {
	NyBit move = ((hi_tot - sf->hi) - (sf->lo - lo_tot)) / 2;
	fp_move(sf->lo + move, sf->lo, tot_size);
	f += move;
	sf->lo += move;
	sf->hi += move;
	if (hi_size <= lo_size && sf->hi < hi_tot)      goto MOVE_HI;
	if (lo_size <= hi_size && sf->lo > lo_tot)      goto MOVE_LO;
	assert(0);
	
    }

 MOVE_HI:
    fp_move(f + 1, f, hi_size);
    sf->hi++;
    return f;

  MOVE_LO:
    fp_move(sf->lo - 1, sf->lo, lo_size);
    sf->lo--;
    return f - 1;
}

static NyBitField *
mutbitset_split_ins1(NyMutBitSetObject *v, NySetField *sf, NyBitField *f, NyBit pos) {
    NyBit sfpos = sf - v->root->ob_field;
    NyBit a_size = f - sf->lo;
    NyBit b_size = sf->hi - f;
    NySetField *nsf = root_ins1(v, sf+1, pos);
    assert(a_size >= 0);
    assert(b_size >= 0);
    if (!nsf)
      return 0;
    sf = v->root->ob_field + sfpos;
    if (sf_realloc(nsf, b_size) == -1)
      return 0;
    nsf->lo = nsf->set->ob_field + (nsf->set->ob_size - b_size) / 2;
    nsf->hi = nsf->lo + b_size;
    fp_move(nsf->lo, f, b_size);
    nsf->pos = nsf->lo->pos;
    sf->hi = f;
    if (sf_realloc(sf, f + 1 - sf->set->ob_field) == -1)
      return 0;
    f = sf->lo + a_size;
    sf->hi = f + 1;
    assert(sf->hi <= sf->set->ob_field+sf->set->ob_size);
    return f;
}

static NyBitField *
mutbitset_ins1(NyMutBitSetObject *v, NySetField *sf, NyBitField *f, NyBit pos)
{
    if (f - sf->lo > v->splitting_size &&
	sf->hi - f > v->splitting_size)
      f = mutbitset_split_ins1(v, sf, f, pos);
    else
      f = sf_ins1(sf, f, pos);
    if (f) {
	f->pos = pos;
	f->bits = 0;
    }
    return f;
}

static NyBitField *
mutbitset_findpos(NyMutBitSetObject *v, NyBit pos)
{
    NyBitField *f = v->cur_field;
    NySetField *sf;
    if (f && f->pos == pos)
      return f;
    {
	NyUnionObject *root = v->root;
	NySetField *lo = &root->ob_field[0];
	NySetField *hi = &root->ob_field[root->cur_size];
	sf = setfield_binsearch(lo, hi, pos);
	assert(lo <= sf && sf < hi);
	assert(lo->pos <= pos);
	assert(sf >= lo);
    }
    {
	f = bitfield_binsearch(sf->lo, sf->hi, pos);
	if (!(f < sf->hi && f->pos == pos))
	  f = 0;
	return f;
    }
}


static NyBitField *
mutbitset_findpos_mut(NyMutBitSetObject *v, NyBit pos)
{
    NyBitField *f = v->cur_field;
    NyUnionObject *root;
    NySetField *sf;
    if (f && f->pos == pos)
      return f;
    root = v->root;
    {
	NySetField *lo = &root->ob_field[0];
	NySetField *hi = &root->ob_field[root->cur_size];
	sf = setfield_binsearch(lo, hi, pos);
	assert(lo <= sf && sf < hi);
	assert(lo->pos <= pos);
	assert(sf >= lo);
    }
    {
	f = bitfield_binsearch(sf->lo, sf->hi, pos);
	if (!(f < sf->hi && f->pos == pos))
	  /* Not found so we are not going to update. */
	  f = 0;
	else {
	    if (root->ob_refcnt > 1 || sf->set->ob_refcnt > 1) {
		/* It was found but some struct needs to be copied.
		   Just research in ins mode. */
		f = mutbitset_findpos_ins(v, pos);
	    }
	}
    }
    return f;
}


static NyBitField *
mutbitset_findpos_ins(NyMutBitSetObject *v, NyBit pos)
{
    int ins = 1;
    NySetField *sf;
    NyBitField *f = v->cur_field;
    if (f && f->pos == pos)
      return f;
    {
	NySetField *lo, *hi;
	hi = 0; /* Avoid warning */
	lo = mutbitset_getrange_mut(v, &hi);
	sf = setfield_binsearch(lo, hi, pos);
	assert(lo <= sf && sf < hi);
	assert(lo->pos <= pos);
	assert(sf >= lo);
    }
    {
	NyBitField *lo, *hi;
	lo = sf_getrange_mut(sf, &hi);
	f = bitfield_binsearch(sf->lo, sf->hi, pos);
	if (ins) {
	    if (!(f < sf->hi && f->pos == pos))
	      f = mutbitset_ins1(v, sf, f, pos);
	    v->cur_field = f;
	} else {
	    if (!(f < sf->hi && f->pos == pos))
	      f = 0;
	}
	return f;
    }

}

static NySetField *
union_getrange(NyUnionObject *v, NySetField **shi)
{
    *shi = &v->ob_field[v->cur_size];
    return &v->ob_field[0];
}


static NySetField *
mutbitset_getrange(NyMutBitSetObject *v, NySetField **shi)
{
    return union_getrange(v->root, shi);
}

static NySetField *
mutbitset_getrange_mut(NyMutBitSetObject *v, NySetField **shi)
{
    NyUnionObject *root = v->root;
    if (root->ob_refcnt > 1) {
	NyUnionObject *nroot = PyObject_NewVar(NyUnionObject, &NyUnion_Type, root->ob_size);
	NyBit i;
	if (!nroot)
	  return 0;
	nroot->cur_size = root->cur_size;
	sfp_move(nroot->ob_field, root->ob_field, root->cur_size);
	for (i = 0; i < nroot->cur_size; i++) {
	    Py_INCREF(nroot->ob_field[i].set);
	}
	v->root = nroot;
	/* assert(!v->cur_field); */ /* See note Oct 20 2004
	   			- it may not be 0 in all cases */

	v->cur_field = 0; /* see notes per 5/6-03,  when it was thought
			 that it should be 0 already but just in case */
	Py_DECREF(root);
	root = nroot;
    }
    return union_getrange(root, shi);
}

static NyImmBitSetObject *
mutbitset_as_noncomplemented_immbitset_subtype(NyMutBitSetObject *v, PyTypeObject *type)
{
    NyBit j;
    NyBit size = 0;
    NyImmBitSetObject *bs;
    NySetField *slo, *shi, *s;
    NyBitField *fhi, *flo, *f;
    flo = fhi = 0; /* Just avoid a spurios undefined-warning */
    slo = mutbitset_getrange(v, &shi);
    for (s = slo; s < shi; s++) {
	flo = sf_getrange(s, &fhi);
	for (f = flo; f < fhi; f++) {
	    if (f->bits)
	      size++;
	}
    }
    if ((type == &NyImmBitSet_Type &&
	 shi - slo == 1 &&
	 fhi - flo == size &&
	 slo->set->ob_size == size)) {
	bs = slo->set;
	Py_INCREF(bs);
	v->cur_field = 0;
    } else {
	bs = NyImmBitSet_SubtypeNew(type, size);
	if (!bs) return 0;
	j = 0;
	for (s = slo; s < shi; s++) {
	    flo = sf_getrange(s, &fhi);
	    for (f = flo; f < fhi; f++) {
		if (f->bits)
		  bs->ob_field[j++] = *f;
	    }
	}
	assert (j == size);
    }
    return bs;
}

static NyImmBitSetObject *
mutbitset_as_noncomplemented_immbitset(NyMutBitSetObject *v)
{
    return mutbitset_as_noncomplemented_immbitset_subtype(v, &NyImmBitSet_Type);
}


static PyObject *
mutbitset_as_immbitset_and_cpl(NyMutBitSetObject *v, int cpl)
{
    NyImmBitSetObject *bs = mutbitset_as_noncomplemented_immbitset(v);
    PyObject *ret;
    if (!bs)
      return 0;
    if ((v->cpl != 0) != (cpl != 0)) {
	ret = immbitset_complement(bs);
	Py_DECREF(bs);
    } else
      ret = (PyObject *)bs;
    return ret;
}

PyObject *
NyMutBitSet_AsImmBitSet(NyMutBitSetObject *v)
{
    return mutbitset_as_immbitset_and_cpl(v, 0);
}

static PyObject *
mutbitset_as_immbitset_and_del(NyMutBitSetObject *v)
{
    PyObject *bs = NyMutBitSet_AsImmBitSet(v);
    Py_DECREF(v);
    return bs;
}


int
NyMutBitSet_hasbit(NyMutBitSetObject *v, NyBit bit)
{
    NyBitField f, *fp;
    bitno_to_field(bit, &f);
    fp = mutbitset_findpos(v, f.pos);
    if (!fp)
      return 0;
    return (fp->bits & f.bits) != 0;
}
static int
mutbitset_contains(NyMutBitSetObject *v, PyObject *w)
{
    NyBit bit = bitno_from_object(w);
    if (bit == -1 && PyErr_Occurred())
      return -1;
    return NyMutBitSet_hasbit(v, bit);
}

static int
mutbitset_clear(NyMutBitSetObject *v)
{
    if (v->root != &v->fst_root) {
	Py_DECREF(v->root);
    } else {
	NyBit i;
	for (i = 0; i < v->root->cur_size; i++)
	  Py_DECREF(v->root->ob_field[i].set);
    }
    v->cur_field = 0;
    v->root = &v->fst_root;
    v->fst_root.ob_size = 0;
    v->fst_root.cur_size = 0;
    return 0;
}


static void
mutbitset_dealloc(NyMutBitSetObject *v)
{
    mutbitset_clear(v);
    v->ob_type->tp_free((PyObject *)v);
    n_mutbitset--;
}

static void
mutbitset_set_hi(NyMutBitSetObject *v, NySetField *sf, NyBitField *f)
{
    sf->hi = f;
    v->cur_field = 0;
}

static void
mutbitset_set_lo(NyMutBitSetObject *v, NySetField *sf, NyBitField *f)
{
    sf->lo = f;
    v->cur_field = 0;
}

static PyObject *
mutbitset_complement(NyMutBitSetObject *v)
{
    return mutbitset_as_immbitset_and_cpl(v, 1);
}

static PyObject *
mutbitset_int(NyMutBitSetObject *v)
{
    PyObject *w = NyMutBitSet_AsImmBitSet(v);
    PyObject *x;
    if (!w) return 0;
    x = PyNumber_Int(w);
    Py_DECREF(w);
    return x;
}
 

static PyObject *
mutbitset_long(NyMutBitSetObject *v)
{
    PyObject *w = NyMutBitSet_AsImmBitSet(v);
    PyObject *x;
    if (!w) return 0;
    x = PyNumber_Long(w);
    Py_DECREF(w);
    return x;
}
 

static int
mutbitset_ior_field(NyMutBitSetObject *v, NyBitField *w)
{
    NyBitField *f;
    if (w->bits) {
	f = mutbitset_findpos_ins(v, w->pos);
	if (!f)  return -1;
	f->bits |= w->bits;
    }
    return 0;
}

static int
mutbitset_ior_fields(NyMutBitSetObject *v, NyBitField *w, NyBit n)
{
    for (; n--;)
      if (mutbitset_ior_field(v, w++))
	return -1;
    return 0;
}

static int
mutbitset_iop_field(NyMutBitSetObject *v, int op, NyBitField *w)
{
    NyBitField *f;
    switch(op) {
      case NyBits_OR:
	return mutbitset_ior_field(v, w);
      case NyBits_XOR:
	if (w->bits) {
	    f = mutbitset_findpos_ins(v, w->pos);
	    if (!f)  return -1;
	    f->bits ^= w->bits;
	}
	break;
      case NyBits_SUB:
	if (w->bits) {
	    f = mutbitset_findpos_mut(v, w->pos);
	    if (!f)  return 0;
	    f->bits &= ~ w->bits;
	}
	break;
      default:
	PyErr_SetString(PyExc_ValueError,
			"Invalid mutbitset_iop_field() operation");
	return -1;
    }
    return 0;
}

/* cpl_conv_left

   Convert left inversion

   ~a & b  ==  		   ==  	a SUBR b
   ~a | b  ==  ~(a & ~ b)  == 	~(a SUB b)
   ~a ^ b  ==		   ==	~(a ^ b)
   ~a SUB b == ~a & ~b    ==	~(a | b)
   ~a SUBR b == ~(~a) & b ==   a & b 

*/


int
cpl_conv_left(int *cplp, int op)
{
    if (*cplp) {
	switch(op) {
	  case NyBits_AND:   op = NyBits_SUBR; *cplp = 0; break;
	  case NyBits_OR:    op = NyBits_SUB; break;
	  case NyBits_XOR:   break;
	  case NyBits_SUB:  op = NyBits_OR; break;
	  case NyBits_SUBR: op = NyBits_AND; *cplp = 0; break;
	  default: assert(0);
	}
    }
    return op;
}

/* cpl_conv_right

   Convert right inversion

   a & ~b  ==  		   ==  	a SUB b
   a | ~b  ==  ~(~a & b)   == 	~(a SUBR b)
   a ^ ~b  ==		   ==	~(a ^ b)
   a SUB ~b == a & ~(~b)  ==	a & b
   a SUBR ~b == ~a & ~b   ==   ~(a | b)

*/

int
cpl_conv_right(int op, int *cplp)
{
    if (*cplp) {
	switch(op) {
	  case NyBits_AND:   op = NyBits_SUB;  *cplp = 0; break;
	  case NyBits_OR:    op = NyBits_SUBR; break;
	  case NyBits_XOR:   break;
	  case NyBits_SUB:  op = NyBits_AND; *cplp = 0; break;
	  case NyBits_SUBR: op = NyBits_OR; break;
	  default: assert(0);
	}
    }
    return op;
}

static int
mutbitset_iop_convert(NyMutBitSetObject *v, int op)
{
    return cpl_conv_left(&v->cpl, op);
}

static int
mutbitset_iop_fields(NyMutBitSetObject *v, int op, NyBitField *w, int n)
{
    NySetField *s, *end_s;
    NyBitField *f, *end_w, *end_f;
    end_s = 0; /* avoid warning */
    op = mutbitset_iop_convert(v, op);
    switch(op) {
      case NyBits_OR:
      case NyBits_XOR:
      case NyBits_SUB:
	while (n > 0) {
	    if (mutbitset_iop_field(v, op, w) == -1)
	      return -1;
	    n--;
	    w++;
	}
	break;
      case NyBits_AND:
	end_w = w + n;
	for (s = mutbitset_getrange_mut(v, &end_s); s < end_s; s++)
	  for (f = sf_getrange_mut(s, &end_f); f < end_f; f++) {
	      while (w < end_w && f->pos > w->pos)
		w++;
	      if (w < end_w && w->pos == f->pos) {
		  f->bits &= w->bits;
		  w++;
	      } else {
		  f->bits = 0;
	      }
	  }
	break;
      case NyBits_SUBR: {
	  NyBit i;
	  for (i = 0; i < n; i++) {
	      if (w[i].bits) {
		  if (!mutbitset_findpos_ins(v, w[i].pos))
		    return -1;
	      }
	  }
	  end_w = w + n;
	  for (s = mutbitset_getrange_mut(v, &end_s); s < end_s; s++)
	    for (f = sf_getrange_mut(s, &end_f); f < end_f; f++) {
		while (w < end_w && f->pos > w->pos)
		  w++;
		if (w < end_w && w->pos == f->pos) {
		    f->bits = ~f->bits & w->bits;
		    w++;
		} else {
		    f->bits = 0;
		}
	    }
      }
	break;
      default:
	PyErr_SetString(PyExc_ValueError,
			"Invalid mutbitset_iop_fields() operation");
	return -1;
    }
    return 0;
}

static int
mutbitset_iop_bitno(NyMutBitSetObject *v, int op, NyBit bitno)
{
    NyBitField f;
    bitno_to_field(bitno, &f);
    return mutbitset_iop_fields(v, op, &f, 1);
}

static int
mutbitset_iop_bits(NyMutBitSetObject *v, int op, NyBit pos, NyBits *bits, NyBit n)
{
    NySetField *s, *end_s;
    NyBitField *f, *end_f;
    end_s = 0; /* avoid warning */
    op = mutbitset_iop_convert(v, op);
    switch(op) {
      case NyBits_OR:
      case NyBits_XOR:
      case NyBits_SUB:
	while (n > 0) {
	    NyBitField f;
	    f.pos = pos;
	    f.bits = *bits++;
	    if (mutbitset_iop_field(v, op, &f) == -1)
	      return -1;
	    n--;
	    pos++;
	}
	break;
      case NyBits_AND: {
	  for (s = mutbitset_getrange_mut(v, &end_s); s < end_s; s++)
	    for (f = sf_getrange_mut(s, &end_f); f < end_f; f++) {
	      while (n > 0 && f->pos > pos) {
		  n--;
		  pos++;
		  bits++;
	      }
	      if (n > 0 && f->pos == pos) {
		  f->bits &= *bits++;
		  n--;
		  pos++;
	      } else {
		  f->bits = 0;
	      }
	  }
      }
	break;
      case NyBits_SUBR: {
	  int i;
	  for (i = 0; i < n; i++) {
	      if (bits[i]) {
		  if (!mutbitset_findpos_ins(v, pos + i))
		    return -1;
	      }
	  }
	  for (s = mutbitset_getrange_mut(v, &end_s); s < end_s; s++)
	    for (f = sf_getrange_mut(s, &end_f); f < end_f; f++) {
	      while (n > 0 && f->pos > pos) {
		  n--;
		  pos++;
		  bits++;
	      }
	      if (n > 0 && f->pos == pos) {
		  f->bits = ~f->bits & *bits++;
		  n--;
		  pos++;
	      } else {
		  f->bits = 0;
	      }
	  }
      }
	break;
      default:
	PyErr_SetString(PyExc_ValueError,
			"Invalid mutbitset_iop_bits() operation");
	return -1;
    }
    return 0;
}


static int
mutbitset_iop_immbitset(NyMutBitSetObject *v, int op, NyImmBitSetObject *w)
{
    return mutbitset_iop_fields(v, op, w->ob_field, w->ob_size);
}

static int
mutbitset_reset(NyMutBitSetObject *v, NyImmBitSetObject *set)
{
    mutbitset_clear(v);
    return mutbitset_initset(v, set);
}

int NyMutBitSet_clear(NyMutBitSetObject *v)
{
    return mutbitset_reset(v, 0);
}


static int
mutbitset_iop_complement(NyMutBitSetObject *v)
{     
    v->cpl = !v->cpl;
    return 0;
}

static int
mutbitset_iop_cplbitset(NyMutBitSetObject *v, int op, NyCplBitSetObject *w)
{
    int cpl = 1;
    int r;
    op = cpl_conv_right(op, &cpl);
    r = mutbitset_iop_immbitset(v, op, cplbitset_cpl(w));
    if (!r && cpl)
      r = mutbitset_iop_complement(v);
    return r;
}

static int
mutbitset_iop_mutset(NyMutBitSetObject *v, int op, NyMutBitSetObject *w)
{
    int cpl = w->cpl;
    NySetField *s, *end_s;
    NyBitField *f, *end_f, *wf;
    end_s = 0; /* avoid warning */
    op = cpl_conv_right(op, &cpl);
    op = mutbitset_iop_convert(v, op);
    if (v == w) {
	/* Special caseing this because:
	   - may be problems updating the same we iterate on
	   - the special case may likely be faster
	   - an obvious opportunity to clear out redundant storage when eg doing ms ^= ms
	*/
	switch (op) {
	  case NyBits_OR:
	  case NyBits_AND:
	    break;
	  case NyBits_SUB:
	  case NyBits_SUBR:
	  case NyBits_XOR:
	    if (mutbitset_reset(v, 0) == -1)
	      return -1;
	    break;
	  default:
	    PyErr_SetString(PyExc_ValueError,
			    "Invalid mutbitset_iop_fields() operation");
	    return -1;
	}
    } else
      switch(op) {
      case NyBits_OR:
      case NyBits_XOR:
      case NyBits_SUB:
	  for (s = mutbitset_getrange(w, &end_s); s < end_s; s++)
	    for (f = sf_getrange(s, &end_f); f < end_f; f++)
	      if (mutbitset_iop_field(v, op, f) == -1)
		return -1;
	  break;
      case NyBits_AND:
	  for (s = mutbitset_getrange_mut(v, &end_s); s < end_s; s++)
	    for (f = sf_getrange_mut(s, &end_f); f < end_f; f++) {
		wf = mutbitset_findpos(w, f->pos);
		if (wf)
		  f->bits &= wf->bits;
		else
		  f->bits = 0;
	    }
	  break;
      case NyBits_SUBR:
	  for (s = mutbitset_getrange(w, &end_s); s < end_s; s++)
	    for (f = sf_getrange(s, &end_f); f < end_f; f++)
	      if (!mutbitset_findpos_ins(v, f->pos))
		return -1;
	  for (s = mutbitset_getrange_mut(v, &end_s); s < end_s; s++)
	    for (f = sf_getrange_mut(s, &end_f); f < end_f; f++) {
		wf = mutbitset_findpos(w, f->pos);
		if (wf)
		  f->bits = ~f->bits & wf->bits;
		else
		  f->bits = 0;
	    }
	  break;
      default:
	PyErr_SetString(PyExc_ValueError,
			"Invalid mutbitset_iop_fields() operation");
	return -1;
      }
    if (cpl)
      mutbitset_iop_complement(v);
    return 0;
}

static int
mutbitset_iop_iterable(NyMutBitSetObject *ms, int op, PyObject *v)
{
    PyObject *it = 0;      /* iter(v) */
    NyMutBitSetObject *tms;
    if (op == NyBits_AND) {
	tms = NyMutBitSet_New();
	if (!tms) return -1;
	op = NyBits_OR;
    }
    else
      tms = ms;


    it = PyObject_GetIter(v);
    if (it == NULL)
      goto Err;
    /* Run iterator to exhaustion. */
    for (;;) {
	PyObject *item = PyIter_Next(it);
	long bit;
	if (item == NULL) {
	    if (PyErr_Occurred())
	      goto Err;
	    break;
	}
	bit = bitno_from_object(item);
	Py_DECREF(item);
	if (bit == -1 && PyErr_Occurred())
	  goto Err;
	if (mutbitset_iop_bitno(tms, op, bit) == -1)
	  goto Err;
    }
    if (tms != ms) {
	if (mutbitset_iop_mutset(ms, NyBits_AND, tms) == -1)
	  goto Err;
	Py_DECREF(tms);
    }
    Py_DECREF(it);
    return 0;
  Err:
    if (tms != ms) {
	Py_DECREF(tms);
    }
    Py_XDECREF(it);
    return -1;

}

static int
mutbitset_iop_PyIntObject(NyMutBitSetObject *ms, int op, PyObject *v)
{
    long val = PyInt_AsLong(v);
    NyBitField f;
    int r;
    int cpl = 0;
    if (val == -1 && PyErr_Occurred())
      return -1;
    f.pos = 0;
    if (val < 0) {
	cpl = !cpl;
	op = cpl_conv_right(op, &cpl);
	val = ~val;
    }
    f.bits = val;
    r = mutbitset_iop_fields(ms, op, &f, 1);
    if (!r && cpl)
      r = mutbitset_iop_complement(ms);
    return r;
}

static int
mutbitset_iop_PyListObject(NyMutBitSetObject *ms, int op, PyObject *v)
{
    NyBit size = PyList_GET_SIZE(v);
    NyBit i;
    NyMutBitSetObject *tms;
    if (op == NyBits_AND) {
	tms = NyMutBitSet_New();
	if (!tms) return -1;
	op = NyBits_OR;
    }
    else
      tms = ms;
    for (i = 0; i < size; i++) {
	long bit = bitno_from_object(PyList_GET_ITEM(v, i));
	if (bit == -1 && PyErr_Occurred())
	  goto Err;
	if (mutbitset_iop_bitno(tms, op, bit) == -1)
	  goto Err;
    }
    if (tms != ms) {
	if (mutbitset_iop_mutset(ms, NyBits_AND, tms) == -1)
	  goto Err;
	Py_DECREF(tms);
    }
    return 0;

  Err:
    if (tms != ms) {
	Py_DECREF(tms);
    }
    return -1;

}

static int
mutbitset_iop_PyTupleObject(NyMutBitSetObject *ms, int op, PyObject *v)
{
    NyBit size = PyTuple_GET_SIZE(v);
    NyBit i;
    NyMutBitSetObject *tms;
    if (op == NyBits_AND) {
	tms = NyMutBitSet_New();
	if (!tms) return -1;

	op = NyBits_OR;
    }
    else
      tms = ms;
    for (i = 0; i < size; i++) {
	long bit = bitno_from_object(PyTuple_GET_ITEM(v, i));
	if (bit == -1 && PyErr_Occurred())
	  goto Err;
	if (mutbitset_iop_bitno(tms, op, bit) == -1)
	  goto Err;
    }
    if (tms != ms) {
	if (mutbitset_iop_mutset(ms, NyBits_AND, tms) == -1)
	  goto Err;
	Py_DECREF(tms);
    }
    return 0;

  Err:
    if (tms != ms) {
	Py_DECREF(tms);
    }
    return -1;

}

static int
mutbitset_iop_PyDictObject(NyMutBitSetObject *ms, int op, PyObject *v)
{
    Py_ssize_t i;
    NyMutBitSetObject *tms;
    PyObject *key, *value;
    if (op == NyBits_AND) {
	tms = NyMutBitSet_New();
	if (!tms) return -1;
	op = NyBits_OR;
    }
    else
      tms = ms;
    i = 0;
    while (PyDict_Next(v, &i, &key, &value)) {
	NyBit bit = bitno_from_object(key);
	if (bit == -1 && PyErr_Occurred())
	  goto Err;
	if (mutbitset_iop_bitno(tms, op, bit) == -1)
	  goto Err;
    }
    if (tms != ms) {
	if (mutbitset_iop_mutset(ms, NyBits_AND, tms) == -1)
	  goto Err;
	Py_DECREF(tms);
    }
    return 0;

  Err:
    if (tms != ms) {
	Py_DECREF(tms);
    }
    return -1;

}

static int
mutbitset_iop_PyLongObject(NyMutBitSetObject *ms, int op, PyObject *v)
{
    NyBits *buf;
    int r = -1;
    int e;
    long num_poses, num_bytes;
    double num_bits, x;
    int cpl = 0;
    PyObject *w = 0;
    
#if PY_VERSION_HEX >= 0x02070000
	x = _PyLong_Frexp(v, &e);
#else
	x = _PyLong_AsScaledDouble(v, &e);
#endif
    if (x == -1 && PyErr_Occurred())
      return -1;
    if (x < 0) {
	cpl = !cpl;
	op = cpl_conv_right(op, &cpl);
	w = PyNumber_Invert(v);
	if (!w) return -1;
	v = w;
#if PY_VERSION_HEX >= 0x02070000
	x = _PyLong_Frexp(v, &e);
#else
	x = _PyLong_AsScaledDouble(v, &e);
#endif
	if (x == -1 && PyErr_Occurred())
	  return -1;
	assert(x >= 0);
    }
    if (x != 0) {
	num_bits = e;
#if PY_VERSION_HEX < 0x02070000
	num_bits *= SHIFT;
#endif
	num_bits += log(x)/log(2) + 1;
    }
    else
	num_bits = 0;
	
    num_poses = (long)(num_bits / NyBits_N + 1);
    /* fprintf(stderr, "x %f e %d num_bits %f num_poses %ld\n", x, e, num_bits, num_poses); */
    num_bytes = num_poses * sizeof(NyBits);
    buf = PyMem_New(NyBits, num_poses);
    if (!buf) {
	PyErr_NoMemory();
	goto Err1;
    }
    r = _PyLong_AsByteArray((PyLongObject *)v,
			(unsigned char *)buf,
			num_bytes,
			1, /* little_endian */
			0  /* is_signed */);
    if (r == -1) goto Err1;
#if NyBits_IS_BIG_ENDIAN
    {
	NyBit pos;
	for (pos = 0; pos < num_poses; pos++) {
	    buf[pos] = NyBits_BSWAP(buf[pos]);
	}
    }
#endif

    r = mutbitset_iop_bits(ms, op, 0, buf, num_poses);
    if (!r && cpl)
      r = mutbitset_iop_complement(ms);
  Err1:
    PyMem_Del(buf);
    Py_XDECREF(w);
    return r;
}

PyObject *
mutbitset_iop(NyMutBitSetObject *v, int op, PyObject *w)
{
    int wt = 0;
    int r;
    anybitset_classify(w, &wt);
    if (wt == BITSET)
      r = mutbitset_iop_immbitset(v, op, (NyImmBitSetObject *)w);
    else if (wt == CPLSET)
      r = mutbitset_iop_cplbitset(v, op, (NyCplBitSetObject *)w);
    else if (wt == MUTSET)
      r = mutbitset_iop_mutset(v, op, (NyMutBitSetObject *)w);
    else if (PyInt_Check(w))
      r = mutbitset_iop_PyIntObject(v, op, w);
    else if (PyLong_Check(w))
      r = mutbitset_iop_PyLongObject(v, op, w);
    else if (PyList_Check(w))
      r = mutbitset_iop_PyListObject(v, op, w);
    else if (PyTuple_Check(w))
      r = mutbitset_iop_PyTupleObject(v, op, w);
    else if (PyDict_Check(w))
      r = mutbitset_iop_PyDictObject(v, op, w);
    else if (PyDict_Check(w))
      r = mutbitset_iop_PyDictObject(v, op, w);
    else if (NyIterable_Check(w))
      r = mutbitset_iop_iterable(v, op, w);
    else {
	PyErr_Format(PyExc_TypeError,
		     "operand for mutable bitset must be integer or iterable");
	return NULL;
    }
    if (r == -1)
      return NULL;
    else {
	Py_INCREF(v);
	return (PyObject *)v;
    }
}

PyObject *
mutbitset_iand(NyMutBitSetObject *v, PyObject *w)
{
    return mutbitset_iop(v, NyBits_AND, w);
}

PyObject *
mutbitset_ior(NyMutBitSetObject *v, PyObject *w)
{
    return mutbitset_iop(v, NyBits_OR, w);
}

PyObject *
mutbitset_isub(NyMutBitSetObject *v, PyObject *w)
{
    return mutbitset_iop(v, NyBits_SUB, w);
}

PyObject *
mutbitset_ixor(NyMutBitSetObject *v, PyObject *w)
{
    return mutbitset_iop(v, NyBits_XOR, w);
}

PyObject *
mutbitset_iter(NyMutBitSetObject *v)
{
    PyObject *bs = NyMutBitSet_AsImmBitSet(v);
    if (bs) {
	PyObject *iter = PyObject_GetIter(bs);
	Py_DECREF(bs);
	return iter;
    }
    return 0;
}


static NyMutBitSetObject *
mutbitset_subtype_new_from_arg(PyTypeObject *type, PyObject *arg)
{
    NyMutBitSetObject *ms;
    NyImmBitSetObject *set = 0;
    NyUnionObject *root = 0;
    if (arg) {
	if (NyImmBitSet_Check(arg)) {
	    set = (NyImmBitSetObject *)arg;
	    Py_INCREF(set);
	} else if (NyMutBitSet_Check(arg)) {
	    NyMutBitSetObject *oms = (NyMutBitSetObject *)arg;
	    if (oms->root != &oms->fst_root) {
		root = oms->root;
		Py_INCREF(root);
		oms->cur_field = 0;
	    }
	}
    }
    ms = NyMutBitSet_SubtypeNew(type, set, root);
    Py_XDECREF(set);
    Py_XDECREF(root);
    if (!ms) return 0;
    if (!(set || root)) {
	if (arg) {
	    void *r = mutbitset_ior(ms, arg);
	    Py_DECREF(ms);
	    ms = r;
	}
    }
    return ms;
}

static NyMutBitSetObject *
mutbitset_new_from_arg(PyObject *arg)
{
    return mutbitset_subtype_new_from_arg(&NyMutBitSet_Type, arg);
}

static PyObject *
mutbitset_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *arg = NULL;
    static char *kwlist[] = {"arg", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O:mutbitset_new",kwlist, &arg))
      return NULL;
    return (PyObject *)mutbitset_subtype_new_from_arg(type, arg);
}

static Py_ssize_t
    mutbitset_length(PyObject *_v)
{
    NyMutBitSetObject *v=(void*)_v;
    NySetField *s, *end_s;
    NyBitField *f, *end_f;
    int n = 0;
    if (v->cpl) {
	PyErr_SetString(PyExc_TypeError, "len() of complemented set is undefined");
	return -1;
    }
    for (s = mutbitset_getrange(v, &end_s); s < end_s; s++)
      for (f = sf_getrange(s, &end_f); f < end_f; f++) {
	  NyBits bits = f->bits;
	  if (bits) {
	      n += bits_length(bits);
	      if (n < 0) {
		  PyErr_SetString(PyExc_OverflowError, "len() is too large");
		  return -1;
	      }
	  }
      }
    return n;
}

static int
mutbitset_nonzero(NyMutBitSetObject *v)
{
    NySetField *s, *end_s;
    NyBitField *f, *end_f;
    if (v->cpl)
      return 1;
    for (s = mutbitset_getrange(v, &end_s); s < end_s; s++)
      for (f = sf_getrange(s, &end_f); f < end_f; f++)
	if (f->bits)
	  return 1;
    return 0;
}

static PyObject *
mutbitset_repr(NyMutBitSetObject *a)
{
	char buf[256];
	PyObject *s, *t, *comma, *v, *iter;
	int i;
	if (a->cpl) {
	    PyOS_snprintf(buf, sizeof(buf), "MutBitSet(~ImmBitSet([");
	    /* Subtle:
	       Get around that mutbitset doesnt allow iteration when complemented -
	       this getaround assumes iter copies it to an immutable bitset. */
	    a->cpl = 0;
	    iter = PyObject_GetIter((PyObject *)a);
	    a->cpl = 1;
	}
	else {
	    PyOS_snprintf(buf, sizeof(buf), "MutBitSet([");
	    iter = PyObject_GetIter((PyObject *)a);
	}
	s = PyString_FromString(buf);
	comma = PyString_FromString(", ");
	if (!(iter && s && comma)) goto Fail;
	for (i = 0; ; i++) {
		v = PyIter_Next(iter);
		if (!v) {
		    if (PyErr_Occurred())
		      goto Fail;
		    break;
		}
		if (i > 0)
			PyString_Concat(&s, comma);
		t = PyObject_Repr(v);
		Py_XDECREF(v);
		PyString_ConcatAndDel(&s, t);
	}
	Py_XDECREF(iter);
	Py_XDECREF(comma);
	if (a->cpl)
	  PyString_ConcatAndDel(&s, PyString_FromString("]))"));
	else
	  PyString_ConcatAndDel(&s, PyString_FromString("])"));
	return s;
      Fail:
	Py_XDECREF(iter);
	Py_XDECREF(comma);
	Py_XDECREF(s);
	return 0;
}

static int
mutbitset_set_or_clr(NyMutBitSetObject *v, NyBit bitno, int set_or_clr)
{
    NyBitField f, *fp;
    int ap = set_or_clr;
    if (v->cpl)
      ap = !ap;
    bitno_to_field(bitno, &f);
    if (ap) {
	fp = mutbitset_findpos_ins(v, f.pos);
	if (!fp)
	  return -1;
	if (fp->bits & f.bits)
	  return set_or_clr;
	fp->bits |= f.bits;
    } else {
	fp = mutbitset_findpos_mut(v, f.pos);
	if (!(fp && (fp->bits & f.bits))) {
	    return set_or_clr;
	}
	fp->bits &= ~f.bits;
    }
    return !set_or_clr;
}


int
NyMutBitSet_setbit(NyMutBitSetObject *v, NyBit bitno)
{
  return mutbitset_set_or_clr(v, bitno, 1);
}

int
NyMutBitSet_clrbit(NyMutBitSetObject *v, NyBit bitno)
{
  return mutbitset_set_or_clr(v, bitno, 0);
}

static PyObject *
mutbitset_tasbit(NyMutBitSetObject *v, PyObject *w)
{
    long bitno = bitno_from_object(w);
    int r;
    if (bitno == -1 && PyErr_Occurred())
      return 0;
    r = NyMutBitSet_setbit(v, bitno);
    if (r == -1)
      return 0;
    return PyInt_FromLong(r);
}


static PyObject *
mutbitset_tacbit(NyMutBitSetObject *v, PyObject *w)
{
    long bitno = bitno_from_object(w);
    int r;
    if (bitno == -1 && PyErr_Occurred())
      return 0;
    r = NyMutBitSet_clrbit(v, bitno);
    if (r == -1)
      return 0;
    return PyInt_FromLong(r);
}


static int
bitfields_iterate(NyBitField *f, NyBitField *end_f,
		   int (*visit)(NyBit, void *),
		   void *arg)
{
    for (;f < end_f; f++) {
	NyBits bits = f->bits;
	int bitpos = 0;
	while (bits) {
	    while (!(bits & 1)) {
		bits >>= 1;
		bitpos += 1;
	    }
	    if (visit(f->pos * NyBits_N + bitpos, arg) == -1)
	      return -1;
	    bits >>= 1;
	    bitpos += 1;
	}
    }
    return 0;
}


static int
mutbitset_iterate(NyMutBitSetObject *v,
		   int (*visit)(NyBit, void *),
		   void *arg)
{
    NySetField *s, *end_s;
    for (s = mutbitset_getrange(v, &end_s); s < end_s; s++) {
	NyBitField *f, *end_f;
	f = sf_getrange(s, &end_f);
	if (bitfields_iterate(f, end_f, visit, arg) == -1)
	  return -1;
    }
    return 0;
}

static int
immbitset_iterate(NyImmBitSetObject *v,
		   int (*visit)(NyBit, void *),
		   void *arg)
{
    return bitfields_iterate(&v->ob_field[0], &v->ob_field[v->ob_size],
			     visit, arg);
}


int
NyAnyBitSet_iterate(PyObject *v,
		   NySetVisitor visit,
		   void *arg)
{
    if (NyImmBitSet_Check(v))
      return immbitset_iterate((NyImmBitSetObject *)v, visit, arg);
    else if (NyMutBitSet_Check(v))
      return mutbitset_iterate((NyMutBitSetObject *)v, visit, arg);
    else {
	PyErr_Format(PyExc_TypeError,
		     "operand for anybitset_iterate must be immbitset or mutset");
	return -1;
    }
}


static PyObject *
mutbitset_append_or_remove(NyMutBitSetObject *v, PyObject *w, int ap, char *errmsg)
{
    NyBitField f, *fp;
    NyBit bitno = bitno_from_object(w);
    if (bitno == -1 && PyErr_Occurred())
      return 0;
    bitno_to_field(bitno, &f);
    if (v->cpl)
      ap = !ap;
    if (ap) {
	fp = mutbitset_findpos_ins(v, f.pos);
	if (!fp)
	  return 0;
	if (fp->bits & f.bits) {
	    PyErr_Format(PyExc_ValueError,
			 errmsg, bitno);
	    return 0;
	}
	fp->bits |= f.bits;
    } else {
	fp = mutbitset_findpos_mut(v, f.pos);
	if (!(fp && (fp->bits & f.bits))) {
	    PyErr_Format(PyExc_ValueError,
			 errmsg, bitno);
	    return 0;
	}
	fp->bits &= ~f.bits;
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
mutbitset_add_or_discard(NyMutBitSetObject *v, PyObject *w, int what)
{
    long bitno = bitno_from_object(w);
    int r;
    if (bitno == -1 && PyErr_Occurred())
      return 0;
    r = mutbitset_set_or_clr(v, bitno, what);
    if (r == -1)
      return 0;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
mutbitset_add(NyMutBitSetObject *v, PyObject *w)
{
    return mutbitset_add_or_discard(v, w, 1);
}

static PyObject *
mutbitset_append(NyMutBitSetObject *v, PyObject *w)
{
    return mutbitset_append_or_remove(v, w, 1,
	  "mutset.append(%ld): bit is already in the set.");
}

static PyObject *
mutbitset_discard(NyMutBitSetObject *v, PyObject *w)
{
    return mutbitset_add_or_discard(v, w, 0);
}

static PyObject *
mutbitset_remove(NyMutBitSetObject *v, PyObject *w)
{
    return mutbitset_append_or_remove(v, w, 0,
	   "mutset.remove(%ld): bit is not in the set.");
}

static PyObject *
_mutbitset_clear(NyMutBitSetObject *self, PyObject *args)
{
    if (NyMutBitSet_clear(self) == -1)
      return 0;
    Py_INCREF(Py_None);
    return Py_None;
    
}

long
NyMutBitSet_pop(NyMutBitSetObject *v, NyBit i)
{
    NyBit j;
    NySetField *s, *end_s;
    NyBitField *f, *end_f;
    NyBit ret = 0;
    s=0;end_s=0; /* avoid warnings */
    if (v->cpl) {
	PyErr_SetString(PyExc_ValueError,
"pop(): The mutset is complemented, and doesn't support pop.\n");
	return -1;
    }
    if (i == - 1) {
	for (end_s = mutbitset_getrange_mut(v, &s); --s >= end_s;)
	  for (end_f = sf_getrange_mut(s, &f); --f >= end_f;) {
	    if (f->bits) {
		j = bits_last(f->bits);
		ret = f->pos * NyBits_N + j;
		f->bits &= ~(1l<<j);
		if (f->bits)
		  mutbitset_set_hi(v, s, f+1);
		else
		  mutbitset_set_hi(v, s, f);
		return ret;
	    }
	}
    } else if (i == 0) {
	for (s = mutbitset_getrange_mut(v, &end_s); s < end_s; s++)
	  for (f = sf_getrange_mut(s, &end_f); f < end_f; f++) {
	    if (f->bits) {
		j = bits_first(f->bits);
		ret = f->pos * NyBits_N + j;
		f->bits &= ~(1l<<j);
		if (f->bits)
		  mutbitset_set_lo(v, s, f);
		else
		  mutbitset_set_lo(v, s, f+1);
		return ret;
	    }
	}
    } else {
	PyErr_SetString(PyExc_IndexError, "pop(): index must be 0 or -1");
	return -1;
    }
    PyErr_SetString(PyExc_ValueError, "pop(): empty set");
    return -1;
}

static PyObject *
mutbitset_pop(NyMutBitSetObject *v, PyObject *args)
{
    int i = -1;
    NyBit bit;
    if (!PyArg_ParseTuple(args, "|i:pop", &i))
      return NULL;
    bit = NyMutBitSet_pop(v, i);
    if (bit == -1 && PyErr_Occurred())
      return 0;
    return PyInt_FromLong(bit); /// xxx from ...
}

static PyObject *
mutbitset_slice(NyMutBitSetObject *a, NyBit ilow, NyBit ihigh)
{
    
    NySetField *ss, *se;
    if (ilow == 0 && ihigh == LONG_MAX) {
	return NyMutBitSet_AsImmBitSet(a);
    }
    if (a->cpl) {
	PyErr_SetString(PyExc_IndexError,
"mutbitset_slice(): The mutset is complemented, and doesn't support other slice than [:].\n");
	return NULL;
    }
    ss = mutbitset_getrange(a, &se);
    return (PyObject *)sf_slice(ss, se, ilow, ihigh);
}


/* stripped down & specialized version of PySlice_GetIndices
   Bitsets don't currently support other step than 1
   and don't support a constant-time length, so we need to do without that.
   Notes per 5/6 -03 comment on why sq_slice didn't work.
*/

static int
NySlice_GetIndices(PySliceObject *r, NyBit *start, NyBit *stop)
{
    NyBit sstep, *step = &sstep;
	if (r->step == Py_None) {
		*step = 1;
	} else {
		if (!PyInt_Check(r->step)) return -1;
		*step = PyInt_AsLong(r->step);
		if (*step != 1) {
		    PyErr_SetString(PyExc_IndexError, "bitset slicing step must be 1");
		    return -1;
		}
	}
	if (r->start == Py_None) {
		*start = 0;
	} else {
		if (!PyInt_Check(r->start)) return -1;
		*start = PyInt_AsLong(r->start);
	}
	if (r->stop == Py_None) {
		*stop = LONG_MAX;
	} else {
		if (!PyInt_Check(r->stop)) return -1;
		*stop = PyInt_AsLong(r->stop);
	}
	return 0;
}



static PyObject *
mutbitset_subscript(NyMutBitSetObject *v, PyObject *w)
{
    NyBit i;
    NySetField *s, *end_s;
    NyBitField *f, *end_f;
    if (PySlice_Check(w)) {
	NyBit start, stop;
	if (NySlice_GetIndices((PySliceObject *)w, &start, &stop) == -1)
	  return NULL;
	return mutbitset_slice(v, start, stop);
    }
    i = PyInt_AsLong(w);
    if (i == -1 && PyErr_Occurred())
      return 0;
    if (v->cpl) {
	PyErr_SetString(PyExc_IndexError,
"mutbitset_subscript(): The mutset is complemented, and doesn't support indexing.\n");
	return NULL;
    }
    if (i == - 1) {
	for (end_s = mutbitset_getrange(v, &s); --s >= end_s;)
	  for (end_f = sf_getrange(s, &f); --f >= end_f;)
	    if (f->bits)
	      return PyInt_FromLong(field_last(f));
    } else if (i == 0) {
	for (s = mutbitset_getrange(v, &end_s); s < end_s; s++)
	  for (f = sf_getrange(s, &end_f); f < end_f; f++)
	    if (f->bits)
	      return PyInt_FromLong(field_first(f));
    } else {
	PyErr_SetString(PyExc_IndexError, "mutbitset_subscript(): index must be 0 or -1");
	return NULL;
    }
    PyErr_SetString(PyExc_IndexError, "mutbitset_subscript(): empty set");
    return NULL;
}



NyCplBitSetObject *
NyCplBitSet_SubtypeNew(PyTypeObject *type, NyImmBitSetObject *v)
{
    if (type == &NyCplBitSet_Type && v == NyImmBitSet_Empty) {
	Py_INCREF(NyImmBitSet_Omega);
	return NyImmBitSet_Omega;
    } else {
	NyCplBitSetObject *w = (NyCplBitSetObject *) type->tp_alloc(type, 1);
	if (w) {
	    w->ob_val = v;
	    Py_INCREF(v);
	    n_cplbitset++;
	}
	return w;
    }
}

NyCplBitSetObject *
NyCplBitSet_New(NyImmBitSetObject *v)
{
    return NyCplBitSet_SubtypeNew(&NyCplBitSet_Type, v);
}

NyCplBitSetObject *
NyCplBitSet_New_Del(NyImmBitSetObject *v)
{
    if (v) {
	NyCplBitSetObject *w = NyCplBitSet_New(v);
	Py_DECREF(v);
	return w;
    }
    return 0;
}

static NyBitField *
immbitset_findpos(NyImmBitSetObject *v, NyBit pos)
{
    NyBitField *f = v->ob_field;
    NyBitField *hi = & v->ob_field[v->ob_size];
    f = bitfield_binsearch(f, hi, pos);
    if (!(f < hi && f->pos == pos))
      return 0;
    return f;
}


static NyImmBitSetObject *
immbitset_op(NyImmBitSetObject *v, int op, NyImmBitSetObject *w)
{
    long z, pos;
    NyBits bits, a, b;
    NyImmBitSetObject *dst = 0;
    NyBitField *zf, *vf, *wf, *ve, *we;
    ve = &v->ob_field[v->ob_size];
    we = &w->ob_field[w->ob_size];
    for (z = 0, zf = 0; ;) {
	for (vf = &v->ob_field[0], wf = &w->ob_field[0];;) {
	    if (vf < ve) {
		if (wf < we) {
		    if (vf->pos <= wf->pos) {
			pos = vf->pos;
			a = vf->bits;
			if (vf->pos == wf->pos) {
			    b = wf->bits;
			    wf++;
			} else {
			    b = NyBits_EMPTY;
			}
			vf++;
		    } else {		/* (vf->pos > wf->pos) { */
			pos = wf->pos;
			a = NyBits_EMPTY;
			b = wf->bits;
			wf++;
		    }
		} else {
		    pos = vf->pos;
		    a = vf->bits;
		    vf++;
		    b = NyBits_EMPTY;
		}
	    } else if (wf < we) { 
		pos = wf->pos;
		a = NyBits_EMPTY;
		b = wf->bits;
		wf++;
	    } else
	      break;
	    switch(op) {
	      case NyBits_AND:		bits = a & b;		break;
	      case NyBits_OR:		bits = a | b;		break;
	      case NyBits_XOR:		bits = a ^ b;		break;
	      case NyBits_SUB:		bits = a & ~b;		break;
	      default:			bits = 0;	/* slicence undefined-warning */
					assert(0);
	    }
	    if (bits) {
		if (zf) {
		    zf->pos = pos;
		    zf->bits = bits;
		    zf++;
		} else {
		    z++;
		}
	    }
	}
	if (zf) {
	    return dst;
	} else {
	    dst = NyImmBitSet_New(z);
	    if (!dst)
	      return dst;
	    zf = & dst->ob_field[0];
	}
    }
}

static PyObject *
cpl_immbitset_op(NyImmBitSetObject *v, int op, NyImmBitSetObject *w)
{
    return (PyObject *)NyCplBitSet_New_Del(immbitset_op(v, op, w));
}

static PyObject *
immbitset_and(NyImmBitSetObject *v, PyObject *w, int wt)
{
    switch (wt) {
      case BITSET:
	return (PyObject *)immbitset_op(v, NyBits_AND, (NyImmBitSetObject *)w);
      case CPLSET:
	return (PyObject *)immbitset_op(v, NyBits_SUB, cplbitset_cpl((NyCplBitSetObject *)w));
      default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}


int
NyImmBitSet_hasbit(NyImmBitSetObject *v, NyBit bit)
{
    NyBitField f, *fp;
    bitno_to_field(bit, &f);
    fp = immbitset_findpos(v, f.pos);
    if (!fp)
      return 0;
    return (fp->bits & f.bits) != 0;

}

static int
immbitset_contains(NyImmBitSetObject *v, PyObject *w)
{
    long bit = bitno_from_object(w);
    if (bit == -1 && PyErr_Occurred())
      return -1;
    return NyImmBitSet_hasbit(v, bit);
}

static void
immbitset_dealloc(PyObject *v)
{
    v->ob_type->tp_free((PyObject *)v);
    n_immbitset--;
}

static int
immbitset_hash(NyImmBitSetObject *v)
{
    NyBitField *f = &v->ob_field[0];
    NyBitField *f_stop = &v->ob_field[v->ob_size];
    long h = 0x1d567f9f;
    while (f < f_stop) {
	h ^= f->bits ^ f->pos;
	f++;
    }
    h += (h >> 16);
    h += (h >> 8);
    h += (h >> 4);
    h += (h << 7);
    if (h == -1)
      h = -2;
    return h;

}

PyObject *
immbitset_int(NyImmBitSetObject *v)
{
    NyBitField *f = &v->ob_field[0];
    NyBitField *f_stop = &v->ob_field[v->ob_size];
    if (f >= f_stop)
      return PyInt_FromLong(0L);
    if (f->pos < 0) {
	PyErr_SetString(PyExc_OverflowError,
			"immbitset with negative bits can not be convert to int");
	return 0;
    }
    if (f + 1 < f_stop ||
	f->pos != 0 ||
	(long)f->bits < 0) {
	PyErr_SetString(PyExc_OverflowError, "immbitset too large to convert to int");
	return 0;
    }
    return PyInt_FromLong(f->bits);
}


static PyObject *
immbitset_complement(NyImmBitSetObject *v)
{
    return (PyObject *)NyCplBitSet_New(v);
}

static Py_ssize_t
immbitset_length(PyObject *_v)
{
    NyImmBitSetObject *v=(void*)_v;

    Py_ssize_t n = v->ob_length;
    if (n == -1) {
	Py_ssize_t i;
	for (i = 0, n = 0; i < v->ob_size; i++) {
	    n += bits_length(v->ob_field[i].bits);
	    if (n < 0) {
		PyErr_SetString(PyExc_OverflowError, "len() of this immbitset is too large to tell");
		return -1;
	    }
	}
	v->ob_length = n;
    }
    return n;
}

int
NyAnyBitSet_length(PyObject *v)
{
    if (NyImmBitSet_Check(v))
      return immbitset_length(v);
    else if (NyMutBitSet_Check(v))
      return mutbitset_length(v);
    else {
	PyErr_SetString(PyExc_ValueError, "NyAnyBitSet_length: bitset required.");
	return -1;
    }
}			

int
pos_add_check(NyBit a, NyBit b)
{
    NyBit tst;
    tst = a + b;
    if (NyPos_MIN <= tst && tst <= NyPos_MAX)
      return 0;
    else
      return -1;
}

static NyImmBitSetObject *
immbitset_lshift(NyImmBitSetObject *v, NyBit w)
{
    NyBit posshift;
    NyBit remshift;
    NyBit n;
    NyBit lopos, hipos;
    NyBit i;
    if (v == NyImmBitSet_Empty) {
	Py_INCREF(NyImmBitSet_Empty);
	return NyImmBitSet_Empty;
    }
    n = v->ob_size;
    lopos = v->ob_field[0].pos;
    hipos = v->ob_field[n-1].pos;
    remshift = bitno_modiv(w, &posshift);
    if (remshift) {
	if (!(v->ob_field[0].bits << remshift))
	  lopos++;
	if ((v->ob_field[v->ob_size-1].bits >> (NyBits_N - remshift)))
	  hipos++;
    } 
    if (pos_add_check(lopos, posshift) ||
	pos_add_check(hipos, posshift)) {
	PyErr_SetString(PyExc_OverflowError, "immbitset_lshift(): too large shift count");
	return 0;
    }
    if (!remshift) {
	NyImmBitSetObject *ret = NyImmBitSet_New(n);
	if (!ret)
	  return 0;
	for (i = 0; i < n; i++) {
	    ret->ob_field[i].bits = v->ob_field[i].bits;
	    ret->ob_field[i].pos = v->ob_field[i].pos + posshift;
	}
	return ret;
    } else {
	NyMutBitSetObject *ms = NyMutBitSet_New();
	NyBitField fs[2], *f;
	if (!ms)
	  return 0;
	f = v->ob_field;
	for (i = 0; i < n; i++) {
	    fs[0].pos = f->pos + posshift;
	    fs[1].pos = f->pos + posshift + 1;
	    fs[0].bits = f->bits << remshift;
	    fs[1].bits = f->bits >> (NyBits_N - remshift);
	    if (mutbitset_ior_fields(ms, &fs[0], 2) == -1) {
		Py_DECREF(ms);
		return 0;
	    }
	    f++;
	}
	return (NyImmBitSetObject *)mutbitset_as_immbitset_and_del(ms);
    }
}

NyImmBitSetObject *
sf_slice(NySetField *ss, NySetField *se, NyBit ilow, NyBit ihigh)
{
    long nbits = 0;
    long nbitswanted;
    long nfields = 0;
    long i;
    NySetField *s;
    NyBitField *f, *fe, *fs, *g;
    NyImmBitSetObject *bs;
    if (ilow == 0 && ihigh > 0) {
	nbitswanted = ihigh;
	for (s = ss; s < se; s++) {
	    for (f = sf_getrange(s, &fe); f < fe; f++) {
		if (nbits >= nbitswanted)
		  break;
		if (f->bits) {
		    nbits += bits_length(f->bits);
		    nfields += 1;
		}
	    }
	    if (nbits >= nbitswanted)
	      break;
	}
	bs = NyImmBitSet_New(nfields);
	g = bs->ob_field;
	i = 0;
	for (s = ss; s < se; s++) {
	    for (f = sf_getrange(s, &fe); f < fe; f++) {
		if (i >= nfields)
		  break;
		if (f->bits) {
		    g->bits = f->bits;
		    g->pos = f->pos;
		    g++;
		    i++;
		}
	    }
	    if (i >= nfields)
	      break;
	}
	if (nbits > nbitswanted) {
	    assert (g > bs->ob_field);
	    g--;
	    while (nbits > nbitswanted) {
		g->bits &= ~(1l<<bits_last(g->bits));
		nbits--;
	    }
	}
	return bs;
    } else if (ilow < 0 && ihigh == LONG_MAX) {
	nbitswanted = - ilow;
	for (s = se; --s >= ss;) {
	    for (fs = sf_getrange(s, &f); --f >= fs; ) {
		if (nbits >= nbitswanted)
		  break;
		if (f->bits) {
		    nbits += bits_length(f->bits);
		    nfields += 1;
		}
	    }
	    if (nbits >= nbitswanted)
	      break;
	}
	bs = NyImmBitSet_New(nfields);
	g = bs->ob_field + nfields - 1;
	i = 0;
	for (s = se; --s >= ss;) {
	    for (fs = sf_getrange(s, &f); --f >= fs; ) {
		if (i >= nfields)
		  break;
		if (f->bits) {
		    g->bits = f->bits;
		    g->pos = f->pos;
		    g--;
		    i++;
		}
	    }
	    if (i >= nfields)
	      break;
	}
	if (nbits > nbitswanted) {
	    g++;
	    assert (g == bs->ob_field);
	    while (nbits > nbitswanted) {
		g->bits &= ~(1l<<bits_first(g->bits));
		nbits--;
	    }
	}
	return bs;
    } else {
	PyErr_SetString(PyExc_IndexError, "this slice index form is not implemented");
	return NULL;
    }

}

static NyImmBitSetObject *
immbitset_slice(NyImmBitSetObject *a, NyBit ilow, NyBit ihigh)
{
    
    NySetField s;
    if (ilow == 0 && ihigh == LONG_MAX) {
	Py_INCREF(a);
	return a;
    }
    s.lo = a->ob_field;
    s.hi = a->ob_field + a->ob_size;
    return sf_slice(&s, (&s)+1, ilow, ihigh);
}


static PyObject *
immbitset_subscript(NyImmBitSetObject *v, PyObject *w)
{
    long i;
    if (PySlice_Check(w)) {
	NyBit start, stop;
	if (NySlice_GetIndices((PySliceObject *)w, &start, &stop) == -1)
	  return NULL;
	return (PyObject *)immbitset_slice(v, start, stop);
    }
    i = PyInt_AsLong(w);
    if (i == -1 && PyErr_Occurred())
      return 0;
    if (v == NyImmBitSet_Empty) {
	PyErr_SetString(PyExc_IndexError, "empty immbitset - index out of range");
	return 0;
    }
    if (i == 0) {
	return PyInt_FromLong(field_first(v->ob_field));
    } else if (i == -1) {
	return PyInt_FromLong(field_last(&v->ob_field[v->ob_size-1]));
    } else {
	PyErr_SetString(PyExc_IndexError, "immbitset_subscript(): index must be 0 or -1");
	return NULL;
    }
}

PyObject *
immbitset_long(NyImmBitSetObject *v)
{
    NyBit num_poses, pos;
    NyBits bits, *buf;
    NyBitField *f = &v->ob_field[0];
    NyBitField *f_stop = &v->ob_field[v->ob_size];
    PyObject *r;
    if (f >= f_stop)
      return PyLong_FromLong(0L);

    if (f->pos < 0) {
	PyErr_SetString(PyExc_OverflowError,
			"immbitset with negative bits can not be converted to long");
	return 0;
    }
    num_poses = (f_stop-1)->pos + 1;
    if (num_poses > NyPos_MAX) {
	PyErr_SetString(PyExc_OverflowError, "immbitset too large to convert to long");
	return 0;
    }
    buf = PyMem_New(NyBits, num_poses);
    if (!buf) {
	PyErr_NoMemory();
	return 0;
    }
    for (pos = 0; pos < num_poses; pos++) {
	if (pos == f->pos) {
	    bits = f->bits;
#if NyBits_IS_BIG_ENDIAN
	    bits = NyBits_BSWAP(bits);
#endif
	    f++;
	} else {
	    bits = NyBits_EMPTY;
	}
	buf[pos] = bits;
    }
    r = _PyLong_FromByteArray((unsigned char *)buf,		/* bytes */
			      num_poses * sizeof(NyBits),	/* n = number of bytes*/
			      1,	/* Always little endian here */
			      0);	/* not is_signed, never here */
    PyMem_Del(buf);
    return r;
}

static PyObject *
immbitset_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *arg = NULL;
    static char *kwlist[] = {"arg", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O:immbitset", kwlist, &arg))
      return NULL;
    return (PyObject *)NyImmBitSet_SubtypeNewArg(type, arg);
}


static char immbitset_doc[] =
"immbitset()         -> empty immutable bitset\n"
"immbitset(bitset)   -> immutable bitset with bitset's bits\n"
"immbitset(iterable) -> immutable bitset with iterable's bits (int items)\n"
"immbitset(integer)  -> immutable bitset with integer's bits (binary 2-complement)\n"
"\n"
"Return an immutable bitset. It will be complemented if the argument\n"
"is a complemented bitset or a negative integer. If the argument is an\n"
"immutable bitset, the result is the same object.\n"
;


static PyObject *
immbitset(PyTypeObject *unused, PyObject *args, PyObject *kwds)
{
    PyObject *arg = NULL;
    PyObject *ret;
    int clas;
    static char *kwlist[] = {"arg", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O:immbitset", kwlist, &arg))
      return NULL;
    if (arg == NULL)
      return (PyObject *)NyImmBitSet_New(0);
    else {
	clas = NOSET;
	ret = anybitset_convert(arg, &clas);
	if (clas == NOSET) {
	    if (ret) {
		PyErr_Format(PyExc_TypeError,
			     "operand for immbitset must be a bitset, iterable or integer");
		Py_DECREF(ret);
	    }
	    return NULL;
	}
	return ret;
    }
}

static int
immbitset_nonzero(NyImmBitSetObject *v)
{
    return v != NyImmBitSet_Empty;
}

static int
sf_tst_sf(NySetField *as, NySetField *ase, int op, NySetField *bs, NySetField *bse)
{
    NyBitField *af, *afe, *bf, *bfe;
    NyBits a, b, c;

    if (op == NyBits_TRUE)
      return 1;

    if (as < ase) {
	af = sf_getrange(as, &afe);
	as++;
    } else
      af = afe = 0;

    if (bs < bse) {
	bf = sf_getrange(bs, &bfe);
	bs++;
    } else
      bf = bfe = 0;

    for (;;) {
	if (af < afe) {
	    if (bf < bfe) {
		if (af->pos < bf->pos) {
		    a = af++->bits;
		    b = 0;
		} else {
		    if (af->pos == bf->pos) {
			a = af++->bits;
		    } else {
			a = 0;
		    }
		    b = bf++->bits;
		    if (bf == bfe) {
			if (bs < bse) {
			    bf = sf_getrange(bs, &bfe);
			    bs++;
			}
		    }
		}
	    } else {
		a = af++->bits;
		b = 0;
	    }
	    if (af == afe) {
		if (as < ase) {
		    af = sf_getrange(as, &afe);
		    as++;
		}
	    }
	} else if (bf < bfe) {
	    a = 0;
	    b = bf++->bits;
	    if (bf == bfe) {
		if (bs < bse) {
		    bf = sf_getrange(bs, &bfe);
		    bs++;
		}
	    }
	} else
	  return 0;

	switch (op) {
	  case NyBits_AND:		c = a & b;		break;
	  case NyBits_OR:		c = a | b;		break;
	  case NyBits_XOR:		c = a ^ b;		break;
	  case NyBits_SUB:		c = a & ~b;		break;
	  case NyBits_SUBR:		c = ~a & b;		break;
	  default:			c = 0;	/* silence undefined-warning */
	    				assert(0);
	}
	if (c)
	  return 1;
    }
}


void
claset_load(PyObject *v, int vt, int *cpl, NySetField *vst, NySetField **vs, NySetField **vse)
{
    switch (vt) {
      case BITSET: {
	  NyImmBitSetObject *bs = (NyImmBitSetObject *)v;
	  *cpl = 0;
	  vst->lo = bs->ob_field;
	  vst->hi = bs->ob_field+bs->ob_size;
	  *vs = vst;
	  *vse = vst+1;
	  break;
      }
      case CPLSET: {
	  NyImmBitSetObject *bs = cplbitset_cpl((NyCplBitSetObject *)v);
	  *cpl = 1;
	  vst->lo = bs->ob_field;
	  vst->hi = bs->ob_field+bs->ob_size;
	  *vs = vst;
	  *vse = vst+1;
	  break;
      }
      case MUTSET: {
	  NyMutBitSetObject *ms = (NyMutBitSetObject *)v;
	  *cpl = ms->cpl;
	  *vs = union_getrange(ms->root, vse);
	  break;
      }
      default:
	assert(0);
    }
}

static PyObject *
claset_richcompare(PyObject *v, int vt, PyObject *w, int op)
{
    NySetField *vs, *vse, *ws, *wse, vst, wst;
    int vcpl, wcpl;
    int cpl = 0;
    int swap = 0;
    int decw = 0;
    int tst;
    int res;
    PyObject *ret = 0;
    int wt;
    anybitset_classify(w, &wt);
    if (wt == NOSET) {
	PyErr_SetString(PyExc_TypeError, "bitset_richcompare: some bitset expected");
	return 0;
/*	We might consider returning NotImplemented but ... we might want
	to implement it here and then we would get a compatibility problem!
	See also Notes May 19 2005.
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
*/


    }
    switch(op) {
      case Py_EQ:	
      case Py_LE:	
      case Py_LT:	break;
      case Py_NE:	cpl = 1; op = Py_EQ; break;
      case Py_GE:	swap = 1; op = Py_LE; break;
      case Py_GT:	swap = 1; op = Py_LT; break;
      default: assert(0);
    }
    if (swap) {
	PyObject *nw = v;
	int nwt = vt;
	v = w;
	vt = wt;
	w = nw;
	wt = nwt;
    }
    claset_load(v, vt, &vcpl, &vst, &vs, &vse);
    claset_load(w, wt, &wcpl, &wst, &ws, &wse);
    switch (op) {
      case Py_EQ:
	if (vcpl == wcpl) {
	    res = !sf_tst_sf(vs, vse, NyBits_XOR, ws, wse);
	} else
	  res = 0;
	break;
      case Py_LE:
      case Py_LT:
	switch (vcpl * 2 | wcpl) {
	  case 0:	tst = NyBits_SUB; ; break;
	  case 1:	tst = NyBits_AND;  ; break;
	  case 2:	tst = NyBits_TRUE; break;
	  case 3:	tst = NyBits_SUBR;;break;
	  default:	tst = NyBits_TRUE;  /* Silence gcc undefined-warning */
	    		assert(0);
	}
	res = !sf_tst_sf(vs, vse, tst, ws, wse);
	if (res && op == Py_LT && vcpl == wcpl) {
	    res = sf_tst_sf(vs, vse, NyBits_XOR, ws, wse);
	}
	break;
      default:
	res = 0; /* silence undefined-warning */
	assert(0);
    }
    if (cpl)
      res = !res;
    ret = res ? Py_True:Py_False;
    if (decw) {
	Py_DECREF(w);
    }
    Py_INCREF(ret);
    return ret;
}

static PyObject *
immbitset_richcompare(NyImmBitSetObject *v, PyObject *w, int op)
{
    return claset_richcompare((PyObject *)v, BITSET, w, op);
}    


static PyObject *
cplbitset_richcompare(NyCplBitSetObject *v, PyObject *w, int op)
{
    return claset_richcompare((PyObject *)v, CPLSET, w, op);
}    


static PyObject *
mutbitset_richcompare(NyMutBitSetObject *v, PyObject *w, int op)
{
    return claset_richcompare((PyObject *)v, MUTSET, w, op);
}    


static PyObject *
immbitset_or(NyImmBitSetObject *v, PyObject *w, int wt)
{
    switch (wt) {
      case BITSET:
	return (PyObject *)immbitset_op(v, NyBits_OR, (NyImmBitSetObject *)w);
      case CPLSET:
	return cpl_immbitset_op(cplbitset_cpl((NyCplBitSetObject *)w), NyBits_SUB, v);
      default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}

static PyObject *
immbitset_repr(NyImmBitSetObject *a)
{
	char buf[256];
	PyObject *s, *t, *comma, *v, *iter;
	NyBit i, len;
	len = a->ob_size;
	if (len == 0) {
		PyOS_snprintf(buf, sizeof(buf), "ImmBitSet([])");
		return PyString_FromString(buf);
	}
	PyOS_snprintf(buf, sizeof(buf), "ImmBitSet([");
	s = PyString_FromString(buf);
	comma = PyString_FromString(", ");
	iter = PyObject_GetIter((PyObject *)a);
	if (!(iter && s && comma)) goto Fail;
	for (i = 0; ; i++) {
		v = PyIter_Next(iter);
		if (!v) {
		    if (PyErr_Occurred())
		      goto Fail;
		    break;
		}
		if (i > 0)
			PyString_Concat(&s, comma);
		t = PyObject_Repr(v);
		Py_XDECREF(v);
		PyString_ConcatAndDel(&s, t);
	}
	Py_XDECREF(iter);
	Py_XDECREF(comma);
	PyString_ConcatAndDel(&s, PyString_FromString("])"));
	return s;
      Fail:
	Py_XDECREF(iter);
	Py_XDECREF(comma);
	Py_XDECREF(s);
	return 0;
}

static PyObject *
immbitset_sub(NyImmBitSetObject *v, PyObject *w, int wt)
{
    switch (wt) {
      case BITSET:
	return (PyObject *)immbitset_op(v, NyBits_SUB, (NyImmBitSetObject *)w);
      case CPLSET:
	return (PyObject *)immbitset_op(v, NyBits_AND, cplbitset_cpl((NyCplBitSetObject *)w));
      default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}



static PyObject *
immbitset_xor(NyImmBitSetObject *v, PyObject *w, int wt)
{
    switch (wt) {
      case BITSET:
	return (PyObject *)immbitset_op(v, NyBits_XOR, (NyImmBitSetObject *)w);
      case CPLSET:
	return cpl_immbitset_op(v, NyBits_XOR, cplbitset_cpl((NyCplBitSetObject *)w));
      default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}


typedef struct {
	PyObject_HEAD
	NyImmBitSetObject *immbitset;
	NyBit fldpos;
	NyBit bitpos;
} NyImmBitSetIterObject;


PyObject *
immbitset_iter(NyImmBitSetObject *v)
{
     NyImmBitSetIterObject *iter;
     iter = PyObject_New(NyImmBitSetIterObject, &NyImmBitSetIter_Type);
     if (iter) {
	 iter->immbitset = v;
	 Py_INCREF(v);
	 iter->fldpos = 0;
	 iter->bitpos = 0;
     }
     return (PyObject *)iter;
}

static void
bsiter_dealloc(NyImmBitSetIterObject *v)
{
	Py_DECREF(v->immbitset);
	PyObject_DEL(v);
}

static PyObject *
bsiter_getiter(PyObject *it)
{
	Py_INCREF(it);
	return it;
}

static PyObject *
bsiter_iternext(NyImmBitSetIterObject *bi)
{
    NyImmBitSetObject *bs = bi->immbitset;
    NyBit fldpos = bi->fldpos;
    if (fldpos < bs->ob_size) {
	NyBit bitpos = bi->bitpos;
	NyBitField *f = &bs->ob_field[fldpos];
	NyBits bits = f->bits >> bitpos;
	long rebit;
	while (!(bits & 1)) {
	    bits >>= 1;
	    bitpos += 1;
	}
	rebit = f->pos * NyBits_N + bitpos;
	bits >>= 1;
	bitpos += 1;
	if (!bits) {
	    fldpos += 1;
	    bi->fldpos = fldpos;
	    bitpos = 0;
	}
	bi->bitpos = bitpos;
	return PyInt_FromLong(rebit);
    } else {
	return NULL;
    }
}

static int
cplbitset_hasbit(NyCplBitSetObject *v, NyBit bit)
{
    return !NyImmBitSet_hasbit(v->ob_val, bit);
}

static int
cplbitset_contains(NyCplBitSetObject *v, PyObject *w)
{
    NyBit bit = bitno_from_object(w);
    if (bit == -1 && PyErr_Occurred())
      return -1;
    return cplbitset_hasbit(v, bit);
}

static void
cplbitset_dealloc(NyCplBitSetObject *v)
{
    Py_DECREF(v->ob_val);
    v->ob_type->tp_free((PyObject *)v);
    n_cplbitset--;
}


PyObject *
cplbitset_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *arg = NULL;
    static char *kwlist[] = {"arg", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!:CplBitSet.__new__", kwlist,
				     &NyImmBitSet_Type, &arg))
      return NULL;
    return (PyObject *)NyCplBitSet_SubtypeNew(type, (NyImmBitSetObject *)arg);
}

static int
cplbitset_hash(NyCplBitSetObject *v)
{
    return ~immbitset_hash(v->ob_val);
}

static NyImmBitSetObject *
cplbitset_cpl(NyCplBitSetObject*v)
{
    return v->ob_val;
}

static PyObject *
cplbitset_complement(NyCplBitSetObject *v)
{
    Py_INCREF(v->ob_val);
    return (PyObject *)v->ob_val;
}

static PyObject *
cplbitset_int(NyCplBitSetObject *v)
{
    PyObject *w = immbitset_int(v->ob_val); // xxx
    PyObject *x;
    if (!w) return 0;
    x = PyNumber_Invert(w);
    Py_DECREF(w);
    return x;
    
}

static PyObject *
cplbitset_long(NyCplBitSetObject *v)
{
    PyObject *w = immbitset_long(v->ob_val);
    PyObject *x;
    if (!w) return 0;
    x = PyNumber_Invert(w);
    Py_DECREF(w);
    return x;
    
}

static int
cplbitset_nonzero(NyImmBitSetObject *v)
{
	return 1;
}


static PyObject *
cplbitset_repr(NyCplBitSetObject *a)
{
	char buf[256];
	PyObject *s, *t;
	PyOS_snprintf(buf, sizeof(buf), "(~");
	s = PyString_FromString(buf);
	t = PyObject_Repr((PyObject *)a->ob_val);
	if (!(s && t))
	    goto Fail;
	PyString_ConcatAndDel(&s, t);
	PyString_ConcatAndDel(&s, PyString_FromString(")"));
	return s;
      Fail:
	Py_XDECREF(s);
	Py_XDECREF(t);
	return 0;
}




static PyObject *
cplbitset_lshift(NyCplBitSetObject *v, long w)
{
    return (PyObject *)NyCplBitSet_New_Del(immbitset_lshift(cplbitset_cpl(v), w));
}

static PyObject *
cplbitset_and(NyCplBitSetObject *v, PyObject *w, int wt)
{
    switch (wt) {
      case BITSET:
	return (PyObject *)
	  immbitset_op((NyImmBitSetObject *)w,
		  NyBits_SUB,
		  cplbitset_cpl(v));

      case CPLSET:
	return cpl_immbitset_op(cplbitset_cpl(v),
			    NyBits_OR,
			    cplbitset_cpl((NyCplBitSetObject *)w));
      default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}

static PyObject *
cplbitset_or(NyCplBitSetObject *v, PyObject *w, int wt)
{
    switch (wt) {
      case BITSET:
	return cpl_immbitset_op(cplbitset_cpl(v),
			     NyBits_SUB,
			     (NyImmBitSetObject *)w);

      case CPLSET:
	return cpl_immbitset_op(cplbitset_cpl(v),
			     NyBits_AND,
			     cplbitset_cpl((NyCplBitSetObject *)w));
      default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}

static PyObject *
cplbitset_sub(NyCplBitSetObject *v, PyObject *w, int wt)
{
    switch (wt) {
      case BITSET:
	return cpl_immbitset_op(cplbitset_cpl(v),
			     NyBits_OR,
			     (NyImmBitSetObject *)w);

      case CPLSET:
	return (PyObject *)
	  immbitset_op(cplbitset_cpl((NyCplBitSetObject *)w),
		    NyBits_SUB,
		    cplbitset_cpl(v));
      default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}

static PyObject *
cplbitset_xor(NyCplBitSetObject *v, PyObject *w, int wt)
{
    switch (wt) {
      case BITSET:
	return cpl_immbitset_op(cplbitset_cpl(v),
			     NyBits_XOR,
			     (NyImmBitSetObject *)w);
      case CPLSET:
	return (PyObject *)
	  immbitset_op(cplbitset_cpl(v),
		  NyBits_XOR,
		  cplbitset_cpl((NyCplBitSetObject *)w));
      default:
	Py_INCREF(Py_NotImplemented);
	return Py_NotImplemented;
    }
}

void
anybitset_classify(PyObject *v, int *vt)
{
    if (NyImmBitSet_Check(v))
      *vt = BITSET;
    else if (NyCplBitSet_Check(v))
      *vt = CPLSET;
    else if (NyMutBitSet_Check(v))
      *vt = MUTSET;
    else
      *vt = NOSET;
}

static PyObject *
anybitset_convert(PyObject *v, int *vt)
{
    anybitset_classify(v, vt);
    if (*vt == BITSET || *vt == CPLSET) {
	Py_INCREF(v);
	return v;
    } else if (*vt == MUTSET)
      v = NyMutBitSet_AsImmBitSet((NyMutBitSetObject *)v);      
    else if (PyInt_Check(v))
      v = NyImmBitSet_FromPyIntObject(v);
    else if (PyLong_Check(v))
      v = NyImmBitSet_FromPyLongObject(v);
    else if (NyIterable_Check(v))
      v = (PyObject *)NyImmBitSet_FromIterable(v);
    else {
	Py_INCREF(v);
	return v;
    }
    if (v)
      anybitset_classify(v, vt);
    return v;
}

typedef PyObject *(*immbitset_op_t)(NyImmBitSetObject *, PyObject *, int);
typedef PyObject *(*cplbitset_op_t)(NyCplBitSetObject *, PyObject *, int);

static PyObject *
anybitset_op(PyObject *v, PyObject *w, immbitset_op_t immbitset_op, cplbitset_op_t cplbitset_op)
{
    PyObject *c;
    int vt, wt;
    v = anybitset_convert(v, &vt);
    if (!v)
      return NULL;
    w = anybitset_convert(w, &wt);
    if (!w) {
	Py_DECREF(v);
	return NULL;
    }
    if (vt == BITSET)
      c = immbitset_op((NyImmBitSetObject *)v, w, wt);
    else if (vt == CPLSET)
      c = cplbitset_op((NyCplBitSetObject *)v, w, wt);
    else if (wt == BITSET)
      c = immbitset_op((NyImmBitSetObject *)w, v, vt);
    else if (wt == CPLSET)
      c = cplbitset_op((NyCplBitSetObject *)w, v, vt);
    else {
	Py_INCREF(Py_NotImplemented);
	c = Py_NotImplemented;
    }
    Py_DECREF(v);
    Py_DECREF(w);
    return c;
}

static PyObject *
anybitset_and(PyObject *v, PyObject *w)
{
    return anybitset_op(v, w, immbitset_and, cplbitset_and);
}

static PyObject *
anybitset_or(PyObject *v, PyObject *w)
{
    return anybitset_op(v, w, immbitset_or, cplbitset_or);
}

static PyObject *
anybitset_sub(PyObject *v, PyObject *w)
{
    return anybitset_op(v, w, immbitset_sub, cplbitset_sub);
}

static PyObject *
anybitset_xor(PyObject *v, PyObject *w)
{
    return anybitset_op(v, w, immbitset_xor, cplbitset_xor);
}

static PyObject *
anybitset_lshift(PyObject *v, PyObject *w)
{
    int vt;
    long shiftby;
    PyObject *c;
    shiftby = bitno_from_object((PyObject *)w);
    if (shiftby == -1L && PyErr_Occurred())
      return 0;
    v = anybitset_convert(v, &vt);
    if (!v)
      return NULL;
    if (vt == BITSET)
      c = (PyObject *)immbitset_lshift((NyImmBitSetObject *)v, shiftby);
    else if (vt == CPLSET) {
	c = cplbitset_lshift((NyCplBitSetObject *)v, shiftby);
    }
    else {
	Py_INCREF(Py_NotImplemented);
	c = Py_NotImplemented;
    }	
    Py_DECREF(v);
    return c;
}

static PyNumberMethods immbitset_as_number = {
        (binaryfunc)	0,		/*nb_add*/
	(binaryfunc)	anybitset_sub,	/*nb_subtract*/
	(binaryfunc)	0,		/*nb_multiply*/
	(binaryfunc)	0,		/*nb_divide*/
	(binaryfunc)	0,		/*nb_remainder*/
	(binaryfunc)	0,		/*nb_divmod*/
	(ternaryfunc)	0,		/*nb_power*/
	(unaryfunc) 	0,		/*nb_negative*/
	(unaryfunc) 	0,		/*tp_positive*/
	(unaryfunc) 	0,		/*tp_absolute*/
	(inquiry)	immbitset_nonzero,	/*tp_nonzero*/
	(unaryfunc)	immbitset_complement,	/*nb_invert*/
	(binaryfunc)	anybitset_lshift,	/*nb_lshift*/
	(binaryfunc)	0,		/*nb_rshift*/
	(binaryfunc)	anybitset_and,	/*nb_and*/
	(binaryfunc)	anybitset_xor,	/*nb_xor*/
	(binaryfunc)	anybitset_or,	/*nb_or*/
	(coercion)	0,		/*nb_coerce*/
	(unaryfunc)	immbitset_int,	/*nb_int*/
	(unaryfunc)	immbitset_long,	/*nb_long*/
	(unaryfunc)	0,		/*nb_float*/
	(unaryfunc)	0,		/*nb_oct*/
	(unaryfunc)	0,		/*nb_hex*/
	0,				/* nb_inplace_add */
	0,				/* nb_inplace_subtract */
	0,				/* nb_inplace_multiply */
	0,				/* nb_inplace_divide */
	0,				/* nb_inplace_remainder */
	0,				/* nb_inplace_power */
	0,				/* nb_inplace_lshift */
	0,				/* nb_inplace_rshift */
	0,				/* nb_inplace_and */
	0,				/* nb_inplace_xor */
	0,				/* nb_inplace_or */
	0,				/* nb_floor_divide */
	0,				/* nb_true_divide */
	0,				/* nb_inplace_floor_divide */
	0,				/* nb_inplace_true_divide */
};

static NyMutBitSetObject *
immbitset_mutable_copy(PyObject *self, PyObject *args)
{
    return mutbitset_new_from_arg(self);
}

static PyObject *
immbitset_reduce_flags(NyImmBitSetObject *self, int flags)
{
    PyObject *a = PyTuple_New(2);
    PyObject *b = PyTuple_New(2);
    PyObject *c = PyInt_FromLong(flags);
    PyObject *d = PyString_FromStringAndSize((char *)self->ob_field,
					     self->ob_size * sizeof(self->ob_field[0]));
    if (!(a && b && c && d)) {
	Py_XDECREF(a);
	Py_XDECREF(b);
	Py_XDECREF(c);
	Py_XDECREF(d);
	return 0;
    }
    PyTuple_SET_ITEM(a, 0, NyBitSet_FormMethod);
    Py_INCREF(NyBitSet_FormMethod);
    PyTuple_SET_ITEM(a, 1, b);
    PyTuple_SET_ITEM(b, 0, c);
    PyTuple_SET_ITEM(b, 1, d);
    return a;
}

static PyObject *
immbitset_reduce(NyImmBitSetObject *self, PyObject *args)
{
    return immbitset_reduce_flags(self, 0);
}

static PyMethodDef immbitset_methods[] = {
	{"mutcopy", (PyCFunction)immbitset_mutable_copy, METH_NOARGS, mutable_copy_doc},
	{"__reduce__", (PyCFunction)immbitset_reduce, METH_NOARGS, "helper for pickle"},
	{NULL,		NULL}		/* sentinel */
};


static PySequenceMethods immbitset_as_sequence = {
	0,/* NOT USED - can be automatically called would be slow *//* sq_length */
	0,					/* sq_concat */
	0,					/* sq_repeat */
	0,					/* sq_item */
	0,					/* sq_slice */
	0,					/* sq_ass_item */
	0,					/* sq_ass_slice */
	(objobjproc)immbitset_contains,		/* sq_contains */
	0,					/* sq_inplace_concat */
	0,					/* sq_inplace_repeat */
};


static PyMappingMethods immbitset_as_mapping = {
	immbitset_length,	       /*mp_length*/
	(binaryfunc)immbitset_subscript, /*mp_subscript*/
	(objobjargproc)0,	      /*mp_ass_subscript*/
};


static PyObject *
immbitset_is_immutable(NyMutBitSetObject *v)
{
    Py_INCREF(Py_True);
    return (Py_True);
}

char immbitset_is_immutable_doc[] =
"S.is_immutable == True\n"
"\n"
"True since S is immutable.";

static PyGetSetDef immbitset_getsets[] = {
    {"is_immutable", (getter)immbitset_is_immutable, (setter)0, immbitset_is_immutable_doc},
    {NULL} /* Sentinel */
};

PyTypeObject NyImmBitSet_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.sets.setsc.ImmBitSet",		/* tp_name */
	sizeof(NyImmBitSetObject) - sizeof(NyBitField),
	  					/* tp_basicsize */
	sizeof(NyBitField),			/* tp_itemsize */
	(destructor)immbitset_dealloc,		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	(cmpfunc)0,				/* tp_compare */
	(reprfunc)immbitset_repr,			/* tp_repr */
	&immbitset_as_number,			/* tp_as_number */
	&immbitset_as_sequence,			/* tp_as_sequence */
	&immbitset_as_mapping,			/* tp_as_mapping */
	(hashfunc)immbitset_hash,			/* tp_hash */
        0,              			/* tp_call */
        (reprfunc)0,				/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES | Py_TPFLAGS_BASETYPE,
	  					/* tp_flags */
	ImmBitSet_doc,				/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	(richcmpfunc)immbitset_richcompare,	/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)immbitset_iter,		/* tp_iter */
	0,					/* tp_iternext */
	immbitset_methods,			/* tp_methods */
	0,					/* tp_members */
	immbitset_getsets,			/* tp_getset */
	&NyBitSet_Type,				/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	immbitset_new,				/* tp_new */
	PyObject_Del,				/* tp_free */
};

static PyNumberMethods cplbitset_as_number = {
        (binaryfunc)	0,		/*nb_add*/
	(binaryfunc)	anybitset_sub,	/*nb_subtract*/
	(binaryfunc)	0,		/*nb_multiply*/
	(binaryfunc)	0,		/*nb_divide*/
	(binaryfunc)	0,		/*nb_remainder*/
	(binaryfunc)	0,		/*nb_divmod*/
	(ternaryfunc)	0,		/*nb_power*/
	(unaryfunc) 	0,		/*nb_negative*/
	(unaryfunc) 	0,		/*tp_positive*/
	(unaryfunc) 	0,		/*tp_absolute*/
	(inquiry)	cplbitset_nonzero,	/*tp_nonzero*/
	(unaryfunc)	cplbitset_complement,	/*nb_invert*/
	(binaryfunc)	anybitset_lshift,/*nb_lshift*/
	(binaryfunc)	0,		/*nb_rshift*/
	(binaryfunc)	anybitset_and,	/*nb_and*/
	(binaryfunc)	anybitset_xor,	/*nb_xor*/
	(binaryfunc)	anybitset_or,	/*nb_or*/
	(coercion)	0,		/*nb_coerce*/
	(unaryfunc)	cplbitset_int,	/*nb_int*/
	(unaryfunc)	cplbitset_long,	/*nb_long*/
	(unaryfunc)	0,		/*nb_float*/
	(unaryfunc)	0,		/*nb_oct*/
	(unaryfunc)	0,		/*nb_hex*/
	0,				/* nb_inplace_add */
	0,				/* nb_inplace_subtract */
	0,				/* nb_inplace_multiply */
	0,				/* nb_inplace_divide */
	0,				/* nb_inplace_remainder */
	0,				/* nb_inplace_power */
	0,				/* nb_inplace_lshift */
	0,				/* nb_inplace_rshift */
	0,				/* nb_inplace_and */
	0,				/* nb_inplace_xor */
	0,				/* nb_inplace_or */
	0,				/* nb_floor_divide */
	0,				/* nb_true_divide */
	0,				/* nb_inplace_floor_divide */
	0,				/* nb_inplace_true_divide */
};

/* Implement "bit in cplbitset" */
static PySequenceMethods cplbitset_as_sequence = {
	0,					/* sq_length */
	0,					/* sq_concat */
	0,					/* sq_repeat */
	0,					/* sq_item */
	0,					/* sq_slice */
	0,					/* sq_ass_item */
	0,					/* sq_ass_slice */
	(objobjproc)cplbitset_contains,		/* sq_contains */
	0,					/* sq_inplace_concat */
	0,					/* sq_inplace_repeat */
};


static NyMutBitSetObject *
cplbitset_mutable_copy(PyObject *self)
{
    return mutbitset_new_from_arg(self);
}

static PyObject *
cplbitset_reduce(NyCplBitSetObject *self, PyObject *args)
{
    return immbitset_reduce_flags(cplbitset_cpl(self), NyForm_CPL);
}

static PyMethodDef cplbitset_methods[] = {
	{"mutcopy", (PyCFunction)cplbitset_mutable_copy, METH_NOARGS, mutable_copy_doc},
	{"__reduce__", (PyCFunction)cplbitset_reduce, METH_NOARGS, "helper for pickle"},
	{NULL,		NULL}		/* sentinel */
};


int
cplbitset_traverse(NyHeapTraverse *ta)
{
    return ta->visit((PyObject *)((NyCplBitSetObject *)ta->obj)->ob_val, ta->arg);
}


static PyGetSetDef cplbitset_getsets[] = {
    {"is_immutable", (getter)immbitset_is_immutable, (setter)0, immbitset_is_immutable_doc},
    {NULL} /* Sentinel */
};


PyTypeObject NyCplBitSet_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.sets.setsc.CplBitSet",		/* tp_name */
	sizeof(NyCplBitSetObject),
	  					/* tp_basicsize */
	0,					/* tp_itemsize */
	(destructor)cplbitset_dealloc,		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	(cmpfunc)0,				/* tp_compare */
	(reprfunc)cplbitset_repr,			/* tp_repr */
	&cplbitset_as_number,			/* tp_as_number */
	&cplbitset_as_sequence,			/* tp_as_sequence */
	0,					/* tp_as_mapping */
	(hashfunc)cplbitset_hash,			/* tp_hash */
        0,              			/* tp_call */
        (reprfunc)0,				/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES | Py_TPFLAGS_BASETYPE,
	  					/* tp_flags */
	cplbitset_doc,				/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	(richcmpfunc)cplbitset_richcompare,	/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	cplbitset_methods,			/* tp_methods */
	0,					/* tp_members */
	cplbitset_getsets,			/* tp_getset */
	&NyBitSet_Type,				/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	cplbitset_new,				/* tp_new */
	PyObject_Del,				/* tp_free */
};


static PyNumberMethods mutbitset_as_number = {
        (binaryfunc)	0,		/*nb_add*/
	(binaryfunc)	anybitset_sub,	/*nb_subtract*/
	(binaryfunc)	0,		/*nb_multiply*/
	(binaryfunc)	0,		/*nb_divide*/
	(binaryfunc)	0,		/*nb_remainder*/
	(binaryfunc)	0,		/*nb_divmod*/
	(ternaryfunc)	0,		/*nb_power*/
	(unaryfunc) 	0,		/*nb_negative*/
	(unaryfunc) 	0,		/*tp_positive*/
	(unaryfunc) 	0,		/*tp_absolute*/
	(inquiry)	mutbitset_nonzero,	/*tp_nonzero*/
	(unaryfunc)	mutbitset_complement,	/*nb_invert*/
	(binaryfunc)	anybitset_lshift,	/*nb_lshift*/
	(binaryfunc)	0,		/*nb_rshift*/
	(binaryfunc)	anybitset_and,	/*nb_and*/
	(binaryfunc)	anybitset_xor,	/*nb_xor*/
	(binaryfunc)	anybitset_or,	/*nb_or*/
	(coercion)	0,		/*nb_coerce*/
	(unaryfunc)	mutbitset_int,	/*nb_int*/
	(unaryfunc)	mutbitset_long,	/*nb_long*/
	(unaryfunc)	0,		/*nb_float*/
	(unaryfunc)	0,		/*nb_oct*/
	(unaryfunc)	0,		/*nb_hex*/
	0,				/* nb_inplace_add */
	(binaryfunc)mutbitset_isub,	/* nb_inplace_subtract */
	0,				/* nb_inplace_multiply */
	0,				/* nb_inplace_divide */
	0,				/* nb_inplace_remainder */
	0,				/* nb_inplace_power */
	0,				/* nb_inplace_lshift */
	0,				/* nb_inplace_rshift */
	(binaryfunc)mutbitset_iand,	/* nb_inplace_and */
	(binaryfunc)mutbitset_ixor,	/* nb_inplace_xor */
	(binaryfunc)mutbitset_ior,	/* nb_inplace_or */
	0,				/* nb_floor_divide */
	0,				/* nb_true_divide */
	0,				/* nb_inplace_floor_divide */
	0,				/* nb_inplace_true_divide */
};

/* Implement "bit in mutset" */
static PySequenceMethods mutbitset_as_sequence = {
	0,/* NOT USED - don't want auto-calling this */	/* sq_length */
	0,					/* sq_concat */
	0,					/* sq_repeat */
	0,					/* sq_item */
	0,					/* sq_slice */
	0,					/* sq_ass_item */
	0,					/* sq_ass_slice */
	(objobjproc)mutbitset_contains,		/* sq_contains */
	0,					/* sq_inplace_concat */
	0,					/* sq_inplace_repeat */
};

static PyObject *
mutbitset_reduce(NyMutBitSetObject *self, PyObject *args)
{
    NyImmBitSetObject *bs = mutbitset_as_noncomplemented_immbitset(self);
    PyObject *ret;
    if (!bs)
      return 0;
    ret = immbitset_reduce_flags(bs, NyForm_MUT | (self->cpl?NyForm_CPL : 0));
    Py_DECREF(bs);
    return ret;
}


static NyMutBitSetObject *
mutbitset_mutable_copy(PyObject *self)
{
    return mutbitset_new_from_arg(self);
}


static PyMethodDef mutbitset_methods[] = {
	{"__reduce__", (PyCFunction)mutbitset_reduce, METH_NOARGS, "helper for pickle"},
	{"add",		(PyCFunction)mutbitset_add, METH_O, add_doc},
	{"append", (PyCFunction)mutbitset_append, METH_O, append_doc},
	{"clear", (PyCFunction)_mutbitset_clear, METH_NOARGS, clear_doc},
	{"discard",	(PyCFunction)mutbitset_discard, METH_O, discard_doc},
	{"pop", (PyCFunction)mutbitset_pop, METH_VARARGS, pop_doc},
	{"remove", (PyCFunction)mutbitset_remove, METH_O, remove_doc},
	{"mutcopy", (PyCFunction)mutbitset_mutable_copy, METH_NOARGS,
	   mutable_copy_doc},
	{"tas", (PyCFunction)mutbitset_tasbit, METH_O, tasbit_doc},
	{"tac", (PyCFunction)mutbitset_tacbit, METH_O, tacbit_doc},
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
mutbitset_get_num_seg(NyMutBitSetObject *v)
{
    return PyInt_FromLong(v->root->cur_size);
}

int
generic_indisize(PyObject *v)
{
    long size = v->ob_type->tp_basicsize;
    if (v->ob_type->tp_itemsize)
      size += ((PyVarObject *)v)->ob_size * v->ob_type->tp_itemsize;
    return size;
}


static int
immbitset_indisize(NyImmBitSetObject *v)
{
    return generic_indisize((PyObject *)v);
}

static int
cplbitset_indisize(NyCplBitSetObject *v)
{
    return generic_indisize((PyObject *)v);
}

int
mutbitset_indisize(NyMutBitSetObject *v)
{
    long size = v->ob_type->tp_basicsize;
    int i;
    if (v->root != &v->fst_root)
      size += v->root->ob_type->tp_basicsize +
	v->root->ob_size * v->root->ob_type->tp_basicsize;
     for (i = 0; i < v->root->cur_size; i++) {
	 size += immbitset_indisize(v->root->ob_field[i].set);
     }
    return size;
}

int
anybitset_indisize(PyObject *obj)
{
    if (NyMutBitSet_Check(obj))
      return mutbitset_indisize((NyMutBitSetObject *)obj);
    else if (NyImmBitSet_Check(obj))
      return immbitset_indisize((NyImmBitSetObject *)obj);
    else if (NyCplBitSet_Check(obj))
      return cplbitset_indisize((NyCplBitSetObject *)obj);
    else {
	PyErr_SetString(PyExc_TypeError, "anybitset_indisize: some bitset expected");
	return -1;
    }
}

static PyObject *
anybitset_get_indisize(NyMutBitSetObject *v)
{
    return PyInt_FromLong(anybitset_indisize((PyObject *)v));
}

char mutbitset_is_immutable_doc[] =
"S.is_immutable == False\n"
"\n"
"False since S is not immmutable.";

static PyObject *
mutbitset_is_immutable(NyMutBitSetObject *v)
{
    Py_INCREF(Py_False);
    return (Py_False);
}

static PyGetSetDef mutbitset_getsets[] = {
    {"_num_seg", (getter)mutbitset_get_num_seg, (setter)0},
    {"_indisize", (getter)anybitset_get_indisize, (setter)0},
    {"is_immutable", (getter)mutbitset_is_immutable, (setter)0, mutbitset_is_immutable_doc},
    {NULL} /* Sentinel */
};

#define OFF(x) offsetof(NyMutBitSetObject, x)
static PyMemberDef mutbitset_members[] = {
    {"_splitting_size", T_INT, OFF(splitting_size)},
    {NULL} /* Sentinel */
};

static PyMappingMethods mutbitset_as_mapping = {
	mutbitset_length,	       /*mp_length*/
	(binaryfunc)mutbitset_subscript, /*mp_subscript*/
	(objobjargproc)0,	      /*mp_ass_subscript*/
};

PyTypeObject NyMutBitSet_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.sets.setsc.MutBitSet",		/* tp_name */
	sizeof(NyMutBitSetObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	(destructor)mutbitset_dealloc,		/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	(cmpfunc)0,				/* tp_compare */
	(reprfunc)mutbitset_repr,			/* tp_repr */
	&mutbitset_as_number,			/* tp_as_number */
	&mutbitset_as_sequence,			/* tp_as_sequence */
	&mutbitset_as_mapping,			/* tp_as_mapping */
	(hashfunc)0,				/* tp_hash */
        0,              			/* tp_call */
        (reprfunc)0,				/* tp_str */
	PyObject_GenericGetAttr,		/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES | Py_TPFLAGS_BASETYPE,
	  					/* tp_flags */
	mutbitset_doc,				/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	(richcmpfunc)mutbitset_richcompare,	/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	(getiterfunc)mutbitset_iter,		/* tp_iter */
	0,					/* tp_iternext */
	mutbitset_methods,			/* tp_methods */
	mutbitset_members,			/* tp_members */
	mutbitset_getsets,			/* tp_getset */
	&NyBitSet_Type,				/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	PyType_GenericAlloc,			/* tp_alloc */
	mutbitset_new,				/* tp_new */
	_PyObject_Del,				/* tp_free */
};


PyTypeObject NyImmBitSetIter_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"immbitset-iterator",			/* tp_name */
	sizeof(NyImmBitSetIterObject),		/* tp_basicsize */
	0,					/* tp_itemsize */
	/* methods */
	(destructor)bsiter_dealloc, 		/* tp_dealloc */
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
	(getiterfunc)bsiter_getiter,		/* tp_iter */
	(iternextfunc)bsiter_iternext,		/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
};

PyTypeObject NyUnion_Type = {
	PyObject_HEAD_INIT(NULL)
	0,					/* ob_size */
	"guppy.sets.setsc.Union",		/* tp_name */
	sizeof(NyUnionObject) - NyUnion_MINSIZE*sizeof(NySetField),
	  					/* tp_basicsize */
	sizeof(NySetField),			/* tp_itemsize */
	/* methods */
	(destructor)union_dealloc, 		/* tp_dealloc */
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
	(getiterfunc)0,				/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
};


static PyObject *
_NyImmBitSet_Singleton(PyObject *unused, PyObject *arg)
{
    return (PyObject *)NyImmBitSet_Singleton(arg);
}

/* Quoting Python/bltinmodule.c */

/* Return number of items in range/xrange (lo, hi, step).  step > 0
 * required.  Return a value < 0 if & only if the true value is too
 * large to fit in a signed long.
 */

static long
get_len_of_range(long lo, long hi, long step)
{
	/* -------------------------------------------------------------
	If lo >= hi, the range is empty.
	Else if n values are in the range, the last one is
	lo + (n-1)*step, which must be <= hi-1.  Rearranging,
	n <= (hi - lo - 1)/step + 1, so taking the floor of the RHS gives
	the proper value.  Since lo < hi in this case, hi-lo-1 >= 0, so
	the RHS is non-negative and so truncation is the same as the
	floor.  Letting M be the largest positive long, the worst case
	for the RHS numerator is hi=M, lo=-M-1, and then
	hi-lo-1 = M-(-M-1)-1 = 2*M.  Therefore unsigned long has enough
	precision to compute the RHS exactly.
	---------------------------------------------------------------*/
	long n = 0;
	if (lo < hi) {
		unsigned long uhi = (unsigned long)hi;
		unsigned long ulo = (unsigned long)lo;
		unsigned long diff = uhi - ulo - 1;
		n = (long)(diff / (unsigned long)step + 1);
	}
	return n;
}

static PyObject *
NyImmBitSet_Range(long lo, long hi, long step)
{
    NyBitField fst, *f, *fhi, fs[NyBits_N];
    NyImmBitSetObject *v;

    NyBit bitno, bitno_per_block, hipos, hibit, bit, pos, fstbit;
    NyBit size, posadd, pos_per_block, d, lim, bign, bp;
    NyBit bitnos[NyBits_N+1];

    NyBit blocksize, i, j, nf, nblocks, n, extra;

    if (step <= 0) {
	PyErr_SetString(PyExc_ValueError, "bitrange() arg 3 must be positive");
	return NULL;
    }
    bign = get_len_of_range(lo, hi, step);
    n = (int)bign;
    if (bign < 0 || (long)n != bign) {
	PyErr_SetString(PyExc_OverflowError,
			"bitrange() result has too many items");
	return NULL;
    }

    if (n == 0) {
	Py_INCREF(NyImmBitSet_Empty);
	return (PyObject *)NyImmBitSet_Empty;
    }

    bitno = lo;
    bit = bitno_modiv(bitno, &pos);
    hibit = bitno_modiv(hi, &hipos);
    
    bp = 0;
    fst.pos = pos;
    fst.bits = 1l<<bit;
    bp++;
    if (step < NyBits_N) { /* has to check, add step may overflow */
	bit += step;
	lim = pos == hipos ? hibit : NyBits_N;
	while (bit < lim) {
	    fst.bits |= 1l<<bit;
	    bit += step;
	    bp++;
	}
    }
    i = 0;
    if (bp < n) {
	bitno = lo + bp * step;
	fstbit = bitno_modiv(bitno, &pos);
	bit = fstbit;
	do {
	    bitnos[i] = bitno;
	    fs[i].bits = 1l<<bit;
	    fs[i].pos = pos;
	    bp++;
	    if (step < NyBits_N) { /* has to check, add step may overflow */
		bit += step;
		lim = pos == hipos ? hibit : NyBits_N;
		while (bit < lim) {
		    fs[i].bits |= 1l<<bit;
		    bp++;
		    bit += step;
		}
	    }
	    bitno = lo + bp * step;
	    bit = bitno_modiv(bitno, &pos);
	    i++;
	} while (! (bp >= n || bit == fstbit ));
    }
    if (bp >= n) {
	assert(bp == n);
	nblocks = 0;
	nf = i;
	size = 1 + nf;
	pos_per_block = 0;	/* avoid spurious undefined-warning */
	blocksize = 0;		/* avoid spurious undefined-warning */
	extra = 0;
    } else {
	bitnos[i] = bitno;
	blocksize = i;
	bitno_per_block = bitno - bitnos[0];
	pos_per_block = (pos - fs[0].pos);
	nblocks = (hipos - fs[0].pos) / pos_per_block - 1;
	if (nblocks < 1)
	  nblocks = 1;
	bitno = bitnos[0] + nblocks * bitno_per_block;
	while (bitno <= hi - bitno_per_block) {
	    nblocks++;
	    bitno += bitno_per_block;
	}
	i = 0;
	while (bitno <= hi - (d = bitnos[i+1] - bitnos[i])) {
	    i++;
	    bitno += d;
	}
	assert (i < blocksize);
	nf = i;
	
	extra = bitno < hi;
	size = 1 + nblocks * blocksize + nf + extra;
    }

    v = NyImmBitSet_New(size);
    if (!v) return 0;
    f = v->ob_field;
    fhi = v->ob_field + v->ob_size;
    assert (f < fhi);
    f->pos = fst.pos;
    f->bits = fst.bits;
    f++;
    for (i = 0, posadd = 0; i < nblocks; i++, posadd += pos_per_block) {
	for (j = 0; j < blocksize; j++, f++) {
	    assert (f < fhi);
	    f->pos = fs[j].pos + posadd;
	    f->bits = fs[j].bits;
	}
    }
    for (i = 0; i < nf; i++, f++) {
	assert (f < fhi);
	f->pos = fs[i].pos + posadd;
	f->bits = fs[i].bits;
    }
    if (extra) {
	assert (f < fhi);
	bit = bitno_modiv(bitno, &f->pos);
	f->bits = 1l<<bit;
	if (step < NyBits_N) /* has to check, add may overflow */ {
	    bit += step;
	    lim = f->pos == hipos ? hibit : NyBits_N;
	    while (bit < lim) {
		f->bits |= 1l<<bit;
		bit += step;
	    }
	}
	f++;
    }

    assert (f == fhi);
    return (PyObject *)v;
}

static PyObject *
_NyImmBitSet_Range(PyObject *unused, PyObject *args)
{
        /* Borrows from builtin_range()	in Python/bltinmodule.c*/
	long ilow = 0, ihigh = 0, istep = 1;

	if (PyTuple_Size(args) <= 1) {
		if (!PyArg_ParseTuple(args,
				"l;bitrange() requires 1-3 int arguments",
				&ihigh))
			return NULL;
	}
	else {
		if (!PyArg_ParseTuple(args,
				"ll|l;bitrange() requires 1-3 int arguments",
				&ilow, &ihigh, &istep))
			return NULL;
	}
	return NyImmBitSet_Range(ilow, ihigh, istep);
}

static PyObject *
NyBitSet_Form(PyObject *args)
{
    PyObject *str;
    NyImmBitSetObject *bs;
    char *s;
    Py_ssize_t len,sz;
    int flags;
    if (!(args && PyTuple_Check(args)) && PyTuple_GET_SIZE(args) == 2) {
	PyErr_SetString(PyExc_TypeError, "NyBitSet_Form() requires exactly 2 arguments");
	return 0;
    }
    if (!PyInt_Check(PyTuple_GET_ITEM(args, 0))) {
	PyErr_SetString(PyExc_TypeError, "NyBitSet_Form(): 1st arg must be an int");
	return 0;
    }
    flags = PyInt_AsLong(PyTuple_GET_ITEM(args, 0));
    str = PyTuple_GET_ITEM(args, 1);
    if (!PyString_Check(str)) {
	PyErr_SetString(PyExc_TypeError, "NyBitSet_Form(): 2nd arg must be a string");
	return 0;
    }
    if (PyString_AsStringAndSize(str, &s, &len) == -1)
      return 0;
    sz = len / sizeof(NyBitField);
    bs = NyImmBitSet_New(sz);
    if (!bs)
      return 0;
    fp_move(bs->ob_field, (NyBitField *)s, sz);
    if (flags & NyForm_MUT) {
	NyMutBitSetObject *ms = mutbitset_new_from_arg((PyObject *)bs);
	Py_DECREF(bs);
	if (!ms) {
	    return 0;
	}
	if (flags & NyForm_CPL)
	  mutbitset_iop_complement(ms);
	return (PyObject *)ms;
    }
    if (flags & NyForm_CPL) {
	NyCplBitSetObject * cpl = NyCplBitSet_New(bs);
	Py_DECREF(bs);
	return (PyObject *)cpl;
    }
    return (PyObject *)bs;
}

static PyObject *
_NyBitSet_Form(PyObject *unused, PyObject *args)
{
    return NyBitSet_Form(args);
}

static PyMethodDef nybitset_methods[] =
{
    {"immbit",(PyCFunction)_NyImmBitSet_Singleton, METH_O, bitsingle_doc},
    {"immbitrange",(PyCFunction)_NyImmBitSet_Range, METH_VARARGS, bitrange_doc},
    {"immbitset",(PyCFunction)immbitset, METH_KEYWORDS, immbitset_doc},
    {"_bs",(PyCFunction)_NyBitSet_Form, METH_VARARGS, bitform_doc},
    {0}
};

static NyBitSet_Exports nybitset_exports = {
    0,
    sizeof(NyBitSet_Exports),
    "NyBitSet_Exports v1.0",
    NyMutBitSet_New,
    NyMutBitSet_setbit,
    NyMutBitSet_clrbit,
    mutbitset_set_or_clr,
    NyMutBitSet_AsImmBitSet,
    NyAnyBitSet_iterate,
    NyMutBitSet_hasbit,
    NyImmBitSet_hasbit,
    cplbitset_hasbit,
};


int fsb_dx_nybitset_init(PyObject *m)
{
    PyObject *d;

    _NyImmBitSet_EmptyStruct.ob_type = &NyImmBitSet_Type;
    _NyImmBitSet_OmegaStruct.ob_type = &NyCplBitSet_Type;

    NYFILL(NyBitSet_Type);
    NYFILL(NyImmBitSet_Type);
    NYFILL(NyCplBitSet_Type);
    NYFILL(NyMutBitSet_Type);
    NYFILL(NyImmBitSetIter_Type);
    NYFILL(NyUnion_Type);

    d = PyModule_GetDict(m);
    PyDict_SetItemString(d, "BitSet", (PyObject *)&NyBitSet_Type);
    PyDict_SetItemString(d, "CplBitSet", (PyObject *)&NyCplBitSet_Type);
    PyDict_SetItemString(d, "ImmBitSet", (PyObject *)&NyImmBitSet_Type);
    PyDict_SetItemString(d, "MutBitSet", (PyObject *)&NyMutBitSet_Type);
    PyDict_SetItemString(d,
			 "NyBitSet_Exports",
			 PyCObject_FromVoidPtrAndDesc(
						      &nybitset_exports,
						      "NybitSet_Exports v1.0",
						      0)
			 );

    if (fsb_dx_addmethods(m, nybitset_methods, 0) == -1)
      goto error;
    NyBitSet_FormMethod = PyObject_GetAttrString(m, "_bs");
    if (!NyBitSet_FormMethod)
      goto error;
    { int i;
      /* initialize len() helper */
      for (i = 0; i < LEN_TAB_SIZE; i++) {
	  unsigned b = i;
	  int n = 0;
	  while (b) {
	      if (b & 1)
		n++;
	      b >>= 1;
	  }
	  len_tab[i] = n;
      }
    }

    return 0;
  error:
    return -1;

}

