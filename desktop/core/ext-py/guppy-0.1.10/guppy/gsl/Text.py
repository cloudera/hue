#._cv_part guppy.gsl.Text

# Convert a node representation to text
# in some different forms

# o output to an object with an interface subset of Tk Text
# o output to ascii-only - best attempt w.o. different fonts
# o output to man-page text

# Parameterized on out

# I have to define the roles of responsibility.

# out is a thin layer above something Tk text-like
# it isolates some details but doesn't provide real new functionality

# Node2Inter takes care of the general formatting
# It needs to know about 
# o the size of out, i.e. width and height
# o the fonts and sizes available
# o the special characters available
# o the size of the fonts
# o we restrict to fixed size fonts
#   otherwise it would have to ask for size of strings?
#

# to be able to do
# o line wrapping
# o paragraphs
# o headers
# o item and bullet lists
# o tables

# The out can 'record' its commands
# and play them on an actual Tk text window.
# with a simple translation
# o it can operate stack-free
# -- so after eg a font change, there is a font change back

# Does the out has a configuration table
# such as, 
# o the fonts to choose 
# o for different sizes
# o whether to make items bold

# In any case there may be default here..

class Node2Inter:
    def __init__(self, mod, node, out, cnf, width=None):
	self.mod = mod
	self.out = out
	self.cnf = cnf
	self.width = width
	
	self.span_stack = []
	self.attrs_stack = [{}]
	self.atparbegin = 1
	self.inpre = 0
	self.ul_level = 0
	self.prev_margin_bottom = 0

	self.sizescale = cnf.sizescale

	if node is not None:
	    self._visit_outer_node(node)

    def _visit_outer_node(self, node):
	cnf = self.cnf
	self.span_begin(font_family=cnf.textfamily, font_size=cnf.sizeindex)
	node, attrs = node.split_attrs()
	for k, v in attrs:
	    k = k.strip()
	    v = v.strip()
	    setattr(self.out, '_gsl_%s'%k, v)
	node.accept(self)
	self.span_end()

    def _visit_node(self):
	node, attrs = node.split_attrs()
	if attrs:
	    self.attrs_stack
	

    def append(self, x):
	self.out.insert('end', x, self.tags)
	
    def div(self, node, margin_bottom=0, **kwds):
	self.div_begin(**kwds)
	node.arg_accept(self)
	self.div_end(margin_bottom)

    def div_begin(self, margin_top=0, **kwds):
	if self.span_stack:
	    d = self.span_stack[-1]
	    if 'spacing1' in d:
		if self.atparbegin:
		    margin_top = max(margin_top, d['spacing1'])
		self.tag_config(self.tag, **d)
		del d['spacing1']

	margin_top = max(margin_top, self.prev_margin_bottom)
	self.prev_margin_bottom = 0

	if not self.atparbegin:
	    self.nl()
	    self.atparbegin = 1
		
	if margin_top:
	    kwds['spacing1'] = margin_top

	self.span_begin(**kwds)

    def div_end(self, margin_bottom=0):
	if not self.atparbegin:
	    self.nl()
	self.span_end()
	self.atparbegin = 1
	self.prev_margin_bottom = margin_bottom

    def getopt(self, name, default=0):
	if self.span_stack and name in self.span_stack[-1]:
	    return self.span_stack[-1][name]
	else:
	    return getattr(self, name, default)

    def nl(self):
	self.append('\n')

    def set_default_tag(self):
	if self.span_stack:
	    tag = 't%s'%self.mod._root.pickle.dumps(self.span_stack[-1])
	else:
	    tag = 'tag'
	self.tag = tag
	self.tags = (tag,)
	
    def span(self, node, **kwds):
	self.span_begin(**kwds)
	node.arg_accept(self)
	self.span_end()

    def span_begin(self, **kwds):
	if self.span_stack:
	    d = self.span_stack[-1].copy()
	    d.update(kwds)
	else:
	    d = kwds
	self.span_stack.append(d)
	
	self.set_default_tag()

    def span_end(self):
	tag = self.tag
	self.tag_config(tag, **self.span_stack[-1])
	self.span_stack.pop()
	self.set_default_tag()
	
    def tag_config(self, tag, **kwds):
	okwds = {}
	fontspecs = []
	for k, v in kwds.items():
	    if not k.startswith('font_'):
		okwds[k] = v
		continue
	    else:
		fontspecs.append((k[5:], v))
	if fontspecs:
	    font = [None, None, '']
	    for k, v in fontspecs:
		if k == 'size':
		    v = max(0, min(len(self.sizescale)-1, v))
		    font[1] = self.sizescale[v]
		elif k == 'family':
		    font[0] = v
		else:
		    if font[2]:
			font[2] += ' '
		    font[2]+= k
	    if not font[2]:
		font.pop()
	    okwds['font'] = tuple(font)

	self.out.tag_config(tag, **okwds)

    def text(self, text):
	if not self.inpre:
	    if self.atparbegin:
		text = text.lstrip()
	    if not text:
		return

	    text = text.replace('\n', ' ')
	    text = text.replace('\t', ' ')
	    while '  ' in text:
		text = text.replace('  ', ' ')

	    if self.atparbegin and self.prev_margin_bottom:
		self.tag_config(self.tag, **self.span_stack[-1])
		self.span_stack[-1]['spacing1'] = self.prev_margin_bottom
		self.set_default_tag()
		self.prev_margin_bottom = 0
		
	    self.append(text)
	else:
	    text = text.expandtabs()
	    idx = text.find('\n')
	    if idx != -1 and 'spacing1' in self.span_stack[-1]:
		self.append(text[:idx+1])
		self.tag_config(self.tag, **self.span_stack[-1])
		del self.span_stack[-1]['spacing1']
		self.set_default_tag()
		text = text[idx+1:]
	    if text:
		self.append(text)

	self.atparbegin = 0

    def _visit_children(self, node):
	E = self.mod.ReportedError
	for ch in node.children:
	    try:
		ch.accept(self)
	    except E:
		pass

    def _visit_hx(self, node):
	n = int(node.tag[1:])
	font_size = 7 - n
	margin_top = 12 - 1 * n
	margin_bottom = 12 - 1 * n
	
	self.div(node,
		 font_size=font_size,
		 font_bold=1,
		 margin_top=margin_top,
		 margin_bottom=margin_bottom )

    def visit_big(self, node):
	self.span(node, font_size=self.getopt('font_size') + 1)

    def visit_blockquote(self, node):
	lmargin = self.getopt('lmargin1') + 36
	rmargin = self.getopt('rmargin') + 36
	self.div(node,
		 lmargin1=lmargin,
		 lmargin2=lmargin,
		 rmargin=rmargin,
		 margin_top=6,
		 margin_bottom=6,
		 )
		 
    def visit_char(self, node):
	code = node.arg.strip()
	if code == 'nbsp':
	    self.span_begin(invisible=1)
	    self.append('x')
	    self.span_end()
	else:
	    self.error('I do not know how to render this character code: %r.'%code, node)


    def visit_code(self, node):
	self.span(node, font_family=self.cnf.codefamily)

    def visit_comment(self, node):
	pass
    def visit_dl(self, node):
	self.div(node)

    def visit_dt(self, node):
	self.div(node)

    def visit_dd(self, node):
	lmargin = self.getopt('lmargin1') + 36
	self.div(node, lmargin1=lmargin, lmargin2=lmargin)

    def visit_define(self, node):
	# xxx
	self._visit_children(node)

    def visit_div(self, node):
	self.div(node)

    def visit_document(self, node):
	self._visit_children(node)

    def visit_document_lang(self, node):
	if self.document_lang is not None:
	    self.error('Duplicate document lang directive.', node)
	self.document_lang = node

    def visit_document_title(self, node):
	if self.document_title is not None:
	    self.error('Duplicate document title directive.', node)
	self.document_title = node

    def visit_em(self, node):
	self.span(node, font_italic=1)

    def visit_gsl_title(self, node):
	self.out._gsl_title = node.arg

    def visit_gsl_width(self, node):
	self.out._gsl_width = int(node.arg)

    def visit_gsl_height(self, node):
	self.out._gsl_height = int(node.arg)

    def visit_h1(self, node):
	self._visit_hx(node)

    def visit_h2(self, node):
	self._visit_hx(node)

    def visit_h3(self, node):
	self._visit_hx(node)

    def visit_h4(self, node):
	self._visit_hx(node)

    def visit_h5(self, node):
	self._visit_hx(node)

    def visit_h6(self, node):
	self._visit_hx(node)

    def visit_li(self, node):
	indent = self.getopt('lmargin1') + 18
	self.div_begin(
		 lmargin1=indent,
		 lmargin2=indent
		 )
		 


	mode = ['disc', 'square', 'circle'][self.ul_level%3]

	char = {'disc':'*', 'circle':'O', 'square':'[]'}[mode]

	     
	self.span_begin()
	self.text('%s '%char)
	self.span_end()
	self.span_begin(
		 lmargin1=indent,
		 lmargin2=indent+12
		 )
	node.arg_accept(self)
	self.span_end()
	self.div_end()


    def visit_p(self, node):
	self.div(node, margin_top=6, margin_bottom=6)

    def visit_pre(self, node):
	self.inpre += 1
	self.div(node, font_family=self.cnf.codefamily, margin_top=6, margin_bottom=6)
	self.inpre -= 1

    def visit_small(self, node):
	self.span(node, font_size=self.getopt('font_size') - 1)

    def visit_span(self, node):
	self.span(node)

    def visit_string(self, node):
	self._visit_children(node)
	
    def visit_strong(self, node):
	self.span(node, font_bold=1)

    def visit_sub(self, node):
	self.span(node,
		   font_size = self.getopt('font_size') - 1,
		   offset=self.getopt('offset') - 2
		   )

    def visit_sup(self, node):
	self.span(node, 
		   font_size = self.getopt('font_size') - 1,
		   offset=self.getopt('offset') + 2
		   )

    def visit_table(self, node):
	Table(self, node)
	pass

    def visit_td(self, node):
	pass

    def visit_th(self, node):
	pass

    def visit_tr(self, node):
	pass

    def visit_text(self, node):
	self.text(node.arg)
	self._visit_children(node)

    def visit_u(self, node):
	self.span(node, underline=1)

    def visit_ul(self, node):
	self.ul_level += 1
	self.div(node)
	self.ul_level -= 1

    def visit_var(self, node):
	self.span(node, font_italic=1)

