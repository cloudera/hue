# Copyright (c) 2010, Steve 'Ashcrow' MIlner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Platform related items.
"""

import os
import platform
import sys
import tempfile


class System(dict):
    """
    Class to make finding out system information all in one place.

    **Note**: You can not add attributes to an instance of this class.
    """

    def __init__(self):
        dict.__init__(self, {
            'architecture': platform.architecture(),
            'max_int': sys.maxint,
            'max_size': sys.maxsize,
            'max_unicode': sys.maxunicode,
            'name': platform.node(),
            'path_seperator': os.path.sep,
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_branch': platform.python_branch(),
            'python_build': platform.python_build(),
            'python_compiler': platform.python_compiler(),
            'python_implementation': platform.python_implementation(),
            'python_revision': platform.python_revision(),
            'python_version_tuple': platform.python_version_tuple(),
            'python_path': sys.path,
            'login': os.getlogin(),
            'system': platform.system(),
            'temp_directory': tempfile.gettempdir(),
            'uname': platform.uname(),
    })

    def __getattr__(self, name):
        """
        Looks in the dictionary for items **only**.

        :Parameters:
           - 'name': name of the attribute to get.
        """
        data = dict(self).get(name)
        if data == None:
            raise AttributeError("'%s' has no attribute '%s'" % (
                self.__class__.__name__, name))
        return data

    def __setattr__(self, key, value):
        """
        Setting attributes is **not** allowed.

        :Parameters:
           - `key`: attribute name to set.
           - `value`: value to set attribute to.
        """
        raise AttributeError("can't set attribute")

    def __repr__(self):
        """
        Nice object representation.
        """
        return unicode(
            "<Platform: system='%s', name='%s', arch=%s, processor='%s'>" % (
            self.system, self.name, self.architecture, self.processor))

    # Method aliases
    __str__ = __repr__
    __unicode__ = __repr__
    __setitem__ = __setattr__
