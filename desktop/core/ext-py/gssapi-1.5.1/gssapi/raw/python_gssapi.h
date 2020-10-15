#ifdef OSX_HAS_GSS_FRAMEWORK
#include <GSS/GSS.h>
#elif __MINGW32__
#include <gss.h>
#else
#include <gssapi/gssapi.h>
#endif
