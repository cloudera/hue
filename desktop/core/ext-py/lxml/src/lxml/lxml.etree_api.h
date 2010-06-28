#ifndef __PYX_HAVE_API__lxml__etree
#define __PYX_HAVE_API__lxml__etree
#include "Python.h"
#include "lxml.etree.h"

static PyTypeObject *__pyx_ptype_4lxml_5etree__Document;
#define LxmlDocumentType (*__pyx_ptype_4lxml_5etree__Document)

static PyTypeObject *__pyx_ptype_4lxml_5etree__Element;
#define LxmlElementType (*__pyx_ptype_4lxml_5etree__Element)

static PyTypeObject *__pyx_ptype_4lxml_5etree__ElementTree;
#define LxmlElementTreeType (*__pyx_ptype_4lxml_5etree__ElementTree)

static PyTypeObject *__pyx_ptype_4lxml_5etree__ElementTagMatcher;
#define LxmlElementTagMatcherType (*__pyx_ptype_4lxml_5etree__ElementTagMatcher)

static PyTypeObject *__pyx_ptype_4lxml_5etree__ElementIterator;
#define LxmlElementIteratorType (*__pyx_ptype_4lxml_5etree__ElementIterator)

static PyTypeObject *__pyx_ptype_4lxml_5etree_ElementBase;
#define LxmlElementBaseType (*__pyx_ptype_4lxml_5etree_ElementBase)

static PyTypeObject *__pyx_ptype_4lxml_5etree_ElementClassLookup;
#define LxmlElementClassLookupType (*__pyx_ptype_4lxml_5etree_ElementClassLookup)

static PyTypeObject *__pyx_ptype_4lxml_5etree_FallbackElementClassLookup;
#define LxmlFallbackElementClassLookupType (*__pyx_ptype_4lxml_5etree_FallbackElementClassLookup)

static struct LxmlElement *(*deepcopyNodeToDocument)(struct LxmlDocument *, xmlNode *);
static struct LxmlElementTree *(*elementTreeFactory)(struct LxmlElement *);
static struct LxmlElementTree *(*newElementTree)(struct LxmlElement *, PyObject *);
static struct LxmlElement *(*elementFactory)(struct LxmlDocument *, xmlNode *);
static struct LxmlElement *(*makeElement)(PyObject *, struct LxmlDocument *, PyObject *, PyObject *, PyObject *, PyObject *, PyObject *);
static struct LxmlElement *(*makeSubElement)(struct LxmlElement *, PyObject *, PyObject *, PyObject *, PyObject *, PyObject *);
static void (*setElementClassLookupFunction)(_element_class_lookup_function, PyObject *);
static PyObject *(*lookupDefaultElementClass)(PyObject *, PyObject *, xmlNode *);
static PyObject *(*lookupNamespaceElementClass)(PyObject *, PyObject *, xmlNode *);
static PyObject *(*callLookupFallback)(struct LxmlFallbackElementClassLookup *, struct LxmlDocument *, xmlNode *);
static int (*tagMatches)(xmlNode *, char *, char *);
static struct LxmlDocument *(*documentOrRaise)(PyObject *);
static struct LxmlElement *(*rootNodeOrRaise)(PyObject *);
static int (*hasText)(xmlNode *);
static int (*hasTail)(xmlNode *);
static PyObject *(*textOf)(xmlNode *);
static PyObject *(*tailOf)(xmlNode *);
static int (*setNodeText)(xmlNode *, PyObject *);
static int (*setTailText)(xmlNode *, PyObject *);
static PyObject *(*attributeValue)(xmlNode *, xmlAttr *);
static PyObject *(*attributeValueFromNsName)(xmlNode *, char *, char *);
static PyObject *(*getAttributeValue)(struct LxmlElement *, PyObject *, PyObject *);
static PyObject *(*iterattributes)(struct LxmlElement *, int);
static PyObject *(*collectAttributes)(xmlNode *, int);
static int (*setAttributeValue)(struct LxmlElement *, PyObject *, PyObject *);
static int (*delAttribute)(struct LxmlElement *, PyObject *);
static int (*delAttributeFromNsName)(xmlNode *, char *, char *);
static int (*hasChild)(xmlNode *);
static xmlNode *(*findChild)(xmlNode *, Py_ssize_t);
static xmlNode *(*findChildForwards)(xmlNode *, Py_ssize_t);
static xmlNode *(*findChildBackwards)(xmlNode *, Py_ssize_t);
static xmlNode *(*nextElement)(xmlNode *);
static xmlNode *(*previousElement)(xmlNode *);
static void (*appendChild)(struct LxmlElement *, struct LxmlElement *);
static PyObject *(*pyunicode)(char *);
static PyObject *(*utf8)(PyObject *);
static PyObject *(*getNsTag)(PyObject *);
static PyObject *(*namespacedName)(xmlNode *);
static PyObject *(*namespacedNameFromNsName)(char *, char *);
static void (*iteratorStoreNext)(struct LxmlElementIterator *, struct LxmlElement *);
static void (*initTagMatch)(struct LxmlElementTagMatcher *, PyObject *);
static xmlNs *(*findOrBuildNodeNsPrefix)(struct LxmlDocument *, xmlNode *, char *, char *);

