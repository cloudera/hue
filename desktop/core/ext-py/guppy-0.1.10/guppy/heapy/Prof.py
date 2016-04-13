#._cv_part guppy.heapy.Prof

from Tkinter import *
import tkFileDialog
import tkMessageBox

class MyVar(StringVar):
    _default = 0.0
    def set(self, value):
	StringVar.set(self, '%.2g'%value)

suffixes = ('','K','M','G','T')


def sizestring(value):
    value = float(value)
    sign = 1
    if value < 0:
	sign = -1
	value = - value
    i = 0
    while value > 99999:
	value /= 1000
	i += 1
    s = str(int(round(value)))+suffixes[i]
    if s.endswith('000'+suffixes[i]):
	s = str(int(round(value/1000)))+suffixes[i+1]
    if sign == -1:
	s = '-' + s
    return s

def percentstring(value):
    a = abs(value)
    if 10 <=  a <= 9999:
	return '%d'%round(value)
    elif 0.01 <= a <= 10:
	return '%.2g'%value
    elif a <= 1e-10:
	return '0'
    else:
	return '%.0e'%value


def stringsize(s):
    if s.isdigit():
	return int(s)
    suf = s[-1:].upper()
    mult = 1000l
    for su in suffixes[1:]:
	if su == suf:
	    break
	mult *= 1000
    else:
	raise ValueError
    return int(s[:-1])*mult



class Menu(Menu):
    # A fix for the .delete() method in Menu.
    # To delete commands defined in the menu items deleted.
    # Also changed the comment: INDEX2 is actually INCLUDED.
    def delete(self, index1, index2=None):
        """Delete menu items between INDEX1 and INDEX2 (included)."""
	if index2 is None:
	    index2 = index1
	# First find out what entries have defined commands.
	cmds = []
	for i in range(self.index(index1), self.index(index2)+1):
	    c = str(self.entrycget(i, 'command'))
	    if c in self._tclCommands:
		# I don't want to delete the command already, since it
		# seems mystical to do that while the entry is not yet deleted.
		cmds.append(c)
	# Delete the menu entries.
	self.tk.call(self._w, 'delete', index1, index2)
	# Now that the menu entries have been deleted,
        # we can delete their commands.
	for c in cmds:
	    self.deletecommand(c)



class SizeVar(StringVar):
    _default = 0.0
    def set(self, value):
	self._value = value
	s = sizestring(value)
	StringVar.set(self, s)


class ValueLabel(Label):
    def __init__(self, *args, **kwds):
	kwds['width']=10
	Label.__init__(self, *args, **kwds)

class ClickButton(Button):
    # Button that runs the command directly at the click, not at release.
    # And has auto-repeat.
    def __init__(self, master, command, firstdelay=500,thendelay=150, **kwds):
	Button.__init__(self, master, **kwds)
	self._command = command
	self._firstdelay = firstdelay
	self._thendelay = thendelay
	self.bind('<Button-1>', self._event_button)
	self.bind('<ButtonRelease-1>', self._event_release)
	
    def _event_button(self, event=None):
	self._command()
	if event is not None:
	    delay = self._firstdelay
	else:
	    delay = self._thendelay
	self._after = self.after(delay, self._event_button)

    def _event_release(self, event):
	self.after_cancel(self._after)
	del self._after
	



class Stats:
    def __init__(self, mod, fn=None):
	self.mod = mod
	self.os = mod.os
	self.md5 = mod.md5
	self.fn = fn

    def clear_cache(self):
	# It is intended to be transparently
	# automagically reopened when needed.
	self.stats = None
	del self.stats

    def get_stats(self):
	self.open(self.fn)
	return self.stats

    stats = property(get_stats)

    def collect(self):
	if not self.fn:
	    return 0,0

	stat = self.os.stat(self.fn)
	if stat == self.laststat:
	    return len(self), 0

	f = open(self.fn)
	str = f.read(self.lastfilesize)
	md5 = self.md5.md5(str)
	digest = md5.digest()
	if digest == self.lastdigest:
	    numoldstats = len(self)
	else:
	    self.loadstr(str, reset=1)
	    numoldstats = 0

	str = f.read()
	    
	self.laststat = self.os.fstat(f.fileno())
	f.close()
	self.lastfilesize = self.laststat.st_size

	md5.update(str)
	self.lastdigest = md5.digest()
	self.loadstr(str)

	numnewstats = len(self.stats)-numoldstats

	return numoldstats, numnewstats

    def open(self, fn):
	if not fn:
	    self.len_stats = 0
	    self.stats = []
	    self.max_size = 0
	    self.fn = fn
	    return

	f = open(fn)
	str = f.read()
	lastdigest = self.md5.md5(str).digest()
	laststat = self.os.fstat(f.fileno())
	f.close()
	self.loadstr(str, reset=1)
	    
	# Update these only if there was no exception so far.
	self.fn = fn
	self.lastdigest = lastdigest
	self.laststat = laststat
	self.lastfilesize = laststat.st_size

    def loadstr(self, str, reset=0):
	stats = []
	lines = str.split('\n')
	del str
	linesiter = iter(lines)
	max_size = 0
	while 1:
	    try:
		st = self.mod.Use.load(linesiter)
	    except StopIteration:
		break
	    stats.append(st)
	    if st.size > max_size:
		max_size = st.size

	# Only update self if there were no exception so far

	if reset:
	    self.stats = []
	    self.max_size = 0

	self.max_size = max(self.max_size, max_size)
	self.stats.extend(stats)
	self.len_stats = len(self.stats)


    def __getitem__(self, idx):
	return self.stats[idx]
	
    def __len__(self):
	try:
	    return self.len_stats
	except AttributeError:
	    self.len_stats = len(self.stats)
	    return self.len_stats

    def get_max_size(self):
	return self.max_size


class ProfileRow:
    kindwidth = 30
    def __init__(self, master, row, usecolor=1):
	self.master = master
	self.row = row
	if usecolor:
	    colbg = Frame(master=master,bg='black',width=1, borderwidth=1, relief=GROOVE)
	    self.color = Label(master=colbg,bg='white',width=1, borderwidth=1, relief=GROOVE)
	    self.color.grid(row=0, column=0)
	    colbg.grid(row=row,column=0, sticky=NW)

	self.rsizevar = SizeVar()
	self.rsize = Label(master=master, textvariable=self.rsizevar, width=6,anchor=E)
	self.rpercentvar = StringVar() #BBIntVar()
	self.rpercent = Label(master=master,textvariable=self.rpercentvar, width=3,anchor=E)
	self.dsizevar = SizeVar()
	self.dsize = Label(master=master, textvariable=self.dsizevar, width=6,anchor=E)
	self.dpercentvar = StringVar() #BBIntVar()
	self.dpercent = Label(master=master,textvariable=self.dpercentvar, width=3,anchor=E)
	self.kindvar = StringVar()
	self.kind = Label(master=master, textvariable=self.kindvar, anchor=NW,
			  width=self.kindwidth ,justify=LEFT)

	self.rsize.grid(row=row, column=1, sticky=NE)
	self.rpercent.grid(row=row,column=2,sticky=NE)
	self.dsize.grid(row=row,column=3,sticky=NE)
	self.dpercent.grid(row=row,column=4,sticky=NE)
	self.kind.grid(row=row, column=5, sticky=NW)

    def set_color_size_percent_kind(self, color, rsize, rpercent, dsize, dpercent, kind):
	self.set_color(color)
	if color is not None:
	    self.set_color(color)
	self.rsizevar.set(rsize)
	if rpercent is None:
	    rpercent = ''
	else:
	    rpercent = str(int(round(rpercent)))
	self.rpercentvar.set(rpercent)

	self.dsizevar.set(dsize)
	dpercent = str(int(round(dpercent)))
	self.dpercentvar.set(dpercent)

	self.set_kind(kind)
	
    def set_color(self, color):
	self.color.configure(bg=color)

    def set_kind(self, kind):
	self.kindtext = kind

	if len(kind) > self.kindwidth:
	    import textwrap
	    kind = textwrap.fill(kind, width=self.kindwidth)
	self.kindvar.set(kind)

    def clear(self):
	self.set_color_size_percent_kind(self.master['bg'], 0, 0, 0, 0, '--')


class AxisControl:
    scale_table = [1l, 2l, 5l]
    while scale_table[-1] < 1e12:
	scale_table.append(scale_table[-3] * 10l)

    def __init__(self, master,
		 name,
		 range,
		 grid,
		 unit,
		 rangecommand,
		 gridcommand,
		 autocommand=None
		 ):
	small = 0


	self.name = name
	self.unit = unit
	self.range = range
	self.rangecommand = rangecommand

	self.frame = frame = Frame(master,borderwidth=2,relief=GROOVE)
	
	self.rangevar = SizeVar()
	self.rangevar.set(range)
	if 1:
	    rangeval = Entry(master=self.frame,
			     # anchor=E,
			     width=4,
			     textvar=self.rangevar,
			     #font=('fixed', '16', 'bold'),
			     #font=('terminal', '16', 'bold'),
			     #font=('terminal', '14'),
			     font=('fixed', '14'),
			     #bg='black',fg='yellow'
			     bg='#fdd'
			     )
	    rangeval.bind('<KeyPress-Return>',self.event_range_enter)

	elif 1:
	    rangeval = Button(master=self.frame,
			     anchor=E,
			     width=4,
			     textvar=self.rangevar,
			     #font=('fixed', '16', 'bold'),
			     font=('terminal', '16', 'bold'),
			     bg='black',fg='yellow')

	else:
	    rangeval = Listbox(
		self.frame,
		height=1,
		width=4,
		font=('terminal', '16', 'bold'),
		bg='black',fg='yellow')
	    for scale in self.scale_table:
		s = sizestring(scale)
		rangeval.insert(0, s)


	namelabel = Menubutton(frame, text=name, relief='raised', anchor=W)

	namemenu = Menu(namelabel)
	namelabel['menu']=namemenu

	if autocommand:
	    self.autovar = BooleanVar()
	    self.autovar.set(True)
	    namemenu.add_checkbutton(
		#autobutton = Checkbutton(frame,
			       label='Auto',
			       variable=self.autovar,
			       command = autocommand,
			       #relief=RAISED
			       )
	    autobutton = Checkbutton(frame,
				     text='Auto',
				     variable=self.autovar,
				     command = autocommand,
				     relief=RAISED
			       )



	else:
	    self.autovar = None

	if gridcommand:
	    self.gridvar = BooleanVar()
	    self.gridvar.set(grid)
	    namemenu.add_checkbutton(
			       label='Grid',
			       variable=self.gridvar,
			       command = lambda: gridcommand(self.gridvar.get()),
			       )


	    gridbutton = Checkbutton(frame,
				     text='Grid',
				     variable=self.gridvar,
				     command = lambda: gridcommand(self.gridvar.get()),
				     relief=RAISED
			       )




	rangelabel = Label(frame, text='Range')

	if name == 'Y' and small:
	    padx = 5
	    pady = 0
	else:
	    padx = 3
	    pady = 3
	ud = Frame(frame)
	rangeup = ClickButton(ud, text='+',
			 pady=pady,padx=padx,
			 font=('fixed',8),
			 command=lambda:self.range_button(1))

	rangedown = ClickButton(ud, text='-',
			 pady=pady,padx=padx,
			 font=('fixed',8),
			 command=lambda:self.range_button(-1))

	rangedown.grid(row=0,column=0)
	rangeup.grid(row=0,column=1)
	row=0
	
	if small and name == 'Y':
	    namelabel.grid(row=0, rowspan=1,column=0)
	    rangeup.grid(row=0, column=1, sticky=W)

	    autobutton.grid(row=1,column=0)

	    rangedown.grid(row=1, column=1, sticky=W)
	    rangeval.grid(row=2, column=0, columnspan=2,sticky=W,padx=3, pady=3)

	elif small and name == 'X':
	    namelabel.grid(row=0, column=0)
	    rangeval.grid(row=0, column=1,sticky=W,padx=3, pady=3)
	    rangedown.grid(row=0, column=2, sticky=W)
	    rangeup.grid(row=0, column=3, sticky=W)

	else:
	    namelabel.grid(row=row, column=0, sticky=N+W,ipadx=0,ipady=0,padx=2,pady=2)
	    rangelabel.grid(row=row, column=1, sticky=W)
	    ud.grid(row=row,column=2, padx=2)
	    row += 1
	    
	    if gridcommand:
		gridbutton.grid(row=row, column=0, sticky=W)
		    
	    rangeval.grid(row=row, column=1, padx=3, pady=3)
	    if autocommand:
		pass
		autobutton.grid(row=row,column=2)
	    

    def cmd_range(self):
	pass

    def event_range_enter(self, event):
	str = self.rangevar.get()
	try:
	    rng = stringsize(str)
	    if rng not in self.scale_table:
		if not 1 <= rng <= self.scale_table[-1]:
		    raise ValueError
	except:
	    self.frame.bell()
	    self.errorbox("""\
Invalid range entry.
It should be a positive integer with an optional multiplier:
K, M, G, or T
(1000, 1e6, 1e9, 1e12)
Maximum range is 1T.""")

	    self.rangevar.set(self.range)
	else:
	    if self.autovar:
		self.autovar.set(False)
	    self.setrange(rng)

    def auto_command(self):
	pass

    def errorbox(self, msg):
	tkMessageBox.showerror(master=self.frame, message=msg)

    def fit(self, range):
	range = self.scale_by_table(range)
	self.setrange(range)

    def range_button(self, d):
	if self.autovar:
	    self.autovar.set(False)
	self.range_change(d)

    def range_change(self, d):
	range = self.range
	srange = self.scale_by_table(range)
	if srange > range:
	    if d > 0:
		d -= 1
	i = self.scale_table.index(srange)
	i += d
	if i >= len(self.scale_table):
	    i = len(self.scale_table) - 1
	if i < 0:
	    i = 0
	
	self.setrange(self.scale_table[i])

    def setrange(self, range):
	if range != self.range:
	    self.range = range
	    self.rangevar.set(range)
	    self.rangecommand(range)

    def scale_by_table(self, s):
	# Return the scale from table that is higher or equal to s
	for ts in self.scale_table:
	    if ts >= s:
		return ts
	return self.scale_table[-1]

