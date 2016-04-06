from _bsdopendirtype import ffi, lib


def _posix_error():
    raise OSError(ffi.errno, os.strerror(ffi.errno))

_dtype_to_smode = {
    lib.DT_BLK:  0o060000,
    lib.DT_CHR:  0o020000,
    lib.DT_DIR:  0o040000,
    lib.DT_FIFO: 0o010000,
    lib.DT_LNK:  0o120000,
    lib.DT_REG:  0o100000,
    lib.DT_SOCK: 0o140000,
}

def opendir(dir):
    if len(dir) == 0:
        dir = b'.'
    dirname = dir
    if not dirname.endswith(b'/'):
        dirname += b'/'
    dirp = lib.opendir(dir)
    if dirp == ffi.NULL:
        raise _posix_error()
    try:
        while True:
            ffi.errno = 0
            dirent = lib.readdir(dirp)
            if dirent == ffi.NULL:
                if ffi.errno != 0:
                    raise _posix_error()
                return
            name = ffi.string(dirent.d_name)
            if name == b'.' or name == b'..':
                continue
            name = dirname + name
            try:
                smode = _dtype_to_smode[dirent.d_type]
            except KeyError:
                smode = os.lstat(name).st_mode
            yield name, smode
    finally:
        lib.closedir(dirp)

if __name__ == '__main__':
    for name, smode in opendir(b'/tmp'):
        print(hex(smode), name)
