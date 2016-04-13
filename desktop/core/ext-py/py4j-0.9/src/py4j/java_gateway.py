# -*- coding: UTF-8 -*-
"""Module to interact with objects in a Java Virtual Machine from a
Python Virtual Machine.

Variables that might clash with the JVM start with an underscore
(Java Naming Convention do not recommend to start with an underscore
so clashes become unlikely).

Created on Dec 3, 2009

:author: Barthelemy Dagenais
"""
from __future__ import unicode_literals, absolute_import

from collections import deque
import logging
import os
from pydoc import pager
import select
import socket
from subprocess import Popen, PIPE
import sys
from threading import Thread, RLock
import weakref

from py4j.compat import (
    range, hasattr2, basestring, CompatThread, Queue)
from py4j.finalizer import ThreadSafeFinalizer
from py4j import protocol as proto
from py4j.protocol import (
    Py4JError, Py4JNetworkError, escape_new_line, get_command_part,
    get_return_value, is_error, register_output_converter, smart_decode)
from py4j.version import __version__


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

null_handler = NullHandler()
logging.getLogger("py4j").addHandler(null_handler)
logger = logging.getLogger("py4j.java_gateway")

BUFFER_SIZE = 4096
DEFAULT_ADDRESS = "127.0.0.1"
DEFAULT_PORT = 25333
DEFAULT_PYTHON_PROXY_PORT = 25334
DEFAULT_CALLBACK_SERVER_ACCEPT_TIMEOUT = 5
PY4J_SKIP_COLLECTIONS = "PY4J_SKIP_COLLECTIONS"
PY4J_TRUE = set(["yes", "y", "t", "true"])


def deprecated(name, last_version, use_instead="", level=logging.DEBUG,
               raise_exc=False):
    if not use_instead:
        msg = "{0} is deprecated and will be removed in version {1}"\
            .format(name, last_version)
    else:
        msg = "{0} is deprecated and will be removed in version {1}. "\
            "Use {2} instead."\
            .format(name, last_version, use_instead)
    logger.log(level, msg)
    if raise_exc:
        raise DeprecationWarning(msg)


def java_import(jvm_view, import_str):
    """Imports the package or class specified by `import_str` in the
    jvm view namespace.

    :param jvm_view: The jvm_view in which to import a class/package.
    :import_str: The class (e.g., java.util.List) or the package
                 (e.g., java.io.*) to import
    """
    gateway_client = jvm_view._gateway_client
    command = proto.JVMVIEW_COMMAND_NAME + proto.JVM_IMPORT_SUB_COMMAND_NAME +\
        jvm_view._id + "\n" + escape_new_line(import_str) + "\n" +\
        proto.END_COMMAND_PART
    answer = gateway_client.send_command(command)
    return_value = get_return_value(answer, gateway_client, None, None)
    return return_value


def find_jar_path():
    """Tries to find the path where the py4j jar is located.
    """
    paths = []
    jar_file = "py4j{0}.jar".format(__version__)
    paths.append(jar_file)
    paths.append(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "../../../py4j-java/" + jar_file))
    paths.append(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "../share/py4j/" + jar_file))
    paths.append("../../../current-release/" + jar_file)
    paths.append(os.path.join(sys.prefix, "share/py4j/" + jar_file))

    for path in paths:
        if os.path.exists(path):
            return path
    return ""


def launch_gateway(port=0, jarpath="", classpath="", javaopts=[],
                   die_on_exit=False, redirect_stdout=None,
                   redirect_stderr=None, daemonize_redirect=False):
    """Launch a `Gateway` in a new Java process.

    The redirect parameters accept file-like objects, Queue, or deque. When
    text lines are sent to the stdout or stderr of the child JVM, these lines
    are redirected to the file-like object (``write(line)``), the Queue
    (``put(line)``), or the deque (``appendleft(line)``).

    The text line will contain a newline character.

    Only text output is accepted on stdout and stderr. If you wish to
    communicate with the child JVM through bytes, you need to create your own
    helper function.

    :param port: the port to launch the Java Gateway on.  If no port is
        specified then an ephemeral port is used.
    :param jarpath: the path to the Py4J jar.  Only necessary if the jar
        was installed at a non-standard location or if Python is using
        a different `sys.prefix` than the one that Py4J was installed
        under.
    :param classpath: the classpath used to launch the Java Gateway.
    :param javaopts: an array of extra options to pass to Java (the classpath
        should be specified using the `classpath` parameter, not `javaopts`.)
    :param die_on_exit: if `True`, the Java gateway process will die when
        this Python process exits or is killed.
    :param redirect_stdout: where to redirect the JVM stdout. If None (default)
        stdout is redirected to os.devnull. Otherwise accepts a
        file descriptor, a queue, or a deque. Will send one line at a time
        to these objects.
    :param redirect_stderr: where to redirect the JVM stdout. If None (default)
        stderr is redirected to os.devnull. Otherwise accepts a
        file descriptor, a queue, or a deque. Will send one line at a time to
        these objects.
    :param daemonize_redirect: if True, the consumer threads will be daemonized
        and will not prevent the main Python process from exiting. This means
        the file descriptors (stderr, stdout, redirect_stderr, redirect_stdout)
        might not be properly closed. This is not usually a problem, but the
        default is conservatively set to False.

    :rtype: the port number of the `Gateway` server.
    """
    if not jarpath:
        jarpath = find_jar_path()

    # Fail if the jar does not exist.
    if not os.path.exists(jarpath):
        raise Py4JError("Could not find py4j jar at {0}".format(jarpath))

    # Launch the server in a subprocess.
    classpath = os.pathsep.join((jarpath, classpath))
    command = ["java", "-classpath", classpath] + javaopts + \
              ["py4j.GatewayServer"]
    if die_on_exit:
        command.append("--die-on-broken-pipe")
    command.append(str(port))
    logger.debug("Launching gateway with command {0}".format(command))

    # stderr redirection
    if redirect_stderr is None:
        stderr = open(os.devnull, "w")
    elif isinstance(redirect_stderr, Queue) or\
            isinstance(redirect_stderr, deque):
        stderr = PIPE
    else:
        stderr = redirect_stderr
        # we don't need this anymore
        redirect_stderr = None

    # stdout redirection
    if redirect_stdout is None:
        redirect_stdout = open(os.devnull, "w")

    proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=stderr,
                 close_fds=True)

    # Determine which port the server started on (needed to support
    # ephemeral ports)
    _port = int(proc.stdout.readline())

    # Start consumer threads so process does not deadlock/hangs
    OutputConsumer(
        redirect_stdout, proc.stdout, daemon=daemonize_redirect).start()
    if redirect_stderr is not None:
        OutputConsumer(
            redirect_stderr, proc.stderr, daemon=daemonize_redirect).start()
    ProcessConsumer(proc, [redirect_stdout], daemon=daemonize_redirect).start()

    return _port


