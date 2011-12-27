/* See http://www.python-ldap.org/ for details.
 * $Id: schema.c,v 1.8 2009/04/17 12:19:09 stroeder Exp $ */

#include "common.h"

#include "schema.h"
#include "ldap_schema.h"

/* 
   This utility function takes a null delimited C array of (null
   delimited) C strings, creates its python equivalent and returns a
   new reference to it. If the array is empty or the pointer to it is
   NULL, an empty python array is returned. 
*/
PyObject* c_string_array_to_python(char **string_array)
{
  Py_ssize_t count = 0;
  char **s;
  PyObject *py_list;
  if (string_array) {
    for (s=string_array; *s != 0; s++) count++;
    py_list = PyList_New(count);
    count = 0;
    for (s=string_array; *s != 0; s++){
      PyList_SetItem(py_list, count, PyString_FromString(*s));
      count++;
    }
  } else py_list=PyList_New(0);
  return py_list;
}


/*
  This function returns a list of tuples. The first entry of each
  tuple is a string (lsei_name), and the second is a lists built from
  lsei_values.

  Probably the C data structure is modeled along the lines of a
  mapping "lsei_name -> (list of lsei_values)". However, there seems
  to be no guarantee that a lsei_name is unique, so I dare not use a
  python mapping for this beast...
 */
PyObject* schema_extension_to_python(LDAPSchemaExtensionItem **extensions)
{
  Py_ssize_t count = 0;
  LDAPSchemaExtensionItem **e;
  PyObject *py_list, *item_tuple;
  if (extensions) {
    for (e = extensions; *e !=0; e++) count++;
    py_list = PyList_New(count);
    count = 0;
    for (e = extensions; *e !=0; e++) {
      item_tuple = PyTuple_New(2);
      PyTuple_SetItem(item_tuple, 0, 
		      PyString_FromString((*e)->lsei_name));
      PyTuple_SetItem(item_tuple, 1, 
		      c_string_array_to_python((*e)->lsei_values));
      PyList_SetItem(py_list, count, item_tuple);
      count++;
      }
    }
  else py_list=PyList_New(0);
  return py_list;
}


/*
  The following four functions do the boring job: they take a python
  string, feed it into the respective parser functions provided by
  openldap, and build a python list from the data structure returned
  by the C function.
 */

static char doc_ldap_str2objectclass[] = 
"";

static PyObject*
l_ldap_str2objectclass(PyObject* self, PyObject *args)
{
  int ret=0, flag = LDAP_SCHEMA_ALLOW_NONE;
  char *oc_string;
  const char *errp;
  LDAPObjectClass *o;
  PyObject *oc_names, *oc_sup_oids, *oc_at_oids_must, 
    *oc_at_oids_may, *py_ret;
 

  if (!PyArg_ParseTuple(args, "si", &oc_string, &flag))
	return NULL;
  o = ldap_str2objectclass( oc_string, &ret, &errp, flag);
  if (ret) {
    py_ret = PyInt_FromLong(ret);
    return py_ret;
  }

  oc_sup_oids     = c_string_array_to_python(o->oc_sup_oids);
  oc_names        = c_string_array_to_python(o->oc_names);
  oc_at_oids_must = c_string_array_to_python(o->oc_at_oids_must);
  oc_at_oids_may  = c_string_array_to_python(o->oc_at_oids_may);
  py_ret = PyList_New(9);
  PyList_SetItem(py_ret, 0, PyString_FromString(o->oc_oid));
  PyList_SetItem(py_ret, 1, oc_names);
  if (o->oc_desc) {
    PyList_SetItem(py_ret, 2, PyString_FromString(o->oc_desc)); 
  } else {
    PyList_SetItem(py_ret, 2, PyString_FromString(""));
  }
  PyList_SetItem(py_ret, 3, PyInt_FromLong(o->oc_obsolete));
  PyList_SetItem(py_ret, 4, oc_sup_oids);
  PyList_SetItem(py_ret, 5, PyInt_FromLong(o->oc_kind));
  PyList_SetItem(py_ret, 6, oc_at_oids_must);
  PyList_SetItem(py_ret, 7, oc_at_oids_may);

  PyList_SetItem(py_ret, 8, 
		 schema_extension_to_python(o->oc_extensions));

  ldap_objectclass_free(o);
  return py_ret;
}


static char doc_ldap_str2attributetype[] = 
"";

