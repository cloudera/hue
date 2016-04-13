#._cv_part guppy.heapy.Path

class R_NORELATION:
    code = -1
    r = None
    def stra(self, a):
	return '%s.??'%a

class R_IDENTITY:
    code = 0
    def stra(self, a):
	return a

class R_ATTRIBUTE:
    code = 1
    strpat = '%s.%s'

class R_INDEXVAL:
    code = 2
    def stra(self, a):
	return '%s[%s]'%(a, self.saferepr(self.r))

class R_INDEXKEY:
    code = 3
    strpat = '%s.keys()[%r]'

class R_INTERATTR:
    code = 4
    strpat = '%s->%s'

class R_HASATTR:
    code = 5
    strpat = '%s.__dict__.keys()[%r]'

class R_LOCAL_VAR:
    code = 6
    strpat = '%s.f_locals[%r]'

class R_CELL:
    code = 7
    strpat = '%s.f_locals [%r]'

class R_STACK:
    code = 8
    strpat = '%s->f_valuestack[%d]'

class R_RELSRC:
    code = 9
    def stra(self, a):	return self.r%(a,)

class R_LIMIT:
    code = 10

    
class RelationBase(object):
    __slots__='r', 'isinverted'
    def __init__(self, r, isinverted = 0):
	self.r = r
	self.isinverted = isinverted

    def __cmp__(self, other):
	if isinstance(other, RelationBase):
	    if self.code != other.code:
		return cmp(self.code, other.code)
	    return cmp(self.r, other.r)
	else:
	    return cmp(type(self), type(other))
	    

    def __str__(self):
	return self.stra('%s')
    
    def inverted(self):
	x = self.__class__(self.r, not self.isinverted)

    def stra(self, a):
	return self.strpat%(a, self.r)

class MultiRelation(RelationBase):
    def __init__(self, rels):
	self.rels = rels

    def stra(self, a):
	return '<'+','.join([x.stra(a) for x in self.rels])+'>'

class Path:
    def __init__(self, mod, path, index, output, srcname):
	self.mod = mod
	self.path = path[1:]
	self.index = index
	self.output = output
	self.src = path[1]
	self.tgt = path[-1]
	self.strprefix = '%s'
	if srcname == '_str_of_src_':
	    srcname = self.src.brief
	if callable(srcname):
	    srcname = srcname(self)
	self.srcname = srcname

    def __cmp__(self, other):
	return cmp(str(self), str(other))

    def __len__(self):
	return int((len(self.path) - 1) / 2)

    def __str__(self):
	if self.path:
	    a = self.path[0]
	    s = self.strprefix
	    for i in range(1, len(self.path), 2):
		r = self.path[i]
		s = r.stra(s)
	else:
	    s = '<Empty Path>'
	return s

    def __repr__(self):
	return repr(str(self))

    def pp(self, output=None):
	if output is None:
	    output = self.output
	print >>output, '%2d:'%self.index, str(self)%self.srcname

    def types(self):
	return [type(x) for x in self.path]



