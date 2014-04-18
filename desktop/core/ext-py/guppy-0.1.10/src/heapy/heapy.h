#ifndef Ny_HEAPY_H

/* Definiing Py_ssize_t for backwards compatibility, from PEP 353 */

#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif

struct ExtraType;

typedef struct {
    PyObject_HEAD
    PyObject *root;
    PyObject *limitframe;
    PyObject *_hiding_tag_;
    PyObject *static_types;
    PyObject *weak_type_callback;
    char is_hiding_calling_interpreter;
    char is_using_traversing_owner_update;
    struct ExtraType **xt_table;
    int xt_mask;
    int xt_size;
} NyHeapViewObject;

#define NyHeapView_Check(op) PyObject_TypeCheck(op, &NyHeapView_Type)

typedef struct ExtraType {
    PyTypeObject *xt_type;
    int (*xt_size) (PyObject *obj);
    int (*xt_traverse)(struct ExtraType *, PyObject *, visitproc, void *);
    int (*xt_relate)(struct ExtraType *, NyHeapRelate *r);
    struct ExtraType *xt_next;
    struct ExtraType *xt_base, *xt_he_xt;
    int (*xt_he_traverse)(struct ExtraType *, PyObject *, visitproc, void *);
    NyHeapViewObject *xt_hv;
    PyObject *xt_weak_type;
    NyHeapDef *xt_hd;
    long xt_he_offs;
    int xt_trav_code;
} ExtraType;



typedef struct NyHeapClassifier{
    PyObject_HEAD
    PyObject (*classify)(struct NyHeapClassifier*self, PyObject *obj);
    void *extra0, *extra1, *extra2, *extra3;
} NyHeapClassifier;

extern PyObject _Ny_RootStateStruct; /* Don't use this directly */

#define Ny_RootState (&_Ny_RootStateStruct)

#endif /* Ny_HEAPY_H */

