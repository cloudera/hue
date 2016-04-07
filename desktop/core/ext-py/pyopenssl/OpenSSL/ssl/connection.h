/*
 * connection.h
 *
 * Copyright (C) AB Strakt
 * See LICENSE for details.
 *
 * Export SSL Connection data structures and functions.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 *
 */
#ifndef PyOpenSSL_SSL_CONNECTION_H_
#define PyOpenSSL_SSL_CONNECTION_H_

#include <Python.h>
#include <openssl/ssl.h>

/* shamelessly stolen from socketmodule.c */
#ifdef MS_WINDOWS
#  include <winsock.h>
typedef SOCKET SOCKET_T;
#  ifdef MS_WIN64
#    define SIZEOF_SOCKET_T 8
#  else
#    define SIZEOF_SOCKET_T 4
#  endif
#else
typedef int SOCKET_T;
#  define SIZEOF_SOCKET_T SIZEOF_INT
#endif


extern  int                      init_ssl_connection      (PyObject *);

extern  PyTypeObject      ssl_Connection_Type;

#define ssl_Connection_Check(v) ((v)->ob_type == &ssl_Connection_Type)

typedef struct {
    PyObject_HEAD
    SSL                 *ssl;
    ssl_ContextObj      *context;
    PyObject            *socket;
    PyThreadState       *tstate; /* This field is no longer used. */
    PyObject            *app_data;
    BIO                 *into_ssl, *from_ssl;  /* for connections without file descriptors */
} ssl_ConnectionObj;



#endif