def get_field(java_object, field_name):
    """Retrieves the field named `field_name` from the `java_object`.

    This function is useful when `auto_field=false` in a gateway or
    Java object.

    :param java_object: the instance containing the field
    :param field_name: the name of the field to retrieve
    """
    command = proto.FIELD_COMMAND_NAME + proto.FIELD_GET_SUBCOMMAND_NAME +\
        java_object._target_id + "\n" + field_name + "\n" +\
        proto.END_COMMAND_PART
    answer = java_object._gateway_client.send_command(command)

    if answer == proto.NO_MEMBER_COMMAND or is_error(answer)[0]:
        raise Py4JError("no field {0} in object {1}".format(
            field_name, java_object._target_id))
    else:
        return get_return_value(
            answer, java_object._gateway_client, java_object._target_id,
            field_name)


def set_field(java_object, field_name, value):
    """Sets the field named `field_name` of `java_object` to `value`.

    This function is the only way to set a field because the assignment
    operator in Python cannot be overloaded.

    :param java_object: the instance containing the field
    :param field_name: the name of the field to set
    :param value: the value to assign to the field
    """

    command_part = get_command_part(
        value,
        java_object._gateway_client.gateway_property.pool)

    command = proto.FIELD_COMMAND_NAME + proto.FIELD_SET_SUBCOMMAND_NAME +\
        java_object._target_id + "\n" + field_name + "\n" +\
        command_part + "\n" + proto.END_COMMAND_PART

    answer = java_object._gateway_client.send_command(command)
    if answer == proto.NO_MEMBER_COMMAND or is_error(answer)[0]:
        raise Py4JError("no field {0} in object {1}".format(
            field_name, java_object._target_id))
    return get_return_value(
        answer, java_object._gateway_client, java_object._target_id,
        field_name)


def get_method(java_object, method_name):
    """Retrieves a reference to the method of an object.

    This function is useful when `auto_field=true` and an instance field has
    the same name as a method. The full signature of the method is not
    required: it is determined when the method is called.

    :param java_object: the instance containing the method
    :param method_name: the name of the method to retrieve
    """
    return JavaMember(
        method_name, java_object, java_object._target_id,
        java_object._gateway_client)


def is_instance_of(gateway, java_object, java_class):
    """Indicates whether a java object is an instance of the provided
    java_class.

    :param gateway: the JavaGateway instance
    :param java_object: the JavaObject instance
    :param java_class: can be a string (fully qualified name), a JavaClass
            instance, or a JavaObject instance)
    """
    if isinstance(java_class, basestring):
        param = java_class
    elif isinstance(java_class, JavaClass):
        param = java_class._fqn
    elif isinstance(java_class, JavaObject):
        param = java_class.getClass()
    else:
        raise Py4JError(
            "java_class must be a string, a JavaClass, or a JavaObject")

    return gateway.jvm.py4j.reflection.TypeUtil.isInstanceOf(
        param, java_object)


def quiet_close(closable):
    """Quietly closes a closable object without throwing an exception.

    :param closable: Object with a ``close`` method.
    """
    try:
        closable.close()
    except Exception:
        logger.debug("Exception while closing", exc_info=True)


def quiet_shutdown(socket_instance):
    """Quietly shuts down a socket without throwing an exception.

    :param socket_instance: Socket with ``shutdown`` method.
    """
    try:
        socket_instance.shutdown(socket.SHUT_RDWR)
    except Exception:
        logger.debug("Exception while shutting down a socket", exc_info=True)


def gateway_help(gateway_client, var, pattern=None, short_name=True,
                 display=True):
    """Displays a help page about a class or an object.

    :param gateway_client: The gatway client

    :param var: JavaObject, JavaClass or JavaMember for which a help page
     will be generated.

    :param pattern: Star-pattern used to filter the members. For example
     "get*Foo" may return getMyFoo, getFoo, getFooBar, but not bargetFoo.
     The pattern is matched against the entire signature. To match only
     the name of a method, use "methodName(*".

    :param short_name: If True, only the simple name of the parameter
     types and return types will be displayed. If False, the fully
     qualified name of the types will be displayed.

    :param display: If True, the help page is displayed in an interactive
     page similar to the `help` command in Python. If False, the page is
     returned as a string.
    """
    if hasattr2(var, "_get_object_id"):
        command = proto.HELP_COMMAND_NAME +\
            proto.HELP_OBJECT_SUBCOMMAND_NAME +\
            var._get_object_id() + "\n" +\
            get_command_part(pattern) +\
            get_command_part(short_name) +\
            proto.END_COMMAND_PART
        answer = gateway_client.send_command(command)
    elif hasattr2(var, "_fqn"):
        command = proto.HELP_COMMAND_NAME +\
            proto.HELP_CLASS_SUBCOMMAND_NAME +\
            var._fqn + "\n" +\
            get_command_part(pattern) +\
            get_command_part(short_name) +\
            proto.END_COMMAND_PART
        answer = gateway_client.send_command(command)
    elif hasattr2(var, "container") and hasattr2(var, "name"):
        if pattern is not None:
            raise Py4JError("pattern should be None with var is a JavaMember")
        pattern = var.name + "(*"
        var = var.container
        return gateway_help(
            gateway_client, var, pattern, short_name=short_name,
            display=display)
    else:
        raise Py4JError(
            "var is none of Java Object, Java Class or Java Member")

    help_page = get_return_value(answer, gateway_client, None, None)
    if (display):
        pager(help_page)
    else:
        return help_page


def _garbage_collect_object(gateway_client, target_id):
    ThreadSafeFinalizer.remove_finalizer(
        smart_decode(gateway_client.address) +
        smart_decode(gateway_client.port) +
        target_id)
    if target_id != proto.ENTRY_POINT_OBJECT_ID and\
            gateway_client.is_connected:
        try:
            gateway_client.send_command(
                proto.MEMORY_COMMAND_NAME +
                proto.MEMORY_DEL_SUBCOMMAND_NAME +
                target_id +
                "\ne\n")
        except Exception:
            logger.debug("Exception while garbage collecting an object",
                         exc_info=True)


def _garbage_collect_connection(socket_instance):
    """Closes the socket if auto_delete is True and the socket is opened.

    This is an acceptable practice if you know that your Python VM implements
    garbage collection and closing sockets immediately is not a concern.
    Otherwise, it is always better (because it is predictable) to explicitly
    close the socket by calling `GatewayConnection.close()`.
    """
    if socket_instance is not None:
        quiet_shutdown(socket_instance)
        quiet_close(socket_instance)


class OutputConsumer(CompatThread):
    """Thread that consumes output
    """

    def __init__(self, redirect, stream, *args, **kwargs):
        super(OutputConsumer, self).__init__(*args, **kwargs)
        self.redirect = redirect
        self.stream = stream

        if isinstance(redirect, Queue):
            self.redirect_func = self._pipe_queue
        if isinstance(redirect, deque):
            self.redirect_func = self._pipe_deque
        if hasattr2(redirect, "write"):
            self.redirect_func = self._pipe_fd

    def _pipe_queue(self, line):
        self.redirect.put(line)

    def _pipe_deque(self, line):
        self.redirect.appendleft(line)

    def _pipe_fd(self, line):
        self.redirect.write(line)

    def run(self):
        lines_iterator = iter(self.stream.readline, b"")
        for line in lines_iterator:
            self.redirect_func(smart_decode(line))


