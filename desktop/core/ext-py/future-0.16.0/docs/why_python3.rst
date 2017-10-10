.. _why-python3:

Why Python 3?
=============

- Python 2.7 is the final Python 2.x release. Python 3.x is the future.
  The Python ecosystem needs to consolidate. A split or schism between
  different incompatible versions is not healthy for growing the
  community.
- Function annotations
- Decimal module 100x faster. As fast as floats.
- Easier to learn. (Less cruft in language and stdlib, more consistency, better docstrings, etc.)
- Much safer handling of unicode text and encodings: fewer bugs.
- More memory efficiency (shared dict keys (PEP 412) and space-efficient
  Unicode representation (PEP 393))
- Exception chaining

Why are Unicode strings better on Python 3?
-------------------------------------------

- it is not the default string type (you have to prefix the string
  with a u to get Unicode);

- it is missing some functionality, e.g. casefold;

- there are two distinct implementations, narrow builds and wide builds;

- wide builds take up to four times more memory per string as needed;

- narrow builds take up to two times more memory per string as needed;

- worse, narrow builds have very naive (possibly even "broken")
  handling of code points in the Supplementary Multilingual Planes.

The unicode string type in Python 3 is better because:

- it is the default string type;

- it includes more functionality;

- starting in Python 3.3, it gets rid of the distinction between
  narrow and wide builds;

- which reduces the memory overhead of strings by up to a factor
  of four in many cases;

- and fixes the issue of SMP code points.

(quote from a mailing list post by Steve D'Aprano on 2014-01-17).


New features
------------

Standard library:
~~~~~~~~~~~~~~~~~

- SSL contexts in http.client
- 



Non-arguments for Python 3
==========================

- 
