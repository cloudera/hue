/**
 * Copyright (c) 2006-2009 Apple Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 **/

#include <Python.h>

#include "kerberosbasic.h"
#include "kerberospw.h"
#include "kerberosgss.h"

PyObject *KrbException_class;
PyObject *BasicAuthException_class;
PyObject *PwdChangeException_class;
PyObject *GssException_class;

static PyObject *checkPassword(PyObject *self, PyObject *args)
{
    const char *user;
    const char *pswd;
    const char *service;
    const char *default_realm;
    int result = 0;

    if (!PyArg_ParseTuple(args, "ssss", &user, &pswd, &service, &default_realm))
        return NULL;

    result = authenticate_user_krb5pwd(user, pswd, service, default_realm);

    if (result)
        return Py_INCREF(Py_True), Py_True;
    else
        return NULL;
}

static PyObject *changePassword(PyObject *self, PyObject *args)
{
    const char *newpswd, *oldpswd;
    const char *user;
    int result = 0;

    if (!PyArg_ParseTuple(args, "sss", &user, &oldpswd, &newpswd))
        return NULL;

    result = change_user_krb5pwd(user, oldpswd, newpswd);

    if (result)
	return Py_INCREF(Py_True), Py_True;
    else
	return NULL;
}

static PyObject *getServerPrincipalDetails(PyObject *self, PyObject *args)
{
    const char *service;
    const char *hostname;
    char* result;

    if (!PyArg_ParseTuple(args, "ss", &service, &hostname))
        return NULL;

    result = server_principal_details(service, hostname);

    if (result != NULL)
    {
        PyObject* pyresult = Py_BuildValue("s", result);
        free(result);
        return pyresult;
    }
    else
        return NULL;
}

static PyObject* authGSSClientInit(PyObject* self, PyObject* args, PyObject* keywds)
{
    const char *service;
    gss_client_state *state;
    PyObject *pystate;
    static char *kwlist[] = {"service", "gssflags", NULL};
    long int gss_flags = GSS_C_MUTUAL_FLAG | GSS_C_SEQUENCE_FLAG;
    int result = 0;

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s|l", kwlist, &service, &gss_flags))
        return NULL;

    state = (gss_client_state *) malloc(sizeof(gss_client_state));
    pystate = PyCObject_FromVoidPtr(state, NULL);

    result = authenticate_gss_client_init(service, gss_flags, state);
    if (result == AUTH_GSS_ERROR)
        return NULL;

    return Py_BuildValue("(iO)", result, pystate);
}

static PyObject *authGSSClientClean(PyObject *self, PyObject *args)
{
    gss_client_state *state;
    PyObject *pystate;
    int result = 0;

    if (!PyArg_ParseTuple(args, "O", &pystate))
        return NULL;

    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);
    if (state != NULL)
    {
        result = authenticate_gss_client_clean(state);

        free(state);
        PyCObject_SetVoidPtr(pystate, NULL);
    }

    return Py_BuildValue("i", result);
}

static PyObject *authGSSClientStep(PyObject *self, PyObject *args)
{
    gss_client_state *state;
    PyObject *pystate;
    char *challenge;
    int result = 0;

    if (!PyArg_ParseTuple(args, "Os", &pystate, &challenge))
        return NULL;

    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);
    if (state == NULL)
        return NULL;

    result = authenticate_gss_client_step(state, challenge);
    if (result == AUTH_GSS_ERROR)
        return NULL;

    return Py_BuildValue("i", result);
}

static PyObject *authGSSClientResponse(PyObject *self, PyObject *args)
{
    gss_client_state *state;
    PyObject *pystate;

    if (!PyArg_ParseTuple(args, "O", &pystate))
        return NULL;

    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);
    if (state == NULL)
        return NULL;

    return Py_BuildValue("s", state->response);
}

static PyObject *authGSSClientUserName(PyObject *self, PyObject *args)
{
    gss_client_state *state;
    PyObject *pystate;

    if (!PyArg_ParseTuple(args, "O", &pystate))
        return NULL;

    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);
    if (state == NULL)
        return NULL;

    return Py_BuildValue("s", state->username);
}

