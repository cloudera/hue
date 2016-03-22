import sys
from cffi import FFI

if not sys.platform.startswith('linux'):
    raise Exception("Linux-only demo")


ffi = FFI()
ffi.cdef("""

    typedef void DIR;
    typedef long ino_t;
    typedef long off_t;

    struct dirent {
        ino_t          d_ino;       /* inode number */
        off_t          d_off;       /* offset to the next dirent */
        unsigned short d_reclen;    /* length of this record */
        unsigned char  d_type;      /* type of file; not supported
                                       by all file system types */
        char           d_name[256]; /* filename */
    };

    int readdir_r(DIR *dirp, struct dirent *entry, struct dirent **result);
    int openat(int dirfd, const char *pathname, int flags);
    DIR *fdopendir(int fd);
    int closedir(DIR *dirp);

""")
ffi.set_source("_readdir", None)

if __name__ == '__main__':
    ffi.compile()
