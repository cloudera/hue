/*
 * context.c
 *
 * Copyright (C) AB Strakt
 * Copyright (C) Jean-Paul Calderone
 * See LICENSE for details.
 *
 * SSL Context objects and their methods.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 */
#include <Python.h>

#if PY_VERSION_HEX >= 0x02050000
# define PYARG_PARSETUPLE_FORMAT const char
# define PYOBJECT_GETATTRSTRING_TYPE const char*
#else
# define PYARG_PARSETUPLE_FORMAT char
# define PYOBJECT_GETATTRSTRING_TYPE char*
#endif

#ifndef MS_WINDOWS
#  include <sys/socket.h>
#  include <netinet/in.h>
#  if !(defined(__BEOS__) || defined(__CYGWIN__))
#    include <netinet/tcp.h>
#  endif
#else
#  include <winsock.h>
#  include <wincrypt.h>
#endif

#define SSL_MODULE
#include "ssl.h"

/*
 * CALLBACKS
 *
 * Callbacks work like this: We provide a "global" callback in C which
 * transforms the arguments into a Python argument tuple and calls the
 * corresponding Python callback, and then parsing the return value back into
 * things the C function can return.
 *
 * Three caveats:
 *  + How do we find the Context object where the Python callbacks are stored?
 *  + What about multithreading and execution frames?
 *  + What about Python callbacks that raise exceptions?
 *
 * The solution to the first issue is trivial if the callback provides
 * "userdata" functionality. Since the only callbacks that don't provide
 * userdata do provide a pointer to an SSL structure, we can associate an SSL
 * object and a Connection one-to-one via the SSL_set/get_app_data()
 * functions.
 *
 * The solution to the other issue is to rewrite the Py_BEGIN_ALLOW_THREADS
 * macro allowing it (or rather a new macro) to specify where to save the
 * thread state (in our case, as a member of the Connection/Context object) so
 * we can retrieve it again before calling the Python callback.
 */

/*
 * Globally defined passphrase callback.  This is called from OpenSSL
 * internally.  The GIL will not be held when this function is invoked.  It
 * must not be held when the function returns.
 *
 * Arguments: buf    - Buffer to store the returned passphrase in
 *            maxlen - Maximum length of the passphrase
 *            verify - If true, the passphrase callback should ask for a
 *                     password twice and verify they're equal. If false, only
 *                     ask once.
 *            arg    - User data, always a Context object
 * Returns:   The length of the password if successful, 0 otherwise
 */
static int
global_passphrase_callback(char *buf, int maxlen, int verify, void *arg)
{
    /*
     * Initialize len here because we're always going to return it, and we
     * might jump to the return before it gets initialized in any other way.
     */
    int len = 0;
    char *str;
    PyObject *argv, *ret = NULL;
    ssl_ContextObj *ctx = (ssl_ContextObj *)arg;

    /*
     * GIL isn't held yet.  First things first - acquire it, or any Python API
     * we invoke might segfault or blow up the sun.  The reverse will be done
     * before returning.
     */
    MY_END_ALLOW_THREADS(ctx->tstate);

    /* The Python callback is called with a (maxlen,verify,userdata) tuple */
    argv = Py_BuildValue("(iiO)", maxlen, verify, ctx->passphrase_userdata);

    /*
     * XXX Didn't check argv to see if it was NULL. -exarkun
     */
    ret = PyEval_CallObject(ctx->passphrase_callback, argv);
    Py_DECREF(argv);

    if (ret == NULL) {
        /*
         * The callback raised an exception.  It will be raised by whatever
         * Python API triggered this callback.
         */
        goto out;
    }

    if (!PyObject_IsTrue(ret)) {
        /*
         * Returned "", or None, or something.  Treat it as no passphrase.
         */
        Py_DECREF(ret);
	goto out;
    }

    if (!PyBytes_Check(ret)) {
        /*
         * XXX Returned something that wasn't a string.  This is bogus.  We'll
         * return 0 and OpenSSL will treat it as an error, resulting in an
         * exception from whatever Python API triggered this callback.
         */
        Py_DECREF(ret);
        goto out;
    }

    len = PyBytes_Size(ret);
    if (len > maxlen) {
        /*
         * Returned more than we said they were allowed to return.  Just
         * truncate it.  Might be better to raise an exception,
         * instead. -exarkun
         */
        len = maxlen;
    }

    str = PyBytes_AsString(ret);
    strncpy(buf, str, len);
    Py_XDECREF(ret);

  out:
    /*
     * This function is returning into OpenSSL.  Release the GIL again.
     */
    MY_BEGIN_ALLOW_THREADS(ctx->tstate);
    return len;
}

/*
 * Globally defined verify callback
 *
 * Arguments: ok       - True everything is OK "so far", false otherwise
 *            x509_ctx - Contains the certificate being checked, the current
 *                       error number and depth, and the Connection we're
 *                       dealing with
 * Returns:   True if everything is okay, false otherwise
 */
