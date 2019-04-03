.. _func_annotations:

Function annotations
====================

Function annotations are a piece of syntax introduced in Python 3.0 that was
not backported to Python 2.x. (See PEP 3107:
http://www.python.org/dev/peps/pep-3107/). They cause Python 2 to raise a
SyntaxError.

To rewrite Python 3 code with function annotations to be compatible with both
Python 3 and Python 2, you can replace the annotation syntax with a dictionary
called ``__annotations__`` as an attribute on your functions. For example, code
such as this::

    def _parse(self, filename: str, dir='.') -> list:
        pass

can be re-expressed like this::

    def _parse(self, filename, dir='.'):
        pass
    _parse.__annotations__ = {'filename': str, 'return': list}

As described in PEP 3107, the annotation for a function's return value
corresponds to the ``'return'`` key in the dictionary.

(Note that PEP 3107 describes annotations as belonging to a
``func_annotations`` attribute. This attribute was renamed in Python 3.2 to
``__annotations__``.)

Be aware that some libraries that consume function annotations, such as
`Reticulated <https://github.com/mvitousek/reticulated>`_, have their own
semantics for supporting earlier Python versions, such as decorators. If you
are using such a library, please use its own mechanism for providing
compatibility with earlier Python versions, rather than the generic equivalent
above.
