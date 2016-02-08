#include <pthread.h>

/* This is only included if GCC doesn't support "__thread" global variables.
 * See USE__THREAD in _ffi_backend.c.
 */

static pthread_key_t cffi_tls_key;

static void init_errno(void)
{
    (void) pthread_key_create(&cffi_tls_key, NULL);
}

static void save_errno(void)
{
    intptr_t value = errno;
    (void) pthread_setspecific(cffi_tls_key, (void *)value);
}

static void restore_errno(void) {
    intptr_t value = (intptr_t)pthread_getspecific(cffi_tls_key);
    errno = value;
}
