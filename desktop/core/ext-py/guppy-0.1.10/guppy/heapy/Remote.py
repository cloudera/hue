#._cv_part guppy.heapy.Remote

"""
    Support remote access to a Python interpreter.
"""

from guppy.etc import cmd
from guppy import hpy
from guppy.heapy import heapyc, Target
from guppy.heapy.RemoteConstants import *
from guppy.heapy.Console import Console
from guppy.sets import mutbitset

import os, socket, sys, time, thread, threading, traceback, Queue

class SocketClosed(Exception):
    pass

class IsolatedCaller:
    # Isolates the target interpreter from us
    # when the _hiding_tag_ is set to the _hiding_tag_ of our hp.
    # A solution of a problem discussed in notes Nov 8-9 2005.
    # Note feb 3 2006: The class in the Target instance must be used.

    def __init__(self, func):
	self.func = func

    def __call__(self, *args, **kwds):
	return self.func(*args, **kwds)

class QueueWithReadline(Queue.Queue):
    def readline(self, size=-1):
        # Make sure we are interruptible
        # in case we get a keyboard interrupt.
        # Not a very elegant way but the 'only' there is?
        while 1:
            try:
                return self.get(timeout=0.5)
            except Queue.Empty:
                continue


class NotiInput:
    def __init__(self, input, output):
	self.input = input
	self.output = output

    def read(self, size=-1):
        # This may return less data than what was requested
        return self.readline(size)

    def readline(self, size=-1):
	self.output.write(READLINE)
	return self.input.readline(size)
    

