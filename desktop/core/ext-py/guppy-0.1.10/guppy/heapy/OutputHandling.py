#._cv_part guppy.heapy.OutputHandling


class OutputHandler:
    def __init__(self, mod, output_file):
	self.mod = mod
	self.output_file = output_file

class OutputBuffer:
    def __init__(self, mod, opts = None):
	self.mod = mod
	self.strio = mod._root.cStringIO.StringIO()

	if opts == None:
	    opts = {}
	self.opts = opts

	self.lines = ['']
	self.line_no = 0

    def getopt(self, opt):
	return self.opts.get(opt)

    def getvalue(self):
	return '\n'.join(self.lines)

    def new_line(self):
	self.line_no += 1
	self.lines.append('')

    def write(self, s):
	lines = s.split('\n')
	for line in lines[:-1]:
	    self.write_seg(line)
	    self.new_line()
	self.write_seg(lines[-1])
	
    def write_seg(self, s):
	self.lines[self.line_no] += s


class MorePrinter:
    _oh_next_lineno = None
    def __init__(self, printer, previous):
	self._oh_printer = printer
	self._oh_previous = previous
	self._hiding_tag_ = printer._hiding_tag_

    def __getattr__(self, attr):
	return self._oh_printer.getattr(self, attr)
	
    def _oh_get_next_lineno(self):
	next_lineno = self._oh_next_lineno
	if next_lineno is None:
	    repr(self)
	    next_lineno = self._oh_next_lineno
	return next_lineno
		
    def _oh_get_start_lineno(self):
	return self._oh_previous._oh_get_next_lineno()

class Printer:
    def __init__(self, mod, client,  get_line_iter=None, max_top_lines=None, max_more_lines=None,
		 get_num_lines = None,
		 get_more_msg = None,
		 get_more_state_msg = None,
		 stop_only_when_told = None
		 ):

	if get_line_iter is None:
	    get_line_iter = client._oh_get_line_iter
	if max_top_lines is None:
	    max_top_lines = mod.max_top_lines
	if max_more_lines is None:
	    max_more_lines = mod.max_more_lines

	self.mod = mod
	self._hiding_tag_ = mod._hiding_tag_
	self.client = client
	self.get_line_iter = get_line_iter 
	self.max_top_lines = max_top_lines
	self.max_more_lines = max_more_lines
	if get_num_lines is not None:
	    self.get_num_lines = get_num_lines
	if get_more_msg is not None:
	    self.get_more_msg = get_more_msg
	if get_more_state_msg is None:
	    get_more_state_msg = getattr(client, '_oh_get_more_state_msg', None)
	if get_more_state_msg is not None:
	    self.get_more_state_msg = get_more_state_msg
	self.stop_only_when_told = stop_only_when_told
	self.reset()

    def getattr(self, mp, attr):
	try:
	    g = getattr(self, '_get_'+attr)
	except AttributeError:
	    return getattr(self.client, attr)
	else:
	    return g(mp)
			
    def line_at(self, idx):
	while idx >= len(self.lines_seen):
	    try:
		li = self.line_iter.next()
	    except StopIteration:
		raise IndexError
	    else:
		if isinstance(li, tuple):
		    cmd, line = li
		    if cmd == 'STOP_AFTER':
			self.stop_linenos[len(self.lines_seen)] = 1
		else:
		    line = li
		self.lines_seen.append(line)
		
	return self.lines_seen[idx]
	
    def lines_from(self, idx=0):
	line_iter = self.line_iter
	if line_iter is None:
	    line_iter = self.line_iter = self.get_line_iter()
	while 1:
	    try:
		yield self.line_at(idx)
	    except IndexError:
		return
	    idx += 1
    

    def _get_more(self, mp):
	return MorePrinter(self, mp)

    def _oh_get_next_lineno(self):
	next_lineno = getattr(self, '_oh_next_lineno', None)
	if next_lineno is None:
	    self.get_str_of_top()
	    next_lineno = self._oh_next_lineno
	return next_lineno
	    
    def _get_prev(self, mp):
	return mp._oh_previous

    def _oh_get_start_lineno(self):
	return 0

    def _get_top(self, mp):
	return self.client

    def _get___repr__(self, mp):
	return lambda: self.get_str(mp, self.max_more_lines)

    _get___str__ = _get___repr__

    def get_str_of_top(self):
	return self.get_str(self, self.max_top_lines)

    def get_more_state_msg(self, start_lineno, end_lineno):
	num_lines = self.get_num_lines()
	if num_lines is None:
	    of_num_lines = ''
	else:
	    of_num_lines = ' of %d'%num_lines
	return "Lines %d..%d%s. "%(start_lineno, end_lineno, of_num_lines)

    def get_more_msg(self, start_lineno, end_lineno):
	state_msg = self.get_more_state_msg(start_lineno, end_lineno)
    	return "<%sType e.g. '_.more' for more.>"%(state_msg)

    def get_num_lines(self):
	return None

    def get_str(self, printer, max_lines):
	def f():
	    _hiding_tag_ = printer._hiding_tag_
	    start_lineno = printer._oh_get_start_lineno()
	    ob = self.mod.output_buffer()
	    it = self.lines_from(start_lineno)
	    numlines = 0
	    lineno = start_lineno
	    for line in it:
		if (numlines >= max_lines and
		    ((not self.stop_only_when_told) or self.stop_linenos.get(lineno-1))) :
		    try:
			self.line_at(lineno+1)
		    except IndexError:
			print >>ob, line
			lineno += 1
			break
		    else:
			print >>ob, self.get_more_msg(start_lineno, lineno-1)
			break
		numlines += 1
		print >>ob, line
		lineno += 1
	    printer._oh_next_lineno = lineno
	    return ob.getvalue().rstrip()

	return printer.mod._parent.View.enter(lambda: f())


	
    def reset(self):
	self.lines_seen = []
	self.stop_linenos = {}
	self.line_iter = None
	
