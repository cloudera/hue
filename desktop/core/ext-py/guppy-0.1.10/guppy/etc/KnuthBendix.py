#._cv_part guppy.etc.KnuthBendix

"""
    An implementation of the Knuth-Bendix algorithm,
    as described in (1), p. 143.
    For determining if two paths in a category are equal.

The algorithm as given here,
takes a set of equations in the form of a sequence:

E = [(a, b), (c, d) ...]

where a, b, c, d are 'paths'.

Paths are given as strings, for example:

E = [ ('fhk', 'gh'), ('m', 'kkm') ]

means that the path 'fhk' equals 'gh' and 'm' equals 'kkm'.

Each arrow in the path is here a single character.  If longer arrow
names are required, a delimiter string can be specified as in:

kb(E, delim='.')

The paths must then be given by the delimiter between each arrow;

E = [ ('h_arrow.g_arrow', 'g_arrow.k_arrow') ... ]


The function kb(E) returns an object, say A, which is

o callable: A(a, b)->boolean determines if two paths given by a, b are equal.
o has a method A.reduce(a)->pathstring, which reduces a path to normal form.

An optional parameter to kb, max_iterations, determines the maximum
number of iterations the algorithm should try making the reduction
system 'confluent'. The algorithm is not guaranteed to terminate
with a confluent system in a finite number of iterations, so if the
number of iterations needed exceeds max_iterations an exception
(ValueError) will be raised. The default is 100.

References

(1)
@book{walters91categories,
    title={Categories and Computer Science},
    author={R. F. C. Walters},
    publisher={Cambridge University Press},
    location={Cambridge},
    year=1991}


(2)
@book{grimaldi94discrete,
author="Ralph P. Grimaldi".
title="Discrete and Combinatorial Mathematics: An Applied Introduction",
publisher="Addison-Wesley",
location="Readin, Massachusetts",
year=1994
}


"""

class KnuthBendix:
    def __init__(self, E, delim = '', max_iterations = 100):
	self.reductions = []
	self.delim = delim
	for a, b in E:
	    if delim:
		a = self.wrap_delim(a)
		b = self.wrap_delim(b)
	    if self.gt(b, a):
		a, b = b, a
	    self.reductions.append((a, b))
	self.make_confluent(max_iterations)
	self.sort()

    def __call__(self, x, y):
	return self.reduce(x) == self.reduce(y)

    def gt(self, a, b):
	delim = self.delim
	if delim:
	    la = len(a)
	    lb = len(b)
	else:
	    la = a.count(delim)
	    lb = b.count(delim)
	if la > lb:
	    return 1
	if la < lb:
	    return 0
	return a > b

    def make_confluent(self, max_iterations):
	def add_reduction(p, q):
	    if p != q:
		#pdb.set_trace()
		if self.gt(p, q):
		    self.reductions.append((p, q))
		else:
		    self.reductions.append((q, p))
		self.confluent = 0
	    
	reds_tested = {}
	for i in range(max_iterations):
	    #print 'iter', i
	    self.confluent = 1
	    reds = list(self.reductions)
	    for u1, v1 in reds:
		for u2, v2 in reds:
		    red = (u1, u2, u2, v2)
		    if red in reds_tested:
			continue
		    reds_tested[red] = 1
		    if u2 in u1:
			p = self.freduce(v1)
			i = u1.index(u2)
			while i >= 0:
			    uuu = u1[:i]+v2+u1[i+len(u2):]
			    q = self.freduce(uuu)
			    add_reduction(p, q)
			    i = u1.find(u2, i+1)
			    
			if 0:
			    uuu = u1.replace(u2, v2)
			    q = self.freduce(uuu)
			    add_reduction(p, q)
		    lu1 = len(u1)
		    for i in range(1, lu1-len(self.delim)):
			if u2[:lu1-i] == u1[i:]:
			    p = self.freduce(v1 + u2[lu1-i:])
			    q = self.freduce(u1[:i] + v2)
			    add_reduction(p, q)

	    assert ('', '') not in reds
	    # Remove redundant reductions
	    newr = []
	    nullred = (self.delim, self.delim)
	    for i, uv in enumerate(self.reductions):
		u, v = uv
		self.reductions[i] = nullred
		ru = self.freduce(u)
		rv = self.freduce(v)
		if ru != v and ru != rv:
		    urv = (u, rv)
		    newr.append(urv)
		    self.reductions[i] = urv
		else:
		    pass
		    #pdb.set_trace()
	    if len(newr) != self.reductions:
		assert ('', '') not in newr
		self.reductions = newr
	    assert ('', '') not in self.reductions
	    #assert ('', '') not in reds
	    if self.confluent:
		break



	else:
	    raise ValueError, """\
KnuthBendix.make_confluent did not terminate in %d iterations.
Check your equations or specify an higher max_iterations value.'
"""%max_iterations
	#print len(reds_tested)
	
	
    def freduce(self, p):
	# This (internal) variant of reduce:
	# Uses the internal representaion:
	# Assumes p is .surrounded. by the delimiter
	# and returns the reduced value .surrounded. by it.
	# This is primarily for internal use by make_confluent

	while 1:
	    q = p
	    for uv in self.reductions:
		p = p.replace(*uv)
	    if q == p:
		break
	return p

    def reduce(self, p):
	# This (external) variant of reduce:
	# will add delim if not .surrounded. by delim
	# but the return value will not be surrounded by it.

	if self.delim:
	    p = self.wrap_delim(p)
	p = self.freduce(p)
	if self.delim:
	    p = p.strip(self.delim)
	return p
    
    def sort(self, reds = None):
	if reds is None:
	    reds = self.reductions
	def cmp((x, _), (y, __)):
	    if self.gt(x, y):
		return 1
	    if x == y:
		return 0
	    return -1
	reds.sort(cmp)

    def pp(self):
	printreds(self.reductions)

    def wrap_delim(self, p):
	if not p.startswith(self.delim):
	    p = self.delim + p
	if not p.endswith(self.delim):
	    p = p + self.delim
	return p
	