#ifndef __PYX_HAVE_API_FUNC_import_module
#define __PYX_HAVE_API_FUNC_import_module

#ifndef __PYX_HAVE_RT_ImportModule
#define __PYX_HAVE_RT_ImportModule
static PyObject *__Pyx_ImportModule(const char *name) {
    PyObject *py_name = 0;
    PyObject *py_module = 0;

    #if PY_MAJOR_VERSION < 3
    py_name = PyString_FromString(name);
    #else
    py_name = PyUnicode_FromString(name);
    #endif
    if (!py_name)
        goto bad;
    py_module = PyImport_Import(py_name);
    Py_DECREF(py_name);
    return py_module;
bad:
    Py_XDECREF(py_name);
    return 0;
}
#endif

#endif


#ifndef __PYX_HAVE_RT_ImportFunction
#define __PYX_HAVE_RT_ImportFunction
static int __Pyx_ImportFunction(PyObject *module, const char *funcname, void (**f)(void), const char *sig) {
#if PY_VERSION_HEX < 0x02050000
    char *api = (char *)"__pyx_capi__";
#else
    const char *api = "__pyx_capi__";
#endif
    PyObject *d = 0;
    PyObject *cobj = 0;
    const char *desc;
    const char *s1, *s2;
    union {
        void (*fp)(void);
        void *p;
    } tmp;

    d = PyObject_GetAttrString(module, api);
    if (!d)
        goto bad;
    cobj = PyDict_GetItemString(d, funcname);
    if (!cobj) {
        PyErr_Format(PyExc_ImportError,
            "%s does not export expected C function %s",
                PyModule_GetName(module), funcname);
        goto bad;
    }
    desc = (const char *)PyCObject_GetDesc(cobj);
    if (!desc)
        goto bad;
    s1 = desc; s2 = sig;
    while (*s1 != '\0' && *s1 == *s2) { s1++; s2++; }
    if (*s1 != *s2) {
        PyErr_Format(PyExc_TypeError,
            "C function %s.%s has wrong signature (expected %s, got %s)",
             PyModule_GetName(module), funcname, sig, desc);
        goto bad;
    }
    tmp.p = PyCObject_AsVoidPtr(cobj);
    *f = tmp.fp;
    Py_DECREF(d);
    return 0;
bad:
    Py_XDECREF(d);
    return -1;
}
#endif


