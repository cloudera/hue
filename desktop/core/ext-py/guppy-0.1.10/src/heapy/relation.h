#ifndef Ny_RELATION_H

typedef struct {
    PyObject_HEAD
    int kind;
    PyObject *relator;
} NyRelationObject;

#define NyRelation_Check(op) PyObject_TypeCheck(op, &NyRelation_Type)

#endif /* #ifndef Ny_RELATION_H */
