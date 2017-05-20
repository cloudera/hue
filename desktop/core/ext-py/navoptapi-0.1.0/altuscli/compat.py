# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import copy
import os
import sys

from altuscli.thirdparty import six  # noqa


if six.PY3:
    from base64 import encodebytes  # noqa
    from email.utils import formatdate  # noqa
    from http.client import HTTPResponse  # noqa
    import locale
    from six.moves import http_client
    from urllib.parse import urlsplit  # noqa
    from urllib.parse import urlunsplit  # noqa

    raw_input = input

    class HTTPHeaders(http_client.HTTPMessage):
        pass

    def get_stdout_text_writer():
        return sys.stdout

    def ensure_unicode(s, encoding=None, errors=None):
        # NOOP in Python 3, because every string is already unicode
        return s

    def compat_open(filename, mode='r', encoding=None):
        """Back-port open() that accepts an encoding argument.

        In python3 this uses the built in open() and in python2 this
        uses the io.open() function.

        If the file is not being opened in binary mode, then we'll
        use locale.getpreferredencoding() to find the preferred
        encoding.

        """
        if 'b' not in mode:
            encoding = locale.getpreferredencoding()
        return open(filename, mode, encoding=encoding)

else:
    from base64 import encodestring as encodebytes  # noqa
    import codecs
    from email.message import Message
    from email.Utils import formatdate  # noqa
    from httplib import HTTPResponse  # noqa
    import io
    import locale
    from urlparse import urlsplit  # noqa
    from urlparse import urlunsplit  # noqa

    raw_input = raw_input

    class HTTPHeaders(Message):

        # The __iter__ method is not available in python2.x, so we have
        # to port the py3 version.
        def __iter__(self):
            for field, value in self._headers:
                yield field

    def get_stdout_text_writer():
        # In python3, all the sys.stdout/sys.stderr streams are in text
        # mode.  This means they expect unicode, and will encode the
        # unicode automatically before actually writing to stdout/stderr.
        # In python2, that's not the case.  In order to provide a consistent
        # interface, we can create a wrapper around sys.stdout that will take
        # unicode, and automatically encode it to the preferred encoding.
        # That way consumers can just call get_stdout_text_writer() and write
        # unicode to the returned stream.  Note that get_stdout_text_writer
        # just returns sys.stdout in the PY3 section above because python3
        # handles this.
        return codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

    def ensure_unicode(s, encoding='utf-8', errors='strict'):
        if isinstance(s, six.text_type):
            return s
        return unicode(s, encoding, errors)

    def compat_open(filename, mode='r', encoding=None):
        # See docstring for compat_open in the PY3 section above.
        if 'b' not in mode:
            encoding = locale.getpreferredencoding()
        return io.open(filename, mode, encoding=encoding)

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # noqa

if sys.version_info[:2] == (2, 6):
    import simplejson as json
else:
    import json  # noqa


@classmethod
def from_dict(cls, d):
    new_instance = cls()
    for key, value in d.items():
        new_instance[key] = value
    return new_instance


@classmethod
def from_pairs(cls, pairs):
    new_instance = cls()
    for key, value in pairs:
        new_instance[key] = value
    return new_instance


HTTPHeaders.from_dict = from_dict
HTTPHeaders.from_pairs = from_pairs


def copy_kwargs(kwargs):
    """
    There is a bug in Python versions < 2.6.5 that prevents you from passing
    unicode keyword args (#4978).  This function takes a dictionary of kwargs and
    returns a copy.  If you are using Python < 2.6.5, it also encodes the keys to
    avoid this bug. Oh, and version_info wasn't a namedtuple back then, either!
    """
    vi = sys.version_info
    if vi[0] == 2 and vi[1] <= 6 and vi[3] < 5:
        copy_kwargs = {}
        for key in kwargs:
            copy_kwargs[key.encode('utf-8')] = kwargs[key]
    else:
        copy_kwargs = copy.copy(kwargs)
    return copy_kwargs


def compat_input(prompt, interactive_long_input=False):
    """
    Cygwin's pty's are based on pipes. Therefore, when it interacts with a Win32
    program (such as Win32 python), what that program sees is a pipe instead of
    a console. This is important because python buffers pipes, and so on a
    pty-based terminal, text will not necessarily appear immediately. In most
    cases, this isn't a big deal. But when we're doing an interactive prompt,
    the result is that the prompts won't display until we fill the buffer. Since
    raw_input does not flush the prompt, we need to manually write and flush it.

    See https://github.com/mintty/mintty/issues/56 for more details.
    """
    is_windows = sys.platform.startswith('win')
    if interactive_long_input:
        # See THUN-222 for context on why this is necessary
        if is_windows is False:
            os.system('stty -icanon')
    sys.stdout.write(prompt)
    sys.stdout.flush()
    if is_windows is False:
        os.system('stty sane')
    return raw_input()