WM = 1

class Marker:
    def __init__(self, d, tag, name, pos, poscommand=None):
	self.d = d
	self.tag = tag
	self.name = name
	self.xmarker = pos
	self.butdown = 0
	self.ocursor = d.ocursor
	self.cursor = self.ocursor
	self.poscommand = None
	self.intpos = None
	self.moving = 0
	self.selected = 0
	self.entered = 0
	self.butdownselected = 0
	self.motion_id = None
	self.create()

    def bind(self, sequence, function):
	tag = self.tag
	self.d.drawingarea.tag_bind(tag, sequence, function)
	if WM:
	    self.xlabel.bind(sequence, function)
	else:
	    self.d.xmarks.tag_bind(tag, sequence, function)

    def coords(self, canx):
	self.d.drawingarea.coords(self.tag,
				canx, 0,
				canx,-int(self.d.boty))
	
	self.d.xmarks.coords(self.tag, canx, 10)


    def create(self):
	tag = self.tag
	text = self.name
	pos = 0

	if 1:
	    self.d.drawingarea.create_line(pos, 0, pos, 20-self.d.boty, stipple='gray12',
			  width=4,tags=(tag,))
	if WM:
	    label = self.xlabel = Label(self.d.xmarks, text=text, padx=2,pady=2,relief=RAISED)
	    self.d.xmarks.create_window(pos, 0, window=label, tags=(tag,))
	else:
	    self.d.xmarks.create_text(pos, 0, text=text, tags=(tag,))

	self.bind('<Button-1>', self.event_button_1)
	self.bind('<ButtonRelease-1>', self.event_button_1_release)
	self.bind('<Enter>', self.event_enter)
	self.bind('<Leave>', self.event_leave)

	self.d.drawingarea.bind('<Enter>', self.event_enter_movearea, add='+')
	self.d.drawingarea.bind('<Button-1>', self.event_button_1_movearea, add='+')

    def event_button_1(self, event):
	self.butdown = 1
	if self.selected:
	    self.butdownselected = 1
	    if self.moving:
		self.event_stop_move(event)
	else:
	    self.butdownselected = 0
	
	
	self.has_moved = 0
	self.event_selected(event)
	self.event_start_move(event)

    def event_button_1_movearea(self, event):
	if not self.entered:
	    self.event_deselected(event)

    def event_button_1_release(self, event):
	self.butdown = 0
	if self.has_moved == self.butdownselected:
	    if self.selected:
		if self.moving and not (self.disloy <= event.y_root < self.dishiy):
		    self.event_stop_move(None)
		    self.setcursor(self.ocursor)
	    else:
		self.setcursor(self.ocursor)
	    return
	self.event_deselected(event)
	
    def event_deselected(self, event):
	if self.selected:
	    self.selected = 0
	    self.xlabel['relief'] = RAISED
	    if self.moving:
		self.event_stop_move(event)

    def event_enter(self, event):
	self.entered = 1
	if not self.moving:
	    if self.selected:
		self.event_start_move(event)
	    else:
		self.setcursor('hand2')

    def event_enter_movearea(self, event):
	if self.selected and not self.moving:
	    self.event_start_move(event)

    def event_leave(self, event):
	self.entered = 0
	if not self.moving:
	    self.setcursor(self.ocursor)
	elif not (self.fraloy <= event.y_root < self.frahiy):
	    pass

    def event_motion(self, event):
	self.has_moved = 1
	if 0: # Simple variant - get back
	    if not (self.fraloy <= event.y_root < self.frahiy):
		self.event_button_1_release(self.down_event)
		return

	inside = (self.fraloy <= event.y_root < self.frahiy)

	if inside != self.inside:
	    self.inside = inside
	    if not inside:
		self.out_event = event
		self.event_stop_move(None)
		if self.butdown:
		    self.setcursor('circle')
		    self.d.bind_motion(self.event_motion_downout)
	    else:
		self.in_event = event
		#self.delta += self.out_event.x_root - event.x_root
		self.event_start_move(event)
		return
	
	if inside:
	    self.moved(event)
	    self.setxvars()

    def event_motion_downout(self, event):
	# We don't get an enter while button is pressed down
	# Emulate an enter if we detect entering
	inside = (self.fraloy <= event.y_root < self.frahiy)
	if inside:
	    self.d.unbind_motion(self.event_motion_downout)
	    self.event_enter_movearea(event)

    def event_selected(self, event):
	for m in self.d.marks:
	    m.event_deselected(event)
	self.selected = 1
	self.xlabel['relief'] = SUNKEN

    def event_start_move(self, event):
	self.moving = 1
	self.fralox = self.d.frame.winfo_rootx()
	self.frahix = self.fralox + self.d.frame.winfo_width()

	self.fraloy = self.d.frame.winfo_rooty()
	self.frahiy = self.fraloy + self.d.frame.winfo_height()

	self.dislox = self.d.drawingarea.winfo_rootx()
	self.dishix = self.dislox + self.d.drawingarea.winfo_width()
	self.disloy = self.d.drawingarea.winfo_rooty()
	self.dishiy = self.disloy + self.d.drawingarea.winfo_height()

	self.down_event = event
	self.prev_event = event
	self.down_xmarker = self.xmarker
	self.down_xvfrac = self.d.drawingarea.xview()[0]
	self.inside = 1
	self.delta = 0
	self.lift()
	    
	self.motion_id = self.d.bind_motion(self.event_motion)
	self.moved(event)
	
    def event_stop_move(self, event):
	assert self.moving
	self.moving = 0

	self.d.unbind_motion(self.motion_id)
	if event is not None:
	    self.moved(event)
	    self.setxvars()
	
	if self.entered and not self.selected:
	    self.setcursor('hand2')
	else:
	    self.setcursor(self.ocursor)

    def lift(self):
	self.d.xmarks.tag_raise(self.tag)
	if WM:
	    self.xlabel.lift()
	self.d.drawingarea.tag_raise(self.tag)

    def move(self, sample):
	canx = self.d.canxscaled(sample)
	self.d.xview_pos(canx)
	self.coords(canx)
	self.xmarker = sample
	self.lift()

    def moved(self, event):
	curx = event.x_root
	cury = event.y_root
	prevx = self.prev_event.x_root

	if prevx > self.dishix and curx < self.dishix:
	    prevx = self.dishix
	elif prevx < self.dislox and curx > self.dislox:
	    prevx = self.dislox

	markx = self.d.canxscaled(self.xmarker) - self.d.drawingarea.canvasx(0) + self.dislox

	dx = curx - prevx
	l = r = 1
	
	if self.xmarker >= self.d.numstats-1:
	    r = 0

	if self.xmarker <= 0:
	    l = 0

	stop = 0

	# Should we allow to move it back or not
	# if it is at an endpoint?
	# Here we don't move it at all, to make marker pos correspond
	# more closely with mouse position.

	if ((r == 0 and curx > markx) or (l == 0 and curx < markx)):
	    l = r = 0

	if self.butdown:
	    if curx > self.dishix:
		l = 0
	    elif curx < self.dislox:
		r = 0
	else:
	    if not (self.dislox <= curx < self.dishix and
		    self.disloy <= cury < self.dishiy):
		l = r = 0
		stop = 1

	if l and r:
	    self.setcursor('sb_h_double_arrow')
	elif l:
	    self.setcursor('sb_left_arrow')
	    if dx > 0:
		dx = 0
	elif r:
	    self.setcursor('sb_right_arrow')
	    if dx < 0:
		dx = 0
	else:
	    self.setcursor('dot')
	    dx = 0

	self.prev_event = event

	sample = self.d.limitx(self.xmarker + dx / self.d.xscale)
	canx = self.d.canxscaled(sample)
	self.d.xview_pos(canx)
	self.coords(canx)
	self.xmarker = sample
	if stop and self.moving:
	    self.event_stop_move(None)

    def set(self):
	canx = self.d.canxscaled(self.xmarker)
	self.coords(canx)
	self.lift()

    def set_poscommand(self, command):
	self.poscommand = command
	self.intpos = None

    def setcursor(self, cursor):
	if cursor != self.cursor:
	    self.xlabel['cursor'] = cursor
	    self.cursor = cursor
	self.d.setcursor(cursor)

    def setxvars(self):
	if self.poscommand:
	    intpos = int(round(self.xmarker))
	    if intpos != self.intpos:
		self.intpos = intpos
		self.poscommand(intpos)