class ProcessConsumer(CompatThread):
    """Thread that ensures process stdout and stderr are properly closed.
    """

    def __init__(self, proc, closable_list, *args, **kwargs):
        super(ProcessConsumer, self).__init__(*args, **kwargs)
        self.proc = proc
        if closable_list:
            # We don't care if it contains queues or deques, quiet_close will
            # just ignore them.
            self.closable_list = closable_list
        else:
            self.closable_list = []

    def run(self):
        self.proc.wait()
        quiet_close(self.proc.stdout)
        quiet_close(self.proc.stderr)
        for closable in self.closable_list:
            quiet_close(closable)


class GatewayParameters(object):
    """Wrapper class that contains all parameters that can be passed to
    configure a `JavaGateway`
    """

    def __init__(
            self, address=DEFAULT_ADDRESS, port=DEFAULT_PORT, auto_field=False,
            auto_close=True, auto_convert=False, eager_load=False):
        """
        :param address: the address to which the client will request a
         connection

        :param port: the port to which the client will request a connection.
         Default is 25333.

        :param auto_field: if `False`, each object accessed through this
         gateway won"t try to lookup fields (they will be accessible only by
         calling get_field). If `True`, fields will be automatically looked
         up, possibly hiding methods of the same name and making method calls
         less efficient.

        :param auto_close: if `True`, the connections created by the client
         close the socket when they are garbage collected.

        :param auto_convert: if `True`, try to automatically convert Python
         objects like sequences and maps to Java Objects. Default value is
         `False` to improve performance and because it is still possible to
         explicitly perform this conversion.

        :param eager_load: if `True`, the gateway tries to connect to the JVM
         by calling System.currentTimeMillis. If the gateway cannot connect to
         the JVM, it shuts down itself and raises an exception.
        """
        self.address = address
        self.port = port
        self.auto_field = auto_field
        self.auto_close = auto_close
        self.auto_convert = auto_convert
        self.eager_load = eager_load


class CallbackServerParameters(object):
    """Wrapper class that contains all parameters that can be passed to
    configure a `CallbackServer`
    """

    def __init__(
            self, address=DEFAULT_ADDRESS, port=DEFAULT_PYTHON_PROXY_PORT,
            daemonize=False, daemonize_connections=False, eager_load=True):
        """
        :param address: the address to which the client will request a
            connection

        :param port: the port to which the client will request a connection.
            Default is 25333.

        :param daemonize: If `True`, will set the daemon property of the server
            thread to True. The callback server will exit automatically if all
            the other threads exit.

        :param daemonize_connections: If `True`, callback server connections
            are executed in daemonized threads and will not block the exit of a
            program if non daemonized threads are finished.

        :param eager_load: If `True`, the callback server is automatically
            started when the JavaGateway is created.

        """
        self.address = address
        self.port = port
        self.daemonize = daemonize
        self.daemonize_connections = daemonize_connections
        self.eager_load = eager_load


class DummyRLock(object):
    def __init__(self):
        pass

    def acquire(self, blocking=1):
        pass

    def release(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        pass


class GatewayClient(object):
    """Responsible for managing connections to the JavaGateway.

    This implementation is thread-safe and connections are created on-demand.
    This means that Py4J-Python can be accessed by multiple threads and
    messages are sent to and processed concurrently by the Java Gateway.

    When creating a custom :class:`JavaGateway`, it is recommended to pass an
    instance of :class:`GatewayClient` instead of a :class:`GatewayConnection`:
    both have the same interface, but the client supports multiple threads and
    connections, which is essential when using callbacks.  """

    def __init__(self, address=DEFAULT_ADDRESS, port=25333, auto_close=True,
                 gateway_property=None):
        """
        :param address: the address to which the client will request a
         connection

        :param port: the port to which the client will request a connection.
         Default is 25333.

        :param auto_close: if `True`, the connections created by the client
         close the socket when they are garbage collected.

        :param gateway_property: used to keep gateway preferences without a
         cycle with the gateway
        """
        self.address = address
        self.port = port
        self.is_connected = True
        self.auto_close = auto_close
        self.gateway_property = gateway_property
        self.deque = deque()

    def _get_connection(self):
        if not self.is_connected:
            raise Py4JNetworkError("Gateway is not connected.")
        try:
            connection = self.deque.pop()
        except IndexError:
            connection = self._create_connection()
        return connection

    def _create_connection(self):
        connection = GatewayConnection(
            self.address, self.port, self.auto_close, self.gateway_property)
        connection.start()
        return connection

    def _give_back_connection(self, connection):
        try:
            self.deque.append(connection)
        except Exception:
            logger.warning(
                "Exception while giving back connection", exc_info=True)

    def shutdown_gateway(self):
        """Sends a shutdown command to the gateway. This will close the
           gateway server: all active connections will be closed. This may
           be useful if the lifecycle of the Java program must be tied to
           the Python program.
        """
        connection = self._get_connection()
        try:
            connection.shutdown_gateway()
            self.close()
            self.is_connected = False
        except Py4JNetworkError:
            logger.debug("Error while shutting down gateway.", exc_info=True)
            self.shutdown_gateway()

    def send_command(self, command, retry=True):
        """Sends a command to the JVM. This method is not intended to be
           called directly by Py4J users. It is usually called by
           :class:`JavaMember` instances.

        :param command: the `string` command to send to the JVM. The command
         must follow the Py4J protocol.

        :param retry: if `True`, the GatewayClient tries to resend a message
         if it fails.

        :rtype: the `string` answer received from the JVM. The answer follows
         the Py4J protocol.
        """
        connection = self._get_connection()
        try:
            response = connection.send_command(command)
            self._give_back_connection(connection)
        except Py4JNetworkError:
            if retry:
                logging.info("Exception while sending command.", exc_info=True)
                response = self.send_command(command)
            else:
                logging.exception(
                    "Exception while sending command.")
                response = proto.ERROR

        return response

    def close(self):
        """Closes all currently opened connections.

        This operation is not thread safe and is only a best effort strategy
        to close active connections.

        All connections are guaranteed to be closed only if no other thread
        is accessing the client and no call is pending.
        """
        size = len(self.deque)
        for _ in range(0, size):
            try:
                connection = self.deque.pop()
                quiet_close(connection)
            except IndexError:
                pass


class GatewayConnection(object):
    """Default gateway connection (socket based) responsible for communicating
       with the Java Virtual Machine."""

    def __init__(self, address=DEFAULT_ADDRESS, port=25333, auto_close=True,
                 gateway_property=None):
        """
        :param address: the address to which the connection will be established

        :param port: the port to which the connection will be established.
         Default is 25333.

        :param auto_close: if `True`, the connection closes the socket when it
         is garbage collected.

        :param gateway_property: contains gateway preferences to avoid a cycle
         with gateway
        """
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.auto_close = auto_close
        self.gateway_property = gateway_property
        self.wr = weakref.ref(
            self,
            lambda wr, socket_instance=self.socket:
            _garbage_collect_connection(socket_instance))

    def start(self):
        """Starts the connection by connecting to the `address` and the `port`
        """
        try:
            self.socket.connect((self.address, self.port))
            self.is_connected = True
            self.stream = self.socket.makefile("rb", 0)
        except Exception as e:
            msg = "An error occurred while trying to connect to the Java "\
                "server"
            logger.exception(msg)
            raise Py4JNetworkError(msg, e)

    def close(self):
        """Closes the connection by closing the socket."""
        quiet_close(self.stream)
        quiet_shutdown(self.socket)
        quiet_close(self.socket)
        self.is_connected = False

    def shutdown_gateway(self):
        """Sends a shutdown command to the gateway. This will close the gateway
           server: all active connections will be closed. This may be useful
           if the lifecycle of the Java program must be tied to the Python
           program.
        """
        if (not self.is_connected):
            raise Py4JError("Gateway must be connected to send shutdown cmd.")

        try:
            quiet_close(self.stream)
            self.socket.sendall(
                proto.SHUTDOWN_GATEWAY_COMMAND_NAME.encode("utf-8"))
            quiet_close(self.socket)
            self.is_connected = False
        except Exception:
            # Do nothing! Exceptions might occur anyway.
            logger.debug("Exception occurred while shutting down gateway",
                         exc_info=True)

    def send_command(self, command):
        """Sends a command to the JVM. This method is not intended to be
           called directly by Py4J users: it is usually called by JavaMember
           instances.

        :param command: the `string` command to send to the JVM. The command
         must follow the Py4J protocol.

        :rtype: the `string` answer received from the JVM. The answer follows
         the Py4J protocol.
        """
        logger.debug("Command to send: {0}".format(command))
        try:
            self.socket.sendall(command.encode("utf-8"))
            answer = smart_decode(self.stream.readline()[:-1])
            logger.debug("Answer received: {0}".format(answer))
            # Happens when a the other end is dead. There might be an empty
            # answer before the socket raises an error.
            if answer.strip() == "":
                self.close()
                raise Py4JError("Answer from Java side is empty")
            return answer
        except Exception as e:
            logger.exception("Error while sending or receiving.")
            raise Py4JNetworkError("Error while sending or receiving", e)


class JavaMember(object):
    """Represents a member (i.e., method) of a :class:`JavaObject`. For now,
       only methods are supported. Fields are retrieved directly and are not
       contained in a JavaMember.
    """

    def __init__(self, name, container, target_id, gateway_client):
        self.name = name
        self.container = container
        self.target_id = target_id
        self.gateway_client = gateway_client
        self.command_header = self.target_id + "\n" + self.name + "\n"
        self.pool = self.gateway_client.gateway_property.pool
        self.converters = self.gateway_client.converters
        self._gateway_doc = None

    @property
    def __doc__(self):
        # The __doc__ string is used by IPython/PyDev/etc to generate
        # help string, therefore provide useful help
        if self._gateway_doc is None:
            self._gateway_doc = gateway_help(
                self.gateway_client, self, display=False)
        return self._gateway_doc

    def _get_args(self, args):
        temp_args = []
        new_args = []
        for arg in args:
            if not isinstance(arg, JavaObject):
                for converter in self.gateway_client.converters:
                    if converter.can_convert(arg):
                        temp_arg = converter.convert(arg, self.gateway_client)
                        temp_args.append(temp_arg)
                        new_args.append(temp_arg)
                        break
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)

        return (new_args, temp_args)

    def __call__(self, *args):
        if self.converters is not None and len(self.converters) > 0:
            (new_args, temp_args) = self._get_args(args)
        else:
            new_args = args
            temp_args = []

        args_command = "".join(
            [get_command_part(arg, self.pool) for arg in new_args])

        command = proto.CALL_COMMAND_NAME +\
            self.command_header +\
            args_command +\
            proto.END_COMMAND_PART

        answer = self.gateway_client.send_command(command)
        return_value = get_return_value(
            answer, self.gateway_client, self.target_id, self.name)

        for temp_arg in temp_args:
            temp_arg._detach()

        return return_value


