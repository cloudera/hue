# Tests for nybitset

# Note: uses assert statements for brevity,
# so wouldn't check so much with python -O.

import gc, random, sys
try:
    import numpy.random
except ImportError:
    has_numpy = 0
else:
    has_numpy = 1

if has_numpy:
    def random_integers_list(low, high, length):
        return map(int, numpy.random.random_integers(low, high, [length]))
else:
    def random_integers_list(low, high, length):
        return [random.randint(low, high) for i in range(length)]

from time import clock
import cPickle
import pickle

from guppy.sets import *
Empty = immbitset()
Omega = ~Empty
bitsmut = mutbitset
bitset = immbitset
bitrange = immbitrange
bitsingle = immbit

def absorption(a, b):
    assert a & (a | b) == a
    assert a | (a & b) == a

def associative(a, b, c):
    assert (a & b) & c == a & (b & c)
    assert (a | b) | c == a | (b | c)

def commutative(a, b):
    assert a & b == b & a
    assert a | b == b | a

def deMorgan(a, b, c=None):
    if c is None:
	assert ~(a & b) == ~a | ~b
	assert ~(a | b) == ~a & ~b
    else:
	assert c - (a & b) == (c - a) | (c - b)
	assert c - (a | b) == (c - a) & (c - b)

def idempotence(a):
    assert a & a == a
    assert a | a == a

def inclusion(a, b):
    assert a & b <= a
    assert a & b <= b
    assert a | b >= a
    assert a | b >= b


def distributive(a, b, c):
    assert a | (b & c) == (a | b) & (a | c)
    assert a & (b | c) == (a & b) | (a & c)
    assert (a & b) | (b & c) | (c & a) == (a | b) & (b | c) & (c | a)
    assert not (a & b == a & c and a | b == a | c) or (b == c)
    
def test_set_operations(as_, bs, cs):
    for a in as_:
	idempotence(a)
	for b in bs:
	    inclusion(a, b)
	    commutative(a, b)
	    absorption(a, b)
	    for c in cs:
		associative(a, b, c)
		distributive(a, b, c)
		deMorgan(a, b, c)

def test_set_sub(as_, bs):
    def imp(a, b):
	assert not a or b
    for a in as_:
	for b in bs:
	    imp(len(a) != len(b), a != b)
	    imp(a < b, b > a and (not b < a))
	    imp(a <= b, b >= a and (a < b or a == b) and not a > b)
	    imp(a == b, a <= b and a >= b and not a != b and not b != a)
	    imp(a != b, not a == b and not b == a)
	    imp(a > b, b < a and not b > a)
	    imp(a >= b, b <= a and (b < a or a == b) and not a < b)


def test_set_len(as_, bs):
    # If a set can provide a len(), it should be convertible to a list
    for a in as_:
	assert len(a) == len(list(a))
	assert len(a&a) == len(a)
	assert len(a|a) == len(a)
	for b in bs:

	    # Test len of binary ops

	    assert len(a | b) == len(list(a | b))
	    assert len(a & b) == len(list(a & b))
	    assert len(a - b) == len(list(a - b))
	    assert len(a ^ b) == len(list(a ^ b))

def test_set_convert(as_, bs):
    for a in as_:
	for b in bs:
	    # Conversions

	    assert a | list(b) == a | b
	    assert a - tuple(b) == a - b
	    assert a & list(b) == a & b
	    assert a ^ tuple(b) == a ^ b


def eltime(f, args=(), N=1, retx=0):
    r = range(N)
    starttime = clock()
    for i in r:
	x = f(*args)
    endtime = clock()
    elapsed = endtime - starttime
    if retx:
	return elapsed, x
    else:
	return elapsed
	
'.nython on'