static PyObject *authGSSClientUnwrap(PyObject *self, PyObject *args)
{
	gss_client_state *state;
	PyObject *pystate;
	char *challenge;
	int result = 0;

	if (!PyArg_ParseTuple(args, "Os", &pystate, &challenge))
		return NULL;

	if (!PyCObject_Check(pystate)) {
		PyErr_SetString(PyExc_TypeError, "Expected a context object");
		return NULL;
	}

	state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);
	if (state == NULL)
		return NULL;

	result = authenticate_gss_client_unwrap(state, challenge);
	if (result == AUTH_GSS_ERROR)
		return NULL;

	return Py_BuildValue("i", result);
}

static PyObject *authGSSClientWrap(PyObject *self, PyObject *args)
{
	gss_client_state *state;
	PyObject *pystate;
	char *challenge, *user = NULL;
	int result = 0;

	if (!PyArg_ParseTuple(args, "Os|z", &pystate, &challenge, &user))
		return NULL;

	if (!PyCObject_Check(pystate)) {
		PyErr_SetString(PyExc_TypeError, "Expected a context object");
		return NULL;
	}

	state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);
	if (state == NULL)
		return NULL;

	result = authenticate_gss_client_wrap(state, challenge, user);
	if (result == AUTH_GSS_ERROR)
		return NULL;

	return Py_BuildValue("i", result);
}

static PyObject *authGSSServerInit(PyObject *self, PyObject *args)
{
    const char *service;
    gss_server_state *state;
    PyObject *pystate;
    int result = 0;

    if (!PyArg_ParseTuple(args, "s", &service))
        return NULL;

    state = (gss_server_state *) malloc(sizeof(gss_server_state));
    pystate = PyCObject_FromVoidPtr(state, NULL);

    result = authenticate_gss_server_init(service, state);
    if (result == AUTH_GSS_ERROR)
        return NULL;

    return Py_BuildValue("(iO)", result, pystate);
}

static PyObject *authGSSServerClean(PyObject *self, PyObject *args)
{
    gss_server_state *state;
    PyObject *pystate;
    int result = 0;

    if (!PyArg_ParseTuple(args, "O", &pystate))
        return NULL;

    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);
    if (state != NULL)
    {
        result = authenticate_gss_server_clean(state);

        free(state);
        PyCObject_SetVoidPtr(pystate, NULL);
    }

    return Py_BuildValue("i", result);
}

static PyObject *authGSSServerStep(PyObject *self, PyObject *args)
{
    gss_server_state *state;
    PyObject *pystate;
    char *challenge;
    int result = 0;

    if (!PyArg_ParseTuple(args, "Os", &pystate, &challenge))
        return NULL;

    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);
    if (state == NULL)
        return NULL;

    result = authenticate_gss_server_step(state, challenge);
    if (result == AUTH_GSS_ERROR)
        return NULL;

    return Py_BuildValue("i", result);
}

static PyObject *authGSSServerResponse(PyObject *self, PyObject *args)
{
    gss_server_state *state;
    PyObject *pystate;

    if (!PyArg_ParseTuple(args, "O", &pystate))
        return NULL;

    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);
    if (state == NULL)
        return NULL;

    return Py_BuildValue("s", state->response);
}

static PyObject *authGSSServerUserName(PyObject *self, PyObject *args)
{
    gss_server_state *state;
    PyObject *pystate;
    
    if (!PyArg_ParseTuple(args, "O", &pystate))
        return NULL;
    
    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }
    
    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);
    if (state == NULL)
        return NULL;
    
    return Py_BuildValue("s", state->username);
}

static PyObject *authGSSServerTargetName(PyObject *self, PyObject *args)
{
    gss_server_state *state;
    PyObject *pystate;
    
    if (!PyArg_ParseTuple(args, "O", &pystate))
        return NULL;
    
    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }
    
    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);
    if (state == NULL)
        return NULL;
    
    return Py_BuildValue("s", state->targetname);
}

