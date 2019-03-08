/**
 * Copyright (c) 2006-2018 Apple Inc. All rights reserved.
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


/*
 * Support the Python 3 API while maintaining backward compatibility for the
 * Python 2 API.
 * Thanks to Lennart Regebro for http://python3porting.com/cextensions.html
 */
// Handle basic API changes
#if PY_MAJOR_VERSION >= 3
    // Basic renames (function parameters are the same)
    // No more int objects
    #define PyInt_FromLong PyLong_FromLong
#endif

#if PY_VERSION_HEX >= 0x03020000
    // CObjects to Capsules
    #define PyCObject_Check PyCapsule_CheckExact
    #define PyCObject_SetVoidPtr PyCapsule_SetPointer

    // More complex macros (function parameters are not the same)
    // Note for PyCObject_FromVoidPtr, destr is now the third parameter
    #define PyCObject_FromVoidPtr(cobj, destr) PyCapsule_New(cobj, NULL, destr)
    #define PyCObject_AsVoidPtr(pobj) PyCapsule_GetPointer(pobj, NULL)
#endif
// Handle differences in module definition syntax and interface
#if PY_MAJOR_VERSION >= 3
    #define MOD_ERROR_VAL NULL
    #define MOD_SUCCESS_VAL(val) val
    #define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
    #define MOD_DEF(ob, name, doc, methods) \
          static struct PyModuleDef moduledef = { \
            PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
          ob = PyModule_Create(&moduledef);
#else
    #define MOD_ERROR_VAL
    #define MOD_SUCCESS_VAL(val)
    #define MOD_INIT(name) void init##name(void)
    #define MOD_DEF(ob, name, doc, methods) \
          ob = Py_InitModule3(name, methods, doc);
#endif

static char krb5_mech_oid_bytes [] = "\x2a\x86\x48\x86\xf7\x12\x01\x02\x02";
gss_OID_desc krb5_mech_oid = { 9, &krb5_mech_oid_bytes };

static char spnego_mech_oid_bytes[] = "\x2b\x06\x01\x05\x05\x02";
gss_OID_desc spnego_mech_oid = { 6, &spnego_mech_oid_bytes };

PyObject *KrbException_class;
PyObject *BasicAuthException_class;
PyObject *PwdChangeException_class;
PyObject *GssException_class;

static PyObject *checkPassword(PyObject *self, PyObject *args)
{
    const char *user = NULL;
    const char *pswd = NULL;
    const char *service = NULL;
    const char *default_realm = NULL;
    int result = 0;

    if (! PyArg_ParseTuple(args, "ssss", &user, &pswd, &service, &default_realm)) {
        return NULL;
    }

    result = authenticate_user_krb5pwd(user, pswd, service, default_realm);

    if (result) {
        return Py_INCREF(Py_True), Py_True;
    } else {
        return NULL;
    }
}

static PyObject *changePassword(PyObject *self, PyObject *args)
{
    const char *newpswd = NULL;
    const char *oldpswd = NULL;
    const char *user = NULL;
    int result = 0;

    if (! PyArg_ParseTuple(args, "sss", &user, &oldpswd, &newpswd)) {
        return NULL;
    }

    result = change_user_krb5pwd(user, oldpswd, newpswd);

    if (result) {
        return Py_INCREF(Py_True), Py_True;
    } else {
        return NULL;
    }
}

static PyObject *getServerPrincipalDetails(PyObject *self, PyObject *args)
{
    const char *service = NULL;
    const char *hostname = NULL;
    char* result = NULL;

    if (! PyArg_ParseTuple(args, "ss", &service, &hostname)) {
        return NULL;
    }

    result = server_principal_details(service, hostname);

    if (result != NULL) {
        PyObject* pyresult = Py_BuildValue("s", result);
        free(result);
        return pyresult;
    } else {
        return NULL;
    }
}

static void
#if PY_VERSION_HEX >= 0x03020000
destroy_gss_client(PyObject *obj) {
    gss_client_state *state = PyCapsule_GetPointer(obj, NULL);
#else
destroy_gss_client(void *obj) {
    gss_client_state *state = (gss_client_state *)obj;
#endif
    if (state) {
        authenticate_gss_client_clean(state);
        free(state);
    }
}

static PyObject* authGSSClientInit(PyObject* self, PyObject* args, PyObject* keywds)
{
    const char *service = NULL;
    const char *principal = NULL;
    gss_client_state *state = NULL;
    PyObject *pystate = NULL;
    gss_server_state *delegatestate = NULL;
    PyObject *pydelegatestate = NULL;
    gss_OID mech_oid = GSS_C_NO_OID;
    PyObject *pymech_oid = NULL;
    static char *kwlist[] = {
        "service", "principal", "gssflags", "delegated", "mech_oid", NULL
    };
    long int gss_flags = GSS_C_MUTUAL_FLAG | GSS_C_SEQUENCE_FLAG;
    int result = 0;

    if (! PyArg_ParseTupleAndKeywords(
        args, keywds, "s|zlOO", kwlist,
        &service, &principal, &gss_flags, &pydelegatestate, &pymech_oid
    )) {
        return NULL;
    }

    state = (gss_client_state *) malloc(sizeof(gss_client_state));
    if (state == NULL)
    {
        PyErr_NoMemory();
        return NULL;
    }
    pystate = PyCObject_FromVoidPtr(state, &destroy_gss_client);

    if (pydelegatestate != NULL && PyCObject_Check(pydelegatestate)) {
        delegatestate = (gss_server_state*)PyCObject_AsVoidPtr(pydelegatestate);
    }

    if (pymech_oid != NULL && PyCObject_Check(pymech_oid)) {
        mech_oid = (gss_OID)PyCObject_AsVoidPtr(pymech_oid);
    }

    result = authenticate_gss_client_init(
        service, principal, gss_flags, delegatestate, mech_oid, state
    );

    if (result == AUTH_GSS_ERROR) {
        return NULL;
    }

    return Py_BuildValue("(iO)", result, pystate);
}

static PyObject *authGSSClientClean(PyObject *self, PyObject *args)
{
    return Py_BuildValue("i", AUTH_GSS_COMPLETE);
}

#if PY_VERSION_HEX >= 0x03020000
void destruct_channel_bindings(PyObject* o) {
    struct gss_channel_bindings_struct *channel_bindings = PyCapsule_GetPointer(o, NULL);
#else
void destruct_channel_bindings(void* o) {
    struct gss_channel_bindings_struct *channel_bindings = (struct gss_channel_bindings_struct *)o;
#endif

    if (channel_bindings != NULL) {
        if (channel_bindings->initiator_address.value != NULL) {
            PyMem_Free(channel_bindings->initiator_address.value);
        }

        if (channel_bindings->acceptor_address.value != NULL) {
            PyMem_Free(channel_bindings->acceptor_address.value);
        }

        if (channel_bindings->application_data.value != NULL) {
            PyMem_Free(channel_bindings->application_data.value);
        }

        free(channel_bindings);
    }
}

static PyObject *channelBindings(PyObject *self, PyObject *args, PyObject* keywds)
{
    int initiator_addrtype = GSS_C_AF_UNSPEC;
    int acceptor_addrtype = GSS_C_AF_UNSPEC;

    const char *encoding = NULL;
    char *initiator_address = NULL;
    char *acceptor_address = NULL;
    char *application_data = NULL;
    int initiator_length = 0;
    int acceptor_length = 0;
    int application_length = 0;

    PyObject *pychan_bindings = NULL;
    struct gss_channel_bindings_struct *input_chan_bindings;
    static char *kwlist[] = {"initiator_addrtype", "initiator_address", "acceptor_addrtype",
        "acceptor_address", "application_data", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "|iet#iet#et#", kwlist,
            &initiator_addrtype, &encoding, &initiator_address, &initiator_length,
            &acceptor_addrtype, &encoding, &acceptor_address, &acceptor_length,
            &encoding, &application_data, &application_length)) {
        return NULL;
    }

    input_chan_bindings = (struct gss_channel_bindings_struct *) malloc(sizeof(struct gss_channel_bindings_struct));
    pychan_bindings = PyCObject_FromVoidPtr(input_chan_bindings, &destruct_channel_bindings);

    input_chan_bindings->initiator_addrtype = initiator_addrtype;
    input_chan_bindings->initiator_address.length = initiator_length;
    input_chan_bindings->initiator_address.value = initiator_address;

    input_chan_bindings->acceptor_addrtype = acceptor_addrtype;
    input_chan_bindings->acceptor_address.length = acceptor_length;
    input_chan_bindings->acceptor_address.value = acceptor_address;

    input_chan_bindings->application_data.length = application_length;
    input_chan_bindings->application_data.value = application_data;

    return Py_BuildValue("N", pychan_bindings);
}

static PyObject *authGSSClientStep(PyObject *self, PyObject *args, PyObject* keywds)
{
    gss_client_state *state = NULL;
    PyObject *pystate = NULL;
    char *challenge = NULL;
    PyObject *pychan_bindings = NULL;
    struct gss_channel_bindings_struct *channel_bindings;
    static char *kwlist[] = {"state", "challenge", "channel_bindings", NULL};
    int result = 0;

    if (! PyArg_ParseTupleAndKeywords(args, keywds, "Os|O", kwlist, &pystate, &challenge, &pychan_bindings)) {
        return NULL;
    }

    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    if (pychan_bindings == NULL) {
        channel_bindings = GSS_C_NO_CHANNEL_BINDINGS;
    } else {
        if (!PyCObject_Check(pychan_bindings)) {
            PyErr_SetString(PyExc_TypeError, "Expected a gss_channel_bindings_struct object");
            return NULL;
        }
        channel_bindings = (struct gss_channel_bindings_struct *)PyCObject_AsVoidPtr(pychan_bindings);
    }

    result = authenticate_gss_client_step(state, challenge, channel_bindings);

    if (result == AUTH_GSS_ERROR) {
        return NULL;
    }

    return Py_BuildValue("i", result);
}

static PyObject *authGSSClientResponseConf(PyObject *self, PyObject *args)
{
    gss_client_state *state = NULL;
    PyObject *pystate = NULL;

    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }

    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    return Py_BuildValue("i", state->responseConf);
}

static PyObject *authGSSServerHasDelegated(PyObject *self, PyObject *args)
{
    gss_server_state *state = NULL;
    PyObject *pystate = NULL;

    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }

    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    return PyBool_FromLong(authenticate_gss_server_has_delegated(state));
}

