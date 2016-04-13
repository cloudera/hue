#._cv_part guppy.heapy.Monitor
import os, pprint, signal, socket, SocketServer, sys, threading, time, traceback
import cPickle as pickle

try:
    import readline # Imported to _enable_ command line editing
except ImportError:
    pass

import select, Queue

from guppy.heapy.RemoteConstants import *
from guppy.heapy.Console import Console
from guppy.sets import mutnodeset
from guppy.etc.etc import ptable
from guppy.etc import cmd

class Server(SocketServer.ThreadingTCPServer):
    pass


def ioready(fd, wait):
    r, w, x = select.select([fd], [], [], wait)
    return len(r)

def queue_get_interruptible(q, noblock=0):
    while 1:
	try:
	    return q.get(timeout=0.2)
	except Queue.Empty:
            if noblock:
                break

# Special value signals that connection has been closed

CONN_CLOSED = ('CLOSED',)

class Handler(SocketServer.StreamRequestHandler):
    allow_reuse_address = 1

    def close(self):
	if not self.isclosed.tas(0):
	    self.server.monitor.remove_connection(self)
	    self.dataq.put(CONN_CLOSED)
	    self.request.shutdown(2)
	    self.request.close()

    def send_cmd(self, cmd):
	if not cmd.endswith('\n'):
	    cmd += '\n'
	self.request.send(cmd)

    def browser_cmd(self, cmd):
	if self.prompt == '>>> ':
	    self.exec_cmd('q', retdata=1)
	if self.prompt == '<Annex> ':
	    self.exec_cmd('cont', retdata=1)
	return self.exec_cmd(cmd, retdata=1)

    def exec_cmd(self, cmd, retdata=0, noblock=0):
	if cmd is not None:
	    self.send_cmd(cmd)
            self.promptstate = False
	datas = []
	while 1:
	    p = queue_get_interruptible(self.dataq, noblock)
            if p is None:
                if self.promptstate:
                    break
                else:
                    time.sleep(1)
                    continue
	    if p is CONN_CLOSED:
		raise EOFError
	    if p[0] == 'DATA':
                self.promptstate = False
		if retdata:
		    datas.append(p[1])
		else:
		    sys.stdout.write(p[1])
	    elif p[0] == 'PROMPT':
		self.prompt = p[1]
                if self.dataq.empty():
                    self.promptstate = True
                    break
                else:
                    self.promptstate = False
	    else:
		assert 0
	if retdata:
	    return ''.join(datas)

    def get_ps(self, name):
	for line in self.firstdata.split('\n'):
	    if line.startswith(name):
                if '=' in line:
                    ix = line.index('=')
                    line = line[ix+1:].strip()
                return line
	return ''

    def get_val(self, expr):
	data = self.browser_cmd('dump %s'%expr)
	return pickle.loads(data)
	

    def handle(self):
	self.prompt = None
        self.promptstate = False
	self.isclosed = mutnodeset()
	self.dataq = Queue.Queue()

	self.server.monitor.add_connection(self)

	while 1:
	    try:
		data = self.rfile.readline()
		if not data:
		    raise EOFError,'End of file'
		if data.endswith(DONE):
		    raise EOFError,'DONE'
	    except (EOFError, socket.error):
		break
	    if data.endswith(READLINE):
		prompt = data[:-len(READLINE)]
		self.dataq.put(('PROMPT',prompt))
		if self.prompt is None:
		    self.firstdata = self.exec_cmd(cmd=None,retdata=1)
	    else:
		self.dataq.put(('DATA',data))
	self.close()