def printreds(reds):
    for i, uv in enumerate(reds):
	print '%s\t'%(uv,),
	if (i + 1) % 4 == 0:
	    print
    if (i + 1) % 4 != 0:
	print
	

def kb(E, *a, **k):
    return KnuthBendix(E, *a, **k)



class _GLUECLAMP_:
    pass





def test2():
    #
    # The group of complex numbers {1, -1, i, -i} under multiplication;
    # generators and table from Example 16.13 in (2).

    G = ['1', '-1', 'i', '-i']
    E = [('1.i',	 'i'),
	 ('i.i',	 '-1'),
	 ('i.i.i',	 '-i'),
	 ('i.i.i.i',	 '1'),
	 ]
    R = kb(E, delim='.')
    T = [['.']+G] + [[y]+[R.reduce('%s.%s'%(y, x)) for x in G] for y in G]

    assert T == [
	['.', '1', '-1', 'i', '-i'],
	['1', '1', '-1', 'i', '-i'],
	['-1', '-1', '1', '-i', 'i'],
	['i', 'i', '-i', '-1', '1'],
	['-i', '-i', 'i', '1', '-1']]

    return R

def test():
    E = [('.a.', '.b.')]
    a = kb(E,delim='.')
    assert a('.a.', '.b.')
    E = [('fhk', 'gh'), ('m', 'kkm')]
    a = kb(E)
    p = a.reduce('fffghkkkm')
    q = a.reduce('ffghkm')
    assert p == 'ffffhm'
    assert q == 'fffhm'
    assert not a(p, q)

    E = [('.a.', '.b.')]
    a = kb(E, delim='.')
    p = a.reduce('aa')
    assert p == 'aa'
    p = a.reduce('.bb.')
    assert p == 'bb'
    p = a.reduce('b')
    assert p == 'a'

    E = [('.f.h.k.', '.g.h.'), ('.m.', '.k.k.m.')]
    a = kb(E, delim='.')
    p = a.reduce('.f.f.f.g.h.k.k.k.m.')
    q = a.reduce('.f.f.g.h.k.m.')
    assert p, q == ('.f.f.f.f.h.m.', '.f.f.f.h.m.')
    assert p == 'f.f.f.f.h.m'
    assert q == 'f.f.f.h.m'

    E = [('.f.ff.fff.', '.ffff.ff.'), ('.fffff.', '.fff.fff.fffff.')]

    a = kb(E, delim='.')

    p = a.reduce('.f.f.f.ffff.ff.fff.fff.fff.fffff.')
    q = a.reduce('.f.f.ffff.ff.fff.fffff.')

    #print p, q
    assert p == 'f.f.f.f.ff.fffff'
    assert q == 'f.f.f.ff.fffff'


def test3():
    # From 9.3 in 251
    E = [('Hcc', 'H'),
	 ('aab','ba'),
	 ('aac','ca'),
	 ('cccb','abc'),
	 ('caca','b')]

    a = kb(E)

    canon = [
	('Hb','Ha'),	('Haa','Ha'),	('Hab','Ha'),	('Hca','Hac'),
	('Hcb','Hac'),	('Hcc','H'),	('aab','ba'),	('aac','ca'),
	('abb','bb'),	('abc','cb'),	('acb','cb'),	('baa','ba'),
	('bab','bb'),	('bac','cb'),	('bba','bb'),	('bca','cb'),
	('bcb','bbc'),	('cab','cb'),	('cba','cb'),	('cbb','bbc'),
	('cbc','bb'),	('ccb','bb'),	('Haca','Hac'),	('Hacc','Ha'),
	('bbbb','bb'),	('bbbc','cb'),	('bbcc','bbb'),	('bcca','bb'),
	('caca','b'),	('ccaa','ba'),	('ccca','cb'),	('cacca','cb')
	]

    a.canon = canon

    if 0:
	for uv in canon:
	    if not uv in a.reductions:
		print uv

    return a

