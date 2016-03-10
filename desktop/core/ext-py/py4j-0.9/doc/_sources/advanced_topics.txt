Advanced Topics
===============

Accessing Java collections and arrays from Python
-------------------------------------------------

Java collections are automatically mapped to Python collections so that
standard Python operations such as slicing work on Java collections. Here is
the mapping of the collection:

=================== ====================== ==========================================================
Java Collection     Python Collection      Py4J Implementation
=================== ====================== ==========================================================
Array               Sequence [#arraynote]_ :class:`JavaArray <py4j.java_collections.JavaArray>`
java.util.List      MutableSequence        :class:`JavaList <py4j.java_collections.JavaList>`
java.util.Set       MutableSet             :class:`JavaSet <py4j.java_collections.JavaSet>`
java.util.Map       MutableMapping         :class:`JavaMap <py4j.java_collections.JavaMap>`
java.util.Iterator  *Iterator Protocol*    :class:`JavaIterator <py4j.java_collections.JavaIterator>`
=================== ====================== ==========================================================

.. [#arraynote] Py4J allows elements to be modified (like a real Java array), which is not the case of true
   immutable sequences like tuples.

Java methods are still accessible when using the Python version of a Java
collection. Here are some usage examples for each collection class. These
examples do not cover the entire API.

It is possible to change this default mapping by registering an output
converter with :func:`register_output_converter
<py4j.protocol.register_output_converter>`

Array
^^^^^

::

  >>> gateway = JavaGateway()
  >>> int_class = gateway.jvm.int
  >>> int_array = gateway.new_array(int_class,2)
  >>> int_array[0] = 1
  >>> int_array[1] = 2
  >>> int_array[0]
  1
  >>> int_array[2]
  Traceback (most recent call last):
  ...
  IndexError: list index out of range
  >>> for i in int_array:
  ...     print(i)
  ...
  1
  2
  >>> sarray = gateway.new_array(gateway.jvm.java.lang.String,2,3)
  >>> len(sarray)
  2
  >>> len(sarray[0])
  3
  >>> sarray[0][1] = 'hello'
  >>> sarray[0][1]
  u'hello'
  >>> sarray[0][0] == None
  True


List
^^^^

::

  >>> l = gateway.jvm.java.util.ArrayList()
  >>> l.append(1) # calling Python interface
  >>> l.add('hello') # calling Java interface
  >>> for elem in l:
  ...     print elem
  ...
  1
  hello
  >>> l[0] = 2
  >>> l.append(3)
  >>> str(l)
  "[2, u'hello', 3]"
  >>> l2 = l[0:-1]
  >>> l2[0] = 999
  >>> l
  [2, u'hello', 3]
  >>> l2 # l2 is a copy of l and not a view so a change in l2 does not affect l
  [999, u'hello']
  >>> del(l[0])
  >>> l
  [u'hello', 3]


Set
^^^

::

  >>> s = gateway.jvm.java.util.HashSet()
  >>> s.add(1)
  >>> s.add('hello')
  >>> s
  set([1, u'hello'])
  >>> 1 in s
  True
  >>> s.remove(u'hello')
  >>> s
  set([1])


Map
^^^

::

  >>> m = gateway.jvm.java.util.HashMap()
  >>> m["a"] = 0
  >>> m.put("b",1)
  >>> m
  {u'a': 0, u'b': 1}
  >>> u"b" in m
  True
  >>> del(m["a"])
  >>> m
  {u'b': 1}
  >>> m["c"] = 2
  >>> for key in m:
  ...     print("%s:%i" % (key,m[key]))
  ...
  b:1
  c:2


Byte array (byte[])
-------------------

Since version 0.7, Py4J automatically passes Java byte array (i.e., `byte[]`)
by value and convert them to Python bytearray (2.x) or bytes (3.x) and vice
versa. The rationale is that byte array are often used for binary processing
and are often immutable: a program reads a series of byte from a data source
and interpret it (or transform it into another byte array).

Prior to 0.7, a Python program could interact with a Java byte[] but each
access to a byte required a call between the Python and the Java interpreter
(i.e., the Python program only had a reference to the array).

In summary:

* If from Java, you return a byte[], Py4J will convert the byte[] to a
  bytearray (Python 2.x) or bytes (Python 3.x) variable in Python.

* If from Python, you pass a bytearray or bytes variable to the Java side,
  Py4J will convert it to a byte[].

* If you pass a byte[] from Java to Python, both arrays are disconnected: a
  change to the array on one side will not be reflected on the other side.

* If you want to pass an array by reference, use a `Byte[]` instead of a
  `byte[]` or you can use  `Bytes.asList
  <http://guava-libraries.googlecode.com/svn/trunk/javadoc/com/google/common/primitives/Bytes.html#asList(byte...)>`_
  from `Guava <http://code.google.com/p/guava-libraries/>`_ to obtain a list
  backed by a byte array.


Implementing Java interfaces from Python (callback)
---------------------------------------------------

Since version 0.3, Py4J allows Python classes to implement Java interfaces so
that the JVM can call back Python objects.  In the following example, you will
play the role of a Mad Scientist :sup:`TM` and you will create a Java program
that invokes an operator with two or three random integers. The operators will
be implemented by a Python class.

Here is the code of the main Java program:

.. code-block:: java

  package py4j.examples;

  import java.util.ArrayList;
  import java.util.List;
  import java.util.Random;

  import py4j.GatewayServer;

  public class OperatorExample {

	  // To prevent integer overflow
	  private final static int MAX = 1000;

	  public List<Integer> randomBinaryOperator(Operator op) {
		  Random random = new Random();
		  List<Integer> numbers = new ArrayList<Integer>();
		  numbers.add(random.nextInt(MAX));
		  numbers.add(random.nextInt(MAX));
		  numbers.add(op.doOperation(numbers.get(0), numbers.get(1)));
		  return numbers;
	  }

	  public List<Integer> randomTernaryOperator(Operator op) {
		  Random random = new Random();
		  List<Integer> numbers = new ArrayList<Integer>();
		  numbers.add(random.nextInt(MAX));
		  numbers.add(random.nextInt(MAX));
		  numbers.add(random.nextInt(MAX));
		  numbers.add(op.doOperation(numbers.get(0), numbers.get(1), numbers.get(2)));
		  return numbers;
	  }

	  public static void main(String[] args) {
		  GatewayServer server = new GatewayServer(new OperatorExample());
		  server.start();
	  }

  }


The program has a main method starting a `GatewayServer`. The entry point, a
`OperatorExample` instance, offers two methods that take as a parameter an
`Operator` instance. Each method calls the operator with two or three random
integers and save the integers and the result in a list. Here is the
declaration of `Operator`:


.. code-block:: java

  package py4j.examples;

  public interface Operator {

	  public int doOperation(int i, int j);

	  public int doOperation(int i, int j, int k);

  }


Now, because the Mad Scientist :sup:`TM` is, well, mad, he wants to define an
Operator in Python. Here is his little Python program:

::

  from py4j.java_gateway import JavaGateway

  class Addition(object):
      def doOperation(self, i, j, k = None):
	  if k == None:
	      return i + j
	  else:
	      return i + j + k

      class Java:
	  implements = ['py4j.examples.Operator']

  if __name__ == '__main__':
      # The callback server parameters is optional, but it tells to start the
      # callback server automatically.
      gateway = JavaGateway(CallbackServerParameters())
      operator = Addition()
      numbers = gateway.entry_point.randomBinaryOperator(operator)
      print(numbers)
      numbers = gateway.entry_point.randomTernaryOperator(operator)
      print(numbers)
      gateway.shutdown()


The `Addition` class is a standard Python class that has one method,
`doOperation`. The signature of the method contains two parameters and an
optional third parameter: this maps with the two overloaded methods in the
`Operator` Java interface. Each method implementing an overloaded method in a
Java interface should accept all possible combinations of parameters,
otherwise, an exception will be thrown if the Java program tries to call an
unsupported method.

Py4J recognizes that the `Addition` class implements a Java interface because
it declares an internal class called `Java`, which has a member named
`implements`. This member is a list of string representing the fully qualified
name of implemented Java interfaces.

Finally, the Python program contains a main method that starts a gateway,
initializes an Addition operator and sends it to the `OperatorExample` instance
on the Java side. Py4J takes care of creating the necessary proxies: the
`doOperation` method of the `Addition` class is called in the Java VM, but the
method is executed in the Python interpreter.

Note that to enable the Python program to receive callbacks, the JavaGateway
instance must be created with `start_callback_server=True`. Otherwise, the
callback server must be started manually by calling
:func:`restart_callback_server
<py4j.java_gateway.JavaGateway.restart_callback_server>`

.. warning::

   Python classes can only implement Java interfaces. Abstract or concrete
   classes are not supported because Java does not natively support dynamic
   proxies for classes. Extending classes may be supported in future releases
   of Py4J.

   As a workaround, a subclass of the abstract class could be created on the
   Java side. The methods of the subclass would call the methods of a custom
   interface that a Python class could implement.


.. warning::

   If you want to implement an interface declared in a class (i.e., an
   internal class), you need to prefix the name of the interface with
   a dollar sign. For example, if the interface `Operator` is declared
   in the class `package1.MyClass`, you will have to write:

   `implements = ['package1.MyClass$Operator']`


.. _collections_conversion:

Converting Python collections to Java Collections
-------------------------------------------------

If you try to pass a Python collection to a method that expects a Java
collection, an error will be thrown:

::

  >>> my_list = [3,2,1]
  >>> gateway.jvm.java.util.Collections.sort(my_list)
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "py4j/java_gateway.py", line 347, in __call__
      args_command = ''.join([get_command_part(arg, self.pool) for arg in new_args])
    File "py4j/protocol.py", line 195, in get_command_part
      command_part = REFERENCE_TYPE + parameter._get_object_id()
  AttributeError: 'list' object has no attribute '_get_object_id'


You can explicitly convert Python collections using one of the following
converter located in the `py4j.java_collections` module: `SetConverter`,
`MapConverter`, `ListConverter`.

::

  >>> from py4j.java_collections import SetConverter, MapConverter, ListConverter
  >>> java_list = ListConverter().convert(my_list, gateway._gateway_client)
  >>> gateway.jvm.java.util.Collections.sort(java_list)
  >>> java_list
  [1, 2, 3]
  >>> my_list
  [3, 2, 1]

Note that the Python list is totally disconnected from the Java list. The Java
List is actually a copy. You can also ask Py4J to automatically convert Python
collections to Java Collections when calling a Java method: just set
``auto_convert=True`` when creating a `JavaGateway`:

::

  >>> gateway = JavaGateway(GatewayParameters(auto_convert=True))
  >>> my_list
  [3, 2, 1]
  >>> gateway.jvm.java.util.Collections.sort(my_list)
  >>> my_list # The python list is not sorted!
  [3, 2, 1]
  >>> gateway.jvm.java.util.Collections.frequency(my_list,2)
  1

Again, note that my_list is not sorted because when calling
`Collections.sort()`, Py4J only makes a copy of the Python list. Still, a copy
can be useful if you do not expect the list to be modified by the Java method
like in the call to ``frequency()``.

**Order of Automatic Conversion**

When ``auto_convert=True``, Py4J will attempt to automatically convert Python
objects that are not an instance of ``basestring`` or ``JavaObject``. By
default, Py4J performs the following checks and conversions:

1. If the Python object is an instance of `collections.Set`, it is converted to
   a `HashSet`.
2. If the object has the methods `keys()` and `__getitem__`, it is converted to
   a `HashMap`
3. If the object is iterable, it is converted to an `ArrayList`.
4. Otherwise, standard Py4J primitive type conversion is attempted (e.g., bool to boolean).

It is possible to add custom converters by calling
:func:`register_input_converter()
<py4j.protocol.register_input_converter>`. Look at the source code of the
default converters for an example. Note that automatic conversion makes calling
Java methods slightly less efficient because in the worst case, Py4J needs to
go through all registered converters for all parameters. This is why automatic
conversion is disabled by default.


.. _py4j_exceptions:

Py4J Exceptions
---------------

Py4J can raise three exceptions on the Python side:

* :class:`Py4JJavaError <py4j.protocol.Py4JJavaError>`. This exception is
  raised when an exception occurs in the Java client code. For example, if you
  try to pop an element from an empty stack. The instance of the Java exception
  thrown is stored in the `java_exception` member.

* :class:`Py4JNetworkError <py4j.protocol.Py4JNetworkError>`. This exception is
  raised when a problem occurs during network transfer (e.g., connection lost).

* :class:`Py4JError <py4j.protocol.Py4JError>`. This exception is raised when
  any other error occurs such as when the client program tries to access an
  object that no longer exists on the Java side.

Both `Py4JJavaError` and `Py4JNetworkError` inherits from `Py4JError` so it is
possible to catch all related Py4J errors with one except clause:

.. code-block:: python

  try:
    java_object.doSomething()
  except Py4JError:
    traceback.print_exc()

If a Py4J Exception wraps another exception, the original exception will be
available in the ``clause`` field.


.. code-block:: python

  try:
    java_object.doSomething()
  except Py4JError as e:
    if e.cause:
        print(e.cause)


.. _jvm_views:

Importing packages with JVM Views
---------------------------------

Py4J allows you to import packages so that you don't have to type the fully
qualified name of the classes you want to instantiate. The `java.lang` package
is always automatically imported.

::

  >>> from py4j.java_gateway import JavaGateway
  >>> gateway = JavaGateway()
  >>> from py4j.java_gateway import java_import
  >>> java_import(gateway.jvm,'java.util.*')
  >>> jList = gateway.jvm.ArrayList()
  >>> jMap = gateway.jvm.HashMap()
  >>> gateway.jvm.java.lang.String("a")
  u'a'
  >>> gateway.jvm.String("a")
  u'a'

As opposed to Java where import statements do not cross compilation units (java
source files), the jvm instance can be shared across multiple Python modules: in
other words, import statements are global.

The recommended way to use import statements is to use one :class:`JVMView
<py4j.java_gateway.JVMView>` instance per Python module. Here is an example on
how to create and use a `JVMView`:

::

  >>> module1_view = gateway.new_jvm_view()
  >>> module2_view = gateway.new_jvm_view()
  >>> jList2 = module1_view.ArrayList()
  Py4JError: Trying to call a package.
  ...
  >>> java_import(module1_view,'java.util.ArrayList')
  >>> jList2 = module1_view.ArrayList()
  >>> jList3 = module2_view.ArrayList()
  Py4JError: Trying to call a package.
  ...

As you can see from the previous example, the import of `java.util.ArrayList`
only affects `module1_view`.

.. note::
  In fact, the `gateway.jvm` member is also an instance of :class:`JVMView
  <py4j.java_gateway.JVMView>`. It is automatically created when a gateway is
  initialized.

.. _eclipse_features:

Using Py4J with Eclipse
-----------------------

Py4J can be used with Eclipse like any normal Java program. A plug-in needs to
instantiate and start a GatewayServer. By default, the GatewayServer will only
be able to access the classes declared in the plug-in or one of its
dependencies.

Unless they have specific needs, users are encouraged to use the Eclipse
plug-ins provided by Py4J available on the following update site:

``http://eclipse.py4j.org/``

The first plug-in, `net.sf.py4j`, provides all the Py4J Java classes such as
`GatewayServer`. The plug-in comes with the source and the javadoc. The plug-in
also declares a `global` buddy policy which allows the `GatewayServer` to
access any class declared in any plug-in loaded with Eclipse.

The second plug-in, `net.sf.py4j.defaultserver`, instantiates a GatewayServer
and starts it as soon as Eclipse is started (no lazy loading). The ports used
by the default server can be changed in the Py4J Preferences page. The server
is also accessible at runtime:


.. code-block:: java

  import net.sf.py4j.defaultserver.DefaultServerActivator;

  ...

  GatewayServer server = DefaultServerActivator.getDefault().getServer();


Here is a short example of what you could do with Py4J and Eclipse:

::

  >>> from py4j.java_gateway import JavaGateway, java_import
  >>> gateway = JavaGateway()
  >>> jvm = gateway.jvm
  >>> java_import(jvm, 'org.eclipse.core.resources.*')
  >>> workspace_root = jvm.ResourcesPlugin.getWorkspace().getRoot()
  >>> gateway.help(workspace_root,'*Projects*')
  Help on class WorkspaceRoot in package org.eclipse.core.internal.resources:

  WorkspaceRoot extends org.eclipse.core.internal.resources.Container implements org.eclipse.core.resources.IWorkspaceRoot {
  |
  |  Methods defined here:
  |
  |  getProjects() : IProject[]
  |
  |  getProjects(int) : IProject[]
  |
  |  ------------------------------------------------------------
  |  Fields defined here:
  |
  |  ------------------------------------------------------------
  |  Internal classes defined here:
  |
  }
  >>> project_names = [project.getName() for project in workspace_root.getProjects()]
  >>> print(project_names)
  [u'test2', u'testplugin', u'testplugin2']

Support for Eclipse was introduced in Py4J 0.5 and more features will be added
in the future.


.. _adv_memory:

Py4J Memory model
-----------------

**Java objects sent to the Python side**

Every time a Java object is sent to the Python side, a reference to the object
is kept on the Java side (in the Gateway class). Once the object is garbage
collected on the Python VM (reference count == 0), the reference is removed on
the Java VM: if this was the last reference, the object will likely be garbage
collected too. When a gateway is shut down, the remaining references are also
removed on the Java VM.

Because Java objects on the Python side are involved in a circular reference
(:class:`JavaObject <py4j.java_gateway.JavaObject>` and :class:`JavaMember
<py4j.java_gateway.JavaMember>` reference each other), these objects are not
immediately garbage collected once the last reference to the object is removed
(but they are guaranteed to be eventually collected **if the Python garbage
collector runs before the Python program exits**).

In doubt, users can always call the :func:`detach
<py4j.java_gateway.JavaGateway.detach>` function on the Python gateway to
explicitly delete a reference on the Java side. A call to `gc.collect()` also
usually works.

**Python objects sent to the Java side (callback)**

Every time a Python object is sent to the Java side, a reference to this object
is kept on the Python side (by a :class:`PythonProxyPool
<py4j.java_callback.PythonProxyPool>`). Once a python object is garbage
collected on the Java side, a message is sent to the Python side to remove the
reference to the Python object. When a gateway is shut down, the remaining
references are removed from the Python VM.

Unfortunately, there is no guarantee that the garbage collection message will
ever be sent to the Python side (it usually works on Sun/Oracle VM). It might
thus be necessary to manually remove the reference to the Python objects. Some
helper functions will be developed in the future, but it is unlikely that
garbage collection will be guarenteed because of the specifications of Java
finalizers (which are surprisingly worse than Python finalizer strategies).

.. _adv_threading:

Py4J Threading and connection model
-----------------------------------

Py4J allocates one thread per connection. The design of Py4j is symmetrical on
the Python and Java sides. A Python GatewayClient communicates with the Java
GatewayServer and is then associated with a GatewayConnection. A Java
CallbackClient (for callbacks) communicates with the Python CallbackServer and
is then associated with a CallbackConnection. A connection runs in the calling
thread.

And now, for the details:

**On the Python side: calling Java**

Py4J on the Python side does not explicitly create a thread to call Java
methods. When a method is called, a connection to the Java GatewayServer is
established in the calling thread. If multiple threads are calling Java methods
concurrently, Py4J will ensure that each thread has its own connection by
requesting more connections.

To be extra clear: if you only call Java, Py4J on the Python side will never
create a thread.

To be extra extra clear: Py4J is thread-safe so if you use a JavaGateway from
multiple threads that **you created**, Py4J will make manage the network
resources appropriately.

**On the Python side: receiving callbacks from Java**

Py4J explicitly creates a thread to run the
:class:`CallbackServer <py4j.java_gateway.CallbackServer>`, which accepts
callback connection requests, and a thread for each callback connection
request. As long as there is no concurrent callback from the Java side, the
same callback connection/thread will be used.

These threads are necessary to prevent deadlocks. For example, if we only had a
single thread to handle callbacks from Java, Py4J would deadlock as soon as it
would encounter an indirect recursion between Java and Python functions. Early
versions of Py4J made this mistake :-)

**On the Java side: receiving calls from Python**

Py4J explicitly creates a thread to run the GatewayServer, which accepts
connection requests (from a GatewayClient), and a thread for each connection
request. As long as there is no concurrent call from the Python side, the same
connection/thread will be used.

**On the Java side: calling back Python**

Py4J on the Java side does not explicitly create a thread to make a callback to
a Python object. When a callback is called, a connection to the CallbackServer
is established in the calling thread. If **you created** multiple threads in
Java to call back Python concurrently, Py4J will ensure that each thread has
its own CallbackConnection.