class JavaObject(object):
    """Represents a Java object from which you can call methods or access
       fields."""

    def __init__(self, target_id, gateway_client):
        """
        :param target_id: the identifier of the object on the JVM side. Given
         by the JVM.

        :param gateway_client: the gateway client used to communicate with
         the JVM.
        """
        self._target_id = target_id
        self._gateway_client = gateway_client
        self._auto_field = gateway_client.gateway_property.auto_field
        self._methods = {}
        self._field_names = set()
        self._fully_populated = False
        self._gateway_doc = None

        key = smart_decode(self._gateway_client.address) +\
            smart_decode(self._gateway_client.port) +\
            self._target_id

        value = weakref.ref(
            self,
            lambda wr, cc=self._gateway_client, id=self._target_id:
            _garbage_collect_object(cc, id))

        ThreadSafeFinalizer.add_finalizer(key, value)

    def _detach(self):
        _garbage_collect_object(self._gateway_client, self._target_id)

    def _get_object_id(self):
        return self._target_id

    @property
    def __doc__(self):
        # The __doc__ string is used by IPython/PyDev/etc to generate
        # help string, therefore provide useful help
        print("HELLO")
        if self._gateway_doc is None:
            self._gateway_doc = gateway_help(
                self._gateway_client, self, display=False)
        return self._gateway_doc

    def __getattr__(self, name):
        if name == "__call__":
            # Provide an explicit definition for __call__ so that a JavaMember
            # does not get created for it. This serves two purposes:
            # 1) IPython (and others?) stop showing incorrect help indicating
            #    that this is callable
            # 2) A TypeError(object not callable) is raised if someone does try
            #    to call here
            raise AttributeError

        if name not in self._methods:
            if (self._auto_field):
                (is_field, return_value) = self._get_field(name)
                if (is_field):
                    self._field_names.add(name)
                    return return_value
            # Theoretically, not thread safe, but the worst case scenario is
            # cache miss or double overwrite of the same method...
            self._methods[name] = JavaMember(
                name, self, self._target_id, self._gateway_client)

        # The name is a method
        return self._methods[name]

    def __dir__(self):
        self._populate_fields()
        return list(set(self._methods.keys()) | self._field_names)

    def _populate_fields(self):
        # Theoretically, not thread safe, but the worst case scenario is
        # cache miss or double overwrite of the same method...
        if not self._fully_populated:
            if self._auto_field:
                command = proto.DIR_COMMAND_NAME +\
                    proto.DIR_FIELDS_SUBCOMMAND_NAME +\
                    self._target_id + "\n" +\
                    proto.END_COMMAND_PART

                answer = self._gateway_client.send_command(command)
                return_value = get_return_value(
                    answer, self._gateway_client, self._target_id, "__dir__")
                self._field_names.update(return_value.split("\n"))

            command = proto.DIR_COMMAND_NAME +\
                proto.DIR_METHODS_SUBCOMMAND_NAME +\
                self._target_id + "\n" +\
                proto.END_COMMAND_PART

            answer = self._gateway_client.send_command(command)
            return_value = get_return_value(
                answer, self._gateway_client, self._target_id, "__dir__")
            names = return_value.split("\n")
            for name in names:
                if name not in self._methods:
                    self._methods[name] = JavaMember(
                        name, self, self._target_id, self._gateway_client)

            self._fully_populated = True

    def _get_field(self, name):
        command = proto.FIELD_COMMAND_NAME +\
            proto.FIELD_GET_SUBCOMMAND_NAME +\
            self._target_id + "\n" +\
            name + "\n" +\
            proto.END_COMMAND_PART

        answer = self._gateway_client.send_command(command)
        if answer == proto.NO_MEMBER_COMMAND or is_error(answer)[0]:
            return (False, None)
        else:
            return_value = get_return_value(
                answer, self._gateway_client, self._target_id, name)
            return (True, return_value)

    def __eq__(self, other):
        if other is None:
            return False
        elif (hasattr2(other, "_get_object_id")):
            return self.equals(other)
        else:
            return other.__eq__(self)

    def __hash__(self):
        return self.hashCode()

    def __str__(self):
        return self.toString()

    def __repr__(self):
        # For now...
        return "JavaObject id=" + self._target_id


