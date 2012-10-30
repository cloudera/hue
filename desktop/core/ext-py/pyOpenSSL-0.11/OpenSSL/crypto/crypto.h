/*
 * crypto.h
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * Exports from crypto.c.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 *
 * @(#) $Id: crypto.h,v 1.14 2004/08/09 13:41:25 martin Exp $
 */
#ifndef PyOpenSSL_CRYPTO_H_
#define PyOpenSSL_CRYPTO_H_

#include <Python.h>
#include "x509.h"
#include "x509name.h"
#include "netscape_spki.h"
#include "x509store.h"
#include "x509req.h"
#include "pkey.h"
#include "x509ext.h"
#include "pkcs7.h"
#include "pkcs12.h"
#include "crl.h"
#include "revoked.h"
#include "../util.h"

extern PyObject *crypto_Error;

#define crypto_X509_New_NUM             0
#define crypto_X509_New_RETURN          crypto_X509Obj *
#define crypto_X509_New_PROTO           (X509 *, int)

#define crypto_X509Req_New_NUM          1
#define crypto_X509Req_New_RETURN       crypto_X509ReqObj *
#define crypto_X509Req_New_PROTO        (X509_REQ *, int)

#define crypto_X509Store_New_NUM        2
#define crypto_X509Store_New_RETURN     crypto_X509StoreObj *
#define crypto_X509Store_New_PROTO      (X509_STORE *, int)

#define crypto_PKey_New_NUM             3
#define crypto_PKey_New_RETURN          crypto_PKeyObj *
#define crypto_PKey_New_PROTO           (EVP_PKEY *, int)

#define crypto_X509Name_New_NUM         4
#define crypto_X509Name_New_RETURN      crypto_X509NameObj *
#define crypto_X509Name_New_PROTO       (X509_NAME *, int)

#define crypto_X509Extension_New_NUM    5
#define crypto_X509Extension_New_RETURN crypto_X509ExtensionObj *
#define crypto_X509Extension_New_PROTO  (char *, int, char *, crypto_X509Obj *, crypto_X509Obj *)

#define crypto_PKCS7_New_NUM            6
#define crypto_PKCS7_New_RETURN         crypto_PKCS7Obj *
#define crypto_PKCS7_New_PROTO          (PKCS7 *, int)

#define crypto_NetscapeSPKI_New_NUM         7
#define crypto_NetscapeSPKI_New_RETURN      crypto_NetscapeSPKIObj *
#define crypto_NetscapeSPKI_New_PROTO       (NETSCAPE_SPKI *, int)

#define crypto_API_pointers             8

#if defined(PY3) || defined(crypto_MODULE)

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern EXPORT crypto_X509_New_RETURN      crypto_X509_New      crypto_X509_New_PROTO;
extern EXPORT crypto_X509Name_New_RETURN  crypto_X509Name_New  crypto_X509Name_New_PROTO;
extern crypto_X509Req_New_RETURN   crypto_X509Req_New   crypto_X509Req_New_PROTO;
extern EXPORT crypto_X509Store_New_RETURN crypto_X509Store_New crypto_X509Store_New_PROTO;
extern crypto_PKey_New_RETURN      crypto_PKey_New      crypto_PKey_New_PROTO;
extern crypto_X509Extension_New_RETURN crypto_X509Extension_New crypto_X509Extension_New_PROTO;
extern crypto_PKCS7_New_RETURN     crypto_PKCS7_New     crypto_PKCS7_New_PROTO;
extern crypto_NetscapeSPKI_New_RETURN  crypto_NetscapeSPKI_New  crypto_NetscapeSPKI_New_PROTO;

int crypto_byte_converter(PyObject *input, void *output);

#else /* crypto_MODULE */

extern void **crypto_API;

#define crypto_X509_New         \
 (*(crypto_X509_New_RETURN (*)crypto_X509_New_PROTO) crypto_API[crypto_X509_New_NUM])
#define crypto_X509Name_New     \
 (*(crypto_X509Name_New_RETURN (*)crypto_X509Name_New_PROTO) crypto_API[crypto_X509Name_New_NUM])
#define crypto_X509Req_New      \
 (*(crypto_X509Req_New_RETURN (*)crypto_X509Req_New_PROTO) crypto_API[crypto_X509Req_New_NUM])
#define crypto_X509Store_New    \
 (*(crypto_X509Store_New_RETURN (*)crypto_X509Store_New_PROTO) crypto_API[crypto_X509Store_New_NUM])
#define crypto_PKey_New         \
 (*(crypto_PKey_New_RETURN (*)crypto_PKey_New_PROTO) crypto_API[crypto_PKey_New_NUM])
#define crypto_X509Extension_New\
 (*(crypto_X509Extension_New_RETURN (*)crypto_X509Extension_New_PROTO) crypto_API[crypto_X509Extension_New_NUM])
#define crypto_PKCS7_New        \
 (*(crypto_PKCS7_New_RETURN (*)crypto_PKCS7_New_PROTO) crypto_API[crypto_PKCS7_New_NUM])
#define crypto_NetscapeSPKI_New     \
 (*(crypto_NetscapeSPKI_New_RETURN (*)crypto_NetscapeSPKI_New_PROTO) crypto_API[crypto_NetscapeSPKI_New_NUM])

#define import_crypto() \
{ \
  PyObject *crypto_module = PyImport_ImportModule("OpenSSL.crypto"); \
  if (crypto_module != NULL) { \
    PyObject *crypto_dict, *crypto_api_object; \
    crypto_dict = PyModule_GetDict(crypto_module); \
    crypto_api_object = PyDict_GetItemString(crypto_dict, "_C_API"); \
    if (PyCObject_Check(crypto_api_object)) { \
      crypto_API = (void **)PyCObject_AsVoidPtr(crypto_api_object); \
    } \
  } \
}

#endif /* crypto_MODULE */

/* Define a new type for emitting text.  Hopefully these don't collide with
 * future official OpenSSL constants, but the switch statement of
 * dump_certificate() will alert us if it matters.
 */
#ifndef X509_FILETYPE_TEXT 
#define X509_FILETYPE_TEXT  (58)
#endif

#endif /* PyOpenSSL_CRYPTO_H_ */