class PathsIter:
    def __init__(self, paths, start=None, stop=None):
	self.paths = paths
	self.mod = paths.mod
	self.stop = stop
	self.reset(start)

    def __iter__(self):
	return self

    def reset(self, idx = None):
	if idx is None:
	    idx = 0
	if idx != 0: # Optimization: don't calculate numpaths in common case.
	    ln = self.paths.numpaths
	    if idx < 0:
		idx = ln + idx
	    if not (0 <= idx < ln):
		self.isatend = 1
		return
	Src = self.paths.Src
	sr = [('%s', src.by(Src.er)) for src in Src.byid.parts]
	srs = []
	idxs = []
	np = 0
	while sr:
	    if idx == 0:
		i, (rel, src) = 0, sr[0]
	    else:
		for i, (rel, src) in enumerate(sr):
		    npnext = np + self.paths.numpaths_from(src)
		    if idx < npnext:
			break
		    np = npnext
		else:
		    assert 0
	    idxs.append(i)
	    srs.append(sr)
	    sr = self.mod.sortedrels(self.paths.IG, src)
	self.pos = idx
	self.idxs = idxs
	self.srs = srs
	self.isatend = not idxs
	

    def next(self):
	paths = self.paths
	if (self.isatend or
	    self.stop is not None and self.pos >= self.stop):
	    raise StopIteration
	path = []
	for row, col in enumerate(self.idxs):
	    sr = self.srs[row]
	    if sr is None:
		sr = self.mod.sortedrels(paths.IG, path[-1])
		self.srs[row] = sr
	    rel, dst = sr[col]
	    path.append(rel)
	    path.append(dst)
	rp = self.mod.Path(paths, path, self.pos, paths.output, paths.srcname)
	self.pos += 1
	while row >= 0:
	    self.idxs[row] += 1
	    if self.idxs[row] < len(self.srs[row]):
		break
	    if row > 0:
		self.srs[row] = None
	    self.idxs[row] = 0
	    row -= 1
	else:
	    self.isatend = 1
	    self.pos = 0
	return rp

class MorePrinter:
    def __init__(self, top, prev=None):
	self.top = top
	if prev is None:
	    prev = top
	self.prev = prev
	self.mod = top.mod
	self.firstpath = self.prev.firstpath + self.maxpaths
	self._hiding_tag_ = self.mod._hiding_tag_

    def __call__(self, start=None, output=None):
	it = self.moreiterator
	if it is None:
	    it = self.iter(start)
	else:
	    if start is not None:
		it.reset(start)
	self.printiter(it, output)
    
    def __getattr__(self, attr):
	if attr == 'more':
	    return MorePrinter(self.top, self)
	else:
	    return getattr(self.top, attr)

    def __repr__(self):
	it = self.iter(self.firstpath)
	output = self.top.mod._root.StringIO.StringIO()
	self.printiter(it, output)
	x = output.getvalue().rstrip()
	if not x:
	    x = '<No more paths>'
	return x
    
    def __str__(self):
	return self.__repr__()