static PyObject *authGSSClientResponse(PyObject *self, PyObject *args)
{
    gss_client_state *state = NULL;
    PyObject *pystate = NULL;

    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }

    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    return Py_BuildValue("s", state->response);
}

static PyObject *authGSSClientUserName(PyObject *self, PyObject *args)
{
    gss_client_state *state = NULL;
    PyObject *pystate = NULL;

    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }

    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    return Py_BuildValue("s", state->username);
}

static PyObject *authGSSClientUnwrap(PyObject *self, PyObject *args)
{
	gss_client_state *state = NULL;
	PyObject *pystate = NULL;
	char *challenge = NULL;
	int result = 0;

	if (! PyArg_ParseTuple(args, "Os", &pystate, &challenge)) {
		return NULL;
    }

	if (! PyCObject_Check(pystate)) {
		PyErr_SetString(PyExc_TypeError, "Expected a context object");
		return NULL;
	}

	state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);

	if (state == NULL) {
		return NULL;
    }

	result = authenticate_gss_client_unwrap(state, challenge);

	if (result == AUTH_GSS_ERROR) {
		return NULL;
    }

	return Py_BuildValue("i", result);
}

static PyObject *authGSSClientWrap(PyObject *self, PyObject *args)
{
	gss_client_state *state = NULL;
	PyObject *pystate = NULL;
	char *challenge = NULL;
	char *user = NULL;
	int protect = 0;
	int result = 0;

	if (! PyArg_ParseTuple(
        args, "Os|zi", &pystate, &challenge, &user, &protect
    )) {
		return NULL;
    }

	if (! PyCObject_Check(pystate)) {
		PyErr_SetString(PyExc_TypeError, "Expected a context object");
		return NULL;
	}

	state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);

	if (state == NULL) {
		return NULL;
    }

	result = authenticate_gss_client_wrap(state, challenge, user, protect);

	if (result == AUTH_GSS_ERROR) {
		return NULL;
    }

	return Py_BuildValue("i", result);
}