class SimulText:
    def __init__(self, mod, width=None):
	self.mod = mod
	self.width = width

	self.lines = [[]]
	self.tags = {}
	self.textntags = []
	self.fonts = {}

    def insert(self, pos, text, tags):
	assert pos == 'end'
	lines = text.split('\n')
	self.lines[-1].append((lines[0], tags))
	for line in lines[1:]:
	    self.lines.append([(line, tags)])
	self.textntags.append((text, tags))

    def tag_config(self, tag, **kwds):
	if tag in self.tags and kwds == self.tags[tag]:
	    return
	self.tags[tag] = kwds

    ##

    def finalize(self):
	if len(self.lines[-1]) == 1 and not self.lines[-1][0][0]:
	    self.lines.pop()
	if self.width is not None:
	    self.wrap_lines()

    def get_width(self):
	width = 0
	for line in self.lines:
	    w = self.text_width(line)
	    if w > width:
		width = w
	return width

    def replay(self, out, lineidx):
	if lineidx >= len(self.lines):
	    return
	line = self.lines[lineidx]
	for (ch, tags) in line:
	    out.insert('end', ch, tags)
	    for tag in tags:
		out.tag_config(tag, **self.tags[tag])
    def split_word(self, line):
	words = [[]]
	for text, tags in line:
	    wtext = text.split(' ')
	    for wt in wtext:
		if wt:
		    words[-1].append((wt, tags))
		if words[-1]:
		    words.append([])
	return words

    def text_width(self, textntags):
	font = None
	subline = None
	subfonts = []
	for ch, tags in textntags:
	    for tag in tags:
		if tag in self.tags and 'font' in self.tags[tag]:
		    newfont = self.tags[tag]['font']
		    break
	    else:
		assert 0

	    if newfont != font:
		if subline:
		    subfonts.append((subline, font))
		font = newfont
		subline = []
	    subline.append(ch)
	if subline:
	    subfonts.append((subline, font))
	width = 0
	for (subline, font) in subfonts:
	    f = self.mod.makefont(font)
	    m = f.measure(''.join(subline))
	    width += m
	return width

    def width_to(self, char):
	# distance from left margin to first occurence of char
	# or the width of longest line, if char not found
	for line in self.lines:
	    w = 0
	    found = 0
	    for (text, tags) in line:
		if char in text:
		    text = text[:text.index(char)]
		    found = 1
		w += self.text_width([(text, tags)])
		if found:
		    break
	    if found:
		break
	if not found:
	    w = self.get_width()
        return w

    def wrap_line(self, line):
	w = self.text_width(line)
	if w <= self.width:
	    self.lines.append(line)
	    return

	words = self.split_word(line)

	i = 0
	while i < len(words):
	    pre = list(words[i])
	    w = self.text_width(pre)
	    while w > self.width:
		# The word is too long to fit.
		# I have to cut it off.
		# xxx this may be somewhat slow
		#  measuring after every character
		j = 0
		# Position j at the chunk that is going to be split
		while j + 1 < len(pre):
		    w = self.text_width(pre[:j+1])
		    if w > self.width:
			break
		    j += 1
		
		# Split this chunk
		# Allow at least one character
		k = 2
		while k <= len(pre[j][0]):
		    w = self.text_width(pre[:j-1] + [(pre[j][0][:k], pre[j][1])])
		    if w > self.width:
			break
		    k += 1
		self.lines.append(pre[:j-1] + [(pre[j][0][:k-1], pre[j][1])])
		assert self.text_width(self.lines[-1]) <= self.width
		pre = [(pre[j][0][k-1:], pre[j][1])]
		w = self.text_width(pre)

	    i += 1
	    while i < len(words):
		space = [(' ', pre[-1][1])]
		word = words[i]
		w = self.text_width(pre + space + word)
		if w > self.width:
		    break
		else:
		    pre.extend(space + word)
		    i += 1
	    self.lines.append(pre)

    def wrap_lines(self):
	lines = self.lines
	self.lines = []
	for line in lines:
	    self.wrap_line(line)