class Display:
    orgwidth = 300
    orgheight = 300
    minwidth = 30
    minheight = 30
    def __init__(self, master,
		 scale_table,
		 numkindrows, 
		 getkindcolor,
		 xrange=100,
		 yrange=100,
		 xgrid = False,
		 ygrid = False,
		 graphtype = 'Bars',
		 statype = 'Size',
		 ):
	self.master = master
	self.scale_table = scale_table
	self.numkindrows = numkindrows
	self.getkindcolor = getkindcolor
	self.xrange = xrange
	self.yrange = yrange
	self.xgrid = xgrid
	self.var_xgrid = BooleanVar(xgrid)
	self.var_xgrid.set(xgrid)
	self.var_ygrid = BooleanVar(xgrid)
	self.ygrid = ygrid
	self.var_ygrid.set(ygrid)
	self.graphtype = graphtype
	self.statype = statype


	self.numstats = 0
	self.ymaxs = []
	self.ymins = []
	self.ymax = 1


	# To get around problems with dynamic unbinding / unbinding of motion,
	# I handle it myself. in the bind_motion method using the following.
	self.bound_motions = {}
	self.event_motion_id = None
	#


	self.frame = frame = Frame(master,
				   borderwidth=3,
				   relief=SUNKEN,
				   #relief=GROOVE,
				   #background='green'
				   )
	#self.frame = frame = Frame(master,background='green')

	bordercolor = '#ccc'
	screencolor = '#e0e0e0'
	xscrollincrement = 1
	frame = Frame(self.frame)
	frame.grid(row=0,column=0)
	#move = Frame(frame, height=10,width=10,background='red', relief=RAISED)
	#move = Button(self.frame, height=10,width=10,background='red')
	self.drawingarea = C = Canvas(frame,
				      width=self.orgwidth,
				      height=self.orgheight,
				      xscrollincrement=xscrollincrement,
				      #background='black',
				      background = screencolor,
				      bd=0,
				      xscrollcommand = self.xscrollbar_set,
				      #confine=False,
				      )

	#self.yctrlframe = Frame(frame, borderwidth=2,relief=GROOVE)
	self.yscrollbar = Scrollbar(frame, orient = VERTICAL, width=10)
	#self.yscrollbar['command']=self.drawingarea.yview
	#self.drawingarea['yscrollcommand'] = self.yscrollbar_set
	#self.yscrollbar.pack(side=RIGHT,fill=Y)
	#self.yctrlframe.grid(row = 0, column = 0,sticky=N+S,padx=3,pady=3)

	self.xaxis = Canvas(frame,
			    width=C['width'],
			    height=20,
			    xscrollincrement=xscrollincrement,
			    bd=0,
			    background = bordercolor,
			    #xscrollcommand = self.xscrollbar_set
			    #confine=False,
			    )
	self.xmarks = Canvas(frame,
			     width=C['width'],
			     height=20,
			     xscrollincrement=xscrollincrement,
			     bd=0,
			     background = bordercolor,
			     #xscrollcommand = self.xscrollbar_set
			     #confine=False,
			    )
	self.yaxis = Canvas(frame, height=C['height'],width=50,
			    bd=0,
			    background = bordercolor,
			    )
	

	self.xscrollbar = Scrollbar(frame, orient=HORIZONTAL,
				    command=self.drawingarea_xview,
				    width=12,
			    background = bordercolor,

				    )


	xy = Canvas(frame, width=50,height=20,bd=0,
		    background = bordercolor,
		    )


	#

	if 0:
	    self.yaxis.grid(row = 0, column = 0)
	    self.yscrollbar.grid(row=0,column=2, sticky=N+S)
	    C.grid(row = 0, column = 1, sticky=W+E )
	    xy.grid(row=1,column=0)
	    self.xaxis.grid(row = 1, column = 1)

	    self.xscrollbar.grid(row=2,column=1,sticky=E+W)
	    self.rsbut.grid(row=2,column=2)
	else:
	    var_yrange = SizeVar()
	    self.var_yrange = var_yrange

	    row = 0

	    Label(frame,
		  textvar=var_yrange,
		  bd=0,
		  relief=FLAT,
		  background=bordercolor).grid(
		      row=row,
		      column=0,
		      sticky=W+E+N+S)


	    self.xscrollbar.grid(row=row,column=1,sticky=E+W)

	    row += 1

	    self.yunit = Label(frame,
		  text='Bytes',
		  bd=0,
		  relief=FLAT,
		  background=bordercolor)
	    self.yunit.grid(
		      row=row,
		      column=0,
		      sticky=W+E+N+S)


	    self.xmarks.grid(row=row, column=1,sticky=W+E+N)

	    row += 1

	    self.yaxis.grid(row = row, column = 0)
	    C.grid(row = row, column = 1, sticky=W+E )

	    row += 1

	    xy.grid(row=row,column=0)
	    self.xaxis.grid(row = row, column = 1,sticky=W+E+N)

	#

	self.botx = float(C['width'])
	self.boty = float(C['height'])
	self.chdim = self.getchdim()
	self.canx0 = 0
	self.tmax = 0
	self.xscale = self.botx / self.xrange
	self.yscale = self.boty / self.yrange
	self.xi0 = None
	

	xy.create_line(0,2,44,2)
	xy.create_line(49, 6,49,22)
	xy.create_text(25, 14, text='Sample')

	self.setscrollregion()

	self.ocursor = self.drawingarea['cursor']
	self.cursor = self.ocursor

	self.marks = []

    def bind_motion(self, function):
	if self.event_motion_id == None:
	    self.event_motion_id = self.frame.bind_all('<Motion>', self.event_motion, add='+')
	self.bound_motions[function] = self.bound_motions.get(function, 0) + 1
	return function
	    
    def event_motion(self, event):
	for f in self.bound_motions.keys():
	    f(event)

    def unbind_motion(self, funcid):
	n = self.bound_motions[funcid] - 1
	if n == 0:
	    del self.bound_motions[funcid]
	else:
	    self.bound_motions[funcid] = n
	

    def new_xmarker(self, name = None, pos=0):
	tag = 'M%d'%len(self.marks)
	if name is None:
	    name = tag
	m = Marker(self, tag, name, pos)
	self.marks.append(m)
	return m


    def canxscaled(self, x):
	return x * self.xscale + self.canx0

    def canyscaled(self, y):
	return - y * self.yscale

    def cmd_xgrid(self):
	self.xgrid = self.var_xgrid.get()
	self.drawxaxis()
	
    def cmd_ygrid(self):
	self.ygrid = self.var_ygrid.get()
	self.drawyaxis()
	
    def cmd_yrange_auto(self):
	self.ymax = None
	self.yrange_auto()

    def limitx(self, x):
	lo = 0
	hi = max(0, self.numstats-1)
	if x < lo:
	    return lo
	if x > hi:
	    return hi
	return x

    def resize(self, dx, dy):
	x =  self.botx + dx
	y = self.boty + dy
	if x < self.minwidth:
	    x = self.minwidth
	    dx = x - self.botx
	if  y < self.minheight:
	    y = self.minheight
	    dy = y - self.boty


	xv = self.drawingarea.xview()
	yv = self.drawingarea.yview()

	self.drawingarea.configure(width=x, height=y)
	self.xaxis.configure(width=x)
	self.xmarks.configure(width=x)
	self.yaxis.configure(height=y)

	xscale = float(x) / self.xrange
	yscale = float(y) / self.yrange
	
	xscaleorg = self.drawingarea.canvasx(0)
	yscaleorg = 0

	xq = xscale / self.xscale
	yq = yscale / self.yscale

	self.drawingarea.scale("all",xscaleorg, yscaleorg, xq, yq)
	#self.drawingarea.scale("barsep",xscaleorg, yscaleorg, xq, yq)
	#self.drawingarea.scale("xmarker",xscaleorg, yscaleorg, xq, yq)

	self.canx0 = xscaleorg + (self.canx0 - xscaleorg) * xq

	self.botx = x
	self.boty = y
	self.xscale = xscale
	self.yscale = yscale

	self.drawxaxis()
	self.drawyaxis()

	self.setscrollregion()

	# If the size changed much, the canvas may scroll though it shouldn't.
	# Notes 11 and 26 Oct 2005 .
	# I save the current scroll position.
	# The caller has to call the .moveback() method some time later.
	self.wantedpos = xv[0]

	return dx, dy

    def moveback(self):
	self.frame.update_idletasks() 
	self.xview(MOVETO, self.wantedpos)

    def draw():
	self.drawxaxis()
	self.drawyaxis()


    def draw_stat(self, idx, stat):
	graphtype = self.graphtype
	statype = self.statype

	rows = stat.get_rows_n_and_other(self.numkindrows, statype)
	if statype == 'Size':
	    kindval = dict([(r.name, r.size) for r in rows])
	else:
	    kindval = dict([(r.name, r.count) for r in rows])
	order = [r.name for r in rows]

	order.reverse()

	lastkindval = self.lastkindval
	self.lastkindval = kindval

	C = self.drawingarea

	yscale = self.yscale
	xscale = self.xscale

	x0 = idx * xscale - 0.5 * xscale + self.canx0
	x1 = x0 + xscale
	ymax = 0
	ymin = 0

	y = 0

	bw = 0.05*xscale
	
	ocolor = None
	for k in order:
	    dy = kindval.get(k, 0)
	    if not dy:
		continue
	    color = self.getkindcolor(k)
	    
	    if graphtype == 'Bars':
		line = C.create_rectangle(x0+bw, -y*yscale,
					  x1-bw, -(y+dy)*yscale,
					  fill=color,
					  outline=color,
					  width = 0,
					  tags=("a",))
		if color == ocolor:
		    C.create_line(x0, -(y)*yscale, 
				  x1, -(y)*yscale, 
				  fill='black',
				  tags=('barsep',))
		ocolor = color
		y += dy
	    elif graphtype == 'Lines':
		if dy > ymax:
		    ymax = dy
		elif dy < ymin:
		    ymin =  dy
		y0 = lastkindval.get(k)
		if y0 is None:
		    y0 = dy
		    x00 = x0
		else:
		    x00 = x0 - 0.4 * xscale
		    C.create_line(x00,  - y0 * yscale,
				  x1 - 0.6 * xscale,  - dy * yscale,
				  fill=color,
				  tags=('a',))

		if 1:
		    C.create_line(x1 - 0.6 * xscale,  - dy * yscale,
				  x1 - 0.4 * xscale,  - dy * yscale,
				  fill=color,
				  width = 4,
				  tags=('a',))

		else:
		    C.create_rectangle(x1 - 0.6 * xscale,  - dy * yscale,
				  x1 - 0.4 * xscale,  - dy * yscale,
				  fill=color,
				  outline=color,
				  width = 2,
				  tags=('a',))


		
		
	if graphtype == 'Bars':
	    if y > ymax:
		ymax = y
	    elif y < ymin:
		ymin = y
	
	assert idx == len(self.ymaxs) == len(self.ymins)
	self.ymaxs.append(ymax)
	self.ymins.append(ymin)
	

	if idx > self.tmax:
	    self.tmax = idx
	

    def drawingarea_xview(self, cmd, what, unit=None):
	if cmd == 'scroll' and unit == 'units':
	    what = int(max(2, self.xscale)*int(what))
	    
	self.xview(cmd, what, unit)


    def setcursor(self, cursor):
	if cursor != self.cursor:
	    self.drawingarea['cursor'] = cursor
	    self.master['cursor'] = cursor
	    self.cursor = cursor

    def xmarkers_set(self):
	for m in self.marks:
	    m.set()

    def xview(self, *args):
	if not args:
	    return self.drawingarea.xview()
	self.drawingarea.xview(*args)
	self.xaxis.xview(*args)
	self.xmarks.xview(*args)

    def xview_moveto(self, fraction):
	self.xview(MOVETO, fraction)

    def xview_pos(self, pos, fraction=None, leftmargin = 5, rightmargin = 5):
	# Scroll canvas view, if necessary, so that something
	# (eg an x marker) at canvas position pos will be visible
	# with minimum specified margin at left and right.
	# Scroll relative to fraction; default is current xview position.

	if fraction is None:
	    fraction = self.xview()[0]

	x1, y1, x2, y2 = self.scrollregion

	cc = x1 + fraction * (x2 - x1)

	xm = pos - cc

	lo = leftmargin
	hi = self.botx - rightmargin

	if xm < lo:
	    dx = xm - lo
	    xm = lo
	elif xm >= hi:
	    dx = (xm - hi)
	    xm = hi
	else:
	    dx = 0

	r = fraction + dx / float(x2 - x1)
	self.xview_moveto(r)

    def drawxaxis(self):
	scale_table = self.scale_table
	self.xaxis.delete('all')
	self.drawingarea.delete('xgrid')
	x1, y1, x2, y2 = self.scrollregion
	
	chdx, chdy = self.chdim

	i = 0
	while (scale_table[i] * self.xscale <
	       min(5, len(str(scale_table[i] * self.tmax))) * chdx):
	    i+=1
	self.xstep = scale_table[i]


	divisuf = (
	    (1000000000000l, '%dT'),
	    (1000000000l, '%dG'),
	    (1000000,  '%dM'),
	    (1000,  '%dK'),
	    (1, '%d')
	    )

	for divi, form in divisuf:
	    if self.xstep >=divi:
		break

	self.xdivi = divi
	self.xform = form


	self.xi0 = 0
	self.updatexaxis()

    def updatexaxis(self):

	chdx, chdy = self.chdim
	step = self.xstep

	gridon = self.xgrid


	for i in range(self.xi0, self.tmax+step, step):
	    x = self.canx0 + i*self.xscale
	    self.xaxis.create_line(x, 0, x, 4)
	    if gridon:
		self.drawingarea.create_line(x, 0, x, -self.boty,
					     tags=('xgrid',),width=2,stipple="gray25")
	    text = self.xform%(i / self.xdivi)
	    self.xaxis.create_text(x, chdy,  text=text)

	self.xaxis.create_line(self.canx0 + self.xi0*self.xscale, 1, x+self.xscale, 1)
	    
	self.xi0 = i
	self.xmarkers_set()


    def drawyaxis(self):

	gridon = self.ygrid

	self.yaxis.delete('all')
	self.drawingarea.delete('ygrid')
	
	chdx, chdy = self.getchdim()

	width = int(self.yaxis['width'])
	i = 0
	maxval = self.yrange

	while (self.scale_table[i] * self.yscale < 1.5 * chdy):
	    i+=1
	step = self.scale_table[i]

	divisuf = (
	    (1000000000000l, '%4dT'),
	    (1000000000l, '%4dG'),
	    (1000000,  '%4dM'),
	    (1000,  '%4dK'),
	    (1, '%5d')
	    )

	for divi, form in divisuf:
	    if step >=divi:
		break

	for i in range(0, maxval+step, step):
	    y =  - i*self.yscale
	    self.yaxis.create_line(width-3, y, width-1, y)
	    if gridon:
		self.drawingarea.create_line(self.scrollregion[0], y,
					     self.scrollregion[2], y,
					     stipple="gray25",
					     tags=('ygrid',))
	    if 0 and i == 0:
		text = '0 bytes'
	    else:
		text = form % (i / divi)
	    self.yaxis.create_text(chdx*2.5, y-0.5*chdy,  text=text)

	#self.yaxis.create_text(chdx*2.5, 0.5*chdy, text='bytes')

	self.yaxis.create_line(width-1, 0, width-1, -self.boty)
	self.xmarkers_set()
	    


    def getchdim(self):
	ch = self.xaxis.create_text(0, 0, text='0')
	x1, y1, x2, y2 = self.xaxis.bbox(ch)
	self.xaxis.delete(ch)
	chdx = abs(x2 - x1)
	chdy = abs(y2 - y1)

	return chdx, chdy

    def load_stats(self, stats):

	ocursor = self.frame.winfo_toplevel()['cursor']
	try:
	    self.frame.winfo_toplevel()['cursor'] = 'watch'
	    self.frame.update()

	    self.numstats = len(stats)

	    self.lastkindval = {}
	    self.tmax = 0
	    self.ymax = None
	    self.ymaxs = []
	    self.ymins = []

	    C = self.drawingarea

	    C.delete('barsep')
	    C.delete('a')


	    for (i, st) in enumerate(stats):
		self.draw_stat(i, st)

	    try:
		self.drawingarea.tag_raise('barsep', 'a')
	    except TclError:
		pass # May be 'tagOrId "a" doesn't match any items' if empty!

	    self.drawxaxis()
	    self.drawyaxis()
	    self.xmarkers_set()
	    self.yrange_auto()
	finally:
	    self.frame.winfo_toplevel()['cursor'] = ocursor

    def add_stats(self, stats):
	for (i, st) in enumerate(stats):
	    self.draw_stat(i+self.numstats, st)
	self.numstats += len(stats)
	self.updatexaxis()
	self.setscrollregion()

    def setxgrid(self, grid):
	self.xgrid = grid
	self.drawxaxis()

    def setygrid(self, grid):
	self.ygrid = grid
	self.drawyaxis()

    def setgraphtype(self, gmode, stats):
	graphtype, statype = gmode.split(' ')
	if graphtype != self.graphtype or statype != self.statype:
	    self.graphtype = graphtype
	    self.statype = statype
	    if statype == 'Size':
		self.yunit['text'] = 'Bytes'
	    elif statype == 'Count':
		self.yunit['text'] = 'Objects'
	    else:
		raise ValueError
	    self.load_stats(stats)

    def setscrollregion(self):
	C = self.drawingarea
	botx = self.botx
	x1 = self.canx0
	x2 = self.tmax * self.xscale + self.canx0
	if 0:
	    x1extra = botx
	    x2extra = botx
	if 1:
	    x1extra = botx / 2 + 2 #max(5, self.xscale*0.5)
	    x2extra = botx / 2 + 2 #max(5, self.xscale*0.5)
	if 0:
	    x1extra = x2extra = max(5, self.xscale * 0.5)
	
	x1 -= x1extra
	x2 += x2extra
	
	y1 = 1-self.boty
	y2 = 1

	if 0:
	    try:
		_x1, _y1, _x2, _y2 = self.scrollregion
	    except:
		pass
	    else:
		if (abs(_x2 - x2) < x2extra / 2 and
		    abs(_x1 - x1) < x1extra / 2 
		    ):
		    return
	    
	self.scrollregion = (x1, y1, x2, y2)
	C.configure(scrollregion = self.scrollregion)
	    
	self.xaxis.configure(scrollregion = (x1, 0, x2, 10))
	self.xmarks.configure(scrollregion = (x1, 0, x2, 20))
	self.yaxis.configure(scrollregion = (0, y1, 20, y2))
	

	self.drawingarea.yview(MOVETO, 0.0)

    def setxrange(self, xrange):
	dxrange = self.xrange / float(xrange)
	self.xrange = xrange
	xscaleorg = self.drawingarea.canvasx(self.botx/2)
	self.drawingarea.scale("a",xscaleorg, 0, dxrange, 1.0)
	self.drawingarea.scale("barsep",xscaleorg, 0, dxrange, 1.0)
	self.canx0 = xscaleorg + (self.canx0 - xscaleorg) * dxrange
	self.xscale = self.botx / float(self.xrange)
	self.setxscrollincrement(max(2, self.xscale))
	self.drawxaxis()
	self.setscrollregion()

    def setxscrollincrement(self, dx):
	return
	self.drawingarea.configure(xscrollincrement=dx)
	self.xaxis.configure(xscrollincrement=dx)
	self.xmarks.configure(xscrollincrement=dx)


    def setyrange(self, yrange):

	dyrange = float(self.yrange) / yrange
	self.yrange = yrange
	self.var_yrange.set(yrange)
	
	self.drawingarea.scale("a",0, 0, 1.0, dyrange)
	self.drawingarea.scale("barsep",0, 0, 1.0, dyrange)
	self.yscale = float(self.boty) / self.yrange
	self.drawingarea.yview(MOVETO, 0.0)
	self.drawyaxis()


    def xscrollbar_set(self, first, last):
	self.xscrollbar.set(first, last)
	self.yrange_auto()
    
    def yrange_auto(self, force=0):
	if force or self.ycontrol.autovar.get():
	    lo = max(0,
		     int(0.5+(self.drawingarea.canvasx(0) - self.canx0) / self.xscale))
	    hi = min(len(self.ymaxs),
		     int(1.5+(self.drawingarea.canvasx(self.botx) - self.canx0) / self.xscale))
	    if lo == hi:
		ymax = 1
	    else:
		ymax = max(self.ymaxs[lo:hi])
	    if ymax != self.ymax:
		self.ymax = ymax
		self.ycontrol.fit(ymax)