static PyObject *authGSSClientInquireCred(PyObject *self, PyObject *args)
{
    gss_client_state *state = NULL;
    PyObject *pystate = NULL;
    int result = 0;
    if (!PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }

    if (!PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_client_state *)PyCObject_AsVoidPtr(pystate);
    if (state == NULL) {
        return NULL;
    }

    result = authenticate_gss_client_inquire_cred(state);
    if (result == AUTH_GSS_ERROR) {
        return NULL;
    }

    return Py_BuildValue("i", result);
}

static void
#if PY_VERSION_HEX >= 0x03020000
destroy_gss_server(PyObject *obj) {
    gss_server_state *state = PyCapsule_GetPointer(obj, NULL);
#else
destroy_gss_server(void *obj) {
    gss_server_state *state = (gss_server_state *)obj;
#endif
    if (state) {
        authenticate_gss_server_clean(state);
        free(state);
    }
}

static PyObject *authGSSServerInit(PyObject *self, PyObject *args)
{
    const char *service = NULL;
    gss_server_state *state = NULL;
    PyObject *pystate = NULL;
    int result = 0;

    if (! PyArg_ParseTuple(args, "s", &service)) {
        return NULL;
    }

    state = (gss_server_state *) malloc(sizeof(gss_server_state));
    if (state == NULL)
    {
        PyErr_NoMemory();
        return NULL;
    }
    pystate = PyCObject_FromVoidPtr(state, &destroy_gss_server);

    result = authenticate_gss_server_init(service, state);

    if (result == AUTH_GSS_ERROR) {
        return NULL;
    }

    return Py_BuildValue("(iO)", result, pystate);
}

static PyObject *authGSSServerClean(PyObject *self, PyObject *args)
{
    return Py_BuildValue("i", AUTH_GSS_COMPLETE);
}

static PyObject *authGSSServerStep(PyObject *self, PyObject *args)
{
    gss_server_state *state = NULL;
    PyObject *pystate = NULL;
    char *challenge = NULL;
    int result = 0;

    if (! PyArg_ParseTuple(args, "Os", &pystate, &challenge)) {
        return NULL;
    }

    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    result = authenticate_gss_server_step(state, challenge);

    if (result == AUTH_GSS_ERROR) {
        return NULL;
    }

    return Py_BuildValue("i", result);
}

static PyObject *authGSSServerStoreDelegate(PyObject *self, PyObject *args)
{
    gss_server_state *state = NULL;
    PyObject *pystate = NULL;
    int result = 0;

    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }

    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    result = authenticate_gss_server_store_delegate(state);

    if (result == AUTH_GSS_ERROR) {
        return NULL;
    }
    
    return Py_BuildValue("i", result);
}

