
/* Implementation of a C object with the 'buffer' or 'memoryview'
 * interface at C-level (as approriate for the version of Python we're
 * compiling for), but only a minimal but *consistent* part of the
 * 'buffer' interface at application level.
 */

typedef struct {
    PyObject_HEAD
    char      *mb_data;
    Py_ssize_t mb_size;
    PyObject  *mb_keepalive;
    PyObject  *mb_weakreflist;    /* weakref support */
} MiniBufferObj;

static Py_ssize_t mb_length(MiniBufferObj *self)
{
    return self->mb_size;
}

static PyObject *mb_item(MiniBufferObj *self, Py_ssize_t idx)
{
    if (idx < 0 || idx >= self->mb_size ) {
        PyErr_SetString(PyExc_IndexError, "buffer index out of range");
        return NULL;
    }
    return PyBytes_FromStringAndSize(self->mb_data + idx, 1);
}

static PyObject *mb_slice(MiniBufferObj *self,
                          Py_ssize_t left, Py_ssize_t right)
{
    Py_ssize_t size = self->mb_size;
    if (left < 0)     left = 0;
    if (right > size) right = size;
    if (left > right) left = right;
    return PyBytes_FromStringAndSize(self->mb_data + left, right - left);
}

static int mb_ass_item(MiniBufferObj *self, Py_ssize_t idx, PyObject *other)
{
    if (idx < 0 || idx >= self->mb_size) {
        PyErr_SetString(PyExc_IndexError,
                        "buffer assignment index out of range");
        return -1;
    }
    if (PyBytes_Check(other) && PyBytes_GET_SIZE(other) == 1) {
        self->mb_data[idx] = PyBytes_AS_STRING(other)[0];
        return 0;
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "must assign a "STR_OR_BYTES
                     " of length 1, not %.200s", Py_TYPE(other)->tp_name);
        return -1;
    }
}

static int mb_ass_slice(MiniBufferObj *self,
                        Py_ssize_t left, Py_ssize_t right, PyObject *other)
{
    const void *buffer;
    Py_ssize_t buffer_len, count;
    Py_ssize_t size = self->mb_size;

    if (PyObject_AsReadBuffer(other, &buffer, &buffer_len) < 0)
        return -1;

    if (left < 0)     left = 0;
    if (right > size) right = size;
    if (left > right) left = right;

    count = right - left;
    if (count != buffer_len) {
        PyErr_SetString(PyExc_ValueError,
                        "right operand length must match slice length");
        return -1;
    }
    memcpy(self->mb_data + left, buffer, count);
    return 0;
}

#if PY_MAJOR_VERSION < 3
static Py_ssize_t mb_getdata(MiniBufferObj *self, Py_ssize_t idx, void **pp)
{
    *pp = self->mb_data;
    return self->mb_size;
}

static Py_ssize_t mb_getsegcount(MiniBufferObj *self, Py_ssize_t *lenp)
{
    if (lenp)
        *lenp = self->mb_size;
    return 1;
}

static PyObject *mb_str(MiniBufferObj *self)
{
    /* Python 2: we want str(buffer) to behave like buffer[:], because
       that's what bytes(buffer) does on Python 3 and there is no way
       we can prevent this. */
    return PyString_FromStringAndSize(self->mb_data, self->mb_size);
}
#endif

static int mb_getbuf(MiniBufferObj *self, Py_buffer *view, int flags)
{
    return PyBuffer_FillInfo(view, (PyObject *)self,
                             self->mb_data, self->mb_size,
                             /*readonly=*/0, flags);
}

static PySequenceMethods mb_as_sequence = {
    (lenfunc)mb_length, /*sq_length*/
    (binaryfunc)0, /*sq_concat*/
    (ssizeargfunc)0, /*sq_repeat*/
    (ssizeargfunc)mb_item, /*sq_item*/
    (ssizessizeargfunc)mb_slice, /*sq_slice*/
    (ssizeobjargproc)mb_ass_item, /*sq_ass_item*/
    (ssizessizeobjargproc)mb_ass_slice, /*sq_ass_slice*/
};

static PyBufferProcs mb_as_buffer = {
#if PY_MAJOR_VERSION < 3
    (readbufferproc)mb_getdata,
    (writebufferproc)mb_getdata,
    (segcountproc)mb_getsegcount,
    (charbufferproc)mb_getdata,
#endif
    (getbufferproc)mb_getbuf,
    (releasebufferproc)0,
};

