#._cv_part guppy.heapy.RefPat

def str_as_atr(s):
    if s == '_':
	return []
    atr = []
    i = 0
    while i < len(s):
	v = s[i]
	if i + 1 < len(s) and s[i+1].isdigit():
	    n = 0
	    i = i + 1
	    while i < len(s) and s[i].isdigit():
		n = n * 10 + int(s[i])
		i += 1
	else:
	    i += 1
	    n = 1
	for j in range(n):
	    atr.append(v)
    return atr

def atr_as_str(atr):
    if not atr:
	return '_'
    prefl = []
    prestr = ''.join([str(x) for x in atr])
    i = 0
    while i < len(prestr):
	c = prestr[i]
	j = i+1
	while j < len(prestr) and prestr[j] == c:
	    j += 1
	if j - i > 2:
	    prefl.append(c)
	    prefl.append(str(j-i))
	else:
	    while i < j:
		prefl.append(c)
		i += 1
	i = j
    return ''.join(prefl)
    
def str_as_ixl(s):
    return [ord(ch)-ord('a') for ch in str_as_atr(s)]

def ixl_as_str(ixl):
    return atr_as_str([chr(ix + ord('a') ) for ix in ixl])
    

class Paths:
    def __init__(self, mod, rp, key, extended = True, andsets=(), variant=2):
	self.mod = mod
	self._hiding_tag_ = mod._hiding_tag_
	self.key = key
	self.rp = rp
	self.extended = extended
	self.srcrow = rp.get_row(self.key)
	self.variant = variant
	self.andsetbyname = {}
	row = self.srcrow
	while row is not None:
	    self.andsetbyname[row.ixlstr] = mod.Use.Anything
	    row = row.parent

	if isinstance(andsets, dict):
	    self.andsetbyname.update(andsets)
	elif isinstance(andsets, (tuple, list)):
	    row = self.srcrow
	    for i, s in enumerate(andsets):
		if row is None:
		    raise ValueError, 'andsets argument is too long'
		if s is not None:
		    self.andsetbyname[row.ixlstr] = s
		row = row.parent
	else:
	    raise TypeError, 'andsets argument must be dict, tuple, or list'

	mod.OutputHandling.setup_printing(
	    self,
	    stop_only_when_told = variant >= 2)

    def get_str_of_path_component_singleton(self, set):
	return set.brief.lstrip('<1 ').rstrip('>')

    def source_to_target_info(self):
	src = 'Source'
	tgt = 'Target'
	via = 'Via'

	row = self.srcrow
	indent = 0
	while row is not None:
	    if row.parent is None:
		a = tgt
	    elif row is srcrow:
		a = src
	    else:
		a = via
	    a = ' '*indent + a
	    name = row.ixlstr
	    a = a + ' ' + ' '*(8+srcrow.depth*indinc-len(name)-len(a)) + name + ': '
	    yield a+row.getsummary(mod.line_length-len(a))
	    row = row.parent
	    indent += indinc


    def _oh_get_line_iter(self):
	return getattr(self, 'get_line_iter_%s'%(self.variant,))()

    def _oh_get_more_state_msg(self, startindex, lastindex):
	return ''

    def get_line_iter_1(self):
	# Original variant indenting from left to right
	
	mod = self.mod

	srcrow = self.srcrow
	srcset = srcrow.set

	yield 'Paths from source %r to target %r.'%(srcrow.ixlstr, '_')

	indinc = 2
	if srcrow.depth >= 10:
	    indinc = 1

	def genlines(row, ks, indent=0):
	    par = row.parent
	    for key, i, set in ks:
		sidx = '%s[%d]'%(row.ixlstr, i)

		if self.extended:
		    strsing = self.get_str_of_path_component_singleton(set)
		else:
		    strsing = ''
		vline = '%s %s %s %s'%(
		    key,
		    ' '*(40-len(key) -len(sidx)),
		    sidx,
		    strsing
		    )

		yield vline

		if par is None:
		    continue

		def get_nks(key, set):
		    parset = set.referents & par.set
		    for i, p in enumerate(parset.byid.parts):
			rels = mod.Path.relations(set.theone, p.theone)
			for rel in rels:
			    if rel is mod.Path.identity:
				continue
			    if rel is mod.Path.norelation:
				k = '??'
			    else:
				k = str(rel)%''
			    k = ' '*(indent+indinc)+k
			    yield k, i, p

		for line in genlines(par, get_nks(key, set), indent+indinc):
		    yield line

	def get_ks():
	    for i, s in enumerate(srcset.byid.parts):
		k = '[%d]  '%i
		k = k + (' -'*20)[:36-len(k)-srcrow.depth]
		yield k, i, s

	for line in genlines(srcrow, get_ks()):
	    yield line
	return

    def get_line_iter_2(self):
	# Newer variant 
	
	mod = self.mod

	srcrow = self.srcrow
	srcset = srcrow.set

	yield 'Paths from source %r to target %r.'%(srcrow.ixlstr, '_')

	indinc = 1
	if srcrow.depth >= 10:
	    indinc = 1

	lno = [0]

	seen = {}

	indir = 1

	if indir == 1:
	    max_ixlstr_len = 0
	    max_str_len_set = 0
	    row = srcrow
	    while row:
		if len(row.ixlstr) > max_ixlstr_len:
		    max_ixlstr_len = len(row.ixlstr)
		if len(str(len(row.set.nodes))) > max_str_len_set:
		    max_str_len_set = len(str(len(row.set.nodes)))
		row = row.parent
	    

	def genlines(row, part, idx):

	    seen[part.nodes, row.depth] = lno[0]
	    sidx = row.ixlstr
	    idxs = '[%d]'%idx
	    if indir < 0:
		indent = (row.depth)*indinc
		sidx = '%s%s%s'%(sidx, ' '*(6+indent-len(sidx)-len(idxs)), idxs)
		if row.parent is None:
		    sidx += ' == %s'% part.brief

	    else:
		#idxs = ('[%.'+str(max_str_len_set)+'d]')%idx
		sidx = '%s%s%s'%(sidx,
				 ' '*(3+max_str_len_set + max_ixlstr_len-len(sidx)-len(idxs)),
				 idxs)
		sidx  += ' ' * (srcrow.depth + 1 - row.depth) 
		if row.parent is not None:
		    sidx += '@'
		else:
		    sidx += '= %s'% part.brief


	    if row.parent is None:
		#vline += ' == %s'%self.get_str_of_path_component_singleton(part)
		vline = '%2s: %s'%(lno[0], sidx)
		lno[0] += 1
		yield ('STOP_AFTER', vline)
		return

	    referents = part.referents & row.parent.set & self.andsetbyname[row.parent.ixlstr]
	    relations = mod.Path.relations
	    iso = mod.Use.iso
	    s = part.theone
	    t = [(relations(s, p.theone), p.by(referents.er), i) for (i, p) in enumerate(referents.byid.parts)]
	    for (rels, p, i) in t:
 		relstrings = []
		for rel in rels:
		    if rel is mod.Path.identity:
			continue
		    if rel is mod.Path.norelation:
			k = '??'
		    else:
			k = str(rel)%''
		    relstrings.append(k)

		relsstr = ' / '.join(relstrings)
		seenlno = seen.get((p.nodes, row.parent.depth))
		vline = '%2s: %s'%(lno[0], sidx)
		lno[0] += 1
		if seenlno is not None:
		    relsstr += ' -> #%d'%seenlno
		    yield ('STOP_AFTER', vline + ' ' + relsstr)
		else:
		    yield vline + ' ' + relsstr
		    for line in genlines(row.parent, p, i):
			yield line
	    
	    
	for i, p in enumerate((srcrow.set & self.andsetbyname[srcrow.ixlstr]).byid.parts):
	    for line in genlines(srcrow, p, i):
		yield line