class TableCell:
    def __init__(self, row, node):
	self.row = row
	self.table = row.table
	self.parent = self.table.parent
	self.cnf = self.parent.cnf
	self.mod = self.parent.mod


	self.attrs = {}
	self.node = self.set_attributes(node)

	self.gen_out()


    def align(self, pos, width):
	align = self.attrs['align']
	if align == 'center':
	    self.tabstop = (pos + 0.5*width, 'center')
	elif align == 'left':
	    self.tabstop = (pos, 'left')
	elif align == 'right':
	    self.tabstop = (pos+width, 'right')
	elif align == 'char':
	    w = self.out.width_to(self.attrs['char'])
	    co = float(self.attrs['charoff'].rstrip('%'))/100.0
	    self.tabstop = (pos + co*width-w, 'left')
	elif align == 'justify':
	    # XXX I don't know how this works
	    self.tabstop = (pos + 0.5*width, 'center')
	else:
	    raise ValueError, 'Invalid align: %s'%align

    def get_edges(self, width):
	align = self.attrs['align']
	mywidth = self.width
	if align == 'center':
	    l, r = 0.5 * width - 0.5 * mywidth, 0.5 * width + 0.5 * mywidth
	elif align == 'left':
	    l, r = 0,  mywidth
	elif align == 'right':
	    l, r = width - mywidth, width
	elif align == 'char':
	    w = self.out.width_to(self.attrs['char'])
	    co = float(self.attrs['charoff'].rstrip('%'))/100.0
	    l = co * width - w
	    r = l + mywidth
	elif align == 'justify':
	    # XXX I don't know how this works
	    l, r = 0, width
	else:
	    raise ValueError, 'Invalid align: %s'%align
	return l, r
	

    def get_width(self):
	self.width = self.out.get_width()
	self.numlines = len(self.out.lines)
	return self.width

    def set_attributes(self, node):
	a = self.attrs
	if node.tag == 'th':
	    align = 'center'
	else:
	    align = 'left'
	a['align'] = align
	a['char'] = self.cnf.decimal_point
	a['charoff'] = '50%'

	node, attrs = node.split_attrs()
	for k, v in attrs:
	    a[k] = v

	return node

    def gen_out(self, width=None):

	self.out = SimulText(self.mod, width=width)

	n2i = Node2Inter(self.mod, None, self.out, self.cnf, width=width)

	kwds = self.parent.span_stack[-1].copy()
	if self.node.tag == 'th':
	    kwds['font_bold'] = 1

	n2i.span_begin(**kwds)
	self.node.arg_accept(n2i)
	n2i.span_end()
	self.out.finalize()

	self.get_width()

    def wrap_to_width(self, width):
	#print 'wrap', width
	if width >= self.width:
	    return
	self.gen_out(width)



