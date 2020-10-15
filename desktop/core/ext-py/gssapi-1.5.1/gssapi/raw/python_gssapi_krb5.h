#ifdef OSX_HAS_GSS_FRAMEWORK
#include <GSS/gssapi_krb5.h>
#elif __MINGW32__
#include <gss.h>
#else
#include <gssapi/gssapi_krb5.h>
#endif
