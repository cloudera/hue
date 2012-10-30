/*
 * crypto.c
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 * Copyright (C) Keyphrene 2004, All rights reserved
 * Copyright (C) Jean-Paul Calderone 2008-2009, All rights reserved
 *
 * Main file of crypto sub module.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"
#include "pkcs12.h"

static char crypto_doc[] = "\n\
Main file of crypto sub module.\n\
See the file RATIONALE for a short explanation of why this module was written.\n\
";

void **ssl_API;

PyObject *crypto_Error;

int crypto_byte_converter(PyObject *input, void* output) {
    char **message = output;
    if (input == Py_None) {
        *message = NULL;
    } else if (PyBytes_CheckExact(input)) {
        *message = PyBytes_AsString(input);
    } else {
        return 0;
    }
    return 1;
}

static int
global_passphrase_callback(char *buf, int len, int rwflag, void *cb_arg)
{
    PyObject *func, *argv, *ret;
    int nchars;

    func = (PyObject *)cb_arg;
    argv = Py_BuildValue("(i)", rwflag);
    ret = PyEval_CallObject(func, argv);
    Py_DECREF(argv);
    if (ret == NULL)
        return 0;
    if (!PyBytes_Check(ret))
    {
        PyErr_SetString(PyExc_ValueError, "String expected");
        return 0;
    }
    nchars = PyBytes_Size(ret);
    if (nchars > len)
        nchars = len;
    strncpy(buf, PyBytes_AsString(ret), nchars);
    return nchars;
}

static char crypto_load_privatekey_doc[] = "\n\
Load a private key from a buffer\n\
\n\
@param type: The file type (one of FILETYPE_PEM, FILETYPE_ASN1)\n\
@param buffer: The buffer the key is stored in\n\
@param passphrase: (optional) if encrypted PEM format, this can be\n\
                   either the passphrase to use, or a callback for\n\
                   providing the passphrase.\n\
\n\
@return: The PKey object\n\
";

static PyObject *
crypto_load_privatekey(PyObject *spam, PyObject *args)
{
    crypto_PKeyObj *crypto_PKey_New(EVP_PKEY *, int);
    int type, len;
    char *buffer;
    PyObject *pw = NULL;
    pem_password_cb *cb = NULL;
    void *cb_arg = NULL;
    BIO *bio;
    EVP_PKEY *pkey;

    if (!PyArg_ParseTuple(args, "is#|O:load_privatekey", &type, &buffer, &len, &pw))
        return NULL;

    if (pw != NULL)
    {
        if (PyBytes_Check(pw))
        {
            cb = NULL;
            cb_arg = PyBytes_AsString(pw);
        }
        else if (PyCallable_Check(pw))
        {
            cb = global_passphrase_callback;
            cb_arg = pw;
        }
        else
        {
            PyErr_SetString(PyExc_TypeError, "Last argument must be string or callable");
            return NULL;
        }
    }

    bio = BIO_new_mem_buf(buffer, len);
    switch (type)
    {
        case X509_FILETYPE_PEM:
            pkey = PEM_read_bio_PrivateKey(bio, NULL, cb, cb_arg);
            break;

        case X509_FILETYPE_ASN1:
            pkey = d2i_PrivateKey_bio(bio, NULL);
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "type argument must be FILETYPE_PEM or FILETYPE_ASN1");
            BIO_free(bio);
            return NULL;
    }
    BIO_free(bio);

    if (pkey == NULL)
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    return (PyObject *)crypto_PKey_New(pkey, 1);
}

static char crypto_dump_privatekey_doc[] = "\n\
Dump a private key to a buffer\n\
\n\
@param type: The file type (one of FILETYPE_PEM, FILETYPE_ASN1)\n\
@param pkey: The PKey to dump\n\
@param cipher: (optional) if encrypted PEM format, the cipher to\n\
               use\n\
@param passphrase - (optional) if encrypted PEM format, this can be either\n\
                    the passphrase to use, or a callback for providing the\n\
                    passphrase.\n\
@return: The buffer with the dumped key in\n\
@rtype: C{str}\n\
";

static PyObject *
crypto_dump_privatekey(PyObject *spam, PyObject *args)
{
    int type, ret, buf_len;
    char *temp;
    PyObject *buffer;
    char *cipher_name = NULL;
    const EVP_CIPHER *cipher = NULL;
    PyObject *pw = NULL;
    pem_password_cb *cb = NULL;
    void *cb_arg = NULL;
    BIO *bio;
    RSA *rsa;
    crypto_PKeyObj *pkey;

    if (!PyArg_ParseTuple(args, "iO!|sO:dump_privatekey", &type,
			  &crypto_PKey_Type, &pkey, &cipher_name, &pw))
        return NULL;

    if (cipher_name != NULL && pw == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Illegal number of arguments");
        return NULL;
    }
    if (cipher_name != NULL)
    {
        cipher = EVP_get_cipherbyname(cipher_name);
        if (cipher == NULL)
        {
            PyErr_SetString(PyExc_ValueError, "Invalid cipher name");
            return NULL;
        }
        if (PyBytes_Check(pw))
        {
            cb = NULL;
            cb_arg = PyBytes_AsString(pw);
        }
        else if (PyCallable_Check(pw))
        {
            cb = global_passphrase_callback;
            cb_arg = pw;
        }
        else
        {
            PyErr_SetString(PyExc_TypeError, "Last argument must be string or callable");
            return NULL;
        }
    }

    bio = BIO_new(BIO_s_mem());
    switch (type)
    {
        case X509_FILETYPE_PEM:
            ret = PEM_write_bio_PrivateKey(bio, pkey->pkey, cipher, NULL, 0, cb, cb_arg);
            if (PyErr_Occurred())
            {
                BIO_free(bio);
                return NULL;
            }
            break;

        case X509_FILETYPE_ASN1:
            ret = i2d_PrivateKey_bio(bio, pkey->pkey);
            break;

        case X509_FILETYPE_TEXT:
            rsa = EVP_PKEY_get1_RSA(pkey->pkey);
            ret = RSA_print(bio, rsa, 0);
            RSA_free(rsa); 
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "type argument must be FILETYPE_PEM, FILETYPE_ASN1, or FILETYPE_TEXT");
            BIO_free(bio);
            return NULL;
    }

    if (ret == 0)
    {
        BIO_free(bio);
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    buf_len = BIO_get_mem_data(bio, &temp);
    buffer = PyBytes_FromStringAndSize(temp, buf_len);
    BIO_free(bio);

    return buffer;
}

static char crypto_load_certificate_doc[] = "\n\
Load a certificate from a buffer\n\
\n\
@param type: The file type (one of FILETYPE_PEM, FILETYPE_ASN1)\n\
             buffer - The buffer the certificate is stored in\n\
@return: The X509 object\n\
";

static PyObject *
crypto_load_certificate(PyObject *spam, PyObject *args)
{
    crypto_X509Obj *crypto_X509_New(X509 *, int);
    int type, len;
    char *buffer;
    BIO *bio;
    X509 *cert;

    if (!PyArg_ParseTuple(args, "is#:load_certificate", &type, &buffer, &len))
        return NULL;

    bio = BIO_new_mem_buf(buffer, len);
    switch (type)
    {
        case X509_FILETYPE_PEM:
            cert = PEM_read_bio_X509(bio, NULL, NULL, NULL);
            break;

        case X509_FILETYPE_ASN1:
            cert = d2i_X509_bio(bio, NULL);
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "type argument must be FILETYPE_PEM or FILETYPE_ASN1");
            BIO_free(bio);
            return NULL;
    }
    BIO_free(bio);

    if (cert == NULL)
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    return (PyObject *)crypto_X509_New(cert, 1);
}

static char crypto_dump_certificate_doc[] = "\n\
Dump a certificate to a buffer\n\
\n\
@param type: The file type (one of FILETYPE_PEM, FILETYPE_ASN1)\n\
@param cert: The certificate to dump\n\
@return: The buffer with the dumped certificate in\n\
";

static PyObject *
crypto_dump_certificate(PyObject *spam, PyObject *args)
{
    int type, ret, buf_len;
    char *temp;
    PyObject *buffer;
    BIO *bio;
    crypto_X509Obj *cert;

    if (!PyArg_ParseTuple(args, "iO!:dump_certificate", &type,
			  &crypto_X509_Type, &cert))
        return NULL;

    bio = BIO_new(BIO_s_mem());
    switch (type)
    {
        case X509_FILETYPE_PEM:
            ret = PEM_write_bio_X509(bio, cert->x509);
            break;

        case X509_FILETYPE_ASN1:
            ret = i2d_X509_bio(bio, cert->x509);
            break;

        case X509_FILETYPE_TEXT:
            ret = X509_print_ex(bio, cert->x509, 0, 0);
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "type argument must be FILETYPE_PEM, FILETYPE_ASN1, or FILETYPE_TEXT");
            BIO_free(bio);
            return NULL;
    }

    if (ret == 0)
    {
        BIO_free(bio);
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    buf_len = BIO_get_mem_data(bio, &temp);
    buffer = PyBytes_FromStringAndSize(temp, buf_len);
    BIO_free(bio);

    return buffer;
}

static char crypto_load_certificate_request_doc[] = "\n\
Load a certificate request from a buffer\n\
\n\
@param type: The file type (one of FILETYPE_PEM, FILETYPE_ASN1)\n\
             buffer - The buffer the certificate request is stored in\n\
@return: The X509Req object\n\
";

static PyObject *
crypto_load_certificate_request(PyObject *spam, PyObject *args)
{
    crypto_X509ReqObj *crypto_X509Req_New(X509_REQ *, int);
    int type, len;
    char *buffer;
    BIO *bio;
    X509_REQ *req;

    if (!PyArg_ParseTuple(args, "is#:load_certificate_request", &type, &buffer, &len))
        return NULL;

    bio = BIO_new_mem_buf(buffer, len);
    switch (type)
    {
        case X509_FILETYPE_PEM:
            req = PEM_read_bio_X509_REQ(bio, NULL, NULL, NULL);
            break;

        case X509_FILETYPE_ASN1:
            req = d2i_X509_REQ_bio(bio, NULL);
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "type argument must be FILETYPE_PEM or FILETYPE_ASN1");
            BIO_free(bio);
            return NULL;
    }
    BIO_free(bio);

    if (req == NULL)
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    return (PyObject *)crypto_X509Req_New(req, 1);
}

static char crypto_dump_certificate_request_doc[] = "\n\
Dump a certificate request to a buffer\n\
\n\
@param type: The file type (one of FILETYPE_PEM, FILETYPE_ASN1)\n\
             req  - The certificate request to dump\n\
@return: The buffer with the dumped certificate request in\n\
";

static PyObject *
crypto_dump_certificate_request(PyObject *spam, PyObject *args)
{
    int type, ret, buf_len;
    char *temp;
    PyObject *buffer;
    BIO *bio;
    crypto_X509ReqObj *req;

    if (!PyArg_ParseTuple(args, "iO!:dump_certificate_request", &type,
			  &crypto_X509Req_Type, &req))
        return NULL;

    bio = BIO_new(BIO_s_mem());
    switch (type)
    {
        case X509_FILETYPE_PEM:
            ret = PEM_write_bio_X509_REQ(bio, req->x509_req);
            break;

        case X509_FILETYPE_ASN1:
            ret = i2d_X509_REQ_bio(bio, req->x509_req);
            break;

        case X509_FILETYPE_TEXT:
            ret = X509_REQ_print_ex(bio, req->x509_req, 0, 0);
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "type argument must be FILETYPE_PEM, FILETYPE_ASN1, or FILETYPE_TEXT");
            BIO_free(bio);
            return NULL;
    }

    if (ret == 0)
    {
        BIO_free(bio);
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    buf_len = BIO_get_mem_data(bio, &temp);
    buffer = PyBytes_FromStringAndSize(temp, buf_len);
    BIO_free(bio);

    return buffer;
}

static char crypto_load_crl_doc[] = "\n\
Load a certificate revocation list from a buffer\n\
\n\
@param type: The file type (one of FILETYPE_PEM, FILETYPE_ASN1)\n\
@param buffer: The buffer the CRL is stored in\n\
\n\
@return: The PKey object\n\
";

static PyObject *
crypto_load_crl(PyObject *spam, PyObject *args) {
    int type, len;
    char *buffer;
    BIO *bio;
    X509_CRL *crl;

    if (!PyArg_ParseTuple(args, "is#:load_crl", &type, &buffer, &len)) {
        return NULL;
    }

    bio = BIO_new_mem_buf(buffer, len);
    switch (type) {
        case X509_FILETYPE_PEM:
            crl = PEM_read_bio_X509_CRL(bio, NULL, NULL, NULL);
            break;

        case X509_FILETYPE_ASN1:
            crl = d2i_X509_CRL_bio(bio, NULL);
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "type argument must be FILETYPE_PEM or FILETYPE_ASN1");
            BIO_free(bio);
            return NULL;
    }
    BIO_free(bio);

    if (crl == NULL) {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    return (PyObject *)crypto_CRL_New(crl);
}

static char crypto_load_pkcs7_data_doc[] = "\n\
Load pkcs7 data from a buffer\n\
\n\
@param type: The file type (one of FILETYPE_PEM or FILETYPE_ASN1)\n\
             buffer - The buffer with the pkcs7 data.\n\
@return: The PKCS7 object\n\
";

static PyObject *
crypto_load_pkcs7_data(PyObject *spam, PyObject *args)
{
    int type, len;
    char *buffer;
    BIO *bio;
    PKCS7 *pkcs7 = NULL;

    if (!PyArg_ParseTuple(args, "is#:load_pkcs7_data", &type, &buffer, &len))
        return NULL;

    /* 
     * Try to read the pkcs7 data from the bio 
     */
    bio = BIO_new_mem_buf(buffer, len);
    switch (type)
    {
        case X509_FILETYPE_PEM:
            pkcs7 = PEM_read_bio_PKCS7(bio, NULL, NULL, NULL);
            break;

        case X509_FILETYPE_ASN1:
            pkcs7 = d2i_PKCS7_bio(bio, NULL);
            break;

        default:
            PyErr_SetString(PyExc_ValueError,
                    "type argument must be FILETYPE_PEM or FILETYPE_ASN1");
            return NULL;
    }
    BIO_free(bio);

    /*
     * Check if we got a PKCS7 structure
     */
    if (pkcs7 == NULL)
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    return (PyObject *)crypto_PKCS7_New(pkcs7, 1);
}