static void
mb_dealloc(MiniBufferObj *ob)
{
    PyObject_GC_UnTrack(ob);
    if (ob->mb_weakreflist != NULL)
        PyObject_ClearWeakRefs((PyObject *)ob);
    Py_XDECREF(ob->mb_keepalive);
    Py_TYPE(ob)->tp_free((PyObject *)ob);
}

static int
mb_traverse(MiniBufferObj *ob, visitproc visit, void *arg)
{
    Py_VISIT(ob->mb_keepalive);
    return 0;
}

static int
mb_clear(MiniBufferObj *ob)
{
    Py_CLEAR(ob->mb_keepalive);
    return 0;
}

#if PY_MAJOR_VERSION >= 3
/* pfffffffffffff pages of copy-paste from listobject.c */
static PyObject *mb_subscript(MiniBufferObj *self, PyObject *item)
{
    if (PyIndex_Check(item)) {
        Py_ssize_t i;
        i = PyNumber_AsSsize_t(item, PyExc_IndexError);
        if (i == -1 && PyErr_Occurred())
            return NULL;
        if (i < 0)
            i += self->mb_size;
        return mb_item(self, i);
    }
    else if (PySlice_Check(item)) {
        Py_ssize_t start, stop, step, slicelength;

        if (PySlice_GetIndicesEx(item, self->mb_size,
                         &start, &stop, &step, &slicelength) < 0)
            return NULL;

        if (step == 1)
            return mb_slice(self, start, stop);
        else {
            PyErr_SetString(PyExc_TypeError,
                            "buffer doesn't support slicing with step != 1");
            return NULL;
        }
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "buffer indices must be integers, not %.200s",
                     item->ob_type->tp_name);
        return NULL;
    }
}
static int
mb_ass_subscript(MiniBufferObj* self, PyObject* item, PyObject* value)
{
    if (PyIndex_Check(item)) {
        Py_ssize_t i = PyNumber_AsSsize_t(item, PyExc_IndexError);
        if (i == -1 && PyErr_Occurred())
            return -1;
        if (i < 0)
            i += self->mb_size;
        return mb_ass_item(self, i, value);
    }
    else if (PySlice_Check(item)) {
        Py_ssize_t start, stop, step, slicelength;

        if (PySlice_GetIndicesEx(item, self->mb_size,
                         &start, &stop, &step, &slicelength) < 0) {
            return -1;
        }

        if (step == 1)
            return mb_ass_slice(self, start, stop, value);
        else {
            PyErr_SetString(PyExc_TypeError,
                            "buffer doesn't support slicing with step != 1");
            return -1;
        }
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "buffer indices must be integers, not %.200s",
                     item->ob_type->tp_name);
        return -1;
    }
}

static PyMappingMethods mb_as_mapping = {
    (lenfunc)mb_length, /*mp_length*/
    (binaryfunc)mb_subscript, /*mp_subscript*/
    (objobjargproc)mb_ass_subscript, /*mp_ass_subscript*/
};
#endif

#if PY_MAJOR_VERSION >= 3
# define MINIBUF_TPFLAGS 0
#else
# define MINIBUF_TPFLAGS (Py_TPFLAGS_HAVE_GETCHARBUFFER | Py_TPFLAGS_HAVE_NEWBUFFER)
#endif

static PyTypeObject MiniBuffer_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_cffi_backend.buffer",
    sizeof(MiniBufferObj),
    0,
    (destructor)mb_dealloc,                     /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    &mb_as_sequence,                            /* tp_as_sequence */
#if PY_MAJOR_VERSION < 3
    0,                                          /* tp_as_mapping */
#else
    &mb_as_mapping,                             /* tp_as_mapping */
#endif
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
#if PY_MAJOR_VERSION < 3
    (reprfunc)mb_str,                           /* tp_str */
#else
    0,                                          /* tp_str */
#endif
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    &mb_as_buffer,                              /* tp_as_buffer */
    (Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
        MINIBUF_TPFLAGS),                       /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)mb_traverse,                  /* tp_traverse */
    (inquiry)mb_clear,                          /* tp_clear */
    0,                                          /* tp_richcompare */
    offsetof(MiniBufferObj, mb_weakreflist),    /* tp_weaklistoffset */
};

static PyObject *minibuffer_new(char *data, Py_ssize_t size,
                                PyObject *keepalive)
{
    MiniBufferObj *ob = PyObject_GC_New(MiniBufferObj, &MiniBuffer_Type);
    if (ob != NULL) {
        ob->mb_data = data;
        ob->mb_size = size;
        ob->mb_keepalive = keepalive; Py_INCREF(keepalive);
        ob->mb_weakreflist = NULL;
        PyObject_GC_Track(ob);
    }
    return (PyObject *)ob;
}
