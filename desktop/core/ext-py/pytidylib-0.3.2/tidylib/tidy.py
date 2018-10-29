# Copyright 2009-2015 Jason Stitt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import ctypes
import ctypes.util
import threading
import platform
import warnings
from contextlib import contextmanager
from .sink import create_sink, destroy_sink

__all__ = ['Tidy', 'PersistentTidy']

# Default search order for library names if nothing is passed in
LIB_NAMES = ['libtidy', 'libtidy.so', 'libtidy-0.99.so.0', 'cygtidy-0-99-0',
             'tidylib', 'libtidy.dylib', 'tidy']

# Error code from library
ENOMEM = -12

# Default options; can be overriden with argument to Tidy()
BASE_OPTIONS = {
    "indent": 1,           # Pretty; not too much of a performance hit
    "tidy-mark": 0,        # No tidy meta tag in output
    "wrap": 0,             # No wrapping
    "alt-text": "",        # Help ensure validation
    "doctype": 'strict',   # Little sense in transitional for tool-generated markup...
    "force-output": 1,     # May not get what you expect but you will get something
}

KEEP_DOC_WARNING = "keep_doc and release_tidy_doc are no longer used. Create a PersistentTidy object instead."

# Fix for Windows b/c tidy uses stdcall on Windows
if "Windows" == platform.system():
    load_library = ctypes.windll.LoadLibrary
else:
    load_library = ctypes.cdll.LoadLibrary

# -------------------------------------------------------------------------- #
# 3.x/2.x cross-compatibility

try:
    unicode  # 2.x

    def is_unicode(obj):
        return isinstance(obj, unicode)

    def encode_key_value(k, v):
        return unicode(k).encode('utf-8'), unicode(v).encode('utf-8')
except NameError:
    # 3.x
    def is_unicode(obj):
        return isinstance(obj, str)

    def encode_key_value(k, v):
        return str(k).encode('utf-8'), str(v).encode('utf-8')

# -------------------------------------------------------------------------- #
# The main python interface


class Tidy(object):

    """ Wrapper around the HTML Tidy library for cleaning up possibly invalid
    HTML and XHTML. """

    def __init__(self, lib_names=None):
        self._tidy = None
        if lib_names is None:
            lib_names = ctypes.util.find_library('tidy') or LIB_NAMES
        if isinstance(lib_names, str):
            lib_names = [lib_names]
        for name in lib_names:
            try:
                self._tidy = load_library(name)
                break
            except OSError:
                continue
        if self._tidy is None:
            raise OSError(
                "Could not load libtidy using any of these names: "
                + ",".join(lib_names))
        self._tidy.tidyCreate.restype = ctypes.POINTER(ctypes.c_void_p)  # Fix for 64-bit systems

    @contextmanager
    def _doc_and_sink(self):
        " Create and cleanup a Tidy document and error sink "
        doc = self._tidy.tidyCreate()
        sink = create_sink()
        self._tidy.tidySetErrorSink(doc, sink)
        yield (doc, sink)
        destroy_sink(sink)
        self._tidy.tidyRelease(doc)

    def tidy_document(self, text, options=None):
        """ Run a string with markup through HTML Tidy; return the corrected one
        and any error output.

        text: The markup, which may be anything from an empty string to a complete
        (X)HTML document. If you pass in a unicode type (py3 str, py2 unicode) you
        get one back out, and tidy will have some options set that may affect
        behavior (e.g. named entities converted to plain unicode characters). If
        you pass in a bytes type (py3 bytes, py2 str) you will get one of those
        back.

        options (dict): Options passed directly to HTML Tidy; see the HTML Tidy docs
        (http://tidy.sourceforge.net/docs/quickref.html) or run tidy -help-config
        from the command line.

        returns (str, str): The tidied markup and unparsed warning/error messages.
        Warnings and errors are returned just as tidylib returns them.
        """

        # Unicode approach is to encode as string, then decode libtidy output
        use_unicode = False
        if is_unicode(text):
            use_unicode = True
            text = text.encode('utf-8')

        with self._doc_and_sink() as (doc, sink):
            tidy_options = dict(BASE_OPTIONS)
            if options:
                tidy_options.update(options)
            if use_unicode:
                tidy_options['input-encoding'] = 'utf8'
                tidy_options['output-encoding'] = 'utf8'
            for key in tidy_options:
                value = tidy_options[key]
                key = key.replace('_', '-')
                if value is None:
                    value = ''
                key, value = encode_key_value(key, value)
                self._tidy.tidyOptParseValue(doc, key, value)
                error = str(sink)
                if error:
                    raise ValueError("(tidylib) " + error)

            self._tidy.tidyParseString(doc, text)
            self._tidy.tidyCleanAndRepair(doc)

            # Guess at buffer size; tidy returns ENOMEM if the buffer is too
            # small and puts the required size into out_length
            out_length = ctypes.c_int(8192)
            out = ctypes.c_buffer(out_length.value)
            while ENOMEM == self._tidy.tidySaveString(doc, out, ctypes.byref(out_length)):
                out = ctypes.c_buffer(out_length.value)

            document = out.value
            if use_unicode:
                document = document.decode('utf-8')
            errors = str(sink)

        return (document, errors)

    def tidy_fragment(self, text, options=None):
        """ Tidy a string with markup and return only the <body> contents.

        HTML Tidy normally returns a full (X)HTML document; this function returns only
        the contents of the <body> element and is meant to be used for snippets.
        Calling tidy_fragment on elements that don't go in the <body>, like <title>,
        will produce incorrect behavior.

        Arguments and return value are the same as tidy_document. Note that HTML
        Tidy will always complain about the lack of a doctype and <title> element
        in fragments, and these errors are not stripped out for you. """
        options = dict(options) if options else dict()
        options["show-body-only"] = 1
        document, errors = self.tidy_document(text, options)
        document = document.strip()
        return document, errors


class PersistentTidy(Tidy):

    """ Functions the same as the Tidy class but keeps a persistent reference
    to one Tidy document object. This increases performance slightly when
    tidying many documents in a row. It also persists all options (not just
    the base options) between runs, which could lead to unexpected behavior.
    If you plan to use different options on each run with PersistentTidy, set
    all options that could change on every call. Note that passing in unicode
    text will result in the input-encoding and output-encoding options being
    automatically set. Thread-local storage is used for the document object
    (one document per thread). """

    def __init__(self, lib_names=None):
        Tidy.__init__(self, lib_names)
        self._local = threading.local()
        self._local.doc = self._tidy.tidyCreate()

    def __del__(self):
        self._tidy.tidyRelease(self._local.doc)

    @contextmanager
    def _doc_and_sink(self):
        " Create and cleanup an error sink but use the persistent doc object "
        sink = create_sink()
        self._tidy.tidySetErrorSink(self._local.doc, sink)
        yield (self._local.doc, sink)
        destroy_sink(sink)


def tidy_document(text, options=None, keep_doc=False):
    if keep_doc:
        warnings.warn(KEEP_DOC_WARNING, DeprecationWarning, stacklevel=2)
    return get_module_tidy().tidy_document(text, options)


def tidy_fragment(text, options=None, keep_doc=False):
    if keep_doc:
        warnings.warn(KEEP_DOC_WARNING, DeprecationWarning, stacklevel=2)
    return get_module_tidy().tidy_fragment(text, options)


def get_module_tidy():
    global _tidy
    if '_tidy' not in globals():
        _tidy = Tidy()
    return _tidy


def release_tidy_doc():
    warnings.warn(KEEP_DOC_WARNING, DeprecationWarning, stacklevel=2)