static char crypto_load_pkcs12_doc[] = "\n\
Load a PKCS12 object from a buffer\n\
\n\
@param buffer: The buffer the certificate is stored in\n\
               passphrase (Optional) - The password to decrypt the PKCS12 lump\n\
@returns: The PKCS12 object\n\
";

static PyObject *
crypto_load_pkcs12(PyObject *spam, PyObject *args)
{
    int len;
    char *buffer, *passphrase = NULL;
    BIO *bio;
    PKCS12 *p12;

    if (!PyArg_ParseTuple(args, "s#|s:load_pkcs12", &buffer, &len, &passphrase))
        return NULL;

    bio = BIO_new_mem_buf(buffer, len);
    if ((p12 = d2i_PKCS12_bio(bio, NULL)) == NULL)
    {
      BIO_free(bio);
      exception_from_error_queue(crypto_Error);
      return NULL;
    }
    BIO_free(bio);

    return (PyObject *)crypto_PKCS12_New(p12, passphrase);
}


static char crypto_X509_verify_cert_error_string_doc[] = "\n\
Get X509 verify certificate error string.\n\
\n\
@param errnum: The error number.\n\
@return: Error string as a Python string\n\
";

static PyObject *
crypto_X509_verify_cert_error_string(PyObject *spam, PyObject *args)
{
    int errnum;
    const char *str;

    if (!PyArg_ParseTuple(args, "i", &errnum))
        return NULL;

    str = X509_verify_cert_error_string(errnum);
    return PyText_FromString(str);
}

