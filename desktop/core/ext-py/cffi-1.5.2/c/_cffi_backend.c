#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "structmember.h"

#define CFFI_VERSION  "1.5.2"

#ifdef MS_WIN32
#include <windows.h>
#include "misc_win32.h"
#else
#include <stddef.h>
#include <stdint.h>
#include <dlfcn.h>
#include <errno.h>
#include <ffi.h>
#include <sys/mman.h>
#endif

/* this block of #ifs should be kept exactly identical between
   c/_cffi_backend.c, cffi/vengine_cpy.py, cffi/vengine_gen.py */
#if defined(_MSC_VER)
# include <malloc.h>   /* for alloca() */
# if _MSC_VER < 1600   /* MSVC < 2010 */
   typedef __int8 int8_t;
   typedef __int16 int16_t;
   typedef __int32 int32_t;
   typedef __int64 int64_t;
   typedef unsigned __int8 uint8_t;
   typedef unsigned __int16 uint16_t;
   typedef unsigned __int32 uint32_t;
   typedef unsigned __int64 uint64_t;
   typedef __int8 int_least8_t;
   typedef __int16 int_least16_t;
   typedef __int32 int_least32_t;
   typedef __int64 int_least64_t;
   typedef unsigned __int8 uint_least8_t;
   typedef unsigned __int16 uint_least16_t;
   typedef unsigned __int32 uint_least32_t;
   typedef unsigned __int64 uint_least64_t;
   typedef __int8 int_fast8_t;
   typedef __int16 int_fast16_t;
   typedef __int32 int_fast32_t;
   typedef __int64 int_fast64_t;
   typedef unsigned __int8 uint_fast8_t;
   typedef unsigned __int16 uint_fast16_t;
   typedef unsigned __int32 uint_fast32_t;
   typedef unsigned __int64 uint_fast64_t;
   typedef __int64 intmax_t;
   typedef unsigned __int64 uintmax_t;
# else
#  include <stdint.h>
# endif
# if _MSC_VER < 1800   /* MSVC < 2013 */
   typedef unsigned char _Bool;
# endif
#else
# include <stdint.h>
# if (defined (__SVR4) && defined (__sun)) || defined(_AIX) || defined(__hpux)
#  include <alloca.h>
# endif
#endif

#include "malloc_closure.h"

#if PY_MAJOR_VERSION >= 3
# define STR_OR_BYTES "bytes"
# define PyText_Type PyUnicode_Type
# define PyText_Check PyUnicode_Check
# define PyTextAny_Check PyUnicode_Check
# define PyText_FromFormat PyUnicode_FromFormat
# define PyText_AsUTF8 _PyUnicode_AsString   /* PyUnicode_AsUTF8 in Py3.3 */
# define PyText_AS_UTF8 _PyUnicode_AsString
# define PyText_GetSize PyUnicode_GetSize
# define PyText_FromString PyUnicode_FromString
# define PyText_FromStringAndSize PyUnicode_FromStringAndSize
# define PyText_InternInPlace PyUnicode_InternInPlace
# define PyText_InternFromString PyUnicode_InternFromString
# define PyIntOrLong_Check PyLong_Check
#else
# define STR_OR_BYTES "str"
# define PyText_Type PyString_Type
# define PyText_Check PyString_Check
# define PyTextAny_Check(op) (PyString_Check(op) || PyUnicode_Check(op))
# define PyText_FromFormat PyString_FromFormat
# define PyText_AsUTF8 PyString_AsString
# define PyText_AS_UTF8 PyString_AS_STRING
# define PyText_GetSize PyString_Size
# define PyText_FromString PyString_FromString
# define PyText_FromStringAndSize PyString_FromStringAndSize
# define PyText_InternInPlace PyString_InternInPlace
# define PyText_InternFromString PyString_InternFromString
# define PyIntOrLong_Check(op) (PyInt_Check(op) || PyLong_Check(op))
#endif

#if PY_MAJOR_VERSION >= 3
# define PyInt_FromLong PyLong_FromLong
# define PyInt_FromSsize_t PyLong_FromSsize_t
# define PyInt_AsSsize_t PyLong_AsSsize_t
# define PyInt_AsLong PyLong_AsLong
#endif

#if PY_MAJOR_VERSION >= 3
/* This is the default on Python3 and constant has been removed. */
# define Py_TPFLAGS_CHECKTYPES 0
#endif

#if PY_MAJOR_VERSION < 3
# undef PyCapsule_GetPointer
# undef PyCapsule_New
# define PyCapsule_GetPointer(capsule, name) \
    (PyCObject_AsVoidPtr(capsule))
# define PyCapsule_New(pointer, name, destructor) \
    (PyCObject_FromVoidPtr(pointer, destructor))
#endif

/************************************************************/

/* base type flag: exactly one of the following: */
#define CT_PRIMITIVE_SIGNED   1    /* signed integer */
#define CT_PRIMITIVE_UNSIGNED 2    /* unsigned integer */
#define CT_PRIMITIVE_CHAR     4    /* char, wchar_t */
#define CT_PRIMITIVE_FLOAT    8    /* float, double, long double */
#define CT_POINTER           16    /* pointer, excluding ptr-to-func */
#define CT_ARRAY             32    /* array */
#define CT_STRUCT            64    /* struct */
#define CT_UNION            128    /* union */
#define CT_FUNCTIONPTR      256    /* pointer to function */
#define CT_VOID             512    /* void */

/* other flags that may also be set in addition to the base flag: */
#define CT_CAST_ANYTHING         1024    /* 'char *' and 'void *' only */
#define CT_PRIMITIVE_FITS_LONG   2048
#define CT_IS_OPAQUE             4096
#define CT_IS_ENUM               8192
#define CT_IS_PTR_TO_OWNED      16384
#define CT_CUSTOM_FIELD_POS     32768
#define CT_IS_LONGDOUBLE        65536
#define CT_IS_BOOL             131072
#define CT_IS_FILE             262144
#define CT_IS_VOID_PTR         524288
#define CT_WITH_VAR_ARRAY     1048576
#define CT_IS_UNSIZED_CHAR_A  2097152
#define CT_LAZY_FIELD_LIST    4194304
#define CT_PRIMITIVE_ANY  (CT_PRIMITIVE_SIGNED |        \
                           CT_PRIMITIVE_UNSIGNED |      \
                           CT_PRIMITIVE_CHAR |          \
                           CT_PRIMITIVE_FLOAT)

typedef struct _ctypedescr {
    PyObject_VAR_HEAD

    struct _ctypedescr *ct_itemdescr;  /* ptrs and arrays: the item type */
    PyObject *ct_stuff;                /* structs: dict of the fields
                                          arrays: ctypedescr of the ptr type
                                          function: tuple(abi, ctres, ctargs..)
                                          enum: pair {"name":x},{x:"name"}
                                          ptrs: lazily, ctypedescr of array */
    void *ct_extra;                    /* structs: first field (not a ref!)
                                          function types: cif_description
                                          primitives: prebuilt "cif" object */

    PyObject *ct_weakreflist;    /* weakref support */

    PyObject *ct_unique_key;    /* key in unique_cache (a string, but not
                                   human-readable) */

    Py_ssize_t ct_size;     /* size of instances, or -1 if unknown */
    Py_ssize_t ct_length;   /* length of arrays, or -1 if unknown;
                               or alignment of primitive and struct types;
                               always -1 for pointers */
    int ct_flags;           /* CT_xxx flags */

    int ct_name_position;   /* index in ct_name of where to put a var name */
    char ct_name[1];        /* string, e.g. "int *" for pointers to ints */
} CTypeDescrObject;

typedef struct {
    PyObject_HEAD
    CTypeDescrObject *c_type;
    char *c_data;
    PyObject *c_weakreflist;
} CDataObject;

typedef struct cfieldobject_s {
    PyObject_HEAD
    CTypeDescrObject *cf_type;
    Py_ssize_t cf_offset;
    short cf_bitshift;   /* >= 0: bitshift; or BS_REGULAR or BS_EMPTY_ARRAY */
    short cf_bitsize;
    struct cfieldobject_s *cf_next;
} CFieldObject;
#define BS_REGULAR     (-1)      /* a regular field, not with bitshift */
#define BS_EMPTY_ARRAY (-2)      /* a field which is an array 'type[0]' */

static PyTypeObject CTypeDescr_Type;
static PyTypeObject CField_Type;
static PyTypeObject CData_Type;
static PyTypeObject CDataOwning_Type;
static PyTypeObject CDataOwningGC_Type;
static PyTypeObject CDataGCP_Type;

#define CTypeDescr_Check(ob)  (Py_TYPE(ob) == &CTypeDescr_Type)
#define CData_Check(ob)       (Py_TYPE(ob) == &CData_Type ||            \
                               Py_TYPE(ob) == &CDataOwning_Type ||      \
                               Py_TYPE(ob) == &CDataOwningGC_Type ||    \
                               Py_TYPE(ob) == &CDataGCP_Type)
#define CDataOwn_Check(ob)    (Py_TYPE(ob) == &CDataOwning_Type ||      \
                               Py_TYPE(ob) == &CDataOwningGC_Type)

typedef union {
    unsigned char m_char;
    unsigned short m_short;
    unsigned int m_int;
    unsigned long m_long;
    unsigned long long m_longlong;
    float m_float;
    double m_double;
    long double m_longdouble;
} union_alignment;

typedef struct {
    CDataObject head;
    union_alignment alignment;
} CDataObject_casted_primitive;

typedef struct {
    CDataObject head;
    union_alignment alignment;
} CDataObject_own_nolength;

typedef struct {
    CDataObject head;
    Py_ssize_t length;
    union_alignment alignment;
} CDataObject_own_length;

typedef struct {
    CDataObject head;
    PyObject *structobj;
} CDataObject_own_structptr;

typedef struct {
    CDataObject head;
    Py_ssize_t length;     /* same as CDataObject_own_length up to here */
    Py_buffer *bufferview;
} CDataObject_owngc_frombuf;

typedef struct {
    CDataObject head;
    Py_ssize_t length;     /* same as CDataObject_own_length up to here */
    PyObject *origobj;
    PyObject *destructor;
} CDataObject_gcp;

typedef struct {
    ffi_cif cif;
    /* the following information is used when doing the call:
       - a buffer of size 'exchange_size' is malloced
       - the arguments are converted from Python objects to raw data
       - the i'th raw data is stored at 'buffer + exchange_offset_arg[1+i]'
       - the call is done
       - the result is read back from 'buffer + exchange_offset_arg[0]' */
    Py_ssize_t exchange_size;
    Py_ssize_t exchange_offset_arg[1];
} cif_description_t;


/* whenever running Python code, the errno is saved in this thread-local
   variable */
#ifndef MS_WIN32
# include "misc_thread_posix.h"
#endif

#include "minibuffer.h"

#if PY_MAJOR_VERSION >= 3
# include "file_emulator.h"
#endif

#ifdef HAVE_WCHAR_H
# include "wchar_helper.h"
#endif

typedef struct _cffi_allocator_s {
    PyObject *ca_alloc, *ca_free;
    int ca_dont_clear;
} cffi_allocator_t;
static const cffi_allocator_t default_allocator = { NULL, NULL, 0 };
static PyObject *FFIError;
static PyObject *unique_cache;

/************************************************************/

static CTypeDescrObject *
ctypedescr_new(int name_size)
{
    CTypeDescrObject *ct = PyObject_GC_NewVar(CTypeDescrObject,
                                              &CTypeDescr_Type,
                                              name_size);
    if (ct == NULL)
        return NULL;

    ct->ct_itemdescr = NULL;
    ct->ct_stuff = NULL;
    ct->ct_weakreflist = NULL;
    ct->ct_unique_key = NULL;
    PyObject_GC_Track(ct);
    return ct;
}

static CTypeDescrObject *
ctypedescr_new_on_top(CTypeDescrObject *ct_base, const char *extra_text,
                      int extra_position)
{
    int base_name_len = strlen(ct_base->ct_name);
    int extra_name_len = strlen(extra_text);
    CTypeDescrObject *ct = ctypedescr_new(base_name_len + extra_name_len + 1);
    char *p;
    if (ct == NULL)
        return NULL;

    Py_INCREF(ct_base);
    ct->ct_itemdescr = ct_base;
    ct->ct_name_position = ct_base->ct_name_position + extra_position;

    p = ct->ct_name;
    memcpy(p, ct_base->ct_name, ct_base->ct_name_position);
    p += ct_base->ct_name_position;
    memcpy(p, extra_text, extra_name_len);
    p += extra_name_len;
    memcpy(p, ct_base->ct_name + ct_base->ct_name_position,
           base_name_len - ct_base->ct_name_position + 1);

    return ct;
}

static PyObject *
ctypedescr_repr(CTypeDescrObject *ct)
{
    return PyText_FromFormat("<ctype '%s'>", ct->ct_name);
}

static void
ctypedescr_dealloc(CTypeDescrObject *ct)
{
    PyObject_GC_UnTrack(ct);
    if (ct->ct_weakreflist != NULL)
        PyObject_ClearWeakRefs((PyObject *) ct);

    if (ct->ct_unique_key != NULL) {
        /* revive dead object temporarily for DelItem */
        Py_REFCNT(ct) = 43;
        PyDict_DelItem(unique_cache, ct->ct_unique_key);
        assert(Py_REFCNT(ct) == 42);
        Py_REFCNT(ct) = 0;
        Py_DECREF(ct->ct_unique_key);
    }
    Py_XDECREF(ct->ct_itemdescr);
    Py_XDECREF(ct->ct_stuff);
    if (ct->ct_flags & CT_FUNCTIONPTR)
        PyObject_Free(ct->ct_extra);
    Py_TYPE(ct)->tp_free((PyObject *)ct);
}

static int
ctypedescr_traverse(CTypeDescrObject *ct, visitproc visit, void *arg)
{
    Py_VISIT(ct->ct_itemdescr);
    Py_VISIT(ct->ct_stuff);
    return 0;
}

static int
ctypedescr_clear(CTypeDescrObject *ct)
{
    Py_CLEAR(ct->ct_itemdescr);
    Py_CLEAR(ct->ct_stuff);
    return 0;
}


static PyObject *nosuchattr(const char *attr)
{
    PyErr_SetString(PyExc_AttributeError, attr);
    return NULL;
}

static PyObject *ctypeget_kind(CTypeDescrObject *ct, void *context)
{
    char *result;
    if (ct->ct_flags & CT_PRIMITIVE_ANY) {
        if (ct->ct_flags & CT_IS_ENUM)
            result = "enum";
        else
            result = "primitive";
    }
    else if (ct->ct_flags & CT_POINTER) {
        result = "pointer";
    }
    else if (ct->ct_flags & CT_ARRAY) {
        result = "array";
    }
    else if (ct->ct_flags & CT_VOID) {
        result = "void";
    }
    else if (ct->ct_flags & CT_STRUCT) {
        result = "struct";
    }
    else if (ct->ct_flags & CT_UNION) {
        result = "union";
    }
    else if (ct->ct_flags & CT_FUNCTIONPTR) {
        result = "function";
    }
    else
        result = "?";

    return PyText_FromString(result);
}

static PyObject *ctypeget_cname(CTypeDescrObject *ct, void *context)
{
    return PyText_FromString(ct->ct_name);
}

static PyObject *ctypeget_item(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & (CT_POINTER | CT_ARRAY)) {
        Py_INCREF(ct->ct_itemdescr);
        return (PyObject *)ct->ct_itemdescr;
    }
    return nosuchattr("item");
}

static PyObject *ctypeget_length(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & CT_ARRAY) {
        if (ct->ct_length >= 0) {
            return PyInt_FromSsize_t(ct->ct_length);
        }
        else {
            Py_INCREF(Py_None);
            return Py_None;
        }
    }
    return nosuchattr("length");
}

static PyObject *
get_field_name(CTypeDescrObject *ct, CFieldObject *cf);   /* forward */

#define force_lazy_struct(ct)                                           \
    ((ct)->ct_stuff != NULL ? 1 : do_realize_lazy_struct(ct))

static int do_realize_lazy_struct(CTypeDescrObject *ct);
/* forward, implemented in realize_c_type.c */

static PyObject *ctypeget_fields(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & (CT_STRUCT | CT_UNION)) {
        if (!(ct->ct_flags & CT_IS_OPAQUE)) {
            CFieldObject *cf;
            PyObject *res;
            if (force_lazy_struct(ct) < 0)
                return NULL;
            res = PyList_New(0);
            if (res == NULL)
                return NULL;
            for (cf = (CFieldObject *)ct->ct_extra;
                 cf != NULL; cf = cf->cf_next) {
                PyObject *o = PyTuple_Pack(2, get_field_name(ct, cf),
                                           (PyObject *)cf);
                int err = (o != NULL) ? PyList_Append(res, o) : -1;
                Py_XDECREF(o);
                if (err < 0) {
                    Py_DECREF(res);
                    return NULL;
                }
            }
            return res;
        }
        else {
            Py_INCREF(Py_None);
            return Py_None;
        }
    }
    return nosuchattr("fields");
}

static PyObject *ctypeget_args(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & CT_FUNCTIONPTR) {
        PyObject *t = ct->ct_stuff;
        return PyTuple_GetSlice(t, 2, PyTuple_GET_SIZE(t));
    }
    return nosuchattr("args");
}

static PyObject *ctypeget_result(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & CT_FUNCTIONPTR) {
        PyObject *res = PyTuple_GetItem(ct->ct_stuff, 1);
        Py_XINCREF(res);
        return res;
    }
    return nosuchattr("result");
}

static PyObject *ctypeget_ellipsis(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & CT_FUNCTIONPTR) {
        PyObject *res = ct->ct_extra ? Py_False : Py_True;
        Py_INCREF(res);
        return res;
    }
    return nosuchattr("ellipsis");
}

static PyObject *ctypeget_abi(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & CT_FUNCTIONPTR) {
        PyObject *res = PyTuple_GetItem(ct->ct_stuff, 0);
        Py_XINCREF(res);
        return res;
    }
    return nosuchattr("abi");
}

static PyObject *ctypeget_elements(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & CT_IS_ENUM) {
        PyObject *res = PyTuple_GetItem(ct->ct_stuff, 1);
        if (res) res = PyDict_Copy(res);
        return res;
    }
    return nosuchattr("elements");
}

static PyObject *ctypeget_relements(CTypeDescrObject *ct, void *context)
{
    if (ct->ct_flags & CT_IS_ENUM) {
        PyObject *res = PyTuple_GetItem(ct->ct_stuff, 0);
        if (res) res = PyDict_Copy(res);
        return res;
    }
    return nosuchattr("relements");
}

static PyGetSetDef ctypedescr_getsets[] = {
    {"kind", (getter)ctypeget_kind, NULL, "kind"},
    {"cname", (getter)ctypeget_cname, NULL, "C name"},
    {"item", (getter)ctypeget_item, NULL, "pointer to, or array of"},
    {"length", (getter)ctypeget_length, NULL, "array length or None"},
    {"fields", (getter)ctypeget_fields, NULL, "struct or union fields"},
    {"args", (getter)ctypeget_args, NULL, "function argument types"},
    {"result", (getter)ctypeget_result, NULL, "function result type"},
    {"ellipsis", (getter)ctypeget_ellipsis, NULL, "function has '...'"},
    {"abi", (getter)ctypeget_abi, NULL, "function ABI"},
    {"elements", (getter)ctypeget_elements, NULL, "enum elements"},
    {"relements", (getter)ctypeget_relements, NULL, "enum elements, reverse"},
    {NULL}                        /* sentinel */
};

static PyObject *
ctypedescr_dir(PyObject *ct, PyObject *noarg)
{
    int err;
    struct PyGetSetDef *gsdef;
    PyObject *res = PyList_New(0);
    if (res == NULL)
        return NULL;

    for (gsdef = ctypedescr_getsets; gsdef->name; gsdef++) {
        PyObject *x = PyObject_GetAttrString(ct, gsdef->name);
        if (x == NULL) {
            PyErr_Clear();
        }
        else {
            Py_DECREF(x);
            x = PyText_FromString(gsdef->name);
            err = (x != NULL) ? PyList_Append(res, x) : -1;
            Py_XDECREF(x);
            if (err < 0) {
                Py_DECREF(res);
                return NULL;
            }
        }
    }
    return res;
}

static PyMethodDef ctypedescr_methods[] = {
    {"__dir__",   ctypedescr_dir,  METH_NOARGS},
    {NULL,        NULL}           /* sentinel */
};

static PyTypeObject CTypeDescr_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.CTypeDescr",
    offsetof(CTypeDescrObject, ct_name),
    sizeof(char),
    (destructor)ctypedescr_dealloc,             /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    (reprfunc)ctypedescr_repr,                  /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)ctypedescr_traverse,          /* tp_traverse */
    (inquiry)ctypedescr_clear,                  /* tp_clear */
    0,                                          /* tp_richcompare */
    offsetof(CTypeDescrObject, ct_weakreflist), /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    ctypedescr_methods,                         /* tp_methods */
    0,                                          /* tp_members */
    ctypedescr_getsets,                         /* tp_getset */
};

/************************************************************/

static PyObject *
get_field_name(CTypeDescrObject *ct, CFieldObject *cf)
{
    Py_ssize_t i = 0;
    PyObject *d_key, *d_value;
    while (PyDict_Next(ct->ct_stuff, &i, &d_key, &d_value)) {
        if (d_value == (PyObject *)cf)
            return d_key;
    }
    Py_FatalError("_cffi_backend: get_field_name()");
    return NULL;
}

static void
cfield_dealloc(CFieldObject *cf)
{
    Py_DECREF(cf->cf_type);
    PyObject_Del(cf);
}

#undef OFF
#define OFF(x) offsetof(CFieldObject, x)

static PyMemberDef cfield_members[] = {
    {"type", T_OBJECT, OFF(cf_type), READONLY},
    {"offset", T_PYSSIZET, OFF(cf_offset), READONLY},
    {"bitshift", T_SHORT, OFF(cf_bitshift), READONLY},
    {"bitsize", T_SHORT, OFF(cf_bitsize), READONLY},
    {NULL}      /* Sentinel */
};
#undef OFF

static PyTypeObject CField_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.CField",
    sizeof(CFieldObject),
    0,
    (destructor)cfield_dealloc,                 /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    0,                                          /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    cfield_members,                             /* tp_members */
};

/************************************************************/

static int
CDataObject_Or_PyFloat_Check(PyObject *ob)
{
    return (PyFloat_Check(ob) ||
            (CData_Check(ob) &&
             (((CDataObject *)ob)->c_type->ct_flags & CT_PRIMITIVE_FLOAT)));
}

static PY_LONG_LONG
_my_PyLong_AsLongLong(PyObject *ob)
{
    /* (possibly) convert and cast a Python object to a long long.
       Like PyLong_AsLongLong(), this version accepts a Python int too, and
       does convertions from other types of objects.  The difference is that
       this version refuses floats. */
#if PY_MAJOR_VERSION < 3
    if (PyInt_Check(ob)) {
        return PyInt_AS_LONG(ob);
    }
    else 
#endif
    if (PyLong_Check(ob)) {
        return PyLong_AsLongLong(ob);
    }
    else {
        PyObject *io;
        PY_LONG_LONG res;
        PyNumberMethods *nb = ob->ob_type->tp_as_number;

        if (CDataObject_Or_PyFloat_Check(ob) ||
                nb == NULL || nb->nb_int == NULL) {
            PyErr_SetString(PyExc_TypeError, "an integer is required");
            return -1;
        }
        io = (*nb->nb_int) (ob);
        if (io == NULL)
            return -1;

        if (PyIntOrLong_Check(io)) {
            res = _my_PyLong_AsLongLong(io);
        }
        else {
            PyErr_SetString(PyExc_TypeError, "integer conversion failed");
            res = -1;
        }
        Py_DECREF(io);
        return res;
    }
}

static unsigned PY_LONG_LONG
_my_PyLong_AsUnsignedLongLong(PyObject *ob, int strict)
{
    /* (possibly) convert and cast a Python object to an unsigned long long.
       Like PyLong_AsLongLong(), this version accepts a Python int too, and
       does convertions from other types of objects.  If 'strict', complains
       with OverflowError and refuses floats.  If '!strict', rounds floats
       and masks the result. */
#if PY_MAJOR_VERSION < 3
    if (PyInt_Check(ob)) {
        long value1 = PyInt_AS_LONG(ob);
        if (strict && value1 < 0)
            goto negative;
        return (unsigned PY_LONG_LONG)(PY_LONG_LONG)value1;
    }
    else
#endif
    if (PyLong_Check(ob)) {
        if (strict) {
            if (_PyLong_Sign(ob) < 0)
                goto negative;
            return PyLong_AsUnsignedLongLong(ob);
        }
        else {
            return PyLong_AsUnsignedLongLongMask(ob);
        }
    }
    else {
        PyObject *io;
        unsigned PY_LONG_LONG res;
        PyNumberMethods *nb = ob->ob_type->tp_as_number;

        if ((strict && CDataObject_Or_PyFloat_Check(ob)) ||
                nb == NULL || nb->nb_int == NULL) {
            PyErr_SetString(PyExc_TypeError, "an integer is required");
            return (unsigned PY_LONG_LONG)-1;
        }
        io = (*nb->nb_int) (ob);
        if (io == NULL)
            return (unsigned PY_LONG_LONG)-1;

        if (PyIntOrLong_Check(io)) {
            res = _my_PyLong_AsUnsignedLongLong(io, strict);
        }
        else {
            PyErr_SetString(PyExc_TypeError, "integer conversion failed");
            res = (unsigned PY_LONG_LONG)-1;
        }
        Py_DECREF(io);
        return res;
    }

 negative:
    PyErr_SetString(PyExc_OverflowError,
                    "can't convert negative number to unsigned");
    return (unsigned PY_LONG_LONG)-1;
}

#define _read_raw_data(type)                    \
    do {                                        \
        if (size == sizeof(type)) {             \
            type r;                             \
            memcpy(&r, target, sizeof(type));   \
            return r;                           \
        }                                       \
    } while(0)

static PY_LONG_LONG
read_raw_signed_data(char *target, int size)
{
    _read_raw_data(signed char);
    _read_raw_data(short);
    _read_raw_data(int);
    _read_raw_data(long);
    _read_raw_data(PY_LONG_LONG);
    Py_FatalError("read_raw_signed_data: bad integer size");
    return 0;
}

static unsigned PY_LONG_LONG
read_raw_unsigned_data(char *target, int size)
{
    _read_raw_data(unsigned char);
    _read_raw_data(unsigned short);
    _read_raw_data(unsigned int);
    _read_raw_data(unsigned long);
    _read_raw_data(unsigned PY_LONG_LONG);
    Py_FatalError("read_raw_unsigned_data: bad integer size");
    return 0;
}

#define _write_raw_data(type)                           \
    do {                                                \
        if (size == sizeof(type)) {                     \
            type r = (type)source;                      \
            memcpy(target, &r, sizeof(type));           \
            return;                                     \
        }                                               \
    } while(0)

static void
write_raw_integer_data(char *target, unsigned PY_LONG_LONG source, int size)
{
    _write_raw_data(unsigned char);
    _write_raw_data(unsigned short);
    _write_raw_data(unsigned int);
    _write_raw_data(unsigned long);
    _write_raw_data(unsigned PY_LONG_LONG);
    Py_FatalError("write_raw_integer_data: bad integer size");
}

static double
read_raw_float_data(char *target, int size)
{
    _read_raw_data(float);
    _read_raw_data(double);
    Py_FatalError("read_raw_float_data: bad float size");
    return 0;
}

static long double
read_raw_longdouble_data(char *target)
{
    int size = sizeof(long double);
    _read_raw_data(long double);
    Py_FatalError("read_raw_longdouble_data: bad long double size");
    return 0;
}