#ifndef __PYX_HAVE_RT_ImportType
#define __PYX_HAVE_RT_ImportType
static PyTypeObject *__Pyx_ImportType(const char *module_name, const char *class_name,
    long size)
{
    PyObject *py_module = 0;
    PyObject *result = 0;
    PyObject *py_name = 0;

    py_module = __Pyx_ImportModule(module_name);
    if (!py_module)
        goto bad;
    #if PY_MAJOR_VERSION < 3
    py_name = PyString_FromString(class_name);
    #else
    py_name = PyUnicode_FromString(class_name);
    #endif
    if (!py_name)
        goto bad;
    result = PyObject_GetAttr(py_module, py_name);
    Py_DECREF(py_name);
    py_name = 0;
    Py_DECREF(py_module);
    py_module = 0;
    if (!result)
        goto bad;
    if (!PyType_Check(result)) {
        PyErr_Format(PyExc_TypeError, 
            "%s.%s is not a type object",
            module_name, class_name);
        goto bad;
    }
    if (((PyTypeObject *)result)->tp_basicsize != size) {
        PyErr_Format(PyExc_ValueError, 
            "%s.%s does not appear to be the correct type object",
            module_name, class_name);
        goto bad;
    }
    return (PyTypeObject *)result;
bad:
    Py_XDECREF(py_module);
    Py_XDECREF(result);
    return 0;
}
#endif