static char crypto_exception_from_error_queue_doc[] = "\n\
Raise an exception from the current OpenSSL error queue.\n\
";

static PyObject *
crypto_exception_from_error_queue(PyObject *spam, PyObject *eggs) {
    exception_from_error_queue(crypto_Error);
    return NULL;
}

static char crypto_sign_doc[] = "\n\
Sign data with a digest\n\
\n\
@param pkey: Pkey to sign with\n\
@param data: data to be signed\n\
@param digest: message digest to use\n\
@return: signature\n\
";

static PyObject *
crypto_sign(PyObject *spam, PyObject *args) {
    PyObject *buffer;
    crypto_PKeyObj *pkey;
    char *data = NULL;
    char *digest_name;
    int err;
    unsigned int sig_len;
    const EVP_MD *digest;
    EVP_MD_CTX md_ctx;
    unsigned char sig_buf[512];

    if (!PyArg_ParseTuple(
            args, "O!" BYTESTRING_FMT "s:sign", &crypto_PKey_Type,
            &pkey, &data, &digest_name)) {
        return NULL;
    }

    if ((digest = EVP_get_digestbyname(digest_name)) == NULL) {
        PyErr_SetString(PyExc_ValueError, "No such digest method");
        return NULL;
    }

    EVP_SignInit(&md_ctx, digest);
    EVP_SignUpdate(&md_ctx, data, strlen(data));
    sig_len = sizeof(sig_buf);
    err = EVP_SignFinal(&md_ctx, sig_buf, &sig_len, pkey->pkey);

    if (err != 1) {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    buffer = PyBytes_FromStringAndSize((char*)sig_buf, sig_len);
    return buffer;
}

static char crypto_verify_doc[] = "\n\
Verify a signature\n\
\n\
@param cert: signing certificate (X509 object)\n\
@param signature: signature returned by sign function\n\
@param data: data to be verified\n\
@param digest: message digest to use\n\
@return: None if the signature is correct, raise exception otherwise\n\
";

static PyObject *
crypto_verify(PyObject *spam, PyObject *args) {
    crypto_X509Obj *cert;
    unsigned char *signature;
    int sig_len;
    char *data, *digest_name;
    int err;
    const EVP_MD *digest;
    EVP_MD_CTX md_ctx;
    EVP_PKEY *pkey;

#ifdef PY3
    if (!PyArg_ParseTuple(args, "O!" BYTESTRING_FMT "#" BYTESTRING_FMT "s:verify", &crypto_X509_Type, &cert, &signature, &sig_len, &data, &digest_name)) {
#else
    if (!PyArg_ParseTuple(args, "O!t#ss:verify", &crypto_X509_Type, &cert, &signature, &sig_len, &data, &digest_name)) {
#endif
        return NULL;
    }

    if ((digest = EVP_get_digestbyname(digest_name)) == NULL){
        PyErr_SetString(PyExc_ValueError, "No such digest method");
        return NULL;
    }

    pkey = X509_get_pubkey(cert->x509);
    if (pkey == NULL) {
        PyErr_SetString(PyExc_ValueError, "No public key");
        return NULL;
    }

    EVP_VerifyInit(&md_ctx, digest);
    EVP_VerifyUpdate(&md_ctx, data, strlen((char*)data));
    err = EVP_VerifyFinal(&md_ctx, signature, sig_len, pkey);
    EVP_PKEY_free(pkey);

    if (err != 1) {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/* Methods in the OpenSSL.crypto module (i.e. none) */
static PyMethodDef crypto_methods[] = {
    /* Module functions */
    { "load_privatekey",  (PyCFunction)crypto_load_privatekey,  METH_VARARGS, crypto_load_privatekey_doc },
    { "dump_privatekey",  (PyCFunction)crypto_dump_privatekey,  METH_VARARGS, crypto_dump_privatekey_doc },
    { "load_certificate", (PyCFunction)crypto_load_certificate, METH_VARARGS, crypto_load_certificate_doc },
    { "dump_certificate", (PyCFunction)crypto_dump_certificate, METH_VARARGS, crypto_dump_certificate_doc },
    { "load_certificate_request", (PyCFunction)crypto_load_certificate_request, METH_VARARGS, crypto_load_certificate_request_doc },
    { "dump_certificate_request", (PyCFunction)crypto_dump_certificate_request, METH_VARARGS, crypto_dump_certificate_request_doc },
    { "load_crl",         (PyCFunction)crypto_load_crl,         METH_VARARGS, crypto_load_crl_doc },
    { "load_pkcs7_data", (PyCFunction)crypto_load_pkcs7_data, METH_VARARGS, crypto_load_pkcs7_data_doc },
    { "load_pkcs12", (PyCFunction)crypto_load_pkcs12, METH_VARARGS, crypto_load_pkcs12_doc },
    { "sign", (PyCFunction)crypto_sign, METH_VARARGS, crypto_sign_doc },
    { "verify", (PyCFunction)crypto_verify, METH_VARARGS, crypto_verify_doc },
    { "X509_verify_cert_error_string", (PyCFunction)crypto_X509_verify_cert_error_string, METH_VARARGS, crypto_X509_verify_cert_error_string_doc },
    { "_exception_from_error_queue", (PyCFunction)crypto_exception_from_error_queue, METH_NOARGS, crypto_exception_from_error_queue_doc },
    { NULL, NULL }
};


#ifdef WITH_THREAD

#include <pythread.h>

/**
 * This array will store all of the mutexes available to OpenSSL.
 */
static PyThread_type_lock *mutex_buf = NULL;


/**
 * Callback function supplied to OpenSSL to acquire or release a lock.
 *
 */
static void locking_function(int mode, int n, const char * file, int line) {
    if (mode & CRYPTO_LOCK) {
        PyThread_acquire_lock(mutex_buf[n], WAIT_LOCK);
    } else {
        PyThread_release_lock(mutex_buf[n]);
    }
}


/**
 * Initialize OpenSSL for use from multiple threads.
 *
 * Returns: 0 if initialization fails, 1 otherwise.
 */
static int init_openssl_threads(void) {
    int i;

    mutex_buf = (PyThread_type_lock *)malloc(
        CRYPTO_num_locks() * sizeof(PyThread_type_lock));
    if (!mutex_buf) {
        return 0;
    }
    for (i = 0; i < CRYPTO_num_locks(); ++i) {
        mutex_buf[i] = PyThread_allocate_lock();
    }
    CRYPTO_set_id_callback((unsigned long (*)(void))PyThread_get_thread_ident);
    CRYPTO_set_locking_callback(locking_function);
    return 1;
}

/* /\** */
/*  * Clean up after OpenSSL thread initialization. */
/*  *\/ */
/* static int deinit_openssl_threads() { */
/*     int i; */

/*     if (!mutex_buf) { */
/*         return 0; */
/*     } */
/*     CRYPTO_set_id_callback(NULL); */
/*     CRYPTO_set_locking_callback(NULL); */
/*     for (i = 0; i < CRYPTO_num_locks(); i++) { */
/*         PyThread_free_lock(mutex_buf[i]); */
/*     } */
/*     free(mutex_buf); */
/*     mutex_buf = NULL; */
/*     return 1; */
/* } */

#endif

#ifdef PY3
static struct PyModuleDef cryptomodule = {
    PyModuleDef_HEAD_INIT,
    "crypto",
    crypto_doc,
    -1,
    crypto_methods
};
#endif

/*
 * Initialize crypto sub module
 *
 * Arguments: None
 * Returns:   None
 */
PyOpenSSL_MODINIT(crypto) {
#ifndef PY3
    static void *crypto_API[crypto_API_pointers];
    PyObject *c_api_object;
#endif
    PyObject *module;

    ERR_load_crypto_strings();
    OpenSSL_add_all_algorithms();

#ifdef PY3
    module = PyModule_Create(&cryptomodule);
#else
    module = Py_InitModule3("crypto", crypto_methods, crypto_doc);
#endif

    if (module == NULL) {
        PyOpenSSL_MODRETURN(NULL);
    }

#ifndef PY3
    /* Initialize the C API pointer array */
    crypto_API[crypto_X509_New_NUM]      = (void *)crypto_X509_New;
    crypto_API[crypto_X509Name_New_NUM]  = (void *)crypto_X509Name_New;
    crypto_API[crypto_X509Req_New_NUM]   = (void *)crypto_X509Req_New;
    crypto_API[crypto_X509Store_New_NUM] = (void *)crypto_X509Store_New;
    crypto_API[crypto_PKey_New_NUM]      = (void *)crypto_PKey_New;
    crypto_API[crypto_X509Extension_New_NUM] = (void *)crypto_X509Extension_New;
    crypto_API[crypto_PKCS7_New_NUM]     = (void *)crypto_PKCS7_New;
    crypto_API[crypto_NetscapeSPKI_New_NUM]     = (void *)crypto_NetscapeSPKI_New;
    c_api_object = PyCObject_FromVoidPtr((void *)crypto_API, NULL);
    if (c_api_object != NULL)
        PyModule_AddObject(module, "_C_API", c_api_object);
#endif

    crypto_Error = PyErr_NewException("OpenSSL.crypto.Error", NULL, NULL);
    if (crypto_Error == NULL)
        goto error;
    if (PyModule_AddObject(module, "Error", crypto_Error) != 0)
        goto error;

    PyModule_AddIntConstant(module, "FILETYPE_PEM",  X509_FILETYPE_PEM);
    PyModule_AddIntConstant(module, "FILETYPE_ASN1", X509_FILETYPE_ASN1);
    PyModule_AddIntConstant(module, "FILETYPE_TEXT", X509_FILETYPE_TEXT);

    PyModule_AddIntConstant(module, "TYPE_RSA", crypto_TYPE_RSA);
    PyModule_AddIntConstant(module, "TYPE_DSA", crypto_TYPE_DSA);

#ifdef WITH_THREAD
    if (!init_openssl_threads())
        goto error;
#endif
    if (!init_crypto_x509(module))
        goto error;
    if (!init_crypto_x509name(module))
        goto error;
    if (!init_crypto_x509store(module))
        goto error;
    if (!init_crypto_x509req(module))
        goto error;
    if (!init_crypto_pkey(module))
        goto error;
    if (!init_crypto_x509extension(module))
        goto error;
    if (!init_crypto_pkcs7(module))
        goto error;
    if (!init_crypto_pkcs12(module))
        goto error;
    if (!init_crypto_netscape_spki(module))
        goto error;
    if (!init_crypto_crl(module))
        goto error;
    if (!init_crypto_revoked(module))
        goto error;

    PyOpenSSL_MODRETURN(module);

error:
    PyOpenSSL_MODRETURN(NULL);
    ;
}
