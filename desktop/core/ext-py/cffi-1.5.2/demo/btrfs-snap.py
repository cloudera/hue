"""
btrfs-snap.py: source target newname

creates a exactly named snapshots and bails out if they exist
"""

import argparse
import fcntl
import os
import sys

import cffi

ffi = cffi.FFI()

ffi.cdef("""
    #define BTRFS_IOC_SNAP_CREATE_V2 ...
    struct btrfs_ioctl_vol_args_v2 {
        int64_t fd;
        char name[];
        ...;
    };
""")

ffi.set_source("_btrfs_cffi", "#include <btrfs/ioctl.h>")
ffi.compile()

# ____________________________________________________________


from _btrfs_cffi import ffi, lib

parser = argparse.ArgumentParser(usage=__doc__.strip())
parser.add_argument('source', help='source subvolume')
parser.add_argument('target', help='target directory')
parser.add_argument('newname', help='name of the new snapshot')
opts = parser.parse_args()

source = os.open(opts.source, os.O_DIRECTORY)
target = os.open(opts.target, os.O_DIRECTORY)


args = ffi.new('struct btrfs_ioctl_vol_args_v2 *')
args.name = opts.newname
args.fd = source
args_buffer = ffi.buffer(args)
try:
    fcntl.ioctl(target, lib.BTRFS_IOC_SNAP_CREATE_V2, args_buffer)
except IOError as e:
    print e
    sys.exit(1)