class RefPatIter:
    def __init__(self, rp, start=0):
	self.rp = rp
	self._hiding_tag_ = rp._hiding_tag_
	self.ix = start

    def __iter__(self):
	return self

    def next(self):
	try:
	    x = self.rp[self.ix]
	except IndexError:
	    raise StopIteration
	self.ix += 1
	return x

class RefPatRow:
    def __init__(self, rp, kindset, seenline, ixl, parent):
	self.rp = rp
	self._hiding_tag_ = rp._hiding_tag_
	self.kindset = kindset
	self.kind, self.set = kindset
	assert self.set <= self.kind
	self.seenline = seenline
	self.ixl = ixl[:]
	self.parent = parent
	if parent is not None:
	    self.depth = parent.depth + 1
	else:
	    self.depth = 0

	self.index = 0
	self.maxdepth = rp.depth
	self.max_str_len = rp.mod.line_length
	self.ixlstr = ixl_as_str(ixl)
	self.isready = 0
	self.children = []

    def __str__(self):
	prestr = '%2d: %s '%(self.index, self.ixlstr)

	if self.index & 1:
	    fillpat = ' ' * 100
	else:
	    fillpat = '-'*100

	lps = len(prestr)
	fill = fillpat[lps:9+self.depth]

	if self.seenline:
	    ref = '[^ %s]'%self.seenline.index
	elif self.isroot:
	    ref = '[R]'
	elif self.depth > 0 and self.set <= self.rp.stopkind:
	    ref = '[S]'
	elif self.depth < self.maxdepth:
	    ref = '[-]'
	else:
	    ref = '[+]'

	prefix = '%s%s %s '%(prestr, fill, ref)
	return '%s%s'%(prefix, self.getsummary(self.max_str_len-len(prefix)))

    def getchild(self, ix):
	while ix >= len(self.children) and not self.isready:
	    self.rp.generate(len(self.rp.lines))
	return self.children[ix]
	

    def getsummary(self, max_len):
	kind, set = self.kind, self.set
	summary = set.fam.get_str_refpat(set, kind, max_len)
	return summary