static void
write_raw_float_data(char *target, double source, int size)
{
    _write_raw_data(float);
    _write_raw_data(double);
    Py_FatalError("write_raw_float_data: bad float size");
}

static void
write_raw_longdouble_data(char *target, long double source)
{
    int size = sizeof(long double);
    _write_raw_data(long double);
}

static PyObject *
new_simple_cdata(char *data, CTypeDescrObject *ct)
{
    CDataObject *cd = PyObject_New(CDataObject, &CData_Type);
    if (cd == NULL)
        return NULL;
    Py_INCREF(ct);
    cd->c_data = data;
    cd->c_type = ct;
    cd->c_weakreflist = NULL;
    return (PyObject *)cd;
}

static CDataObject *_new_casted_primitive(CTypeDescrObject *ct);  /*forward*/

static PyObject *
convert_to_object(char *data, CTypeDescrObject *ct)
{
    if (!(ct->ct_flags & CT_PRIMITIVE_ANY)) {
        /* non-primitive types (check done just for performance) */
        if (ct->ct_flags & (CT_POINTER|CT_FUNCTIONPTR)) {
            char *ptrdata = *(char **)data;
            /*READ(data, sizeof(char *))*/
            return new_simple_cdata(ptrdata, ct);
        }
        else if (ct->ct_flags & CT_IS_OPAQUE) {
            PyErr_Format(PyExc_TypeError, "cdata '%s' is opaque",
                         ct->ct_name);
            return NULL;
        }
        else if (ct->ct_flags & (CT_STRUCT|CT_UNION)) {
            return new_simple_cdata(data, ct);
        }
        else if (ct->ct_flags & CT_ARRAY) {
            if (ct->ct_length < 0) {
                /* we can't return a <cdata 'int[]'> here, because we don't
                   know the length to give it.  As a compromize, returns
                   <cdata 'int *'> in this case. */
                ct = (CTypeDescrObject *)ct->ct_stuff;
            }
            return new_simple_cdata(data, ct);
        }
    }
    else if (ct->ct_flags & CT_PRIMITIVE_SIGNED) {
        PY_LONG_LONG value;
        /*READ(data, ct->ct_size)*/
        value = read_raw_signed_data(data, ct->ct_size);
        if (ct->ct_flags & CT_PRIMITIVE_FITS_LONG)
            return PyInt_FromLong((long)value);
        else
            return PyLong_FromLongLong(value);
    }
    else if (ct->ct_flags & CT_PRIMITIVE_UNSIGNED) {
        unsigned PY_LONG_LONG value;
        /*READ(data, ct->ct_size)*/
        value = read_raw_unsigned_data(data, ct->ct_size);

        if (ct->ct_flags & CT_PRIMITIVE_FITS_LONG)
            return PyInt_FromLong((long)value);
        else
            return PyLong_FromUnsignedLongLong(value);
    }
    else if (ct->ct_flags & CT_PRIMITIVE_FLOAT) {
        /*READ(data, ct->ct_size)*/
        if (!(ct->ct_flags & CT_IS_LONGDOUBLE)) {
            double value = read_raw_float_data(data, ct->ct_size);
            return PyFloat_FromDouble(value);
        }
        else {
            long double value = read_raw_longdouble_data(data);
            CDataObject *cd = _new_casted_primitive(ct);
            if (cd != NULL)
                write_raw_longdouble_data(cd->c_data, value);
            return (PyObject *)cd;
        }
    }
    else if (ct->ct_flags & CT_PRIMITIVE_CHAR) {
        /*READ(data, ct->ct_size)*/
        if (ct->ct_size == sizeof(char))
            return PyBytes_FromStringAndSize(data, 1);
#ifdef HAVE_WCHAR_H
        else
            return _my_PyUnicode_FromWideChar((wchar_t *)data, 1);
#endif
    }

    PyErr_Format(PyExc_SystemError,
                 "convert_to_object: '%s'", ct->ct_name);
    return NULL;
}

static PyObject *
convert_to_object_bitfield(char *data, CFieldObject *cf)
{
    CTypeDescrObject *ct = cf->cf_type;
    /*READ(data, ct->ct_size)*/

    if (ct->ct_flags & CT_PRIMITIVE_SIGNED) {
        unsigned PY_LONG_LONG value, valuemask, shiftforsign;
        PY_LONG_LONG result;

        value = (unsigned PY_LONG_LONG)read_raw_signed_data(data, ct->ct_size);
        valuemask = (1ULL << cf->cf_bitsize) - 1ULL;
        shiftforsign = 1ULL << (cf->cf_bitsize - 1);
        value = ((value >> cf->cf_bitshift) + shiftforsign) & valuemask;
        result = ((PY_LONG_LONG)value) - (PY_LONG_LONG)shiftforsign;

        if (ct->ct_flags & CT_PRIMITIVE_FITS_LONG)
            return PyInt_FromLong((long)result);
        else
            return PyLong_FromLongLong(result);
    }
    else {
        unsigned PY_LONG_LONG value, valuemask;

        value = read_raw_unsigned_data(data, ct->ct_size);
        valuemask = (1ULL << cf->cf_bitsize) - 1ULL;
        value = (value >> cf->cf_bitshift) & valuemask;

        if (ct->ct_flags & CT_PRIMITIVE_FITS_LONG)
            return PyInt_FromLong((long)value);
        else
            return PyLong_FromUnsignedLongLong(value);
    }
}

static int _convert_overflow(PyObject *init, const char *ct_name)
{
    PyObject *s;
    if (PyErr_Occurred())   /* already an exception pending */
        return -1;
    s = PyObject_Str(init);
    if (s == NULL)
        return -1;
    PyErr_Format(PyExc_OverflowError, "integer %s does not fit '%s'",
                 PyText_AS_UTF8(s), ct_name);
    Py_DECREF(s);
    return -1;
}

static int _convert_to_char(PyObject *init)
{
    if (PyBytes_Check(init) && PyBytes_GET_SIZE(init) == 1) {
        return (unsigned char)(PyBytes_AS_STRING(init)[0]);
    }
    if (CData_Check(init) &&
           (((CDataObject *)init)->c_type->ct_flags & CT_PRIMITIVE_CHAR) &&
           (((CDataObject *)init)->c_type->ct_size == sizeof(char))) {
        char *data = ((CDataObject *)init)->c_data;
        /*READ(data, 1)*/
        return *(unsigned char *)data;
    }
    PyErr_Format(PyExc_TypeError,
                 "initializer for ctype 'char' must be a "STR_OR_BYTES
                 " of length 1, not %.200s", Py_TYPE(init)->tp_name);
    return -1;
}

#ifdef HAVE_WCHAR_H
static wchar_t _convert_to_wchar_t(PyObject *init)
{
    if (PyUnicode_Check(init)) {
        wchar_t ordinal;
        if (_my_PyUnicode_AsSingleWideChar(init, &ordinal) == 0)
            return ordinal;
    }
    if (CData_Check(init) &&
           (((CDataObject *)init)->c_type->ct_flags & CT_PRIMITIVE_CHAR) &&
           (((CDataObject *)init)->c_type->ct_size == sizeof(wchar_t))) {
        char *data = ((CDataObject *)init)->c_data;
        /*READ(data, sizeof(wchar_t))*/
        return *(wchar_t *)data;
    }
    PyErr_Format(PyExc_TypeError,
                 "initializer for ctype 'wchar_t' must be a unicode string "
                 "of length 1, not %.200s", Py_TYPE(init)->tp_name);
    return (wchar_t)-1;
}
#endif

static int _convert_error(PyObject *init, const char *ct_name,
                          const char *expected)
{
    if (CData_Check(init)) {
        const char *ct_name_2 = ((CDataObject *)init)->c_type->ct_name;
        if (strcmp(ct_name, ct_name_2) != 0)
            PyErr_Format(PyExc_TypeError,
                         "initializer for ctype '%s' must be a %s, "
                         "not cdata '%s'",
                         ct_name, expected, ct_name_2);
        else {
            /* in case we'd give the error message "initializer for
               ctype 'A' must be a pointer to same type, not cdata
               'B'", but with A=B, then give instead a different error
               message to try to clear up the confusion */
            PyErr_Format(PyExc_TypeError,
                         "initializer for ctype '%s' appears indeed to be '%s',"
                         " but the types are different (check that you are not"
                         " e.g. mixing up different ffi instances)",
                         ct_name, ct_name_2);
        }
    }
    else
        PyErr_Format(PyExc_TypeError,
                     "initializer for ctype '%s' must be a %s, "
                     "not %.200s",
                     ct_name, expected, Py_TYPE(init)->tp_name);
    return -1;
}

static int    /* forward */
convert_from_object(char *data, CTypeDescrObject *ct, PyObject *init);
static int    /* forward */
convert_from_object_bitfield(char *data, CFieldObject *cf, PyObject *init);

static Py_ssize_t
get_new_array_length(PyObject **pvalue)
{
    PyObject *value = *pvalue;

    if (PyList_Check(value) || PyTuple_Check(value)) {
        return PySequence_Fast_GET_SIZE(value);
    }
    else if (PyBytes_Check(value)) {
        /* from a string, we add the null terminator */
        return PyBytes_GET_SIZE(value) + 1;
    }
    else if (PyUnicode_Check(value)) {
        /* from a unicode, we add the null terminator */
        return _my_PyUnicode_SizeAsWideChar(value) + 1;
    }
    else {
        Py_ssize_t explicitlength;
        explicitlength = PyNumber_AsSsize_t(value, PyExc_OverflowError);
        if (explicitlength < 0) {
            if (!PyErr_Occurred())
                PyErr_SetString(PyExc_ValueError, "negative array length");
            return -1;
        }
        *pvalue = Py_None;
        return explicitlength;
    }
}

static int
convert_field_from_object(char *data, CFieldObject *cf, PyObject *value)
{
    data += cf->cf_offset;
    if (cf->cf_bitshift >= 0)
        return convert_from_object_bitfield(data, cf, value);
    else
        return convert_from_object(data, cf->cf_type, value);
}

static int
convert_vfield_from_object(char *data, CFieldObject *cf, PyObject *value,
                           Py_ssize_t *optvarsize)
{
    /* a special case for var-sized C99 arrays */
    if ((cf->cf_type->ct_flags & CT_ARRAY) && cf->cf_type->ct_size < 0) {
        Py_ssize_t varsizelength = get_new_array_length(&value);
        if (varsizelength < 0)
            return -1;
        if (optvarsize != NULL) {
            /* in this mode, the only purpose of this function is to compute
               the real size of the structure from a var-sized C99 array */
            Py_ssize_t size, itemsize;
            assert(data == NULL);
            itemsize = cf->cf_type->ct_itemdescr->ct_size;
            size = cf->cf_offset + itemsize * varsizelength;
            if (size < 0 ||
                ((size - cf->cf_offset) / itemsize) != varsizelength) {
                PyErr_SetString(PyExc_OverflowError,
                                "array size would overflow a Py_ssize_t");
                return -1;
            }
            if (size > *optvarsize)
                *optvarsize = size;
            return 0;
        }
        /* if 'value' was only an integer, get_new_array_length() returns
           it and convert 'value' to be None.  Detect if this was the case,
           and if so, stop here, leaving the content uninitialized
           (it should be zero-initialized from somewhere else). */
        if (value == Py_None)
            return 0;
    }
    if (optvarsize == NULL)
        return convert_field_from_object(data, cf, value);
    else
        return 0;
}

static int
convert_array_from_object(char *data, CTypeDescrObject *ct, PyObject *init)
{
    /* used by convert_from_object(), and also to decode lists/tuples/unicodes
       passed as function arguments.  'ct' is an CT_ARRAY in the first case
       and a CT_POINTER in the second case. */
    const char *expected;
    CTypeDescrObject *ctitem = ct->ct_itemdescr;

    if (PyList_Check(init) || PyTuple_Check(init)) {
        PyObject **items;
        Py_ssize_t i, n;
        n = PySequence_Fast_GET_SIZE(init);
        if (ct->ct_length >= 0 && n > ct->ct_length) {
            PyErr_Format(PyExc_IndexError,
                         "too many initializers for '%s' (got %zd)",
                         ct->ct_name, n);
            return -1;
        }
        items = PySequence_Fast_ITEMS(init);
        for (i=0; i<n; i++) {
            if (convert_from_object(data, ctitem, items[i]) < 0)
                return -1;
            data += ctitem->ct_size;
        }
        return 0;
    }
    else if ((ctitem->ct_flags & CT_PRIMITIVE_CHAR) ||
             ((ctitem->ct_flags & (CT_PRIMITIVE_SIGNED|CT_PRIMITIVE_UNSIGNED))
              && (ctitem->ct_size == sizeof(char)))) {
        if (ctitem->ct_size == sizeof(char)) {
            char *srcdata;
            Py_ssize_t n;
            if (!PyBytes_Check(init)) {
                expected = STR_OR_BYTES" or list or tuple";
                goto cannot_convert;
            }
            n = PyBytes_GET_SIZE(init);
            if (ct->ct_length >= 0 && n > ct->ct_length) {
                PyErr_Format(PyExc_IndexError,
                             "initializer "STR_OR_BYTES" is too long for '%s' "
                             "(got %zd characters)", ct->ct_name, n);
                return -1;
            }
            if (n != ct->ct_length)
                n++;
            srcdata = PyBytes_AS_STRING(init);
            memcpy(data, srcdata, n);
            return 0;
        }
#ifdef HAVE_WCHAR_H
        else {
            Py_ssize_t n;
            if (!PyUnicode_Check(init)) {
                expected = "unicode or list or tuple";
                goto cannot_convert;
            }
            n = _my_PyUnicode_SizeAsWideChar(init);
            if (ct->ct_length >= 0 && n > ct->ct_length) {
                PyErr_Format(PyExc_IndexError,
                             "initializer unicode is too long for '%s' "
                             "(got %zd characters)", ct->ct_name, n);
                return -1;
            }
            if (n != ct->ct_length)
                n++;
            _my_PyUnicode_AsWideChar(init, (wchar_t *)data, n);
            return 0;
        }
#endif
    }
    else {
        expected = "list or tuple";
        goto cannot_convert;
    }

 cannot_convert:
    return _convert_error(init, ct->ct_name, expected);
}

static int
convert_struct_from_object(char *data, CTypeDescrObject *ct, PyObject *init,
                           Py_ssize_t *optvarsize)
{
    const char *expected;

    if (force_lazy_struct(ct) <= 0) {
        if (!PyErr_Occurred())
            PyErr_Format(PyExc_TypeError, "'%s' is opaque", ct->ct_name);
        return -1;
    }

    if (ct->ct_flags & CT_UNION) {
        Py_ssize_t n = PyObject_Size(init);
        if (n < 0)
            return -1;
        if (n > 1) {
            PyErr_Format(PyExc_ValueError,
                         "initializer for '%s': %zd items given, but "
                         "only one supported (use a dict if needed)",
                         ct->ct_name, n);
            return -1;
        }
    }
    if (PyList_Check(init) || PyTuple_Check(init)) {
        PyObject **items = PySequence_Fast_ITEMS(init);
        Py_ssize_t i, n = PySequence_Fast_GET_SIZE(init);
        CFieldObject *cf = (CFieldObject *)ct->ct_extra;

        for (i=0; i<n; i++) {
            if (cf == NULL) {
                PyErr_Format(PyExc_ValueError,
                             "too many initializers for '%s' (got %zd)",
                             ct->ct_name, n);
                return -1;
            }
            if (convert_vfield_from_object(data, cf, items[i], optvarsize) < 0)
                return -1;
            cf = cf->cf_next;
        }
        return 0;
    }
    if (PyDict_Check(init)) {
        PyObject *d_key, *d_value;
        Py_ssize_t i = 0;
        CFieldObject *cf;

        while (PyDict_Next(init, &i, &d_key, &d_value)) {
            cf = (CFieldObject *)PyDict_GetItem(ct->ct_stuff, d_key);
            if (cf == NULL) {
                PyErr_SetObject(PyExc_KeyError, d_key);
                return -1;
            }
            if (convert_vfield_from_object(data, cf, d_value, optvarsize) < 0)
                return -1;
        }
        return 0;
    }
    expected = optvarsize == NULL ? "list or tuple or dict or struct-cdata"
                                  : "list or tuple or dict";
    return _convert_error(init, ct->ct_name, expected);
}

#ifdef __GNUC__
# if __GNUC__ >= 4
/* Don't go inlining this huge function.  Needed because occasionally
   it gets inlined in places where is causes a warning: call to
   __builtin___memcpy_chk will always overflow destination buffer
   (which is places where the 'ct' should never represent such a large
   primitive type anyway). */
__attribute__((noinline))
# endif
#endif
static int
convert_from_object(char *data, CTypeDescrObject *ct, PyObject *init)
{
    const char *expected;
    char buf[sizeof(PY_LONG_LONG)];

    /*if (ct->ct_size > 0)*/
        /*WRITE(data, ct->ct_size)*/

    if (ct->ct_flags & CT_ARRAY) {
        return convert_array_from_object(data, ct, init);
    }
    if (ct->ct_flags & (CT_POINTER|CT_FUNCTIONPTR)) {
        char *ptrdata;
        CTypeDescrObject *ctinit;

        if (!CData_Check(init)) {
            expected = "cdata pointer";
            goto cannot_convert;
        }
        ctinit = ((CDataObject *)init)->c_type;
        if (!(ctinit->ct_flags & (CT_POINTER|CT_FUNCTIONPTR))) {
            if (ctinit->ct_flags & CT_ARRAY)
                ctinit = (CTypeDescrObject *)ctinit->ct_stuff;
            else {
                expected = "pointer or array";
                goto cannot_convert;
            }
        }
        if (ctinit != ct) {
            if ((ct->ct_flags & CT_CAST_ANYTHING) ||
                (ctinit->ct_flags & CT_CAST_ANYTHING))
                ;   /* accept void* or char* as either source or target */
            else {
                expected = "pointer to same type";
                goto cannot_convert;
            }
        }
        ptrdata = ((CDataObject *)init)->c_data;

        *(char **)data = ptrdata;
        return 0;
    }
    if (ct->ct_flags & CT_PRIMITIVE_SIGNED) {
        PY_LONG_LONG value = _my_PyLong_AsLongLong(init);
        if (value == -1 && PyErr_Occurred())
            return -1;
        write_raw_integer_data(buf, value, ct->ct_size);
        if (value != read_raw_signed_data(buf, ct->ct_size))
            goto overflow;
        write_raw_integer_data(data, value, ct->ct_size);
        return 0;
    }
    if (ct->ct_flags & CT_PRIMITIVE_UNSIGNED) {
        unsigned PY_LONG_LONG value = _my_PyLong_AsUnsignedLongLong(init, 1);
        if (value == (unsigned PY_LONG_LONG)-1 && PyErr_Occurred())
            return -1;
        if (ct->ct_flags & CT_IS_BOOL)
            if (value & ~1)      /* value != 0 && value != 1 */
                goto overflow;
        write_raw_integer_data(buf, value, ct->ct_size);
        if (value != read_raw_unsigned_data(buf, ct->ct_size))
            goto overflow;
        write_raw_integer_data(data, value, ct->ct_size);
        return 0;
    }
    if (ct->ct_flags & CT_PRIMITIVE_FLOAT) {
        double value;
        if ((ct->ct_flags & CT_IS_LONGDOUBLE) &&
                CData_Check(init) &&
                (((CDataObject *)init)->c_type->ct_flags & CT_IS_LONGDOUBLE)) {
            long double lvalue;
            char *initdata = ((CDataObject *)init)->c_data;
            /*READ(initdata, sizeof(long double))*/
            lvalue = read_raw_longdouble_data(initdata);
            write_raw_longdouble_data(data, lvalue);
            return 0;
        }
        value = PyFloat_AsDouble(init);
        if (value == -1.0 && PyErr_Occurred())
            return -1;
        if (!(ct->ct_flags & CT_IS_LONGDOUBLE))
            write_raw_float_data(data, value, ct->ct_size);
        else
            write_raw_longdouble_data(data, (long double)value);
        return 0;
    }
    if (ct->ct_flags & CT_PRIMITIVE_CHAR) {
        if (ct->ct_size == sizeof(char)) {
            int res = _convert_to_char(init);
            if (res < 0)
                return -1;
            data[0] = res;
            return 0;
        }
#ifdef HAVE_WCHAR_H
        else {
            wchar_t res = _convert_to_wchar_t(init);
            if (res == (wchar_t)-1 && PyErr_Occurred())
                return -1;
            *(wchar_t *)data = res;
            return 0;
        }
#endif
    }
    if (ct->ct_flags & (CT_STRUCT|CT_UNION)) {

        if (CData_Check(init)) {
            if (((CDataObject *)init)->c_type == ct && ct->ct_size >= 0) {
                memcpy(data, ((CDataObject *)init)->c_data, ct->ct_size);
                return 0;
            }
        }
        return convert_struct_from_object(data, ct, init, NULL);
    }
    PyErr_Format(PyExc_SystemError,
                 "convert_from_object: '%s'", ct->ct_name);
    return -1;

 overflow:
    return _convert_overflow(init, ct->ct_name);

 cannot_convert:
    return _convert_error(init, ct->ct_name, expected);
}

static int
convert_from_object_bitfield(char *data, CFieldObject *cf, PyObject *init)
{
    CTypeDescrObject *ct = cf->cf_type;
    PY_LONG_LONG fmin, fmax, value = PyLong_AsLongLong(init);
    unsigned PY_LONG_LONG rawfielddata, rawvalue, rawmask;
    if (value == -1 && PyErr_Occurred())
        return -1;

    if (ct->ct_flags & CT_PRIMITIVE_SIGNED) {
        fmin = -(1LL << (cf->cf_bitsize-1));
        fmax = (1LL << (cf->cf_bitsize-1)) - 1LL;
        if (fmax == 0)
            fmax = 1;    /* special case to let "int x:1" receive "1" */
    }
    else {
        fmin = 0LL;
        fmax = (PY_LONG_LONG)((1ULL << cf->cf_bitsize) - 1ULL);
    }
    if (value < fmin || value > fmax) {
        /* phew, PyErr_Format does not support "%lld" in Python 2.6 */
        PyObject *svalue = NULL, *sfmin = NULL, *sfmax = NULL;
        PyObject *lfmin = NULL, *lfmax = NULL;
        svalue = PyObject_Str(init);
        if (svalue == NULL) goto skip;
        lfmin = PyLong_FromLongLong(fmin);
        if (lfmin == NULL) goto skip;
        sfmin = PyObject_Str(lfmin);
        if (sfmin == NULL) goto skip;
        lfmax = PyLong_FromLongLong(fmax);
        if (lfmax == NULL) goto skip;
        sfmax = PyObject_Str(lfmax);
        if (sfmax == NULL) goto skip;
        PyErr_Format(PyExc_OverflowError,
                     "value %s outside the range allowed by the "
                     "bit field width: %s <= x <= %s",
                     PyText_AS_UTF8(svalue),
                     PyText_AS_UTF8(sfmin),
                     PyText_AS_UTF8(sfmax));
       skip:
        Py_XDECREF(svalue);
        Py_XDECREF(sfmin);
        Py_XDECREF(sfmax);
        Py_XDECREF(lfmin);
        Py_XDECREF(lfmax);
        return -1;
    }

    rawmask = ((1ULL << cf->cf_bitsize) - 1ULL) << cf->cf_bitshift;
    rawvalue = ((unsigned PY_LONG_LONG)value) << cf->cf_bitshift;
    /*WRITE(data, ct->ct_size)*/
    rawfielddata = read_raw_unsigned_data(data, ct->ct_size);
    rawfielddata = (rawfielddata & ~rawmask) | (rawvalue & rawmask);
    write_raw_integer_data(data, rawfielddata, ct->ct_size);
    return 0;
}

static Py_ssize_t
get_array_length(CDataObject *cd)
{
    if (cd->c_type->ct_length < 0)
        return ((CDataObject_own_length *)cd)->length;
    else
        return cd->c_type->ct_length;
}

static int
get_alignment(CTypeDescrObject *ct)
{
    int align;
 retry:
    if ((ct->ct_flags & (CT_PRIMITIVE_ANY|CT_STRUCT|CT_UNION)) &&
        !(ct->ct_flags & CT_IS_OPAQUE)) {
        align = ct->ct_length;
        if (align == -1 && (ct->ct_flags & CT_LAZY_FIELD_LIST)) {
            force_lazy_struct(ct);
            align = ct->ct_length;
        }
    }
    else if (ct->ct_flags & (CT_POINTER|CT_FUNCTIONPTR)) {
        struct aligncheck_ptr { char x; char *y; };
        align = offsetof(struct aligncheck_ptr, y);
    }
    else if (ct->ct_flags & CT_ARRAY) {
        ct = ct->ct_itemdescr;
        goto retry;
    }
    else {
        PyErr_Format(PyExc_ValueError, "ctype '%s' is of unknown alignment",
                     ct->ct_name);
        return -1;
    }

    if ((align < 1) || (align & (align-1))) {
        PyErr_Format(PyExc_SystemError,
                     "found for ctype '%s' bogus alignment '%d'",
                     ct->ct_name, align);
        return -1;
    }
    return align;
}

static void cdata_dealloc(CDataObject *cd)
{
    if (cd->c_weakreflist != NULL)
        PyObject_ClearWeakRefs((PyObject *) cd);

    Py_DECREF(cd->c_type);
#ifndef CFFI_MEM_LEAK     /* never release anything, tests only */
    Py_TYPE(cd)->tp_free((PyObject *)cd);
#endif
}

static void cdataowning_dealloc(CDataObject *cd)
{
    assert(!(cd->c_type->ct_flags & (CT_IS_VOID_PTR | CT_FUNCTIONPTR)));

    if (cd->c_type->ct_flags & CT_IS_PTR_TO_OWNED) {
        Py_DECREF(((CDataObject_own_structptr *)cd)->structobj);
    }
#if defined(CFFI_MEM_DEBUG) || defined(CFFI_MEM_LEAK)
    if (cd->c_type->ct_flags & (CT_PRIMITIVE_ANY | CT_STRUCT | CT_UNION)) {
        assert(cd->c_type->ct_size >= 0);
        memset(cd->c_data, 0xDD, cd->c_type->ct_size);
    }
    else if (cd->c_type->ct_flags & CT_ARRAY) {
        Py_ssize_t x = get_array_length(cd);
        assert(x >= 0);
        x *= cd->c_type->ct_itemdescr->ct_size;
        assert(x >= 0);
        memset(cd->c_data, 0xDD, x);
    }
#endif
    cdata_dealloc(cd);
}

static void cdataowninggc_dealloc(CDataObject *cd)
{
    assert(!(cd->c_type->ct_flags & (CT_IS_PTR_TO_OWNED |
                                     CT_PRIMITIVE_ANY |
                                     CT_STRUCT | CT_UNION)));
    PyObject_GC_UnTrack(cd);

    if (cd->c_type->ct_flags & CT_IS_VOID_PTR) {        /* a handle */
        PyObject *x = ((CDataObject_own_structptr *)cd)->structobj;
        Py_DECREF(x);
    }
    else if (cd->c_type->ct_flags & CT_FUNCTIONPTR) {   /* a callback */
        ffi_closure *closure = (ffi_closure *)cd->c_data;
        PyObject *args = (PyObject *)(closure->user_data);
        Py_XDECREF(args);
        cffi_closure_free(closure);
    }
    else if (cd->c_type->ct_flags & CT_IS_UNSIZED_CHAR_A) {  /* from_buffer */
        Py_buffer *view = ((CDataObject_owngc_frombuf *)cd)->bufferview;
        PyBuffer_Release(view);
        PyObject_Free(view);
    }
    cdata_dealloc(cd);
}

