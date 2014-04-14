python-snappy
=============

Python library for the snappy compression library from Google.
This library is distributed under the New BSD License
(http://www.opensource.org/licenses/bsd-license.php).

Dependencies
============

* snappy library >= 1.0.2 (or revision 27)
  http://code.google.com/p/snappy/

* Supports Python 2.7 and Python 3

Build & Install
===============

Build:

::

  python setup.py build

Install:

::

  python setup.py install


Or install it from PyPi:

::

  pip install python-snappy

Run tests
=========

::

  nosetest test_snappy.py

Benchmarks
==========

*snappy vs. zlib*

**Compressing:**

::

  %timeit zlib.compress("hola mundo cruel!")
  100000 loops, best of 3: 9.64 us per loop

  %timeit snappy.compress("hola mundo cruel!")
  1000000 loops, best of 3: 849 ns per loop

**Snappy** is **11 times faster** than zlib when compressing

**Uncompressing:**

::

  r = snappy.compress("hola mundo cruel!")

  %timeit snappy.uncompress(r)
  1000000 loops, best of 3: 755 ns per loop

  r = zlib.compress("hola mundo cruel!")

  %timeit zlib.decompress(r)
  1000000 loops, best of 3: 1.11 us per loop

**Snappy** is **twice** as fast as zlib

Commandline usage
=================

You can invoke Python Snappy to compress or decompress files or streams from
the commandline after installation as follows

Compressing and decompressing a file:

::

  $ python -m snappy -c uncompressed_file compressed_file.snappy
  $ python -m snappy -d compressed_file.snappy uncompressed_file

Compressing and decompressing a stream:

::

  $ cat uncompressed_data | python -m snappy -c > compressed_data.snappy
  $ cat compressed_data.snappy | python -m snappy -d > uncompressed_data

You can get help by running

::

  $ python -m snappy --help


Snappy - compression library from Google (c)
 http://code.google.com/p/snappy
