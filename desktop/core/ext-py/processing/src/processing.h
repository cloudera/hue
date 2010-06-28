#ifndef PROCESSING_H
#define PROCESSING_H

#define PY_SSIZE_T_CLEAN

#include "Python.h"
#include "structmember.h"
#include "pythread.h"

/*
 * Platform includes and definitions
 */

#ifdef MS_WINDOWS
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
#  include <winsock2.h>
#  include <process.h>
#  define SEM_HANDLE HANDLE
   HANDLE duplicate_handle(HANDLE h);
#else
#  include <unistd.h>
#  include <sys/socket.h>
#  include <arpa/inet.h>
#  if HAVE_SEM_OPEN
#    include <semaphore.h>
#    include <fcntl.h>
     typedef sem_t *SEM_HANDLE;
#  endif
#  define HANDLE int
#  define SOCKET int
#  define BOOL int
#  define UINT32 uint32_t
#  define INT32 int32_t
#  define TRUE 1
#  define FALSE 0
#  define INVALID_HANDLE_VALUE (-1)
#endif

/*
 * Make sure Py_ssize_t available
 */

#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
   typedef int Py_ssize_t;
#  define PY_SSIZE_T_MAX INT_MAX
#  define PY_SSIZE_T_MIN INT_MIN
#  define F_PY_SSIZE_T "i"
#  define PY_FORMAT_SIZE_T ""
#  define PyInt_FromSsize_t(n) PyInt_FromLong((long)n)
#else
#  define F_PY_SSIZE_T "n"
#endif

/*
 * Format codes
 */

#if SIZEOF_VOID_P == SIZEOF_LONG
#  define F_POINTER "k"
#  define T_POINTER T_ULONG
#elif defined(HAVE_LONG_LONG) && (SIZEOF_VOID_P == SIZEOF_LONG_LONG)
#  define F_POINTER "K"
#  define T_POINTER T_ULONGLONG
#else
#  error "can't find format code for unsigned integer of same size as void*"
#endif

#ifdef MS_WINDOWS
#  define F_HANDLE F_POINTER
#  define T_HANDLE T_POINTER
#  define F_SEM_HANDLE F_HANDLE
#  define T_SEM_HANDLE T_HANDLE
#  define F_DWORD "k"
#  define T_DWORD T_ULONG
#else
#  define F_HANDLE "i"
#  define T_HANDLE T_INT
#  define F_SEM_HANDLE F_POINTER
#  define T_SEM_HANDLE T_POINTER
#endif

/*
 * Message length limited to 2**31-1
 */

#define TOO_LONG(n) ((UINT32)n >= 0x7fffffff)

/*
 * Error codes which can be returned by functions called without GIL
 */

#define SUCCESS (0)
#define STANDARD_ERROR (-1)
#define MEMORY_ERROR (-1001)
#define END_OF_FILE (-1002)
#define EARLY_END_OF_FILE (-1003)
#define BAD_MESSAGE_LENGTH (-1004)
#define WSA_ERROR (-1005)
#define EXCEPTION_HAS_BEEN_SET (-1006)

PyObject *SetException(PyObject *Type, int num);

/*
 * Externs
 */

extern PyObject *dumpsFunction;
extern PyObject *loadsFunction;
extern PyObject *protocol;
extern PyObject *BufferTooShort;
extern PyTypeObject SemLockType;
extern PyTypeObject ConnectionType;

#ifdef MS_WINDOWS
extern PyTypeObject PipeConnectionType;
extern HANDLE hInterruptEvent;
extern long main_thread;
#endif

#endif /* PROCESSING_H */
