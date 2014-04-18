#._cv_part guppy.heapy.Part

class Format(object):
    __slots__ = 'impl', 'mod'
    def __init__(self, impl):
	self.impl = impl
	self.mod = impl.mod

    def get_formatted_row(self, row):
	fr = self.get_stat_data(row)
	rows = []
	rs = row.name.split('\n')
	subsequent_indent = len(fr)*' '
	rows.extend(self.mod.wrap(
	    fr+rs[0],
	    width=self.mod.line_length,
	    subsequent_indent=subsequent_indent))

	for r in rs[1:]:
	    rows.extend(self.mod.wrap(
		r,
		width=self.mod.line_length,
		initial_indent=subsequent_indent,
		subsequent_indent=subsequent_indent))
	return '\n'.join(rows)

    def get_more_index(self, idx=None):
	if idx is None:
	    idx = 0
	idx += 10
	return idx

    def get_row_header(self):
        impl = self.impl
        if not (impl.count or impl.size):
            return ''
	sh = self.get_stat_header()
	return self.mod.fill(
	    sh + self.impl.kindheader,
	    width=self.mod.line_length,
	    subsequent_indent=' '*len(sh))

    def load_statrow_csk(self, r):
	impl = self.impl
	count, size, kind = r.split(' ', 2)
	count = int(count)
	size = int(size)
	impl.cum_size += size
	return StatRow(count, size, kind, impl.cur_index, impl.cum_size)
	
    def load_statrow_sk(self, r):
	impl = self.impl
	size, kind = r.split(' ', 1)
	size = int(size)
	impl.cum_size += size
	return StatRow(1, size, kind, impl.cur_index, impl.cum_size)

    def ppob(self, ob, idx=None):
	impl = self.impl
	if idx is None:
	    label = self.get_label()
	    if label is not None:
		print >>ob, label
	    idx = 0
	if idx < 0:
	    idx = impl.numrows + startindex

	it = impl.get_rows(idx)
	print >>ob, self.get_row_header()
	numrows = 0
	for row in it:
	    form = self.get_formatted_row(row)
	    print >>ob, form
	    numrows += 1
	    if numrows >= 10:
		nummore = impl.numrows - 1 - row.index
		if nummore > 1:
		    print >>ob, \
"<%d more rows. Type e.g. '_.more' to view.>"%nummore
		    break


class SetFormat(Format):
    __slots__ = ()
    def get_label(self):
	impl = self.impl
	if impl.count != 1:
	    s = 's'
	else:
	    s = ''
	return 'Partition of a set of %d object%s. Total size = %d bytes.'%(
	    impl.count, s, impl.size)


    def get_rowdata(self, row):
	return '%d %d %s'%(row.count, row.size, row.name)

    def get_stat_header(self):
	return (
' Index  Count   %     Size   % Cumulative  % ')

    def get_stat_data(self, row):
	format = '%6d %6d %3d %8d %3d %9d %3d '
	impl = self.impl
	fr = format % (
	    row.index,
	    row.count, int('%.0f'%(row.count * 100.0/impl.count)),
	    row.size, int('%.0f'%(row.size * 100.0/impl.size)),
	    row.cumulsize, int('%.0f'%(row.cumulsize * 100.0/impl.size)),
	    )
	return fr
    
    def load_statrow(self, r):
	return self.load_statrow_csk(r)

class IdFormat(Format):
    __slots__ = ()
    def get_label(self):
	impl = self.impl
	if impl.count != 1:
	    s = 's'
	else:
	    s = ''
	return (
'Set of %d %s object%s. Total size = %d bytes.'%(
    impl.count, impl.kindname, s, impl.size))
	return part

    def get_rowdata(self, row):
	return '%d %s'%(row.size, row.name)

    def get_stat_header(self):
	return (
' Index     Size   %   Cumulative  %   ')

    def get_stat_data(self, row):
	impl = self.impl
	format = '%6d %8d %5.1f %9d %5.1f '
	fr = format % (
	    row.index,
	    row.size, (row.size * 100.0/impl.size),
	    row.cumulsize, row.cumulsize * 100.0/impl.size,
	    )
	return fr

    def load_statrow(self, r):
	return self.load_statrow_sk(r)