class MonitorConnection(cmd.Cmd):
    use_raw_input = 1

    def __init__(self, monitor):
	self.aliases = {}
	cmd.Cmd.__init__(self)
	self.hno = 0
	self.isclosed = 0
	self.forceexit = 0
	self.prompt = '<Monitor> '


	self.monitor = monitor
	self.server = s = Server((LOCALHOST, HEAPYPORT), Handler)
	self.server.monitor = monitor
        self.st = threading.Thread(target = self.run_server,
                                   args = ())
        self.st.start()

    def close(self):
	self.isclosed = 1
	self.server.socket.shutdown(2)
	self.server.server_close()
	self.server.verify_request = lambda x, y: 0

    def default(self, line):
	cmd.Cmd.default(self, line)
	cmd.Cmd.do_help(self, '')

    def run_server(self):
	s = self.server
	while not self.isclosed:
	    s.handle_request()	    
	s.server_close()

    def exec_cmd(self, cmd):
	if not cmd:
	    # I don't want the repeat of previous command when giving
            # empty command that is provided by cmd.py.
	    # It turned out to be confusing sometimes.
	    return
	line = cmd
	try:
	    line = self.precmd(line)
	    stop = self.onecmd(line)
	    stop = self.postcmd(stop, line)
	    return stop
	except:
	    self.handle_error(line)


    def handle_error(self, cmdline):
	"""Handle an error gracefully.  May be overridden.

	The default is to print a traceback and continue.

	"""
	print >>sys.stderr,'-'*40
	print >>sys.stderr,'Exception happened during processing the command',
	print >>sys.stderr,repr(cmdline)
	import traceback
	traceback.print_exc()
	print >>sys.stderr, '-'*40

    # Alias handling etc copied from pdb.py in Python dist

    def precmd(self, line):
	"""Handle alias expansion and ';;' separator."""
	self.curline = line
	if not line:
	    return line
	args = line.split()
	while self.aliases.has_key(args[0]):
	    line = self.aliases[args[0]]
	    if '%' in line:
		ii = 1
		for tmpArg in args[1:]:
		    line = line.replace("%" + str(ii),
					  tmpArg)
		    line = line.replace('%>=' + str(ii),
					' '.join(args[ii:]))
		    ii = ii + 1
		line = line.replace("%*", ' '.join(args[1:]))
	    else:
		line = line + ' ' + ' '.join(args[1:])
	    args = line.split()
	# split into ';;' separated commands
	# unless it's an alias command
	if args[0] != 'alias':
	    marker = line.find(';;')
	    if marker >= 0:
		# queue up everything after marker
		next = line[marker+2:].lstrip()
		self.cmdqueue.append(next)
		line = line[:marker].rstrip()
	return line


    def do_exit(self, arg):
	self.forceexit = 1
	return 1
	
    def help_exit(self):
	print """exit
-----
Exit from the monitor and from the Python process that started it. 
This makes sure to exit without waiting for the server thread to terminate.
See also the q command."""

    do_h = cmd.Cmd.do_help

    def help_h(self):
        print """h(elp)
-----
Without argument, print the list of available commands.
With a command name as argument, print help about that command."""

    def help_help(self):
        self.help_h()

    def do_int(self, arg):
	try:
	    con = Console(stdin=self.stdin,stdout=self.stdout,
				       locals=self.__dict__)
	    con.interact(
                "Local interactive console. To return to Monitor, type %r."%
                         con.EOF_key_sequence)

	finally:
	    pass

    def help_int(self):
	print """int
-----
Local interactive console.
This will bring up a Python console locally in
the same interpreter process that the Monitor itself."""


    def do_ki(self, arg):
        if not arg:
            arg = self.conid
        arg = int(arg)
        c = self.monitor.connections[arg]
        if c.get_ps('noninterruptible'):
            print '''\
Error: Can not interrupt this remote connection (uses Python < 2.4)'''
        else:
            print 'Sending KeyboardInterrupt to connection %s.'%arg
            c.send_cmd(KEYBOARDINTERRUPT)

    def help_ki(self):
        print """ki <connection ID>
-----
Keyboard Interrupt

Send a command to interrupt the remote thread on the specified
connection (default is the last one connected to).

Notes:

It currently only works with Python >= 2.4.  The remote thread will
not always be awakened, for example if it is waiting in
time.sleep(). Sometimes using several ki commands helps."""
        
    def do_lc(self, arg):
	table = [['CID', 'PID', 'ARGV']]
	for cid, con in self.monitor.connections.items():
	    table.append([cid,
			  con.get_ps('target.pid'),
			  con.get_ps('target.sys.argv')])

	ptable(table, self.stdout)

    def help_lc(self):
	print """lc
-----
List Connections.
List the currently open connections.
The table printed has one line per connection in this form:

CID PID   ARGV
  1 17999 ['/home/nilsson/bin/solitaire.py']

CID is the connection ID, which may be used as argument to the sc
command.

PID is the process ID of the target interpreter process.  In Linux,
this is the parent of the remote control interpreter thread that runs
the Annex that the connection is talking to.

ARGV is the argument vector in the target Python interpereter."""


    def do_sc(self, arg):
	if arg:
	    self.conid = int(arg)
	print 'Remote connection %d. To return to Monitor, type <Ctrl-C> or .<RETURN>'%self.conid
	self.monitor.set_connection(self.monitor.connections[self.conid])

    def help_sc(self):
	print """sc <connection ID>
-----
Set connection to communicate with a remote thread.

With an argument, set current connection to the number specified.
Without argument, use the same connection as last time.  You will then
be talking to a remote process via that connection.  You can return to
Monitor at any time by <Ctrl-C>. You may also use the '.' command
(followed by <Return>), if the remote process is waiting for input.
The '.' character may be followed by a monitor command, to execute it
directly instead of returning to the monitor. For example, when
talking to a connection, '.sc 1' will directly change to connection 1."""

    def do_q(self, arg):
	return 1

    def help_q(self):
	print """q
-----
Quit from the monitor.
This will not exit from Python itself if called from an interactive
interpreter. To make sure to exit from Python, use the exit command."""

