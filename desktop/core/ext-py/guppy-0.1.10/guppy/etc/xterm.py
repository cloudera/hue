#._cv_part xterm

# Run an xterm on current process or a forked process

# Adapted from pty.py in Python 1.5.2 distribution.
# The pty.fork() couldnt be used because it didn't return 
# the pty name needed by xterm
# I couldnt import pty.py to use master_open because it didn't find termios.

import os, sys, FCNTL

# We couldnt find termios

STDIN_FILENO, STDOUT_FILENO, STDERR_FILENO = 0, 1, 2

# Open pty master.  Returns (master_fd, tty_name).  SGI and Linux/BSD version.
# Copied from pty.py from Python 1.5.2. /SN

def master_open():
	try:
		import sgi
	except ImportError:
		pass
	else:
		try:
		    tty_name, master_fd = sgi._getpty(FCNTL.O_RDWR, 0666, 0)
		except IOError, msg:
			raise os.error, msg
		return master_fd, tty_name
	for x in 'pqrstuvwxyzPQRST':
		for y in '0123456789abcdef':
			pty_name = '/dev/pty' + x + y
			try:
				fd = os.open(pty_name, FCNTL.O_RDWR)
			except os.error:
				continue
			return (fd, '/dev/tty' + x + y)
	raise os.error, 'out of pty devices'

# Open the pty slave.  Acquire the controlling terminal.
# Returns file descriptor.  Linux version.  (Should be universal? --Guido)
# Copied from pty.py from Python 1.5.2. /SN

def slave_open(tty_name):
	return os.open(tty_name, FCNTL.O_RDWR)


def xterm(prog = None, options=''):
    master_fd, tty_name = master_open()
    pid = os.fork()
    if pid:
	# Acquire controlling terminal.
	slave_fd = slave_open(tty_name)

	# Slave becomes stdin/stdout/stderr of child.
	os.dup2(slave_fd, STDIN_FILENO)
	os.dup2(slave_fd, STDOUT_FILENO)
	os.dup2(slave_fd, STDERR_FILENO)
	if (slave_fd > STDERR_FILENO):
		os.close (slave_fd)
	os.close(master_fd)
	sys.stdin.readline() # Throw away an init string from xterm
	if prog is not None:
	    prog()
    else:
	os.setsid()
	cmd = 'xterm %s -S%s%d'%(options, tty_name[-2:], master_fd)
	os.system(cmd)
	#os.waitpid(pid, 0)
    return pid


def forkxterm(prog = None, options=''):
    pid = os.fork()
    if pid:
	return pid
    else:
	os.setsid()
	pid = xterm(prog, options)
	if not pid:
	    os._exit(0)


def hello():
    print 'hello'
    while 1:
	pass
