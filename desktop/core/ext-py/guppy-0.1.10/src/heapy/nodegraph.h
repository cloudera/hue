#ifndef NY_NODEGRAPH_H
#define NY_NODEGRAPH_H

typedef struct {
    PyObject *src, *tgt;
} NyNodeGraphEdge;

typedef struct {
    PyObject_HEAD
    PyObject *_hiding_tag_;
    NyNodeGraphEdge *edges;
    int used_size;
    int allo_size;
    char is_mapping;
    char is_sorted;
    char is_preserving_duplicates;
} NyNodeGraphObject;

extern PyTypeObject NyNodeGraph_Type;

#define NyNodeGraph_Check(op) PyObject_TypeCheck(op, &NyNodeGraph_Type)


NyNodeGraphObject *NyNodeGraph_New(void);
int NyNodeGraph_Region(NyNodeGraphObject *rg, PyObject *key,
		       NyNodeGraphEdge **lop, NyNodeGraphEdge **hip);
int NyNodeGraph_AddEdge(NyNodeGraphObject *rg, PyObject *src, PyObject *tgt);
void NyNodeGraph_Clear(NyNodeGraphObject *rg);
NyNodeGraphObject *NyNodeGraph_Copy(NyNodeGraphObject *rg);
int NyNodeGraph_Invert(NyNodeGraphObject *rg);
NyNodeGraphObject *NyNodeGraph_Inverted(NyNodeGraphObject *rg);
int NyNodeGraph_Update(NyNodeGraphObject *a, PyObject *b);

#endif /* NY_NODEGRAPH_H */