static int cdataowninggc_traverse(CDataObject *cd, visitproc visit, void *arg)
{
    if (cd->c_type->ct_flags & CT_IS_VOID_PTR) {        /* a handle */
        PyObject *x = ((CDataObject_own_structptr *)cd)->structobj;
        Py_VISIT(x);
    }
    else if (cd->c_type->ct_flags & CT_FUNCTIONPTR) {   /* a callback */
        ffi_closure *closure = (ffi_closure *)cd->c_data;
        PyObject *args = (PyObject *)(closure->user_data);
        Py_VISIT(args);
    }
    else if (cd->c_type->ct_flags & CT_IS_UNSIZED_CHAR_A) {  /* from_buffer */
        Py_buffer *view = ((CDataObject_owngc_frombuf *)cd)->bufferview;
        Py_VISIT(view->obj);
    }
    return 0;
}

static int cdataowninggc_clear(CDataObject *cd)
{
    if (cd->c_type->ct_flags & CT_IS_VOID_PTR) {        /* a handle */
        CDataObject_own_structptr *cd1 = (CDataObject_own_structptr *)cd;
        PyObject *x = cd1->structobj;
        Py_INCREF(Py_None);
        cd1->structobj = Py_None;
        Py_DECREF(x);
    }
    else if (cd->c_type->ct_flags & CT_FUNCTIONPTR) {   /* a callback */
        ffi_closure *closure = (ffi_closure *)cd->c_data;
        PyObject *args = (PyObject *)(closure->user_data);
        closure->user_data = NULL;
        Py_XDECREF(args);
    }
    else if (cd->c_type->ct_flags & CT_IS_UNSIZED_CHAR_A) {  /* from_buffer */
        Py_buffer *view = ((CDataObject_owngc_frombuf *)cd)->bufferview;
        PyBuffer_Release(view);
    }
    return 0;
}

/* forward */
static void _my_PyErr_WriteUnraisable(char *objdescr, PyObject *obj,
                                      char *extra_error_line);


static void gcp_finalize(PyObject *destructor, PyObject *origobj)
{
    /* NOTE: this decrements the reference count of the two arguments */

    if (destructor != NULL) {
        PyObject *result;
        PyObject *error_type, *error_value, *error_traceback;

        /* Save the current exception */
        PyErr_Fetch(&error_type, &error_value, &error_traceback);

        result = PyObject_CallFunctionObjArgs(destructor, origobj, NULL);
        if (result != NULL) {
            Py_DECREF(result);
        }
        else {
            _my_PyErr_WriteUnraisable("From callback for ffi.gc ",
                                      origobj, NULL);
        }
        Py_DECREF(destructor);

        /* Restore the saved exception */
        PyErr_Restore(error_type, error_value, error_traceback);
    }
    Py_XDECREF(origobj);
}

#ifdef Py_TPFLAGS_HAVE_FINALIZE     /* CPython >= 3.4 */
static void cdatagcp_finalize(CDataObject_gcp *cd)
{
    PyObject *destructor = cd->destructor;
    PyObject *origobj = cd->origobj;
    cd->destructor = NULL;
    cd->origobj = NULL;
    gcp_finalize(destructor, origobj);
}
#endif

static void cdatagcp_dealloc(CDataObject_gcp *cd)
{
    PyObject *destructor = cd->destructor;
    PyObject *origobj = cd->origobj;
    cdata_dealloc((CDataObject *)cd);

    gcp_finalize(destructor, origobj);
}

static int cdatagcp_traverse(CDataObject_gcp *cd, visitproc visit, void *arg)
{
    Py_VISIT(cd->destructor);
    Py_VISIT(cd->origobj);
    return 0;
}

static PyObject *cdata_float(CDataObject *cd);  /*forward*/

static PyObject *convert_cdata_to_enum_string(CDataObject *cd, int both)
{
    PyObject *d_key, *d_value;
    CTypeDescrObject *ct = cd->c_type;

    assert(ct->ct_flags & CT_IS_ENUM);
    d_key = convert_to_object(cd->c_data, ct);
    if (d_key == NULL)
        return NULL;

    d_value = PyDict_GetItem(PyTuple_GET_ITEM(ct->ct_stuff, 1), d_key);
    if (d_value != NULL) {
        if (both) {
            PyObject *o = PyObject_Str(d_key);
            if (o == NULL)
                d_value = NULL;
            else {
                d_value = PyText_FromFormat("%s: %s",
                                            PyText_AS_UTF8(o),
                                            PyText_AS_UTF8(d_value));
                Py_DECREF(o);
            }
        }
        else
            Py_INCREF(d_value);
    }
    else
        d_value = PyObject_Str(d_key);
    Py_DECREF(d_key);
    return d_value;
}

static PyObject *cdata_repr(CDataObject *cd)
{
    char *extra;
    PyObject *result, *s;

    if (cd->c_type->ct_flags & CT_PRIMITIVE_ANY) {
        if (cd->c_type->ct_flags & CT_IS_ENUM) {
            s = convert_cdata_to_enum_string(cd, 1);
        }
        else if (cd->c_type->ct_flags & CT_IS_LONGDOUBLE) {
            long double lvalue;
            char buffer[128];   /* big enough */
            /*READ(cd->c_data, sizeof(long double)*/
            lvalue = read_raw_longdouble_data(cd->c_data);
            sprintf(buffer, "%LE", lvalue);
            s = PyText_FromString(buffer);
        }
        else {
            PyObject *o = convert_to_object(cd->c_data, cd->c_type);
            if (o == NULL)
                return NULL;
            s = PyObject_Repr(o);
            Py_DECREF(o);
        }
    }
    else if ((cd->c_type->ct_flags & CT_ARRAY) && cd->c_type->ct_length < 0) {
        s = PyText_FromFormat("sliced length %zd", get_array_length(cd));
    }
    else {
        if (cd->c_data != NULL) {
            s = PyText_FromFormat("%p", cd->c_data);
        }
        else
            s = PyText_FromString("NULL");
    }
    if (s == NULL)
        return NULL;
    /* it's slightly confusing to get "<cdata 'struct foo' 0x...>" because the
       struct foo is not owned.  Trying to make it clearer, write in this
       case "<cdata 'struct foo &' 0x...>". */
    if (cd->c_type->ct_flags & (CT_STRUCT|CT_UNION))
        extra = " &";
    else
        extra = "";
    result = PyText_FromFormat("<cdata '%s%s' %s>",
                               cd->c_type->ct_name, extra,
                               PyText_AsUTF8(s));
    Py_DECREF(s);
    return result;
}

static PyObject *_cdata_repr2(CDataObject *cd, char *text, PyObject *x)
{
    PyObject *res, *s = PyObject_Repr(x);
    if (s == NULL)
        return NULL;
    res = PyText_FromFormat("<cdata '%s' %s %s>",
                            cd->c_type->ct_name, text, PyText_AsUTF8(s));
    Py_DECREF(s);
    return res;
}

static PyObject *cdataowning_repr(CDataObject *cd)
{
    Py_ssize_t size;
    if (cd->c_type->ct_flags & CT_POINTER)
        size = cd->c_type->ct_itemdescr->ct_size;
    else if (cd->c_type->ct_flags & CT_ARRAY)
        size = get_array_length(cd) * cd->c_type->ct_itemdescr->ct_size;
    else
        size = cd->c_type->ct_size;

    return PyText_FromFormat("<cdata '%s' owning %zd bytes>",
                             cd->c_type->ct_name, size);
}

static PyObject *cdataowninggc_repr(CDataObject *cd)
{
    if (cd->c_type->ct_flags & CT_IS_VOID_PTR) {        /* a handle */
        PyObject *x = ((CDataObject_own_structptr *)cd)->structobj;
        return _cdata_repr2(cd, "handle to", x);
    }
    else if (cd->c_type->ct_flags & CT_FUNCTIONPTR) {   /* a callback */
        PyObject *args = (PyObject *)((ffi_closure *)cd->c_data)->user_data;
        if (args == NULL)
            return cdata_repr(cd);
        else
            return _cdata_repr2(cd, "calling", PyTuple_GET_ITEM(args, 1));
    }
    else if (cd->c_type->ct_flags & CT_IS_UNSIZED_CHAR_A) {  /* from_buffer */
        Py_buffer *view = ((CDataObject_owngc_frombuf *)cd)->bufferview;
        Py_ssize_t buflen = get_array_length(cd);
        return PyText_FromFormat(
            "<cdata '%s' buffer len %zd from '%.200s' object>",
            cd->c_type->ct_name,
            buflen,
            view->obj ? Py_TYPE(view->obj)->tp_name : "(null)");
    }
    return cdataowning_repr(cd);
}

static int cdata_nonzero(CDataObject *cd)
{
    return cd->c_data != NULL;
}

static PyObject *cdata_int(CDataObject *cd)
{
    if ((cd->c_type->ct_flags & (CT_PRIMITIVE_SIGNED|CT_PRIMITIVE_FITS_LONG))
                             == (CT_PRIMITIVE_SIGNED|CT_PRIMITIVE_FITS_LONG)) {
        /* this case is to handle enums, but also serves as a slight
           performance improvement for some other primitive types */
        long value;
        /*READ(cd->c_data, cd->c_type->ct_size)*/
        value = (long)read_raw_signed_data(cd->c_data, cd->c_type->ct_size);
        return PyInt_FromLong(value);
    }
    if (cd->c_type->ct_flags & (CT_PRIMITIVE_SIGNED|CT_PRIMITIVE_UNSIGNED)) {
        return convert_to_object(cd->c_data, cd->c_type);
    }
    else if (cd->c_type->ct_flags & CT_PRIMITIVE_CHAR) {
        /*READ(cd->c_data, cd->c_type->ct_size)*/
        if (cd->c_type->ct_size == sizeof(char))
            return PyInt_FromLong((unsigned char)cd->c_data[0]);
#ifdef HAVE_WCHAR_H
        else
            return PyInt_FromLong((long)*(wchar_t *)cd->c_data);
#endif
    }
    else if (cd->c_type->ct_flags & CT_PRIMITIVE_FLOAT) {
        PyObject *o = cdata_float(cd);
#if PY_MAJOR_VERSION < 3
        PyObject *r = o ? PyNumber_Int(o) : NULL;
#else
        PyObject *r = o ? PyNumber_Long(o) : NULL;
#endif
        Py_XDECREF(o);
        return r;
    }
    PyErr_Format(PyExc_TypeError, "int() not supported on cdata '%s'",
                 cd->c_type->ct_name);
    return NULL;
}

#if PY_MAJOR_VERSION < 3
static PyObject *cdata_long(CDataObject *cd)
{
    PyObject *res = cdata_int(cd);
    if (res != NULL && PyInt_CheckExact(res)) {
        PyObject *o = PyLong_FromLong(PyInt_AS_LONG(res));
        Py_DECREF(res);
        res = o;
    }
    return res;
}
#endif

static PyObject *cdata_float(CDataObject *cd)
{
    if (cd->c_type->ct_flags & CT_PRIMITIVE_FLOAT) {
        double value;
        /*READ(cd->c_data, cd->c_type->ct_size)*/
        if (!(cd->c_type->ct_flags & CT_IS_LONGDOUBLE)) {
            value = read_raw_float_data(cd->c_data, cd->c_type->ct_size);
        }
        else {
            value = (double)read_raw_longdouble_data(cd->c_data);
        }
        return PyFloat_FromDouble(value);
    }
    PyErr_Format(PyExc_TypeError, "float() not supported on cdata '%s'",
                 cd->c_type->ct_name);
    return NULL;
}

static PyObject *cdata_richcompare(PyObject *v, PyObject *w, int op)
{
    int res;
    PyObject *pyres;
    char *v_cdata, *w_cdata;

    assert(CData_Check(v));
    if (!CData_Check(w)) {
        pyres = Py_NotImplemented;
        goto done;
    }

    if ((op != Py_EQ && op != Py_NE) &&
        ((((CDataObject *)v)->c_type->ct_flags & CT_PRIMITIVE_ANY) ||
         (((CDataObject *)w)->c_type->ct_flags & CT_PRIMITIVE_ANY)))
        goto Error;

    v_cdata = ((CDataObject *)v)->c_data;
    w_cdata = ((CDataObject *)w)->c_data;

    switch (op) {
    case Py_EQ: res = (v_cdata == w_cdata); break;
    case Py_NE: res = (v_cdata != w_cdata); break;
    case Py_LT: res = (v_cdata <  w_cdata); break;
    case Py_LE: res = (v_cdata <= w_cdata); break;
    case Py_GT: res = (v_cdata >  w_cdata); break;
    case Py_GE: res = (v_cdata >= w_cdata); break;
    default: res = -1;
    }
    pyres = res ? Py_True : Py_False;
 done:
    Py_INCREF(pyres);
    return pyres;

 Error:
    PyErr_SetString(PyExc_TypeError,
                    "cannot do comparison on a primitive cdata");
    return NULL;
}

static long cdata_hash(CDataObject *cd)
{
    return _Py_HashPointer(cd->c_data);
}

static Py_ssize_t
cdata_length(CDataObject *cd)
{
    if (cd->c_type->ct_flags & CT_ARRAY) {
        return get_array_length(cd);
    }
    PyErr_Format(PyExc_TypeError, "cdata of type '%s' has no len()",
                 cd->c_type->ct_name);
    return -1;
}

static char *
_cdata_get_indexed_ptr(CDataObject *cd, PyObject *key)
{
    Py_ssize_t i = PyNumber_AsSsize_t(key, PyExc_IndexError);
    if (i == -1 && PyErr_Occurred())
        return NULL;

    if (cd->c_type->ct_flags & CT_POINTER) {
        if (CDataOwn_Check(cd)) {
            if (i != 0) {
                PyErr_Format(PyExc_IndexError,
                             "cdata '%s' can only be indexed by 0",
                             cd->c_type->ct_name);
                return NULL;
            }
        }
        else {
            if (cd->c_data == NULL) {
                PyErr_Format(PyExc_RuntimeError,
                             "cannot dereference null pointer from cdata '%s'",
                             cd->c_type->ct_name);
                return NULL;
            }
        }
    }
    else if (cd->c_type->ct_flags & CT_ARRAY) {
        if (i < 0) {
            PyErr_SetString(PyExc_IndexError,
                            "negative index not supported");
            return NULL;
        }
        if (i >= get_array_length(cd)) {
            PyErr_Format(PyExc_IndexError,
                         "index too large for cdata '%s' (expected %zd < %zd)",
                         cd->c_type->ct_name,
                         i, get_array_length(cd));
            return NULL;
        }
    }
    else {
        PyErr_Format(PyExc_TypeError, "cdata of type '%s' cannot be indexed",
                     cd->c_type->ct_name);
        return NULL;
    }
    return cd->c_data + i * cd->c_type->ct_itemdescr->ct_size;
}

static PyObject *
new_array_type(CTypeDescrObject *ctptr, Py_ssize_t length);   /* forward */

static CTypeDescrObject *
_cdata_getslicearg(CDataObject *cd, PySliceObject *slice, Py_ssize_t bounds[])
{
    Py_ssize_t start, stop;
    CTypeDescrObject *ct;

    start = PyInt_AsSsize_t(slice->start);
    if (start == -1 && PyErr_Occurred()) {
        if (slice->start == Py_None)
            PyErr_SetString(PyExc_IndexError, "slice start must be specified");
        return NULL;
    }
    stop = PyInt_AsSsize_t(slice->stop);
    if (stop == -1 && PyErr_Occurred()) {
        if (slice->stop == Py_None)
            PyErr_SetString(PyExc_IndexError, "slice stop must be specified");
        return NULL;
    }
    if (slice->step != Py_None) {
        PyErr_SetString(PyExc_IndexError, "slice with step not supported");
        return NULL;
    }
    if (start > stop) {
        PyErr_SetString(PyExc_IndexError, "slice start > stop");
        return NULL;
    }

    ct = cd->c_type;
    if (ct->ct_flags & CT_ARRAY) {
        if (start < 0) {
            PyErr_SetString(PyExc_IndexError,
                            "negative index not supported");
            return NULL;
        }
        if (stop > get_array_length(cd)) {
            PyErr_Format(PyExc_IndexError,
                         "index too large (expected %zd <= %zd)",
                         stop, get_array_length(cd));
            return NULL;
        }
        ct = (CTypeDescrObject *)ct->ct_stuff;
    }
    else if (!(ct->ct_flags & CT_POINTER)) {
        PyErr_Format(PyExc_TypeError, "cdata of type '%s' cannot be indexed",
                     ct->ct_name);
        return NULL;
    }

    bounds[0] = start;
    bounds[1] = stop - start;
    return ct;
}

static PyObject *
cdata_slice(CDataObject *cd, PySliceObject *slice)
{
    Py_ssize_t bounds[2];
    CDataObject_own_length *scd;
    CTypeDescrObject *ct = _cdata_getslicearg(cd, slice, bounds);
    if (ct == NULL)
        return NULL;

    if (ct->ct_stuff == NULL) {
        ct->ct_stuff = new_array_type(ct, -1);
        if (ct->ct_stuff == NULL)
            return NULL;
    }
    ct = (CTypeDescrObject *)ct->ct_stuff;

    scd = (CDataObject_own_length *)PyObject_Malloc(
              offsetof(CDataObject_own_length, alignment));
    if (PyObject_Init((PyObject *)scd, &CData_Type) == NULL)
        return NULL;
    Py_INCREF(ct);
    scd->head.c_type = ct;
    scd->head.c_data = cd->c_data + ct->ct_itemdescr->ct_size * bounds[0];
    scd->head.c_weakreflist = NULL;
    scd->length = bounds[1];
    return (PyObject *)scd;
}

static int
cdata_ass_slice(CDataObject *cd, PySliceObject *slice, PyObject *v)
{
    Py_ssize_t bounds[2], i, length, itemsize;
    PyObject *it, *item;
    PyObject *(*iternext)(PyObject *);
    char *cdata;
    int err;
    CTypeDescrObject *ct = _cdata_getslicearg(cd, slice, bounds);
    if (ct == NULL)
        return -1;
    ct = ct->ct_itemdescr;
    itemsize = ct->ct_size;
    cdata = cd->c_data + itemsize * bounds[0];
    length = bounds[1];

    if (CData_Check(v)) {
        CTypeDescrObject *ctv = ((CDataObject *)v)->c_type;
        if ((ctv->ct_flags & CT_ARRAY) && (ctv->ct_itemdescr == ct) &&
            (get_array_length((CDataObject *)v) == length)) {
            /* fast path: copying from exactly the correct type */
            memmove(cdata, ((CDataObject *)v)->c_data, itemsize * length);
            return 0;
        }
    }

    /* A fast path for <char[]>[0:N] = b"somestring", which also adds
       support for Python 3: otherwise, you get integers while enumerating
       the string, and you can't set them to characters :-/
    */
    if (PyBytes_Check(v) && (ct->ct_flags & CT_PRIMITIVE_CHAR)
            && itemsize == sizeof(char)) {
        if (PyBytes_GET_SIZE(v) != length) {
            PyErr_Format(PyExc_ValueError,
                         "need a string of length %zd, got %zd",
                         length, PyBytes_GET_SIZE(v));
            return -1;
        }
        memcpy(cdata, PyBytes_AS_STRING(v), length);
        return 0;
    }

    it = PyObject_GetIter(v);
    if (it == NULL)
        return -1;
    iternext = *it->ob_type->tp_iternext;

    for (i = 0; i < length; i++) {
        item = iternext(it);
        if (item == NULL) {
            if (!PyErr_Occurred())
                PyErr_Format(PyExc_ValueError,
                             "need %zd values to unpack, got %zd",
                             length, i);
            goto error;
        }
        err = convert_from_object(cdata, ct, item);
        Py_DECREF(item);
        if (err < 0)
            goto error;

        cdata += itemsize;
    }
    item = iternext(it);
    if (item != NULL) {
        Py_DECREF(item);
        PyErr_Format(PyExc_ValueError,
                     "got more than %zd values to unpack", length);
    }
 error:
    Py_DECREF(it);
    return PyErr_Occurred() ? -1 : 0;
}

static PyObject *
cdataowning_subscript(CDataObject *cd, PyObject *key)
{
    char *c;
    if (PySlice_Check(key))
        return cdata_slice(cd, (PySliceObject *)key);

    c = _cdata_get_indexed_ptr(cd, key);
    /* use 'mp_subscript' instead of 'sq_item' because we don't want
       negative indexes to be corrected automatically */
    if (c == NULL && PyErr_Occurred())
        return NULL;

    if (cd->c_type->ct_flags & CT_IS_PTR_TO_OWNED) {
        PyObject *res = ((CDataObject_own_structptr *)cd)->structobj;
        Py_INCREF(res);
        return res;
    }
    else {
        return convert_to_object(c, cd->c_type->ct_itemdescr);
    }
}

static PyObject *
cdata_subscript(CDataObject *cd, PyObject *key)
{
    char *c;
    if (PySlice_Check(key))
        return cdata_slice(cd, (PySliceObject *)key);

    c = _cdata_get_indexed_ptr(cd, key);
    /* use 'mp_subscript' instead of 'sq_item' because we don't want
       negative indexes to be corrected automatically */
    if (c == NULL && PyErr_Occurred())
        return NULL;
    return convert_to_object(c, cd->c_type->ct_itemdescr);
}

static int
cdata_ass_sub(CDataObject *cd, PyObject *key, PyObject *v)
{
    char *c;
    CTypeDescrObject *ctitem;
    if (PySlice_Check(key))
        return cdata_ass_slice(cd, (PySliceObject *)key, v);

    c = _cdata_get_indexed_ptr(cd, key);
    ctitem = cd->c_type->ct_itemdescr;
    /* use 'mp_ass_subscript' instead of 'sq_ass_item' because we don't want
       negative indexes to be corrected automatically */
    if (c == NULL && PyErr_Occurred())
        return -1;
    if (v == NULL) {
        PyErr_SetString(PyExc_TypeError,
                        "'del x[n]' not supported for cdata objects");
        return -1;
    }
    return convert_from_object(c, ctitem, v);
}

static PyObject *
_cdata_add_or_sub(PyObject *v, PyObject *w, int sign)
{
    Py_ssize_t i, itemsize;
    CDataObject *cd;
    CTypeDescrObject *ctptr;

    if (!CData_Check(v)) {
        PyObject *swap;
        assert(CData_Check(w));
        if (sign != 1)
            goto not_implemented;
        swap = v;
        v = w;
        w = swap;
    }

    i = PyNumber_AsSsize_t(w, PyExc_OverflowError);
    if (i == -1 && PyErr_Occurred())
        return NULL;
    i *= sign;

    cd = (CDataObject *)v;
    if (cd->c_type->ct_flags & CT_POINTER)
        ctptr = cd->c_type;
    else if (cd->c_type->ct_flags & CT_ARRAY) {
        ctptr = (CTypeDescrObject *)cd->c_type->ct_stuff;
    }
    else {
        PyErr_Format(PyExc_TypeError, "cannot add a cdata '%s' and a number",
                     cd->c_type->ct_name);
        return NULL;
    }
    itemsize = ctptr->ct_itemdescr->ct_size;
    if (itemsize < 0) {
        if (ctptr->ct_flags & CT_IS_VOID_PTR) {
            itemsize = 1;
        }
        else {
            PyErr_Format(PyExc_TypeError,
                         "ctype '%s' points to items of unknown size",
                         cd->c_type->ct_name);
            return NULL;
        }
    }
    return new_simple_cdata(cd->c_data + i * itemsize, ctptr);

 not_implemented:
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
}

static PyObject *
cdata_add(PyObject *v, PyObject *w)
{
    return _cdata_add_or_sub(v, w, +1);
}

static PyObject *
cdata_sub(PyObject *v, PyObject *w)
{
    if (CData_Check(v) && CData_Check(w)) {
        CDataObject *cdv = (CDataObject *)v;
        CDataObject *cdw = (CDataObject *)w;
        CTypeDescrObject *ct = cdw->c_type;
        Py_ssize_t diff, itemsize;

        if (ct->ct_flags & CT_ARRAY)     /* ptr_to_T - array_of_T: ok */
            ct = (CTypeDescrObject *)ct->ct_stuff;

        if (ct != cdv->c_type || !(ct->ct_flags & CT_POINTER) ||
                (ct->ct_itemdescr->ct_size <= 0 &&
                 !(ct->ct_flags & CT_IS_VOID_PTR))) {
            PyErr_Format(PyExc_TypeError,
                         "cannot subtract cdata '%s' and cdata '%s'",
                         cdv->c_type->ct_name, ct->ct_name);
            return NULL;
        }
        itemsize = ct->ct_itemdescr->ct_size;
        if (itemsize <= 0) itemsize = 1;
        diff = (cdv->c_data - cdw->c_data) / itemsize;
#if PY_MAJOR_VERSION < 3
        return PyInt_FromSsize_t(diff);
#else
        return PyLong_FromSsize_t(diff);
#endif
    }

    return _cdata_add_or_sub(v, w, -1);
}

static PyObject *
cdata_getattro(CDataObject *cd, PyObject *attr)
{
    CFieldObject *cf;
    CTypeDescrObject *ct = cd->c_type;

    if (ct->ct_flags & CT_POINTER)
        ct = ct->ct_itemdescr;

    if (ct->ct_flags & (CT_STRUCT|CT_UNION)) {
        switch (force_lazy_struct(ct)) {
        case 1:
            cf = (CFieldObject *)PyDict_GetItem(ct->ct_stuff, attr);
            if (cf != NULL) {
                /* read the field 'cf' */
                char *data = cd->c_data + cf->cf_offset;
                if (cf->cf_bitshift == BS_REGULAR)
                    return convert_to_object(data, cf->cf_type);
                else if (cf->cf_bitshift == BS_EMPTY_ARRAY)
                    return new_simple_cdata(data,
                        (CTypeDescrObject *)cf->cf_type->ct_stuff);
                else
                    return convert_to_object_bitfield(data, cf);
            }
            break;
        case -1:
            return NULL;
        default:
            break;
        }
    }
    return PyObject_GenericGetAttr((PyObject *)cd, attr);
}

static int
cdata_setattro(CDataObject *cd, PyObject *attr, PyObject *value)
{
    CFieldObject *cf;
    CTypeDescrObject *ct = cd->c_type;

    if (ct->ct_flags & CT_POINTER)
        ct = ct->ct_itemdescr;

    if (ct->ct_flags & (CT_STRUCT|CT_UNION)) {
        switch (force_lazy_struct(ct)) {
        case 1:
            cf = (CFieldObject *)PyDict_GetItem(ct->ct_stuff, attr);
            if (cf != NULL) {
                /* write the field 'cf' */
                if (value != NULL) {
                    return convert_field_from_object(cd->c_data, cf, value);
                }
                else {
                    PyErr_SetString(PyExc_AttributeError,
                                    "cannot delete struct field");
                    return -1;
                }
            }
            break;
        case -1:
            return -1;
        default:
            break;
        }
    }
    return PyObject_GenericSetAttr((PyObject *)cd, attr, value);
}

static PyObject *
convert_struct_to_owning_object(char *data, CTypeDescrObject *ct); /*forward*/

static cif_description_t *
fb_prepare_cif(PyObject *fargs, CTypeDescrObject *, ffi_abi);      /*forward*/

static PyObject *new_primitive_type(const char *name);             /*forward*/

static CTypeDescrObject *_get_ct_int(void)
{
    static CTypeDescrObject *ct_int = NULL;
    if (ct_int == NULL) {
        ct_int = (CTypeDescrObject *)new_primitive_type("int");
    }
    return ct_int;
}

