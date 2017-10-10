.. _bind-method:

Binding a method to a class
---------------------------

Python 2 draws a distinction between bound and unbound methods, whereas
in Python 3 this distinction is gone: unbound methods have been removed
from the language. To bind a method to a class compatibly across Python
3 and Python 2, you can use the :func:`bind_method` helper function::

    from future.utils import bind_method
    
    class Greeter(object):
        pass
    
    def greet(self, message):
        print(message)

    bind_method(Greeter, 'greet', greet)

    g = Greeter()
    g.greet('Hi!')


On Python 3, calling ``bind_method(cls, name, func)`` is equivalent to
calling ``setattr(cls, name, func)``. On Python 2 it is equivalent to::
    
    import types
    setattr(cls, name, types.MethodType(func, None, cls))