class MarkerControl:
    def __init__(self, master,
		 marker,
		 setcommand = lambda:0
		 ):
	self.sample = 0
	self.numsamples = 0
	self.setcommand = setcommand
	self.marker = marker
	self.name = marker.name
	sf = self.frame = Frame(master, borderwidth=2,relief=GROOVE)
	self.samplevar = SizeVar()
	Label(sf, text='%s sample'%marker.name).grid(row = 0, column = 0)
	Label(sf,
	      textvariable=self.samplevar,
	      font=('terminal', '16', 'bold'),
	      bg='black',fg='yellow'
	      ).grid(row = 1, column = 0, padx=3,pady=3)
	ClickButton(sf, text='-',
	       pady=0,padx=5,
	       command=lambda:self.changesample(-1)).grid(row=0,column=1, sticky=E)
	ClickButton(sf, text='+',
	       pady=0,padx=5,
	       command=lambda:self.changesample(1)).grid(row=0,column=2, sticky=W)
	self.trackingvar = BooleanVar()
	self.trackbutton = Checkbutton(
	    sf, text='Track',
	    padx=5,
	    
	    variable = self.trackingvar,
	    relief=RAISED,
	    command=self.settracking,
	    indicatoron=1,
	    )
	self.trackbutton.grid(row=1,column=1,columnspan=2)

    def changesample(self, d):
	sample = self.sample + d
	if 0 <= sample < self.numsamples:
	    self.setmarker(sample)

    def setmarker(self, sample):
	self.marker.move(sample)
	self.setsample(sample)

    def setnumsamples(self, num):
	self.numsamples = num
	if self.trackingvar.get() or self.sample >= self.numsamples:
	    self.setmarker(max(0, self.numsamples-1))

    def setsample(self, sample):
	self.sample = sample
	self.samplevar.set(sample)
	self.setcommand()

    def settracking(self, tracking=None):
	if tracking is not None:
	    self.trackingvar.set(tracking)
	else:
	    tracking = self.trackingvar.get()
	if tracking:
	    self.setmarker(max(0, self.numsamples-1))