class Annex(cmd.Cmd):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    use_rawinput = 0
    prompt = '<Annex> '
    def __init__(self, target, port=None):
	cmd.Cmd.__init__(self)
	if port is None:
	    port = HEAPYPORT
	self.server_address = (LOCALHOST, port)
	self.target = target
	#target.close = target.sys.modules['guppy.heapy.Remote'].IsolatedCaller(
	target.close = IsolatedCaller(
            self.asynch_close)
	self.socket = None
	self.isclosed = 0
	self.closelock = thread.allocate_lock()

	self.intlocals = {
	    }
	self.do_reset('')


    def asynch_close(self):
	# This may be called asynchronously
	# by some other thread than the current (annex) thread.
	# So I need to protect for a possible race condition.
	# It is NOT enough with just an atomic test-and-set here
	# since we need to wait during the time a close initiated
	# from another thread is in progress, before exiting.

	self.closelock.acquire()

        try:
            if not self.isclosed:
                self.isclosed = 1
                self.disconnect()

        finally:
            self.closelock.release()

    def connect(self):
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
	while not self.isclosed:
	    try:
		# print 'connecting'
		self.socket.connect(self.server_address)
	    except SystemExit:
		raise
	    except socket.error:
		if self.isclosed:
		    raise
		time.sleep(2)
	    else:
                break
        else:
            return

        #print 'CONNECTED'
        self.stdout = self.socket.makefile('w', bufsize=0)
        self.stdin = NotiInput(self.socket.makefile('r'), self.stdout)
        self.stderr = sys.stderr

        if sys.version_info < (2, 4):
            self.interruptible = 0
	else:
            self.start_ki_thread()
            self.interruptible = 1

        cmd.Cmd.__init__(self, stdin=self.stdin, stdout=self.stdout)


    def start_ki_thread(self):
        # Start a thread that can generates keyboard interrupr
        # Inserts a spy thread between old stdin and a new stdin

        queue = QueueWithReadline()
        ostdin = self.stdin

        self.stdin = NotiInput(input=queue,
                               output=ostdin.output)


        socket = self.socket
        def run():
            try:
                _hiding_tag_ = self.intlocals['hp']._hiding_tag_
                while socket is self.socket:
                    line = ostdin.input.readline()
                    if not line:
                        break
                    if line == KEYBOARDINTERRUPT:
                        if socket is self.socket:
                            heapyc.set_async_exc(self.target.annex_thread,
                                                 KeyboardInterrupt)
                    else:
                        queue.put(line)
            finally:
                if socket is self.socket:
                    heapyc.set_async_exc(self.target.annex_thread,
                                         SocketClosed) 


        th = threading.Thread(target=run,
                                  args=())

        th.start()




    def disconnect(self):
        socket = self.socket
	if socket is None:
	    return
        self.socket = None
	try:
	    socket.send(DONE)
	except:
	    pass
	try:
	    socket.close()
	except:
	    pass
	sys.last_traceback=None
	sys.exc_clear()

    def do_close(self, arg):
	self.asynch_close()
	return 1

    def help_close(self):
	print >>self.stdout, """close
-----
Close and disable this remote connection completely.  It can then not
be reopened other than by some command from within the target process.

Normally you shouldn't need to use this command, because you can
return to the Monitor via other commands (<Ctrl-C> or .) keeping the
connection open.

But it might be useful when you want to get rid of the remote control
interpreter and thread, if it uses too much memory or disturbs the
target process in some other way."""

    do_h = cmd.Cmd.do_help

    def help_h(self):
        print >>self.stdout, """h(elp)
-----
Without argument, print the list of available commands.
With a command name as argument, print help about that command."""

    help_help = help_h

    def do_int(self, arg):
	# XXX We should really stop other tasks while we use changed stdio files
	# but that seems to be hard to do
	# so this is ok for some practical purposes.
	# --- new note May 8 2005:
	# --- and doesn't matter since we are in a different interpreter -
	# --- so there is no XXX issue ?
	ostdin = sys.stdin
	ostdout = sys.stdout
	ostderr = sys.stderr
	
	try:
            sys.stdin = self.stdin
	    sys.stdout = self.stdout
	    sys.stderr = self.stdout

            con = Console(stdin=sys.stdin,stdout=sys.stdout,
				       locals=self.intlocals)
            con.interact(
                "Remote interactive console. To return to Annex, type %r."%
                con.EOF_key_sequence)



	finally:
	    sys.stdin = ostdin
	    sys.stdout = ostdout
	    sys.stderr = ostderr

    def help_int(self):
	print >>self.stdout, """int
-----
Interactive console.
Bring up a Python console in the Remote Control interpreter.

This console will initially have access to a heapy constructor, named
hpy, and a ready-made instance, named hp, and the target (see also the
reset command).  Other things may be imported as needed.

After returning to the Annex (by q) or to the Monitor (by . or
<Ctrl-C>), the data in the interactive console will remain there - and
will be available till the next time the console is entered.  But the
data may be cleared and reset to the initial state - a new heapy
instance will be created - by the 'reset' command of Annex.

It should be noted that the interpreter thread under investigation is
executing in parallell with the remote control interpreter. So there
may be some problems to do with that if both are executing at the same
time. This has to be dealt with for each case specifically."""


    _bname = 'a1e55f5dc4c9f708311e9f97b8098cd3'


    def do_isolatest(self, arg):
	hp = self.intlocals['hp']
    
	a = []
	self._a = a
	b = []
	self.intlocals[self._bname] = b
	eval('0', self.intlocals) # to make __builtins__ exist if it did not already

	testobjects = [a,
		    b,
		    self.intlocals['__builtins__'],
		    self.intlocals,
		    hp]

	h = hp.heap()
	if hp.iso(*testobjects) & h:
	    print >>self.stdout, 'Isolation test failed.'
	    for i, v in enumerate(testobjects):
		if hp.iso(v) & h:
		    print >>self.stdout, '-- Shortest Path(s) to testobjects[%d] --'%i
		    print >>self.stdout, hp.iso(v).shpaths
	else:
	    print >>self.stdout, 'Isolation test succeeded.'
	
	del self._a
	del self.intlocals[self._bname]

    def help_isolatest(self):
	print >>self.stdout, """isolatest
----------
Isolation test.

Test that the target interpreter heap view is isolated from the data
in the remote control interpreter. Data introduced here, eg in the
interactive console, should not be seen in the heap as reported by
hp.heap() etc. This is achieved by setting hp to not follow the
calling interpreter root.  However, this isolation may become broken.
This test is intended to diagnose this problem. The test checks that
none of a number of test objects is visible in the target heap
view. If the test failed, it will show the shortest path(s) to each of
the test objects that was visible."""

    def do_q(self, arg):
	print >>self.stdout, 'To return to Monitor, type <Ctrl-C> or .'
	print >>self.stdout, "To close this connection ('permanently'), type close"

    def help_q(self):
	print >>self.stdout, """q
-----
Quit.

This doesn't currently do anything except printing a message.  (I
thought it would be too confusing to have a q (quit) command from the
Annex, when there was a similarly named command in the Monitor.)"""


    def do_reset(self, arg):
	self.intlocals.clear()
	self.intlocals.update(
	    {'hpy' : self.hpy,
	     'hp'  : self.hpy(),
	     'target':self.target
	     })
        # Set shorthand h, it is so commonly used
        # and the instance name now used in README example etc
        self.intlocals['h'] = self.intlocals['hp']
	
    def help_reset(self):
	print >>self.stdout, """reset
-----
Reset things to an initial state.

This resets the state of the interactive console data only, for now.
It is reinitialized to contain the following:

hpy	--- from guppy import hpy
hp      --- hp = hpy()
target  --- a reference to some data in the target interpreter
h       --- h = hp; h is a shorthand for hp

(The hpy function is modified here from the normal one so
it sets some options to make it be concerned with the target
interpreter heap under investigation rather than the current one.)
"""

    def do_stat(self, arg):
	print >>self.stdout, "Target overview"
	print >>self.stdout, "------------------------------------"
	print >>self.stdout, "target.sys.executable   = %s"%self.target.sys.executable
	print >>self.stdout, "target.sys.argv         = %s"%self.target.sys.argv
	print >>self.stdout, "target.wd               = %s"%self.target.wd
	print >>self.stdout, "target.pid              = %d"%self.target.pid
	print >>self.stdout, "------------------------------------"
        if not self.interruptible:
            print >>self.stdout, "noninterruptible interactive console"
    
    def help_stat(self):
	print >>self.stdout, """stat
-----
Print an overview status table, with data from the target interpreter.

In the table, sys.executable and sys.argv means the current values of
those attributes in the sys module of the target interpreter. The row
labeled target.wd is the working directory of the target interpreter,
at the time the Remote Control interpreter was started (the actual
working directory may have changed since that time). The row labeled
target.pid is the process id of the target interpreter.

"""
    def hpy(self, *args, **kwds):
	from guppy import hpy
	hp = hpy(*args, **kwds)
	hp.View.is_hiding_calling_interpreter = 1
	hp.View.target = self.target
	self.target.close._hiding_tag_ = hp._hiding_tag_
	hp.reprefix = 'hp.'
	return hp
	
    def run(self):
	try:
	    while not self.isclosed:
		self.connect()
		if not self.isclosed:
                    self.do_stat('')
                    while 1:
                        try:
                            self.cmdloop()
                        except SocketClosed:
                            break
                        except:
                            try:
                                traceback.print_exc(file=self.stdout)
                            except:
				traceback.print_exc(file=sys.stdout)
                                break
                            continue
		self.disconnect()
	finally:
	    # Make sure the thread/interpreter can't terminate
	    # without the annex being closed,
	    # and that we WAIT if someone else is being closing us.
	    self.asynch_close()
	    #print 'Annex DONE'


def on():
    # Start a remote monitoring enabling thread,
    # unless I am that thread myself.
    global annex_thread, target
    if annex_thread is not None:
	return
    if getattr(sys, '_is_guppy_heapy_remote_interpreter_', 0):
        return
    start_annex = """\
# Set a flag to stop recursion when importing site
# in case sitecustomize tries to do Remote.on()
import sys
sys._is_guppy_heapy_remote_interpreter_ = 1
import site
from guppy.heapy import Remote
Remote.Annex(target).run()
"""
    target = Target.Target()
    annex_thread = heapyc.interpreter(start_annex, {'target':target})
    target.annex_thread = annex_thread

def off():
    global annex_thread, target
    if annex_thread is None:
	return 
    for i in range(10):
	try:
	    close = target.close
	except AttributeError:
	    # It may not have been initiated yet.
	    # wait and repeat
	    print 'Can not turn it off yet, waiting..'
	    time.sleep(1)
	else:
	    close()
	    break
    else:
	raise
	
    heapyc.set_async_exc(annex_thread, SystemExit)
    annex_thread = target = None

annex_thread = None
target = None