static PyObject *authGSSServerResponse(PyObject *self, PyObject *args)
{
    gss_server_state *state = NULL;
    PyObject *pystate = NULL;

    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }

    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }

    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    return Py_BuildValue("s", state->response);
}

static PyObject *authGSSServerUserName(PyObject *self, PyObject *args)
{
    gss_server_state *state = NULL;
    PyObject *pystate = NULL;
    
    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }
    
    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }
    
    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }
    
    return Py_BuildValue("s", state->username);
}

static PyObject *authGSSServerCacheName(PyObject *self, PyObject *args)
{
    gss_server_state *state = NULL;
    PyObject *pystate = NULL;
    
    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }
    
    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }
    
    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }

    return Py_BuildValue("s", state->ccname);
}

static PyObject *authGSSServerTargetName(PyObject *self, PyObject *args)
{
    gss_server_state *state = NULL;
    PyObject *pystate = NULL;
    
    if (! PyArg_ParseTuple(args, "O", &pystate)) {
        return NULL;
    }
    
    if (! PyCObject_Check(pystate)) {
        PyErr_SetString(PyExc_TypeError, "Expected a context object");
        return NULL;
    }
    
    state = (gss_server_state *)PyCObject_AsVoidPtr(pystate);

    if (state == NULL) {
        return NULL;
    }
    
    return Py_BuildValue("s", state->targetname);
}

