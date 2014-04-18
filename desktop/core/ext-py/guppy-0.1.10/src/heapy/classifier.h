#ifndef NY_CLASSIFIER_H
#define NY_CLASSIFIER_H

typedef struct {
    int flags;
    int size;
    char *name;
    char *doc;
    PyObject * (*classify)(PyObject *self, PyObject *arg);
    PyObject * (*memoized_kind)(PyObject *self, PyObject *kind);
    int (*cmp_le)(PyObject *self, PyObject *a, PyObject *b);
} NyObjectClassifierDef;

typedef struct{
    PyObject_HEAD
    NyObjectClassifierDef *def;
    PyObject *self;
} NyObjectClassifierObject;

#define NyObjectClassifier_Check(op) PyObject_TypeCheck(op, &NyObjectClassifier_Type)

int NyObjectClassifier_Compare(NyObjectClassifierObject *cli, PyObject *a, PyObject *b, int cmp);

/* cmp argument (to select etc)
   The first 6 happen to correspond to Py_LT , Py_LE etc
   but I didn't want to define them as such to not introduce a dependency.
*/

#define CLI_LT	0
#define CLI_LE	1
#define CLI_EQ  2
#define CLI_NE	3
#define CLI_GT	4
#define CLI_GE	5
#define CLI_MAX	5	/* Current end of definitions */

#endif /* NY_CLASSIFIER_H */

