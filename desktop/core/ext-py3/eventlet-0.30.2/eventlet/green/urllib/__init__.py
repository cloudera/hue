from eventlet import patcher
from eventlet.green import socket
from eventlet.green import time
from eventlet.green import httplib
from eventlet.green import ftplib
import six

if six.PY2:
    to_patch = [('socket', socket), ('httplib', httplib),
                ('time', time), ('ftplib', ftplib)]
    try:
        from eventlet.green import ssl
        to_patch.append(('ssl', ssl))
    except ImportError:
        pass

    patcher.inject('urllib', globals(), *to_patch)
    try:
        URLopener
    except NameError:
        patcher.inject('urllib.request', globals(), *to_patch)


    # patch a bunch of things that have imports inside the
    # function body; this is lame and hacky but I don't feel
    # too bad because urllib is a hacky pile of junk that no
    # one should be using anyhow
    URLopener.open_http = patcher.patch_function(URLopener.open_http, ('httplib', httplib))
    if hasattr(URLopener, 'open_https'):
        URLopener.open_https = patcher.patch_function(URLopener.open_https, ('httplib', httplib))

    URLopener.open_ftp = patcher.patch_function(URLopener.open_ftp, ('ftplib', ftplib))
    ftpwrapper.init = patcher.patch_function(ftpwrapper.init, ('ftplib', ftplib))
    ftpwrapper.retrfile = patcher.patch_function(ftpwrapper.retrfile, ('ftplib', ftplib))

    del patcher

    # Run test program when run as a script
    if __name__ == '__main__':
        main()