static PyMethodDef KerberosMethods[] = {
    {
        "checkPassword",
        checkPassword, METH_VARARGS,
        "Check the supplied user/password against Kerberos KDC."
    },
    {
        "changePassword",
        changePassword, METH_VARARGS,
        "Change the user password."
    },
    {
        "getServerPrincipalDetails",
        getServerPrincipalDetails, METH_VARARGS,
        "Return the service principal for a given service and hostname."
    },
    {
        "authGSSClientInit",
        (PyCFunction)authGSSClientInit, METH_VARARGS | METH_KEYWORDS,
        "Initialize client-side GSSAPI operations."
    },
    {
        "channelBindings",
        (PyCFunction)channelBindings, METH_VARARGS | METH_KEYWORDS,
        "Build the Channel Bindings Structure for authGSSClientStep."
    },
    {
        "authGSSClientClean",
        authGSSClientClean, METH_VARARGS,
        "Terminate client-side GSSAPI operations."
    },
    {
        "authGSSClientStep",
        (PyCFunction)authGSSClientStep, METH_VARARGS | METH_KEYWORDS,
        "Do a client-side GSSAPI step."
    },
    {
        "authGSSClientResponse",
        authGSSClientResponse, METH_VARARGS,
        "Get the response from the last client-side GSSAPI step."
    },
    {
        "authGSSClientInquireCred",  authGSSClientInquireCred, METH_VARARGS,
        "Get the current user name, if any, without a client-side GSSAPI step"
    },
    {
        "authGSSClientResponseConf",
        authGSSClientResponseConf, METH_VARARGS,
        "return 1 if confidentiality was set in the last unwrapped buffer, 0 otherwise."
    },
    {
        "authGSSClientUserName",
        authGSSClientUserName, METH_VARARGS,
        "Get the user name from the last client-side GSSAPI step."
    },
    {
        "authGSSServerInit",
        authGSSServerInit, METH_VARARGS,
        "Initialize server-side GSSAPI operations."
    },
    {
        "authGSSClientWrap",
        authGSSClientWrap, METH_VARARGS,
        "Do a GSSAPI wrap."
    },
    {
        "authGSSClientUnwrap",
        authGSSClientUnwrap, METH_VARARGS,
        "Do a GSSAPI unwrap."
    },
    {
        "authGSSClientInquireCred", authGSSClientInquireCred, METH_VARARGS,
        "Get the current user name, if any."
    },
    {
        "authGSSServerClean",
        authGSSServerClean, METH_VARARGS,
        "Terminate server-side GSSAPI operations."
    },
    {
        "authGSSServerStep",
        authGSSServerStep, METH_VARARGS,
        "Do a server-side GSSAPI step."
    },
    {
        "authGSSServerHasDelegated",
        authGSSServerHasDelegated, METH_VARARGS,
        "Check whether the client delegated credentials to us."
    },
    {
        "authGSSServerStoreDelegate",
        authGSSServerStoreDelegate, METH_VARARGS,
        "Store the delegated Credentials."
    },
    {
        "authGSSServerResponse",
        authGSSServerResponse, METH_VARARGS,
        "Get the response from the last server-side GSSAPI step."
    },
    {
        "authGSSServerUserName",
        authGSSServerUserName, METH_VARARGS,
        "Get the user name from the last server-side GSSAPI step."
    },
    {
        "authGSSServerCacheName",
        authGSSServerCacheName, METH_VARARGS,
        "Get the location of the cache where delegated credentials are stored."
    },
    {
        "authGSSServerTargetName",
        authGSSServerTargetName, METH_VARARGS,
        "Get the target name from the last server-side GSSAPI step."
    },
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

MOD_INIT(kerberos)
{
    PyObject *m,*d;

    MOD_DEF(m, "kerberos", NULL, KerberosMethods);

    if (m == NULL) {
        return MOD_ERROR_VAL;
    }

    d = PyModule_GetDict(m);

    /* create the base exception class */
    if (! (KrbException_class = PyErr_NewException(
        "kerberos.KrbError", NULL, NULL
    ))) {
        goto error;
    }

    PyDict_SetItemString(d, "KrbError", KrbException_class);
    Py_INCREF(KrbException_class);

    /* ...and the derived exceptions */
    if (! (BasicAuthException_class = PyErr_NewException(
        "kerberos.BasicAuthError", KrbException_class, NULL
    ))) {
        goto error;
    }

    Py_INCREF(BasicAuthException_class);
    PyDict_SetItemString(d, "BasicAuthError", BasicAuthException_class);

    if (! (PwdChangeException_class = PyErr_NewException(
        "kerberos.PwdChangeError", KrbException_class, NULL
    ))) {
        goto error;
    }

    Py_INCREF(PwdChangeException_class);
    PyDict_SetItemString(d, "PwdChangeError", PwdChangeException_class);

    if (! (GssException_class = PyErr_NewException(
        "kerberos.GSSError", KrbException_class, NULL
    ))) {
        goto error;
    }

    Py_INCREF(GssException_class);
    PyDict_SetItemString(
        d, "GSSError", GssException_class
    );

    PyDict_SetItemString(
        d, "AUTH_GSS_COMPLETE", PyInt_FromLong(AUTH_GSS_COMPLETE)
    );
    PyDict_SetItemString(
        d, "AUTH_GSS_CONTINUE", PyInt_FromLong(AUTH_GSS_CONTINUE)
    );

    PyDict_SetItemString(
        d, "GSS_C_DELEG_FLAG", PyInt_FromLong(GSS_C_DELEG_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_C_MUTUAL_FLAG", PyInt_FromLong(GSS_C_MUTUAL_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_C_REPLAY_FLAG", PyInt_FromLong(GSS_C_REPLAY_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_C_SEQUENCE_FLAG", PyInt_FromLong(GSS_C_SEQUENCE_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_C_CONF_FLAG", PyInt_FromLong(GSS_C_CONF_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_C_INTEG_FLAG", PyInt_FromLong(GSS_C_INTEG_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_C_ANON_FLAG", PyInt_FromLong(GSS_C_ANON_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_C_PROT_READY_FLAG", PyInt_FromLong(GSS_C_PROT_READY_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_C_TRANS_FLAG", PyInt_FromLong(GSS_C_TRANS_FLAG)
    );
    PyDict_SetItemString(
        d, "GSS_MECH_OID_KRB5", PyCObject_FromVoidPtr(&krb5_mech_oid, NULL)
    );
    PyDict_SetItemString(
        d, "GSS_MECH_OID_SPNEGO", PyCObject_FromVoidPtr(&spnego_mech_oid, NULL)
    );

error:
    if (PyErr_Occurred()) {
         PyErr_SetString(PyExc_ImportError, "kerberos: init failed");
        return MOD_ERROR_VAL;
    }

    return MOD_SUCCESS_VAL(m);
}