class TableRow:
    def __init__(self, table, node):
	self.table = table
	self.node = node
	self.numlines = 1

	self.cells = []

	node, attrs = node.split_attrs()
	self.attrs = attrs
	node.children_accept(self)
    
    def new_cell(self, node):
	cell = TableCell(self, node)
	self.cells.append(cell)

    def visit_td(self, node):
	self.new_cell(node)

    def visit_th(self, node):
	self.new_cell(node)


class Table:
    def __init__(self, parent, node):
	self.parent = parent
	self.node = node

	self.caption = None
	self.rows = []

	parent.div_begin(margin_top=6)

	self.lmargin = parent.getopt('lmargin1')

	node.children_accept(self)

	Width = 400
	w = self.columnify()
	widths = self.widths
	spacings = self.spacings

	if w > Width:
	    # Which one to wrap?
	    # The longest?
	    # All?
	    gw = [Width / len(self.widths)]*len(self.widths)
	    if 1:
		extra = 0
		others = range(len(self.widths))
		for i, w in enumerate(self.widths):
		    if w < gw[i]:
			extra += gw[i] - w
			gw[i] = w
			others.remove(i)
		extra = int(extra / len(others))
		for i in others:
		    gw[i] += extra

	    widths = self.widths = gw
	    for row in self.rows:
		col = 0
		for cell in row.cells:
		    cell.wrap_to_width(gw[col])
		    col += 1
	    
	    for row in self.rows:
		col = 0
		pos = 0
		for cell in row.cells:
		    w = widths[col]
		    cell.align(pos+self.lmargin, w)
		    pos += w + spacings[col]
		    col += 1
		    row.numlines = max(row.numlines, cell.numlines)


	for row in self.rows:
	    for i in range(row.numlines):
		tabstops = []
		for cell in row.cells:
		    tabstops.extend(cell.tabstop)
		tabstops = tuple(tabstops)
		if i == 0 and row is self.rows[0]:
		    tabkwds = row.cells[0].out.tags[row.cells[0].out.lines[0][0][1][0]]
		else:
		    tabkwds = {}
		    if row is not self.rows[0] and i == 0:
			tabkwds['spacing1'] = 6
		tabtag = str(tabstops)+str(tabkwds)
		for cell in row.cells:
		    parent.out.insert('end', '\t', (tabtag,))
		    cell.out.replay(parent.out, i)
		parent.out.tag_config(tabtag, tabs=tabstops, **tabkwds)
		parent.nl()
	parent.div_end()


    def columnify(self):
	# Make the cells aligned in columns

	widths = self.widths = []
	
	for row in self.rows:
	    col = 0
	    for cell in row.cells:
		w = cell.get_width()
		if col >= len(widths):
		    widths.append(w)
		else:
		    widths[col] = max(w, widths[col])
		row.numlines = max(row.numlines, cell.numlines)

		col += 1

	spacings = self.spacings = [0] * len(widths) # Extra spacing after column i

	MINSPACING = 10

	for row in self.rows:
	    col = 0
	    for cell in row.cells[:-1]:
		rcell = row.cells[col+1]
		ledge = cell.get_edges(widths[col])[1]
		redge = rcell.get_edges(widths[col+1])[0]+widths[col]
		spacing = MINSPACING - (redge - ledge)
		spacings[col] = max(spacing, spacings[col])
		col += 1

	width = 0
	for row in self.rows:
	    col = 0
	    pos = 0
	    for cell in row.cells:
		w = widths[col]
		cell.align(pos+self.lmargin, w)
		pos += w + spacings[col]
		col += 1

	    if pos > width:
		width = pos

	self.width = width
	return width


    def visit_tfoot(self, node):
	node.children_accept(self)

    def visit_thead(self, node):
	node.children_accept(self)

    def visit_tr(self, node):
	row = TableRow(self, node)
	self.rows.append(row)