static int
global_verify_callback(int ok, X509_STORE_CTX *x509_ctx)
{
    PyObject *argv, *ret;
    SSL *ssl;
    ssl_ConnectionObj *conn;
    crypto_X509Obj *cert;
    int errnum, errdepth, c_ret;

    // Get Connection object to check thread state
    ssl = (SSL *)X509_STORE_CTX_get_app_data(x509_ctx);
    conn = (ssl_ConnectionObj *)SSL_get_app_data(ssl);

    MY_END_ALLOW_THREADS(conn->tstate);

    cert = new_x509(X509_STORE_CTX_get_current_cert(x509_ctx), 0);
    errnum = X509_STORE_CTX_get_error(x509_ctx);
    errdepth = X509_STORE_CTX_get_error_depth(x509_ctx);

    argv = Py_BuildValue("(OOiii)", (PyObject *)conn, (PyObject *)cert,
                                    errnum, errdepth, ok);
    Py_DECREF(cert);
    ret = PyEval_CallObject(conn->context->verify_callback, argv);
    Py_DECREF(argv);

    if (ret != NULL && PyObject_IsTrue(ret)) {
        X509_STORE_CTX_set_error(x509_ctx, X509_V_OK);
        Py_DECREF(ret);
        c_ret = 1;
    } else {
        c_ret = 0;
    }

    MY_BEGIN_ALLOW_THREADS(conn->tstate);
    return c_ret;
}

/*
 * Globally defined info callback.  This is called from OpenSSL internally.
 * The GIL will not be held when this function is invoked.  It must not be held
 * when the function returns.
 *
 * Arguments: ssl   - The Connection
 *            where - The part of the SSL code that called us
 *            _ret  - The return code of the SSL function that called us
 * Returns:   None
 */
static void
global_info_callback(const SSL *ssl, int where, int _ret)
{
    ssl_ConnectionObj *conn = (ssl_ConnectionObj *)SSL_get_app_data(ssl);
    PyObject *argv, *ret;

    /*
     * GIL isn't held yet.  First things first - acquire it, or any Python API
     * we invoke might segfault or blow up the sun.  The reverse will be done
     * before returning.
     */
    MY_END_ALLOW_THREADS(conn->tstate);

    argv = Py_BuildValue("(Oii)", (PyObject *)conn, where, _ret);
    ret = PyEval_CallObject(conn->context->info_callback, argv);
    Py_DECREF(argv);

    if (ret == NULL) {
        /*
         * XXX - This should be reported somehow. -exarkun
         */
        PyErr_Clear();
    } else {
        Py_DECREF(ret);
    }

    /*
     * This function is returning into OpenSSL.  Release the GIL again.
     */
    MY_BEGIN_ALLOW_THREADS(conn->tstate);
    return;
}

/*
 * Globally defined TLS extension server name callback.  This is called from
 * OpenSSL internally.  The GIL will not be held when this function is invoked.
 * It must not be held when the function returns.
 *
 * ssl represents the connection this callback is for
 *
 * alert is a pointer to the alert value which maybe will be emitted to the
 * client if there is an error handling the client hello (which contains the
 * server name).  This is an out parameter, maybe.
 *
 * arg is an arbitrary pointer specified by SSL_CTX_set_tlsext_servername_arg.
 * It will be NULL for all pyOpenSSL uses.
 */
static int
global_tlsext_servername_callback(const SSL *ssl, int *alert, void *arg) {
    int result = 0;
    PyObject *argv, *ret;
    ssl_ConnectionObj *conn = (ssl_ConnectionObj *)SSL_get_app_data(ssl);

    /*
     * GIL isn't held yet.  First things first - acquire it, or any Python API
     * we invoke might segfault or blow up the sun.  The reverse will be done
     * before returning.
     */
    MY_END_ALLOW_THREADS(conn->tstate);

    argv = Py_BuildValue("(O)", (PyObject *)conn);
    ret = PyEval_CallObject(conn->context->tlsext_servername_callback, argv);
    Py_DECREF(argv);
    Py_DECREF(ret);

    /*
     * This function is returning into OpenSSL.  Release the GIL again.
     */
    MY_BEGIN_ALLOW_THREADS(conn->tstate);
    return result;
}

/*
 * More recent builds of OpenSSL may have SSLv2 completely disabled.
 */
#ifdef OPENSSL_NO_SSL2
#define SSLv2_METHOD_TEXT ""
#else
#define SSLv2_METHOD_TEXT "SSLv2_METHOD, "
#endif


static char ssl_Context_doc[] = "\n\
Context(method) -> Context instance\n\
\n\
OpenSSL.SSL.Context instances define the parameters for setting up new SSL\n\
connections.\n\
\n\
@param method: One of " SSLv2_METHOD_TEXT "SSLv3_METHOD, SSLv23_METHOD, or\n\
               TLSv1_METHOD.\n\
";

#undef SSLv2_METHOD_TEXT