static PyObject*
l_ldap_str2attributetype(PyObject* self, PyObject *args)
{
  int ret=0, flag = LDAP_SCHEMA_ALLOW_NONE;
  char *at_string;
  const char *errp;
  LDAPAttributeType *a;
  PyObject *py_ret;
  PyObject *at_names;
  
  if (!PyArg_ParseTuple(args, "si", &at_string,&flag))
    return NULL;
  a = ldap_str2attributetype( at_string, &ret, &errp, flag);
  if (ret) {
    py_ret = PyInt_FromLong(ret);
    return py_ret;
  }
  
  py_ret = PyList_New(15);
  PyList_SetItem(py_ret, 0, PyString_FromString(a->at_oid));
  at_names = c_string_array_to_python(a->at_names);
  PyList_SetItem(py_ret, 1, at_names);
  if (a->at_desc) {
    PyList_SetItem(py_ret, 2, PyString_FromString(a->at_desc)); 
  } else {
    PyList_SetItem(py_ret, 2, PyString_FromString(""));
  }
  PyList_SetItem(py_ret, 3, PyInt_FromLong(a->at_obsolete));
  if (a->at_sup_oid) {
    PyList_SetItem(py_ret, 4, PyString_FromString(a->at_sup_oid)); 
  } else {
    PyList_SetItem(py_ret, 4, PyString_FromString(""));
  }
  if (a->at_equality_oid) {
    PyList_SetItem(py_ret, 5, PyString_FromString(a->at_equality_oid)); 
  } else {
    PyList_SetItem(py_ret, 5, PyString_FromString(""));
  }
  if (a->at_ordering_oid) {
    PyList_SetItem(py_ret, 6, PyString_FromString(a->at_ordering_oid)); 
  } else {
    PyList_SetItem(py_ret, 6, PyString_FromString(""));
  }
  if (a->at_substr_oid) {
    PyList_SetItem(py_ret, 7, PyString_FromString(a->at_substr_oid)); 
  } else {
    PyList_SetItem(py_ret, 7, PyString_FromString(""));
  }
  if (a->at_syntax_oid) {
    PyList_SetItem(py_ret, 8, PyString_FromString(a->at_syntax_oid)); 
  } else {
    PyList_SetItem(py_ret, 8, PyString_FromString(""));
  }
  PyList_SetItem(py_ret, 9, PyInt_FromLong(a->at_syntax_len));
  PyList_SetItem(py_ret,10, PyInt_FromLong(a->at_single_value));
  PyList_SetItem(py_ret,11, PyInt_FromLong(a->at_collective));
  PyList_SetItem(py_ret,12, PyInt_FromLong(a->at_no_user_mod));
  PyList_SetItem(py_ret,13, PyInt_FromLong(a->at_usage));
  
  PyList_SetItem(py_ret, 14, 
		 schema_extension_to_python(a->at_extensions));
  ldap_attributetype_free(a);
  return py_ret;
}

static char doc_ldap_str2syntax[] = 
"";


static PyObject*
l_ldap_str2syntax(PyObject* self, PyObject *args)
{
  LDAPSyntax *s;
  int ret=0, flag = LDAP_SCHEMA_ALLOW_NONE;
  const char *errp;
  char *syn_string;
  PyObject *py_ret, *syn_names;
  
  if (!PyArg_ParseTuple(args, "si", &syn_string,&flag))
    return NULL;
  s = ldap_str2syntax(syn_string, &ret, &errp, flag);
  if (ret) {
    py_ret = PyInt_FromLong(ret);
    return py_ret;
  }
  py_ret = PyList_New(4);
  PyList_SetItem(py_ret, 0, PyString_FromString(s->syn_oid));
  syn_names = c_string_array_to_python(s->syn_names);
  PyList_SetItem(py_ret, 1, syn_names);
  if (s->syn_desc) {
    PyList_SetItem(py_ret, 2, PyString_FromString(s->syn_desc)); 
  } else {
    PyList_SetItem(py_ret, 2, PyString_FromString(""));
  }
  PyList_SetItem(py_ret, 3, 
		 schema_extension_to_python(s->syn_extensions));
  ldap_syntax_free(s);
  return py_ret;
}

static char doc_ldap_str2matchingrule[] = 
"";

static PyObject*
l_ldap_str2matchingrule(PyObject* self, PyObject *args)
{
  LDAPMatchingRule *m;
  int ret=0, flag = LDAP_SCHEMA_ALLOW_NONE;
  const char *errp;
  char *mr_string;
  PyObject *py_ret, *mr_names;
  
  if (!PyArg_ParseTuple(args, "si", &mr_string,&flag))
    return NULL;
  m = ldap_str2matchingrule(mr_string, &ret, &errp, flag);
  if (ret) {
    py_ret = PyInt_FromLong(ret);
    return py_ret;
  }
  py_ret = PyList_New(6);
  PyList_SetItem(py_ret, 0, PyString_FromString(m->mr_oid));
  mr_names = c_string_array_to_python(m->mr_names);
  PyList_SetItem(py_ret, 1, mr_names);
  if (m->mr_desc) {
    PyList_SetItem(py_ret, 2, PyString_FromString(m->mr_desc)); 
  } else {
    PyList_SetItem(py_ret, 2, PyString_FromString(""));
  }
  PyList_SetItem(py_ret, 3, PyInt_FromLong(m->mr_obsolete));
  if (m->mr_syntax_oid) {
    PyList_SetItem(py_ret, 4, PyString_FromString(m->mr_syntax_oid)); 
  } else {
    PyList_SetItem(py_ret, 4, PyString_FromString(""));
  }  
  PyList_SetItem(py_ret, 5, 
		 schema_extension_to_python(m->mr_extensions));
  ldap_matchingrule_free(m);
  return py_ret;
}

/* methods */

static PyMethodDef methods[] = {
    { "str2objectclass", (PyCFunction)l_ldap_str2objectclass,	METH_VARARGS,
    	doc_ldap_str2objectclass },
    { "str2attributetype", (PyCFunction)l_ldap_str2attributetype,	
      METH_VARARGS, doc_ldap_str2attributetype },
    { "str2syntax", (PyCFunction)l_ldap_str2syntax, 
      METH_VARARGS, doc_ldap_str2syntax },
    { "str2matchingrule", (PyCFunction)l_ldap_str2matchingrule, 
      METH_VARARGS, doc_ldap_str2matchingrule },
    { NULL, NULL }
};


void
LDAPinit_schema( PyObject* d ) {
    LDAPadd_methods( d, methods );
}