class DiffFormat(Format):
    __slots__ = ()

    def _percent_of_b(self, size):
	if self.impl.b_size != 0:
	    return '%9.3g'%(size*100.0/self.impl.b_size,)
	else:
	    return '   (n.a.)'

    def get_label(self):
	impl = self.impl
	x = (
'Summary of difference operation (A-B).\n'+
'        Count     Size\n'+
'  A    %6d %8d\n'%(impl.count+impl.b_count, impl.size+impl.b_size)+
'  B    %6d %8d\n'%(impl.b_count, impl.b_size)+
'  A-B  %6d %8d  = %s %% of B\n'%(impl.count, impl.size, self._percent_of_b(impl.size)))

	if impl.count or impl.size:
            x += '\nDifferences by kind, largest absolute size diffs first.'
        return x

    def get_rowdata(self, row):
	return '%d %d %s'%(row.count, row.size, row.name)

    def get_stat_header(self):
        return (
' Index  Count     Size  Cumulative  % of B ')

    def get_stat_data(self, row):
	impl = self.impl
	format = '%6d %6d %8d %9d %s '
	fr = format % (
	    row.index,
	    row.count,
	    row.size,
	    row.cumulsize,
	    self._percent_of_b(row.cumulsize),
	    )
	return fr
    
    def load_statrow(self, r):
	return self.load_statrow_csk(r)

class StatRow(object):
    __slots__ = 'count', 'size', 'name', 'index', 'cumulsize'

    def __init__(self, count, size, name, index=None, cumulsize=None):
	self.count = count
	self.size = size
	self.name = name
	self.index = index
	self.cumulsize = cumulsize

class PartRow(StatRow):
    __slots__ = 'set', 'kind'

    def __init__(self, count, size, name, index, cumulsize, set, kind):
	self.count = count
	self.size = size
	self.name = name
	self.index = index
	self.cumulsize = cumulsize
	self.set = set
	self.kind = kind

