/*
 * A type which wraps a pipe handle in message oriented mode
 *
 * pipe_connection.c
 *
 * Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
 */

#include "processing.h"

#define CLOSE(h) CloseHandle(h)
#define DUPLICATE(h) duplicate_handle(h)

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
 * Send string to the pipe; assumes in message oriented mode
 */

static Py_ssize_t
conn_send_string(Connection *conn, char *string, size_t length)
{
    DWORD amount_written;

    if (!WriteFile(conn->handle, string, length, &amount_written, NULL))
        return STANDARD_ERROR;

    /* assert(length == amount_written); */
    return SUCCESS;
}

/*
 * Attempts to read into buffer, or if buffer too small into *newbuffer.
 *
 * Returns number of bytes read.  Assumes in message oriented mode.
 */

static Py_ssize_t
conn_recv_string(Connection *conn, char *buffer, 
                 size_t buflength, char **newbuffer)
{
    DWORD left, length, full_length, err;
    
    *newbuffer = NULL;

    if (ReadFile(conn->handle, buffer, buflength, &length, NULL))
        return length;
    
    err = GetLastError();
    if (err != ERROR_MORE_DATA) {
        if (err == ERROR_BROKEN_PIPE)
            return END_OF_FILE;
        return STANDARD_ERROR;
    }
    
    if (!PeekNamedPipe(conn->handle, NULL, 0, NULL, NULL, &left))
        return STANDARD_ERROR;

    full_length = length + left;
    if (TOO_LONG(full_length))
        return BAD_MESSAGE_LENGTH;

    *newbuffer = PyMem_Malloc(full_length);
    if (*newbuffer == NULL)
        return MEMORY_ERROR;
    
    memcpy(*newbuffer, buffer, length);

    if (ReadFile(conn->handle, *newbuffer+length, left, &length, NULL)) {
        assert(length == left);
        return full_length;
    } else {
        PyMem_Free(*newbuffer);
        return STANDARD_ERROR;
    }
}

/*
 * Check whether any data is available for reading
 */

#define conn_poll(conn, timeout) conn_poll_save(conn, timeout, _save)

static int
conn_poll_save(Connection *conn, double timeout, PyThreadState *_save)
{
    DWORD bytes, deadline, delay;
    int difference, res;
    BOOL block = FALSE;
    
    if (!PeekNamedPipe(conn->handle, NULL, 0, NULL, &bytes, NULL))
        return STANDARD_ERROR;

    if (timeout == 0.0)
        return bytes > 0;

    if (timeout < 0.0)
        block = TRUE;
    else
        /* XXX does not check for overflow */
        deadline = GetTickCount() + (DWORD)(1000 * timeout + 0.5);

    Sleep(0);

    for (delay = 1 ; ; delay += 1) {
        if (!PeekNamedPipe(conn->handle, NULL, 0, NULL, &bytes, NULL))
            return STANDARD_ERROR;
        else if (bytes > 0)
            return TRUE;

        if (!block) {
            difference = deadline - GetTickCount();
            if (difference < 0)
                return FALSE;
            if ((int)delay > difference)
                delay = difference;
        }

        if (delay > 20)
            delay = 20;

        Sleep(delay);
        
        /* check for signals */
        Py_BLOCK_THREADS 
        res = PyErr_CheckSignals();
        Py_UNBLOCK_THREADS
            
        if (res)
            return EXCEPTION_HAS_BEEN_SET;
    }
}

/*
 * "connection.h" defines the PipeConnection type using the definitions above
 */

#define CONNECTION_NAME "PipeConnection"
#define CONNECTION_TYPE PipeConnectionType

#include "connection.h"
