
limitations of the ``future`` module and differences between Py2 and Py3 that are not (yet) handled
===================================================================================================

The following attributes on functions in Python 3 are not provided in Python
2.7:

__func__: see six.get_method_function()
__self__: see six.get_method_self()
__self__.__class__


Limitations of the ``futurize`` script
--------------------------------------
The ``futurize`` script is not yet mature; like ``2to3``, on which it is based,
it makes mistakes. Nevertheless, it should be useful for automatically
performing a lot of the repetitive code-substitution tasks when porting from
Py2 to Py2/3.

Some new Python 3.3 features that cause SyntaxErrors on earlier versions
are not currently handled by the ``futurize`` script. This includes:

- ``yield ... from`` syntax for generators in Py3.3

- ``raise ... from`` syntax for exceptions. (This is simple to fix
  manually by creating a temporary variable.)

Also:

- Usage of ``file('myfile', 'w')`` as a synonym for ``open`` doesn't seem
  to be converted currently.

- ``isinstance(var, basestring)`` should sometimes be converted to
  ``isinstance(var, str) or isinstance(var, bytes)``, or sometimes simply
  ``isinstance(var, str)``, depending on the context. Currently it is always
  converted to ``isinstance(var, str)``.

- Caveats with bytes indexing!::

      b'\x00'[0] != 0
      b'\x01'[0] != 1
  
  ``futurize`` does not yet wrap all byte-string literals in a ``bytes()``
  call. This is on the to-do list. See :ref:`bytes-object` for more information.


Notes
-----
- Ensure you are using new-style classes on Py2. Py3 doesn't require
  inheritance from ``object`` for this, but Py2 does. ``pasteurize``
  adds this back in automatically, but ensure you do this too
  when writing your classes, otherwise weird breakage when e.g. calling
  ``super()`` may occur.