class Monitor:
    use_raw_input = 1

    def __init__(self):
	self.connection = self.monitor_connection = MonitorConnection(self)
	self.connections = {}
	self.ids = 0
	self.prompt = None

    def newid(self):
	if not self.connections:
	    self.ids = 1
	    self.monitor_connection.conid = self.ids
	else:
	    self.ids = max([1]+[c for c in self.connections.keys()])+1
	return self.ids

    def add_connection(self, connection):
	hid = self.newid()
	self.connections[hid] = connection
	connection.monitor_id = hid
	self.print_async( '*** Connection %s opened ***'%hid)

    
    def print_async(self, text):
	""" Print text only if we are waiting for input,
	and then restore the prompt. """
	if self.prompt is not None:
	    print '\n'+text
	    sys.stdout.write(self.prompt)
	    sys.stdout.flush()

    def remove_connection(self, connection):
	del self.connections[connection.monitor_id]
	if connection is self.connection:
	    self.set_connection(self.monitor_connection)
	self.print_async( '*** Connection %s closed ***'%connection.monitor_id)

    def run(self):
	try:
	    stop = 0
	    while not stop:
		try:
		    while not stop:
			    conn = self.connection
			    self.prompt = conn.prompt
                            if conn is not self.monitor_connection:
                                conn.exec_cmd(cmd=None,noblock=1)
			    cmd = raw_input(conn.prompt)
			    self.prompt = None
			    conn = None
			    if cmd.startswith('.'):
				if cmd == '.':
				    self.connection = self.monitor_connection
				else:
				    cmd = cmd[1:]
				    conn = self.monitor_connection
                            #elif cmd or self.connection is self.monitor_connection:
                            else:
				conn = self.connection
			    if conn:
				try:
				    r = conn.exec_cmd(cmd)
				except EOFError:
				    r = 1
				if conn is self.monitor_connection and r:
				    stop = 1
				    #print 'to stop'
		    #print 'end of loop'
		except EOFError:
                    'We better exit in case the input is from a file'
		    #print 'EOFError'
		    #print 'Use the monitor q command to quit.'
                    print '*** End Of File - Exiting Monitor ***'
		    self.connection = self.monitor_connection
                    stop = 1
		except KeyboardInterrupt:
		    print 'KeyboardInterrupt'
                    print 'Use the ki command to interrupt a remote process.'
		    self.connection = self.monitor_connection
		    continue
		
	finally:
            self.prompt=None # Avoid closing messages
	    #print 'to close'
	    self.close()

    def close(self):
	for c in self.connections.values():
	    try:
		#print 'to close:', c
		c.close()
	    except socket.error:
		pass
	try:
	    #print 'to close: self'
	    self.monitor_connection.close()
	except socket.error:
	    pass
	if self.monitor_connection.forceexit:
	    os._exit(0)

    def set_connection(self, connection):
	self.connection = connection
	self.prompt = connection.prompt

def monitor():
    """monitor() [0]

Start an interactive remote monitor.

This can be used to get information about the state, in
particular the memory usage, of separately running Python
processes. 

References
    [0] heapy_Use.html#heapykinds.Use.monitor"""
    from guppy.heapy import Remote
    Remote.off()
    m = Monitor()
    m.run()

if __name__ == '__main__':
    monitor()