class ShortestPaths:
    firstpath = 0
    maxpaths = 10
    def __init__(self, sg, Dst):
	self.sg = sg
	self.Dst = Dst
	self.mod = mod = sg.mod
	self._hiding_tag_ = mod._hiding_tag_
	self.srcname = sg.srcname
	self.output = mod.output
        self.moreiterator = None
	self.top = self

	self.IG = IG = mod.nodegraph()
	Edges = []
	Y = Dst.nodes
	while Y:
	    R = sg.G.domain_restricted(Y)
	    R.invert()
	    IG.update(R)
	    Edges.append(R)
	    Y = R.get_domain()
	if Edges:
	    Edges.pop()
	    Edges.reverse()
	    self.Src = mod.idset(Edges[0].get_domain())
	else:
	    self.Src = mod.iso()

	self.edges = tuple(Edges)
	sets = []
	for i, e in enumerate(Edges):
	    if i == 0:
		sets.append(mod.idset(e.get_domain()))
	    sets.append(mod.idset(e.get_range()))
	self.sets = tuple(sets)

	self.more = MorePrinter(self)

    def __getitem__(self, idx):
	try:
	    return self.iter(start=idx).next()
	except StopIteration:
	    raise IndexError

    def __iter__(self):
	return self.iter()

    def __repr__(self):
	f = self.mod._root.StringIO.StringIO()
	self.pp(output=f)
	return f.getvalue().rstrip()

    def __str__(self):
	return self.__repr__()

    def iter(self, start=0, stop=None):
	return PathsIter(self, start, stop)

    def aslist(self, maxpaths = None, firstpath = None):
	if maxpaths is None:
	    maxpaths = self.maxpaths
	if firstpath is None:
	    firstpath = self.firstpath
	li = list(self.iter(firstpath, firstpath+maxpaths))
	if len(li) >= maxpaths:
	    more = (self.numpaths - (firstpath + len(li)))
	    if more:
		li.append('<... %d more paths ...>'%more)
	return li

    def copy_but_avoid_edges_at_levels(self, *args):
	avoid = self.edges_at(*args).updated(self.sg.AvoidEdges)
	assert avoid._hiding_tag_ is self.mod._hiding_tag_
	return self.mod.shpaths(self.Dst, self.Src, avoid_edges=avoid)
	#return self.mod.shpaths(self.dst, self.src, avoid_edges=avoid)

    avoided = copy_but_avoid_edges_at_levels

    # The builtin __len__ doesn't always work due to builtin Python restriction to int result:
    # so we don't provide it at all to avoid unsuspected errors sometimes.
    # Use .numpaths attribute instead.
    #	def __len__(self):
    #	   return self.numpaths

    def depth(self):
	pass

    def edges_at(self, *args):
	E = self.mod.nodegraph()
	for col in args:
	    E.update(self.edges[col])
	assert E._hiding_tag_ == self.mod._parent.View._hiding_tag_
	return E

    def numpaths_from(self, Src):
	try:
	    NP = self.NP
	except AttributeError:
	    NP = self.mod.nodegraph(is_mapping = True)
	    NP.add_edges_n1(self.IG.get_domain(), None)
	    for dst in self.Dst.nodes:
		NP.add_edge(dst, 1)
	    self.NP = NP
	numedges = self.mod.hv.numedges
	IG = self.IG
	def np(y):
	    n = NP[y]
	    if n is None:
		n = 0
		for z in IG[y]:
		    sn = NP[z]
		    if sn is None:
			sn = np(z)
		    n += sn * numedges(y, z)
		NP[y] = n
	    return n
	num = 0
	for src in Src.nodes:
	    num += np(src)
	return num

    def _get_numpaths(self):
	num = self.numpaths_from(self.Src)
	self.numpaths = num
	return num

    numpaths = property(fget=_get_numpaths)
	
    def pp(self, start=None, output=None):
	self.moreiterator = None
	self.more(start, output=output)

    def printiter(self, it, output=None):
	if output is None:
	    output = self.output
	self.moreiterator = it
	i = 0
	lastindex = None
	while i < self.maxpaths:
	    try:
		el = it.next()
	    except StopIteration:
		it.reset(0)
		break
	    el.pp(output=output)
	    i += 1
	    lastindex = el.index
	else:
	    if lastindex is not None:
		nummore = self.numpaths-(lastindex+1)
		if nummore == 1:
		    it.next().pp(output=output)
		elif nummore > 1:
		    print >>output, '<... %d more paths ...>'%nummore

class ShortestGraph:
    def __init__(self, mod, G, DstSets, Src, AvoidEdges,
		 srcname=None, dstname=None):
	self.mod = mod
	self.G = G
	self.Src = Src
	self.DstSets = DstSets
	self.AvoidEdges = AvoidEdges
	if srcname is None:
	    if Src.count == 1:
		srcname = mod.srcname_1
	    else:
		srcname = mod.srcname_n
	self.srcname = srcname
	if dstname is None:
	    dstname = mod.dstname
	self.dstname = dstname

    def __getitem__(self, idx):
	return self.mod.ShortestPaths(self, self.DstSets[idx])
	
    def __len__(self):
	return len(self.DstSets)

    def __str__(self):
	f = self.mod._root.StringIO.StringIO()
	self.pp(f)
	return f.getvalue()

    def pp(self, output=None):
	if output is None:
	    output = self.mod.output
	for i, p in enumerate(self):
	    print >>output, '--- %s[%d] ---'%(self.dstname, i)
	    p.pp(output=output)
	


