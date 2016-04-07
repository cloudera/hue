#include "_cffi_include.h"


#define AA  (42)
#define BB  (&bb)
static int bb = 16261;

int foo42(int a, int *b)
{
    return a - *b;
}

int foo64(int a)
{
    return ~a;
}

struct foo_s {
    int a;
};

/************************************************************/

static void *_cffi_types[] = {
    _CFFI_OP(_CFFI_OP_FUNCTION, 1),
    _CFFI_OP(_CFFI_OP_PRIMITIVE, _CFFI_PRIM_INT),
    _CFFI_OP(_CFFI_OP_POINTER, 1),
    _CFFI_OP(_CFFI_OP_FUNCTION_END, 0),
    _CFFI_OP(_CFFI_OP_FUNCTION, 1),
    _CFFI_OP(_CFFI_OP_PRIMITIVE, _CFFI_PRIM_INT),
    _CFFI_OP(_CFFI_OP_FUNCTION_END, 0),
    _CFFI_OP(_CFFI_OP_STRUCT_UNION, 0),
};

#ifndef PYPY_VERSION
static PyObject *
_cffi_f_foo42(PyObject *self, PyObject *args)
{
  int x0;
  int * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:foo42", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_types[1], arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_types[1], arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = foo42(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}
#else
static int _cffi_f_foo42(int x0, int *x1)
{
  return foo42(x0, x1);
}
#endif

#ifndef PYPY_VERSION
static PyObject *
_cffi_f_foo64(PyObject *self, PyObject *arg0)
{
  int x0;
  int result;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = foo64(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}
#else
static int _cffi_f_foo64(int x0)
{
  return foo64(x0);
}
#endif

static int _cffi_const_AA(unsigned long long *output)
{
    *output = (unsigned long long)((AA) << 0);   // integer
    return (AA) <= 0;
}

static void _cffi_const_BB(char *output)
{
    *(int **)output = BB;
}

static const struct _cffi_global_s _cffi_globals[] = {
    { "AA",    &_cffi_const_AA, _CFFI_OP(_CFFI_OP_CONSTANT_INT, 0) },
    { "BB",    &_cffi_const_BB, _CFFI_OP(_CFFI_OP_CONSTANT, 2) },
    { "bb",    &bb, _CFFI_OP(_CFFI_OP_GLOBAL_VAR, 1) },
    { "foo42", &_cffi_f_foo42, _CFFI_OP(_CFFI_OP_CPYTHON_BLTN_V, 0) },
    { "foo64", &_cffi_f_foo64, _CFFI_OP(_CFFI_OP_CPYTHON_BLTN_O, 4) },
};

struct _cffi_align_foo_s { char x; struct foo_s y; };

static const struct _cffi_struct_union_s _cffi_struct_unions[] = {
    { "foo_s", 7, 0,
      sizeof(struct foo_s),
      offsetof(struct _cffi_align_foo_s, y),
      1, 0 },
};

static const struct _cffi_field_s _cffi_fields[] = {
    { "a", offsetof(struct foo_s, a), sizeof(((struct foo_s *)0)->a),
      _CFFI_OP(_CFFI_OP_NOOP, 1) },
};

static const struct _cffi_type_context_s _cffi_type_context = {
    _cffi_types,
    _cffi_globals,
    _cffi_fields,
    _cffi_struct_unions,
    NULL,
    NULL,
    5,  /* num_globals */
    1,  /* num_struct_unions */
    0,
    0,
    NULL,
    8,  /* num_types */
};

#ifndef PYPY_VERSION
PyMODINIT_FUNC
initmanual(void)
{
    _cffi_init("manual", 0x2601, &_cffi_type_context);
}
#else
PyMODINIT_FUNC
_cffi_pypyinit_manual(const void *p[])
{
    p[0] = (const void *)0x2601;
    p[1] = &_cffi_type_context;
}
#endif
