About Py4J
==========

Py4J is developed by `Barthélémy Dagenais <http://www.infobart.com>`_. The
goal is to enable developers to program in Python and benefit from Python
libraries such as `lxml <http://lxml.de>`_ while being able to
reuse Java libraries and frameworks such as `Eclipse
<http://www.eclipse.org>`_. You can see Py4J as an hybrid between a glorified
Remote Procedure Call and using the Java Virtual Machine to run a Python
program.


License
=======

Py4J is distributed under the `BSD license
<https://github.com/bartdag/py4j/blob/master/LICENSE.txt>`_.


Alternatives to Py4J
====================

As opposed to `Jython <http://www.jython.org/>`_, Py4J does not execute the
Python code in the JVM so it does not need to reimplement the Python language
and developers can use any libraries supported by their Python interpreter such
as libraries written in Cython. Py4J is more focused than `JPype
<http://jpype.sourceforge.net/index.html>`_. For example, it does not attempt
to link Python threads to Java threads. JPype also uses JNI to communicate with
the JVM while Py4J uses plain old sockets, which are more portable in practice.

In terms of performance, Py4J has a bigger overhead than both of the previous
solutions because it relies on sockets, but if performance is critical to your
application, accessing Java objects from Python programs might not be the best
idea :-) If you have a particular use case that you want to speed up with Py4J,
do not hesitate to write on the mailing list or open an issue and we'll see
what we can do.
