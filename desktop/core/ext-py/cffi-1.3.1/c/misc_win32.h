#include <malloc.h>   /* for alloca() */

/************************************************************/
/* errno and GetLastError support */

struct cffi_errno_s {
    int saved_errno;
    int saved_lasterror;
};

static DWORD cffi_tls_index = TLS_OUT_OF_INDEXES;

static void init_errno(void)
{
    if (cffi_tls_index == TLS_OUT_OF_INDEXES) {
        cffi_tls_index = TlsAlloc();
        if (cffi_tls_index == TLS_OUT_OF_INDEXES)
            PyErr_SetString(PyExc_WindowsError, "TlsAlloc() failed");
    }
}

static struct cffi_errno_s *_geterrno_object(void)
{
    LPVOID p = TlsGetValue(cffi_tls_index);

    if (p == NULL) {
        /* XXX this malloc() leaks */
        p = malloc(sizeof(struct cffi_errno_s));
        if (p == NULL)
            return NULL;
        memset(p, 0, sizeof(struct cffi_errno_s));
        TlsSetValue(cffi_tls_index, p);
    }
    return (struct cffi_errno_s *)p;
}

static void save_errno(void)
{
    int current_err = errno;
    int current_lasterr = GetLastError();
    struct cffi_errno_s *p;

    p = _geterrno_object();
    if (p != NULL) {
        p->saved_errno = current_err;
        p->saved_lasterror = current_lasterr;
    }
    /* else: cannot report the error */
}

static void save_errno_only(void)
{
    int current_err = errno;
    struct cffi_errno_s *p;

    p = _geterrno_object();
    if (p != NULL) {
        p->saved_errno = current_err;
    }
    /* else: cannot report the error */
}

static void restore_errno(void)
{
    struct cffi_errno_s *p;

    p = _geterrno_object();
    if (p != NULL) {
        SetLastError(p->saved_lasterror);
        errno = p->saved_errno;
    }
    /* else: cannot report the error */
}

static void restore_errno_only(void)
{
    struct cffi_errno_s *p;

    p = _geterrno_object();
    if (p != NULL) {
        errno = p->saved_errno;
    }
    /* else: cannot report the error */
}

#if PY_MAJOR_VERSION >= 3
static PyObject *b_getwinerror(PyObject *self, PyObject *args, PyObject *kwds)
{
    int err = -1;
    int len;
    WCHAR *s_buf = NULL; /* Free via LocalFree */
    PyObject *v, *message;
    static char *keywords[] = {"code", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", keywords, &err))
        return NULL;

    if (err == -1) {
        struct cffi_errno_s *p;
        p = _geterrno_object();
        if (p == NULL)
            return PyErr_NoMemory();
        err = p->saved_lasterror;
    }

    len = FormatMessageW(
        /* Error API error */
        FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_FROM_SYSTEM |
        FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL,           /* no message source */
        err,
        MAKELANGID(LANG_NEUTRAL,
        SUBLANG_DEFAULT), /* Default language */
        (LPWSTR) &s_buf,
        0,              /* size not used */
        NULL);          /* no args */
    if (len==0) {
        /* Only seen this in out of mem situations */
        message = PyUnicode_FromFormat("Windows Error 0x%X", err);
    } else {
        /* remove trailing cr/lf and dots */
        while (len > 0 && (s_buf[len-1] <= L' ' || s_buf[len-1] == L'.'))
            s_buf[--len] = L'\0';
        message = PyUnicode_FromWideChar(s_buf, len);
    }
    if (message != NULL)
        v = Py_BuildValue("(iO)", err, message);
    else
        v = NULL;
    LocalFree(s_buf);
    return v;
}
#else
static PyObject *b_getwinerror(PyObject *self, PyObject *args, PyObject *kwds)
{
    int err = -1;
    int len;
    char *s;
    char *s_buf = NULL; /* Free via LocalFree */
    char s_small_buf[28]; /* Room for "Windows Error 0xFFFFFFFF" */
    PyObject *v;
    static char *keywords[] = {"code", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", keywords, &err))
        return NULL;

    if (err == -1) {
        struct cffi_errno_s *p;
        p = _geterrno_object();
        if (p == NULL)
            return PyErr_NoMemory();
        err = p->saved_lasterror;
    }

    len = FormatMessage(
        /* Error API error */
        FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_FROM_SYSTEM |
        FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL,           /* no message source */
        err,
        MAKELANGID(LANG_NEUTRAL,
        SUBLANG_DEFAULT), /* Default language */
        (LPTSTR) &s_buf,
        0,              /* size not used */
        NULL);          /* no args */
    if (len==0) {
        /* Only seen this in out of mem situations */
        sprintf(s_small_buf, "Windows Error 0x%X", err);
        s = s_small_buf;
        s_buf = NULL;
    } else {
        s = s_buf;
        /* remove trailing cr/lf and dots */
        while (len > 0 && (s[len-1] <= ' ' || s[len-1] == '.'))
            s[--len] = '\0';
    }
    v = Py_BuildValue("(is)", err, s);
    LocalFree(s_buf);
    return v;
}
#endif

/************************************************************/
/* Emulate dlopen()&co. from the Windows API */

#define RTLD_LAZY   0
#define RTLD_NOW    0
#define RTLD_GLOBAL 0
#define RTLD_LOCAL  0

static void *dlopen(const char *filename, int flag)
{
    return (void *)LoadLibrary(filename);
}

static void *dlsym(void *handle, const char *symbol)
{
    void *address = GetProcAddress((HMODULE)handle, symbol);
#ifndef MS_WIN64
    if (!address) {
        /* If 'symbol' is not found, then try '_symbol@N' for N in
           (0, 4, 8, 12, ..., 124).  Unlike ctypes, we try to do that
           for any symbol, although in theory it should only be done
           for __stdcall functions.
        */
        int i;
        char *mangled_name = alloca(1 + strlen(symbol) + 1 + 3 + 1);
        if (!mangled_name)
            return NULL;
        for (i = 0; i < 32; i++) {
            sprintf(mangled_name, "_%s@%d", symbol, i * 4);
            address = GetProcAddress((HMODULE)handle, mangled_name);
            if (address)
                break;
        }
    }
#endif
    return address;
}

static int dlclose(void *handle)
{
    return FreeLibrary((HMODULE)handle) ? 0 : -1;
}

static const char *dlerror(void)
{
    static char buf[32];
    DWORD dw = GetLastError(); 
    if (dw == 0)
        return NULL;
    sprintf(buf, "error 0x%x", (unsigned int)dw);
    return buf;
}

/************************************************************/
/* obscure */

#define ffi_prep_closure(a,b,c,d)  ffi_prep_closure_loc(a,b,c,d,a)