class RecordingInter:
    FLATTEXT = 1
    FLATKWDS = 0
    lasttext = ()
    lasttag = None
    def __init__(self):

	self.appends = []
	self.tag_configs = {}
	self.lasttext = []
	self.clearmemo()

    def __str__(self):
	return 'APPENDS: %s TAG_CONFIGS: %s'%(self.appends, self.tag_configs)

    def clearmemo(self):
	self.memo = {}		# Maps any value to it self
	self.tagmemo = {}	# Maps tag to integer tag number

    def flush(self):
	if self.lasttext:
	    tag = self.tagmemo.setdefault(self.lasttag, len(self.tagmemo))
	    text = ''.join(self.lasttext)
	    text = self.memo.setdefault(text, text)
	    if self.FLATTEXT:
		self.appends.append(tag)
		self.appends.append(text)
	    else:
		tt = tag, text
		tt = self.memo.setdefault(tt, tt)
		self.appends.append(tt)
	    self.lasttext = []
	    
    def insert(self, pos, text, tags):
	assert pos == 'end'
	assert len(tags) == 1
	
	tag = tags[0]
	if tag != self.lasttag:
	    self.flush()
	    self.lasttag = tag
	self.lasttext.append(text)
	
    def play(self, out):
	self.flush()
	if self.FLATTEXT:
	    i = 0
	    while i < len(self.appends):
		tag = self.appends[i]
		text = self.appends[i+1]
		out.insert('end', text, (tag,))
		i += 2
	else:
	    for tag, text in self.appends:
		out.insert('end', text, (tag,))
	for (tag, kwdlist) in self.tag_configs.items():

	    if self.FLATKWDS:
		kwds = {}
		i = 0
		while i < len(kwdlist):
		    kwds[kwdlist[i]] = kwdlist[i+1]
		    i += 2
		out.tag_config(tag, **kwds)
	    else:
		out.tag_config(tag, **dict(kwdlist))

	for k in self.__dict__:
	    if k.startswith('_gsl_'):
		setattr(out, k, getattr(self, k))

    def prepare_for_pickle(self):
	# Call this before pickling to reduce space usage.
	self.flush()
	for k in self.__dict__.keys():
	    if k not in ('appends', 'tag_configs') and not k.startswith('_gsl_'):
		delattr(self, k)

    def tag_config(self, tag, **kwds):
	kwdlist = []
	for k, v in kwds.items():
	    k = self.memo.setdefault(k, k)
	    v = self.memo.setdefault(v, v)
	    if self.FLATKWDS:
		kwdlist.append(k)
		kwdlist.append(v)
	    else:
		kv = k, v
		kv = self.memo.setdefault(kv, kv)
		kwdlist.append(kv)
	kwdlist = tuple(kwdlist)
	kwdlist = self.memo.setdefault(kwdlist, kwdlist)
	tag = self.tagmemo.setdefault(tag, len(self.tagmemo))

	if tag in self.tag_configs:
	    assert self.tag_configs[tag] == kwdlist
	else:
	    self.tag_configs[tag] = kwdlist

