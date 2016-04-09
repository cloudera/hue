from cffi import FFI

ffi = FFI()
ffi.cdef("""

    typedef ... DIR;

    struct dirent {
        unsigned char  d_type;      /* type of file; not supported
                                       by all file system types */
        char           d_name[...]; /* filename */
        ...;
    };

    int readdir_r(DIR *dirp, struct dirent *entry, struct dirent **result);
    int openat(int dirfd, const char *pathname, int flags);
    DIR *fdopendir(int fd);
    int closedir(DIR *dirp);

    static const int DT_DIR;

""")
ffi.set_source("_readdir2_cffi", """
#ifndef _ATFILE_SOURCE
#  define _ATFILE_SOURCE
#endif
#ifndef _BSD_SOURCE
#  define _BSD_SOURCE
#endif
#include <fcntl.h>
#include <sys/types.h>
#include <dirent.h>
""")

if __name__ == '__main__':
    ffi.compile()