static Py_ssize_t
_prepare_pointer_call_argument(CTypeDescrObject *ctptr, PyObject *init,
                               char **output_data)
{
    /* 'ctptr' is here a pointer type 'ITEM *'.  Accept as argument an
       initializer for an array 'ITEM[]'.  This includes the case of
       passing a Python byte string to a 'char *' argument.

       This function returns -1 if an error occurred,
       0 if conversion succeeded (into *output_data),
       or N > 0 if conversion would require N bytes of storage.
    */
    Py_ssize_t length, datasize;
    CTypeDescrObject *ctitem;

    if (CData_Check(init))
        goto convert_default;

    ctitem = ctptr->ct_itemdescr;
    /* XXX some code duplication, how to avoid it? */
    if (PyBytes_Check(init)) {
        /* from a string: just returning the string here is fine.
           We assume that the C code won't modify the 'char *' data. */
        if ((ctptr->ct_flags & CT_CAST_ANYTHING) ||
            ((ctitem->ct_flags & (CT_PRIMITIVE_SIGNED|CT_PRIMITIVE_UNSIGNED))
             && (ctitem->ct_size == sizeof(char)))) {
#if defined(CFFI_MEM_DEBUG) || defined(CFFI_MEM_LEAK)
            length = PyBytes_GET_SIZE(init) + 1;
#else
            *output_data = PyBytes_AS_STRING(init);
            return 0;
#endif
        }
        else
            goto convert_default;
    }
    else if (PyList_Check(init) || PyTuple_Check(init)) {
        length = PySequence_Fast_GET_SIZE(init);
    }
    else if (PyUnicode_Check(init)) {
        /* from a unicode, we add the null terminator */
        length = _my_PyUnicode_SizeAsWideChar(init) + 1;
    }
    else if ((ctitem->ct_flags & CT_IS_FILE) && PyFile_Check(init)) {
        *output_data = (char *)PyFile_AsFile(init);
        if (*output_data == NULL && PyErr_Occurred())
            return -1;
        return 0;
    }
    else {
        /* refuse to receive just an integer (and interpret it
           as the array size) */
        goto convert_default;
    }

    if (ctitem->ct_size <= 0)
        goto convert_default;
    datasize = length * ctitem->ct_size;
    if ((datasize / ctitem->ct_size) != length) {
        PyErr_SetString(PyExc_OverflowError,
                        "array size would overflow a Py_ssize_t");
        return -1;
    }
    if (datasize <= 0)
        datasize = 1;
    return datasize;

 convert_default:
    return convert_from_object((char *)output_data, ctptr, init);
}

static PyObject*
cdata_call(CDataObject *cd, PyObject *args, PyObject *kwds)
{
    char *buffer;
    void** buffer_array;
    cif_description_t *cif_descr;
    Py_ssize_t i, nargs, nargs_declared;
    PyObject *signature, *res = NULL, *fvarargs;
    CTypeDescrObject *fresult;
    char *resultdata;
    char *errormsg;

    if (!(cd->c_type->ct_flags & CT_FUNCTIONPTR)) {
        PyErr_Format(PyExc_TypeError, "cdata '%s' is not callable",
                     cd->c_type->ct_name);
        return NULL;
    }
    if (kwds != NULL && PyDict_Size(kwds) != 0) {
        PyErr_SetString(PyExc_TypeError,
                "a cdata function cannot be called with keyword arguments");
        return NULL;
    }
    signature = cd->c_type->ct_stuff;
    nargs = PyTuple_Size(args);
    if (nargs < 0)
        return NULL;
    nargs_declared = PyTuple_GET_SIZE(signature) - 2;
    fresult = (CTypeDescrObject *)PyTuple_GET_ITEM(signature, 1);
    fvarargs = NULL;
    buffer = NULL;

    cif_descr = (cif_description_t *)cd->c_type->ct_extra;

    if (cif_descr != NULL) {
        /* regular case: this function does not take '...' arguments */
        if (nargs != nargs_declared) {
            errormsg = "'%s' expects %zd arguments, got %zd";
          bad_number_of_arguments:
            PyErr_Format(PyExc_TypeError, errormsg,
                         cd->c_type->ct_name, nargs_declared, nargs);
            goto error;
        }
    }
    else {
        /* call of a variadic function */
        ffi_abi fabi;
        if (nargs < nargs_declared) {
            errormsg = "'%s' expects at least %zd arguments, got %zd";
            goto bad_number_of_arguments;
        }
        fvarargs = PyTuple_New(nargs);
        if (fvarargs == NULL)
            goto error;
        for (i = 0; i < nargs_declared; i++) {
            PyObject *o = PyTuple_GET_ITEM(signature, 2 + i);
            Py_INCREF(o);
            PyTuple_SET_ITEM(fvarargs, i, o);
        }
        for (i = nargs_declared; i < nargs; i++) {
            PyObject *obj = PyTuple_GET_ITEM(args, i);
            CTypeDescrObject *ct;

            if (CData_Check(obj)) {
                ct = ((CDataObject *)obj)->c_type;
                if (ct->ct_flags & (CT_PRIMITIVE_CHAR | CT_PRIMITIVE_UNSIGNED |
                                    CT_PRIMITIVE_SIGNED)) {
                    if (ct->ct_size < (Py_ssize_t)sizeof(int)) {
                        ct = _get_ct_int();
                        if (ct == NULL)
                            goto error;
                    }
                }
                else if (ct->ct_flags & CT_ARRAY) {
                    ct = (CTypeDescrObject *)ct->ct_stuff;
                }
                Py_INCREF(ct);
            }
            else {
                PyErr_Format(PyExc_TypeError,
                             "argument %zd passed in the variadic part "
                             "needs to be a cdata object (got %.200s)",
                             i + 1, Py_TYPE(obj)->tp_name);
                goto error;
            }
            PyTuple_SET_ITEM(fvarargs, i, (PyObject *)ct);
        }
#if PY_MAJOR_VERSION < 3
        fabi = PyInt_AS_LONG(PyTuple_GET_ITEM(signature, 0));
#else
        fabi = PyLong_AS_LONG(PyTuple_GET_ITEM(signature, 0));
#endif
        cif_descr = fb_prepare_cif(fvarargs, fresult, fabi);
        if (cif_descr == NULL)
            goto error;
    }

    buffer = PyObject_Malloc(cif_descr->exchange_size);
    if (buffer == NULL) {
        PyErr_NoMemory();
        goto error;
    }

    buffer_array = (void **)buffer;

    for (i=0; i<nargs; i++) {
        CTypeDescrObject *argtype;
        char *data = buffer + cif_descr->exchange_offset_arg[1 + i];
        PyObject *obj = PyTuple_GET_ITEM(args, i);

        buffer_array[i] = data;

        if (i < nargs_declared)
            argtype = (CTypeDescrObject *)PyTuple_GET_ITEM(signature, 2 + i);
        else
            argtype = (CTypeDescrObject *)PyTuple_GET_ITEM(fvarargs, i);

        if (argtype->ct_flags & CT_POINTER) {
            char *tmpbuf;
            Py_ssize_t datasize = _prepare_pointer_call_argument(
                                            argtype, obj, (char **)data);
            if (datasize == 0)
                ;    /* successfully filled '*data' */
            else if (datasize < 0)
                goto error;
            else {
                tmpbuf = alloca(datasize);
                memset(tmpbuf, 0, datasize);
                *(char **)data = tmpbuf;
                if (convert_array_from_object(tmpbuf, argtype, obj) < 0)
                    goto error;
            }
        }
        else if (convert_from_object(data, argtype, obj) < 0)
            goto error;
    }

    resultdata = buffer + cif_descr->exchange_offset_arg[0];
    /*READ(cd->c_data, sizeof(void(*)(void)))*/

    Py_BEGIN_ALLOW_THREADS
    restore_errno();
    ffi_call(&cif_descr->cif, (void (*)(void))(cd->c_data),
             resultdata, buffer_array);
    save_errno();
    Py_END_ALLOW_THREADS

    if (fresult->ct_flags & (CT_PRIMITIVE_CHAR | CT_PRIMITIVE_SIGNED |
                             CT_PRIMITIVE_UNSIGNED)) {
#ifdef WORDS_BIGENDIAN
        /* For results of precisely these types, libffi has a strange
           rule that they will be returned as a whole 'ffi_arg' if they
           are smaller.  The difference only matters on big-endian. */
        if (fresult->ct_size < sizeof(ffi_arg))
            resultdata += (sizeof(ffi_arg) - fresult->ct_size);
#endif
        res = convert_to_object(resultdata, fresult);
    }
    else if (fresult->ct_flags & CT_VOID) {
        res = Py_None;
        Py_INCREF(res);
    }
    else if (fresult->ct_flags & CT_STRUCT) {
        res = convert_struct_to_owning_object(resultdata, fresult);
    }
    else {
        res = convert_to_object(resultdata, fresult);
    }
    /* fall-through */

 error:
    if (buffer)
        PyObject_Free(buffer);
    if (fvarargs != NULL) {
        Py_DECREF(fvarargs);
        if (cif_descr != NULL)  /* but only if fvarargs != NULL, if variadic */
            PyObject_Free(cif_descr);
    }
    return res;
}

static PyObject *cdata_iter(CDataObject *);

static PyNumberMethods CData_as_number = {
    (binaryfunc)cdata_add,      /*nb_add*/
    (binaryfunc)cdata_sub,      /*nb_subtract*/
    0,                          /*nb_multiply*/
#if PY_MAJOR_VERSION < 3
    0,                          /*nb_divide*/
#endif
    0,                          /*nb_remainder*/
    0,                          /*nb_divmod*/
    0,                          /*nb_power*/
    0,                          /*nb_negative*/
    0,                          /*nb_positive*/
    0,                          /*nb_absolute*/
    (inquiry)cdata_nonzero,     /*nb_nonzero*/
    0,                          /*nb_invert*/
    0,                          /*nb_lshift*/
    0,                          /*nb_rshift*/
    0,                          /*nb_and*/
    0,                          /*nb_xor*/
    0,                          /*nb_or*/
#if PY_MAJOR_VERSION < 3
    0,                          /*nb_coerce*/
#endif
    (unaryfunc)cdata_int,       /*nb_int*/
#if PY_MAJOR_VERSION < 3
    (unaryfunc)cdata_long,      /*nb_long*/
#else
    0,
#endif
    (unaryfunc)cdata_float,     /*nb_float*/
    0,                          /*nb_oct*/
    0,                          /*nb_hex*/
};

static PyMappingMethods CData_as_mapping = {
    (lenfunc)cdata_length, /*mp_length*/
    (binaryfunc)cdata_subscript, /*mp_subscript*/
    (objobjargproc)cdata_ass_sub, /*mp_ass_subscript*/
};

static PyMappingMethods CDataOwn_as_mapping = {
    (lenfunc)cdata_length, /*mp_length*/
    (binaryfunc)cdataowning_subscript, /*mp_subscript*/
    (objobjargproc)cdata_ass_sub, /*mp_ass_subscript*/
};

static PyTypeObject CData_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.CData",
    sizeof(CDataObject),
    0,
    (destructor)cdata_dealloc,                  /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    (reprfunc)cdata_repr,                       /* tp_repr */
    &CData_as_number,                           /* tp_as_number */
    0,                                          /* tp_as_sequence */
    &CData_as_mapping,                          /* tp_as_mapping */
    (hashfunc)cdata_hash,                       /* tp_hash */
    (ternaryfunc)cdata_call,                    /* tp_call */
    0,                                          /* tp_str */
    (getattrofunc)cdata_getattro,               /* tp_getattro */
    (setattrofunc)cdata_setattro,               /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES, /* tp_flags */
    0,                                          /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    cdata_richcompare,                          /* tp_richcompare */
    offsetof(CDataObject, c_weakreflist),       /* tp_weaklistoffset */
    (getiterfunc)cdata_iter,                    /* tp_iter */
    0,                                          /* tp_iternext */
};

static PyTypeObject CDataOwning_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.CDataOwn",
    sizeof(CDataObject),
    0,
    (destructor)cdataowning_dealloc,            /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    (reprfunc)cdataowning_repr,                 /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    &CDataOwn_as_mapping,                       /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES, /* tp_flags */
    0,                                          /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    &CData_Type,                                /* tp_base */
};

static PyTypeObject CDataOwningGC_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.CDataOwnGC",
    sizeof(CDataObject_owngc_frombuf),
    0,
    (destructor)cdataowninggc_dealloc,          /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    (reprfunc)cdataowninggc_repr,               /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES  /* tp_flags */
                       | Py_TPFLAGS_HAVE_GC,
    0,                                          /* tp_doc */
    (traverseproc)cdataowninggc_traverse,       /* tp_traverse */
    (inquiry)cdataowninggc_clear,               /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    &CDataOwning_Type,                          /* tp_base */
};

static PyTypeObject CDataGCP_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.CDataGCP",
    sizeof(CDataObject_gcp),
    0,
    (destructor)cdatagcp_dealloc,               /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_CHECKTYPES  /* tp_flags */
#ifdef Py_TPFLAGS_HAVE_FINALIZE
                       | Py_TPFLAGS_HAVE_FINALIZE
#endif
                       | Py_TPFLAGS_HAVE_GC,
    0,                                          /* tp_doc */
    (traverseproc)cdatagcp_traverse,            /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    &CData_Type,                                /* tp_base */
#ifdef Py_TPFLAGS_HAVE_FINALIZE  /* CPython >= 3.4 */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    0,                                          /* tp_new */
    0,                                          /* tp_free */
    0,                                          /* tp_is_gc */
    0,                                          /* tp_bases */
    0,                                          /* tp_mro */
    0,                                          /* tp_cache */
    0,                                          /* tp_subclasses */
    0,                                          /* tp_weaklist */
    0,                                          /* tp_del */
    0,                                          /* version_tag */
    (destructor)cdatagcp_finalize,              /* tp_finalize */
#endif
};

/************************************************************/

typedef struct {
    PyObject_HEAD
    char *di_next, *di_stop;
    CDataObject *di_object;
    CTypeDescrObject *di_itemtype;
} CDataIterObject;

static PyObject *
cdataiter_next(CDataIterObject *it)
{
    char *result = it->di_next;
    if (result != it->di_stop) {
        it->di_next = result + it->di_itemtype->ct_size;
        return convert_to_object(result, it->di_itemtype);
    }
    return NULL;
}

static void
cdataiter_dealloc(CDataIterObject *it)
{
    Py_DECREF(it->di_object);
    PyObject_Del(it);
}

static PyTypeObject CDataIter_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.CDataIter",              /* tp_name */
    sizeof(CDataIterObject),                /* tp_basicsize */
    0,                                      /* tp_itemsize */
    /* methods */
    (destructor)cdataiter_dealloc,          /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_compare */
    0,                                      /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    PyObject_GenericGetAttr,                /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                     /* tp_flags */
    0,                                      /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    PyObject_SelfIter,                      /* tp_iter */
    (iternextfunc)cdataiter_next,           /* tp_iternext */
};

static PyObject *
cdata_iter(CDataObject *cd)
{
    CDataIterObject *it;

    if (!(cd->c_type->ct_flags & CT_ARRAY)) {
        PyErr_Format(PyExc_TypeError, "cdata '%s' does not support iteration",
                     cd->c_type->ct_name);
        return NULL;
    }

    it = PyObject_New(CDataIterObject, &CDataIter_Type);
    if (it == NULL)
        return NULL;

    Py_INCREF(cd);
    it->di_object = cd;
    it->di_itemtype = cd->c_type->ct_itemdescr;
    it->di_next = cd->c_data;
    it->di_stop = cd->c_data + get_array_length(cd) * it->di_itemtype->ct_size;
    return (PyObject *)it;
}

/************************************************************/

static CDataObject *allocate_owning_object(Py_ssize_t size,
                                           CTypeDescrObject *ct)
{
    CDataObject *cd;
    cd = (CDataObject *)PyObject_Malloc(size);
    if (PyObject_Init((PyObject *)cd, &CDataOwning_Type) == NULL)
        return NULL;

    Py_INCREF(ct);
    cd->c_type = ct;
    cd->c_weakreflist = NULL;
    return cd;
}

static PyObject *
convert_struct_to_owning_object(char *data, CTypeDescrObject *ct)
{
    CDataObject *cd;
    Py_ssize_t dataoffset = offsetof(CDataObject_own_nolength, alignment);
    Py_ssize_t datasize = ct->ct_size;

    if ((ct->ct_flags & (CT_STRUCT|CT_IS_OPAQUE)) != CT_STRUCT) {
        PyErr_SetString(PyExc_TypeError,
                        "return type is not a struct or is opaque");
        return NULL;
    }
    cd = allocate_owning_object(dataoffset + datasize, ct);
    if (cd == NULL)
        return NULL;
    cd->c_data = ((char *)cd) + dataoffset;

    memcpy(cd->c_data, data, datasize);
    return (PyObject *)cd;
}

static CDataObject *allocate_gcp_object(CDataObject *origobj,
                                        CTypeDescrObject *ct,
                                        PyObject *destructor)
{
    CDataObject_gcp *cd = PyObject_GC_New(CDataObject_gcp, &CDataGCP_Type);
    if (cd == NULL)
        return NULL;

    Py_XINCREF(destructor);
    Py_INCREF(origobj);
    Py_INCREF(ct);
    cd->head.c_data = origobj->c_data;
    cd->head.c_type = ct;
    cd->head.c_weakreflist = NULL;
    cd->origobj = (PyObject *)origobj;
    cd->destructor = destructor;

    PyObject_GC_Track(cd);
    return (CDataObject *)cd;
}

static CDataObject *allocate_with_allocator(Py_ssize_t basesize,
                                            Py_ssize_t datasize,
                                            CTypeDescrObject *ct,
                                            const cffi_allocator_t *allocator)
{
    CDataObject *cd;

    if (allocator->ca_alloc == NULL) {
        cd = allocate_owning_object(basesize + datasize, ct);
        if (cd == NULL)
            return NULL;
        cd->c_data = ((char *)cd) + basesize;
    }
    else {
        PyObject *res = PyObject_CallFunction(allocator->ca_alloc, "n", datasize);
        if (res == NULL)
            return NULL;

        if (!CData_Check(res)) {
            PyErr_Format(PyExc_TypeError,
                         "alloc() must return a cdata object (got %.200s)",
                         Py_TYPE(res)->tp_name);
            Py_DECREF(res);
            return NULL;
        }
        cd = (CDataObject *)res;
        if (!(cd->c_type->ct_flags & (CT_POINTER|CT_ARRAY))) {
            PyErr_Format(PyExc_TypeError,
                         "alloc() must return a cdata pointer, not '%s'",
                         cd->c_type->ct_name);
            Py_DECREF(res);
            return NULL;
        }
        if (!cd->c_data) {
            PyErr_SetString(PyExc_MemoryError, "alloc() returned NULL");
            Py_DECREF(res);
            return NULL;
        }

        cd = allocate_gcp_object(cd, ct, allocator->ca_free);
        Py_DECREF(res);
    }
    if (!allocator->ca_dont_clear)
        memset(cd->c_data, 0, datasize);
    return cd;
}

static PyObject *direct_newp(CTypeDescrObject *ct, PyObject *init,
                             const cffi_allocator_t *allocator)
{
    CTypeDescrObject *ctitem;
    CDataObject *cd;
    Py_ssize_t dataoffset, datasize, explicitlength;

    explicitlength = -1;
    if (ct->ct_flags & CT_POINTER) {
        dataoffset = offsetof(CDataObject_own_nolength, alignment);
        ctitem = ct->ct_itemdescr;
        datasize = ctitem->ct_size;
        if (datasize < 0) {
            PyErr_Format(PyExc_TypeError,
                         "cannot instantiate ctype '%s' of unknown size",
                         ctitem->ct_name);
            return NULL;
        }
        if (ctitem->ct_flags & CT_PRIMITIVE_CHAR)
            datasize *= 2;   /* forcefully add another character: a null */

        if ((ctitem->ct_flags & (CT_STRUCT | CT_UNION)) && init != Py_None) {
            if (force_lazy_struct(ctitem) < 0)   /* for CT_WITH_VAR_ARRAY */
                return NULL;
            if (ctitem->ct_flags & CT_WITH_VAR_ARRAY) {
                Py_ssize_t optvarsize = datasize;
                if (convert_struct_from_object(NULL,ctitem, init,
                                               &optvarsize) < 0)
                    return NULL;
                datasize = optvarsize;
            }
        }
    }
    else if (ct->ct_flags & CT_ARRAY) {
        dataoffset = offsetof(CDataObject_own_nolength, alignment);
        datasize = ct->ct_size;
        if (datasize < 0) {
            explicitlength = get_new_array_length(&init);
            if (explicitlength < 0)
                return NULL;
            ctitem = ct->ct_itemdescr;
            dataoffset = offsetof(CDataObject_own_length, alignment);
            datasize = explicitlength * ctitem->ct_size;
            if (explicitlength > 0 &&
                    (datasize / explicitlength) != ctitem->ct_size) {
                PyErr_SetString(PyExc_OverflowError,
                                "array size would overflow a Py_ssize_t");
                return NULL;
            }
        }
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "expected a pointer or array ctype, got '%s'",
                     ct->ct_name);
        return NULL;
    }

    if (ct->ct_flags & CT_IS_PTR_TO_OWNED) {
        /* common case of ptr-to-struct (or ptr-to-union): for this case
           we build two objects instead of one, with the memory-owning
           one being really the struct (or union) and the returned one
           having a strong reference to it */
        CDataObject *cds;

        cds = allocate_with_allocator(dataoffset, datasize, ct->ct_itemdescr,
                                      allocator);
        if (cds == NULL)
            return NULL;

        cd = allocate_owning_object(sizeof(CDataObject_own_structptr), ct);
        if (cd == NULL) {
            Py_DECREF(cds);
            return NULL;
        }
        /* store the only reference to cds into cd */
        ((CDataObject_own_structptr *)cd)->structobj = (PyObject *)cds;
        assert(explicitlength < 0);

        cd->c_data = cds->c_data;
    }
    else {
        cd = allocate_with_allocator(dataoffset, datasize, ct, allocator);
        if (cd == NULL)
            return NULL;

        if (explicitlength >= 0)
            ((CDataObject_own_length*)cd)->length = explicitlength;
    }

    if (init != Py_None) {
        if (convert_from_object(cd->c_data,
              (ct->ct_flags & CT_POINTER) ? ct->ct_itemdescr : ct, init) < 0) {
            Py_DECREF(cd);
            return NULL;
        }
    }
    return (PyObject *)cd;
}

static PyObject *b_newp(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ct;
    PyObject *init = Py_None;
    if (!PyArg_ParseTuple(args, "O!|O:newp", &CTypeDescr_Type, &ct, &init))
        return NULL;
    return direct_newp(ct, init, &default_allocator);
}

static int
_my_PyObject_AsBool(PyObject *ob)
{
    /* convert and cast a Python object to a boolean.  Accept an integer
       or a float object, up to a CData 'long double'. */
    PyObject *io;
    PyNumberMethods *nb;
    int res;

#if PY_MAJOR_VERSION < 3
    if (PyInt_Check(ob)) {
        return PyInt_AS_LONG(ob) != 0;
    }
    else
#endif
    if (PyLong_Check(ob)) {
        return _PyLong_Sign(ob) != 0;
    }
    else if (PyFloat_Check(ob)) {
        return PyFloat_AS_DOUBLE(ob) != 0.0;
    }
    else if (CData_Check(ob)) {
        CDataObject *cd = (CDataObject *)ob;
        if (cd->c_type->ct_flags & CT_PRIMITIVE_FLOAT) {
            /*READ(cd->c_data, cd->c_type->ct_size)*/
            if (cd->c_type->ct_flags & CT_IS_LONGDOUBLE) {
                /* 'long double' objects: return the answer directly */
                return read_raw_longdouble_data(cd->c_data) != 0.0;
            }
            else {
                /* 'float'/'double' objects: return the answer directly */
                return read_raw_float_data(cd->c_data,
                                           cd->c_type->ct_size) != 0.0;
            }
        }
    }
    nb = ob->ob_type->tp_as_number;
    if (nb == NULL || (nb->nb_float == NULL && nb->nb_int == NULL)) {
        PyErr_SetString(PyExc_TypeError, "integer/float expected");
        return -1;
    }
    if (nb->nb_float && !CData_Check(ob))
        io = (*nb->nb_float) (ob);
    else
        io = (*nb->nb_int) (ob);
    if (io == NULL)
        return -1;

    if (PyIntOrLong_Check(io) || PyFloat_Check(io)) {
        res = _my_PyObject_AsBool(io);
    }
    else {
        PyErr_SetString(PyExc_TypeError, "integer/float conversion failed");
        res = -1;
    }
    Py_DECREF(io);
    return res;
}

static CDataObject *_new_casted_primitive(CTypeDescrObject *ct)
{
    int dataoffset = offsetof(CDataObject_casted_primitive, alignment);
    CDataObject *cd = (CDataObject *)PyObject_Malloc(dataoffset + ct->ct_size);
    if (PyObject_Init((PyObject *)cd, &CData_Type) == NULL)
        return NULL;
    Py_INCREF(ct);
    cd->c_type = ct;
    cd->c_data = ((char*)cd) + dataoffset;
    cd->c_weakreflist = NULL;
    return cd;
}

static CDataObject *cast_to_integer_or_char(CTypeDescrObject *ct, PyObject *ob)
{
    unsigned PY_LONG_LONG value;
    CDataObject *cd;

    if (CData_Check(ob) &&
        ((CDataObject *)ob)->c_type->ct_flags &
                                 (CT_POINTER|CT_FUNCTIONPTR|CT_ARRAY)) {
        value = (Py_intptr_t)((CDataObject *)ob)->c_data;
    }
#if PY_MAJOR_VERSION < 3
    else if (PyString_Check(ob)) {
        if (PyString_GET_SIZE(ob) != 1) {
            PyErr_Format(PyExc_TypeError,
                         "cannot cast string of length %zd to ctype '%s'",
                         PyString_GET_SIZE(ob), ct->ct_name);
            return NULL;
        }
        value = (unsigned char)PyString_AS_STRING(ob)[0];
    }
#endif
#ifdef HAVE_WCHAR_H
    else if (PyUnicode_Check(ob)) {
        wchar_t ordinal;
        if (_my_PyUnicode_AsSingleWideChar(ob, &ordinal) < 0) {
            PyErr_Format(PyExc_TypeError,
                      "cannot cast unicode string of length %zd to ctype '%s'",
                         PyUnicode_GET_SIZE(ob), ct->ct_name);
            return NULL;
        }
        value = (long)ordinal;
    }
#endif
    else if (PyBytes_Check(ob)) {
        int res = _convert_to_char(ob);
        if (res < 0)
            return NULL;
        value = (unsigned char)res;
    }
    else if (ct->ct_flags & CT_IS_BOOL) {
        int res = _my_PyObject_AsBool(ob);
        if (res < 0)
            return NULL;
        value = res;
    }
    else {
        value = _my_PyLong_AsUnsignedLongLong(ob, 0);
        if (value == (unsigned PY_LONG_LONG)-1 && PyErr_Occurred())
            return NULL;
    }
    if (ct->ct_flags & CT_IS_BOOL)
        value = !!value;
    cd = _new_casted_primitive(ct);
    if (cd != NULL)
        write_raw_integer_data(cd->c_data, value, ct->ct_size);
    return cd;
}