class Stat:
    def __init__(self, mod, get_trows, firstheader=''):
	self.mod = mod
	self._hiding_tag_ = mod._hiding_tag_
	self.get_trows = get_trows
        self.firstheader = firstheader

	self.it = iter(get_trows())

	self.cur_index = 0
	self.cum_size = 0
	self.rows = []

	r = self.get_next()
	while r and not r.startswith('.r:'):
	    name = r[1:r.index(':')]
	    value = r[r.index(':')+1:].strip()
	    try:
		value = int(value)
	    except ValueError:
		pass
	    setattr(self, name, value)
	    r = self.get_next()

	self.format_name = self.format
	self.format_class = getattr(self.mod, self.format)
	self.format = self.format_class(self)

	self.timemade = float(self.timemade)

    def __getitem__(self, idx):
	if  isinstance(idx, (int, long)):
	    if idx < 0:
		idx = self.numrows + idx
	    if not (0 <= idx < self.numrows):
		raise IndexError, 'Stat index out of range.'
	    rows = [self.get_row(idx)]
	elif isinstance(idx, slice):
	    start, stop, step = idx.indices(self.numrows)
	    rows = [self.get_row(idx) for idx in range(start, stop, step)]
	else:
	    raise IndexError, 'Stat indices must be integers or slices.'

	count = 0
	size = 0
	for r in rows:
	    count += r.count
	    size += r.size

	trows = [
	    '.loader: _load_stat',
	    '.format: %s'%self.format_name,
	    '.timemade: %f'%self.timemade,
	    '.count: %d'%count,
	    '.size: %d'%size,
	    '.kindheader: %s'%self.kindheader,
	    '.kindname: %s'%self.kindname,
	    '.numrows: %d'%len(rows),
	    ]
	if getattr(self, 'b_count', None) is not None:
	    trows.append('.b_count: %d'%self.b_count)
	    trows.append('.b_size: %d'%self.b_size)
	for r in rows:
	    trows.append('.r: %s'%self.format.get_rowdata(r))
	return self.mod.load(trows)

    def __len__(self):
	return self.numrows

    def __repr__(self):
	ob = self.mod.output_buffer()
	self.ppob(ob)
	return self.firstheader + ob.getvalue().rstrip()

    def __sub__(self, other):
	if not isinstance(other, Stat):
	    raise TypeError, 'Can only take difference with other Stat instance.'
	if self.kindheader != other.kindheader:
	    raise ValueError, 'Mismatching table kind header, %r vs %r.'%(
		self.kindheader, other.kindheader)
	rows = []
	otab = {}
	stab = {}
	for r in other.get_rows():
	    o = otab.get(r.name)
	    if o:
		otab[r.name] = StatRow(r.count+o.count, r.size+o.size, r.name, o.index,  None)
	    else:
		otab[r.name] = r
	for r in self.get_rows():
	    o = otab.get(r.name)
	    if o:
		del otab[r.name]
		count = r.count - o.count
		size = r.size - o.size
	    else:
		count = r.count
		size = r.size
	    if count == 0 and size == 0:
		continue
	    sr = stab.get(r.name)
	    if sr:
		sr.count += count
		sr.size += size
	    else:
		sr = StatRow(count, size, r.name)
		stab[sr.name] = sr
		rows.append(sr)
	rs = otab.values()
	rs.sort(lambda x,y:cmp(x.index, y.index)) # Preserve orig. order
	for r in rs:
	    sr = StatRow(-r.count, -r.size, r.name)
	    assert sr.name not in stab
	    rows.append(sr)
	rows.sort(lambda x,y:cmp(abs(y.size), abs(x.size)))
	cumulcount = 0
	cumulsize = 0
	for r in rows:
	    cumulcount += r.count
	    cumulsize += r.size
	    r.cumulsize = cumulsize
	trows = [
	    '.loader: _load_stat',
	    '.format: DiffFormat',
	    '.timemade: %f'%self.mod.time.time(),
	    '.b_count: %d'%other.count,
	    '.b_size: %d'%other.size,
	    '.count: %d'%cumulcount,
	    '.size: %d'%cumulsize,
	    '.kindheader: %s'%self.kindheader,
	    '.kindname: %s'%self.kindname,
	    '.numrows: %d'%len(rows),
	    ]
	for r in rows:
	    trows.append('.r: %d %d %s'%(r.count, r.size, r.name))
	return self.mod.load(trows)
	   
    def dump(self, fn, mode='a'):
	if not hasattr(fn, 'write'):
	    f = open(fn, mode)
	else:
	    f = fn
	try:
	    for r in self.get_trows():
		if not r[-1:] == '\n':
		    r += '\n'
		f.write(r)
	    end = '.end: .loader: %s\n'%self.loader
	    if r != end:
		f.write(end)
	finally:
	    if f is not fn:
		f.close()

    def _get_more(self):
	return self.mod.basic_more_printer(self, self)
	
    more = property(_get_more)

    def get_more_index(self, idx=None):
	return self.format.get_more_index(idx)

    def get_next(self):
	try:
	    r = self.it.next()
	except StopIteration:
	    r = None
	else:
	    r = r.rstrip('\n')
	self.last = r
	return r

    def get_row(self, idx):
	while idx >= len(self.rows):
	    self.parse_next_row()
	return self.rows[idx]

    def get_rows(self, idx = None):
	if idx is None:
	    idx = 0
	while idx < self.numrows:
	    try:
		row = self.get_row(idx)
	    except IndexError:
		return
	    else:
		yield row
	    idx += 1

    def get_rows_of_kinds(self, kinds):
	# Return the rows with names in sequence kinds of unique names
	# in that order. None if no such kind.

	kindtab = {}
	N = len(kinds)
	res = [None] * len(kinds)
	for i, kind in enumerate(kinds):
	    kindtab[kind] = i
	assert len(kindtab) == N

	n = 0
	for row in self.get_rows():
	    idx = kindtab.get(row.name)
	    if idx is not None:
		res[idx] = row
	    n += 1
	    if n >= N:
		break
	return res

    def get_rows_n_and_other(self, N, sortby='Size'):
	# Get N rows, the largest first
	# mix in an '<Other>' row at a sorted position
	# Size is either size if sortby = 'Size',
	#    or count if sortby = 'Count'.
	# Returns a NEW LIST (caller may modify/sort it)

	if sortby not in ('Size', 'Count'):
	    raise ValueError, "Argument 'sortby' must be 'Size' or 'Count'."

	# Rows are already sorted by Size, largest first.
	# If they want by Count, we need to resort them.

	rows = self.get_rows()

	if sortby == 'Count':
	    rows = list(rows)
	    rows.sort(lambda x, y: cmp(y.count, x.count))
	
	retrows = []
	cumulcount = 0
	cumulsize = 0
		    
	for (i, r) in enumerate(rows):
	    if i >= N:
		othercount = self.count - cumulcount
		othersize = self.size - cumulsize
		other = StatRow(othercount,
				othersize,
				'<Other>')
				
		if sortby == 'Size':
		    for (i, r) in enumerate(retrows):
			if r.size < othersize:
			    retrows[i:i] = [other]
			    break
		    else:
			retrows.append(other)
		elif sortby == 'Count':
		    for (i, r) in enumerate(retrows):
			if r.count < othercount:
			    retrows[i:i] = [other]
			    break
		    else:
			retrows.append(other)
		else:
		    assert 0
		break

	    cumulcount += r.count
	    cumulsize += r.size
	    retrows.append(r)
	else:
	    assert cumulcount == self.count
	    assert cumulsize == self.size

	return retrows

    def parse_next_row(self):
	r = self.last
	if not r:
	    raise IndexError, 'Row index out of range.'
	if r.startswith('.r: '):
	    r = r[4:]
	    sr = self.format.load_statrow(r)

	    self.cur_index += 1
	    self.rows.append(sr)
	    self.get_next()
	    return

	elif r.startswith('.end'):
	    raise IndexError, 'Row index out of range.'
	else:
	    raise SyntaxError
		
    def ppob(self, ob, idx=None):
	return self.format.ppob(ob, idx)

