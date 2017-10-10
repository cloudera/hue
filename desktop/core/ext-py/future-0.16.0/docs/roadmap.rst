Development roadmap
===================

futurize script
---------------

1. "Safe" mode -- from Py2 to modern Py2 or Py3 to more-compatible Py3

   - Split the fixers into two categories: safe and bold
   - Safe is highly unlikely to break existing Py2 or Py3 support. The
     output of this still requires :mod:`future` imports. Examples:

      - Compatible metaclass syntax on Py3
      - Explicit inheritance from object on Py3
    
   - Bold might make assumptions about which strings on Py2 should be
     unicode strings and which should be bytestrings.

     - We should also build up a database of which standard library
       interfaces on Py2 and Py3 accept unicode strings versus
       byte-strings, which have changed, and which haven't.

2. Windows support

future package
--------------

- [Done] Add more tests for bytes ... preferably all from test_bytes.py in Py3.3.
- [Done] Add remove_hooks() and install_hooks() as functions in the
  :mod:`future.standard_library` module. (See the uprefix module for how
  to do this.)

Experimental:
- Add::

    from future import bytes_literals
    from future import new_metaclass_syntax
    from future import new_style_classes

- [Done] Maybe::

    from future.builtins import str

  should import a custom str is a Py3 str-like object which inherits from unicode and
  removes the decode() method and has any other Py3-like behaviours
  (possibly stricter casting?)