class Window:
    def __init__(self, app, frame, windowmenu=None):
	self.app = app
	self.frame = frame
	self.windowmenu = windowmenu
	self.wtitle = frame.title()
	self._is_destroyed = 0
	# Binding to <destroy> didnt work well:
	#   frame.bind('<Destroy>', self.event_destroy, add='+')
	# I give up. I modify .destroy of frame argument instead.
	self.old_destroy = frame.destroy
	frame.destroy = self.new_destroy

    def new_destroy(self):
	if self._is_destroyed:
	    return
	self._is_destroyed = 1
	self.app.del_window(self)
	try:
	    self.old_destroy()
	except TclError:
	    # This may happen at closing last window
	    # because exit destroys the root when it sees all windows were closed.
	    # So I ignore it.
	    pass

    def title(self, title):
	self.frame.title(title)
	self.frame.iconname(title)
	self.wtitle = title
	self.app.chg_window(self)

    def wakeup(self):
	frame = self.frame
        try:
            if frame.wm_state() == "iconic":
                frame.wm_deiconify()
	    frame.tkraise()
	    # I don't think I want .focus_set: it behaved strange in X at least.
	    #frame.focus_set()
        except TclError:
            # This can happen when the window menu was torn off.
            # Simply ignore it.
            pass


class WindowMenu:
    def __init__(self, frame, variable):
	self.button = Menubutton(frame, text='Window')
	self.menu = Menu(self.button)
	self.button['menu'] = self.menu
	self.variable = variable
	self.wmap = {}

    def add_window(self, window):
	self.menu.add_radiobutton(
	    command = window.wakeup,
	    label='%d %s'%(window.wid, window.wtitle),
	    value=window.wid,
	    variable=self.variable)
	self.wmap[window.wid] = self.menu.index(END)
	
    def chg_window(self, window):
	self.menu.delete(self.wmap[window.wid])
	self.menu.insert_radiobutton(
	    self.wmap[window.wid],
	    command = window.wakeup,
	    label='%d %s'%(window.wid, window.wtitle),
	    value=window.wid,
	    variable=self.variable)

    def del_window(self, window):
	idx = self.wmap[window.wid]
	del self.wmap[window.wid]
	try:
	    self.menu.delete(idx)
	except TclError:
	    # This can happen if the menu was destroyed before its contents.
	    # Simply ignore it.
	    pass
	for wid in self.wmap.keys():
	    if self.wmap[wid] > idx:
		self.wmap[wid] -= 1


class ProfileApp:
    def __init__(self, mod):
	self.mod = mod
	root = Tk()
	self.root = root
	root.withdraw()
	self.windows = {}
	self.windowmenus = {}
	self.var_window = IntVar(root)

    def add_window(self, window):
	window.wid = max([0]+self.windows.keys())+1
	self.windows[window.wid] = window
	wm = getattr(window, 'windowmenu', None)
	if wm:
	    self.windowmenus[window.wid] = wm
	    for w in self.windows.values():
		if w is not window:
		    wm.add_window(w)
	for wm in self.windowmenus.values():
	    wm.add_window(window)
	self.var_window.set(window.wid)
	window.frame.bind('<FocusIn>',
			  lambda event:self.var_window.set(window.wid), add='+')
	window.frame.bind('<Deactivate>',
			  lambda event:self.var_window.set(0), add='+')

    def add_window_frame(self, frame, windowmenu=None):
	w = Window(self, frame, windowmenu)
	self.add_window(w)
	return w

    def chg_window(self, window):
	for wm in self.windowmenus.values():
	    wm.chg_window(window)

    def del_window(self, window):
	wid = window.wid
	if getattr(window, 'windowmenu', None):
	    del self.windowmenus[wid]
	del self.windows[wid]
	for wm in self.windowmenus.values():
	    wm.del_window(window)
	if not self.windows:
	    self.exit()
	
    def exit(self):
	try:
	    self.root.destroy()
	except TclError:
	    pass
	self.root.quit()

    def mainloop(self):
	return self.root.mainloop()

    def new_profile_browser(self, filename):
	return ProfileBrowser(self, filename)

class PaneDiv:
    def __init__(self, master, movecommand):
	self.frame = frame = Frame(master)
	self.movecommand = movecommand
	
	self.butsize = bs = 6
	bc = self.butcent = bs / 2 + 3
	h = 10
	self.top = Canvas(
	    frame,
	    width=10,
	    height=h,
	    )

	self.top.create_line(
	    bc,0,bc,h,fill='#808080', width=1)
	self.top.create_line(
	    bc+1,0,bc+1,h,fill='white', width=1)

	self.rsbut = Canvas(
	    frame,
	    cursor='crosshair',
	    width=self.butsize,
	    height=self.butsize,
	    relief=RAISED,
	    bd=2
	    )

	self.bot = Canvas(
	    frame,
	    width=10,
	    height=300,
	    bd=0
	    )

	self.top.grid(row=0,column=0, sticky=N)
	self.rsbut.grid(row=1,column=0, sticky=N)
	self.bot.grid(row=2,column=0, sticky=N)

	self.rsbut.bind('<Button-1>',self.but_down)
	self.rsbut.bind('<ButtonRelease-1>', self.but_up)

    def but_down(self, event):
	self.down_event = event
	self.rsbut.configure(relief=SUNKEN)

    def but_up(self, event):
	self.rsbut.configure(relief=RAISED)
	dx = event.x - self.down_event.x
	self.movecommand(dx)


    def setheight(self, height):
	h = height - 18
	self.bot['height'] = h

	bc = self.butcent

	self.bot.create_line(
		bc,0,bc,h,fill='#808080', width=1)
	self.bot.create_line(
	    bc+1,0,bc+1,h,fill='white', width=1)



class TableFrame:
    def __init__(self, graph, master, numkindrows, samplevar):
	self.graph = graph
	self.mod = graph.mod
	frame = self.frame = Frame(master,borderwidth=2,relief=GROOVE)
	row = 0
	self.marktime = StringVar()
	self.totsizevar = SizeVar()
	self.sampler = StringVar()
	self.sampler.set('R')

	if 1:
	    fr = Frame(frame) # For header
	    om = OptionMenu(fr, self.sampler, 'R', 'L', 'R-L')
	    om.grid(row=0,column=0,sticky=W)
	    Label(fr, text='Sample').grid(row=0,column=1,sticky=W)
	    Label(fr, textvariable=samplevar,background='black',foreground='yellow',
		  ).grid(row=0,column=2,sticky=W, pady=3)
	    Label(fr, text='at').grid(row=0,column=3,sticky=W)
	    Label(fr, textvariable=self.marktime).grid(row = 0, column = 4, sticky=W)
	    Label(fr, text='Total size = ').grid(row=1,column=0,columnspan=3,sticky=W)
	    Label(fr, textvar=self.totsizevar).grid(row=1,column=3,columnspan=2,sticky=W)
	    fr.grid(row=row, column=0, sticky=W)
	    row += 1

	orow = row

	tb = Frame(frame)
	row = 0

	Label(tb, text="").grid(row=row, column=0)
	Label(tb, text="R", ).grid(row=row, column=1, sticky=E)
	Label(tb, text="%R").grid(row=row, column=2, sticky=E)
	Label(tb, text="R-L", ).grid(row=row, column=3, sticky=E)
	Label(tb, text="%L").grid(row=row, column=4, sticky=E)
	Label(tb, text="Kind").grid(row=row, column=5, sticky=W)

	row += 1
	self.profrows = []
	self.totrow = ProfileRow(tb, row)
	self.profrows.append(self.totrow)
	row += 1

	for i in range(numkindrows+1):
	    profrow = ProfileRow(tb, row)
	    self.profrows.append(profrow)
	    row += 1

	row = orow
	tb.grid(row=row, column=0, sticky=W)


	# for next..
	row += 1

	self.totresize = 0
	self.kindwidth = ProfileRow.kindwidth

    def resize(self, dx, dy):
	dx = int(dx)
	self.totresize += dx
	charresize, extra = divmod(self.totresize, 7)
	newwidth = ProfileRow.kindwidth + charresize
	oldwidth = self.profrows[0].kind['width']
	if newwidth < 10:
	    newwidth = 10
	    dx = (newwidth - oldwidth) * 7 + extra
	for pr in self.profrows:
	    pr.kind['width'] = newwidth
	    pr.kindwidth = newwidth
	    pr.kind['padx'] = extra / 2
	    import textwrap
	    kindtext = textwrap.fill(pr.kindtext, width=pr.kindwidth)
	    pr.set_kind(pr.kindtext)


	return dx, dy

    def update(self, lsamp, rsamp):

	self.marktime.set(self.mod.time.asctime(self.mod.time.localtime(rsamp.stat.timemade)))

	return

	for pr in self.profrows:
	    pr.clear()

	rdiv = float(rsamp.stat.size)
	ldiv = float(lsamp.stat.size)

	self.totrow.set_color_size_percent_kind(
	    None,
	    rsamp.stat.size,
	    100.0,
	    rsamp.stat.size - lsamp.stat.size,
	    (rsamp.stat.size - lsamp.stat.size) * 100.0 / ldiv,
	    '<Total>'
	    )

	for i, r in enumerate(rsamp.rows):
	    l = lsamp.kindrows[r.name]
	    self.profrows[i+1].set_color_size_percent_kind(
		self.graph.getkindcolor(r.name),
		r.size,
		r.size * 100.0 / rdiv,
		r.size - l.size,
		(r.size - l.size) * 100.0 / ldiv,
		r.name)
	
	
class ColSpec:
    def __init__(self, tf, header, width, pos, render, idx=()):
	self.tf = tf
	self.header = header
	self.name = header
	self.width = width
	self.pos = pos
	self.render = render
	self.idx = idx

    def align(self, text):
	sp = ' '*(self.width - len(text))
	if self.pos == LEFT:
	    text = text + sp
	elif self.pos == RIGHT:
	    text = sp[:-1] + text + ' '
	else:
	    assert 0
	assert len(text) == self.width
	return text
		

