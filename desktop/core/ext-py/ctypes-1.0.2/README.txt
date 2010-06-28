Overview

    ctypes is a ffi (Foreign Function Interface) package for Python.

    It allows to call functions exposed from dlls/shared libraries and
    has extensive facilities to create, access and manipulate simpole
    and complicated C data types transparently from Python - in other
    words: wrap libraries in pure Python.

    ctypes runs on Windows, Windows CE, MacOS X, Linux, Solaris,
    FreeBSD, OpenBSD.  It may also run on other systems, provided that
    libffi supports this platform.

    ctypes includes libffi, which is copyright Red Hat, Inc.  Complete
    license see below.


Requirements

    ctypes requires Python 2.3 or higher, since it makes intensive use
    of the new type system.

    In Python 2.5, the ctypes package is already included.


Installation

    Windows

        On Windows, it is the easiest to download the executable
        installer for your Python version and run it.

    Installation from source

        To install ctypes from source, unpack the distribution, enter
        the ctypes-x.y.z source directory, and enter

            python setup.py build

	This will build the Python extension modules.  A C compiler is
	required.

	To run the supplied tests, enter

	    python setup.py test

	To install ctypes, enter

            python setup.py install --help

        to see the avaibable options, and finally

	    python setup.py install [options]


    Windows CE

        Required software to build the _ctypes.pyd extension module
        for Windows CE (all these are free downloads):

	- Embedded Visual C 4.0 with service pack 2 (3?, 4?)

	- Pocket PC 2003 SDK

	- The Python 2.3 or 2.4 windows CE development files: include
	files, header files.

	Open the wince\_ctypes.vcw project file with embedded visual C
	4.0.  Select "POCKET PC 2003", "Win32 (WCE ARMV4) Release",
	and "POCKET PC 2003 Device" in the comboboxes.

	From the menu, select Tools->Options->Directories, and add
	these directories:

	    Include files: add c:\Python-2.4.3-wince-dev\INCLUDE
	    Library files: add c:\Python-2.4.3-wince-dev\LIB

	Right click '_ctypes files' in the FileView, select
	'Settings', then the 'Debug' tab.

	Enter '\Program Files\Python24' in the 'Download directory'
	box.  Do the same for the '_ctypes_test' project.

	Now you can connect your pocket PC, build the projects in
	visual C, and both _ctypes.pyd and _ctypes_test.pyd should be
	downloaded automatically to your device.


ctypes license

  Copyright (c) 2000, 2001, 2002, 2003, 2004, 2005, 2006 Thomas Heller

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation files
  (the "Software"), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge,
  publish, distribute, sublicense, and/or sell copies of the Software,
  and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.

libffi license

  libffi - Copyright (c) 1996-2003  Red Hat, Inc.

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation files
  (the ``Software''), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge,
  publish, distribute, sublicense, and/or sell copies of the Software,
  and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED ``AS IS'', WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT.  IN NO EVENT SHALL CYGNUS SOLUTIONS BE LIABLE FOR
  ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
