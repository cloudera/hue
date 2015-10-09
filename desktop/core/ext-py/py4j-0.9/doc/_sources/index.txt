.. Py4J documentation master file, created by
   sphinx-quickstart on Thu Dec 10 15:12:43 2009.

Welcome to Py4J
===============

Py4J enables Python programs running in a Python interpreter to dynamically
access Java objects in a Java Virtual Machine. Methods are called as if the
Java objects resided in the Python interpreter and Java collections can be
accessed through standard Python collection methods. Py4J also enables Java
programs to call back Python objects. Py4J is distributed under the `BSD
license <https://github.com/bartdag/py4j/blob/master/LICENSE.txt>`_.

Here is a brief example of what you can do with Py4J. The following Python
program creates a `java.util.Random` instance from a JVM and calls some of its
methods. It also accesses a custom Java class, `AdditionApplication` to add the
generated numbers.

::

  >>> from py4j.java_gateway import JavaGateway
  >>> gateway = JavaGateway()                   # connect to the JVM
  >>> random = gateway.jvm.java.util.Random()   # create a java.util.Random instance
  >>> number1 = random.nextInt(10)              # call the Random.nextInt method
  >>> number2 = random.nextInt(10)
  >>> print(number1,number2)
  (2, 7)
  >>> addition_app = gateway.entry_point        # get the AdditionApplication instance
  >>> addition_app.addition(number1,number2)    # call the addition method
  9

This is the Java program that was executing at the same time (no code was
generated and no tool was required to run these programs). The
`AdditionApplication app` instance is the `gateway.entry_point` in the
previous code snippet. Note that the Java program must be started before
executing the Python code above. In other words, the Py4J does not start a
JVM.

.. code-block:: java

  public class AdditionApplication {

    public int addition(int first, int second) {
      return first + second;
    }

    public static void main(String[] args) {
      AdditionApplication app = new AdditionApplication();
      // app is now the gateway.entry_point
      GatewayServer server = new GatewayServer(app);
      server.start();
    }
  }


Support & Resources
===================

* Take a look at the tutorial :doc:`getting_started`.
* Browse the :doc:`contents` or the :doc:`faq`.
* Ask a question on the `mailing list
  <https://groups.google.com/a/py4j.org/forum/#!forum/py4j/join>`_.
* Look at the `roadmap <https://github.com/bartdag/py4j/milestones>`_.

News
====

* **July 25th 2015** - Py4J 0.9 has been released. See the :doc:`changelog`
  for more details about the bug fixes. Py4j has moved away from sourcefoge
  and is now hosted on `py4j.org <https://www.py4j.org/>`_ and it has a new
  mailing list.

* **July 27th 2014** - Py4J 0.8.2 has been released. See the :doc:`changelog`
  for more details about the bug fixes.

* **December 26th 2013** - Py4J 0.8.1 has been released. See the
  :doc:`changelog` for more details about the new features.

* **June 14th 2013** - Py4J 0.8 has been released. See the :doc:`changelog`
  for more details about the new features.

* **June 2nd 2011** - Py4J 0.7 has been released. See the :doc:`changelog` for
  more details about the new features.

* **February 17th 2011** - Py4J 0.6 has been released. See the
  :doc:`changelog` for more details about the new features.

* **October 30th 2010** - Py4J 0.5 has been released. See the :doc:`changelog`
  for more details about the new features.

* **September 19th 2010** - Py4J 0.4 has been released. See the
  :doc:`changelog` for more details about the new features.

* **April 27th 2010** - Py4J 0.3 has been released. See the :doc:`changelog`
  for more details about the new features!

* **February 11th 2010** - Py4J 0.2 has been released. See the
  :doc:`changelog` for more details about all the new features that found
  their way in the latest release!

* **December 23rd 2009** - Py4J 0.1 has been released. Rejoice!

* **December 11th 2009** - Py4J is still in the planning phase, but the code
  currently works for basic scenarios. A release and a tutorial should be
  available in the following weeks.