static PyObject *do_cast(CTypeDescrObject *ct, PyObject *ob)
{
    CDataObject *cd;

    if (ct->ct_flags & (CT_POINTER|CT_FUNCTIONPTR|CT_ARRAY) &&
        ct->ct_size >= 0) {
        /* cast to a pointer, to a funcptr, or to an array.
           Note that casting to an array is an extension to the C language,
           which seems to be necessary in order to sanely get a
           <cdata 'int[3]'> at some address. */
        unsigned PY_LONG_LONG value;

        if (CData_Check(ob)) {
            CDataObject *cdsrc = (CDataObject *)ob;
            if (cdsrc->c_type->ct_flags &
                    (CT_POINTER|CT_FUNCTIONPTR|CT_ARRAY)) {
                return new_simple_cdata(cdsrc->c_data, ct);
            }
        }
        if ((ct->ct_flags & CT_POINTER) &&
                (ct->ct_itemdescr->ct_flags & CT_IS_FILE) &&
                PyFile_Check(ob)) {
            FILE *f = PyFile_AsFile(ob);
            if (f == NULL && PyErr_Occurred())
                return NULL;
            return new_simple_cdata((char *)f, ct);
        }
        value = _my_PyLong_AsUnsignedLongLong(ob, 0);
        if (value == (unsigned PY_LONG_LONG)-1 && PyErr_Occurred())
            return NULL;
        return new_simple_cdata((char *)(Py_intptr_t)value, ct);
    }
    else if (ct->ct_flags & (CT_PRIMITIVE_SIGNED|CT_PRIMITIVE_UNSIGNED
                             |CT_PRIMITIVE_CHAR)) {
        /* cast to an integer type or a char */
        return (PyObject *)cast_to_integer_or_char(ct, ob);
    }
    else if (ct->ct_flags & CT_PRIMITIVE_FLOAT) {
        /* cast to a float */
        double value;
        PyObject *io;

        if (CData_Check(ob)) {
            CDataObject *cdsrc = (CDataObject *)ob;

            if (!(cdsrc->c_type->ct_flags & CT_PRIMITIVE_ANY))
                goto cannot_cast;
            io = convert_to_object(cdsrc->c_data, cdsrc->c_type);
            if (io == NULL)
                return NULL;
        }
        else {
            io = ob;
            Py_INCREF(io);
        }

        if (PyBytes_Check(io)) {
            if (PyBytes_GET_SIZE(io) != 1) {
                Py_DECREF(io);
                goto cannot_cast;
            }
            value = (unsigned char)PyBytes_AS_STRING(io)[0];
        }
#if HAVE_WCHAR_H
        else if (PyUnicode_Check(io)) {
            wchar_t ordinal;
            if (_my_PyUnicode_AsSingleWideChar(io, &ordinal) < 0) {
                Py_DECREF(io);
                goto cannot_cast;
            }
            value = (long)ordinal;
        }
#endif
        else if ((ct->ct_flags & CT_IS_LONGDOUBLE) &&
                 CData_Check(io) &&
                 (((CDataObject *)io)->c_type->ct_flags & CT_IS_LONGDOUBLE)) {
            long double lvalue;
            char *data = ((CDataObject *)io)->c_data;
            /*READ(data, sizeof(long double)*/
            lvalue = read_raw_longdouble_data(data);
            Py_DECREF(io);
            cd = _new_casted_primitive(ct);
            if (cd != NULL)
                write_raw_longdouble_data(cd->c_data, lvalue);
            return (PyObject *)cd;
        }
        else {
            value = PyFloat_AsDouble(io);
        }
        Py_DECREF(io);
        if (value == -1.0 && PyErr_Occurred())
            return NULL;

        cd = _new_casted_primitive(ct);
        if (cd != NULL) {
            if (!(ct->ct_flags & CT_IS_LONGDOUBLE))
                write_raw_float_data(cd->c_data, value, ct->ct_size);
            else
                write_raw_longdouble_data(cd->c_data, (long double)value);
        }
        return (PyObject *)cd;
    }
    else {
        PyErr_Format(PyExc_TypeError, "cannot cast to ctype '%s'",
                     ct->ct_name);
        return NULL;
    }

 cannot_cast:
    if (CData_Check(ob))
        PyErr_Format(PyExc_TypeError, "cannot cast ctype '%s' to ctype '%s'",
                     ((CDataObject *)ob)->c_type->ct_name, ct->ct_name);
    else
        PyErr_Format(PyExc_TypeError,
                     "cannot cast %.200s object to ctype '%s'",
                     Py_TYPE(ob)->tp_name, ct->ct_name);
    return NULL;
}

static PyObject *b_cast(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ct;
    PyObject *ob;
    if (!PyArg_ParseTuple(args, "O!O:cast", &CTypeDescr_Type, &ct, &ob))
        return NULL;

    return do_cast(ct, ob);
}

/************************************************************/

typedef struct {
    PyObject_HEAD
    void *dl_handle;
    char *dl_name;
} DynLibObject;

static void dl_dealloc(DynLibObject *dlobj)
{
    dlclose(dlobj->dl_handle);
    free(dlobj->dl_name);
    PyObject_Del(dlobj);
}

static PyObject *dl_repr(DynLibObject *dlobj)
{
    return PyText_FromFormat("<clibrary '%s'>", dlobj->dl_name);
}

static PyObject *dl_load_function(DynLibObject *dlobj, PyObject *args)
{
    CTypeDescrObject *ct;
    char *funcname;
    void *funcptr;
    int ok;

    if (!PyArg_ParseTuple(args, "O!s:load_function",
                          &CTypeDescr_Type, &ct, &funcname))
        return NULL;

    ok = 0;
    if (ct->ct_flags & CT_FUNCTIONPTR)
        ok = 1;
    if ((ct->ct_flags & CT_POINTER) && (ct->ct_itemdescr->ct_flags & CT_VOID))
        ok = 1;
    if (!ok) {
        PyErr_Format(PyExc_TypeError, "function cdata expected, got '%s'",
                     ct->ct_name);
        return NULL;
    }
    dlerror();   /* clear error condition */
    funcptr = dlsym(dlobj->dl_handle, funcname);
    if (funcptr == NULL) {
        const char *error = dlerror();
        PyErr_Format(PyExc_KeyError,
                     "function '%s' not found in library '%s': %s",
                     funcname, dlobj->dl_name, error);
        return NULL;
    }

    return new_simple_cdata(funcptr, ct);
}

static PyObject *dl_read_variable(DynLibObject *dlobj, PyObject *args)
{
    CTypeDescrObject *ct;
    char *varname;
    char *data;

    if (!PyArg_ParseTuple(args, "O!s:read_variable",
                          &CTypeDescr_Type, &ct, &varname))
        return NULL;

    dlerror();   /* clear error condition */
    data = dlsym(dlobj->dl_handle, varname);
    if (data == NULL) {
        const char *error = dlerror();
        if (error != NULL) {
            PyErr_Format(PyExc_KeyError,
                         "variable '%s' not found in library '%s': %s",
                         varname, dlobj->dl_name, error);
            return NULL;
        }
    }
    return convert_to_object(data, ct);
}

static PyObject *dl_write_variable(DynLibObject *dlobj, PyObject *args)
{
    CTypeDescrObject *ct;
    PyObject *value;
    char *varname;
    char *data;

    if (!PyArg_ParseTuple(args, "O!sO:write_variable",
                          &CTypeDescr_Type, &ct, &varname, &value))
        return NULL;

    dlerror();   /* clear error condition */
    data = dlsym(dlobj->dl_handle, varname);
    if (data == NULL) {
        const char *error = dlerror();
        PyErr_Format(PyExc_KeyError,
                     "variable '%s' not found in library '%s': %s",
                     varname, dlobj->dl_name, error);
        return NULL;
    }
    if (convert_from_object(data, ct, value) < 0)
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef dl_methods[] = {
    {"load_function",   (PyCFunction)dl_load_function,  METH_VARARGS},
    {"read_variable",   (PyCFunction)dl_read_variable,  METH_VARARGS},
    {"write_variable",  (PyCFunction)dl_write_variable, METH_VARARGS},
    {NULL,              NULL}           /* sentinel */
};

static PyTypeObject dl_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.Library",            /* tp_name */
    sizeof(DynLibObject),               /* tp_basicsize */
    0,                                  /* tp_itemsize */
    /* methods */
    (destructor)dl_dealloc,             /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_compare */
    (reprfunc)dl_repr,                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    PyObject_GenericGetAttr,            /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    0,                                  /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    dl_methods,                         /* tp_methods */
};

static PyObject *b_load_library(PyObject *self, PyObject *args)
{
    char *filename_or_null, *printable_filename;
    void *handle;
    DynLibObject *dlobj;
    int flags = 0;

    if (PyTuple_GET_SIZE(args) == 0 || PyTuple_GET_ITEM(args, 0) == Py_None) {
        PyObject *dummy;
        if (!PyArg_ParseTuple(args, "|Oi:load_library",
                              &dummy, &flags))
            return NULL;
        filename_or_null = NULL;
    }
    else if (!PyArg_ParseTuple(args, "et|i:load_library",
                          Py_FileSystemDefaultEncoding, &filename_or_null,
                          &flags))
        return NULL;

    if ((flags & (RTLD_NOW | RTLD_LAZY)) == 0)
        flags |= RTLD_NOW;

    printable_filename = filename_or_null ? filename_or_null : "<None>";
    handle = dlopen(filename_or_null, flags);
    if (handle == NULL) {
        const char *error = dlerror();
        PyErr_Format(PyExc_OSError, "cannot load library %s: %s",
                     printable_filename, error);
        return NULL;
    }

    dlobj = PyObject_New(DynLibObject, &dl_type);
    if (dlobj == NULL) {
        dlclose(handle);
        return NULL;
    }
    dlobj->dl_handle = handle;
    dlobj->dl_name = strdup(printable_filename);
    return (PyObject *)dlobj;
}

/************************************************************/

static PyObject *get_unique_type(CTypeDescrObject *x,
                                 const void *unique_key[], long keylength)
{
    /* Replace the CTypeDescrObject 'x' with a standardized one.
       This either just returns x, or x is decrefed and a new reference
       to the already-existing equivalent is returned.

       In this function, 'x' always contains a reference that must be
       either decrefed or returned.

       Keys:
           void       ["void"]
           primitive  [&static_struct]
           pointer    [ctype]
           array      [ctype, length]
           funcptr    [ctresult, ellipsis+abi, num_args, ctargs...]
    */
    PyObject *key, *y;
    void *pkey;

    key = PyBytes_FromStringAndSize(NULL, keylength * sizeof(void *));
    if (key == NULL)
        goto error;

    pkey = PyBytes_AS_STRING(key);
    memcpy(pkey, unique_key, keylength * sizeof(void *));

    y = PyDict_GetItem(unique_cache, key);
    if (y != NULL) {
        Py_DECREF(key);
        Py_INCREF(y);
        Py_DECREF(x);
        return y;
    }
    if (PyDict_SetItem(unique_cache, key, (PyObject *)x) < 0) {
        Py_DECREF(key);
        goto error;
    }
    /* Haaaack for our reference count hack: gcmodule.c must not see this
       dictionary.  The problem is that any PyDict_SetItem() notices that
       'x' is tracked and re-tracks the unique_cache dictionary.  So here
       we re-untrack it again... */
    PyObject_GC_UnTrack(unique_cache);

    assert(x->ct_unique_key == NULL);
    x->ct_unique_key = key; /* the key will be freed in ctypedescr_dealloc() */
    Py_DECREF(x);          /* the 'value' in unique_cache doesn't count as 1 */
    return (PyObject *)x;

 error:
    Py_DECREF(x);
    return NULL;
}