class Partition:
    def __init__(self, mod, set, er):
	self.mod = mod
	self.set = set
	self.er = er
	self._hiding_tag_ = mod._hiding_tag_
	self.timemade = mod.time.time()
	
    def __iter__(self):
	# The default iteration is over the sets
	# To iterate over rows (if more info is needed), get_rows() is available.
	return self.get_sets()

    def get_more_index(self, idx=None):
	return self.format.get_more_index(idx)

    def get_rows(self, rowindex = None):
	# Iterator over rows
	if rowindex is None:
	    rowindex = 0
	while 1:
	    try:
		row = self.get_row(rowindex)
	    except IndexError:
		return
	    else:
		yield row
	    rowindex += 1
	    
    def get_set(self, index):
	if isinstance(index, slice):
	    start, stop, step = index.indices(self.numrows)
	    ns = self.get_nodeset(start, stop, step)
	    return self.mod.idset(ns, er=self.er)
	else:
	    if index < 0:
		index += self.numrows
	    return self.get_rowset(index)

    def get_sets(self, index=None):
	for idx in range(self.numrows):
	    yield self.get_rowset(idx)

    def get_stat(self):
        # Avoid any references into the set!
        trows = list(self.get_trows())
        def get_trows():
            return trows
	return self.mod._load_stat(get_trows)

    def get_trows(self):
	yield '.loader: _load_stat'
	yield '.format: %s'%self.format.__class__.__name__
	yield '.timemade: %f'%self.timemade
	yield '.count: %d'%self.count
	yield '.size: %d'%self.size
	yield '.kindname: %s'%self.kindname
	yield '.kindheader: %s'%self.kindheader
	yield '.numrows: %d'%self.numrows
	for row in self.get_rows():
	    yield '.r: %s'%self.format.get_rowdata(row)

    def init_format(self, FormatClass):
	self.format = FormatClass(self)

    def ppob(self, ob, idx=None):
	return self.format.ppob(ob, idx)

class IdentityPartitionCluster(object):
    # Contains objects of same size.
    # to speed up management of identity partition
    # - since otherwise we'd have to sort all the objects,
    #   on their string representation in worst case.
    __slots__ = 'objects','locount','hicount','losize','obsize','issorted'
    def __init__(self, objects, locount, count, losize, obsize):
	self.objects = objects		# tuple of objects in this segment
	self.locount = locount	 	# count BEFORE objects in this cluster
	self.hicount = locount+count	# count AFTER these objects
	self.losize = losize		# size BEFORE  objects in this cluster
	self.obsize = obsize		# size of EACH object in this segment
	self.issorted = False		# indicates if .objects is sorted
	