static int import_lxml__etree(void) {
  PyObject *module = 0;
  module = __Pyx_ImportModule("lxml.etree");
  if (!module) goto bad;
  if (__Pyx_ImportFunction(module, "deepcopyNodeToDocument", (void (**)(void))&deepcopyNodeToDocument, "struct LxmlElement *(struct LxmlDocument *, xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "elementTreeFactory", (void (**)(void))&elementTreeFactory, "struct LxmlElementTree *(struct LxmlElement *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "newElementTree", (void (**)(void))&newElementTree, "struct LxmlElementTree *(struct LxmlElement *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "elementFactory", (void (**)(void))&elementFactory, "struct LxmlElement *(struct LxmlDocument *, xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "makeElement", (void (**)(void))&makeElement, "struct LxmlElement *(PyObject *, struct LxmlDocument *, PyObject *, PyObject *, PyObject *, PyObject *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "makeSubElement", (void (**)(void))&makeSubElement, "struct LxmlElement *(struct LxmlElement *, PyObject *, PyObject *, PyObject *, PyObject *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "setElementClassLookupFunction", (void (**)(void))&setElementClassLookupFunction, "void (_element_class_lookup_function, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "lookupDefaultElementClass", (void (**)(void))&lookupDefaultElementClass, "PyObject *(PyObject *, PyObject *, xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "lookupNamespaceElementClass", (void (**)(void))&lookupNamespaceElementClass, "PyObject *(PyObject *, PyObject *, xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "callLookupFallback", (void (**)(void))&callLookupFallback, "PyObject *(struct LxmlFallbackElementClassLookup *, struct LxmlDocument *, xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "tagMatches", (void (**)(void))&tagMatches, "int (xmlNode *, char *, char *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "documentOrRaise", (void (**)(void))&documentOrRaise, "struct LxmlDocument *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "rootNodeOrRaise", (void (**)(void))&rootNodeOrRaise, "struct LxmlElement *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "hasText", (void (**)(void))&hasText, "int (xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "hasTail", (void (**)(void))&hasTail, "int (xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "textOf", (void (**)(void))&textOf, "PyObject *(xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "tailOf", (void (**)(void))&tailOf, "PyObject *(xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "setNodeText", (void (**)(void))&setNodeText, "int (xmlNode *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "setTailText", (void (**)(void))&setTailText, "int (xmlNode *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "attributeValue", (void (**)(void))&attributeValue, "PyObject *(xmlNode *, xmlAttr *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "attributeValueFromNsName", (void (**)(void))&attributeValueFromNsName, "PyObject *(xmlNode *, char *, char *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "getAttributeValue", (void (**)(void))&getAttributeValue, "PyObject *(struct LxmlElement *, PyObject *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "iterattributes", (void (**)(void))&iterattributes, "PyObject *(struct LxmlElement *, int)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "collectAttributes", (void (**)(void))&collectAttributes, "PyObject *(xmlNode *, int)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "setAttributeValue", (void (**)(void))&setAttributeValue, "int (struct LxmlElement *, PyObject *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "delAttribute", (void (**)(void))&delAttribute, "int (struct LxmlElement *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "delAttributeFromNsName", (void (**)(void))&delAttributeFromNsName, "int (xmlNode *, char *, char *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "hasChild", (void (**)(void))&hasChild, "int (xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "findChild", (void (**)(void))&findChild, "xmlNode *(xmlNode *, Py_ssize_t)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "findChildForwards", (void (**)(void))&findChildForwards, "xmlNode *(xmlNode *, Py_ssize_t)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "findChildBackwards", (void (**)(void))&findChildBackwards, "xmlNode *(xmlNode *, Py_ssize_t)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "nextElement", (void (**)(void))&nextElement, "xmlNode *(xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "previousElement", (void (**)(void))&previousElement, "xmlNode *(xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "appendChild", (void (**)(void))&appendChild, "void (struct LxmlElement *, struct LxmlElement *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "pyunicode", (void (**)(void))&pyunicode, "PyObject *(char *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "utf8", (void (**)(void))&utf8, "PyObject *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "getNsTag", (void (**)(void))&getNsTag, "PyObject *(PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "namespacedName", (void (**)(void))&namespacedName, "PyObject *(xmlNode *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "namespacedNameFromNsName", (void (**)(void))&namespacedNameFromNsName, "PyObject *(char *, char *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "iteratorStoreNext", (void (**)(void))&iteratorStoreNext, "void (struct LxmlElementIterator *, struct LxmlElement *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "initTagMatch", (void (**)(void))&initTagMatch, "void (struct LxmlElementTagMatcher *, PyObject *)") < 0) goto bad;
  if (__Pyx_ImportFunction(module, "findOrBuildNodeNsPrefix", (void (**)(void))&findOrBuildNodeNsPrefix, "xmlNs *(struct LxmlDocument *, xmlNode *, char *, char *)") < 0) goto bad;
  Py_DECREF(module); module = 0;
  __pyx_ptype_4lxml_5etree__Document = __Pyx_ImportType("lxml.etree", "_Document", sizeof(struct LxmlDocument)); if (!__pyx_ptype_4lxml_5etree__Document) goto bad;
  __pyx_ptype_4lxml_5etree__Element = __Pyx_ImportType("lxml.etree", "_Element", sizeof(struct LxmlElement)); if (!__pyx_ptype_4lxml_5etree__Element) goto bad;
  __pyx_ptype_4lxml_5etree__ElementTree = __Pyx_ImportType("lxml.etree", "_ElementTree", sizeof(struct LxmlElementTree)); if (!__pyx_ptype_4lxml_5etree__ElementTree) goto bad;
  __pyx_ptype_4lxml_5etree__ElementTagMatcher = __Pyx_ImportType("lxml.etree", "_ElementTagMatcher", sizeof(struct LxmlElementTagMatcher)); if (!__pyx_ptype_4lxml_5etree__ElementTagMatcher) goto bad;
  __pyx_ptype_4lxml_5etree__ElementIterator = __Pyx_ImportType("lxml.etree", "_ElementIterator", sizeof(struct LxmlElementIterator)); if (!__pyx_ptype_4lxml_5etree__ElementIterator) goto bad;
  __pyx_ptype_4lxml_5etree_ElementBase = __Pyx_ImportType("lxml.etree", "ElementBase", sizeof(struct LxmlElementBase)); if (!__pyx_ptype_4lxml_5etree_ElementBase) goto bad;
  __pyx_ptype_4lxml_5etree_ElementClassLookup = __Pyx_ImportType("lxml.etree", "ElementClassLookup", sizeof(struct LxmlElementClassLookup)); if (!__pyx_ptype_4lxml_5etree_ElementClassLookup) goto bad;
  __pyx_ptype_4lxml_5etree_FallbackElementClassLookup = __Pyx_ImportType("lxml.etree", "FallbackElementClassLookup", sizeof(struct LxmlFallbackElementClassLookup)); if (!__pyx_ptype_4lxml_5etree_FallbackElementClassLookup) goto bad;
  return 0;
  bad:
  Py_XDECREF(module);
  return -1;
}

#endif