static PyObject *new_primitive_type(const char *name)
{
#define ENUM_PRIMITIVE_TYPES                                    \
       EPTYPE(c, char, CT_PRIMITIVE_CHAR)                       \
       EPTYPE(s, short, CT_PRIMITIVE_SIGNED )                   \
       EPTYPE(i, int, CT_PRIMITIVE_SIGNED )                     \
       EPTYPE(l, long, CT_PRIMITIVE_SIGNED )                    \
       EPTYPE(ll, long long, CT_PRIMITIVE_SIGNED )              \
       EPTYPE(sc, signed char, CT_PRIMITIVE_SIGNED )            \
       EPTYPE(uc, unsigned char, CT_PRIMITIVE_UNSIGNED )        \
       EPTYPE(us, unsigned short, CT_PRIMITIVE_UNSIGNED )       \
       EPTYPE(ui, unsigned int, CT_PRIMITIVE_UNSIGNED )         \
       EPTYPE(ul, unsigned long, CT_PRIMITIVE_UNSIGNED )        \
       EPTYPE(ull, unsigned long long, CT_PRIMITIVE_UNSIGNED )  \
       EPTYPE(f, float, CT_PRIMITIVE_FLOAT )                    \
       EPTYPE(d, double, CT_PRIMITIVE_FLOAT )                   \
       EPTYPE(ld, long double, CT_PRIMITIVE_FLOAT | CT_IS_LONGDOUBLE ) \
       ENUM_PRIMITIVE_TYPES_WCHAR                               \
       EPTYPE(b, _Bool, CT_PRIMITIVE_UNSIGNED | CT_IS_BOOL )    \
     /* the following types are not primitive in the C sense */ \
       EPTYPE(i8, int8_t, CT_PRIMITIVE_SIGNED)                  \
       EPTYPE(u8, uint8_t, CT_PRIMITIVE_UNSIGNED)               \
       EPTYPE(i16, int16_t, CT_PRIMITIVE_SIGNED)                \
       EPTYPE(u16, uint16_t, CT_PRIMITIVE_UNSIGNED)             \
       EPTYPE(i32, int32_t, CT_PRIMITIVE_SIGNED)                \
       EPTYPE(u32, uint32_t, CT_PRIMITIVE_UNSIGNED)             \
       EPTYPE(i64, int64_t, CT_PRIMITIVE_SIGNED)                \
       EPTYPE(u64, uint64_t, CT_PRIMITIVE_UNSIGNED)             \
       EPTYPE(il8, int_least8_t, CT_PRIMITIVE_SIGNED)           \
       EPTYPE(ul8, uint_least8_t, CT_PRIMITIVE_UNSIGNED)        \
       EPTYPE(il16, int_least16_t, CT_PRIMITIVE_SIGNED)         \
       EPTYPE(ul16, uint_least16_t, CT_PRIMITIVE_UNSIGNED)      \
       EPTYPE(il32, int_least32_t, CT_PRIMITIVE_SIGNED)         \
       EPTYPE(ul32, uint_least32_t, CT_PRIMITIVE_UNSIGNED)      \
       EPTYPE(il64, int_least64_t, CT_PRIMITIVE_SIGNED)         \
       EPTYPE(ul64, uint_least64_t, CT_PRIMITIVE_UNSIGNED)      \
       EPTYPE(if8, int_fast8_t, CT_PRIMITIVE_SIGNED)            \
       EPTYPE(uf8, uint_fast8_t, CT_PRIMITIVE_UNSIGNED)         \
       EPTYPE(if16, int_fast16_t, CT_PRIMITIVE_SIGNED)          \
       EPTYPE(uf16, uint_fast16_t, CT_PRIMITIVE_UNSIGNED)       \
       EPTYPE(if32, int_fast32_t, CT_PRIMITIVE_SIGNED)          \
       EPTYPE(uf32, uint_fast32_t, CT_PRIMITIVE_UNSIGNED)       \
       EPTYPE(if64, int_fast64_t, CT_PRIMITIVE_SIGNED)          \
       EPTYPE(uf64, uint_fast64_t, CT_PRIMITIVE_UNSIGNED)       \
       EPTYPE(ip, intptr_t, CT_PRIMITIVE_SIGNED)                \
       EPTYPE(up, uintptr_t, CT_PRIMITIVE_UNSIGNED)             \
       EPTYPE(im, intmax_t, CT_PRIMITIVE_SIGNED)                \
       EPTYPE(um, uintmax_t, CT_PRIMITIVE_UNSIGNED)             \
       EPTYPE(pd, ptrdiff_t, CT_PRIMITIVE_SIGNED)               \
       EPTYPE(sz, size_t, CT_PRIMITIVE_UNSIGNED)                \
       EPTYPE(ssz, ssize_t, CT_PRIMITIVE_SIGNED)

#ifdef HAVE_WCHAR_H
# define ENUM_PRIMITIVE_TYPES_WCHAR                             \
       EPTYPE(wc, wchar_t, CT_PRIMITIVE_CHAR )
#else
# define ENUM_PRIMITIVE_TYPES_WCHAR   /* nothing */
#endif

#define EPTYPE(code, typename, flags)                   \
    struct aligncheck_##code { char x; typename y; };
    ENUM_PRIMITIVE_TYPES
#undef EPTYPE

    CTypeDescrObject *td;
    static const struct descr_s { const char *name; int size, align, flags; }
    types[] = {
#define EPTYPE(code, typename, flags)                   \
        { #typename,                                    \
          sizeof(typename),                             \
          offsetof(struct aligncheck_##code, y),        \
          flags                                         \
        },
    ENUM_PRIMITIVE_TYPES
#undef EPTYPE
#undef ENUM_PRIMITIVE_TYPES_WCHAR
#undef ENUM_PRIMITIVE_TYPES
        { NULL }
    };
    const struct descr_s *ptypes;
    const void *unique_key[1];
    int name_size;
    ffi_type *ffitype;

    for (ptypes=types; ; ptypes++) {
        if (ptypes->name == NULL) {
#ifndef HAVE_WCHAR_H
            if (strcmp(name, "wchar_t"))
                PyErr_SetString(PyExc_NotImplementedError, name);
            else
#endif
            PyErr_SetString(PyExc_KeyError, name);
            return NULL;
        }
        if (strcmp(name, ptypes->name) == 0)
            break;
    }

    if (ptypes->flags & CT_PRIMITIVE_SIGNED) {
        switch (ptypes->size) {
        case 1: ffitype = &ffi_type_sint8; break;
        case 2: ffitype = &ffi_type_sint16; break;
        case 4: ffitype = &ffi_type_sint32; break;
        case 8: ffitype = &ffi_type_sint64; break;
        default: goto bad_ffi_type;
        }
    }
    else if (ptypes->flags & CT_PRIMITIVE_FLOAT) {
        if (strcmp(ptypes->name, "float") == 0)
            ffitype = &ffi_type_float;
        else if (strcmp(ptypes->name, "double") == 0)
            ffitype = &ffi_type_double;
        else if (strcmp(ptypes->name, "long double") == 0) {
            /* assume that if sizeof(double) == sizeof(long double), then
               the two types are equivalent for C.  libffi bugs on Win64
               if a function's return type is ffi_type_longdouble... */
            if (sizeof(double) == sizeof(long double))
                ffitype = &ffi_type_double;
            else
                ffitype = &ffi_type_longdouble;
        }
        else
            goto bad_ffi_type;
    }
    else {
        switch (ptypes->size) {
        case 1: ffitype = &ffi_type_uint8; break;
        case 2: ffitype = &ffi_type_uint16; break;
        case 4: ffitype = &ffi_type_uint32; break;
        case 8: ffitype = &ffi_type_uint64; break;
        default: goto bad_ffi_type;
        }
    }

    name_size = strlen(ptypes->name) + 1;
    td = ctypedescr_new(name_size);
    if (td == NULL)
        return NULL;

    memcpy(td->ct_name, name, name_size);
    td->ct_size = ptypes->size;
    td->ct_length = ptypes->align;
    td->ct_extra = ffitype;
    td->ct_flags = ptypes->flags;
    if (td->ct_flags & (CT_PRIMITIVE_SIGNED | CT_PRIMITIVE_CHAR)) {
        if (td->ct_size <= (Py_ssize_t)sizeof(long))
            td->ct_flags |= CT_PRIMITIVE_FITS_LONG;
    }
    else if (td->ct_flags & CT_PRIMITIVE_UNSIGNED) {
        if (td->ct_size < (Py_ssize_t)sizeof(long))
            td->ct_flags |= CT_PRIMITIVE_FITS_LONG;
    }
    td->ct_name_position = strlen(td->ct_name);
    unique_key[0] = ptypes;
    return get_unique_type(td, unique_key, 1);

 bad_ffi_type:
    PyErr_Format(PyExc_NotImplementedError,
                 "primitive type '%s' has size %d; "
                 "the supported sizes are 1, 2, 4, 8",
                 name, (int)ptypes->size);
    return NULL;
}

static PyObject *b_new_primitive_type(PyObject *self, PyObject *args)
{
    char *name;
    if (!PyArg_ParseTuple(args, "s:new_primitive_type", &name))
        return NULL;
    return new_primitive_type(name);
}

static PyObject *new_pointer_type(CTypeDescrObject *ctitem)
{
    CTypeDescrObject *td;
    const char *extra;
    const void *unique_key[1];

    if (ctitem->ct_flags & CT_ARRAY)
        extra = "(*)";   /* obscure case: see test_array_add */
    else
        extra = " *";
    td = ctypedescr_new_on_top(ctitem, extra, 2);
    if (td == NULL)
        return NULL;

    td->ct_size = sizeof(void *);
    td->ct_length = -1;
    td->ct_flags = CT_POINTER;
    if (ctitem->ct_flags & (CT_STRUCT|CT_UNION))
        td->ct_flags |= CT_IS_PTR_TO_OWNED;
    if (ctitem->ct_flags & CT_VOID)
        td->ct_flags |= CT_IS_VOID_PTR;
    if ((ctitem->ct_flags & CT_VOID) ||
        ((ctitem->ct_flags & CT_PRIMITIVE_CHAR) &&
         ctitem->ct_size == sizeof(char)))
        td->ct_flags |= CT_CAST_ANYTHING;   /* 'void *' or 'char *' only */
    unique_key[0] = ctitem;
    return get_unique_type(td, unique_key, 1);
}

static PyObject *b_new_pointer_type(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ctitem;
    if (!PyArg_ParseTuple(args, "O!:new_pointer_type",
                          &CTypeDescr_Type, &ctitem))
        return NULL;
    return new_pointer_type(ctitem);
}

static PyObject *b_new_array_type(PyObject *self, PyObject *args)
{
    PyObject *lengthobj;
    Py_ssize_t length;
    CTypeDescrObject *ctptr;

    if (!PyArg_ParseTuple(args, "O!O:new_array_type",
                          &CTypeDescr_Type, &ctptr, &lengthobj))
        return NULL;

    if (lengthobj == Py_None) {
        length = -1;
    }
    else {
        length = PyNumber_AsSsize_t(lengthobj, PyExc_OverflowError);
        if (length < 0) {
            if (!PyErr_Occurred())
                PyErr_SetString(PyExc_ValueError, "negative array length");
            return NULL;
        }
    }
    return new_array_type(ctptr, length);
}

static PyObject *
new_array_type(CTypeDescrObject *ctptr, Py_ssize_t length)
{
    CTypeDescrObject *td, *ctitem;
    char extra_text[32];
    Py_ssize_t arraysize;
    int flags = CT_ARRAY;
    const void *unique_key[2];

    if (!(ctptr->ct_flags & CT_POINTER)) {
        PyErr_SetString(PyExc_TypeError, "first arg must be a pointer ctype");
        return NULL;
    }
    ctitem = ctptr->ct_itemdescr;
    if (ctitem->ct_size < 0) {
        PyErr_Format(PyExc_ValueError, "array item of unknown size: '%s'",
                     ctitem->ct_name);
        return NULL;
    }

    if (length < 0) {
        sprintf(extra_text, "[]");
        length = -1;
        arraysize = -1;
        if ((ctitem->ct_flags & CT_PRIMITIVE_CHAR) &&
                ctitem->ct_size == sizeof(char))
            flags |= CT_IS_UNSIZED_CHAR_A;
    }
    else {
        sprintf(extra_text, "[%llu]", (unsigned PY_LONG_LONG)length);
        arraysize = length * ctitem->ct_size;
        if (length > 0 && (arraysize / length) != ctitem->ct_size) {
            PyErr_SetString(PyExc_OverflowError,
                            "array size would overflow a Py_ssize_t");
            return NULL;
        }
    }
    td = ctypedescr_new_on_top(ctitem, extra_text, 0);
    if (td == NULL)
        return NULL;

    Py_INCREF(ctptr);
    td->ct_stuff = (PyObject *)ctptr;
    td->ct_size = arraysize;
    td->ct_length = length;
    td->ct_flags = flags;
    unique_key[0] = ctptr;
    unique_key[1] = (void *)length;
    return get_unique_type(td, unique_key, 2);
}

static PyObject *new_void_type(void)
{
    int name_size = strlen("void") + 1;
    const void *unique_key[1];
    CTypeDescrObject *td = ctypedescr_new(name_size);
    if (td == NULL)
        return NULL;

    memcpy(td->ct_name, "void", name_size);
    td->ct_size = -1;
    td->ct_flags = CT_VOID | CT_IS_OPAQUE;
    td->ct_name_position = strlen("void");
    unique_key[0] = "void";
    return get_unique_type(td, unique_key, 1);
}

static PyObject *b_new_void_type(PyObject *self, PyObject *args)
{
    return new_void_type();
}

static PyObject *new_struct_or_union_type(const char *name, int flag)
{
    int namelen = strlen(name);
    CTypeDescrObject *td = ctypedescr_new(namelen + 1);
    if (td == NULL)
        return NULL;

    td->ct_size = -1;
    td->ct_length = -1;
    td->ct_flags = flag | CT_IS_OPAQUE;
    td->ct_extra = NULL;
    memcpy(td->ct_name, name, namelen + 1);
    td->ct_name_position = namelen;
    return (PyObject *)td;
}

static PyObject *b_new_struct_type(PyObject *self, PyObject *args)
{
    char *name;
    int flag;
    if (!PyArg_ParseTuple(args, "s:new_struct_type", &name))
        return NULL;

    flag = CT_STRUCT;
    if (strcmp(name, "struct _IO_FILE") == 0 || strcmp(name, "FILE") == 0)
        flag |= CT_IS_FILE;
    return new_struct_or_union_type(name, flag);
}

static PyObject *b_new_union_type(PyObject *self, PyObject *args)
{
    char *name;
    if (!PyArg_ParseTuple(args, "s:new_union_type", &name))
        return NULL;
    return new_struct_or_union_type(name, CT_UNION);
}

static CFieldObject *
_add_field(PyObject *interned_fields, PyObject *fname, CTypeDescrObject *ftype,
           Py_ssize_t offset, int bitshift, int fbitsize)
{
    int err;
    Py_ssize_t prev_size;
    CFieldObject *cf = PyObject_New(CFieldObject, &CField_Type);
    if (cf == NULL)
        return NULL;

    Py_INCREF(ftype);
    cf->cf_type = ftype;
    cf->cf_offset = offset;
    cf->cf_bitshift = bitshift;
    cf->cf_bitsize = fbitsize;

    Py_INCREF(fname);
    PyText_InternInPlace(&fname);
    prev_size = PyDict_Size(interned_fields);
    err = PyDict_SetItem(interned_fields, fname, (PyObject *)cf);
    Py_DECREF(fname);
    Py_DECREF(cf);
    if (err < 0)
        return NULL;

    if (PyDict_Size(interned_fields) != prev_size + 1) {
        PyErr_Format(PyExc_KeyError, "duplicate field name '%s'",
                     PyText_AS_UTF8(fname));
        return NULL;
    }
    return cf;   /* borrowed reference */
}

#define SF_MSVC_BITFIELDS     0x01
#define SF_GCC_ARM_BITFIELDS  0x02
#define SF_GCC_X86_BITFIELDS  0x10

#define SF_GCC_BIG_ENDIAN     0x04
#define SF_GCC_LITTLE_ENDIAN  0x40

#define SF_PACKED             0x08
#define SF_STD_FIELD_POS      0x80

static int complete_sflags(int sflags)
{
    /* add one of the SF_xxx_BITFIELDS flags if none is specified */
    if (!(sflags & (SF_MSVC_BITFIELDS | SF_GCC_ARM_BITFIELDS |
                    SF_GCC_X86_BITFIELDS))) {
#ifdef MS_WIN32
        sflags |= SF_MSVC_BITFIELDS;
#else
# if defined(__arm__) || defined(__aarch64__)
        sflags |= SF_GCC_ARM_BITFIELDS;
# else
        sflags |= SF_GCC_X86_BITFIELDS;
# endif
#endif
    }
    /* add one of SF_GCC_xx_ENDIAN if none is specified */
    if (!(sflags & (SF_GCC_BIG_ENDIAN | SF_GCC_LITTLE_ENDIAN))) {
        int _check_endian = 1;
        if (*(char *)&_check_endian == 0)
            sflags |= SF_GCC_BIG_ENDIAN;
        else
            sflags |= SF_GCC_LITTLE_ENDIAN;
    }
    return sflags;
}

static int detect_custom_layout(CTypeDescrObject *ct, int sflags,
                                Py_ssize_t cdef_value,
                                Py_ssize_t compiler_value,
                                const char *msg1, const char *txt,
                                const char *msg2)
{
    if (compiler_value != cdef_value) {
        if (sflags & SF_STD_FIELD_POS) {
            PyErr_Format(FFIError,
                         "%s: %s%s%s (cdef says %zd, but C compiler says %zd)."
                         " fix it or use \"...;\" in the cdef for %s to "
                         "make it flexible",
                         ct->ct_name, msg1, txt, msg2,
                         cdef_value, compiler_value,
                         ct->ct_name);
            return -1;
        }
        ct->ct_flags |= CT_CUSTOM_FIELD_POS;
    }
    return 0;
}

static PyObject *b_complete_struct_or_union(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ct;
    PyObject *fields, *interned_fields, *ignored;
    int is_union, alignment;
    Py_ssize_t boffset, i, nb_fields, boffsetmax, alignedsize;
    Py_ssize_t totalsize = -1;
    int totalalignment = -1;
    CFieldObject **previous;
    int prev_bitfield_size, prev_bitfield_free;
    int sflags = 0;

    if (!PyArg_ParseTuple(args, "O!O!|Onii:complete_struct_or_union",
                          &CTypeDescr_Type, &ct,
                          &PyList_Type, &fields,
                          &ignored, &totalsize, &totalalignment, &sflags))
        return NULL;

    sflags = complete_sflags(sflags);

    if ((ct->ct_flags & (CT_STRUCT|CT_IS_OPAQUE)) ==
                        (CT_STRUCT|CT_IS_OPAQUE)) {
        is_union = 0;
    }
    else if ((ct->ct_flags & (CT_UNION|CT_IS_OPAQUE)) ==
                             (CT_UNION|CT_IS_OPAQUE)) {
        is_union = 1;
    }
    else {
        PyErr_SetString(PyExc_TypeError,
                  "first arg must be a non-initialized struct or union ctype");
        return NULL;
    }
    ct->ct_flags &= ~CT_CUSTOM_FIELD_POS;

    alignment = 1;
    boffset = 0;         /* this number is in *bits*, not bytes! */
    boffsetmax = 0;      /* the maximum value of boffset, in bits too */
    prev_bitfield_size = 0;
    prev_bitfield_free = 0;
    nb_fields = PyList_GET_SIZE(fields);
    interned_fields = PyDict_New();
    if (interned_fields == NULL)
        return NULL;

    previous = (CFieldObject **)&ct->ct_extra;

    for (i=0; i<nb_fields; i++) {
        PyObject *fname;
        CTypeDescrObject *ftype;
        int fbitsize = -1, falign, do_align;
        Py_ssize_t foffset = -1;

        if (!PyArg_ParseTuple(PyList_GET_ITEM(fields, i), "O!O!|in:list item",
                              &PyText_Type, &fname,
                              &CTypeDescr_Type, &ftype,
                              &fbitsize, &foffset))
            goto error;

        if (ftype->ct_size < 0) {
            if ((ftype->ct_flags & CT_ARRAY) && fbitsize < 0
                    && (i == nb_fields - 1 || foffset != -1)) {
                ct->ct_flags |= CT_WITH_VAR_ARRAY;
            }
            else {
                PyErr_Format(PyExc_TypeError,
                             "field '%s.%s' has ctype '%s' of unknown size",
                             ct->ct_name, PyText_AS_UTF8(fname),
                             ftype->ct_name);
                goto error;
            }
        }

        if (is_union)
            boffset = 0;   /* reset each field at offset 0 */

        /* update the total alignment requirement, but skip it if the
           field is an anonymous bitfield or if SF_PACKED */
        falign = (sflags & SF_PACKED) ? 1 : get_alignment(ftype);
        if (falign < 0)
            goto error;

        do_align = 1;
        if (!(sflags & SF_GCC_ARM_BITFIELDS) && fbitsize >= 0) {
            if (!(sflags & SF_MSVC_BITFIELDS)) {
                /* GCC: anonymous bitfields (of any size) don't cause alignment */
                do_align = PyText_GetSize(fname) > 0;
            }
            else {
                /* MSVC: zero-sized bitfields don't cause alignment */
                do_align = fbitsize > 0;
            }
        }
        if (alignment < falign && do_align)
            alignment = falign;

        if (fbitsize < 0) {
            /* not a bitfield: common case */
            int bs_flag;

            if (ftype->ct_flags & CT_ARRAY && ftype->ct_length == 0)
                bs_flag = BS_EMPTY_ARRAY;
            else
                bs_flag = BS_REGULAR;

            /* align this field to its own 'falign' by inserting padding */
            boffset = (boffset + falign*8-1) & ~(falign*8-1); /* bits! */

            if (foffset >= 0) {
                /* a forced field position: ignore the offset just computed,
                   except to know if we must set CT_CUSTOM_FIELD_POS */
                if (detect_custom_layout(ct, sflags, boffset / 8, foffset,
                                         "wrong offset for field '",
                                         PyText_AS_UTF8(fname), "'") < 0)
                    goto error;
                boffset = foffset * 8;
            }

            if (PyText_GetSize(fname) == 0 &&
                    ftype->ct_flags & (CT_STRUCT|CT_UNION)) {
                /* a nested anonymous struct or union */
                CFieldObject *cfsrc = (CFieldObject *)ftype->ct_extra;
                for (; cfsrc != NULL; cfsrc = cfsrc->cf_next) {
                    /* broken complexity in the call to get_field_name(),
                       but we'll assume you never do that with nested
                       anonymous structures with thousand of fields */
                    *previous = _add_field(interned_fields,
                                           get_field_name(ftype, cfsrc),
                                           cfsrc->cf_type,
                                           boffset / 8 + cfsrc->cf_offset,
                                           cfsrc->cf_bitshift,
                                           cfsrc->cf_bitsize);
                    if (*previous == NULL)
                        goto error;
                    previous = &(*previous)->cf_next;
                }
                /* always forbid such structures from being passed by value */
                ct->ct_flags |= CT_CUSTOM_FIELD_POS;
            }
            else {
                *previous = _add_field(interned_fields, fname, ftype,
                                        boffset / 8, bs_flag, -1);
                if (*previous == NULL)
                    goto error;
                previous = &(*previous)->cf_next;
            }
            if (ftype->ct_size >= 0)
                boffset += ftype->ct_size * 8;
            prev_bitfield_size = 0;
        }
        else {
            /* this is the case of a bitfield */
            Py_ssize_t field_offset_bytes;
            int bits_already_occupied, bitshift;

            if (foffset >= 0) {
                PyErr_Format(PyExc_TypeError,
                             "field '%s.%s' is a bitfield, "
                             "but a fixed offset is specified",
                             ct->ct_name, PyText_AS_UTF8(fname));
                goto error;
            }

            if (!(ftype->ct_flags & (CT_PRIMITIVE_SIGNED |
                                     CT_PRIMITIVE_UNSIGNED |
                                     CT_PRIMITIVE_CHAR))) {
                PyErr_Format(PyExc_TypeError,
                        "field '%s.%s' declared as '%s' cannot be a bit field",
                             ct->ct_name, PyText_AS_UTF8(fname),
                             ftype->ct_name);
                goto error;
            }
            if (fbitsize > 8 * ftype->ct_size) {
                PyErr_Format(PyExc_TypeError,
                             "bit field '%s.%s' is declared '%s:%d', which "
                             "exceeds the width of the type",
                             ct->ct_name, PyText_AS_UTF8(fname),
                             ftype->ct_name, fbitsize);
                goto error;
            }

            /* compute the starting position of the theoretical field
               that covers a complete 'ftype', inside of which we will
               locate the real bitfield */
            field_offset_bytes = boffset / 8;
            field_offset_bytes &= ~(falign - 1);

            if (fbitsize == 0) {
                if (PyText_GetSize(fname) > 0) {
                    PyErr_Format(PyExc_TypeError,
                                 "field '%s.%s' is declared with :0",
                                 ct->ct_name, PyText_AS_UTF8(fname));
                    goto error;
                }
                if (!(sflags & SF_MSVC_BITFIELDS)) {
                    /* GCC's notion of "ftype :0;" */

                    /* pad boffset to a value aligned for "ftype" */
                    if (boffset > field_offset_bytes * 8) {
                        field_offset_bytes += falign;
                        assert(boffset < field_offset_bytes * 8);
                    }
                    boffset = field_offset_bytes * 8;
                }
                else {
                    /* MSVC's notion of "ftype :0;" */

                    /* Mostly ignored.  It seems they only serve as
                       separator between other bitfields, to force them
                       into separate words. */
                }
                prev_bitfield_size = 0;
            }
            else {
                if (!(sflags & SF_MSVC_BITFIELDS)) {
                    /* GCC's algorithm */

                    /* Can the field start at the offset given by 'boffset'?  It
                       can if it would entirely fit into an aligned ftype field. */
                    bits_already_occupied = boffset - (field_offset_bytes * 8);

                    if (bits_already_occupied + fbitsize > 8 * ftype->ct_size) {
                        /* it would not fit, we need to start at the next
                           allowed position */
                        if ((sflags & SF_PACKED) &&
                            (bits_already_occupied & 7)) {
                            PyErr_Format(PyExc_NotImplementedError,
                                "with 'packed', gcc would compile field "
                                "'%s.%s' to reuse some bits in the previous "
                                "field", ct->ct_name, PyText_AS_UTF8(fname));
                            goto error;
                        }
                        field_offset_bytes += falign;
                        assert(boffset < field_offset_bytes * 8);
                        boffset = field_offset_bytes * 8;
                        bitshift = 0;
                    }
                    else {
                        bitshift = bits_already_occupied;
                        assert(bitshift >= 0);
                    }
                    boffset += fbitsize;
                }
                else {
                    /* MSVC's algorithm */

                    /* A bitfield is considered as taking the full width
                       of their declared type.  It can share some bits
                       with the previous field only if it was also a
                       bitfield and used a type of the same size. */
                    if (prev_bitfield_size == ftype->ct_size &&
                        prev_bitfield_free >= fbitsize) {
                        /* yes: reuse */
                        bitshift = 8 * prev_bitfield_size - prev_bitfield_free;
                    }
                    else {
                        /* no: start a new full field */
                        boffset = (boffset + falign*8-1) & ~(falign*8-1); /*align*/
                        boffset += ftype->ct_size * 8;
                        bitshift = 0;
                        prev_bitfield_size = ftype->ct_size;
                        prev_bitfield_free = 8 * prev_bitfield_size;
                    }
                    prev_bitfield_free -= fbitsize;
                    field_offset_bytes = boffset / 8 - ftype->ct_size;
                }

                if (sflags & SF_GCC_BIG_ENDIAN)
                    bitshift = 8 * ftype->ct_size - fbitsize - bitshift;

                *previous = _add_field(interned_fields, fname, ftype,
                                       field_offset_bytes, bitshift, fbitsize);
                if (*previous == NULL)
                    goto error;
                previous = &(*previous)->cf_next;
            }
        }

        if (boffset > boffsetmax)
            boffsetmax = boffset;
    }
    *previous = NULL;

    /* Like C, if the size of this structure would be zero, we compute it
       as 1 instead.  But for ctypes support, we allow the manually-
       specified totalsize to be zero in this case. */
    boffsetmax = (boffsetmax + 7) / 8;        /* bits -> bytes */
    alignedsize = (boffsetmax + alignment - 1) & ~(alignment-1);
    if (alignedsize == 0)
        alignedsize = 1;

    if (totalsize < 0) {
        totalsize = alignedsize;
    }
    else {
        if (detect_custom_layout(ct, sflags, alignedsize,
                                 totalsize, "wrong total size", "", "") < 0)
            goto error;
        if (totalsize < boffsetmax) {
            PyErr_Format(PyExc_TypeError,
                         "%s cannot be of size %zd: there are fields at least "
                         "up to %zd", ct->ct_name, totalsize, boffsetmax);
            goto error;
        }
    }
    if (totalalignment < 0) {
        totalalignment = alignment;
    }
    else {
        if (detect_custom_layout(ct, sflags, alignment, totalalignment,
                                 "wrong total alignment", "", "") < 0)
            goto error;
    }

    ct->ct_size = totalsize;
    ct->ct_length = totalalignment;
    ct->ct_stuff = interned_fields;
    ct->ct_flags &= ~CT_IS_OPAQUE;

    Py_INCREF(Py_None);
    return Py_None;

 error:
    ct->ct_extra = NULL;
    Py_DECREF(interned_fields);
    return NULL;
}

struct funcbuilder_s {
    Py_ssize_t nb_bytes;
    char *bufferp;
    ffi_type **atypes;
    ffi_type *rtype;
    Py_ssize_t nargs;
    CTypeDescrObject *fct;
};

static void *fb_alloc(struct funcbuilder_s *fb, Py_ssize_t size)
{
    if (fb->bufferp == NULL) {
        fb->nb_bytes += size;
        return NULL;
    }
    else {
        char *result = fb->bufferp;
        fb->bufferp += size;
        return result;
    }
}

static ffi_type *fb_fill_type(struct funcbuilder_s *fb, CTypeDescrObject *ct,
                              int is_result_type)
{
    const char *place = is_result_type ? "return value" : "argument";

    if (ct->ct_flags & CT_PRIMITIVE_ANY) {
        return (ffi_type *)ct->ct_extra;
    }
    else if (ct->ct_flags & (CT_POINTER|CT_FUNCTIONPTR)) {
        return &ffi_type_pointer;
    }
    else if ((ct->ct_flags & CT_VOID) && is_result_type) {
        return &ffi_type_void;
    }

    if (ct->ct_size <= 0) {
        PyErr_Format(PyExc_TypeError,
                     ct->ct_size < 0 ? "ctype '%s' has incomplete type"
                                     : "ctype '%s' has size 0",
                     ct->ct_name);
        return NULL;
    }
    if (ct->ct_flags & CT_STRUCT) {
        ffi_type *ffistruct, *ffifield;
        ffi_type **elements;
        Py_ssize_t i, n, nflat;
        CFieldObject *cf;

        /* We can't pass a struct that was completed by verify().
           Issue: assume verify() is given "struct { long b; ...; }".
           Then it will complete it in the same way whether it is actually
           "struct { long a, b; }" or "struct { double a; long b; }".
           But on 64-bit UNIX, these two structs are passed by value
           differently: e.g. on x86-64, "b" ends up in register "rsi" in
           the first case and "rdi" in the second case.

           Another reason for CT_CUSTOM_FIELD_POS would be anonymous
           nested structures: we lost the information about having it
           here, so better safe (and forbid it) than sorry (and maybe
           crash).
        */
        if (force_lazy_struct(ct) < 0)
            return NULL;
        if (ct->ct_flags & CT_CUSTOM_FIELD_POS) {
            /* these NotImplementedErrors may be caught and ignored until
               a real call is made to a function of this type */
            PyErr_Format(PyExc_NotImplementedError,
                "ctype '%s' not supported as %s (it is a struct declared "
                "with \"...;\", but the C calling convention may depend "
                "on the missing fields)", ct->ct_name, place);
            return NULL;
        }

        n = PyDict_Size(ct->ct_stuff);
        nflat = 0;

        /* walk the fields, expanding arrays into repetitions; first,
           only count how many flattened fields there are */
        cf = (CFieldObject *)ct->ct_extra;
        for (i=0; i<n; i++) {
            Py_ssize_t flat;
            CTypeDescrObject *ct1;
            assert(cf != NULL);
            if (cf->cf_bitshift >= 0) {
                PyErr_Format(PyExc_NotImplementedError,
                     "ctype '%s' not supported as %s"
                     " (it is a struct with bit fields)",
                     ct->ct_name, place);
                return NULL;
            }
            flat = 1;
            ct1 = cf->cf_type;
            while (ct1->ct_flags & CT_ARRAY) {
                flat *= ct1->ct_length;
                ct1 = ct1->ct_itemdescr;
            }
            if (flat <= 0) {
                PyErr_Format(PyExc_NotImplementedError,
                     "ctype '%s' not supported as %s"
                     " (it is a struct with a zero-length array)",
                     ct->ct_name, place);
                return NULL;
            }
            nflat += flat;
            cf = cf->cf_next;
        }
        assert(cf == NULL);

        /* next, allocate and fill the flattened list */
        elements = fb_alloc(fb, (nflat + 1) * sizeof(ffi_type*));
        nflat = 0;
        cf = (CFieldObject *)ct->ct_extra;
        for (i=0; i<n; i++) {
            Py_ssize_t j, flat = 1;
            CTypeDescrObject *ct = cf->cf_type;
            while (ct->ct_flags & CT_ARRAY) {
                flat *= ct->ct_length;
                ct = ct->ct_itemdescr;
            }
            ffifield = fb_fill_type(fb, ct, 0);
            if (elements != NULL) {
                for (j=0; j<flat; j++)
                    elements[nflat++] = ffifield;
            }
            cf = cf->cf_next;
        }

        /* finally, allocate the FFI_TYPE_STRUCT */
        ffistruct = fb_alloc(fb, sizeof(ffi_type));
        if (ffistruct != NULL) {
            elements[nflat] = NULL;
            ffistruct->size = ct->ct_size;
            ffistruct->alignment = ct->ct_length;
            ffistruct->type = FFI_TYPE_STRUCT;
            ffistruct->elements = elements;
        }
        return ffistruct;
    }
    else {
        PyErr_Format(PyExc_NotImplementedError,
                     "ctype '%s' (size %zd) not supported as %s",
                     ct->ct_name, ct->ct_size, place);
        return NULL;
    }
}

#define ALIGN_ARG(n)  ((n) + 7) & ~7

static int fb_build(struct funcbuilder_s *fb, PyObject *fargs,
                    CTypeDescrObject *fresult)
{
    Py_ssize_t i, nargs = PyTuple_GET_SIZE(fargs);
    Py_ssize_t exchange_offset;
    cif_description_t *cif_descr;

    /* ffi buffer: start with a cif_description */
    cif_descr = fb_alloc(fb, sizeof(cif_description_t) +
                             nargs * sizeof(Py_ssize_t));

    /* ffi buffer: next comes an array of 'ffi_type*', one per argument */
    fb->atypes = fb_alloc(fb, nargs * sizeof(ffi_type*));
    fb->nargs = nargs;

    /* ffi buffer: next comes the result type */
    fb->rtype = fb_fill_type(fb, fresult, 1);
    if (PyErr_Occurred())
        return -1;
    if (cif_descr != NULL) {
        /* exchange data size */
        /* first, enough room for an array of 'nargs' pointers */
        exchange_offset = nargs * sizeof(void*);
        exchange_offset = ALIGN_ARG(exchange_offset);
        cif_descr->exchange_offset_arg[0] = exchange_offset;
        /* then enough room for the result --- which means at least
           sizeof(ffi_arg), according to the ffi docs */
        i = fb->rtype->size;
        if (i < (Py_ssize_t)sizeof(ffi_arg))
            i = sizeof(ffi_arg);
        exchange_offset += i;
    }
    else
        exchange_offset = 0;   /* not used */

    /* loop over the arguments */
    for (i=0; i<nargs; i++) {
        CTypeDescrObject *farg;
        ffi_type *atype;

        farg = (CTypeDescrObject *)PyTuple_GET_ITEM(fargs, i);
        /* convert arrays to pointers */
        if (farg->ct_flags & CT_ARRAY)
            farg = (CTypeDescrObject *)farg->ct_stuff;

        /* ffi buffer: fill in the ffi for the i'th argument */
        assert(farg != NULL);
        atype = fb_fill_type(fb, farg, 0);
        if (PyErr_Occurred())
            return -1;

        if (fb->atypes != NULL) {
            fb->atypes[i] = atype;
            /* exchange data size */
            exchange_offset = ALIGN_ARG(exchange_offset);
            cif_descr->exchange_offset_arg[1 + i] = exchange_offset;
            exchange_offset += atype->size;
        }
    }

    if (cif_descr != NULL) {
        /* exchange data size */
        /* we also align it to the next multiple of 8, in an attempt to
           work around bugs(?) of libffi like #241 */
        cif_descr->exchange_size = ALIGN_ARG(exchange_offset);
    }
    return 0;
}

#undef ALIGN_ARG

static void fb_cat_name(struct funcbuilder_s *fb, char *piece, int piecelen)
{
    if (fb->bufferp == NULL) {
        fb->nb_bytes += piecelen;
    }
    else {
        memcpy(fb->bufferp, piece, piecelen);
        fb->bufferp += piecelen;
    }
}

static int fb_build_name(struct funcbuilder_s *fb, PyObject *fargs,
                         CTypeDescrObject *fresult, int ellipsis, int fabi)
{
    Py_ssize_t i, nargs = PyTuple_GET_SIZE(fargs);
    fb->nargs = nargs;

    /* name: the function type name we build here is, like in C, made
       as follows:

         RESULT_TYPE_HEAD (*)(ARG_1_TYPE, ARG_2_TYPE, etc) RESULT_TYPE_TAIL
    */
    fb_cat_name(fb, fresult->ct_name, fresult->ct_name_position);
    fb_cat_name(fb, "(", 1);
    i = 2;
#if defined(MS_WIN32) && !defined(_WIN64)
    if (fabi == FFI_STDCALL) {
        fb_cat_name(fb, "__stdcall ", 10);
        i += 10;
    }
#endif
    fb_cat_name(fb, "*)(", 3);
    if (fb->fct) {
        i = fresult->ct_name_position + i;  /* between '(*' and ')(' */
        fb->fct->ct_name_position = i;
    }

    /* loop over the arguments */
    for (i=0; i<nargs; i++) {
        CTypeDescrObject *farg;

        farg = (CTypeDescrObject *)PyTuple_GET_ITEM(fargs, i);
        if (!CTypeDescr_Check(farg)) {
            PyErr_SetString(PyExc_TypeError, "expected a tuple of ctypes");
            return -1;
        }
        /* name: concatenate the name of the i'th argument's type */
        if (i > 0)
            fb_cat_name(fb, ", ", 2);
        fb_cat_name(fb, farg->ct_name, strlen(farg->ct_name));
    }

    /* name: add the '...' if needed */
    if (ellipsis) {
        if (nargs > 0)
            fb_cat_name(fb, ", ", 2);
        fb_cat_name(fb, "...", 3);
    }

    /* name: concatenate the tail of the result type */
    fb_cat_name(fb, ")", 1);
    fb_cat_name(fb, fresult->ct_name + fresult->ct_name_position,
                strlen(fresult->ct_name) - fresult->ct_name_position + 1);
    return 0;
}

static CTypeDescrObject *fb_prepare_ctype(struct funcbuilder_s *fb,
                                          PyObject *fargs,
                                          CTypeDescrObject *fresult,
                                          int ellipsis, int fabi)
{
    CTypeDescrObject *fct;

    fb->nb_bytes = 0;
    fb->bufferp = NULL;
    fb->fct = NULL;

    /* compute the total size needed for the name */
    if (fb_build_name(fb, fargs, fresult, ellipsis, fabi) < 0)
        return NULL;

    /* allocate the function type */
    fct = ctypedescr_new(fb->nb_bytes);
    if (fct == NULL)
        return NULL;
    fb->fct = fct;

    /* call again fb_build_name() to really build the ct_name */
    fb->bufferp = fct->ct_name;
    if (fb_build_name(fb, fargs, fresult, ellipsis, fabi) < 0)
        goto error;
    assert(fb->bufferp == fct->ct_name + fb->nb_bytes);

    fct->ct_extra = NULL;
    fct->ct_size = sizeof(void(*)(void));
    fct->ct_flags = CT_FUNCTIONPTR;
    return fct;

 error:
    Py_DECREF(fct);
    return NULL;
}

static cif_description_t *fb_prepare_cif(PyObject *fargs,
                                         CTypeDescrObject *fresult,
                                         ffi_abi fabi)
{
    char *buffer;
    cif_description_t *cif_descr;
    struct funcbuilder_s funcbuffer;

    funcbuffer.nb_bytes = 0;
    funcbuffer.bufferp = NULL;

    /* compute the total size needed in the buffer for libffi */
    if (fb_build(&funcbuffer, fargs, fresult) < 0)
        return NULL;

    /* allocate the buffer */
    buffer = PyObject_Malloc(funcbuffer.nb_bytes);
    if (buffer == NULL) {
        PyErr_NoMemory();
        return NULL;
    }

    /* call again fb_build() to really build the libffi data structures */
    funcbuffer.bufferp = buffer;
    if (fb_build(&funcbuffer, fargs, fresult) < 0)
        goto error;
    assert(funcbuffer.bufferp == buffer + funcbuffer.nb_bytes);

    cif_descr = (cif_description_t *)buffer;
    if (ffi_prep_cif(&cif_descr->cif, fabi, funcbuffer.nargs,
                     funcbuffer.rtype, funcbuffer.atypes) != FFI_OK) {
        PyErr_SetString(PyExc_SystemError,
                        "libffi failed to build this function type");
        goto error;
    }
    return cif_descr;

 error:
    PyObject_Free(buffer);
    return NULL;
}

static PyObject *new_function_type(PyObject *fargs,   /* tuple */
                                   CTypeDescrObject *fresult,
                                   int ellipsis, int fabi)
{
    PyObject *fabiobj;
    CTypeDescrObject *fct;
    struct funcbuilder_s funcbuilder;
    Py_ssize_t i;
    const void **unique_key;

    if ((fresult->ct_size < 0 && !(fresult->ct_flags & CT_VOID)) ||
        (fresult->ct_flags & CT_ARRAY)) {
        char *msg;
        if (fresult->ct_flags & CT_IS_OPAQUE)
            msg = "result type '%s' is opaque";
        else
            msg = "invalid result type: '%s'";
        PyErr_Format(PyExc_TypeError, msg, fresult->ct_name);
        return NULL;
    }

    fct = fb_prepare_ctype(&funcbuilder, fargs, fresult, ellipsis, fabi);
    if (fct == NULL)
        return NULL;

    if (!ellipsis) {
        /* Functions with '...' varargs are stored without a cif_descr
           at all.  The cif is computed on every call from the actual
           types passed in.  For all other functions, the cif_descr
           is computed here. */
        cif_description_t *cif_descr;

        cif_descr = fb_prepare_cif(fargs, fresult, fabi);
        if (cif_descr == NULL) {
            if (PyErr_ExceptionMatches(PyExc_NotImplementedError)) {
                PyErr_Clear();   /* will get the exception if we see an
                                    actual call */
            }
            else
                goto error;
        }

        fct->ct_extra = (char *)cif_descr;
    }

    /* build the signature, given by a tuple of ctype objects */
    fct->ct_stuff = PyTuple_New(2 + funcbuilder.nargs);
    if (fct->ct_stuff == NULL)
        goto error;
    fabiobj = PyInt_FromLong(fabi);
    if (fabiobj == NULL)
        goto error;
    PyTuple_SET_ITEM(fct->ct_stuff, 0, fabiobj);

    Py_INCREF(fresult);
    PyTuple_SET_ITEM(fct->ct_stuff, 1, (PyObject *)fresult);
    for (i=0; i<funcbuilder.nargs; i++) {
        PyObject *o = PyTuple_GET_ITEM(fargs, i);
        /* convert arrays into pointers */
        if (((CTypeDescrObject *)o)->ct_flags & CT_ARRAY)
            o = ((CTypeDescrObject *)o)->ct_stuff;
        Py_INCREF(o);
        PyTuple_SET_ITEM(fct->ct_stuff, 2 + i, o);
    }

    /* [ctresult, ellipsis+abi, num_args, ctargs...] */
    unique_key = alloca((3 + funcbuilder.nargs) * sizeof(void *));
    unique_key[0] = fresult;
    unique_key[1] = (const void *)(Py_ssize_t)((fabi << 1) | !!ellipsis);
    unique_key[2] = (const void *)(Py_ssize_t)(funcbuilder.nargs);
    for (i=0; i<funcbuilder.nargs; i++)
        unique_key[3 + i] = PyTuple_GET_ITEM(fct->ct_stuff, 2 + i);
    return get_unique_type(fct, unique_key, 3 + funcbuilder.nargs);

 error:
    Py_DECREF(fct);
    return NULL;
}

static PyObject *b_new_function_type(PyObject *self, PyObject *args)
{
    PyObject *fargs;
    CTypeDescrObject *fresult;
    int ellipsis = 0, fabi = FFI_DEFAULT_ABI;

    if (!PyArg_ParseTuple(args, "O!O!|ii:new_function_type",
                          &PyTuple_Type, &fargs,
                          &CTypeDescr_Type, &fresult,
                          &ellipsis,
                          &fabi))
        return NULL;

    return new_function_type(fargs, fresult, ellipsis, fabi);
}

static int convert_from_object_fficallback(char *result,
                                           CTypeDescrObject *ctype,
                                           PyObject *pyobj,
                                           int encode_result_for_libffi)
{
    /* work work work around a libffi irregularity: for integer return
       types we have to fill at least a complete 'ffi_arg'-sized result
       buffer. */
    if (ctype->ct_size < (Py_ssize_t)sizeof(ffi_arg)) {
        if (ctype->ct_flags & CT_VOID) {
            if (pyobj == Py_None) {
                return 0;
            }
            else {
                PyErr_SetString(PyExc_TypeError,
                    "callback with the return type 'void' must return None");
                return -1;
            }
        }
        if (!encode_result_for_libffi)
            goto skip;
        if (ctype->ct_flags & CT_PRIMITIVE_SIGNED) {
            PY_LONG_LONG value;
            /* It's probably fine to always zero-extend, but you never
               know: maybe some code somewhere expects a negative
               'short' result to be returned into EAX as a 32-bit
               negative number.  Better safe than sorry.  This code
               is about that case.  Let's ignore this for enums.
            */
            /* do a first conversion only to detect overflows.  This
               conversion produces stuff that is otherwise ignored. */
            if (convert_from_object(result, ctype, pyobj) < 0)
                return -1;
            /* manual inlining and tweaking of convert_from_object()
               in order to write a whole 'ffi_arg'. */
            value = _my_PyLong_AsLongLong(pyobj);
            if (value == -1 && PyErr_Occurred())
                return -1;
            write_raw_integer_data(result, value, sizeof(ffi_arg));
            return 0;
        }
        else if (ctype->ct_flags & (CT_PRIMITIVE_CHAR | CT_PRIMITIVE_SIGNED |
                                    CT_PRIMITIVE_UNSIGNED)) {
            /* zero extension: fill the '*result' with zeros, and (on big-
               endian machines) correct the 'result' pointer to write to */
            memset(result, 0, sizeof(ffi_arg));
#ifdef WORDS_BIGENDIAN
            result += (sizeof(ffi_arg) - ctype->ct_size);
#endif
        }
    }
 skip:
    return convert_from_object(result, ctype, pyobj);
}

static void _my_PyErr_WriteUnraisable(char *objdescr, PyObject *obj,
                                      char *extra_error_line)
{
    /* like PyErr_WriteUnraisable(), but write a full traceback */
    PyObject *f, *t, *v, *tb;
    PyErr_Fetch(&t, &v, &tb);
#if PY_MAJOR_VERSION >= 3
    /* jump through hoops to ensure the tb is attached to v, on Python 3 */
    PyErr_NormalizeException(&t, &v, &tb);
    if (tb == NULL) {
        tb = Py_None;
        Py_INCREF(tb);
    }
    PyException_SetTraceback(v, tb);
#endif
    f = PySys_GetObject("stderr");
    if (f != NULL) {
        if (obj != NULL) {
            PyFile_WriteString(objdescr, f);
            PyFile_WriteObject(obj, f, 0);
            PyFile_WriteString(":\n", f);
        }
        if (extra_error_line != NULL)
            PyFile_WriteString(extra_error_line, f);
        PyErr_Display(t, v, tb);
    }
    Py_XDECREF(t);
    Py_XDECREF(v);
    Py_XDECREF(tb);
}

static void general_invoke_callback(int decode_args_from_libffi,
                                    void *result, char *args, void *userdata)
{
    PyObject *cb_args = (PyObject *)userdata;
    CTypeDescrObject *ct = (CTypeDescrObject *)PyTuple_GET_ITEM(cb_args, 0);
    PyObject *signature = ct->ct_stuff;
    PyObject *py_ob = PyTuple_GET_ITEM(cb_args, 1);
    PyObject *py_args = NULL;
    PyObject *py_res = NULL;
    PyObject *py_rawerr;
    PyObject *onerror_cb;
    Py_ssize_t i, n;
    char *extra_error_line = NULL;

#define SIGNATURE(i)  ((CTypeDescrObject *)PyTuple_GET_ITEM(signature, i))

    Py_INCREF(cb_args);

    n = PyTuple_GET_SIZE(signature) - 2;
    py_args = PyTuple_New(n);
    if (py_args == NULL)
        goto error;

    for (i=0; i<n; i++) {
        char *a_src;
        PyObject *a;
        CTypeDescrObject *a_ct = SIGNATURE(2 + i);

        if (decode_args_from_libffi) {
            a_src = ((void **)args)[i];
        }
        else {
            a_src = args + i * 8;
            if (a_ct->ct_flags & (CT_IS_LONGDOUBLE | CT_STRUCT | CT_UNION))
                a_src = *(char **)a_src;
        }
        a = convert_to_object(a_src, a_ct);
        if (a == NULL)
            goto error;
        PyTuple_SET_ITEM(py_args, i, a);
    }

    py_res = PyObject_Call(py_ob, py_args, NULL);
    if (py_res == NULL)
        goto error;
    if (convert_from_object_fficallback(result, SIGNATURE(1), py_res,
                                        decode_args_from_libffi) < 0) {
        extra_error_line = "Trying to convert the result back to C:\n";
        goto error;
    }
 done:
    Py_XDECREF(py_args);
    Py_XDECREF(py_res);
    Py_DECREF(cb_args);
    return;

 error:
    if (SIGNATURE(1)->ct_size > 0) {
        py_rawerr = PyTuple_GET_ITEM(cb_args, 2);
        memcpy(result, PyBytes_AS_STRING(py_rawerr),
                       PyBytes_GET_SIZE(py_rawerr));
    }
    onerror_cb = PyTuple_GET_ITEM(cb_args, 3);
    if (onerror_cb == Py_None) {
        _my_PyErr_WriteUnraisable("From cffi callback ", py_ob,
                                  extra_error_line);
    }
    else {
        PyObject *exc1, *val1, *tb1, *res1, *exc2, *val2, *tb2;
        PyErr_Fetch(&exc1, &val1, &tb1);
        PyErr_NormalizeException(&exc1, &val1, &tb1);
        res1 = PyObject_CallFunctionObjArgs(onerror_cb,
                                            exc1 ? exc1 : Py_None,
                                            val1 ? val1 : Py_None,
                                            tb1  ? tb1  : Py_None,
                                            NULL);
        if (res1 != NULL) {
            if (res1 != Py_None)
                convert_from_object_fficallback(result, SIGNATURE(1), res1,
                                                decode_args_from_libffi);
            Py_DECREF(res1);
        }
        if (!PyErr_Occurred()) {
            Py_XDECREF(exc1);
            Py_XDECREF(val1);
            Py_XDECREF(tb1);
        }
        else {
            /* double exception! print a double-traceback... */
            PyErr_Fetch(&exc2, &val2, &tb2);
            PyErr_Restore(exc1, val1, tb1);
            _my_PyErr_WriteUnraisable("From cffi callback ", py_ob,
                                      extra_error_line);
            PyErr_Restore(exc2, val2, tb2);
            extra_error_line = ("\nDuring the call to 'onerror', "
                                "another exception occurred:\n\n");
            _my_PyErr_WriteUnraisable(NULL, NULL, extra_error_line);
        }
    }
    goto done;

#undef SIGNATURE
}

static void invoke_callback(ffi_cif *cif, void *result, void **args,
                            void *userdata)
{
    save_errno();
    {
        PyGILState_STATE state = gil_ensure();
        general_invoke_callback(1, result, (char *)args, userdata);
        gil_release(state);
    }
    restore_errno();
}

static PyObject *prepare_callback_info_tuple(CTypeDescrObject *ct,
                                             PyObject *ob,
                                             PyObject *error_ob,
                                             PyObject *onerror_ob,
                                             int decode_args_from_libffi)
{
    CTypeDescrObject *ctresult;
    PyObject *py_rawerr, *infotuple;
    Py_ssize_t size;

    if (!(ct->ct_flags & CT_FUNCTIONPTR)) {
        PyErr_Format(PyExc_TypeError, "expected a function ctype, got '%s'",
                     ct->ct_name);
        return NULL;
    }
    if (!PyCallable_Check(ob)) {
        PyErr_Format(PyExc_TypeError,
                     "expected a callable object, not %.200s",
                     Py_TYPE(ob)->tp_name);
        return NULL;
    }
    if (onerror_ob != Py_None && !PyCallable_Check(onerror_ob)) {
        PyErr_Format(PyExc_TypeError,
                     "expected a callable object for 'onerror', not %.200s",
                     Py_TYPE(onerror_ob)->tp_name);
        return NULL;
    }

    ctresult = (CTypeDescrObject *)PyTuple_GET_ITEM(ct->ct_stuff, 1);
    size = ctresult->ct_size;
    if (size < (Py_ssize_t)sizeof(ffi_arg))
        size = sizeof(ffi_arg);
    py_rawerr = PyBytes_FromStringAndSize(NULL, size);
    if (py_rawerr == NULL)
        return NULL;
    memset(PyBytes_AS_STRING(py_rawerr), 0, size);
    if (error_ob != Py_None) {
        if (convert_from_object_fficallback(
                PyBytes_AS_STRING(py_rawerr), ctresult, error_ob,
                decode_args_from_libffi) < 0) {
            Py_DECREF(py_rawerr);
            return NULL;
        }
    }
    infotuple = Py_BuildValue("OOOO", ct, ob, py_rawerr, onerror_ob);
    Py_DECREF(py_rawerr);

#ifdef WITH_THREAD
    /* We must setup the GIL here, in case the callback is invoked in
       some other non-Pythonic thread.  This is the same as ctypes. */
    PyEval_InitThreads();
#endif

    return infotuple;
}

static PyObject *b_callback(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ct;
    CDataObject *cd;
    PyObject *ob, *error_ob = Py_None, *onerror_ob = Py_None;
    PyObject *infotuple;
    cif_description_t *cif_descr;
    ffi_closure *closure;

    if (!PyArg_ParseTuple(args, "O!O|OO:callback", &CTypeDescr_Type, &ct, &ob,
                          &error_ob, &onerror_ob))
        return NULL;

    infotuple = prepare_callback_info_tuple(ct, ob, error_ob, onerror_ob, 1);
    if (infotuple == NULL)
        return NULL;

    closure = cffi_closure_alloc();

    cd = PyObject_GC_New(CDataObject, &CDataOwningGC_Type);
    if (cd == NULL)
        goto error;
    Py_INCREF(ct);
    cd->c_type = ct;
    cd->c_data = (char *)closure;
    cd->c_weakreflist = NULL;
    PyObject_GC_Track(cd);

    cif_descr = (cif_description_t *)ct->ct_extra;
    if (cif_descr == NULL) {
        PyErr_Format(PyExc_NotImplementedError,
                     "%s: callback with unsupported argument or "
                     "return type or with '...'", ct->ct_name);
        goto error;
    }
    if (ffi_prep_closure(closure, &cif_descr->cif,
                         invoke_callback, infotuple) != FFI_OK) {
        PyErr_SetString(PyExc_SystemError,
                        "libffi failed to build this callback");
        goto error;
    }
    assert(closure->user_data == infotuple);
    return (PyObject *)cd;

 error:
    closure->user_data = NULL;
    if (cd == NULL)
        cffi_closure_free(closure);
    else
        Py_DECREF(cd);
    Py_XDECREF(infotuple);
    return NULL;
}

static PyObject *b_new_enum_type(PyObject *self, PyObject *args)
{
    char *ename;
    PyObject *enumerators, *enumvalues;
    PyObject *dict1 = NULL, *dict2 = NULL, *combined = NULL, *tmpkey = NULL;
    int name_size;
    CTypeDescrObject *td, *basetd;
    Py_ssize_t i, n;

    if (!PyArg_ParseTuple(args, "sO!O!O!:new_enum_type",
                          &ename,
                          &PyTuple_Type, &enumerators,
                          &PyTuple_Type, &enumvalues,
                          &CTypeDescr_Type, &basetd))
        return NULL;

    n = PyTuple_GET_SIZE(enumerators);
    if (n != PyTuple_GET_SIZE(enumvalues)) {
        PyErr_SetString(PyExc_ValueError,
                        "tuple args must have the same size");
        return NULL;
    }

    if (!(basetd->ct_flags & (CT_PRIMITIVE_SIGNED|CT_PRIMITIVE_UNSIGNED))) {
        PyErr_SetString(PyExc_TypeError,
                        "expected a primitive signed or unsigned base type");
        return NULL;
    }

    dict1 = PyDict_New();
    if (dict1 == NULL)
        goto error;
    dict2 = PyDict_New();
    if (dict2 == NULL)
        goto error;

    for (i=n; --i >= 0; ) {
        long long lvalue;
        PyObject *value = PyTuple_GET_ITEM(enumvalues, i);
        tmpkey = PyTuple_GET_ITEM(enumerators, i);
        Py_INCREF(tmpkey);
        if (!PyText_Check(tmpkey)) {
#if PY_MAJOR_VERSION < 3
            if (PyUnicode_Check(tmpkey)) {
                char *text = PyText_AsUTF8(tmpkey);
                if (text == NULL)
                    goto error;
                Py_DECREF(tmpkey);
                tmpkey = PyString_FromString(text);
                if (tmpkey == NULL)
                    goto error;
            }
            else
#endif
            {
                PyErr_SetString(PyExc_TypeError,
                                "enumerators must be a list of strings");
                goto error;
            }
        }
        if (convert_from_object((char*)&lvalue, basetd, value) < 0)
            goto error;     /* out-of-range or badly typed 'value' */
        if (PyDict_SetItem(dict1, tmpkey, value) < 0)
            goto error;
        if (PyDict_SetItem(dict2, value, tmpkey) < 0)
            goto error;
        Py_DECREF(tmpkey);
        tmpkey = NULL;
    }

    combined = PyTuple_Pack(2, dict1, dict2);
    if (combined == NULL)
        goto error;

    Py_CLEAR(dict2);
    Py_CLEAR(dict1);

    name_size = strlen(ename) + 1;
    td = ctypedescr_new(name_size);
    if (td == NULL)
        goto error;

    memcpy(td->ct_name, ename, name_size);
    td->ct_stuff = combined;
    td->ct_size = basetd->ct_size;
    td->ct_length = basetd->ct_length;   /* alignment */
    td->ct_extra = basetd->ct_extra;     /* ffi type  */
    td->ct_flags = basetd->ct_flags | CT_IS_ENUM;
    td->ct_name_position = name_size - 1;
    return (PyObject *)td;

 error:
    Py_XDECREF(tmpkey);
    Py_XDECREF(combined);
    Py_XDECREF(dict2);
    Py_XDECREF(dict1);
    return NULL;
}

static PyObject *b_alignof(PyObject *self, PyObject *arg)
{
    int align;
    if (!CTypeDescr_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, "expected a 'ctype' object");
        return NULL;
    }
    align = get_alignment((CTypeDescrObject *)arg);
    if (align < 0)
        return NULL;
    return PyInt_FromLong(align);
}

