# Copyright 2009 Jason Stitt
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

from distutils.core import setup

longdesc = """\
0.2.0: Works on Windows! See documentation for available DLL download
locations. Documentation rewritten and expanded.

`PyTidyLib`_ is a Python package that wraps the `HTML Tidy`_ library. This
allows you, from Python code, to "fix" invalid (X)HTML markup. Some of the
library's many capabilities include:

* Clean up unclosed tags and unescaped characters such as ampersands
* Output HTML 4 or XHTML, strict or transitional, and add missing doctypes
* Convert named entities to numeric entities, which can then be used in XML
  documents without an HTML doctype.
* Clean up HTML from programs such as Word (to an extent)
* Indent the output, including proper (i.e. no) indenting for ``pre`` elements,
  which some (X)HTML indenting code overlooks.

Small example of use
====================

The following code cleans up an invalid HTML document and sets an option::

    from tidylib import tidy_document
    document, errors = tidy_document('''<p>f&otilde;o <img src="bar.jpg">''',
      options={'numeric-entities':1})
    print document
    print errors
    
Docs
====

Documentation is shipped with the source distribution and is available at
the `PyTidyLib`_ web page.

.. _`HTML Tidy`: http://tidy.sourceforge.net/
.. _`PyTidyLib`: http://countergram.com/open-source/pytidylib/
"""

VERSION = "0.2.1"

setup(
    name="pytidylib",
    version=VERSION,
    description="Python wrapper for HTML Tidy (tidylib)",
    long_description=longdesc,
    author="Jason Stitt",
    author_email="js@jasonstitt.com",
    url="http://countergram.com/open-source/pytidylib/",
    download_url="http://cloud.github.com/downloads/countergram/pytidylib/pytidylib-%s.tar.gz" % VERSION,
    packages=['tidylib'],
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Topic :: Utilities',
          'Topic :: Text Processing :: Markup :: HTML',
          'Topic :: Text Processing :: Markup :: XML',
          ],
    )

