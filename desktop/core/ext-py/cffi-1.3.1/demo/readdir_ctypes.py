# A Linux-only demo
#
# For comparison purposes, this is a ctypes version of readdir.py.
import sys
import ctypes

if not sys.platform.startswith('linux'):
    raise Exception("Linux-only demo")


DIR_p = ctypes.c_void_p
ino_t = ctypes.c_long
off_t = ctypes.c_long

class DIRENT(ctypes.Structure):
    _fields_ = [
        ('d_ino', ino_t),                 # inode number
        ('d_off', off_t),                 # offset to the next dirent
        ('d_reclen', ctypes.c_ushort),    # length of this record
        ('d_type', ctypes.c_ubyte),       # type of file; not supported
                                          #   by all file system types
        ('d_name', ctypes.c_char * 256),  # filename
        ]
DIRENT_p = ctypes.POINTER(DIRENT)
DIRENT_pp = ctypes.POINTER(DIRENT_p)

C = ctypes.CDLL(None)

readdir_r = C.readdir_r
readdir_r.argtypes = [DIR_p, DIRENT_p, DIRENT_pp]
readdir_r.restype = ctypes.c_int

openat = C.openat
openat.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
openat.restype = ctypes.c_int

fdopendir = C.fdopendir
fdopendir.argtypes = [ctypes.c_int]
fdopendir.restype = DIR_p

closedir = C.closedir
closedir.argtypes = [DIR_p]
closedir.restype = ctypes.c_int


def walk(basefd, path):
    print '{', path
    dirfd = openat(basefd, path, 0)
    if dirfd < 0:
        # error in openat()
        return
    dir = fdopendir(dirfd)
    dirent = DIRENT()
    result = DIRENT_p()
    while True:
        if readdir_r(dir, dirent, result):
            # error in readdir_r()
            break
        if not result:
            break
        name = dirent.d_name
        print '%3d %s' % (dirent.d_type, name)
        if dirent.d_type == 4 and name != '.' and name != '..':
            walk(dirfd, name)
    closedir(dir)
    print '}'


walk(-1, "/tmp")