class IdentityPartition(Partition):
    def __init__(self, mod, set, er):
	Partition.__init__(self, mod, set, er)

	clusters = []
	sizeclasses = mod.Size.classifier.partition_cli(set.nodes)
	sizeclasses.sort()
	sizeclasses.reverse()
	totcount = 0
	totsize = 0
	for size, v in sizeclasses:
	    count = len(v)
	    clusters.append(IdentityPartitionCluster(
		self.mod.observation_list(v), totcount, count, totsize, size))
	    totsize += size * count
	    totcount += count
	assert totcount == set.count

	self.cluidx = 0
	self.clusters = clusters
	self.count = totcount
	self.kind = kind = set.byclodo.kind
	self.kindheader = kind.fam.c_get_idpart_header(kind)
	self.kindname = kind.fam.c_get_idpart_label(kind)
	self.numrows = totcount
	self.render = kind.fam.c_get_idpart_render(kind)
	self.size = totsize
	self.sortrender = kind.fam.c_get_idpart_sortrender(kind)

	self.init_format(IdFormat)

    def get_nodeset(self, start, stop, step):
	return self.get_nodeset_cluster(start, stop, step)[0]

    def get_nodeset_cluster(self, start, stop, step):
	if step <= 0:
	    raise ValueError, 'Step must be positive.'
	ns = self.mod.mutnodeset()
	if start >= stop:
	    return (ns, None)
	clusters = self.clusters
	lo = 0
	hi = len(clusters)
	cluidx = self.cluidx

	while lo < hi:
	    clu = clusters[cluidx]
	    if clu.locount <= start:
		if start < clu.hicount:
		    break
		else:
		    lo = cluidx + 1
	    else:
		hi = cluidx
	    cluidx = (lo + hi) // 2
	else:
	    return (ns, None)
	clu_to_return = clu

	while 1:
	    objects = clu.objects
	    if start != clu.locount or stop < clu.hicount or step != 1:
		if not clu.issorted:
		    sortrender = self.sortrender
		    if sortrender == 'IDENTITY':
			ks = objects
		    else:
			ks = [sortrender(x) for x in objects]
		    ks = [(kind, i) for i, kind in enumerate(ks)]
		    ks.sort()
		    clu.objects = objects = self.mod.observation_list(
			[objects[i] for (kind, i) in ks])
		    clu.issorted = True
		objects = objects[start-clu.locount:stop-clu.locount:step]

	    ns |= objects
	    self.cluidx = cluidx # memo till next call
	    start += len(objects)*step
	    if start >= stop:
		break
	    for cluidx in range(cluidx + 1, len(clusters)):
		clu = clusters[cluidx]
		if clu.locount <= start < clu.hicount:
		    break
	    else:
		break
	return (ns, clu_to_return)

    def get_row(self, rowidx):
	ns, clu = self.get_nodeset_cluster(rowidx, rowidx+1, 1)
	if not ns:
	    raise IndexError, 'Partition index out of range.'
	vi = self.mod.idset(ns, er=self.er)
	row = PartRow(1, clu.obsize, self.render(vi.theone),
		      rowidx, (rowidx+1-clu.locount)*clu.obsize + clu.losize,
		      vi, vi.kind)
	return row

    def get_rowset(self, rowidx):
	ns = self.get_nodeset(rowidx, rowidx+1, 1)
	if not ns:
	    raise IndexError, 'Partition index out of range.'
	return self.mod.idset(ns, er=self.er)


class SetPartition(Partition):
    def __init__(self, mod, set, er):
	Partition.__init__(self, mod, set, er)

	classifier = er.classifier
	tosort = [(-part.size, classifier.get_tabrendering(kind, ''), kind, part)
		  for (kind, part) in classifier.partition(set.nodes)]
	tosort.sort()
	cumulsize = 0
	rows = []
	for (minusize, name, kind, part) in tosort:
	    size = -minusize
	    cumulsize += size
	    # assert size == part.size
	    rows.append(PartRow(
		part.count, size, name,
		len(rows), cumulsize,
		part, kind))
	    
        # No check. Sizes may change. Note feb 8 2006.
        #assert cumulsize == set.size

	self.count = set.count
	self.kindheader = classifier.get_tabheader('')
	self.kindname = ''
	self.numrows = len(rows)
	self.rows = rows
	self.size = cumulsize

	self.init_format(SetFormat)

    def get_nodeset(self, start, stop, step):
	if step <= 0:
	    raise ValueError, 'Step must be positive.'
	ns = self.mod.mutnodeset()	
	while start < stop:
	    ns |= self.rows[start].set.nodes
	    start += step
	return ns

    def get_row(self, idx):
	try:
	    return self.rows[idx]
	except IndexError:
	    raise IndexError, 'Partition index out of range.'

    def get_rowset(self, idx):
	return self.get_row(idx).set


class _GLUECLAMP_:
    _preload_ = ('_hiding_tag_',)
    _chgable_ = ('line_length', 'backup_suffix')
    _imports_ = (
	'_parent.OutputHandling:output_buffer',
	'_parent.OutputHandling:basic_more_printer',
	'_parent.ImpSet:mutnodeset',
	'_parent.Use:Id',
	'_parent.Use:Size',
	'_parent.Use:idset',
	'_parent.Use:load',
	'_parent.View:_hiding_tag_',
	'_parent.View:observation_list',
	'_root.os:rename',
	'_root.textwrap:fill',
	'_root.textwrap:wrap',
	'_root.textwrap:wrap',
	'_root:time',
	)
    
    # 'Config'

    line_length = 100
    backup_suffix = '.old'
    

    # Factory method

    def partition(self, set, er):
	if er.classifier is self.Id.classifier:
	    return IdentityPartition(self, set, er)
	else:
	    return SetPartition(self, set, er)
    
    # Private - Use.load is intended to be used directly.
    def _load_stat(self, get_trows):
	return Stat(self, get_trows)