class ReferencePattern:
    __doc__ = '<Help Text'
    help = """\
Methods




"""
    maxprint = 10
    def __init__(self, mod, set, depth, er, relimg, bf, stopkind, nocyc):
	self.mod = mod
	self._hiding_tag_ = mod._hiding_tag_
	self.View = mod.View
	self.set = set
	self.depth = depth
	self.er = er
	self.bf = bf
	self.stopkind = stopkind
	self.nocyc = nocyc
	self.is_initialized = 0

	self.totcount = set.count
	self.totsize = set.indisize
	self.kind = set.kind
	self.kindset = (self.kind, self.set)
	self.relimg = relimg
	self.top = self

	mod.OutputHandling.setup_printing(
	    self,
	    max_top_lines=mod.OutputHandling.max_top_lines+1)
	self.View.referrers_add_target(self)
	self.reset_nogc()
	self.is_initialized = 1


    def __getattr__(self, s):
	if not self.is_initialized:
	    raise AttributeError, s

	try:
	    return getattr(self.__class__, s)
	except AttributeError:
	    pass
	try:
	    row = self.get_row_named(s)
	except ValueError:
	    raise AttributeError, s
	return row.set

    def __getitem__(self, ix):
	return self.get_row_indexed(ix).set

    def __iter__(self, start=0):
	return RefPatIter(self, start)

    def __len__(self):
	self.generate()
	return len(self.lines)


    def _cv_getheader(self):
	return ('Reference Pattern by <' + self.er.classifier.get_byname() + '>.')

    def _cv_getlabel(self):
	return self._cv_getheader()

    def _cv_print(self, file):
	label = self._cv_getlabel()
	print >>file, label

	for line in self:
	    print >>file, line


    def _oh_get_more_state_msg(self, startindex, lastindex):
	if self.isfullygenerated:
	    msg = '%d more lines. '%(len(self.lines)+len(self._cv_getlabel().split('\n'))
				     -1-lastindex,)
	else:
	    msg = ''
	return msg
	

    def _oh_get_line_iter(self):
	for line in self._cv_getlabel().split('\n'):
	    yield line
	it = self.iterlines(0)
	for el in it:
	    yield str(el)
	

    def generate(self, ix=None):
	while ix is None or ix < 0 or ix >= len(self.lines):
	    try:
		self.lines.append(self.lg.next())
	    except StopIteration:
		self.isfullygenerated = 1
		return
	    self.lines[-1].index = len(self.lines) - 1

    def get_row(self, key):
	try:
	    [][key]
	except TypeError:
	    return self.get_row_named(key)
	except IndexError:
	    return self.get_row_indexed(key)

    def get_row_indexed(self, ix):
	self.generate(ix)
	return self.lines[ix]

    def get_row_named(self, name):
	row = self.get_row_indexed(0)
	for ix in str_as_ixl(name):
	    try:
		row = row.getchild(ix)
	    except IndexError:
		raise ValueError, 'Reference pattern has no row named %r'%name
	return row
	

    def iterlines(self, start=None):
	if start is None:
	    start = 0
	while 1:
	    try:
		yield self.get_row_indexed(start)
	    except IndexError:
		return
	    start += 1

    def linegenerator(self, (kind, set), ixl, parent=None):
	seenline = self.seensets.get(set.nodes)
	ixl = list(ixl)
	line = RefPatRow(self, (kind, set), seenline=seenline,
			 ixl=ixl, parent=parent)
	children = self.get_children(line)
	line.isroot = not children
	if seenline is None:
	    self.seensets[set.nodes] = line
	if parent is not None:
	    parent.children.append(line)
	yield line
	
	depth = line.depth
	if (not seenline and depth < self.depth and
            (depth == 0 or not (set <= self.stopkind))):
	    for i, cs in enumerate(children):
		ixl.append( i )
		for rl in self.linegenerator(cs, ixl, line):
		    yield rl
		ixl.pop()
	line.isready = 1	    

    def get_children(self, line):
	(kind, set) = line.kindset
	chset = self.relimg(set)
	if self.nocyc:
	    while line is not None:
		chset -= line.set
		line = line.parent
	return [(row.kind, row.set)
		for row in self.get_partition(chset, self.er).get_rows()]

    def get_partition(self, set, er):
	p = self.mod.Part.partition(set, er)
	return p

    def paths(self, key, **kwds):
	return Paths(self.mod, self, key, **kwds)

    def reset(self):
	self.reset_nogc()
	self.printer.reset()
	self.mod._root.gc.collect()

    def reset_nogc(self):
	self.isfullygenerated = 0
	self.seensets = {}
	self.lines = []
	self.lg = self.linegenerator(self.kindset, [])
	self.lastindex = None
	

