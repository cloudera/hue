#._cv_part guppy.etc.RE_Rect
""" Support functions for RE simplification.
This module is intended for use by the RE module.
It is in a separate module to keep RE itself cleaner
since the algorithm, 'rectangle selection', is a quite
separate part that depends on some tricky heuristics.

The primary entry function is

chooserects(lines, gauges, trace)

It chooses 'the best' rectangles from lines to base simplification on.
A weight on atoms is given by gauges.
The trace parameter is for debugging.

pr() gives some example usages of chooserects.

"""

from guppy.sets import immbitset, mutbitset, immbitrange

class Rect(object):
    __slots__ = 'width', 'lines', 'gainmemo', 'lnos', 'all_lines', 'common_part'
    def __init__(self, width, lines):
	self.width = width
	self.lines = lines
	assert not (width and len(lines) == 1)
	self.gainmemo = {}

    def init2(self, lnobyid, all_lines):
	self.all_lines = all_lines
	self.lnos = immbitset([lnobyid[id(line)] for line in self.lines])
	self.common_part = self.get_common_part()

    def reducelines(self, lnos):
	# Reduce lines of self by removing some lines
	# Argument: lnos, a 'set' of line numbers to remove
    
	olnos = self.lnos
	lnos = olnos & ~lnos
	if lnos != olnos:
	    self.lnos = lnos
	    self.lines = [self.all_lines[lno] for lno in lnos]
	if len(lnos) == 1:
	    self.width = len(self.lines[0])

    def get_lines(self, pickednos = 0):
	lines = []
	for i in self.lnos & ~ pickednos:
	    lines.append(self.all_lines[i])
	return lines

    def __str__(self):
	return '<\n dir = %d\n width = %d\n lnos = %s\n lines = %s\n>'%(
	    self.dir, self.width, list(self.lnos), self.lines)

    __repr__=__str__


class LeftRect(Rect):
    __slots__ = ()
    dir = 0
    def get_common_part(self):
	return self.lines[0][:self.width]

    def get_uncommons(self, pickednos=0):
	uc = []
	for line in self.get_lines(pickednos):
	    uc.append(line[self.width:])
	return uc

class RightRect(Rect, object):
    __slots__ = ()
    dir = -1
    def get_common_part(self):
	lo = -self.width
	if lo == 0:
	    return []
	return self.lines[0][lo:]

    def get_uncommons(self, pickednos=0):
	uc = []
	hi = -self.width
	if hi == 0:
	    hi = None
	for line in self.get_lines(pickednos):
	    uc.append(line[:hi])
	return uc

def sum_gauge(gauge, lst):
    global hits, misses
    if gauge is None:
	return len(lst)
    else:
	gain = 0
	for x in lst:
	    gain += gauge(x)
    return gain
    
def cmp_gauged(xs, ys, gauges):
    for gauge in gauges:
	gx = sum_gauge(gauge, xs)
	gy = sum_gauge(gauge, ys)
	c = cmp(gx, gy)
	if c:
	    return c
    return 0

class InducedRect:
    def __init__(self, s, lines, lnos):
	self.s = s
	self.width = s.width
	self.all_lines = s.all_lines
	self.lines = lines
	self.lnos = lnos

	

class InducedRightRect(InducedRect, RightRect):
    pass

class InducedLeftRect(InducedRect, LeftRect):
    pass



def brect(lines):
    if len(lines) <= 1:
	return [LeftRect(0, lines)]
    newrects = [LeftRect(0, lines), RightRect(0, lines)]
    donerects = []
    while newrects:
	oldrects = newrects
	newrects = []
	for r in oldrects:
	    width = r.width
	    while 1:
		is_done = 0
		d = {}
		pos = width ^ r.dir
		for line in r.lines:
		    if width < len(line):
			d.setdefault(line[pos], []).append(line)
		    else:
			is_done = 1
		if is_done or len(d) != 1:
		    break
		r.width = width = width + 1
	    donerects.append(r)
	    width += 1
	    for k, v in d.items():
		if len(v) > 1:
		    new_r = r.__class__(width, v)
		    newrects.append(new_r)
		
    return donerects

