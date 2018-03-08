from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef("""
    typedef ... DIR;
    struct dirent {
        unsigned char d_type;   /* type of file */
        char d_name[];          /* filename */
        ...;
    };
    DIR *opendir(const char *name);
    int closedir(DIR *dirp);
    struct dirent *readdir(DIR *dirp);
    static const int DT_BLK, DT_CHR, DT_DIR, DT_FIFO, DT_LNK, DT_REG, DT_SOCK;
""")

ffibuilder.set_source("_bsdopendirtype", """
    #include <sys/types.h>
    #include <dirent.h>
""")

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