static PyObject *b_sizeof(PyObject *self, PyObject *arg)
{
    Py_ssize_t size;

    if (CData_Check(arg)) {
        CDataObject *cd = (CDataObject *)arg;

        if (cd->c_type->ct_flags & CT_ARRAY)
            size = get_array_length(cd) * cd->c_type->ct_itemdescr->ct_size;
        else
            size = cd->c_type->ct_size;
    }
    else if (CTypeDescr_Check(arg)) {
        size = ((CTypeDescrObject *)arg)->ct_size;
        if (size < 0) {
            PyErr_Format(PyExc_ValueError, "ctype '%s' is of unknown size",
                         ((CTypeDescrObject *)arg)->ct_name);
            return NULL;
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError,
                        "expected a 'cdata' or 'ctype' object");
        return NULL;
    }
    return PyInt_FromSsize_t(size);
}

static PyObject *b_typeof(PyObject *self, PyObject *arg)
{
    PyObject *res;

    if (!CData_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, "expected a 'cdata' object");
        return NULL;
    }
    res = (PyObject *)((CDataObject *)arg)->c_type;
    Py_INCREF(res);
    return res;
}

static CTypeDescrObject *direct_typeoffsetof(CTypeDescrObject *ct,
                                             PyObject *fieldname,
                                             int following, Py_ssize_t *offset)
{
    /* Does not return a new reference! */
    CTypeDescrObject *res;
    CFieldObject *cf;

    if (PyTextAny_Check(fieldname)) {
        if (!following && (ct->ct_flags & CT_POINTER))
            ct = ct->ct_itemdescr;
        if (!(ct->ct_flags & (CT_STRUCT|CT_UNION))) {
            PyErr_SetString(PyExc_TypeError,
                            "with a field name argument, expected a "
                            "struct or union ctype");
            return NULL;
        }
        if (force_lazy_struct(ct) <= 0) {
            if (!PyErr_Occurred())
                PyErr_SetString(PyExc_TypeError, "struct/union is opaque");
            return NULL;
        }
        cf = (CFieldObject *)PyDict_GetItem(ct->ct_stuff, fieldname);
        if (cf == NULL) {
            PyErr_SetObject(PyExc_KeyError, fieldname);
            return NULL;
        }
        if (cf->cf_bitshift >= 0) {
            PyErr_SetString(PyExc_TypeError, "not supported for bitfields");
            return NULL;
        }
        res = cf->cf_type;
        *offset = cf->cf_offset;
    }
    else {
        ssize_t index = PyInt_AsSsize_t(fieldname);
        if (index < 0 && PyErr_Occurred()) {
            PyErr_SetString(PyExc_TypeError,
                            "field name or array index expected");
            return NULL;
        }

        if (!(ct->ct_flags & (CT_ARRAY|CT_POINTER)) ||
                ct->ct_itemdescr->ct_size < 0) {
            PyErr_SetString(PyExc_TypeError, "with an integer argument, "
                                             "expected an array ctype or a "
                                             "pointer to non-opaque");
            return NULL;
        }
        res = ct->ct_itemdescr;
        *offset = index * ct->ct_itemdescr->ct_size;
        if ((*offset / ct->ct_itemdescr->ct_size) != index) {
            PyErr_SetString(PyExc_OverflowError,
                            "array offset would overflow a Py_ssize_t");
            return NULL;
        }
    }
    return res;
}

static PyObject *b_typeoffsetof(PyObject *self, PyObject *args)
{
    PyObject *res, *fieldname;
    CTypeDescrObject *ct;
    Py_ssize_t offset;
    int following = 0;

    if (!PyArg_ParseTuple(args, "O!O|i:typeoffsetof",
                          &CTypeDescr_Type, &ct, &fieldname, &following))
        return NULL;

    res = (PyObject *)direct_typeoffsetof(ct, fieldname, following, &offset);
    if (res == NULL)
        return NULL;

    return Py_BuildValue("(On)", res, offset);
}

static PyObject *b_rawaddressof(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ct;
    CDataObject *cd;
    Py_ssize_t offset;
    int accepted_flags;

    if (!PyArg_ParseTuple(args, "O!O!n:rawaddressof",
                          &CTypeDescr_Type, &ct,
                          &CData_Type, &cd,
                          &offset))
        return NULL;

    accepted_flags = CT_STRUCT | CT_UNION | CT_ARRAY | CT_POINTER;
    if ((cd->c_type->ct_flags & accepted_flags) == 0) {
        PyErr_SetString(PyExc_TypeError,
                        "expected a cdata struct/union/array/pointer object");
        return NULL;
    }
    if ((ct->ct_flags & CT_POINTER) == 0) {
        PyErr_SetString(PyExc_TypeError,
                        "expected a pointer ctype");
        return NULL;
    }
    return new_simple_cdata(cd->c_data + offset, ct);
}

static PyObject *b_getcname(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ct;
    char *replace_with, *p, *s;
    Py_ssize_t namelen, replacelen;

    if (!PyArg_ParseTuple(args, "O!s:getcname",
                          &CTypeDescr_Type, &ct, &replace_with))
        return NULL;

    namelen = strlen(ct->ct_name);
    replacelen = strlen(replace_with);
    s = p = alloca(namelen + replacelen + 1);
    memcpy(p, ct->ct_name, ct->ct_name_position);
    p += ct->ct_name_position;
    memcpy(p, replace_with, replacelen);
    p += replacelen;
    memcpy(p, ct->ct_name + ct->ct_name_position,
           namelen - ct->ct_name_position);

    return PyText_FromStringAndSize(s, namelen + replacelen);
}

static PyObject *b_string(PyObject *self, PyObject *args, PyObject *kwds)
{
    CDataObject *cd;
    Py_ssize_t maxlen = -1;
    static char *keywords[] = {"cdata", "maxlen", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|n:string", keywords,
                                     &CData_Type, &cd, &maxlen))
        return NULL;

    if (cd->c_type->ct_itemdescr != NULL &&
        cd->c_type->ct_itemdescr->ct_flags & (CT_PRIMITIVE_CHAR |
                                              CT_PRIMITIVE_SIGNED |
                                              CT_PRIMITIVE_UNSIGNED)) {
        Py_ssize_t length = maxlen;
        if (cd->c_data == NULL) {
            PyObject *s = cdata_repr(cd);
            if (s != NULL) {
                PyErr_Format(PyExc_RuntimeError,
                             "cannot use string() on %s",
                             PyText_AS_UTF8(s));
                Py_DECREF(s);
            }
            return NULL;
        }
        if (length < 0 && cd->c_type->ct_flags & CT_ARRAY) {
            length = get_array_length(cd);
        }
        if (cd->c_type->ct_itemdescr->ct_size == sizeof(char)) {
            const char *start = cd->c_data;
            if (length < 0) {
                /*READ(start, 1)*/
                length = strlen(start);
                /*READ(start, length)*/
            }
            else {
                const char *end;
                /*READ(start, length)*/
                end = (const char *)memchr(start, 0, length);
                if (end != NULL)
                    length = end - start;
            }
            return PyBytes_FromStringAndSize(start, length);
        }
#ifdef HAVE_WCHAR_H
        else if (cd->c_type->ct_itemdescr->ct_flags & CT_PRIMITIVE_CHAR) {
            const wchar_t *start = (wchar_t *)cd->c_data;
            assert(cd->c_type->ct_itemdescr->ct_size == sizeof(wchar_t));
            if (length < 0) {
                /*READ(start, sizeof(wchar_t))*/
                length = 0;
                while (start[length])
                    length++;
                /*READ(start, sizeof(wchar_t) * length)*/
            }
            else {
                /*READ(start, sizeof(wchar_t) * length)*/
                maxlen = length;
                length = 0;
                while (length < maxlen && start[length])
                    length++;
            }
            return _my_PyUnicode_FromWideChar(start, length);
        }
#endif
    }
    else if (cd->c_type->ct_flags & CT_IS_ENUM) {
        return convert_cdata_to_enum_string(cd, 0);
    }
    else if (cd->c_type->ct_flags & CT_IS_BOOL) {
        /* fall through to TypeError */
    }
    else if (cd->c_type->ct_flags & (CT_PRIMITIVE_CHAR |
                                     CT_PRIMITIVE_SIGNED |
                                     CT_PRIMITIVE_UNSIGNED)) {
        /*READ(cd->c_data, cd->c_type->ct_size)*/
        if (cd->c_type->ct_size == sizeof(char))
            return PyBytes_FromStringAndSize(cd->c_data, 1);
#ifdef HAVE_WCHAR_H
        else if (cd->c_type->ct_flags & CT_PRIMITIVE_CHAR) {
            assert(cd->c_type->ct_size == sizeof(wchar_t));
            return _my_PyUnicode_FromWideChar((wchar_t *)cd->c_data, 1);
        }
#endif
    }
    PyErr_Format(PyExc_TypeError, "string(): unexpected cdata '%s' argument",
                 cd->c_type->ct_name);
    return NULL;
}

static PyObject *b_buffer(PyObject *self, PyObject *args, PyObject *kwds)
{
    CDataObject *cd;
    Py_ssize_t size = -1;
    static char *keywords[] = {"cdata", "size", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|n:buffer", keywords,
                                     &CData_Type, &cd, &size))
        return NULL;

    if (cd->c_type->ct_flags & CT_POINTER) {
        if (size < 0)
            size = cd->c_type->ct_itemdescr->ct_size;
    }
    else if (cd->c_type->ct_flags & CT_ARRAY) {
        if (size < 0)
            size = get_array_length(cd) * cd->c_type->ct_itemdescr->ct_size;
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "expected a pointer or array cdata, got '%s'",
                     cd->c_type->ct_name);
        return NULL;
    }
    if (size < 0) {
        PyErr_Format(PyExc_TypeError,
                     "don't know the size pointed to by '%s'",
                     cd->c_type->ct_name);
        return NULL;
    }
    /*WRITE(cd->c_data, size)*/
    return minibuffer_new(cd->c_data, size, (PyObject *)cd);
}

static PyObject *b_get_errno(PyObject *self, PyObject *noarg)
{
    int err;
    restore_errno_only();
    err = errno;
    errno = 0;
    return PyInt_FromLong(err);
}

static PyObject *b_set_errno(PyObject *self, PyObject *arg)
{
    long ival = PyInt_AsLong(arg);
    if (ival == -1 && PyErr_Occurred())
        return NULL;
    else if (ival < INT_MIN || ival > INT_MAX) {
        PyErr_SetString(PyExc_OverflowError, "errno value too large");
        return NULL;
    }
    errno = (int)ival;
    save_errno_only();
    errno = 0;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *newp_handle(CTypeDescrObject *ct_voidp, PyObject *x)
{
    CDataObject_own_structptr *cd;
    cd = (CDataObject_own_structptr *)PyObject_GC_New(CDataObject_own_structptr,
                                                      &CDataOwningGC_Type);
    if (cd == NULL)
        return NULL;
    Py_INCREF(ct_voidp);
    cd->head.c_type = ct_voidp;
    cd->head.c_data = (char *)cd;
    cd->head.c_weakreflist = NULL;
    Py_INCREF(x);
    cd->structobj = x;
    PyObject_GC_Track(cd);
    return (PyObject *)cd;
}

static PyObject *b_newp_handle(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ct;
    PyObject *x;
    if (!PyArg_ParseTuple(args, "O!O", &CTypeDescr_Type, &ct, &x))
        return NULL;

    if (!(ct->ct_flags & CT_IS_VOID_PTR)) {
        PyErr_Format(PyExc_TypeError, "needs 'void *', got '%s'", ct->ct_name);
        return NULL;
    }

    return newp_handle(ct, x);
}

static PyObject *b_from_handle(PyObject *self, PyObject *arg)
{
    CTypeDescrObject *ct;
    CDataObject_own_structptr *orgcd;
    PyObject *x;
    if (!CData_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, "expected a 'cdata' object");
        return NULL;
    }
    ct = ((CDataObject *)arg)->c_type;
    if (!(ct->ct_flags & CT_CAST_ANYTHING)) {
        PyErr_Format(PyExc_TypeError,
                     "expected a 'cdata' object with a 'void *' out of "
                     "new_handle(), got '%s'", ct->ct_name);
        return NULL;
    }
    orgcd = (CDataObject_own_structptr *)((CDataObject *)arg)->c_data;
    if (!orgcd) {
        PyErr_SetString(PyExc_RuntimeError,
                        "cannot use from_handle() on NULL pointer");
        return NULL;
    }
    if (Py_REFCNT(orgcd) <= 0 || Py_TYPE(orgcd) != &CDataOwningGC_Type) {
        Py_FatalError("ffi.from_handle() detected that the address passed "
                      "points to garbage. If it is really the result of "
                      "ffi.new_handle(), then the Python object has already "
                      "been garbage collected");
    }
    x = orgcd->structobj;
    Py_INCREF(x);
    return x;
}