class JavaClass(object):
    """A `JavaClass` represents a Java Class from which static members can be
       retrieved. `JavaClass` instances are also needed to initialize an array.

       Usually, `JavaClass` are not initialized using their constructor, but
       they are created while accessing the `jvm` property of a gateway, e.g.,
       `gateway.jvm.java.lang.String`.
    """
    def __init__(self, fqn, gateway_client):
        self._fqn = fqn
        self._gateway_client = gateway_client
        self._pool = self._gateway_client.gateway_property.pool
        self._command_header = fqn + "\n"
        self._converters = self._gateway_client.converters
        self._gateway_doc = None
        self._statics = None

    @property
    def __doc__(self):
        # The __doc__ string is used by IPython/PyDev/etc to generate
        # help string, therefore provide useful help
        if self._gateway_doc is None:
            self._gateway_doc = gateway_help(
                self._gateway_client, self, display=False)
        return self._gateway_doc

    def __dir__(self):
        # Theoretically, not thread safe, but the worst case scenario is
        # cache miss or double overwrite of the same method...
        if self._statics is None:
            command = proto.DIR_COMMAND_NAME +\
                proto.DIR_STATIC_SUBCOMMAND_NAME +\
                self._fqn + "\n" +\
                proto.END_COMMAND_PART

            answer = self._gateway_client.send_command(command)
            return_value = get_return_value(
                answer, self._gateway_client, self._fqn, "__dir__")
            self._statics = return_value.split("\n")
        return self._statics[:]

    def __getattr__(self, name):
        if name in ["__str__", "__repr__"]:
            raise AttributeError

        command = proto.REFLECTION_COMMAND_NAME +\
            proto.REFL_GET_MEMBER_SUB_COMMAND_NAME +\
            self._fqn + "\n" +\
            name + "\n" +\
            proto.END_COMMAND_PART
        answer = self._gateway_client.send_command(command)

        if len(answer) > 1 and answer[0] == proto.SUCCESS:
            if answer[1] == proto.METHOD_TYPE:
                return JavaMember(
                    name, None, proto.STATIC_PREFIX + self._fqn,
                    self._gateway_client)
            elif answer[1].startswith(proto.CLASS_TYPE):
                return JavaClass(
                    self._fqn + "$" + name, self._gateway_client)
            else:
                return get_return_value(
                    answer, self._gateway_client, self._fqn, name)
        else:
            raise Py4JError(
                "{0}.{1} does not exist in the JVM".format(self._fqn, name))

    def _get_args(self, args):
        temp_args = []
        new_args = []
        for arg in args:
            if not isinstance(arg, JavaObject):
                for converter in self._converters:
                    if converter.can_convert(arg):
                        temp_arg = converter.convert(arg, self._gateway_client)
                        temp_args.append(temp_arg)
                        new_args.append(temp_arg)
                        break
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)

        return (new_args, temp_args)

    def __call__(self, *args):
        # TODO Refactor to use a mixin shared by JavaMember and JavaClass
        if self._converters is not None and len(self._converters) > 0:
            (new_args, temp_args) = self._get_args(args)
        else:
            new_args = args
            temp_args = []

        args_command = "".join(
            [get_command_part(arg, self._pool) for arg in new_args])

        command = proto.CONSTRUCTOR_COMMAND_NAME +\
            self._command_header +\
            args_command +\
            proto.END_COMMAND_PART

        answer = self._gateway_client.send_command(command)
        return_value = get_return_value(
            answer, self._gateway_client, None, self._fqn)

        for temp_arg in temp_args:
            temp_arg._detach()

        return return_value


class UserHelpAutoCompletion(object):
    """
    Type a package name or a class name.

    For example with a JVMView called view:
    >>> o = view.Object() # create a java.lang.Object
    >>> random = view.jvm.java.util.Random() # create a java.util.Random

    The default JVMView is in the gateway and is called:
    >>> gateway.jvm

    By default, java.lang.* is available in the view. To
    add additional Classes/Packages, do:
    >>> from py4j.java_gateway import java_import
    >>> java_import(gateway.jvm, "com.example.Class1")
    >>> instance = gateway.jvm.Class1()

    Package and class completions are only available for
    explicitly imported Java classes. For example, if you
    java_import(gateway.jvm, "com.example.Class1")
    then Class1 will appear in the completions.
    """
    KEY = "<package or class name>"


class JavaPackage(object):
    """A `JavaPackage` represents part of a Java package from which Java
       classes can be accessed.

       Usually, `JavaPackage` are not initialized using their constructor, but
       they are created while accessing the `jvm` property of a gateway, e.g.,
       `gateway.jvm.java.lang`.
    """
    def __init__(self, fqn, gateway_client, jvm_id=None):
        self._fqn = fqn
        self._gateway_client = gateway_client
        if jvm_id is None:
            self._jvm_id = proto.DEFAULT_JVM_ID
        self._jvm_id = jvm_id

    def __dir__(self):
        return [UserHelpAutoCompletion.KEY]

    def __getattr__(self, name):
        if name == UserHelpAutoCompletion.KEY:
            return UserHelpAutoCompletion

        if name in ["__str__", "__repr__"]:
            raise AttributeError

        if name == "__call__":
            raise Py4JError("Trying to call a package.")
        new_fqn = self._fqn + "." + name
        command = proto.REFLECTION_COMMAND_NAME +\
            proto.REFL_GET_UNKNOWN_SUB_COMMAND_NAME +\
            new_fqn + "\n" +\
            self._jvm_id + "\n" +\
            proto.END_COMMAND_PART
        answer = self._gateway_client.send_command(command)
        if answer == proto.SUCCESS_PACKAGE:
            return JavaPackage(new_fqn, self._gateway_client, self._jvm_id)
        elif answer.startswith(proto.SUCCESS_CLASS):
            return JavaClass(
                answer[proto.CLASS_FQN_START:], self._gateway_client)
        else:
            raise Py4JError("{0} does not exist in the JVM".format(new_fqn))