def choose(rects, lines = [], gauges = [None], trace=''):
    def induce(r):
	if trace == 'induce':
	    pdb.set_trace()
	uncommons = r.get_uncommons()
	if len(uncommons) < 2:
	    return
	irs = []
	for s in rects:
	    if s.dir != r.dir:
		continue
	    pss = []
	    uncs = s.get_uncommons(pickednos)
	    lnos = s.lnos & ~pickednos
	    assert len(uncs) == len(lnos)
	    for unc, lno in zip(uncs, lnos):
		if unc in uncommons:
		    pss.append(lno)
	    if len(pss) == len(uncommons):
		pslnos = immbitset(pss)
		pss = [lines[lno] for lno in pss]
		if s.dir == -1:
		    c = InducedRightRect
		else:
		    c = InducedLeftRect
		ir = c(s, pss, pslnos)
		if trace == 'indap':
		    pdb.set_trace()
		irs.append(ir)
		
	if irs:
	    #pdb.set_trace()
	    news.extend(irs)
		
	
    def overlap(r):
	#
	if 'overlap' in trace:
	    pdb.set_trace()
	rlnos = r.lnos
	tonews = []
	for s in rects:
	    if s is r:
		continue
	    if s.dir != r.dir:
		continue
	    slnos = s.lnos
	    if not (slnos & rlnos):
		continue
	    slnos &= ~ pickednos
	    if not slnos:
		# remove
		continue
	    scom = s.common_part
	    if not scom:
		continue
	    for t in rects:
		if t is s:
		    continue
		if t.dir == s.dir:
		    continue
		tlnos = t.lnos & ~pickednos
		if (tlnos & rlnos):
		    continue
		olnos = tlnos & slnos
		if not olnos:
		    continue
		if slnos == tlnos:
		    continue
		tcom = t.common_part
		if not tcom:
		    continue
		c = cmp_gauged(scom, tcom, gauges)
		if c > 0:
		    continue
		
		if trace == 'obreak':
		    pdb.set_trace
		break
		    
	    else:
		# s is ok
		tonews.append(s)
		rects.remove(s)
	if len(tonews) > 1:
	    pdb.set_trace()
	news.extend(tonews)

    def picknext():
	while 1:
	    if news:
		if trace == 'news':
		    pdb.set_trace()
		r = news[0]
		del news[0]
	    else:
		r = None
		for s in list(rects):
		    slnos = s.lnos - pickednos
		    if not slnos:
			rects.remove(s)
			continue
		    sn = len(slnos) - 1
		    sw = s.width
		    if r is not None:
			if not sw:
			    break
			if not sn:
			    continue
			if rwn:
			    rmemo = r.gainmemo
			    smemo = s.gainmemo
			    c = 0
			    for gauge in gauges:
				try:
				    gr = rmemo[gauge]
				except KeyError:
				    gr = sum_gauge(gauge, r.common_part)
				    rmemo[gauge] = gr
				gr *= rn
				try:
				    gs = smemo[gauge]
				except KeyError:
				    gs = sum_gauge(gauge, s.common_part)
				    smemo[gauge] = gs
				gs *= sn
				c = gr - gs
				if c:
				    break
			    if c >= 0:
				continue
		    r = s
		    rlnos = slnos
		    if not sw:
			break
		    rn = sn
		    rw = sw
		    rwn =  sn * sw
		if r is not None:
		    rects.remove(r)
	    if r is not None:
		r.reducelines(pickednos)
		if r.lnos:
		    return r

    def cmpinit(x, y):
	wx = x.width
	wy = y.width
	c = wy - wx
	if c:
	    return c
	c = y.dir - x.dir
	if c:
	    return c
	c = cmp(x.lnos[0], y.lnos[0])
	return c

    if gauges[0] == None:
	gauges = gauges[1:]


    lnobyid = dict([(id(line), i) for i, line in enumerate(lines)])

    orects = rects
    rects = list(orects)


    for r in rects:
	r.init2(lnobyid, lines)

    rects.sort(cmpinit)

    allnos = immbitrange(len(lines))

    pickednos = mutbitset()
    pickedrects = []

    news = []
    while pickednos != allnos:
	r = picknext()
	pickednos |= r.lnos
	pickedrects.append(r)
	induce(r)
	if trace == 'induced':
	    pdb.set_trace()
	overlap(r)

    if trace == 'chosorted':
	pdb.set_trace()

    if trace == 'choosen':
	pdb.set_trace()
    return pickedrects


def chooserects(lines, gauges = [None], trace=''):
    rects = brect(lines)
    choosen = choose(rects, lines, gauges, trace)
    return choosen


def pr():
    x = chooserects(['abc','ade'])
    x = chooserects(['abc',
		 'abe',
		 'ace',
		 'xby'])

    print x
    x = chooserects(['ab1',
		 'ab2',
		 'ac3',
		 'ac4'])

    print x
	
    # Case where.. (from right).. :
    # the total gain of two rects (bfbf+cfcf = 4) is greater than the gain of another
    # overlapping rect (ffff == 3), although the individual gains are less (= 2).
    # But in this case at least, the end result should likely become the same

    x = chooserects([
	'1bf',
	'2bf',
	'3cf',
	'4cf'])

    print x

    # Case where it chooses twice..


    x = chooserects([
	'abc',
	'abd',
	'bcx',
	'bdy'
	])

    print 'TW',x

    # Case where it didn't choose enough rects

    x = ([
	'abc',
	'abd',
	'e'
	])

    print chooserects(x)

    # Case where it should prefer one side or the other
    # i.e. left traditionally

    print chooserects(['abc','axc'])

    # Case where it should give a width 0 rect

    print chooserects(['a',''])

    # Case with overlap

    print chooserects(['abcd','abce','a','f'])

    # Case with induce

    print chooserects(['abcd','abce','d','e'])


    print chooserects(['auvw', 'buvw', 'a', 'b'])
    print chooserects(['axuvw','bxuvw','axy','bxy','cy'])
    
    # Case with overlap reversed as per Mar 4

    print chooserects(['dcba','ecba','a','f'], trace='choosen')

def tmany():
    for i in range(100):
	x = chooserects(['abc',
	     'abe',
	     'ace',
	     'xby'])