class TableFrame:
    def __init__(self, graph, master):
	self.graph = graph
	self.mod = graph.mod

	frame = self.frame = Frame(
	    master,
	    borderwidth=3,
	    relief=SUNKEN
	    )

	self.colspecs = {}
	self.colwidths = []

	def defcol(names, width, pos, put, idxfunc = lambda x:()):
	    if callable(put):
		put = [put]*len(names)
	    self.colwidths.append(width)
	    for name, put in zip(names, put):
		spec = ColSpec(self, name, width, pos, put, idxfunc(name))
		self.colspecs[name] = spec


	defcol(('A', 'B'), 2, LEFT, self.putcolor, lambda x:x)
	defcol(('Size', 'Count'), 7, RIGHT, [self.putsize, self.putcount])
	defcol(('%A:Tot', '%B:Tot'), 7, RIGHT, self.putpercent, lambda name:name[1])
	defcol(('B-A', 'A-B', 'Cumul'), 7, RIGHT, [self.putdiff, self.putdiff, self.putcumul],
	       lambda name:[(),name.split('-')]['-' in name])
	defcol(('%A:Tot', '%B:Tot'), 7, RIGHT, self.putpercent, lambda name:name[1])
	defcol(('Kind',), 20, LEFT, self.putkind)


	width = 0
	for w in self.colwidths:
	    width += w
	self.totxresize = 0
	self.totyresize = 0
	self.kindcol = self.colspecs['Kind']
	self.orgkindwidth = self.kindcol.width
	self.widthbeforekind = width - self.orgkindwidth
	self.minkindwidth = 10
	self.mintextheight = 2
	width += 1
	self.width = self.orgwidth = width

	wrap = NONE
	cursor = master['cursor']
	relief = FLAT
	self.minpadx = 3
	self.tothead = Text(
	    frame,
	    width=width,
	    wrap=wrap,
	    background='#ccc',
	    height=2,
	    padx=self.minpadx,
	    relief=relief,
	    cursor=cursor,
	    )

	self.rowhead = Text(
	    frame,
	    width=width,
	    wrap=wrap,
	    background='#ccc',
	    height=1,
	    padx=self.minpadx,
	    relief=relief,
	    cursor=cursor,
	    )

	self.tsframe = Frame(frame)

	self.textminpady = 2
	self.text = Text(
	    self.tsframe,
	    width=width,
	    wrap=wrap,
	    height=21,
	    background='#e0e0e0',
	    relief=relief,
	    takefocus=0,
	    cursor=cursor,
	    padx=self.minpadx,
	    pady=self.textminpady,
	    )

	self.scrollbar = Scrollbar(
	    self.tsframe,
	    width=10,
	    orient=VERTICAL,
	    command=self.text.yview
	    )
	self.scrollbar_totwidth = int(self.scrollbar['width']) + 6 # width + padding

	self.uses_scrollbar = 0
	self.auto_scrollbar = 1


	self.orgtextheight = int(self.text['height'])

	padx = 0
	pady = 0
	self.tothead.pack(anchor=N+W, padx=padx, pady=pady)
	self.rowhead.pack(anchor=N+W, padx=padx, pady=pady)
	self.text.pack(side=LEFT,anchor=N+W, padx=padx, pady=pady)
	self.tsframe.pack(anchor=N+W, padx=padx, pady=pady)

	
    def setchdim(self):
	self.text.update()
	self.chdx = float(self.text.winfo_width()) / self.width
	self.chdy = float(self.text.winfo_height()) / self.orgtextheight
	self.chdx = int(round(self.chdx))
	self.chdy = int(round(self.chdy))
	self.pixwidth = self.width * self.chdx
	self.pixheight = self.width * self.chdy


    def putcolor(self, col):
	if self.colorow.name == '<Total>':
	    text = col.align(' ')
	    color = '#e0e0e0'
	else:
	    color = self.graph.getkindcolor(self.colorow.name),
	    text = col.align('@')
	self.text.insert('end', text, (color,))
	self.text.tag_config(color,foreground=color, background='#e0e0e0',
			     font=('terminal', '12', 'bold'),)
		     
    def putcount(self, col):
	self.valmode = 'Count'
	count = self.colorow.count
	self.cumulval += count
	self.putval(col, count)

    def putsize(self, col):
	self.valmode = 'Size'
	size = self.colorow.size
	self.cumulval += size
	self.putval(col, size)
    
    def putval(self, col, val):
	self.curval = val
	self.ap(col.align(sizestring(val)))
    
    def putpercent(self, col):
	a = self.statbyname[col.idx]

	if self.valmode == 'Count':
	    ref = a.count
	elif self.valmode == 'Size':
	    ref = a.size

	if ref:
	    ps = percentstring(self.curval * 100.0 / ref)
	else:
	    ps = '---'
	self.ap(col.align(ps))
    
    def putdiff(self, col):

	a, b = self.rowbyname[col.idx[0]], self.rowbyname[col.idx[1]]
	if self.valmode == 'Count':
	    a, b = a.count, b.count
	elif self.valmode == 'Size':
	    a, b = a.size, b.size

	self.putval(col, a - b)
    
    def putcumul(self, col):
	self.putval(col, self.cumulval)
	
    def putkind(self, col):
	# Must be last!
	import textwrap
	wraplines = textwrap.wrap(self.colorow.name, width=col.width)
	self.ap(col.align(wraplines[0]))
	if len(wraplines) > 1:
	    initial = '\n'+' '*(self.widthbeforekind)
	    for line in wraplines[1:]:
		self.ap(initial+col.align(line))

    def setmode(self, mode, numkindrows):
	self.mode = mode
	self.numkindrows = numkindrows
	self.mcontrols = self.graph.mcontrolbyname
	self.stats = self.graph.stats
	self.cols = [self.colspecs[x.strip()] for x in mode.split(' ') if x.strip()]
	self.controlnames = {}
	name = self.cols[0].idx
	self.colorcontrol = self.mcontrols[name]
	self.controlnames[name] = 1
	self.controls = [self.colorcontrol]
	self.lastidxs = [None]
	for i, co in enumerate(self.cols):
	    idx = co.idx
	    if not isinstance(idx, (tuple, list)):
		idx = (idx,)
	    for idx in idx:
		if idx not in self.controlnames:
		    self.controls.append(self.mcontrols[idx])
		    self.controlnames[idx] = 1
		    self.lastidxs.append(None)

    def setscrollbar(self, sb):
	if sb == self.uses_scrollbar:
	    return
	self.uses_scrollbar = sb
	w = self.scrollbar_totwidth
	if sb:
	    self.resize(-w, 0, setscrollbar=0)
	    self.scrollbar.pack(side=LEFT, fill=Y)
	    self.text['yscrollcommand'] = self.scrollbar.set
	else:
	    self.resize(w, 0, setscrollbar=0)
	    self.scrollbar.pack_forget()
	    self.text['yscrollcommand'] = None
	    
	    

    def update_simple(self, lsamp, rsamp):
	t = self.text
	t.delete('1.0', '100.0')
	t.insert('1.0', str(rsamp.stat))

    def update(self, force=0, setscrollbar=1):

	stats = self.stats

	idxs = [max(0, min(control.sample, len(stats)-1)) for control in self.controls]
	if (idxs == self.lastidxs) and not force:
	    return

	self.lastidxs = idxs

	self.text['state'] = self.tothead['state'] = self.rowhead['state'] = NORMAL

	self.text.delete('1.0', END)
	self.tothead.delete('1.0', END)
	self.rowhead.delete('1.0', END)

	if not stats:
	    self.tothead.insert('end', '-- No Sample --')
	    self.text['state'] = self.tothead['state'] = self.rowhead['state'] = DISABLED
	    return

	
	self.statbyname = {}
	statbyidx = []
	for i, control in enumerate(self.controls):
	    stat = stats[idxs[i]]
	    statbyidx.append(stat)
	    self.statbyname[control.name] = stat


	samps = self.samps = [
	    Sample(self.mod, statbyidx[0], self.controls[0].marker.name, idxs[0],
		   numkindrows=self.numkindrows,
		   statype = self.graph.display.statype
		   )]

	self.colorsamp = samps[0]
	if len(self.controls) > 1:
	    samps.append(Sample(self.mod, statbyidx[1], self.controls[1].marker.name, idxs[1],
				relative=samps[0]))

	    self.relsamp = samps[1]



	t = self.tothead

	n = max([len(str(samp.index)) for samp in samps])
	for samp in samps:
	    t.insert('end', 'Sample %s: '%samp.name)
	    t.insert('end', ('%%%dd'%n)%samp.index, ('index',))
	    t.insert('end', ' at %s\n' % (samp.datetime))

	t.tag_configure('index', background='#e0e0e0')

	t = self.rowhead

	self.sizes = [float(samp.stat.size) for samp in samps]

	for col in self.cols:
	    t.insert('end', col.align(col.header), ('header',))
	t.insert('end', '\n')

	t = self.text

	self.ap = lambda text:t.insert('end', text)

	self.colorow = Row(samps[0].count, samps[0].size, '<Total>')
	self.rowbyname = self.statbyname
	self.cumulval = 0
	for col in self.cols:
	    col.render(col)
	self.ap('\n\n')

	self.cumulval = 0
	for i, a in enumerate(samps[0].rows):
	    self.colorow = a
	    if len(samps) > 1:
		self.rowbyname = {
		    samps[0].name:a,
		    samps[1].name:samps[1].kindrows[a.name]
		    }
	    for col in self.cols:
		col.render(col)
	    self.ap('\n')

	if setscrollbar and self.auto_scrollbar:
	    numrows = int(self.text.index('end').split('.')[0])-2
	    h = int(self.text['height'])
	    needs_scrollbar = numrows > h
	    if needs_scrollbar != self.uses_scrollbar:
		self.setscrollbar(needs_scrollbar)

	self.text['state'] = self.tothead['state'] = self.rowhead['state'] = DISABLED

    def resize(self, dx, dy, setscrollbar=1):
	dx = int(dx)
	oldwidth = self.pixwidth
	newwidth = self.pixwidth + dx
	if newwidth < self.chdx * 2:
	    newwidth = self.chdx * 2

	self.pixwidth = newwidth
	dx = newwidth - oldwidth

	charwidth, extra = divmod(newwidth, self.chdx)

	self.kindcol.width = max(charwidth - self.widthbeforekind - 1, self.minkindwidth)
	    
	self.totxresize += dx
	for t in (self.tothead, self.rowhead, self.text):
	    t['width'] = charwidth
	    t['padx'] =  self.minpadx + extra / 2


	dy = int(dy)

	rowresize, extra = divmod(self.totyresize + dy, self.chdy)
	newheight = self.orgtextheight + rowresize
	oldheight = int(self.text['height'])
	if newheight < self.mintextheight:
	    newheight = self.mintextheight
	    dy = (newheight - oldheight) * self.chdy + extra
	self.totyresize += dy

	self.text['height'] = newheight
	self.text['pady'] = self.textminpady + extra / 2

	self.update(force=1, setscrollbar=1)

	return dx, dy




class Filler:
    def __init__(self, master):
	self.frame = self.can = Canvas(
	    master,
	    #background='blue',
	    width=0,
	    height=0)

    def getsize(self):
	return int(self.can['width']),int(self.can['height']),

    def setsize(self, w, h):
	self.can.configure(
	    width = w,
	    height = h
	    )

    def resize(self, dw, dh):
	w, h = self.getsize()
	self.setsize(max(0, w + dw), max(0, h + dh))


class Row:
    def __init__(self, count, size, name):
	self.count = count
	self.size = size
	self.name = name

class Sample:
    def __init__(self, mod, stat, name, index, numkindrows=None, statype='Size', relative=None):
	self.stat = stat
	self.size = stat.size
	self.count = stat.count
	self.name = name
	self.index = index

	self.datetime = mod.time.asctime(mod.time.localtime(stat.timemade))

	self.kindrows = {}

	if numkindrows is not None:
	    rows = stat.get_rows_n_and_other(numkindrows, statype)
	    for r in rows:
		self.kindrows[r.name] = r
	else:
	    kinds = []
	    oidx = None
	    for row in relative.rows:
		if row.name == '<Other>':
		    oidx = len(kinds)
		    continue
		else:
		    kinds.append(row.name)

	    rows = stat.get_rows_of_kinds(kinds)
	    size = 0
	    count = 0
	    for i, row in enumerate(rows):
		kind = kinds[i]
		if row is None:
		    row = Row(0, 0, kind)
		self.kindrows[kind] = row
		size += row.size
		count += row.count

	    if oidx is not None:
		other = Row(stat.count - count, stat.size - size, '<Other>')
		rows[oidx:oidx] = [other]
		self.kindrows['<Other>'] = other

	self.rows = rows