class JVMView(object):
    """A `JVMView` allows access to the Java Virtual Machine of a
       `JavaGateway`.

       This can be used to reference static members (fields and methods) and
       to call constructors.
    """

    def __init__(self, gateway_client, jvm_name, id=None, jvm_object=None):
        self._gateway_client = gateway_client
        self._jvm_name = jvm_name
        if id is not None:
            self._id = id
        elif jvm_object is not None:
            self._id = proto.REFERENCE_TYPE + jvm_object._get_object_id()
            # So that both JVMView instances (on Python and Java) have the
            # same lifecycle. Theoretically, JVMView could inherit from
            # JavaObject, but I would like to avoid the use of reflection
            # for regular Py4J classes.
            self._jvm_object = jvm_object

        self._dir_sequence_and_cache = (None, [])

    def __dir__(self):
        command = proto.DIR_COMMAND_NAME +\
            proto.DIR_JVMVIEW_SUBCOMMAND_NAME +\
            self._id + "\n" +\
            get_command_part(self._dir_sequence_and_cache[0]) + "\n" +\
            proto.END_COMMAND_PART

        answer = self._gateway_client.send_command(command)
        return_value = get_return_value(
            answer, self._gateway_client, self._fqn, "__dir__")
        if return_value is not None:
            result = return_value.split("\n")
            # Theoretically, not thread safe, but the worst case scenario is
            # cache miss or double overwrite of the same method...
            self._dir_sequence_and_cache = (
                result[0], result[1:] + [UserHelpAutoCompletion.KEY])
        return self._dir_sequence_and_cache[1][:]

    def __getattr__(self, name):
        if name == UserHelpAutoCompletion.KEY:
            return UserHelpAutoCompletion()

        answer = self._gateway_client.send_command(
            proto.REFLECTION_COMMAND_NAME +
            proto.REFL_GET_UNKNOWN_SUB_COMMAND_NAME + name + "\n" + self._id +
            "\n" + proto.END_COMMAND_PART)
        if answer == proto.SUCCESS_PACKAGE:
            return JavaPackage(name, self._gateway_client, jvm_id=self._id)
        elif answer.startswith(proto.SUCCESS_CLASS):
            return JavaClass(
                answer[proto.CLASS_FQN_START:], self._gateway_client)
        else:
            raise Py4JError("{0} does not exist in the JVM".format(name))


class GatewayProperty(object):
    """Object shared by callbackserver, gateway, and connections.
    """
    def __init__(self, auto_field, pool):
        self.auto_field = auto_field
        self.pool = pool