class _GLUECLAMP_:
    _preload_ = ('_hiding_tag_',)
    _chgable_ = ('output', 'srcname_1', 'srcname_n')

    srcname_1 = 'Src'
    srcname_n = '_str_of_src_'
    dstname = 'Dst'

    _imports_ = (
	'_parent.ImpSet:mutnodeset',
	'_parent.Use:idset',
	'_parent.Use:iso',
	'_parent.Use:Nothing',
	'_parent.Use:reprefix',
	'_parent.UniSet:idset_adapt',
	'_parent.View:hv',
	'_parent.View:nodegraph',
	'_parent:View', # NOT View.root, since it may change 
	)

    def _get_rel_table(self):
	table = {}
	for name in dir(self._module):
	    if name.startswith('R_'):
		c = getattr(self, name)
		class r(c, self.RelationBase):
		    saferepr = self.saferepr
		r.__name__= 'Based_'+name
		table[c.code] = r
	return table

    def _get__hiding_tag_(self):return self._parent.View._hiding_tag_
    def _get_identity(self):	return R_IDENTITY()
    def _get_norelation(self):	return R_NORELATION()
    def _get_output(self):	return self._parent.OutputHandling.stdout
    def _get_saferepr(self):	return self._root.repr.repr
    def _get_shpathstep(self):	return self.hv.shpathstep


    def sortedrels(self, IG, Src):
	t = []
	iso = self.iso
	for src in Src.nodes:
	    for dst in IG[src]:
		Dst = iso(dst)
		for rel in self.relations(src, dst):
		    t.append((rel, Dst))
	t.sort(lambda (rel1, dst1), (rel2, dst2) : cmp(rel1, rel2))
	return t
	

    def prunedinverted(self, G, Y):
	IG = self.nodegraph()
	while Y:
	    R = G.domain_restricted(Y)
	    R.invert()
	    IG.update(R)
	    Y = R.get_domain()
	return IG
	    
    def relation(self, src, dst):
	tab = self.relations(src, dst)
	if len(tab) > 1:
	    r = MultiRelation(tab)
	elif not tab:
	    r = self.norelation
	else:
	    r = tab[0]
	return r

    def relations(self, src, dst):
	tab = []
	if src is dst:
	    tab.append(self.identity)
	rawrel = self.hv.relate(src, dst)
	for i, rs in enumerate(rawrel):
	    for r in rs:
		tab.append(self.rel_table[i](r))
	if not tab:
	    tab = [self.norelation]
	return tab

    def shpaths(self, dst, src=None, avoid_nodes=None, avoid_edges=()):
	return self.shpgraph([dst], src, avoid_nodes, avoid_edges)[0]

    def shpgraph(self, DstSets, src=None, avoid_nodes=None, avoid_edges=(),
		 srcname=None, dstname=None):
	if src is None:
	    Src = self.iso(self.View.root)
            if srcname is None and self.View.root is self.View.heapyc.RootState:
                srcname = '%sRoot'%self.reprefix
	else:
	    Src = self.idset_adapt(src)
	if avoid_nodes is None:
	    AvoidNodes = self.Nothing
	else:
	    AvoidNodes = self.idset_adapt(avoid_nodes)
	AvoidEdges = self.nodegraph(avoid_edges)
	G, DstSets = self.shpgraph_algorithm(DstSets, Src, AvoidNodes, AvoidEdges)

	return self.ShortestGraph(self, G, DstSets, Src, AvoidEdges,
				  srcname, dstname)

    def shpgraph_algorithm(self, DstSets, Src, AvoidNodes, AvoidEdges):
	U = (Src - AvoidNodes).nodes
	S = self.mutnodeset(AvoidNodes.nodes)
	G = self.nodegraph()
	unseen = list(enumerate(DstSets))
	DstSets = [self.Nothing]*len(DstSets)
	while U and unseen:
	    S |= U
	    U = self.shpathstep(G, U, S, AvoidEdges)
	    unseen_ = []
	    for i, D in unseen:
		D_ = D & U
		if D_:
		    DstSets[i] = D_
		else:
		    unseen_.append((i, D))
	    unseen = unseen_
	return G, [self.idset_adapt(D) for D in DstSets]

class _Specification_:
    class GlueTypeExpr:
	exec("""\
if 1:
	shpgraph	<in>	callable
    
""".replace('<in>', ' = lambda IN : '))