static PyMethodDef KerberosMethods[] = {
    {"checkPassword",  checkPassword, METH_VARARGS,
     "Check the supplied user/password against Kerberos KDC."},
    {"changePassword",  changePassword, METH_VARARGS,
     "Change the user password."},
    {"getServerPrincipalDetails",  getServerPrincipalDetails, METH_VARARGS,
     "Return the service principal for a given service and hostname."},
    {"authGSSClientInit",  (PyCFunction)authGSSClientInit, METH_VARARGS | METH_KEYWORDS,
     "Initialize client-side GSSAPI operations."},
    {"authGSSClientClean",  authGSSClientClean, METH_VARARGS,
     "Terminate client-side GSSAPI operations."},
    {"authGSSClientStep",  authGSSClientStep, METH_VARARGS,
     "Do a client-side GSSAPI step."},
    {"authGSSClientResponse",  authGSSClientResponse, METH_VARARGS,
     "Get the response from the last client-side GSSAPI step."},
    {"authGSSClientUserName",  authGSSClientUserName, METH_VARARGS,
     "Get the user name from the last client-side GSSAPI step."},
    {"authGSSServerInit",  authGSSServerInit, METH_VARARGS,
     "Initialize server-side GSSAPI operations."},
    {"authGSSClientWrap",  authGSSClientWrap, METH_VARARGS,
     "Do a GSSAPI wrap."},
    {"authGSSClientUnwrap",  authGSSClientUnwrap, METH_VARARGS,
     "Do a GSSAPI unwrap."},
    {"authGSSServerClean",  authGSSServerClean, METH_VARARGS,
     "Terminate server-side GSSAPI operations."},
    {"authGSSServerStep",  authGSSServerStep, METH_VARARGS,
     "Do a server-side GSSAPI step."},
    {"authGSSServerResponse",  authGSSServerResponse, METH_VARARGS,
     "Get the response from the last server-side GSSAPI step."},
    {"authGSSServerUserName",  authGSSServerUserName, METH_VARARGS,
        "Get the user name from the last server-side GSSAPI step."},
    {"authGSSServerTargetName",  authGSSServerTargetName, METH_VARARGS,
        "Get the target name from the last server-side GSSAPI step."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initkerberos(void)
{
    PyObject *m,*d;

    m = Py_InitModule("kerberos", KerberosMethods);

    d = PyModule_GetDict(m);

    /* create the base exception class */
    if (!(KrbException_class = PyErr_NewException("kerberos.KrbError", NULL, NULL)))
        goto error;
    PyDict_SetItemString(d, "KrbError", KrbException_class);
    Py_INCREF(KrbException_class);

    /* ...and the derived exceptions */
    if (!(BasicAuthException_class = PyErr_NewException("kerberos.BasicAuthError", KrbException_class, NULL)))
        goto error;
    Py_INCREF(BasicAuthException_class);
    PyDict_SetItemString(d, "BasicAuthError", BasicAuthException_class);

    if (!(PwdChangeException_class = PyErr_NewException("kerberos.PwdChangeError", KrbException_class, NULL)))
        goto error;
    Py_INCREF(PwdChangeException_class);
    PyDict_SetItemString(d, "PwdChangeError", PwdChangeException_class);

    if (!(GssException_class = PyErr_NewException("kerberos.GSSError", KrbException_class, NULL)))
        goto error;
    Py_INCREF(GssException_class);
    PyDict_SetItemString(d, "GSSError", GssException_class);

    PyDict_SetItemString(d, "AUTH_GSS_COMPLETE", PyInt_FromLong(AUTH_GSS_COMPLETE));
    PyDict_SetItemString(d, "AUTH_GSS_CONTINUE", PyInt_FromLong(AUTH_GSS_CONTINUE));

    PyDict_SetItemString(d, "GSS_C_DELEG_FLAG", PyInt_FromLong(GSS_C_DELEG_FLAG));
    PyDict_SetItemString(d, "GSS_C_MUTUAL_FLAG", PyInt_FromLong(GSS_C_MUTUAL_FLAG));
    PyDict_SetItemString(d, "GSS_C_REPLAY_FLAG", PyInt_FromLong(GSS_C_REPLAY_FLAG));
    PyDict_SetItemString(d, "GSS_C_SEQUENCE_FLAG", PyInt_FromLong(GSS_C_SEQUENCE_FLAG));
    PyDict_SetItemString(d, "GSS_C_CONF_FLAG", PyInt_FromLong(GSS_C_CONF_FLAG));
    PyDict_SetItemString(d, "GSS_C_INTEG_FLAG", PyInt_FromLong(GSS_C_INTEG_FLAG));
    PyDict_SetItemString(d, "GSS_C_ANON_FLAG", PyInt_FromLong(GSS_C_ANON_FLAG));
    PyDict_SetItemString(d, "GSS_C_PROT_READY_FLAG", PyInt_FromLong(GSS_C_PROT_READY_FLAG));
    PyDict_SetItemString(d, "GSS_C_TRANS_FLAG", PyInt_FromLong(GSS_C_TRANS_FLAG));

error:
    if (PyErr_Occurred())
        PyErr_SetString(PyExc_ImportError, "kerberos: init failed");
}