class JavaGateway(object):
    """A `JavaGateway` is the main interaction point between a Python VM and
       a JVM.

    * A `JavaGateway` instance is connected to a `Gateway` instance on the
      Java side.

    * The `entry_point` field of a `JavaGateway` instance is connected to
      the `Gateway.entryPoint` instance on the Java side.

    * The `jvm` field of `JavaGateway` enables user to access classes, static
      members (fields and methods) and call constructors.

    Methods that are not defined by `JavaGateway` are always redirected to
    `entry_point`. For example, ``gateway.doThat()`` is equivalent to
    ``gateway.entry_point.doThat()``. This is a trade-off between convenience
    and potential confusion.
    """

    def __init__(
            self, gateway_client=None, auto_field=False,
            python_proxy_port=DEFAULT_PYTHON_PROXY_PORT,
            start_callback_server=False, auto_convert=False, eager_load=False,
            gateway_parameters=None, callback_server_parameters=None):
        """
        :param gateway_parameters: An instance of `GatewayParameters` used to
            configure the various options of the gateway.

        :param callback_server_parameters: An instance of
            `CallbackServerParameters` used to configure various options of the
            gateway server. Must be provided to start a gateway server.
            Otherwise, callbacks won"t be available.
        """

        self.gateway_parameters = gateway_parameters
        if not gateway_parameters:
            self.gateway_parameters = GatewayParameters(
                auto_field=auto_field, auto_convert=auto_convert,
                eager_load=eager_load)

        self.callback_server_parameters = callback_server_parameters
        if not callback_server_parameters:
            # No parameters were provided so do not autostart callback server.
            self.callback_server_parameters = CallbackServerParameters(
                port=python_proxy_port, eager_load=False)

        # Check for deprecation warnings
        if auto_field:
            deprecated("JavaGateway.auto_field", "1.0", "GatewayParameters")

        if auto_convert:
            deprecated("JavaGateway.auto_convert", "1.0", "GatewayParameters")

        if eager_load:
            deprecated("JavaGateway.eager_load", "1.0", "GatewayParameters")

        if start_callback_server:
            deprecated(
                "JavaGateway.start_callback_server and python_proxy_port",
                "1.0", "CallbackServerParameters")
            self.callback_server_parameters.eager_load = True

        if gateway_client:
            deprecated("JavaGateway.gateway_client", "1.0",
                       "GatewayParameters")
        else:
            gateway_client = GatewayClient(
                address=self.gateway_parameters.address,
                port=self.gateway_parameters.port,
                auto_close=self.gateway_parameters.auto_close)

        self.gateway_property = GatewayProperty(
            self.gateway_parameters.auto_field, PythonProxyPool())
        self._python_proxy_port = python_proxy_port

        # Setup gateway client
        self.set_gateway_client(gateway_client)

        # Setup callback server property
        self._callback_server = None

        if self.gateway_parameters.eager_load:
            self._eager_load()
        if self.callback_server_parameters.eager_load:
            self.start_callback_server(self.callback_server_parameters)

    def set_gateway_client(self, gateway_client):
        """Sets the gateway client for this JavaGateway. This sets the
        appropriate gateway_property and resets the main jvm view (self.jvm).

        This is for advanced usage only. And should only be set before the
        gateway is loaded.
        """
        if self.gateway_parameters.auto_convert:
            gateway_client.converters = proto.INPUT_CONVERTER
        else:
            gateway_client.converters = None
        gateway_client.gateway_property = self.gateway_property
        self._gateway_client = gateway_client

        self.entry_point = JavaObject(
            proto.ENTRY_POINT_OBJECT_ID, self._gateway_client)

        self.jvm = JVMView(
            self._gateway_client, jvm_name=proto.DEFAULT_JVM_NAME,
            id=proto.DEFAULT_JVM_ID)

    def __getattr__(self, name):
        return self.entry_point.__getattr__(name)

    def _eager_load(self):
        try:
            self.jvm.System.currentTimeMillis()
        except Exception:
            self.shutdown()
            raise

    def start_callback_server(self, callback_server_parameters=None):
        """Starts the callback server.

        :param callback_server_parameters: parameters to use to start the
            server. If not provided, it will use the gateway callback server
            parameters.

        :rtype: Returns True if the server was started by this call or False if
            it was already started (you cannot have more than one started
            callback server).
        """
        if self._callback_server:
            return False

        if not callback_server_parameters:
            callback_server_parameters = self.callback_server_parameters

        self._callback_server = CallbackServer(
            self.gateway_property.pool, self._gateway_client,
            callback_server_parameters=callback_server_parameters)
        try:
            self._callback_server.start()
        except Py4JNetworkError:
            # Clean up ourselves before raising the exception.
            self.shutdown()
            self._callback_server = None
            raise

        return True

    def new_jvm_view(self, name="custom jvm"):
        """Creates a new JVM view with its own imports. A JVM view ensures
        that the import made in one view does not conflict with the import
        of another view.

        Generally, each Python module should have its own view (to replicate
        Java behavior).

        :param name: Optional name of the jvm view. Does not need to be
            unique, i.e., two distinct views can have the same name
            (internally, they will have a distinct id).

        :rtype: A JVMView instance (same class as the gateway.jvm instance).
        """
        command = proto.JVMVIEW_COMMAND_NAME +\
            proto.JVM_CREATE_VIEW_SUB_COMMAND_NAME +\
            get_command_part(name) +\
            proto.END_COMMAND_PART

        answer = self._gateway_client.send_command(command)
        java_object = get_return_value(answer, self._gateway_client)

        return JVMView(
            gateway_client=self._gateway_client, jvm_name=name,
            jvm_object=java_object)

    def new_array(self, java_class, *dimensions):
        """Creates a Java array of type `java_class` of `dimensions`

        :param java_class: The :class:`JavaClass` instance representing the
            type of the array.

        :param dimensions: A list of dimensions of the array. For example
            `[1,2]` would produce an `array[1][2]`.

        :rtype: A :class:`JavaArray <py4j.java_collections.JavaArray>`
            instance.
        """
        if len(dimensions) == 0:
            raise Py4JError("new arrays must have at least one dimension")
        command = proto.ARRAY_COMMAND_NAME +\
            proto.ARRAY_CREATE_SUB_COMMAND_NAME +\
            get_command_part(java_class._fqn)
        for dimension in dimensions:
            command += get_command_part(dimension)
        command += proto.END_COMMAND_PART
        answer = self._gateway_client.send_command(command)
        return get_return_value(answer, self._gateway_client)

    def shutdown(self, raise_exception=False):
        """Shuts down the :class:`GatewayClient` and the
           :class:`CallbackServer <py4j.java_callback.CallbackServer>`.

        :param raise_exception: If `True`, raise an exception if an error
            occurs while shutting down (very likely with sockets).
        """
        try:
            self._gateway_client.shutdown_gateway()
        except Exception:
            if raise_exception:
                raise
            else:
                logger.info(
                    "Exception while shutting down callback server",
                    exc_info=True)
        self.shutdown_callback_server()

    def shutdown_callback_server(self, raise_exception=False):
        """Shuts down the
           :class:`CallbackServer <py4j.java_callback.CallbackServer>`.

        :param raise_exception: If `True`, raise an exception if an error
            occurs while shutting down (very likely with sockets).
        """
        try:
            self._callback_server.shutdown()
        except Exception:
            if raise_exception:
                raise
            else:
                logger.info(
                    "Exception while shutting down callback server",
                    exc_info=True)

    def restart_callback_server(self):
        """Shuts down the callback server (if started) and restarts a new one.
        """
        self.shutdown_callback_server()
        self._callback_server = None
        self.start_callback_server(self.callback_server_parameters)

    def close(self, keep_callback_server=False):
        """Closes all gateway connections. A connection will be reopened if
           necessary (e.g., if a :class:`JavaMethod` is called).

        :param keep_callback_server: if `True`, the callback server is not
            shut down.
        """
        self._gateway_client.close()
        if not keep_callback_server:
            self.shutdown_callback_server()

    def detach(self, java_object):
        """Makes the Java Gateway dereference this object.

        The equivalent of this method is called when a JavaObject instance
        is garbage collected on the Python side. This method, or gc.collect()
        should still be invoked when memory is limited or when too many objects
        are created on the Java side.

        :param java_object: The JavaObject instance to dereference (free) on
            the Java side.
        """
        java_object._detach()

    def help(self, var, pattern=None, short_name=True, display=True):
        """Displays a help page about a class or an object.

        :param var: JavaObject, JavaClass or JavaMember for which a help page
            will be generated.

        :param pattern: Star-pattern used to filter the members. For example
            "get\*Foo" may return getMyFoo, getFoo, getFooBar, but not
            bargetFoo. The pattern is matched against the entire signature.
            To match only the name of a method, use "methodName(\*".

        :param short_name: If True, only the simple name of the parameter
            types and return types will be displayed. If False, the fully
            qualified name of the types will be displayed.

        :param display: If True, the help page is displayed in an interactive
            page similar to the `help` command in Python. If False, the page is
            returned as a string.
        """
        return gateway_help(
            self._gateway_client, var, pattern, short_name, display)

    @classmethod
    def launch_gateway(
            cls, port=0, jarpath="", classpath="", javaopts=[],
            die_on_exit=False, redirect_stdout=None,
            redirect_stderr=None, daemonize_redirect=False):
        """Launch a `Gateway` in a new Java process and create a default
        :class:`JavaGateway <py4j.java_gateway.JavaGateway>` to connect to
        it.

        See :func:`launch_gateway <py4j.java_gateway.launch_gateway>` for more
        information about this function.

        :param port: the port to launch the Java Gateway on.  If no port is
            specified then an ephemeral port is used.
        :param jarpath: the path to the Py4J jar.  Only necessary if the jar
            was installed at a non-standard location or if Python is using
            a different `sys.prefix` than the one that Py4J was installed
            under.
        :param classpath: the classpath used to launch the Java Gateway.
        :param javaopts: an array of extra options to pass to Java (the
            classpath should be specified using the `classpath` parameter,
            not `javaopts`.)
        :param die_on_exit: if `True`, the Java gateway process will die when
            this Python process exits or is killed.
        :param redirect_stdout: where to redirect the JVM stdout.
            If None (default)
            stdout is redirected to os.devnull. Otherwise accepts a
            file descriptor, a queue, or a deque. Will send one line at a time
            to these objects.
        :param redirect_stderr: where to redirect the JVM stdout.
            If None (default)
            stderr is redirected to os.devnull. Otherwise accepts a
            file descriptor, a queue, or a deque. Will send one line at a time
            to these objects.
        :param daemonize_redirect: if True, the consumer threads will be
            daemonized and will not prevent the main Python process from
            exiting. This means the file descriptors (stderr, stdout,
            redirect_stderr, redirect_stdout) might not be properly closed.
            This is not usually a problem, but the default is conservatively
            set to False.

        :rtype: a :class:`JavaGateway <py4j.java_gateway.JavaGateway>`
            connected to the `Gateway` server.
        """
        _port = launch_gateway(
            port, jarpath, classpath, javaopts, die_on_exit,
            redirect_stdout=redirect_stdout, redirect_stderr=redirect_stderr,
            daemonize_redirect=daemonize_redirect)
        gateway = JavaGateway(gateway_parameters=GatewayParameters(port=_port))
        return gateway


# CALLBACK SPECIFIC