class ProfileBrowser:
    colors = ("red", "green", "blue", "yellow", "magenta", "cyan", 'white')
    numkindrows = 10

    def __init__(self, app, filename):
	self.inited = 0
	self.app = app
	self.mod = mod = app.mod
	self.master = master = app.root
	if filename:
	    filename = mod.path.abspath(filename)
	    self.initialdir = mod.path.dirname(filename)
	else:
	    self.initialdir = mod.os.getcwd()
    
	self.frame = frame = Toplevel(
	    master,
	    #background='#bbb'
	    )
	#frame['cursor'] = 'umbrella'
	#frame.resizable(True,True)

	self.menubar = Frame(self.frame, relief=RAISED, bd=2)

	self.filebutton = Menubutton(self.menubar, text='File')
	self.filemenu = Menu(self.filebutton)
	self.filebutton['menu'] = self.filemenu
	self.filemenu.add_command(label='New Profile Browser', command=self.cmd_new)
	self.filemenu.add_command(label='Open Profile', command=self.cmd_open)
	self.filemenu.add_command(label='Close Window', command=self.cmd_close)
	self.filemenu.add_command(label='Clear Cache', command=self.cmd_clear_cache)
	self.filemenu.add_command(label='Exit', command=self.cmd_exit)
	self.panebutton = Menubutton(self.menubar, text='Pane')
	self.panemenu = Menu(self.panebutton)
	self.panebutton['menu'] = self.panemenu

	choices = [
	    ('Bars', 'Lines'),
	    ('Size', 'Count'),
	    ]

	self.graphtypevar = StringVar()
	self.graphbutton = self.modechooser(
	    self.menubar, 'Graph', choices,
	    self.graphtypevar, self.cmd_graphtype)

	choices = [
	    ('A', 'B'),
	    ('Size', 'Count'),
	    ('%A:Tot', '%B:Tot'),
	    ('Cumul', 'A-B', 'B-A'),
	    ('%A:Tot', '%B:Tot'),
	    ('Kind',),
	    ]
	    
	self.var_tablemode=StringVar()
	self.tablebutton = Menubutton(self.menubar, text='Table')
	self.tablemenu = Menu(self.tablebutton)
	self.tablebutton['menu'] = self.tablemenu
	self.headermenu = Menu(self.tablebutton, title='Table header')
	self.addmodechooser(
	    self.headermenu,
	    choices,
	    self.var_tablemode,
	    self.cmd_tablemode
	    )
	self.tablemenu.add_cascade(label='Header',menu=self.headermenu)
	self.var_tablescrollbar = StringVar()
	self.tablescrollbarmenu = Menu(self.tablebutton, title = 'Table scrollbar')

	self.addmodechooser(
	    self.tablescrollbarmenu,
	    [('Auto', 'On', 'Off')],
	    self.var_tablescrollbar,
	    self.cmd_tablescrollbar
	    )

	self.tablemenu.add_cascade(
	    label='Scrollbar',
	    menu = self.tablescrollbarmenu)

	self.windowmenu = WindowMenu(self.menubar, self.app.var_window)
	self.window = app.add_window_frame(self.frame, self.windowmenu)

	self.helpbutton = Menubutton(self.menubar, text='Help')
	self.helpmenu = Menu(self.helpbutton)
	self.helpbutton['menu'] = self.helpmenu
	self.helpmenu.add_command(label='About', command=self.cmd_about)
	self.helpmenu.add_command(label='Help', command=self.cmd_help)


	self.ctrlframe = Frame(
	    self.frame,
	    bd=2,
	    relief=GROOVE,
	    #background='#999',
	    
	    
	    )


	self.exitbutton = Button(self.ctrlframe, text='Exit', command=self.cmd_exit,
				 background='red')



	self.set_filename(filename)


	self.id_collect = None
	self.collecting = IntVar()
	self.collecting.set(0)
	self.collectbutton = Checkbutton(self.ctrlframe, text='Collect',
				       variable = self.collecting,
					 command=self.cmd_collect,
					 relief=RAISED)


	self.stats = Stats(self.mod)

	self.disptab = Frame(self.frame,
			     #relief=SUNKEN,
			     #bd=3
			     )

	self.display = Display(self.disptab, 
			       scale_table = AxisControl.scale_table,
			       numkindrows = self.numkindrows,
			       getkindcolor = self.getkindcolor,
			       )

	self.xcontrol = AxisControl(self.ctrlframe,
				    name = 'X',
				    range = self.display.xrange, 
				    grid = self.display.xgrid,
				    unit = 'samples',
				    rangecommand = self.display.setxrange,
				    gridcommand = self.display.setxgrid
				    )


	self.ycontrol = AxisControl(self.ctrlframe,
				    name = 'Y',
				    range = self.display.yrange,
				    grid = self.display.ygrid,
				    unit = 'bytes',
				    rangecommand = self.display.setyrange,
				    gridcommand = self.display.setygrid,
				    autocommand = self.display.cmd_yrange_auto
				    )


	self.display.xcontrol = self.xcontrol
	self.display.ycontrol = self.ycontrol

	self.mcontrols = []
	self.mcontrolbyname = {}
	for name in ('A', 'B'):
	    marker = self.display.new_xmarker(name)
	    control = MarkerControl(self.ctrlframe, marker, self.update_tableframe)
	    marker.set_poscommand(control.setsample)
	    self.mcontrols.append(control)
	    self.mcontrolbyname[name] = control

	if 0:

	    self.optionsmenu.add_checkbutton(
		label='X grid',
		variable = self.display.var_xgrid,
		command = self.display.cmd_xgrid)

	    self.optionsmenu.add_checkbutton(
		label='Y grid',
		variable = self.display.var_ygrid,
		command = self.display.cmd_ygrid)


	self.var_showcontrol=BooleanVar()
	self.var_showcontrol.set(1)
	self.panemenu.add_checkbutton(
	    label='Show Control Panel',
	    variable = self.var_showcontrol,
	    command = self.cmd_showcontrol)

	self.var_showgraph=BooleanVar()
	self.var_showgraph.set(1)
	self.panemenu.add_checkbutton(
	    label='Show Graph',
	    variable = self.var_showgraph,
	    command = self.cmd_showgraph)

	self.var_showtable=BooleanVar()
	self.var_showtable.set(1)
	self.panemenu.add_checkbutton(
	    label='Show Table',
	    variable = self.var_showtable,
	    command = self.cmd_showtable)



	tf = self.tf = TableFrame(self, self.disptab)
	d_t = self.d_t = PaneDiv(self.disptab, movecommand=self.cmd_dt_moved)


	if 0:
	    self.ycontrol.frame.pack(side=LEFT, padx=3,pady=3)
	    self.xcontrol.frame.pack(side=LEFT, padx=3,pady=3)
	    self.scontrol.frame.pack(side=LEFT, padx=3, pady=3)
	    self.graphtypeframe.pack(side=LEFT, padx=3,pady=3)
	    self.collectbutton.pack(side=LEFT, padx=3,pady=3)
	else:
	    self.xcontrol.frame.grid(row=0,column=0, padx=3,pady=3, sticky=W)
	    self.ycontrol.frame.grid(row=1,column=0, padx=3,pady=3)
	    self.mcontrols[0].frame.grid(row=0,column=1, columnspan=1,sticky=W,padx=3,pady=3)
	    self.mcontrols[1].frame.grid(row=1,column=1, columnspan=1,sticky=W,padx=3,pady=3)
	    self.exitbutton.grid(row=0,column=2, padx=3,pady=3)
	    self.collectbutton.grid(row=0,column=3, padx=3,pady=3)

	self.filler = Filler(self.frame)

	if 1:
	    self.filebutton.pack(side=LEFT)
	    self.panebutton.pack(side=LEFT)
	    self.graphbutton.pack(side=LEFT)
	    self.tablebutton.pack(side=LEFT)
	    self.windowmenu.button.pack(side=LEFT)
	    self.helpbutton.pack(side=LEFT)
	    
	    self.menubar.grid(column=0,columnspan=4, sticky=N+W+E)
	    self.gridmain()


	if 0:
	    self.display.frame.grid(row = 0, column = 0, sticky=N+W, padx=3,pady=3)

	    tf.frame.grid(row=0, column=1, sticky=S+E, padx=3,pady=3)

	    self.ctrlframe.grid(row=1,column=0, columnspan=2, sticky=W)



	frame.bind('<Map>', self.event_map)

	self.tf.setmode(self.var_tablemode.get(), self.numkindrows)

	self.load_filename(filename)

	d_t.frame.update_idletasks()
	d_t.setheight(max(self.display.frame.winfo_height(),
			      tf.frame.winfo_height()))



	d_t.frame.update_idletasks()
	self.minsize = (500,400)
	self.maxsize = (self.frame.winfo_screenwidth(), self.frame.winfo_screenheight())
	minsizes = {
	    # (ctrl, disp, tab) : (width, height)
	    (0,0,0): (270, 25),
	    (1,0,0): (363, 61),
	    (0,1,0): (270, 131),
	    (1,1,0): (270, 131),
	    }


	self.setusergeometry()

	def initfinal():
	    self.tf.setchdim()

	    rx = self.frame.winfo_rootx() + self.frame.winfo_width()
	    self.tf_wanted_margin =  rx - (self.tf.frame.winfo_rootx() +  self.tf.frame.winfo_width())

	    self.lastw = self.frame.winfo_width()
	    self.lasth = self.frame.winfo_height()
	    self.in_configure = 0
	    frame.bind('<Configure>', self.event_configure)
	    self.inited = 1

	initfinal()
	#self.frame.after_idle(initfinal)

    def cmd_about(self):
	self.cmd_help('about')

    def cmd_help(self, pickname='help'):
	os = self.mod.os
	ocursor = self.frame.winfo_toplevel()['cursor']
	try:
	    self.frame.winfo_toplevel()['cursor'] = 'watch'
	    self.frame.update()
	    m = self.mod.Text.gsltextviewer(
		self.frame,
		inpickle = getattr(self.mod.pbhelp, pickname)
		#htmloutfile='/tmp/x.html',
		)

	    self.app.add_window_frame(m)
	finally:
	    self.frame.winfo_toplevel()['cursor'] = ocursor

    def cmd_clear_cache(self):
	self.stats.clear_cache()

    def cmd_close(self):
	self.frame.destroy()

    def cmd_collect(self, *args):
	#self.afterfunc()
	#self.frame.after(1, self.afterfunc) # Turn on button first.??

	if self.collecting.get():
	    self.event_collect()
	else:
	    if self.id_collect is not None:
		self.frame.after_cancel(self.id_collect)
		self.id_collect = None

    def event_collect(self):
	o, n = self.stats.collect()
	if n:
	    if o != self.display.numstats:
		self.display.load_stats(self.stats)
	    else:
		st = self.stats[-n:]
		self.display.add_stats(st)
	    for c in self.mcontrols:
		c.setnumsamples(len(self.stats))

	self.id_collect = self.frame.after(1000, self.event_collect)



    def cmd_dt_moved(self, dx):
	# The division between display and table panes moved.

	# Disable configure event handling while we are resizing.
	self.in_configure += 1

	# Right x position of enclosing frame

	rx = self.frame.winfo_rootx() + self.frame.winfo_width()

	# Right margin between pane divider and enclosing window

	mx = rx - (self.d_t.frame.winfo_rootx() + self.d_t.frame.winfo_width())

	# Don't move pane divider outside window
	dx = min(dx, mx)

	# Right margin between table and enclosing window
	# before resizing
	mx =  rx - (self.tf.frame.winfo_rootx() +  self.tf.frame.winfo_width())

	dx, _ = self.display.resize(dx, 0)

	wanted_margin = self.tf_wanted_margin

	# After move
	mx -= dx
	self.tf.resize(mx - wanted_margin, 0)

	self.display.moveback()

	self.in_configure -= 1

    def cmd_exit(self):
	self.app.exit()

    def cmd_graphtype(self):
	self.display.setgraphtype(self.graphtypevar.get(), self.stats)
	self.cmd_tablemode()

    def cmd_new(self):
	self.app.new_profile_browser(self.filename)

    def cmd_open(self):
	op = tkFileDialog.Open(self.frame,
			       # ? Should we have default extension or not??
			       # defaultextension='.hpy',
			       initialdir = self.initialdir,
			       filetypes=[('Heapy data files','.hpy'),
					  ('All files', '*')
					  ]
			       )
	filename = op.show()
	if filename:
	    self.load_filename(filename)

    def cmd_showcontrol(self):
	self.grid_things()

    def cmd_showgraph(self):
	if self.var_showgraph.get() and self.var_showtable.get():
	    self.tf.resize(-self.tf.totxresize, 0)
	    self.display.resize(self.display.orgwidth - self.display.botx, 0)
	    self.display.moveback()
	self.grid_things()
	
    cmd_showtable = cmd_showgraph
	
    def cmd_tablemode(self):
	self.tf.setmode(self.var_tablemode.get(), self.numkindrows)
	self.tf.update()

    def cmd_tablescrollbar(self):
	tf = self.tf
	s = self.var_tablescrollbar.get()
	if s == 'Auto':
	    tf.auto_scrollbar = 1
	    tf.update(force=1, setscrollbar=1)
	elif s == 'On':
	    tf.auto_scrollbar = 0
	    tf.setscrollbar(1)
	elif s == 'Off':
	    tf.auto_scrollbar = 0
	    tf.setscrollbar(0)
	else:
	    assert 0

    def setusergeometry(self):
	# Make the geometry of the window be user-specified
	# This is called after Tk has determined the size
	# of the window needed for the initial widget configuration.
	# The size is not to be changed after that, other than
	# on user request.
	# I couldn't just do frame.geometry(frame.geometry()) because,
	# presumably, of a bug in the Tk and/or wm I am using. I hope
	# this works for all systems .. Notes  26 Oct 2005.

	self.frame.update()
	g = '%dx%d+%d+%d'%(
	    self.frame.winfo_width(),
	    self.frame.winfo_height(),
	    self.frame.winfo_rootx(),
	    self.frame.winfo_rooty())
	self.frame.geometry(g)
	

    def modechooser(self, frame, name, choices, cmdvar, command):

	button = Menubutton(frame, text=name)
	menu = Menu(button)
	button['menu'] = menu

	self.addmodechooser(menu, choices, cmdvar, command)
	return button

    def addmodechooser(self, menu, choices, cmdvar, command):

	def setcmdvar():
	    cmdvar.set(' '.join([v.get() for v in vars]))
	    
	def cmd():
	    setcmdvar()
	    command()
		       
	vars = []
	for ch in choices:
	    var = StringVar()
	    vars.append(var)
	    var.set(ch[0])
	    for a in ch:
		menu.add_radiobutton(
		    command = cmd,
		    label = a,
		    value=a,
		    variable=var,
		    #font=('Courier','12', 'bold'),
		    #font=('Helvetica','12', 'bold'),
		    columnbreak = (a == ch[0])
		    )

	setcmdvar()


    def grid_things(self):
	ow = self.frame.winfo_width()
	oh = self.frame.winfo_height()



	self.ctrlframe.grid_forget()
	self.display.frame.grid_forget()
	self.d_t.frame.grid_forget()
	self.tf.frame.grid_forget()
	self.disptab.grid_forget()
	self.filler.frame.grid_forget()

	self.gridmain()

	self.frame.update_idletasks()
	self.sizewidgets()


    def gridmain(self):

	row = 1

	c = self.var_showcontrol.get()
	if c:
	    self.ctrlframe.grid(row=row,column=0, columnspan=3, padx=3,pady=3,sticky=W)
	    row += 1

	column = 0

	g = self.var_showgraph.get()
	t = self.var_showtable.get()
	gt = (g, t)
	if g:
	    self.display.frame.grid(row=0, column = column, sticky=N+W,
				    padx=3,pady=3
				    )
	    column += 1
	    
	if g and t:
	    self.d_t.frame.grid(row=0, column=column, sticky=N+W)
	    column += 1
	if t:
	    self.tf.frame.grid(row=0, column=column, sticky=N+W
			       , padx=3,pady=3
			       )
	if g or t:
	    self.disptab.grid(row=row, column=0,
			      sticky=N+W,
			      #padx=3,pady=3,
			      )
	    row += 1
	self.filler.setsize(0, 0)
	self.filler.frame.grid(row=row,column=3, sticky=N+W)

	if 0 and not (g or t):
	    self.frame.resizable(0,0)
	else:
	    self.frame.resizable(1,1)




    def event_configure(self, event):
	if event.widget is not self.frame:
	    return

	if not self.inited:
	    return

	if self.in_configure:
	    return

	curw = self.frame.winfo_width()
	curh = self.frame.winfo_height()
	if curw == self.lastw and curh == self.lasth:
	    return

	self.in_configure += 1

	self.lastw = curw
	self.lasth = curh

	self.sizewidgets()

	self.in_configure -= 1

    def sizewidgets(self):
	self.frame.update()
	curw = self.frame.winfo_width()
	curh = self.frame.winfo_height()

	mbx = self.menubar.winfo_rootx()
	mby = self.menubar.winfo_rooty()


	sfs = []
	if self.var_showgraph.get():
	    sfs.append(self.display)
	if self.var_showtable.get():
	    sfs.append(self.tf)

	if not sfs:
	    sfs.append(self.filler)

	dys = {}
	didh = 0
	for sf in sfs:
	    f = sf.frame
	    diy = f.winfo_rooty()
	    dih = f.winfo_height()

	    ch = diy - mby + dih
	    dy = curh - ch - 7
	    didh = didh or dy
	    dys[sf] = dy
	    

	if self.var_showtable.get():
	    f = self.tf.frame
	elif self.var_showgraph.get():
	    f = self.display.frame
	else:
	    f = self.filler.frame

	fx = f.winfo_rootx()
	fw = f.winfo_width()

	cw = fx - mbx + fw

	fdw = curw - cw - 6

	if f is self.filler.frame and not self.var_showcontrol.get():
	    fdw = curw - self.filler.getsize()[0] - 3

	if didh or fdw:
	    if self.var_showgraph.get() and self.var_showtable.get():
		dprop = float(self.display.frame.winfo_width())
		dprop = dprop / (dprop + self.tf.frame.winfo_width())
		dx, dy = self.display.resize(fdw * dprop, dys[self.display])
		self.tf.resize(fdw - dx, dys[self.tf])
		self.frame.update_idletasks()
		self.d_t.setheight(max(self.display.frame.winfo_height(),
				       self.tf.frame.winfo_height()))



	    elif self.var_showgraph.get():
		self.display.resize(fdw, dys[self.display])
	    elif self.var_showtable.get():
		self.tf.resize(fdw, dys[self.tf])
	    else:
		self.filler.resize(fdw, dys[self.filler])
		self.filler.setsize(self.filler.getsize()[0],1000)
	    if self.var_showgraph.get():
		self.display.moveback()

	#self.resize(dw, dh)


    def resize(self, dw, dh):
	self.display.resize(dw, dh)
	#self.frame.wm_geometry('')


    def event_map(self, event):
	self.frame.unbind('<Map>')
	self.frame.bind('<Unmap>', self.event_unmap)
	self.frame.lift()
	
    def event_unmap(self, event):
	self.frame.unbind('<Unmap>')
	self.frame.bind('<Map>', self.event_map)
	
	
    def load_filename(self, filename):
	ocursor = self.frame.winfo_toplevel()['cursor']
	try:
	    self.frame.winfo_toplevel()['cursor'] = 'watch'
	    self.frame.update()
	    if filename:
		filename = self.mod.path.abspath(filename)
	    try:
		self.stats.open(filename)
	    except:
		etype, value, tb = self.mod._root.sys.exc_info()
		tkMessageBox.showerror(
		    master=self.frame,
		    message = (
			"Error when loading\n%r:\n"%filename+
			"%s"%''.join(self.mod._root.traceback.format_exception_only(
			    etype, value)))
		    )
	    else:
		self.display.load_stats(self.stats)

		for c in self.mcontrols:
		    c.setnumsamples(len(self.stats))
		#self.scontrol.trackcommand(1)
		self.set_filename(filename)

		self.xrange_fit()
		self.display.xview_moveto(0)
		self.mcontrols[1].settracking(0)
		self.mcontrols[0].settracking(1)
		self.yrange_fit()
		self.tf.update(force=1)
		if filename:
		    self.initialdir = self.mod.path.dirname(filename)
		
	finally:
	    self.frame.winfo_toplevel()['cursor'] = ocursor

    def update_tableframe(self):
	self.tf.update()

    def getkindcolor(self, kind):
	if kind == '<Other>':
	    return 'black'
	else:
	    return self.colors[abs(hash(kind))%len(self.colors)]


    def set_filename(self, filename):
	self.filename = filename
	if not filename:
	    filename = '<No File>'
	title = 'Heapy Profile Browser: %s'%filename
	self.window.title(title)

    def setnormpos(self):
	self.setscrollregion()
	if self.ymax >= self.yrange:
	    self.yrange_fit()
	if self.xi0 is None:
	    self.drawxaxis()
	else:
	    self.updatexaxis()
	
	self.track()

    def redraw_all(self):
	pass
	
    def trackoff(self):
	self.rcontrol.settracking(0)

    def xrange_fit(self):
	self.xcontrol.fit(len(self.stats))

    def yrange_fit(self):
	self.display.yrange_auto(force=1)
	
class _GLUECLAMP_:
    _imports_ = (
	'_parent:Use',
	'_parent:pbhelp',
	'_root.guppy.etc:textView',
	'_root.guppy:specs',
	'_root:md5',
	'_root:os',
	'_root.os:path',
	'_root:time',
	'_root.guppy.gsl:Text',
	)
    

    def pb(self, filename=None):
        """pb( [filename: profilefilename+])

Create a Profile Browser window.

Argument
    filename: profilefilename+
        The name of a file containing profile data.
See also
    Heapy Profile Browser[1]
    Screenshot[2]
References
    [0] heapy_Use.html#heapykinds.Use.pb
    [1] ProfileBrowser.html
    [2] pbscreen.jpg"""    

	pa = ProfileApp(self)
	pa.new_profile_browser(filename)
	pa.mainloop()
	

    def tpg(self):
	self('/tmp/x.hpy')

