/*
 * A type which wraps a socket
 *
 * socket_connection.c
 *
 * Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
 */

#include "processing.h"

#ifdef MS_WINDOWS
#  define WRITE(h, buffer, length) send((SOCKET)h, buffer, length, 0)
#  define READ(h, buffer, length) recv((SOCKET)h, buffer, length, 0)
#  define CLOSE(h) CloseHandle(h)
#  define DUPLICATE(h) duplicate_handle(h)
#else
#  define WRITE(h, buffer, length) write(h, buffer, length)
#  define READ(h, buffer, length) read(h, buffer, length)
#  define CLOSE(h) close(h)
#  define DUPLICATE(h) dup(h)
#endif

/*
 * Connection struct
 */

#define BUFFER_SIZE 1024

typedef struct {
    PyObject_HEAD
    HANDLE handle;
    PyObject *weakreflist;
    char buffer[BUFFER_SIZE];
} Connection;

/*
 * Send string to file descriptor
 */

static Py_ssize_t
_conn_sendall(HANDLE h, char *string, size_t length)
{
    char *p = string;
    Py_ssize_t res;
    
    while (length > 0) {
        res = WRITE(h, p, length);
        if (res < 0)
            return STANDARD_ERROR;
        length -= res;
        p += res;
    }
    
    return SUCCESS;
}

/*
 * Receive string of exact length from file descriptor 
 */

static Py_ssize_t
_conn_recvall(HANDLE h, char *buffer, size_t length)
{
    size_t remaining = length;
    Py_ssize_t temp;
    char *p = buffer;
    
    while (remaining > 0) {
        temp = READ(h, p, remaining);
        if (temp <= 0) {
            if (temp == 0)
                return remaining == length ? END_OF_FILE : EARLY_END_OF_FILE;
            else
                return temp;
        }
        remaining -= temp;
        p += temp;
    }
    
    return SUCCESS;
}

/*
 * Send a string prepended by the string length in network byte order
 */

static Py_ssize_t
conn_send_string(Connection *conn, char *string, size_t length)
{
    /* The "header" of the message is a 32 bit unsigned number (in
       network order) which signifies the length of the "body".  If
       the message is shorter than about 16kb then it is quicker to
       combine the "header" and the "body" of the message and send
       them at once. */
    if (length < (16*1024)) {
        char *message;
        int res;
        
        message = PyMem_Malloc(length+4);
        if (message == NULL)
            return MEMORY_ERROR;
        
        *(UINT32*)message = htonl((UINT32)length);     
        memcpy(message+4, string, length);
        res = _conn_sendall(conn->handle, message, length+4);
        PyMem_Free(message);
        return res;
    } else {
        UINT32 lenbuff;

        if (TOO_LONG(length))
            return BAD_MESSAGE_LENGTH;

        lenbuff = htonl((UINT32)length);
        return _conn_sendall(conn->handle, (char*)&lenbuff, 4) || 
            _conn_sendall(conn->handle, string, length);
    }
}

/*
 * Attempts to read into buffer, or failing that into *newbuffer
 *
 * Returns number of bytes read.
 */

static Py_ssize_t
conn_recv_string(Connection *conn, char *buffer, 
                 size_t buflength, char **newbuffer)
{
    int res;
    UINT32 ulength;
    
    *newbuffer = NULL;
    
    res = _conn_recvall(conn->handle, (char*)&ulength, 4);
    if (res < 0)
        return res;
    
    ulength = ntohl(ulength);
    if (TOO_LONG(ulength))
        return BAD_MESSAGE_LENGTH;
    
    if (ulength <= buflength) {
        res = _conn_recvall(conn->handle, buffer, (size_t)ulength);
        return res < 0 ? res : ulength;
    } else {
        *newbuffer = PyMem_Malloc((size_t)ulength);
        if (*newbuffer == NULL)
            return MEMORY_ERROR;
        res = _conn_recvall(conn->handle, *newbuffer, (size_t)ulength);
        return res < 0 ? (Py_ssize_t)res : (Py_ssize_t)ulength;
    }
}

/*
 * Check whether any data is available for reading -- neg timeout blocks
 */

static int
conn_poll(Connection *conn, double timeout)
{
    int res;
    fd_set rfds;
    
    FD_ZERO(&rfds);
    FD_SET((SOCKET)conn->handle, &rfds);

    if (timeout < 0.0) {
        res = select((int)conn->handle+1, &rfds, NULL, NULL, NULL);
    } else {
        struct timeval tv;
        tv.tv_sec = (long)timeout;
        tv.tv_usec = (long)((timeout - tv.tv_sec) * 1e6 + 0.5);
        res = select((int)conn->handle+1, &rfds, NULL, NULL, &tv);
    }
    
#ifdef MS_WINDOWS
    if (res == SOCKET_ERROR) {
        return WSA_ERROR;
#else
    if (res < 0) {
        return STANDARD_ERROR;
#endif
    } else if (FD_ISSET(conn->handle, &rfds)) {
        return TRUE;
    } else if (res == 0) {
        return FALSE;
    } else {
        return -2000;           /* should not get here */
    }
}

/*
 * "connection.h" defines the Connection type using the definitions above
 */

#define CONNECTION_NAME "Connection"
#define CONNECTION_TYPE ConnectionType

#include "connection.h"