class CallbackServer(object):
    """The CallbackServer is responsible for receiving call back connection
       requests from the JVM. Usually connections are reused on the Java side,
       but there is at least one connection per concurrent thread.
    """

    def __init__(
            self, pool, gateway_client, port=DEFAULT_PYTHON_PROXY_PORT,
            address=DEFAULT_ADDRESS, callback_server_parameters=None):
        """
        :param pool: the pool responsible of tracking Python objects passed to
            the Java side.

        :param gateway_client: the gateway client used to call Java objects.

        :param callback_server_parameters: An instance of
            `CallbackServerParameters` used to configure various options of the
            callback server.

        """
        self.gateway_client = gateway_client

        self.callback_server_parameters = callback_server_parameters
        if not callback_server_parameters:
            deprecated(
                "CallbackServer.port and address", "1.0",
                "CallbackServerParameters")
            self.callback_server_parameters = CallbackServerParameters(
                address=address, port=port)

        self.port = self.callback_server_parameters.port
        self.address = self.callback_server_parameters.address
        self.pool = pool
        self.connections = []
        # Lock is used to isolate critical region like connection creation.
        # Some code can produce exceptions when ran in parallel, but
        # They will be caught and dealt with.
        self.lock = RLock()
        self.is_shutdown = False

    def start(self):
        """Starts the CallbackServer. This method should be called by the
        client instead of run()."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.address, self.port))
        except Exception as e:
            msg = "An error occurred while trying to start the callback server"
            logger.exception(msg)
            raise Py4JNetworkError(msg, e)

        # Maybe thread needs to be cleanup up?
        self.thread = Thread(target=self.run)

        # Default is False
        self.thread.daemon = self.callback_server_parameters.daemonize
        self.thread.start()

    def run(self):
        """Starts listening and accepting connection requests.

           This method is called when invoking `CallbackServer.start()`. A
           CallbackServer instance is created and started automatically when
           a :class:`JavaGateway <py4j.java_gateway.JavaGateway>` instance is
           created.
        """
        try:
            with self.lock:
                self.is_shutdown = False
            logger.info("Callback Server Starting")
            self.server_socket.listen(5)
            logger.info(
                "Socket listening on {0}".
                format(smart_decode(self.server_socket.getsockname())))

            read_list = [self.server_socket]
            while not self.is_shutdown:
                readable, writable, errored = select.select(
                    read_list, [], [], DEFAULT_CALLBACK_SERVER_ACCEPT_TIMEOUT)

                if self.is_shutdown:
                    break

                for s in readable:
                    socket_instance, _ = self.server_socket.accept()
                    input = socket_instance.makefile("rb", 0)
                    connection = CallbackConnection(
                        self.pool, input, socket_instance, self.gateway_client,
                        self.callback_server_parameters)
                    with self.lock:
                        if not self.is_shutdown:
                            self.connections.append(connection)
                            connection.start()
                        else:
                            quiet_shutdown(connection.socket)
                            quiet_close(connection.socket)
        except Exception:
            if self.is_shutdown:
                logger.info("Error while waiting for a connection.")
            else:
                logger.exception("Error while waiting for a connection.")

    def shutdown(self):
        """Stops listening and accepting connection requests. All live
           connections are closed.

           This method can safely be called by another thread.
        """
        logger.info("Callback Server Shutting Down")
        with self.lock:
            self.is_shutdown = True
            quiet_shutdown(self.server_socket)
            quiet_close(self.server_socket)
            self.server_socket = None

            for connection in self.connections:
                quiet_shutdown(connection.socket)
                quiet_close(connection.socket)

            self.pool.clear()
        self.thread.join()
        self.thread = None


class CallbackConnection(Thread):
    """A `CallbackConnection` receives callbacks and garbage collection
       requests from the Java side.
    """
    def __init__(
            self, pool, input, socket_instance, gateway_client,
            callback_server_parameters):
        super(CallbackConnection, self).__init__()
        self.pool = pool
        self.input = input
        self.socket = socket_instance
        self.gateway_client = gateway_client

        self.callback_server_parameters = callback_server_parameters
        if not callback_server_parameters:
            self.callback_server_parameters = CallbackServerParameters()

        self.daemon = self.callback_server_parameters.daemonize_connections

    def run(self):
        logger.info("Callback Connection ready to receive messages")
        try:
            while True:
                command = smart_decode(self.input.readline())[:-1]
                obj_id = smart_decode(self.input.readline())[:-1]
                logger.info(
                    "Received command {0} on object id {1}".
                    format(command, obj_id))
                if obj_id is None or len(obj_id.strip()) == 0:
                    break
                if command == proto.CALL_PROXY_COMMAND_NAME:
                    return_message = self._call_proxy(obj_id, self.input)
                    self.socket.sendall(return_message.encode("utf-8"))
                elif command == proto.GARBAGE_COLLECT_PROXY_COMMAND_NAME:
                    self.input.readline()
                    del(self.pool[obj_id])
                else:
                    logger.error("Unknown command {0}".format(command))
        except Exception:
            # This is a normal exception...
            logger.info(
                "Error while callback connection was waiting for"
                "a message", exc_info=True)

            logger.info("Closing down connection")
            quiet_shutdown(self.socket)
            quiet_close(self.socket)

    def _call_proxy(self, obj_id, input):
        return_message = proto.ERROR_RETURN_MESSAGE
        if obj_id in self.pool:
            try:
                method = smart_decode(input.readline())[:-1]
                params = self._get_params(input)
                return_value = getattr(self.pool[obj_id], method)(*params)
                return_message = "y" +\
                    get_command_part(return_value, self.pool)
            except Exception:
                logger.exception("There was an exception while executing the "
                                 "Python Proxy on the Python Side.")
        return return_message

    def _get_params(self, input):
        params = []
        temp = smart_decode(input.readline())[:-1]
        while temp != proto.END:
            param = get_return_value("y" + temp, self.gateway_client)
            params.append(param)
            temp = smart_decode(input.readline())[:-1]
        return params


class PythonProxyPool(object):
    """A `PythonProxyPool` manages proxies that are passed to the Java side.
       A proxy is a Python class that implements a Java interface.

       A proxy has an internal class named `Java` with a member named
       `implements` which is a list of fully qualified names (string) of the
       implemented interfaces.

       The `PythonProxyPool` implements a subset of the dict interface:
       `pool[id]`, `del(pool[id])`, `pool.put(proxy)`, `pool.clear()`,
       `id in pool`, `len(pool)`.

       The `PythonProxyPool` is thread-safe.
    """
    def __init__(self):
        self.lock = RLock()
        self.dict = {}
        self.next_id = 0

    def put(self, object):
        """Adds a proxy to the pool.

        :param object: The proxy to add to the pool.
        :rtype: A unique identifier associated with the object.
        """
        with self.lock:
            id = proto.PYTHON_PROXY_PREFIX + smart_decode(self.next_id)
            self.next_id += 1
            self.dict[id] = object
        return id

    def __getitem__(self, key):
        with self.lock:
            return self.dict[key]

    def __delitem__(self, key):
        with self.lock:
            del(self.dict[key])

    def clear(self):
        with self.lock:
            self.dict.clear()

    def __contains__(self, key):
        with self.lock:
            return key in self.dict

    def __len__(self):
        with self.lock:
            return len(self.dict)

# Basic registration
register_output_converter(
    proto.REFERENCE_TYPE,
    lambda target_id, gateway_client: JavaObject(target_id, gateway_client))

if PY4J_SKIP_COLLECTIONS not in os.environ or\
   os.environ[PY4J_SKIP_COLLECTIONS].lower() not in PY4J_TRUE:
    __import__("py4j.java_collections")