class TextInter:

    def __init__(self, mod, wid):
	self.mod = mod
	self.wid = wid

	for name in (
	    'config',
	    'insert',
	    'tag_delete',
	    ):
	    setattr(self, name, getattr(wid, name))

    def tag_config(self, tag, **kwds):
	if 'invisible' in kwds:
	    del kwds['invisible']
	    kwds['foreground'] = kwds['background'] = kwds.get('background', self.wid['background'])
	    

	self.wid.tag_config(tag, **kwds)

class TkConfig:
    sizeindex = 3
    sizescale = (6,8,10,12,16,20,24,28)
    textfamily = 'times'
    codefamily = 'courier'
    decimal_point = '.' # default CHAR attribute


class _GLUECLAMP_:
    _imports_ = (
	'_parent:SpecNodes',
	'_parent.SpecNodes:node_of_taci',
	'_parent.SpecNodes:node_of_string',
	'_parent.Main:ReportedError',
	'_parent:Html',
	'_root:cPickle',
	'_root.md5:md5',
	'_root:os',
	'_root:re',
	'_root:string',
	'_root:Tkinter',
	'_root:tkFont',
	)

    def _get_makefont(self):
	fonts = {}
	root = self.Tkinter.Tk()
	root.withdraw()

	def makefont(font):

	    if font in fonts:
		return fonts[font]
	    weight='normal'
	    slant='roman'
	    if len(font) > 2:
		if 'bold' in font[2]:
		    weight='bold'
		if 'italic' in font[2]:
		    slant='italic'
	    f = self.tkFont.Font(family=font[0], size=font[1],
			    weight=weight, slant=slant)
	    fonts[font] = f
	    return f
	return makefont

    def _get_tkconfig(self):
	return TkConfig()

    def node2inter(self, node, inter, tkconfig=None):
	if tkconfig is None:
	    tkconfig = self.tkconfig
	Node2Inter(self, node, inter, tkconfig)

    def gsltextviewer(self, parent=None, filename = None, text=None, node=None, htmloutfile=None,
		      inpickle=0,
		      inrecorder=0,
		      outrecorder=0
		      ):


	# It seems they dont want we mix data and py files in the dist sigh
	# so these are last minute hacks

	pickle = self.cPickle

	if inpickle:
	    inrecorder = pickle.loads(inpickle)

	if node is None:
	    if text is None:
		if filename is not None:
		    f = open(filename)
		    text = f.read()
		    f.close()
	    node = self.node_of_string(text, nostrip=1)

	if htmloutfile is not None:
	    self.Html.node2file(node, htmloutfile)

	if outrecorder:
	    r = RecordingInter()
	    self.node2inter(node, r)
	    r.prepare_for_pickle()
	    return r
	    
	cache = None
	if filename is not None:
	    sp = self.os.path.splitext(filename)
	    if sp[1] == '.gsl':
		cache = sp[0] + '.gsc'

	m = self._root.guppy.etc.textView.TextViewer(parent, 'Untitled', data='')
	v = m.textView
	v['state']='normal'
	v['font'] = 'Times -12'
	v.bind('<Destroy>', lambda event:m.quit())


	if cache or inrecorder:
	    if inrecorder:
		r = inrecorder
	    else:
		r = None
		textdigest = self.md5(text).digest()
		try:
		    f = open(cache)
		except IOError:
		    pass
		else:
		    td = f.read(len(textdigest))
		    if td == textdigest:
			r = pickle.load(f)
			f.close()
		if r is None:
		    r = RecordingInter()
		    self.node2inter(node, r)
		    r.prepare_for_pickle()
		    f = open(cache, 'w')
		    try:
			try:
			    f.write(textdigest)
			except IOError:
			    pass # maybe write protected just ignore for now XXX
			else:
			    pickle.dump(r, f, 0)
		    finally:
			f.close()
	    r.play(v)

	else:
	    self.node2inter(node, v)

	title = getattr(v, '_gsl_title', None)
	if title:
	    m.title(title)
	    m.iconname(title)

	geometry = getattr(v, '_gsl_tk_geometry', None)
	if geometry:
	    m.geometry(geometry)

	v['state']='disabled'
	return m

def test_string(s=None, name=None):
    from guppy import Root
    gsl = Root().guppy.gsl
    me = gsl.Text
    if s is None:
	s = getattr(me._parent.test.testdata, name)

    T = me.Tkinter
    node = me.node_of_string(s, nostrip=1)

    me._parent.Html.node2file(node, '/tmp/x.html')

    t = RecordingInter()
    me.node2inter(node, t)


    import cPickle as pickle
    t.prepare_for_pickle()

    root = T.Tk()
    root.withdraw()
    text = me._root.guppy.etc.textView.TextViewer(root, 'test', data='').textView
    text['state']='normal'
    text['font'] = 'Times -12'
    text.bind('<Destroy>', lambda event:root.quit())
    ti = TextInter(me, text)

    t.play(ti)

    text.mainloop()
    
def test():
    name='long_wrapping_tables'
    name='html_tables'
    test_string(name=name)


#test()