static char ssl_Context_load_verify_locations_doc[] = "\n\
Let SSL know where we can find trusted certificates for the certificate\n\
chain\n\
\n\
@param cafile: In which file we can find the certificates\n\
@param capath: In which directory we can find the certificates\n\
@return: None\n\
";
static PyObject *
ssl_Context_load_verify_locations(ssl_ContextObj *self, PyObject *args) {
    char *cafile = NULL;
    char *capath = NULL;

    if (!PyArg_ParseTuple(args, "z|z:load_verify_locations", &cafile, &capath)) {
        return NULL;
    }

    if (!SSL_CTX_load_verify_locations(self->ctx, cafile, capath))
    {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static char ssl_Context_set_default_verify_paths_doc[] = "\n\
Use the platform-specific CA certificate locations\n\
\n\
@return: None\n\
";
static PyObject *
ssl_Context_set_default_verify_paths(ssl_ContextObj *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, ":set_default_verify_paths")) {
        return NULL;
    }

    /*
     * XXX Error handling for SSL_CTX_set_default_verify_paths is untested.
     * -exarkun
     */
    if (!SSL_CTX_set_default_verify_paths(self->ctx)) {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
};


static char ssl_Context_set_passwd_cb_doc[] = "\n\
Set the passphrase callback\n\
\n\
@param callback: The Python callback to use\n\
@param userdata: (optional) A Python object which will be given as\n\
                 argument to the callback\n\
@return: None\n\
";
static PyObject *
ssl_Context_set_passwd_cb(ssl_ContextObj *self, PyObject *args)
{
    PyObject *callback = NULL, *userdata = Py_None;

    if (!PyArg_ParseTuple(args, "O|O:set_passwd_cb", &callback, &userdata))
        return NULL;

    if (!PyCallable_Check(callback))
    {
        PyErr_SetString(PyExc_TypeError, "expected PyCallable");
        return NULL;
    }

    Py_DECREF(self->passphrase_callback);
    Py_INCREF(callback);
    self->passphrase_callback = callback;
    SSL_CTX_set_default_passwd_cb(self->ctx, global_passphrase_callback);

    Py_DECREF(self->passphrase_userdata);
    Py_INCREF(userdata);
    self->passphrase_userdata = userdata;
    SSL_CTX_set_default_passwd_cb_userdata(self->ctx, (void *)self);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyTypeObject *
type_modified_error(const char *name) {
    PyErr_Format(PyExc_RuntimeError,
                 "OpenSSL.crypto's '%s' attribute has been modified",
                 name);
    return NULL;
}

static PyTypeObject *
import_crypto_type(const char *name, size_t objsize) {
    PyObject *module, *type, *name_attr;
    PyTypeObject *res;
    int right_name;

    module = PyImport_ImportModule("OpenSSL.crypto");
    if (module == NULL) {
        return NULL;
    }
    type = PyObject_GetAttrString(module, (PYOBJECT_GETATTRSTRING_TYPE)name);
    Py_DECREF(module);
    if (type == NULL) {
        return NULL;
    }
    if (!(PyType_Check(type))) {
        Py_DECREF(type);
        return type_modified_error(name);
    }
    name_attr = PyObject_GetAttrString(type, "__name__");
    if (name_attr == NULL) {
        Py_DECREF(type);
        return NULL;
    }

#ifdef PY3
    {
        PyObject* asciiname = PyUnicode_AsASCIIString(name_attr);
        Py_DECREF(name_attr);
        name_attr = asciiname;
    }
#endif
    right_name = (PyBytes_CheckExact(name_attr) &&
                  strcmp(name, PyBytes_AsString(name_attr)) == 0);
    Py_DECREF(name_attr);
    res = (PyTypeObject *)type;
    if (!right_name || res->tp_basicsize != objsize) {
        Py_DECREF(type);
        return type_modified_error(name);
    }
    return res;
}

static crypto_X509Obj *
parse_certificate_argument(const char* format, PyObject* args) {
    static PyTypeObject *crypto_X509_type = NULL;
    crypto_X509Obj *cert;

    if (!crypto_X509_type) {
        crypto_X509_type = import_crypto_type("X509", sizeof(crypto_X509Obj));
        if (!crypto_X509_type) {
            return NULL;
        }
    }
    if (!PyArg_ParseTuple(args, (PYARG_PARSETUPLE_FORMAT *)format,
                          crypto_X509_type, &cert)) {
        return NULL;
    }
    return cert;
}

static char ssl_Context_add_extra_chain_cert_doc[] = "\n\
Add certificate to chain\n\
\n\
@param certobj: The X509 certificate object to add to the chain\n\
@return: None\n\
";

static PyObject *
ssl_Context_add_extra_chain_cert(ssl_ContextObj *self, PyObject *args)
{
    X509* cert_original;
    crypto_X509Obj *cert = parse_certificate_argument(
        "O!:add_extra_chain_cert", args);
    if (cert == NULL)
    {
        return NULL;
    }
    if (!(cert_original = X509_dup(cert->x509)))
    {
        /* exception_from_error_queue(ssl_Error); */
        PyErr_SetString(PyExc_RuntimeError, "X509_dup failed");
        return NULL;
    }
    if (!SSL_CTX_add_extra_chain_cert(self->ctx, cert_original))
    {
        X509_free(cert_original);
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}


static char ssl_Context_use_certificate_chain_file_doc[] = "\n\
Load a certificate chain from a file\n\
\n\
@param certfile: The name of the certificate chain file\n\
@return: None\n\
";
static PyObject *
ssl_Context_use_certificate_chain_file(ssl_ContextObj *self, PyObject *args)
{
    char *certfile;

    if (!PyArg_ParseTuple(args, "s:use_certificate_chain_file", &certfile))
        return NULL;

    if (!SSL_CTX_use_certificate_chain_file(self->ctx, certfile))
    {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}


static char ssl_Context_use_certificate_file_doc[] = "\n\
Load a certificate from a file\n\
\n\
@param certfile: The name of the certificate file\n\
@param filetype: (optional) The encoding of the file, default is PEM\n\
@return: None\n\
";
static PyObject *
ssl_Context_use_certificate_file(ssl_ContextObj *self, PyObject *args)
{
    char *certfile;
    int filetype = SSL_FILETYPE_PEM;

    if (!PyArg_ParseTuple(args, "s|i:use_certificate_file", &certfile, &filetype))
        return NULL;

    if (!SSL_CTX_use_certificate_file(self->ctx, certfile, filetype))
    {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static char ssl_Context_use_certificate_doc[] = "\n\
Load a certificate from a X509 object\n\
\n\
@param cert: The X509 object\n\
@return: None\n\
";
static PyObject *
ssl_Context_use_certificate(ssl_ContextObj *self, PyObject *args)
{
    crypto_X509Obj *cert = parse_certificate_argument(
        "O!:use_certificate", args);
    if (cert == NULL) {
        return NULL;
    }
    
    if (!SSL_CTX_use_certificate(self->ctx, cert->x509))
    {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static char ssl_Context_use_privatekey_file_doc[] = "\n\
Load a private key from a file\n\
\n\
@param keyfile: The name of the key file\n\
@param filetype: (optional) The encoding of the file, default is PEM\n\
@return: None\n\
";
static PyObject *
ssl_Context_use_privatekey_file(ssl_ContextObj *self, PyObject *args)
{
    char *keyfile;
    int filetype = SSL_FILETYPE_PEM, ret;

    if (!PyArg_ParseTuple(args, "s|i:use_privatekey_file", &keyfile, &filetype))
        return NULL;

    MY_BEGIN_ALLOW_THREADS(self->tstate);
    ret = SSL_CTX_use_PrivateKey_file(self->ctx, keyfile, filetype);
    MY_END_ALLOW_THREADS(self->tstate);

    if (PyErr_Occurred())
    {
        flush_error_queue();
        return NULL;
    }

    if (!ret)
    {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static char ssl_Context_use_privatekey_doc[] = "\n\
Load a private key from a PKey object\n\
\n\
@param pkey: The PKey object\n\
@return: None\n\
";
static PyObject *
ssl_Context_use_privatekey(ssl_ContextObj *self, PyObject *args) {
    static PyTypeObject *crypto_PKey_type = NULL;
    crypto_PKeyObj *pkey;

    if (!crypto_PKey_type) {
        crypto_PKey_type = import_crypto_type("PKey", sizeof(crypto_PKeyObj));
        if (!crypto_PKey_type) {
            return NULL;
        }
    }
    if (!PyArg_ParseTuple(args, "O!:use_privatekey", crypto_PKey_type, &pkey)) {
        return NULL;
    }

    if (!SSL_CTX_use_PrivateKey(self->ctx, pkey->pkey)) {
        exception_from_error_queue(ssl_Error);
        return NULL;
    } else {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static char ssl_Context_check_privatekey_doc[] = "\n\
Check that the private key and certificate match up\n\
\n\
@return: None (raises an exception if something's wrong)\n\
";
static PyObject *
ssl_Context_check_privatekey(ssl_ContextObj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":check_privatekey"))
        return NULL;

    if (!SSL_CTX_check_private_key(self->ctx))
    {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static char ssl_Context_load_client_ca_doc[] = "\n\
Load the trusted certificates that will be sent to the client (basically\n \
telling the client \"These are the guys I trust\").  Does not actually\n\
imply any of the certificates are trusted; that must be configured\n\
separately.\n\
\n\
@param cafile: The name of the certificates file\n\
@return: None\n\
";
static PyObject *
ssl_Context_load_client_ca(ssl_ContextObj *self, PyObject *args)
{
    char *cafile;

    if (!PyArg_ParseTuple(args, "s:load_client_ca", &cafile))
        return NULL;

    SSL_CTX_set_client_CA_list(self->ctx, SSL_load_client_CA_file(cafile));

    Py_INCREF(Py_None);
    return Py_None;
}

static char ssl_Context_set_session_id_doc[] = "\n\
Set the session identifier, this is needed if you want to do session\n\
resumption (which, ironically, isn't implemented yet)\n\
\n\
@param buf: A Python object that can be safely converted to a string\n\
@returns: None\n\
";
static PyObject *
ssl_Context_set_session_id(ssl_ContextObj *self, PyObject *args)
{
    unsigned char *buf;
    unsigned int len;

    if (!PyArg_ParseTuple(args, "s#:set_session_id", &buf, &len))
        return NULL;

    if (!SSL_CTX_set_session_id_context(self->ctx, buf, len))
    {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static char ssl_Context_set_verify_doc[] = "\n\
Set the verify mode and verify callback\n\
\n\
@param mode: The verify mode, this is either VERIFY_NONE or\n\
             VERIFY_PEER combined with possible other flags\n\
@param callback: The Python callback to use\n\
@return: None\n\
\n\
See SSL_CTX_set_verify(3SSL) for further details.\n\
";
static PyObject *
ssl_Context_set_verify(ssl_ContextObj *self, PyObject *args)
{
    int mode;
    PyObject *callback = NULL;

    if (!PyArg_ParseTuple(args, "iO:set_verify", &mode, &callback))
        return NULL;

    if (!PyCallable_Check(callback))
    {
        PyErr_SetString(PyExc_TypeError, "expected PyCallable");
        return NULL;
    }

    Py_DECREF(self->verify_callback);
    Py_INCREF(callback);
    self->verify_callback = callback;
    SSL_CTX_set_verify(self->ctx, mode, global_verify_callback);

    Py_INCREF(Py_None);
    return Py_None;
}

static char ssl_Context_set_verify_depth_doc[] = "\n\
Set the verify depth\n\
\n\
@param depth: An integer specifying the verify depth\n\
@return: None\n\
";
static PyObject *
ssl_Context_set_verify_depth(ssl_ContextObj *self, PyObject *args)
{
    int depth;

    if (!PyArg_ParseTuple(args, "i:set_verify_depth", &depth))
        return NULL;

    SSL_CTX_set_verify_depth(self->ctx, depth);
    Py_INCREF(Py_None);
    return Py_None;
}

static char ssl_Context_get_verify_mode_doc[] = "\n\
Get the verify mode\n\
\n\
@return: The verify mode\n\
";
static PyObject *
ssl_Context_get_verify_mode(ssl_ContextObj *self, PyObject *args)
{
    int mode;

    if (!PyArg_ParseTuple(args, ":get_verify_mode"))
        return NULL;

    mode = SSL_CTX_get_verify_mode(self->ctx);
    return PyLong_FromLong((long)mode);
}

static char ssl_Context_get_verify_depth_doc[] = "\n\
Get the verify depth\n\
\n\
@return: The verify depth\n\
";
static PyObject *
ssl_Context_get_verify_depth(ssl_ContextObj *self, PyObject *args)
{
    int depth;

    if (!PyArg_ParseTuple(args, ":get_verify_depth"))
        return NULL;

    depth = SSL_CTX_get_verify_depth(self->ctx);
    return PyLong_FromLong((long)depth);
}

static char ssl_Context_load_tmp_dh_doc[] = "\n\
Load parameters for Ephemeral Diffie-Hellman\n\
\n\
@param dhfile: The file to load EDH parameters from\n\
@return: None\n\
";
static PyObject *
ssl_Context_load_tmp_dh(ssl_ContextObj *self, PyObject *args)
{
    char *dhfile;
    BIO *bio;
    DH *dh;

    if (!PyArg_ParseTuple(args, "s:load_tmp_dh", &dhfile))
        return NULL;

    bio = BIO_new_file(dhfile, "r");
    if (bio == NULL) {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }

    dh = PEM_read_bio_DHparams(bio, NULL, NULL, NULL);
    SSL_CTX_set_tmp_dh(self->ctx, dh);
    DH_free(dh);
    BIO_free(bio);

    Py_INCREF(Py_None);
    return Py_None;
}

static char ssl_Context_set_cipher_list_doc[] = "\n\
Change the cipher list\n\
\n\
@param cipher_list: A cipher list, see ciphers(1)\n\
@return: None\n\
";
static PyObject *
ssl_Context_set_cipher_list(ssl_ContextObj *self, PyObject *args)
{
    char *cipher_list;

    if (!PyArg_ParseTuple(args, "s:set_cipher_list", &cipher_list))
        return NULL;

    if (!SSL_CTX_set_cipher_list(self->ctx, cipher_list))
    {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    else
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static char ssl_Context_set_client_ca_list_doc[] = "\n\
Set the list of preferred client certificate signers for this server context.\n\
\n\
This list of certificate authorities will be sent to the client when the\n\
server requests a client certificate.\n\
\n\
@param certificate_authorities: a sequence of X509Names.\n\
@return: None\n\
";

static PyObject *
ssl_Context_set_client_ca_list(ssl_ContextObj *self, PyObject *args)
{
    static PyTypeObject *X509NameType;
    PyObject *sequence, *tuple, *item;
    crypto_X509NameObj *name;
    X509_NAME *sslname;
    STACK_OF(X509_NAME) *CANames;
    Py_ssize_t length;
    int i;

    if (X509NameType == NULL) {
        X509NameType = import_crypto_type("X509Name", sizeof(crypto_X509NameObj));
        if (X509NameType == NULL) {
            return NULL;
        }
    }
    if (!PyArg_ParseTuple(args, "O:set_client_ca_list", &sequence)) {
        return NULL;
    }
    tuple = PySequence_Tuple(sequence);
    if (tuple == NULL) {
        return NULL;
    }
    length = PyTuple_Size(tuple);
    if (length >= INT_MAX) {
        PyErr_SetString(PyExc_ValueError, "client CA list is too long");
        Py_DECREF(tuple);
        return NULL;
    }
    CANames = sk_X509_NAME_new_null();
    if (CANames == NULL) {
        Py_DECREF(tuple);
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    for (i = 0; i < length; i++) {
        item = PyTuple_GetItem(tuple, i);
        if (item->ob_type != X509NameType) {
            PyErr_Format(PyExc_TypeError,
                         "client CAs must be X509Name objects, not %s objects",
                         item->ob_type->tp_name);
            sk_X509_NAME_free(CANames);
            Py_DECREF(tuple);
            return NULL;
        }
        name = (crypto_X509NameObj *)item;
        sslname = X509_NAME_dup(name->x509_name);
        if (sslname == NULL) {
            sk_X509_NAME_free(CANames);
            Py_DECREF(tuple);
            exception_from_error_queue(ssl_Error);
            return NULL;
        }
        if (!sk_X509_NAME_push(CANames, sslname)) {
            X509_NAME_free(sslname);
            sk_X509_NAME_free(CANames);
            Py_DECREF(tuple);
            exception_from_error_queue(ssl_Error);
            return NULL;
        }
    }
    Py_DECREF(tuple);
    SSL_CTX_set_client_CA_list(self->ctx, CANames);
    Py_INCREF(Py_None);
    return Py_None;
}

static char ssl_Context_add_client_ca_doc[] = "\n\
Add the CA certificate to the list of preferred signers for this context.\n\
\n\
The list of certificate authorities will be sent to the client when the\n\
server requests a client certificate.\n\
\n\
@param certificate_authority: certificate authority's X509 certificate.\n\
@return: None\n\
";

static PyObject *
ssl_Context_add_client_ca(ssl_ContextObj *self, PyObject *args)
{
    crypto_X509Obj *cert;

    cert = parse_certificate_argument("O!:add_client_ca", args);
    if (cert == NULL) {
        return NULL;
    }
    if (!SSL_CTX_add_client_CA(self->ctx, cert->x509)) {
        exception_from_error_queue(ssl_Error);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static char ssl_Context_set_timeout_doc[] = "\n\
Set session timeout\n\
\n\
@param timeout: The timeout in seconds\n\
@return: The previous session timeout\n\
";
static PyObject *
ssl_Context_set_timeout(ssl_ContextObj *self, PyObject *args)
{
    long t, ret;

    if (!PyArg_ParseTuple(args, "l:set_timeout", &t))
        return NULL;

    ret = SSL_CTX_set_timeout(self->ctx, t);
    return PyLong_FromLong(ret);
}

static char ssl_Context_get_timeout_doc[] = "\n\
Get the session timeout\n\
\n\
@return: The session timeout\n\
";
static PyObject *
ssl_Context_get_timeout(ssl_ContextObj *self, PyObject *args)
{
    long ret;

    if (!PyArg_ParseTuple(args, ":get_timeout"))
        return NULL;

    ret = SSL_CTX_get_timeout(self->ctx);
    return PyLong_FromLong(ret);
}

static char ssl_Context_set_info_callback_doc[] = "\n\
Set the info callback\n\
\n\
@param callback: The Python callback to use\n\
@return: None\n\
";
static PyObject *
ssl_Context_set_info_callback(ssl_ContextObj *self, PyObject *args)
{
    PyObject *callback;

    if (!PyArg_ParseTuple(args, "O:set_info_callback", &callback))
        return NULL;

    if (!PyCallable_Check(callback))
    {
        PyErr_SetString(PyExc_TypeError, "expected PyCallable");
        return NULL;
    }

    Py_DECREF(self->info_callback);
    Py_INCREF(callback);
    self->info_callback = callback;
    SSL_CTX_set_info_callback(self->ctx, global_info_callback);

    Py_INCREF(Py_None);
    return Py_None;
}

static char ssl_Context_get_app_data_doc[] = "\n\
Get the application data (supplied via set_app_data())\n\
\n\
@return: The application data\n\
";
static PyObject *
ssl_Context_get_app_data(ssl_ContextObj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":get_app_data"))
        return NULL;

    Py_INCREF(self->app_data);
    return self->app_data;
}

static char ssl_Context_set_app_data_doc[] = "\n\
Set the application data (will be returned from get_app_data())\n\
\n\
@param data: Any Python object\n\
@return: None\n\
";
static PyObject *
ssl_Context_set_app_data(ssl_ContextObj *self, PyObject *args)
{
    PyObject *data;

    if (!PyArg_ParseTuple(args, "O:set_app_data", &data))
        return NULL;

    Py_DECREF(self->app_data);
    Py_INCREF(data);
    self->app_data = data;

    Py_INCREF(Py_None);
    return Py_None;
}

static char ssl_Context_get_cert_store_doc[] = "\n\
Get the certificate store for the context\n\
\n\
@return: A X509Store object\n\
";
static PyObject *
ssl_Context_get_cert_store(ssl_ContextObj *self, PyObject *args)
{
    X509_STORE *store;

    if (!PyArg_ParseTuple(args, ":get_cert_store"))
        return NULL;

    if ((store = SSL_CTX_get_cert_store(self->ctx)) == NULL)
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
    else
    {
        return (PyObject *)new_x509store(store, 0);
    }
}

static char ssl_Context_set_options_doc[] = "\n\
Add options. Options set before are not cleared!\n\
\n\
@param options: The options to add.\n\
@return: The new option bitmask.\n\
";
static PyObject *
ssl_Context_set_options(ssl_ContextObj *self, PyObject *args)
{
    long options;

    if (!PyArg_ParseTuple(args, "l:set_options", &options))
        return NULL;

    return PyLong_FromLong(SSL_CTX_set_options(self->ctx, options));
}

static char ssl_Context_set_tlsext_servername_callback_doc[] = "\n\
Specify a callback function to be called when clients specify a server name.\n\
\n\
@param callback: The callback function.  It will be invoked with one\n\
    argument, the Connection instance.\n\
\n\
";
static PyObject *
ssl_Context_set_tlsext_servername_callback(ssl_ContextObj *self, PyObject *args) {
    PyObject *callback;
    PyObject *old;

    if (!PyArg_ParseTuple(args, "O:set_tlsext_servername_callback", &callback)) {
        return NULL;
    }

    Py_INCREF(callback);
    old = self->tlsext_servername_callback;
    self->tlsext_servername_callback = callback;
    Py_DECREF(old);

    SSL_CTX_set_tlsext_servername_callback(self->ctx, global_tlsext_servername_callback);
    SSL_CTX_set_tlsext_servername_arg(self->ctx, NULL);

    Py_INCREF(Py_None);
    return Py_None;
}


/*
 * Member methods in the Context object
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)ssl_Context_name, METH_VARARGS }
 * for convenience
 * ADD_ALIAS(name,real) creates an "alias" of the ssl_Context_real
 * function with the name 'name'
 */
#define ADD_METHOD(name) { #name, (PyCFunction)ssl_Context_##name, METH_VARARGS, ssl_Context_##name##_doc }
static PyMethodDef ssl_Context_methods[] = {
    ADD_METHOD(load_verify_locations),
    ADD_METHOD(set_passwd_cb),
    ADD_METHOD(set_default_verify_paths),
    ADD_METHOD(use_certificate_chain_file),
    ADD_METHOD(use_certificate_file),
    ADD_METHOD(use_certificate),
    ADD_METHOD(add_extra_chain_cert),
    ADD_METHOD(use_privatekey_file),
    ADD_METHOD(use_privatekey),
    ADD_METHOD(check_privatekey),
    ADD_METHOD(load_client_ca),
    ADD_METHOD(set_session_id),
    ADD_METHOD(set_verify),
    ADD_METHOD(set_verify_depth),
    ADD_METHOD(get_verify_mode),
    ADD_METHOD(get_verify_depth),
    ADD_METHOD(load_tmp_dh),
    ADD_METHOD(set_cipher_list),
    ADD_METHOD(set_client_ca_list),
    ADD_METHOD(add_client_ca),
    ADD_METHOD(set_timeout),
    ADD_METHOD(get_timeout),
    ADD_METHOD(set_info_callback),
    ADD_METHOD(get_app_data),
    ADD_METHOD(set_app_data),
    ADD_METHOD(get_cert_store),
    ADD_METHOD(set_options),
    ADD_METHOD(set_tlsext_servername_callback),
    { NULL, NULL }
};
#undef ADD_METHOD

/*
 * Despite the name which might suggest otherwise, this is not the tp_init for
 * the Context type.  It's just the common initialization code shared by the
 * two _{Nn}ew functions below.
 */
static ssl_ContextObj*
ssl_Context_init(ssl_ContextObj *self, int i_method) {
#if (OPENSSL_VERSION_NUMBER >> 28) == 0x01
    const
#endif
    SSL_METHOD *method;

    switch (i_method) {
        case ssl_SSLv2_METHOD:
#ifdef OPENSSL_NO_SSL2
            PyErr_SetString(PyExc_ValueError, "SSLv2_METHOD not supported by this version of OpenSSL");
            return NULL;
#else      
            method = SSLv2_method();
#endif
            break;
        case ssl_SSLv23_METHOD:
            method = SSLv23_method();
            break;
        case ssl_SSLv3_METHOD:
            method = SSLv3_method();
            break;
        case ssl_TLSv1_METHOD:
            method = TLSv1_method();
            break;
        default:
            PyErr_SetString(PyExc_ValueError, "No such protocol");
            return NULL;
    }

    self->ctx = SSL_CTX_new(method);
    Py_INCREF(Py_None);
    self->passphrase_callback = Py_None;
    Py_INCREF(Py_None);
    self->verify_callback = Py_None;
    Py_INCREF(Py_None);
    self->info_callback = Py_None;

    Py_INCREF(Py_None);
    self->tlsext_servername_callback = Py_None;

    Py_INCREF(Py_None);
    self->passphrase_userdata = Py_None;

    Py_INCREF(Py_None);
    self->app_data = Py_None;

    /* Some initialization that's required to operate smoothly in Python */
    SSL_CTX_set_app_data(self->ctx, self);
    SSL_CTX_set_mode(self->ctx, SSL_MODE_ENABLE_PARTIAL_WRITE |
                                SSL_MODE_ACCEPT_MOVING_WRITE_BUFFER |
                                SSL_MODE_AUTO_RETRY);

    self->tstate = NULL;

    return self;
}

/*
 * This one is exposed in the CObject API.  I want to deprecate it.
 */
ssl_ContextObj*
ssl_Context_New(int i_method) {
    ssl_ContextObj *self;

    self = PyObject_GC_New(ssl_ContextObj, &ssl_Context_Type);
    if (self == NULL) {
       return (ssl_ContextObj *)PyErr_NoMemory();
    }
    self = ssl_Context_init(self, i_method);
    PyObject_GC_Track((PyObject *)self);
    return self;
}


/*
 * This one is the tp_new of the Context type.  It's great.
 */
static PyObject*
ssl_Context_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    int i_method;
    ssl_ContextObj *self;
    static char *kwlist[] = {"method", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "i:Context", kwlist, &i_method)) {
        return NULL;
    }

    self = (ssl_ContextObj *)subtype->tp_alloc(subtype, 1);
    if (self == NULL) {
        return NULL;
    }

    return (PyObject *)ssl_Context_init(self, i_method);
}

/*
 * Call the visitproc on all contained objects.
 *
 * Arguments: self - The Context object
 *            visit - Function to call
 *            arg - Extra argument to visit
 * Returns:   0 if all goes well, otherwise the return code from the first
 *            call that gave non-zero result.
 */
static int
ssl_Context_traverse(ssl_ContextObj *self, visitproc visit, void *arg)
{
    int ret = 0;

    if (ret == 0 && self->passphrase_callback != NULL)
        ret = visit((PyObject *)self->passphrase_callback, arg);
    if (ret == 0 && self->passphrase_userdata != NULL)
        ret = visit((PyObject *)self->passphrase_userdata, arg);
    if (ret == 0 && self->verify_callback != NULL)
        ret = visit((PyObject *)self->verify_callback, arg);
    if (ret == 0 && self->info_callback != NULL)
        ret = visit((PyObject *)self->info_callback, arg);
    if (ret == 0 && self->app_data != NULL)
        ret = visit(self->app_data, arg);
    return ret;
}

/*
 * Decref all contained objects and zero the pointers.
 *
 * Arguments: self - The Context object
 * Returns:   Always 0.
 */
static int
ssl_Context_clear(ssl_ContextObj *self)
{
    Py_XDECREF(self->passphrase_callback);
    self->passphrase_callback = NULL;
    Py_XDECREF(self->passphrase_userdata);
    self->passphrase_userdata = NULL;
    Py_XDECREF(self->verify_callback);
    self->verify_callback = NULL;
    Py_XDECREF(self->info_callback);
    self->info_callback = NULL;
    Py_XDECREF(self->app_data);
    self->app_data = NULL;
    return 0;
}

/*
 * Deallocate the memory used by the Context object
 *
 * Arguments: self - The Context object
 * Returns:   None
 */
static void
ssl_Context_dealloc(ssl_ContextObj *self)
{
    PyObject_GC_UnTrack((PyObject *)self);
    SSL_CTX_free(self->ctx);
    ssl_Context_clear(self);
    PyObject_GC_Del(self);
}


PyTypeObject ssl_Context_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "OpenSSL.SSL.Context",
    sizeof(ssl_ContextObj),
    0,
    (destructor)ssl_Context_dealloc, /* tp_dealloc */
    NULL, /* print */
    NULL, /* tp_getattr */
    NULL, /* setattr */
    NULL, /* compare */
    NULL, /* repr */
    NULL, /* as_number */
    NULL, /* as_sequence */
    NULL, /* as_mapping */
    NULL, /* hash */
    NULL, /* call */
    NULL, /* str */
    NULL, /* getattro */
    NULL, /* setattro */
    NULL, /* as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE, /* tp_flags */
    ssl_Context_doc, /* tp_doc */
    (traverseproc)ssl_Context_traverse, /* tp_traverse */
    (inquiry)ssl_Context_clear, /* tp_clear */
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    ssl_Context_methods, /* tp_methods */
    NULL, /* tp_members */
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    0, /* tp_dictoffset */
    NULL, /* tp_init */
    NULL, /* tp_alloc */
    ssl_Context_new, /* tp_new */
};


/*
 * Initialize the Context part of the SSL sub module
 *
 * Arguments: dict - The OpenSSL.SSL module
 * Returns:   1 for success, 0 otherwise
 */
int
init_ssl_context(PyObject *module) {

    if (PyType_Ready(&ssl_Context_Type) < 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference.
     */
    Py_INCREF((PyObject *)&ssl_Context_Type);
    if (PyModule_AddObject(module, "Context", (PyObject *)&ssl_Context_Type) < 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference.
     */
    Py_INCREF((PyObject *)&ssl_Context_Type);
    if (PyModule_AddObject(module, "ContextType", (PyObject *)&ssl_Context_Type) < 0) {
        return 0;
    }

    return 1;
}