static int _my_PyObject_GetContiguousBuffer(PyObject *x, Py_buffer *view,
                                            int writable_only)
{
#if PY_MAJOR_VERSION < 3
    /* Some objects only support the buffer interface and CPython doesn't
       translate it into the memoryview interface, mess.  Hack a very
       minimal content for 'view'.  Don't care if the other fields are
       uninitialized: we only call PyBuffer_Release(), which only reads
       'view->obj'. */
    PyBufferProcs *pb = x->ob_type->tp_as_buffer;
    if (pb && !pb->bf_releasebuffer) {
        /* we used to try all three in some vaguely sensible order,
           i.e. first the write.  But trying to call the write on a
           read-only buffer fails with TypeError.  So we use a less-
           sensible order now.  See test_from_buffer_more_cases.

           If 'writable_only', we only try bf_getwritebuffer.
        */
        readbufferproc proc = NULL;
        if (!writable_only) {
            proc = (readbufferproc)pb->bf_getreadbuffer;
            if (!proc)
                proc = (readbufferproc)pb->bf_getcharbuffer;
        }
        if (!proc)
            proc = (readbufferproc)pb->bf_getwritebuffer;

        if (proc && pb->bf_getsegcount) {
            if ((*pb->bf_getsegcount)(x, NULL) != 1) {
                PyErr_SetString(PyExc_TypeError,
                                "expected a single-segment buffer object");
                return -1;
            }
            view->len = (*proc)(x, 0, &view->buf);
            if (view->len < 0)
                return -1;
            view->obj = x;
            Py_INCREF(x);
            return 0;
        }
    }
#endif

    if (PyObject_GetBuffer(x, view, writable_only ? PyBUF_WRITABLE
                                                  : PyBUF_SIMPLE) < 0)
        return -1;

    if (!PyBuffer_IsContiguous(view, 'A')) {
        PyBuffer_Release(view);
        PyErr_SetString(PyExc_TypeError, "contiguous buffer expected");
        return -1;
    }
    return 0;
}

static int invalid_input_buffer_type(PyObject *x)
{
#if PY_MAJOR_VERSION < 3
    if (PyBuffer_Check(x)) {
        /* XXX fish fish fish in an inofficial way */
        typedef struct {
            PyObject_HEAD
            PyObject *b_base;
        } _my_PyBufferObject;

        _my_PyBufferObject *b = (_my_PyBufferObject *)x;
        x = b->b_base;
        if (x == NULL)
            return 0;
    }
    else
#endif
#if PY_MAJOR_VERSION > 2 || PY_MINOR_VERSION > 6
    if (PyMemoryView_Check(x)) {
        x = PyMemoryView_GET_BASE(x);
        if (x == NULL)
            return 0;
    }
    else
#endif
        ;

    if (PyBytes_Check(x) || PyUnicode_Check(x))
        return 1;
    if (PyByteArray_Check(x)) /* <= this one here for PyPy compatibility */
        return 1;
    return 0;
}

static PyObject *direct_from_buffer(CTypeDescrObject *ct, PyObject *x)
{
    CDataObject *cd;
    Py_buffer *view;

    if (invalid_input_buffer_type(x)) {
        PyErr_SetString(PyExc_TypeError,
                        "from_buffer() cannot return the address of the "
                        "raw string within a "STR_OR_BYTES" or unicode or "
                        "bytearray object");
        return NULL;
    }

    view = PyObject_Malloc(sizeof(Py_buffer));
    if (view == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    if (_my_PyObject_GetContiguousBuffer(x, view, 0) < 0)
        goto error1;

    cd = (CDataObject *)PyObject_GC_New(CDataObject_owngc_frombuf,
                                        &CDataOwningGC_Type);
    if (cd == NULL)
        goto error2;

    Py_INCREF(ct);
    cd->c_type = ct;
    cd->c_data = view->buf;
    cd->c_weakreflist = NULL;
    ((CDataObject_owngc_frombuf *)cd)->length = view->len;
    ((CDataObject_owngc_frombuf *)cd)->bufferview = view;
    PyObject_GC_Track(cd);
    return (PyObject *)cd;

 error2:
    PyBuffer_Release(view);
 error1:
    PyObject_Free(view);
    return NULL;
}

static PyObject *b_from_buffer(PyObject *self, PyObject *args)
{
    CTypeDescrObject *ct;
    PyObject *x;

    if (!PyArg_ParseTuple(args, "O!O", &CTypeDescr_Type, &ct, &x))
        return NULL;

    if (!(ct->ct_flags & CT_IS_UNSIZED_CHAR_A)) {
        PyErr_Format(PyExc_TypeError, "needs 'char[]', got '%s'", ct->ct_name);
        return NULL;
    }
    return direct_from_buffer(ct, x);
}

static int _fetch_as_buffer(PyObject *x, Py_buffer *view, int writable_only)
{
    if (CData_Check(x)) {
        CTypeDescrObject *ct = ((CDataObject *)x)->c_type;
        if (!(ct->ct_flags & (CT_POINTER|CT_ARRAY))) {
            PyErr_Format(PyExc_TypeError,
                         "expected a pointer or array ctype, got '%s'",
                         ct->ct_name);
            return -1;
        }
        view->buf = ((CDataObject *)x)->c_data;
        view->obj = NULL;
        return 0;
    }
    else {
        return _my_PyObject_GetContiguousBuffer(x, view, writable_only);
    }
}

static PyObject *b_memmove(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *dest_obj, *src_obj;
    Py_buffer dest_view, src_view;
    Py_ssize_t n;
    static char *keywords[] = {"dest", "src", "n", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOn", keywords,
                                     &dest_obj, &src_obj, &n))
        return NULL;
    if (n < 0) {
        PyErr_SetString(PyExc_ValueError, "negative size");
        return NULL;
    }

    if (_fetch_as_buffer(src_obj, &src_view, 0) < 0) {
        return NULL;
    }
    if (_fetch_as_buffer(dest_obj, &dest_view, 1) < 0) {
        PyBuffer_Release(&src_view);
        return NULL;
    }

    memmove(dest_view.buf, src_view.buf, n);

    PyBuffer_Release(&dest_view);
    PyBuffer_Release(&src_view);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *b__get_types(PyObject *self, PyObject *noarg)
{
    return PyTuple_Pack(2, (PyObject *)&CData_Type,
                           (PyObject *)&CTypeDescr_Type);
}

/* forward, in commontypes.c */
static PyObject *b__get_common_types(PyObject *self, PyObject *arg);

static PyObject *b_gcp(PyObject *self, PyObject *args, PyObject *kwds)
{
    CDataObject *cd;
    CDataObject *origobj;
    PyObject *destructor;
    static char *keywords[] = {"cdata", "destructor", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O:gc", keywords,
                                     &CData_Type, &origobj, &destructor))
        return NULL;

    cd = allocate_gcp_object(origobj, origobj->c_type, destructor);
    return (PyObject *)cd;
}

/************************************************************/

static char _testfunc0(char a, char b)
{
    return a + b;
}
static long _testfunc1(int a, long b)
{
    return (long)a + b;
}
static PY_LONG_LONG _testfunc2(PY_LONG_LONG a, PY_LONG_LONG b)
{
    return a + b;
}
static double _testfunc3(float a, double b)
{
    return a + b;
}
static float _testfunc4(float a, double b)
{
    return (float)(a + b);
}
static void _testfunc5(void)
{
    errno = errno + 15;
}
static int *_testfunc6(int *x)
{
    static int y;
    y = *x - 1000;
    return &y;
}
struct _testfunc7_s { unsigned char a1; short a2; };
static short _testfunc7(struct _testfunc7_s inlined)
{
    return inlined.a1 + inlined.a2;
}
static int _testfunc9(int num, ...)
{
    va_list vargs;
    int i, total = 0;
    va_start(vargs, num);
    for (i=0; i<num; i++) {
        int value = va_arg(vargs, int);
        if (value == 0)
            value = -66666666;
        total += value;
    }
    va_end(vargs);
    return total;
}

static struct _testfunc7_s _testfunc10(int n)
{
    struct _testfunc7_s result;
    result.a1 = n;
    result.a2 = n * n;
    return result;
}

struct _testfunc11_s { int a1, a2; };
static struct _testfunc11_s _testfunc11(int n)
{
    struct _testfunc11_s result;
    result.a1 = n;
    result.a2 = n * n;
    return result;
}

struct _testfunc12_s { double a1; };
static struct _testfunc12_s _testfunc12(int n)
{
    struct _testfunc12_s result;
    result.a1 = n;
    return result;
}

struct _testfunc13_s { int a1, a2, a3; };
static struct _testfunc13_s _testfunc13(int n)
{
    struct _testfunc13_s result;
    result.a1 = n;
    result.a2 = n * n;
    result.a3 = n * n * n;
    return result;
}

struct _testfunc14_s { float a1; };
static struct _testfunc14_s _testfunc14(int n)
{
    struct _testfunc14_s result;
    result.a1 = (float)n;
    return result;
}

struct _testfunc15_s { float a1; int a2; };
static struct _testfunc15_s _testfunc15(int n)
{
    struct _testfunc15_s result;
    result.a1 = (float)n;
    result.a2 = n * n;
    return result;
}

struct _testfunc16_s { float a1, a2; };
static struct _testfunc16_s _testfunc16(int n)
{
    struct _testfunc16_s result;
    result.a1 = (float)n;
    result.a2 = -(float)n;
    return result;
}

struct _testfunc17_s { int a1; float a2; };
static struct _testfunc17_s _testfunc17(int n)
{
    struct _testfunc17_s result;
    result.a1 = n;
    result.a2 = (float)n * (float)n;
    return result;
}

static int _testfunc18(struct _testfunc17_s *ptr)
{
    return ptr->a1 + (int)ptr->a2;
}

static long double _testfunc19(long double x, int count)
{
    int i;
    for (i=0; i<count; i++) {
        x = 4*x - x*x;
    }
    return x;
}

static short _testfunc20(struct _testfunc7_s *ptr)
{
    return ptr->a1 + ptr->a2;
}

struct _testfunc21_s { int a, b, c, d, e, f, g, h, i, j; };
static int _testfunc21(struct _testfunc21_s inlined)
{
    return ((inlined.a << 0) +
            (inlined.b << 1) +
            (inlined.c << 2) +
            (inlined.d << 3) +
            (inlined.e << 4) +
            (inlined.f << 5) +
            (inlined.g << 6) +
            (inlined.h << 7) +
            (inlined.i << 8) +
            (inlined.j << 9));
}

struct _testfunc22_s { int a[10]; };
static struct _testfunc22_s _testfunc22(struct _testfunc22_s s1,
                                        struct _testfunc22_s s2)
{
    struct _testfunc22_s result;
    int i;
    for (i=0; i<10; i++)
        result.a[i] = s1.a[i] - s2.a[i];
    return result;
}

static int _testfunc23(char *p)
{
    if (p)
        return 1000 * p[0];
    return -42;
}

static PyObject *b__testfunc(PyObject *self, PyObject *args)
{
    /* for testing only */
    int i;
    void *f;
    if (!PyArg_ParseTuple(args, "i:_testfunc", &i))
        return NULL;
    switch (i) {
    case 0: f = &_testfunc0; break;
    case 1: f = &_testfunc1; break;
    case 2: f = &_testfunc2; break;
    case 3: f = &_testfunc3; break;
    case 4: f = &_testfunc4; break;
    case 5: f = &_testfunc5; break;
    case 6: f = &_testfunc6; break;
    case 7: f = &_testfunc7; break;
    case 8: f = stderr; break;
    case 9: f = &_testfunc9; break;
    case 10: f = &_testfunc10; break;
    case 11: f = &_testfunc11; break;
    case 12: f = &_testfunc12; break;
    case 13: f = &_testfunc13; break;
    case 14: f = &_testfunc14; break;
    case 15: f = &_testfunc15; break;
    case 16: f = &_testfunc16; break;
    case 17: f = &_testfunc17; break;
    case 18: f = &_testfunc18; break;
    case 19: f = &_testfunc19; break;
    case 20: f = &_testfunc20; break;
    case 21: f = &_testfunc21; break;
    case 22: f = &_testfunc22; break;
    case 23: f = &_testfunc23; break;
    default:
        PyErr_SetNone(PyExc_ValueError);
        return NULL;
    }
    return PyLong_FromVoidPtr(f);
}

#if PY_MAJOR_VERSION < 3
static Py_ssize_t _test_segcountproc(PyObject *o, Py_ssize_t *ignored)
{
    return 1;
}
static Py_ssize_t _test_getreadbuf(PyObject *o, Py_ssize_t i, void **r)
{
    static char buf[] = "RDB";
    *r = buf;
    return 3;
}
static Py_ssize_t _test_getwritebuf(PyObject *o, Py_ssize_t i, void **r)
{
    static char buf[] = "WRB";
    *r = buf;
    return 3;
}
static Py_ssize_t _test_getcharbuf(PyObject *o, Py_ssize_t i, char **r)
{
    static char buf[] = "CHB";
    *r = buf;
    return 3;
}
#endif
static int _test_getbuf(PyObject *self, Py_buffer *view, int flags)
{
    static char buf[] = "GTB";
    return PyBuffer_FillInfo(view, self, buf, 3, /*readonly=*/0, flags);
}
static int _test_getbuf_ro(PyObject *self, Py_buffer *view, int flags)
{
    static char buf[] = "ROB";
    return PyBuffer_FillInfo(view, self, buf, 3, /*readonly=*/1, flags);
}


static PyObject *b__testbuff(PyObject *self, PyObject *args)
{
    /* for testing only */
    int methods;
    PyTypeObject *obj;
    if (!PyArg_ParseTuple(args, "O!i|_testbuff", &PyType_Type, &obj, &methods))
        return NULL;

    assert(obj->tp_as_buffer != NULL);

#if PY_MAJOR_VERSION < 3
    obj->tp_as_buffer->bf_getsegcount = &_test_segcountproc;
    obj->tp_flags |= Py_TPFLAGS_HAVE_GETCHARBUFFER;
    obj->tp_flags |= Py_TPFLAGS_HAVE_NEWBUFFER;
    if (methods & 1)  obj->tp_as_buffer->bf_getreadbuffer  = &_test_getreadbuf;
    if (methods & 2)  obj->tp_as_buffer->bf_getwritebuffer = &_test_getwritebuf;
    if (methods & 4)  obj->tp_as_buffer->bf_getcharbuffer  = &_test_getcharbuf;
#endif
    if (methods & 8)  obj->tp_as_buffer->bf_getbuffer      = &_test_getbuf;
    if (methods & 16) obj->tp_as_buffer->bf_getbuffer      = &_test_getbuf_ro;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *b_init_cffi_1_0_external_module(PyObject *, PyObject *);
/* forward, see cffi1_module.c */


static PyMethodDef FFIBackendMethods[] = {
    {"load_library", b_load_library, METH_VARARGS},
    {"new_primitive_type", b_new_primitive_type, METH_VARARGS},
    {"new_pointer_type", b_new_pointer_type, METH_VARARGS},
    {"new_array_type", b_new_array_type, METH_VARARGS},
    {"new_void_type", b_new_void_type, METH_NOARGS},
    {"new_struct_type", b_new_struct_type, METH_VARARGS},
    {"new_union_type", b_new_union_type, METH_VARARGS},
    {"complete_struct_or_union", b_complete_struct_or_union, METH_VARARGS},
    {"new_function_type", b_new_function_type, METH_VARARGS},
    {"new_enum_type", b_new_enum_type, METH_VARARGS},
    {"newp", b_newp, METH_VARARGS},
    {"cast", b_cast, METH_VARARGS},
    {"callback", b_callback, METH_VARARGS},
    {"alignof", b_alignof, METH_O},
    {"sizeof", b_sizeof, METH_O},
    {"typeof", b_typeof, METH_O},
    {"typeoffsetof", b_typeoffsetof, METH_VARARGS},
    {"rawaddressof", b_rawaddressof, METH_VARARGS},
    {"getcname", b_getcname, METH_VARARGS},
    {"string", (PyCFunction)b_string, METH_VARARGS | METH_KEYWORDS},
    {"buffer", (PyCFunction)b_buffer, METH_VARARGS | METH_KEYWORDS},
    {"get_errno", b_get_errno, METH_NOARGS},
    {"set_errno", b_set_errno, METH_O},
    {"newp_handle", b_newp_handle, METH_VARARGS},
    {"from_handle", b_from_handle, METH_O},
    {"from_buffer", b_from_buffer, METH_VARARGS},
    {"memmove", (PyCFunction)b_memmove, METH_VARARGS | METH_KEYWORDS},
    {"gcp", (PyCFunction)b_gcp, METH_VARARGS | METH_KEYWORDS},
#ifdef MS_WIN32
    {"getwinerror", (PyCFunction)b_getwinerror, METH_VARARGS | METH_KEYWORDS},
#endif
    {"_get_types", b__get_types, METH_NOARGS},
    {"_get_common_types", b__get_common_types, METH_O},
    {"_testfunc", b__testfunc, METH_VARARGS},
    {"_testbuff", b__testbuff, METH_VARARGS},
    {"_init_cffi_1_0_external_module", b_init_cffi_1_0_external_module, METH_O},
    {NULL,     NULL}    /* Sentinel */
};

/************************************************************/
/* Functions used by '_cffi_N.so', the generated modules    */

#define _cffi_to_c_SIGNED_FN(RETURNTYPE, SIZE)                          \
static RETURNTYPE _cffi_to_c_i##SIZE(PyObject *obj) {                   \
    PY_LONG_LONG tmp = _my_PyLong_AsLongLong(obj);                      \
    if ((tmp > (PY_LONG_LONG)((1ULL<<(SIZE-1)) - 1)) ||                 \
        (tmp < (PY_LONG_LONG)(0ULL-(1ULL<<(SIZE-1)))))                  \
        if (!PyErr_Occurred())                                          \
            return (RETURNTYPE)_convert_overflow(obj, #SIZE "-bit int"); \
    return (RETURNTYPE)tmp;                                             \
}

#define _cffi_to_c_UNSIGNED_FN(RETURNTYPE, SIZE)                        \
static RETURNTYPE _cffi_to_c_u##SIZE(PyObject *obj) {                   \
    unsigned PY_LONG_LONG tmp = _my_PyLong_AsUnsignedLongLong(obj, 1);  \
    if (tmp > ~(((unsigned PY_LONG_LONG)-2) << (SIZE-1)))               \
        if (!PyErr_Occurred())                                          \
            return (RETURNTYPE)_convert_overflow(obj,                   \
                                   #SIZE "-bit unsigned int");          \
    return (RETURNTYPE)tmp;                                             \
}

_cffi_to_c_SIGNED_FN(int, 8)
_cffi_to_c_SIGNED_FN(int, 16)
_cffi_to_c_SIGNED_FN(int, 32)
_cffi_to_c_SIGNED_FN(PY_LONG_LONG, 64)
_cffi_to_c_UNSIGNED_FN(int, 8)
_cffi_to_c_UNSIGNED_FN(int, 16)
_cffi_to_c_UNSIGNED_FN(unsigned int, 32)
_cffi_to_c_UNSIGNED_FN(unsigned PY_LONG_LONG, 64)

static PyObject *_cffi_from_c_pointer(char *ptr, CTypeDescrObject *ct)
{
    return convert_to_object((char *)&ptr, ct);
}

static char *_cffi_to_c_pointer(PyObject *obj, CTypeDescrObject *ct)
{
    char *result;
    if (convert_from_object((char *)&result, ct, obj) < 0) {
        if ((ct->ct_flags & CT_POINTER) &&
                (ct->ct_itemdescr->ct_flags & CT_IS_FILE) &&
                PyFile_Check(obj)) {
            PyErr_Clear();
            return (char *)PyFile_AsFile(obj);
        }
        return NULL;
    }
    return result;
}

static long double _cffi_to_c_long_double(PyObject *obj)
{
    if (CData_Check(obj) &&
            (((CDataObject *)obj)->c_type->ct_flags & CT_IS_LONGDOUBLE)) {
        char *data = ((CDataObject *)obj)->c_data;
        /*READ(data, sizeof(long double))*/
        return read_raw_longdouble_data(data);
    }
    else
        return PyFloat_AsDouble(obj);
}

static _Bool _cffi_to_c__Bool(PyObject *obj)
{
    PY_LONG_LONG tmp = _my_PyLong_AsLongLong(obj);
    if (tmp == 0)
        return 0;
    else if (tmp == 1)
        return 1;
    else if (PyErr_Occurred())
        return (_Bool)-1;
    else
        return (_Bool)_convert_overflow(obj, "_Bool");
}

static PyObject *_cffi_get_struct_layout(Py_ssize_t nums[])
{
    PyObject *result;
    int count = 0;
    while (nums[count] >= 0)
        count++;

    result = PyList_New(count);
    if (result == NULL)
        return NULL;

    while (--count >= 0) {
        PyObject *o = PyInt_FromSsize_t(nums[count]);
        if (o == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyList_SET_ITEM(result, count, o);
    }
    return result;
}

static PyObject *_cffi_from_c_char(char x) {
    return PyBytes_FromStringAndSize(&x, 1);
}

#ifdef HAVE_WCHAR_H
static PyObject *_cffi_from_c_wchar_t(wchar_t x) {
    return _my_PyUnicode_FromWideChar(&x, 1);
}
#endif

struct _cffi_externpy_s;      /* forward declaration */
static void cffi_call_python(struct _cffi_externpy_s *, char *args);

static void *cffi_exports[] = {
    NULL,
    _cffi_to_c_i8,
    _cffi_to_c_u8,
    _cffi_to_c_i16,
    _cffi_to_c_u16,
    _cffi_to_c_i32,
    _cffi_to_c_u32,
    _cffi_to_c_i64,
    _cffi_to_c_u64,
    _convert_to_char,
    _cffi_from_c_pointer,
    _cffi_to_c_pointer,
    _cffi_get_struct_layout,
    restore_errno,
    save_errno,
    _cffi_from_c_char,
    convert_to_object,
    convert_from_object,
    convert_struct_to_owning_object,
#ifdef HAVE_WCHAR_H
    _convert_to_wchar_t,
    _cffi_from_c_wchar_t,
#else
    0,
    0,
#endif
    _cffi_to_c_long_double,
    _cffi_to_c__Bool,
    _prepare_pointer_call_argument,
    convert_array_from_object,
    cffi_call_python,
};

static struct { const char *name; int value; } all_dlopen_flags[] = {
    { "RTLD_LAZY",     RTLD_LAZY     },
    { "RTLD_NOW",      RTLD_NOW      },
    { "RTLD_GLOBAL",   RTLD_GLOBAL   },
#ifdef RTLD_LOCAL
    { "RTLD_LOCAL",    RTLD_LOCAL    },
#else
    { "RTLD_LOCAL",    0             },
#endif
#ifdef RTLD_NODELETE
    { "RTLD_NODELETE", RTLD_NODELETE },
#endif
#ifdef RTLD_NOLOAD
    { "RTLD_NOLOAD",   RTLD_NOLOAD   },
#endif
#ifdef RTLD_DEEPBIND
    { "RTLD_DEEPBIND", RTLD_DEEPBIND },
#endif
    { NULL, 0 }
};


/************************************************************/

#include "cffi1_module.c"

/************************************************************/

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef FFIBackendModuleDef = {
  PyModuleDef_HEAD_INIT,
  "_cffi_backend",
  NULL,
  -1,
  FFIBackendMethods,
  NULL, NULL, NULL, NULL
};
#define INITERROR return NULL

PyMODINIT_FUNC
PyInit__cffi_backend(void)
#else
#define INITERROR return

PyMODINIT_FUNC
init_cffi_backend(void)
#endif
{
    PyObject *m, *v;
    int i;
    static char init_done = 0;

    v = PySys_GetObject("version");
    if (v == NULL || !PyText_Check(v) ||
            strncmp(PyText_AS_UTF8(v), PY_VERSION, 3) != 0) {
        PyErr_Format(PyExc_ImportError,
                     "this module was compiled for Python %c%c%c",
                     PY_VERSION[0], PY_VERSION[1], PY_VERSION[2]);
        INITERROR;
    }

#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&FFIBackendModuleDef);
#else
    m = Py_InitModule("_cffi_backend", FFIBackendMethods);
#endif

    if (m == NULL)
        INITERROR;

    if (unique_cache == NULL) {
        unique_cache = PyDict_New();
        if (unique_cache == NULL)
            INITERROR;
    }

    if (PyType_Ready(&dl_type) < 0)
        INITERROR;
    if (PyType_Ready(&CTypeDescr_Type) < 0)
        INITERROR;
    if (PyType_Ready(&CField_Type) < 0)
        INITERROR;
    if (PyType_Ready(&CData_Type) < 0)
        INITERROR;
    if (PyType_Ready(&CDataOwning_Type) < 0)
        INITERROR;
    if (PyType_Ready(&CDataOwningGC_Type) < 0)
        INITERROR;
    if (PyType_Ready(&CDataGCP_Type) < 0)
        INITERROR;
    if (PyType_Ready(&CDataIter_Type) < 0)
        INITERROR;
    if (PyType_Ready(&MiniBuffer_Type) < 0)
        INITERROR;

    if (!init_done) {
        v = PyText_FromString("_cffi_backend");
        if (v == NULL || PyDict_SetItemString(CData_Type.tp_dict,
                                              "__module__", v) < 0)
            INITERROR;
        v = PyText_FromString("<cdata>");
        if (v == NULL || PyDict_SetItemString(CData_Type.tp_dict,
                                              "__name__", v) < 0)
            INITERROR;
        init_done = 1;
    }

    /* this is for backward compatibility only */
    v = PyCapsule_New((void *)cffi_exports, "cffi", NULL);
    if (v == NULL || PyModule_AddObject(m, "_C_API", v) < 0)
        INITERROR;

    v = PyText_FromString(CFFI_VERSION);
    if (v == NULL || PyModule_AddObject(m, "__version__", v) < 0)
        INITERROR;

    if (PyModule_AddIntConstant(m, "FFI_DEFAULT_ABI", FFI_DEFAULT_ABI) < 0 ||
#if defined(MS_WIN32) && !defined(_WIN64)
        PyModule_AddIntConstant(m, "FFI_STDCALL", FFI_STDCALL) < 0 ||
#endif
        PyModule_AddIntConstant(m, "FFI_CDECL", FFI_DEFAULT_ABI) < 0 ||

#ifdef MS_WIN32
#  ifdef _WIN64
        PyModule_AddIntConstant(m, "_WIN", 64) < 0 ||   /* win64 */
#  else
        PyModule_AddIntConstant(m, "_WIN", 32) < 0 ||   /* win32 */
#  endif
#endif
        0)
      INITERROR;

    for (i = 0; all_dlopen_flags[i].name != NULL; i++) {
        if (PyModule_AddIntConstant(m,
                                    all_dlopen_flags[i].name,
                                    all_dlopen_flags[i].value) < 0)
            INITERROR;
    }

    init_cffi_tls();
    if (PyErr_Occurred())
        INITERROR;

    if (init_ffi_lib(m) < 0)
        INITERROR;

#if PY_MAJOR_VERSION >= 3
    if (init_file_emulator() < 0)
        INITERROR;
    return m;
#endif
}