class IdSet(bitsmut):
    def append(self, x):
	bitsmut.append(self, id(x) // 12)

    def remove(self, x):
	bitsmut.remove(self, id(x) // 12)

    def __contains__(self, x):
	return bitsmut.__contains__(self, id(x) // 12)

'.nython off'


def add(a, b):
    c = b
    while c:
	a, c = a ^ c, (a & c) << 1
	print a,c
    return a


def randint(lim=1l<<30):
    # Return a random signed int
    return long(random.randrange(-lim, lim))
def randlong():
    a = randint()
    b = randint()
    ash = randint() & 255l
    c = randint()
    d = randint()
    bsh = randint() & 255l
    r = (a * b << ash) +  (c * d << bsh)
    return r


def dictset(l):
    ds = {}
    for e in l:
	if e not in ds:
	    ds[e] = 1
    return ds
    
def dslist(l):
    ds = dictset(l)
    ks = ds.keys()
    ks.sort()
    return ks


def randlist(n, amp):
    ' randlist(n, amp) -> list of n unique random ints in [-amp,amp]'
    ds={}
    rng = [] # To become a non-sorted list of unique random ints
    for i in range(10000):
	while 1:
	    b = randint(50000)
	    if b not in ds:
		rng.append(b)
		ds[b] = 1
		break
    return rng


'.nython on'

def t_append(a, b) :
    ap = a.append
    for bit in b:
	ap(bit)

def t_append_id(a, b) :
    ap = a.append
    for bit in b:
	ap(id(bit) // 12)


'.nython off'

class Test:
    faster = 1	# Set to 1 if test should be faster (less exhaustive) than normally

    def test0(self):
	pass

    def test1(self):
	import StringIO
	f = StringIO.StringIO()

	bitset([1,3,4]) | []
	bitset([1,3,4]) & []
	#bitset([1,3,4]) | {}
	# bitset([1,3,4]) & {}
	bitset([1,3,4]) | [5]
	bitset([1,3,4]) | range(100)
	bitset([1,3,4]) | range(100,-1,-1)

	empties = (
	    bitset(),
	    bitset([]),
	    bitset(()),
	    bitset(0),
	    bitset(0l),
	    bitset(bitset())
	    )
	print >>f, empties
	for e in empties:
	    assert e is Empty
	
	bitset(0x1l<<30)
	bitset(0x1l<<32)

	print >>f,bitset(0x8000)
	print >>f,bitset((4,))
	print >>f,~bitset(0x8000)
	print >>f,bitset([1]) | bitset(3)
	print >>f,long(bitset([1]))
	print >>f,int(bitset([1]))

	ms = bitset(0).mutcopy()
	msa = ms
	ms |= 1
	print >>f,list(ms)
	ms |= 0x4000l
	print >>f,list(ms)
	ms |= [3, 4]
	print >>f,list(ms)
	ms |= (6, 8)
	print >>f,list(ms)
	ms |= bitset([7])
	print >>f,list(ms), ms
	ms |= bitset([37])
	ts = bitset(ms)
	print >>f,ts
	ms &= ts
	print >>f,ms

	ms &= 1
	print >>f,ms
	ms |= ts
	ms &= 0x4000l
	print >>f,list(ms)
	ms |= ts
	ms &= [3, 4]
	print >>f,list(ms)
	ms |= ts
	ms &= (6, 8)
	print >>f,list(ms)
	ms |= ts
	ms &= bitset([7])
	print >>f,ms

	ms |= ts
	ms &= ~bitset([6])
	print >>f,ms, 'ts&.', ts &~bitset([6])

	ms ^= 1
	print >>f,ms
	ms ^= 0x4000l
	print >>f,list(ms)
	ms ^= [3, 4]
	print >>f,list(ms)
	ms ^= (6, 8)
	print >>f,list(ms)
	ms ^= bitset([7])

	print >>f,ms

	ms &= 0
	ms |= ts

	ms |= ~ts
	print >>f,ms, 'mt',ms |~ ts, ts |~ts, ~bitset([]) |~ts

	xs = bitset(ms)

	ms |= 1
	print >>f,ms, xs | 1, long(xs), int(xs)

	ms ^= ms
	print >>f,ms

	ms &= ~ms
	print >>f,ms, long(ms), int(ms)

	ms |= -1
	print >>f,ms, long(ms)
	ms &= -2
	print >>f,ms, long(ms)
	ms ^= -4
	print >>f,ms, long(ms)

	ms |= -1l
	print >>f,ms, long(ms)
	ms &= -2l
	print >>f,ms, long(ms)
	ms ^= -4l
	print >>f,ms, long(ms)

	ms |= bitset(-1)
	print >>f,ms, long(ms)
	ms &= bitset(-2)
	print >>f,ms, long(ms)


	assert ms is msa


	print >>f,bitset(-1)
	print >>f,bitset([-1])
	print >>f,bitset([-1]) | bitset([4])
	#print >>f,long(bitset([-1]))

        # LP: #770882
        if sys.hexversion < 0x2070000:
            assert f.getvalue() == """\
(ImmBitSet([]), ImmBitSet([]), ImmBitSet([]), ImmBitSet([]), ImmBitSet([]), ImmBitSet([]))
ImmBitSet([15])
ImmBitSet([4])
(~ImmBitSet([15]))
ImmBitSet([0, 1])
2
2
[0]
[0, 14]
[0, 3, 4, 14]
[0, 3, 4, 6, 8, 14]
[0, 3, 4, 6, 7, 8, 14] MutBitSet([0, 3, 4, 6, 7, 8, 14])
ImmBitSet([0, 3, 4, 6, 7, 8, 14, 37])
MutBitSet([0, 3, 4, 6, 7, 8, 14, 37])
MutBitSet([0])
[14]
[3, 4]
[6, 8]
MutBitSet([7])
MutBitSet([0, 3, 4, 7, 8, 14, 37]) ts&. ImmBitSet([0, 3, 4, 7, 8, 14, 37])
MutBitSet([3, 4, 7, 8, 14, 37])
[3, 4, 7, 8, 37]
[7, 8, 37]
[6, 7, 37]
MutBitSet([6, 37])
MutBitSet(~ImmBitSet([])) mt (~ImmBitSet([])) (~ImmBitSet([])) (~ImmBitSet([]))
MutBitSet(~ImmBitSet([])) (~ImmBitSet([])) -1 -1
MutBitSet([])
MutBitSet([]) 0 0
MutBitSet(~ImmBitSet([])) -1
MutBitSet(~ImmBitSet([0])) -2
MutBitSet([1]) 2
MutBitSet(~ImmBitSet([])) -1
MutBitSet(~ImmBitSet([0])) -2
MutBitSet([1]) 2
MutBitSet(~ImmBitSet([])) -1
MutBitSet(~ImmBitSet([0])) -2
(~ImmBitSet([]))
ImmBitSet([-1])
ImmBitSet([-1, 4])
"""
    def test2(self):
	# Test standard operators (not-inplace)
	for a in [randlong() for i in range(10)]:
	    for b in [randlong() for j in range(10)]:
		ts = []
		for ta in (a, bitset(a), bitsmut(a)):
		    for tb in (b, bitset(b), bitsmut(b)):
			tr = []
			tr.append(ta | tb)
			tr.append(ta & tb)
			tr.append(ta ^ tb)

			tr.append(ta | ~tb)
			tr.append(ta & ~tb)
			tr.append(ta ^ ~tb)

			tr.append(~ta | tb)
			tr.append(~ta & tb)
			tr.append(~ta ^ tb)

			tr.append(~ta | ~tb)
			tr.append(~ta & ~tb)
			tr.append(~ta ^ ~tb)
			ts.append(tr)

                # LP: #770882
                if sys.hexversion >= 0x2070000:
                    continue
		for tr in ts[1:]:
		    for r, x in zip(tr, ts[0]):
			assert long(r) == x

    def test3(self):
	# Test in-place operators
	p = randlong()
	op = randint()
	a = randlong()
	b = randlong()
	ts = []
	for tp in (p, bitset(p), bitsmut(p)):
	    for ta in (a, bitset(a), bitsmut(a)):
		if op & 1:
		    ta |= tp
		elif op & 2:
		    ta &= tp
		elif op & 4:
		    ta ^= tp
		for tb in (b, bitset(b), bitsmut(b)):
		    tr = []
		    tb |= ta
		    tr.append(long(tb))
		    tb &= ta
		    tr.append(long(tb))
		    tb ^= ta
		    tr.append(long(tb))

		    tb |= ~ta
		    tr.append(long(tb))
		    tb &= ~ta
		    tr.append(long(tb))
		    tb ^= ~ta
		    tr.append(long(tb))
		    ts.append(tr)

        # LP: #770882
        if sys.hexversion >= 0x2070000:
            return
	for tr in ts[1:]:
	    #print tr
	    for r, x in zip(tr, ts[0]):
		assert long(r) == x

    def test4(self):
	# Some performance test
	def f1(n, x, y):
	    while n > 0:
		x |= y
		x |= y
		x |= y
		x |= y
		x |= y
		n -= 1
	
	x = 0l
	for exp in range(0,1024*32,16*32*(1+self.faster*31)):
	    y = 1l<<exp
	    print exp, eltime(f1, (1000, x, y)), \
		  eltime(f1, (1000, bitset(x), y)), \
		  eltime(f1, (1000, bitset(x), bitset(y))), \
		  eltime(f1, (1000, bitsmut(x), y)), \
		  eltime(f1, (1000, bitsmut(x), bitsmut(y))), \
		  eltime(f1, (1000, bitsmut(x), bitset(y)))
			   

    def test5(self):
	# Bitset from sequences in different ways

	bits = {}
	for i in range(50):
	    bit = randint()
	    bits[bit] = 1
	    bits[bit+randint()%15]=1
	    bits[bit+randint()%15]=1
	    bits[bit-randint()%15]=1
	    bits[bit-randint()%15]=1
	bits = list(bits)
	sbits = list(bits)
	sbits.sort()

	def dictset(bits):
	    return dict([(bit, 1) for bit in bits])

	seqs = [bits, tuple(bits), dictset(bits)]
	for seq in seqs:
	    assert list(bitset(seq)) == sbits 

	    bs = Empty
	    bs = bs | seq
	    assert list(bs) == sbits 
	    bs = Empty
	    bs = seq | bs
	    assert list(bs) == sbits 
	    bs = Empty
	    bs |= seq
	    assert list(bs) == sbits 
	    bs = bitsmut(Empty)
	    bs |= seq
	    assert list(bs) == sbits 


	    bs = Empty
	    bs = bs ^ seq
	    assert list(bs) == sbits 
	    bs = Empty
	    bs = seq ^ bs
	    assert list(bs) == sbits 
	    bs = Empty
	    bs ^= seq
	    assert list(bs) == sbits 
	    bs = bitsmut(Empty)
	    bs ^= seq
	    assert list(bs) == sbits 

	    bs = Omega
	    bs = bs & seq
	    assert list(bs) == sbits 
	    bs = Omega
	    bs = seq & bs
	    assert list(bs) == sbits 
	    bs = Omega
	    bs &= seq
	    assert list(bs) == sbits 
	    bs = bitsmut(Omega)
	    bs &= seq
	    assert list(bs) == sbits 

	    bs = Omega
	    bs = bs ^ seq
	    bs = ~bs
	    assert list(bs) == sbits 
	    bs = Omega
	    bs = seq ^ bs
	    bs = ~bs
	    assert list(bs) == sbits 
	    bs = Omega
	    bs ^= seq
	    bs = ~bs
	    assert list(bs) == sbits 
	    bs = bitsmut(Omega)
	    bs ^= seq
	    bs = ~bs
	    assert list(bs) == sbits 

    def test6(self):
	# Comparisons
        # LP: #770882
        if sys.hexversion >= 0x2070000:
            return
	for a in (randlong(),):
	    for b in (a, ~a, randlong()):
		assert ((bitset(a) == bitset(b)) == (a == b))
		assert ((bitset(a) != bitset(b)) == (a != b))
		assert ((bitset(a) == ~bitset(b)) == (a == ~b))
		assert ((bitset(a) != ~bitset(b)) == (a != ~b))
		assert ((~bitset(a) == bitset(b)) == (~a == b))
		assert ((~bitset(a) != bitset(b)) == (~a != b))
		assert ((~bitset(a) == ~bitset(b)) == (~a == ~b))
		assert ((~bitset(a) != ~bitset(b)) == (~a != ~b))

		assert ((bitsmut(a) == bitsmut(b)) == (a == b))
		assert ((bitsmut(a) != bitsmut(b)) == (a != b))

		assert ((bitsmut(a) == bitset(b)) == (a == b))
		assert ((bitsmut(a) != bitset(b)) == (a != b))

		assert ((bitset(a) == bitsmut(b)) == (a == b))
		assert ((bitset(a) != bitsmut(b)) == (a != b))



    def test7(self):
	# Bitsmut gymnastics
	import StringIO
	f = StringIO.StringIO()

	a=bitsmut(0)
	print >>f,a
	a.append(1)
	print >>f,a, a.pop(), a
	a.append(1)
	print >>f,a, a.pop(-1), a
	a.append(1)
	print >>f,a, a.pop(0), a
	a.append(1)
	a.append(2)
	a.append(3)
	print >>f,a, a.pop(), a
	print >>f,a, a.pop(0), a
	a.remove(2)
	print >>f,a

	assert f.getvalue()=="""\
MutBitSet([])
MutBitSet([1]) 1 MutBitSet([])
MutBitSet([1]) 1 MutBitSet([])
MutBitSet([1]) 1 MutBitSet([])
MutBitSet([1, 2, 3]) 3 MutBitSet([1, 2])
MutBitSet([1, 2]) 1 MutBitSet([2])
MutBitSet([])
"""

	def f(a, b) :
	    ap = a.append
	    for bit in b:
		ap(bit)


	def flu(a, b):
	    s = 0
	    for bit in b:
		if bit in a:
		    s += 1
	    return s

	def g(a, b):
	    for bit in b:
		a[bit] = 1

	
	def h(a, b):
	    for bit in b:
		a |= bitsingle(bit)

	
	def tms(rng, f=f):
	    ms = bitsmut(0)
	    t = eltime(f, (ms, rng))
	    srng = list(rng)
	    srng.sort()
	    assert ms == bitset(srng)
	    return t
	    
	def tmslu(rng, n = None):
	    if n is None:
		n = len(rng)
	    ms = bitsmut(rng[:n])
	    elt, s = eltime(flu, (ms, rng), retx=1)
	    assert s == n
	    return elt
	    

	def tbslu(rng, n = None):
	    if n is None:
		n = len(rng)
	    ms = bitset(rng[:n])
	    elt, s = eltime(flu, (ms, rng), retx=1)
	    assert s == n
	    return elt
	    

	def tlo(rng):
	    lo = 0l
	    def f(a, b):
		for bit in b:
		    a |= 1l<<b
	    return eltime(h, (lo, rng))

	def tbs(rng):
	    lo = bitset()
	    def f(a, b):
		for bit in b:
		    a |= bitsingle(b)
	    return eltime(h, (lo, rng))

	def tls(rng):
	    ls = []
	    return eltime(f, (ls, rng))

	def tds(rng):
	    ds = {}
	    return eltime(g, (ds, rng))

	def tdslu(rng, n = None):
	    if n is None:
		n = len(rng)
	    ds = dict([(x, 1) for x in rng[:n]])
	    elt, s = eltime(flu, (ds, rng), retx=1)
	    assert s == n
	    return elt


	step = (1 + self.faster*5)

	for rng in ( range(0, 10000, step),
		     range(0, 100000, step),
		     range(10000,-1,-1*step),
		     randlist(10000, 50000-self.faster*40000)):
	    print tms(rng), tds(rng), tls(rng), tms(rng, h), \
		  tmslu(rng), tbslu(rng), tdslu(rng), \
		  tmslu(rng, 100), tbslu(rng, 100), tdslu(rng, 100)



	rng = range(10000)
	print tlo(rng), tbs(rng)


    def test8(self):
	# Subclassing a bitsmut
	BS = IdSet
	for bs in ( BS(), BS([]), BS([0])):
	    os = ((), [], {})
	    for o in os:
		bs.append(o)
	    for o in os:
		assert o in bs
	    for o in os:
		bs.remove(o)
	    for o in os:
		assert o not in bs

	try:
	    from snidioms import ListLikeDictSet
	except ImportError:
	    print 'can not import snidioms, skipping a performance comparison'
	else:
	    rng = range(10000)
	    for s in [], BS(), ListLikeDictSet():
		print eltime(t_append, (s, rng))

	    for s in [], bitsmut([]),:
		print eltime(t_append_id, (s, rng))

    def test9(self):
	# Making bigger bitsmuts - testing the split
	for i in (1000, 10000, 100000):
	    r = range(i)
	    m = bitsmut(r)
	    assert list(m) == r

	    la=random_integers_list(-i,i,i)
	    m = bitsmut(la)
	    las=dslist(la)
	    bs=bitset(m)
	    assert list(bs) == las


    def test10(self):

	# Performance test 

	def tests(la):
	    for i in (1000, 10000, 100000, 400000):
		print 'eltime(bitset, (la[:%d],))'%i
		print eltime(bitset, (la[:i],))
	la = range(400000)
	print  'la = range(400000)'
	tests(la)
	la.reverse()
	print  'la.reverse()'
	tests(la)
	la=random_integers_list(-400000,400000,400000)
	print 'la=random_integers_list(-400000,400000,400000))'
	tests(la)

    def test11(self, n=1):
	# A specific bug showed when setting splitting_size
	la=random_integers_list(-400000,400000,400000)
	while n > 0:
	    ms=bitsmut([])
	    ms._splitting_size=100
	    ms |= la
	    print 'test11', n, ms._indisize, ms._num_seg
	    n -= 1
	
    def test12(self):
	# append should be able to reuse space that was pop()'d
	# even for other bit ranges
	# Due to allocation strategy, the size may differ an
	# initial round	but should then be stable.

	for N in (32, 64, 128, 256, 31, 33, 63, 65, 255, 257):
	    ms = bitsmut()

	    # Train it
	    rng = range(N)
	    ms |= rng
	    for popix in (-1, 0):
		for j in range(N):
		    ms.pop(popix)
		ms |= rng
	    # Now should be stable..
	    indisize = ms._indisize
	    for popix in (-1, 0):
		for i in range(0, N*10, N):
		    pops = []
		    for j in range(N):
			pops.append(ms.pop(popix))
		    assert list(ms) == []
		    if popix == -1:
			pops.reverse()
		    assert pops == rng
		    rng = range(i, i+N)
		    ms |= rng
		    assert indisize == ms._indisize
		    assert list(ms) == rng

    def test13(self):
	# append, remove for inverted bitsmuts, 
	# have inverted sense. 'nonzero' is always true.
	# (pop is not supported - it seems it conceptually should give infite range of bits)

	ms = bitsmut()
	assert not ms
	ms ^= ~0	# Make it inverted - contains 'all bits'
	assert ms
	ms.remove(0)
	assert ms
	assert list(~ms) == [0]
	try:
	    ms.remove(0)
	except ValueError:
	    pass
	else:
	    raise 'expected ValueError for remove'
	ms.append(0)
	assert list(~ms) == []
	try:
	    ms.append(0)
	except ValueError:
	    pass
	else:
	    raise 'expected ValueError for append'

	ms.remove(0)
	try:
	    ms.pop()
	except ValueError:
	    pass
	else:
	    raise 'expected ValueError for pop'

    def test14(self):
	# Test the bitrange() constructor
	xs = (-1000, -100, -33, -32, -31, -10, -1, 0, 1, 10, 31, 32, 33, 100, 1000)
	for lo in xs:
	    assert list(bitrange(lo)) == range(lo)
	    for hi in xs:
		assert list(bitrange(lo, hi)) == range(lo, hi)
		for step in (1, 2, 3, 4, 5, 6, 7, 31, 32, 33):
		    r = range(lo, hi, step)
		    assert list(bitrange(lo, hi, step)) == r
    
    def test15(self):
	# Test the indexing
	# Only index 0 or -1 is currently supported, for first or last bit -
	# the others would take more work and might appear surprisingly slow.

	for a in range(-33,34):
	    for b in range(a+1, a+35):
		rng = range(a, b)
		bs = bitrange(a, b)
		assert bs[0] == a
		assert bs[-1] == b-1
		ms = bitsmut(bs)
		assert ms[0] == a
		assert ms[-1] == b-1
		i = 0
		while ms:
		    x = ms[i]
		    assert x == ms.pop(i)
		    assert x == rng.pop(i)
		    i = -1 - i

    def test16(self):
	# Test shifting
	for sh in range(64):
	    for v in range(64):
		assert long(bitset(v) << sh) == long(v)<<sh

	maxint = sys.maxint
	minint = -maxint - 1

	b = bitset([0])

	for sh in (maxint, -maxint, minint):
	    assert b<<sh == bitset([sh])

	def tsv(bs, sh):
	    try:
		bs << sh
	    except OverflowError:
		pass
	    else:
		raise 'expected OverflowError'

	tsv(bitset([maxint]), 1)
	tsv(bitset([minint]), -1)
	tsv(bitset([-maxint])<<(-1), -1)

	for a, b in ((0, 10), (0, 10000), (-1000, 1000)):
	    for sh in (-257,-256,-255,-1,0,1,255,256,257):
		for step in (1, 2, 3):
		    assert bitrange(a, b, step)<<sh == bitrange(a+sh, b+sh, step)

    def test17(self):
	# Comparisons: inclusion tests

	for a in (0, 1, 2, range(31), range(32), range(33), randlong()):
	    for b in (0, 1, 2, range(31), range(32), range(33), randlong()):
		for as_ in ( bitset(a), ~bitset(a), bitsmut(a), bitsmut(~bitset(a))):
		    for bs in (as_, ~as_, bitset(b), ~bitset(b), bitsmut(b), bitsmut(~bitset(b))):
			t = as_ <= bs
			assert t == (bs >= as_)
			assert t == ((as_ & bs) == as_)
			assert t == ((long(as_) & long(bs)) == long(as_))
			
			t = as_ < bs
			assert t == (bs > as_)
			assert t == ((as_ <= bs) and (as_ != bs))
			assert t == ((as_ <= bs) and (long(as_) != long(bs)))


    def test18(self):
	# Testing internal consistency, with test values
	# that may not be practical to convert to longs.
	# Using Properties of Boolean algebras
	# (from 'Mathematichal Handbook'... tables p.30, p.15) 
	# Some tests should be quite redundant given others passed,
	# but are kept anyway for reference & doublechecking.

	any = [bitset(abs(randlong())) << randint(),
	       bitset(abs(randlong())) << randint(),
	       bitset(abs(randlong())) << randint() | bitset(abs(randlong())) << randint(),
	       bitset(abs(randlong())) << randint() | bitset(abs(randlong())) << randint(),
	       ]

	any = [Empty, Omega, bitset([0]),
	       bitset(randlong()),
	       bitset(randlong())] + [a ^ randlong() for a in any]
	any = any + [bitsmut(a) for a in any]
	for a in any:
	    # Empty and Omega are the least and greatest elements
	    assert Empty <= a <= Omega
	    assert a & Empty == Empty
	    assert a | Omega == Omega
	    # Identity elements for & and |
	    assert a & Omega == a
	    assert a | Empty == a
	    # Complement laws
	    assert a & ~a == Empty
	    assert a | ~a == Omega
	    assert ~Empty == Omega
	    assert ~Omega == Empty
	    assert ~(~a) == a

	    idempotence(a)
	    for b in any:
		# Relative complement, definition
		assert a & ~b == a - b
		# ...
		absorption(a, b)
		commutative(a, b)
		deMorgan(a, b)
		inclusion(a, b)
		for c in any:
		    associative(a, b, c)
		    distributive(a, b, c)

		# ...
		assert ((a <= b) == (a & b == a) == (a | b == b) ==
			(a & ~b == Empty) == (~b <= ~a) == (~a | b == Omega))
		
		# Symmetric difference
		# From p. 15
		assert a ^ b == b ^ a
		for c in any:
		    assert (a ^ b) ^ c == a ^ (b ^ c)
		    deMorgan(a, b, c)
		assert a ^ Empty == a
		assert a ^ a == Empty
		assert a ^ b == (a & ~b) | (b & ~a)
		
    def test19(self):
	# Finding prime numbers using the Sieve of Eratosthenes
	# - an excercise for eg bitrange().

	N = 4000

	primes = ([2] | bitrange(3, N, 2)).mutcopy()
	for i in bitrange(3, N // 2, 2):
	    primes &= ~bitrange(2 * i, N, i)

	# print primes._indisize, primes._num_seg

	primes = list(primes)
	assert len(primes) == 550
	assert primes[:10] == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
	assert primes[399] == 2741
	assert primes[549] == 3989
	return primes


    def test20(self):
	# Some bitrange arguments used when debugging its optimized version.
	# Entered here, in case some wasn't covered by previous tests.
	maxint = sys.maxint
	minint = -maxint - 1
	for a in (
	    (32,),
	    (31,),
	    (33,),
	    (13,),
	    (1,33),
	    (1,33,2),
	    (1,63,2),
	    (0,64,32),
	    (0,64+17,32),
	    (0,32*3,32),
	    (0,32*3+1,32),
	    (0,32*4,32),
	    (0,32*4,16),
	    (0,32*2,16),
	    (0,32*3,16),
	    (maxint-32,maxint),
	    (maxint-32,maxint, 2),
	    (maxint-32,maxint, 4),
	    (maxint-32,maxint, 16),
	    (maxint-32,maxint, 20),
	    (maxint-320,maxint),
	    (maxint-320,maxint, 2),
	    (maxint-320,maxint, 4),
	    (maxint-320,maxint, 16),
	    (maxint-320,maxint, 20),
	    (-1,maxint, maxint),
	    (0,maxint, maxint),
	    (1,maxint, maxint),
	    (minint,maxint, maxint),
	    (minint,maxint, maxint/32),
	    (minint,maxint, maxint/320),
	    (minint,maxint, -(minint/32)),
	    (minint,maxint, -(minint/320)),
	    ):
	    br = bitrange(*a)
	    #print br
	    assert list(br) == range(*a)

	try:
	    bitrange(minint,maxint,1)
	except OverflowError:
	    pass
	else:
	    raise 'expected OverflowError'

	# a more exhaustive check,
	# it tests some > 70000 combinations if not self.faster
	if not self.faster:
	    print 'bitrange testing many combinations, this may take some time...'
	for a in range(0, 34, 1 + 8*self.faster):
	    print 'a', a, 
	    sys.stdout.flush()
	    for l in range(1000, 1034, 1 + 8*self.faster):
		for st in range(1, 34, 1 + 8*self.faster):
		    for arg in ((maxint - l, maxint - a, st),
				(minint + a, minint + l, st)):
			br = bitrange(*arg)
			assert list(br) == range(*arg)
	print 'done'

    def test21(self):
	# Test bitset as dict key - i.e. hashing, equality
	D = {}
	a = bitrange(1)
	b = bitrange(1)
	c = ~a
	d = ~b
	D[a] = 1
	D[c] = -1
	assert D[b] == D[a] == 1
	assert D[c] == D[d] == -1

    def test22(self):
	# Test pickling
	any = [bitset() for x in range(10)]
	any = any + [bitrange(x, y, z)
		     for x in (-1000, 0, 1000)
		     for y in (2000,)
		     for z in (1, 3, 300)]
	any = any + [~x for x in any]
	any = any + [bitsmut(x) for x in any]
	for a in any:
	    for p in pickle, cPickle:
		for bin in (0, 1):
		    da = p.dumps(a, bin)
		    #print len(da), len(bitset(a))
		    aa = p.loads(da)
		    assert aa == a
		    assert type(aa) is type(a)

    def test23(self):
	# bitset from general sequence with iterator
	# We already special-cased list, tuple & dict

	class T:
	    def __init__(self, data):
		self.data = data

	    def __iter__(self):
		return iter(self.data)

	l = range(10)
	t = T(l)
	b = bitset(t)
	assert list(b) == l

	bo100 = b | T([100])
	assert list(bo100) == l + [100]

	ms = bitsmut(t)
	assert ms == b

	ms |= T([100])
	assert ms == bo100

    def test24(self):
	# tests to do with the copy-on-write optimizations
	# this should show in improved timing for some operation sequences

	def f1(n):
	    return bitrange(n).mutcopy()[0]

	t, v = eltime(f1, (10000000,), retx=1)
	print t
	assert v == 0

	bs = bitrange(10000000)
	def f2(bs):
	    ms = bs.mutcopy()
	    ms &= ~1
	    return ms[0], bs[0]

	t, v = eltime(f2, (bs,), retx=1)
	print t
	assert v == (1, 0)

	ms = bs.mutcopy()
	
	# Test that a temporary immutable copy can be fast

	def f3(ms):
	    bs = bitset(ms)
	    return ms[0], bs[0],

	t, v = eltime(f3, (ms,), retx=1)
	print t
	assert v == (0, 0)

	def f4(ms):
	    bs = bitset(ms)
	    ms &= ~1
	    return ms[0], bs[0],

	def f4b(ms):
	    # make sure cur_field is cleared when bitset is made
	    ms |= 1
	    bs = bitset(ms)
	    ms ^= 1
	    return ms[0], bs[0],

	for f in (f4, f4b):
	    ms = bs.mutcopy()

	    t, v = eltime(f, (ms,), retx=1)
	    print t
	    assert v == (1, 0)


	ms = bs.mutcopy()

	# Test that a temporary mutable copy of a bitsmut can be fast

	def f5(ms):
	    mc = ms.mutcopy()
	    return mc[0], ms[0],

	t, v = eltime(f5, (ms,), retx=1)
	print t
	assert v == (0, 0)
	
	# Test that a temporary mutable copy of a bitsmut can be fast
	# and still be separately updated

	def f6(ms):
	    ms &= ~bitrange(15)
	    mc = ms.mutcopy()
	    mc |= [2]
	    ms |= [4]
	    return mc[0], ms[0],

	def f6a(ms):
	    # as f6 but updating in the other order - tried to induce a bug
	    ms &= ~bitrange(15)
	    mc = ms.mutcopy()
	    ms |= [4]
	    mc |= [2]
	    return mc[0], ms[0],

	def f6b(ms):
	    # working harder and managed to provoke test of a noticed copy-on-write
	    # requirement (cur_field had to be cleared when the set was borrowed)
	    ms &= ~bitrange(15)
	    ms |= [8]
	    mc = ms.mutcopy()
	    ms |= [1,4]
	    mc |= [2]
	    ms &= ~bitsingle(1)
	    return mc[0], ms[0],

	for f in (f6, f6a, f6b):
	    t, v = eltime(f, (ms,), retx=1)
	    print t
	    assert v == (2, 4)

	# Temporary mutable copy of splitted bitsmut

	for f in (f6, f6a, f6b):
	    bs = bitrange(100000) | bitrange(200000, 300000)
	    ms = bs.mutcopy()

	    ms |= bitsingle(150000)	# Force a split

	    assert ms._num_seg > 1
	    print 'num_seg', ms._num_seg

	    t, v = eltime(f, (ms,), retx=1)
	    print t
	    assert v == (2, 4)
	
    def test25(self):
	# Thing that came up
	# converting to int should fail here, not become negative.
	# (Assuming 'standard' 2-complement int representation)

	bs = bitset(long(sys.maxint)+1)
	try:
	    a = int(bs)
	except OverflowError:
	    pass
	else:
	    raise 'expected OverflowError'

	assert long(bs) == long(sys.maxint)+1

	# These border cases should pass
	assert int(bitset(sys.maxint)) == sys.maxint
	assert int(bitset(-sys.maxint - 1)) == - sys.maxint - 1
	

	if 0:
	    # This was added without implementing & testing
	    # I have not implemented it yet.
	    # It is possible but I don't need to right now. / Also Notes May 19 2005
	    # 

	    # Relation operation with iterable right argument,
	    # apparently not tested before. (Nov. 10 2004)

	    assert not immbitset([1,2,3]) <= [1,2]
	    assert not mutbitset([1,2,3]) <= [1,2]
	    assert not mutnodeset([1,2,3]) <= [1,2]
	    assert not immnodeset([1,2,3]) <= [1,2]
	    assert immbitset([1,2,3]) <= [1,2, 3]
	    assert mutbitset([1,2,3]) <= [1,2, 3]
	    assert immnodeset([1,2,3]) <= [1,2, 3]
	    assert mutnodeset([1,2,3]) <= [1,2, 3]
	    assert [1,2] <= immbitset([1,2,3])
	    assert [1,2] <= mutbitset([1,2,3])
	    assert [1,2] <= immnodeset([1,2,3])
	    assert [1,2] <= mutnodeset([1,2,3])
	    assert not [1,2,3] <= immbitset([1,2])
	    assert not [1,2,3] <= mutbitset([1,2])
	    assert not [1,2,3] <= immnodeset([1,2])
	    assert not [1,2,3] <= mutnodeset([1,2])


    def test26(self):
	# len() tests

	for thelen in [0, 15, 17, 31, 33, 1023, 1024, 1025, int(1e7)]:
	    for args in [(thelen,), (0,thelen * 3,3)]:
		bs = bitrange(*args)
		t, v = eltime(len, (bs,), retx=1)
		if t > 0.01:
		    print t, v
		assert v == thelen

		bs = bitsmut(bs)

		t, v = eltime(len, (bs,), retx=1)
		if t > 0.01:
		    print t, v
		assert v == thelen



    def test27(self):
	# slices
	for b in (bitset(64), bitrange(64), bitset(abs(randlong()))):
	    for st in (b, b.mutcopy()):
		for i in (1, 2, 3, 30, 31, 32, 33, 34, 63, 64, 65):
		    assert b[:i] == bitset(list(b)[:i])
		    assert b[-i:] == bitset(list(b)[-i:])

    def test28(self):
	# test & set; test & clr
	for s in (bitsmut(), bitsmut(~bitset() & ~bitset([14]))):
		  assert s.tas(14) == 0
		  assert s.tas(14) == 1
		  assert s.tac(14) == 1
		  assert s.tac(14) == 0


    def test29(self):
	# Compatibility functions added:
	# add, discard, -, -=
	# Also tests S.mutcopy() where S is mutable with 1 or 2 segments

	def t(p):
	    # print p._num_seg
	    q = p.mutcopy()
	    p.add(17)
	    assert p != q
	    q.append(17)
	    assert p == q

	    p.discard(-1)
	    assert p == q
	    p.discard(17)
	    assert p != q
	    q.remove(17)
	    assert p == q


	    r = p - q
	    assert r == bitsmut([])

	    
	ms  = bitsmut(12345)
	t(ms)

	bs = bitrange(20, 100000) | bitrange(200000, 300000)
	ms = bs.mutcopy()

	ms |= bitsingle(150000)	# Force a split
	assert ms._num_seg > 1
	
	t(ms)

	all = 0, -1, 1, -2, 2, randlong(), -randlong()
	all = [bitsmut(a) for a in all]
	all = all + [bitsmut(a) for a in all]
	for a in all:
	    a = a.mutcopy()
	    aa = a.mutcopy()
	    for b in all:
		a -= b
		aa &= ~b
		assert a == aa
		
    def test30(self):
	# Test nodeset

	nodeset = immnodeset
	ns = mutnodeset()
	ns0 = ns
	a = []
	b = ()
	c = {}
	d = 0
	e = ''
	
	# Test 5 ways to add elements

	ns.add(a)
	ns.append(b)
	ns |= nodeset([c])
	assert not ns.tas(d) 
	ns ^= [e]

	assert ns == nodeset([a,b,c,d,e])
	
	# Test 5 ways to remove elements

	ns ^= [e]
	assert ns == nodeset([a, b, c, d])
	assert ns.tac(d)
	assert ns == nodeset([a, b, c])
	ns -= nodeset([c])
	assert ns == nodeset([a, b])
	ns.remove(b)
	assert ns == nodeset([a])
	ns.discard(a)
	assert ns == nodeset([])

	# Test pop
	ns.add(a)
	assert ns.pop() is a
	try:
	    ns.pop()
	except ValueError:
	    pass
	else:
	    raise 'expected ValueError'

	assert ns0 is ns

	ns = immnodeset(ns)

	ns |= nodeset([a])
	assert ns == nodeset([a])
	assert ns is not ns0

	# ns is now immutable
	# this is like bitset
	# see note per Wed Jan 21 16:13:55 MET 2004
	# The change was made after that.

	ns1 = ns

	ns -= nodeset([a])

	# See note above. The following check
	# applies since mutability behaviour is as for bitset

	assert ns is not ns1

	assert ns == nodeset([])

	# Test clear

	ns = mutnodeset([1,2,3])
	assert len(ns) == 3
	ns.clear()
	assert len(ns) == 0
	assert list(ns) == []

    def test31(self):
	# Test nodeset, element-wise operations & object deallocation w. gc

	H = mutnodeset
	from sys import getrefcount as grc

	if 0:
	    print H.add.__doc__
	    print H.append.__doc__
	    print H.discard.__doc__
	    print H.remove.__doc__
	    print H.tas.__doc__
	    print H.tac.__doc__
	

	e1 = []
	e2 = []
	e3 = []
	r1 = grc(e1)
	r2 = grc(e2)
	r3 = grc(e3)

	s = H()
	s.add(e1)
	assert e1 in s
	assert e2 not in s
	s.append(e2)
	assert e2 in s
	assert s.tas(e3) == 0

	assert e3 in s

	assert r1 + 1 == grc(e1)
	assert r2 + 1 == grc(e2)
	assert r3 + 1 == grc(e3)

	assert s.tas(e3) == 1
	assert s.tac(e3) == 1
	assert s.tac(e3) == 0
	s.discard(e3)
	s.remove(e2)

	try:
	    s.append(e1)
	except ValueError:
	    pass
	else:
	    raise 'no exception from append'

	s.remove(e1)
    
	try:
	    s.remove(e1)
	except ValueError:
	    pass
	else:
	    raise 'no exception from remove'

	assert r1 == grc(e1)
	assert r2 == grc(e2)
	assert r3 == grc(e3)

	s.add(e1)
	s.add(e2)
	s.add(e3)

	s = None

	assert r1 == grc(e1)
	assert r2 == grc(e2)
	assert r3 == grc(e3)


	# Test gc support

	import gc

	s = H()
	s.append(e1)
	s.append(s)	# Make it cyclic
	assert s in s
	s = None
	gc.collect()
	#assert r1 == grc(e1)

	s = H()
	s.append(e1)
	s.append(e2)
	e2.append(s)	# Make it cyclic
	s = None
	e2 = None
	gc.collect()
	assert r1 == grc(e1)
	
    def test32(self):
	# Test extended NodeSet functionality

	H = immnodeset
	import gc
	from sys import getrefcount as grc

	gc.collect()
	e1 = []
	e2 = []
	e3 = []
	r1 = grc(e1)
	r2 = grc(e2)
	r3 = grc(e3)

	s = H([e1,e2])

	assert e1 in s and e2 in s and not e3 in s

	s3 = H([e1, e3])
	
	s |= s3
	assert e3 in s
	assert e2 in s
	s &= s3
	assert e2 not in s
	assert e1 in s 
	

	la = [], [e1], [e1, e2], [e1, e2, e3], [e2], [e2, e3], [e3], [e1,e3,e3,e1]

	ss = [H(x) for x in la]

	test_set_operations(ss, ss, ss)
	test_set_len(ss, ss)
	test_set_sub(ss, ss)
	test_set_convert(ss, ss)

	for a in ss:
	    for b in ss:
		

		# Not supported...yet..
		for x in (
		    'assert list(b) | a == a | b',
		    'assert list(b) & a == a & b',
		    ):
		    try:
			exec x
		    except TypeError:
			pass
		    else:
			raise Exception, 'Expected TypeError'
		

	ss = s=s3=la=a=b=c=x=None
	locals().clear()
	gc.collect()
	gc.collect()
	
	assert r1==grc(e1)
	assert r2==grc(e2)
	assert r3==grc(e3)

    def test33(self):
	# Test with multiple segments - so that code
	# in union_realloc is covered
	# I am unsure if any of the other tests used more segments than 2
	# It is a bit tricky (and implementation-dependent)
	# to make it make a specific number of segments.

	# The testing with 20 segments will make 3 reallocations:
	# to make place for 8, 16 and 24 segments.

	numseg = 20

	bs = bitset()

	for i in range(numseg):
	    bs |= bitrange(i*2*100000+20, (i*2+1)*100000)

	ms = bs.mutcopy()
	mss = []

	assert ms._num_seg == 1

	for i in range(numseg-1):
	    mss.append(ms.mutcopy())
	    ms |= bitsingle((i*2+1)*100000+50000)
	    assert ms._num_seg == i+2

	
	# Test that the copies were separate copies (Testing copy-on-write)

	for i in range(numseg-1):
	    assert mss[i] == bs
	    bs |= bitsingle((i*2+1)*100000+50000)


    def test34(self):
	# Test nodeset inheritance
	# This leaks in Python 2.3.3; whether or not H is MutNodeSet or list.
	H = MutNodeSet
	e1 = []

	class X(H):
	    def extend(self, y):
		for e in y:
		    self.append(e)


	s = X()
	assert e1 not in s
	s.extend([e1])
	assert e1 in s
	
    def test35(self):
	# Test bitset inheritance

	for i in range(2):
	    # An error didn't show until second time around


	    for H in ImmBitSet, MutBitSet:
		class X(H):
		    bitnames = ['red','green','blue']
		    def __new__(clas, *args):
			return H.__new__(clas, [clas.bitnames.index(x) for x in args])

		    def __iter__(self):
			for bit in H.__iter__(self):
			    yield self.bitnames[bit]

		    def __str__(self):
			return '{%s}'%(', '.join(self))

		    def __eq__(self, other):
			return str(self) == str(other)

		x = X()
		x = X('red','blue')
		assert list(x) == ['red', 'blue']

		# Test different kinds of construction args

		assert (H.__new__(X, )) == '{}'
		assert (H.__new__(X, immbitset(1))) == '{red}'
		assert (H.__new__(X, mutbitset(2))) == '{green}'
		assert (H.__new__(X, 3)) == '{red, green}'
		assert (H.__new__(X, 4l)) == '{blue}'

		if H is ImmBitSet:
		    x = X('red','blue')
		    import guppy.sets.setsc
		    # See that we can pass a subtype to CplBitSet
		    assert( str(guppy.sets.setsc.CplBitSet(x)) == "(~ImmBitSet(['red', 'blue']))" )
		

class MemStat:
    def __init__(self):
	self.nrefs = {}
	from guppy import Root
	self.R = R = Root()
	self.V = R.guppy.heapy.View
	self.P = R.guppy.heapy.Path
	self.xmemstats = R.guppy.heapy.heapyc.xmemstats
	#self.alset = R.guppy.heapy.heapyc.set_alset()

	#self.mark()

    def mark(self):
	self.R.gc.collect()
	h = self.V.horizon()
	h.update(gc.get_objects())
	self.h=h


    def dump(self):
	gc.collect()
	self.xmemstats()
	#print 'len alset', len(self.alset)

	V = self.V
	R = self.R
	P = self.P
	nrefs = self.nrefs
	if 0:
	    h = self.h

	    n = h.news(gc.get_objects())
	    print V.retset(n)
	    if len(n) <= 12:
		l = list(n)
		for i in range(len(n)):
		    V.enter(
			lambda : P.shpaths((), l[i]).pp())
	try:
	    co = sys.getcounts()
	except AttributeError:
	    pass
	else:
	    for (name, allo, free, max) in co:
		nref = allo - free
		if name not in nrefs or nref != nrefs[name]:
		    print >>sys.stderr, (name, nref),
		    nrefs[name] = nref
	    print >>sys.stderr
	h=self.h=n=co=name=allo=free=max=l=i=None
	#self.mark()
	#self.alset = None
	#R.guppy.heapy.heapyc.clr_alset()
	gc.collect()
	#self.alset = R.guppy.heapy.heapyc.set_alset()

def test_nums(numbers, dump=None):
    enufuncs = []
    for n in numbers:
	enufuncs.append((n, getattr(t, 'test%d'%n)))
    for n, f in enufuncs :
	print 'Test #%d'%n
	f()
	if dump is not None:
	    dump()

def test_leak():
    import gc
    # Test 34 is known to leak in Python 2.3.3.
    nums = range(36)
    nums.remove(34)
    ms = MemStat()
    if 0:
	clr_alset = ms.R.guppy.heapy.heapyc.clr_alset
	dump_alset = ms.R.guppy.heapy.heapyc.dump_alset
    #dump_alset()
    i = 0
    while 1:
	test_nums(nums, ms.dump)
	gc.collect()
	if 0 and i >= 2:
	    dump_alset();
	i += 1
	#ms.dump()

def test_main():
    test_nums(range(36))

t=Test()

if __name__ == '__main__':	    
    #test_leak()
    #t.test25()
    #t.test30()
    test_main()
    #test_nums(range(30, 36))
    #test_nums(range(13,35))