class BasicMorePrinter:
    def __init__(self, mod, top, handler, startindex=None):
	self.mod = mod
	self.top = top

	self.handler = handler
	if startindex is None:
	    startindex = handler.get_more_index()
	self.startindex = startindex
	self._hiding_tag_ = mod._hiding_tag_

    def __getattr__(self, attr):
	if attr == 'more':
	    return self.__class__(self.mod, self.top, self.handler,
			       self.handler.get_more_index(self.startindex))
	else:
	    return getattr(self.top, attr)

    def __repr__(self):
	return self.__str__()

    def __str__(self):
	ob = self.mod.output_buffer()
	self.handler.ppob(ob, self.startindex)
	return ob.getvalue().rstrip()

    def at(self, idx):
	return self.__class__(self.mod, self.top, self.handler,
			   idx)



class _GLUECLAMP_:
    _chgable_ = 'output_file', 'max_top_lines', 'max_more_lines', 
    _preload_ = ('_hiding_tag_',)

    max_top_lines = 10
    max_more_lines = 10

    def _get__hiding_tag_(self):		return self._parent.View._hiding_tag_
    def _get_output_file(self):		return self._root.sys.stdout

    def more_printer(self, client, **kwds):

	printer = Printer(self, client, **kwds)
	return MorePrinter(printer, printer)

    def output_buffer(self):
	return OutputBuffer(self)

    def output_handler(self, output_file=None):
	if output_file is None:
	    output_file = self.output_file
	return OutputHandler(self, output_file)


    def setup_printing(self, client, **kwds):
	more = self.more_printer(client, **kwds)
	printer = more._oh_printer
	client.more = more
	client.printer = printer
	client.__str__ = client.__repr__ = (lambda:
	    printer.get_str_of_top())
	

    def basic_more_printer(self, top, handler, startindex=None):
	return BasicMorePrinter(self, top, handler, startindex)

    def _get_stdout(self):		return self._root.sys.stdout
	