class _GLUECLAMP_:
    _preload_ = ('_hiding_tag_',)

    depth = 7
    line_length = 80

    _uniset_exports = ('rp',)
    _chgable_ = ('er',
		 'depth'
		 'line_length',
		 )

    # 'module imports'

    _imports_ = (
	'_parent:OutputHandling',
	'_parent:Part',
	'_parent:Path',
	'_parent:UniSet',
	'_parent:Use',
	'_parent:View',
	'_parent.View:_hiding_tag_',
	)

    #

    def _get_er(self):	 return self.Use.Clodo
    def _get_stopkind(self):
	hp = self.Use
	return (
	    hp.Type.Module |
	    hp.Type.Class |
	    hp.Type.Type |
	    hp.Type.Module.dictof |
	    hp.Type.Class.dictof |
	    hp.Type.Type.dictof |
	    hp.Type.Code |
	    hp.Type.Frame
	    )


    def rp(self, X, depth=None, er=None, imdom=0, bf=0, src=None, stopkind=None,
           nocyc=False, ref=None):
	"""rp(X, depth=None, er=None, imdom=0, bf=0, src=None, stopkind=None, nocyc=False, ref=None)
Reference pattern forming.
Arguments
	X	Set of objects for which a reference pattern is sought.
	depth	The depth to which the pattern will be generated. The
		default is taken from depth of this module.
	er	The equivalence relation to partition the referrers. The default
		is Clodo.
	imdom	If true, the immediate dominators will be used instead
		of the referrers. This will take longer time to calculate,
		but may be useful to reduce the complexity of the reference
		pattern.
	bf	If true, the pattern will be printed in breadth-first
		order instead of depth-first. (Experimental.)
	src	If specified, an alternative reference source instead
		of the default root.
        stopkind
	nocyc
        ref

Description
	Return a reference pattern object based on the objects in the set X.
	The reference pattern object is of class ReferencePattern. It is
	described in XXX.
"""
	if depth is None:
	    depth = self.depth
	X = self.UniSet.idset_adapt(X)
	if src is not None:
	    # Creates an entire new guppy tree
	    # Mostly for testing purposes -
	    # can likely cause type problems generally
	    src = self.UniSet.idset_adapt(src)
	    self = self._root.guppy.Root().guppy.heapy.RefPat
	    self.View.root = tuple(src.nodes)
	    X = self.Use.idset(X.nodes)

	if er is None:
	    er = self.er # NEEDS to be loaded after new Classifier created
	if imdom:
	    relimg = lambda X:X.imdom
        elif ref is not None:
            if ref == 'gc':
                relimg = lambda X:X.referrers_gc
            elif ref == 'gcx':
                relimg = (lambda x:x.referrers_gc
                          - self._root.guppy.sets.ImmNodeSet
                          - self._parent.heapyc.NodeGraph
                          - self.View.ObservationList)
            elif ref == 'imdom':
                relimg = lambda X:X.imdom
            elif callable(ref):
                relimg = ref
            else:
                raise ValueError, \
 "ref should be 'gc', 'gcx', 'imdom', or a callable"
	else:
	    relimg = lambda X:X.referrers
	if stopkind is None:
	    stopkind = self.stopkind
	rp = ReferencePattern(self, X, depth, er, relimg, bf, stopkind, nocyc)
	return rp
