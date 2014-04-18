from guppy.heapy.test import support
import StringIO, sys, types, unittest

class TestCase(support.TestCase):
    def setUp(self):
	support.TestCase.setUp(self)
	self.RefPat = self.heapy.RefPat
	self.iso = self.Use.iso

    def makegraph(self, width, length):
	# Generate a structure which will yield a high number
	# of shortest paths.
	# Returns a pair src, dst which are connected via a noncyclic graph
	# with many edges.
	# The length of each path (all shortest), number of edges will be length
	# The number of nodes will be 2 + width * (length - 1)
	# The number of paths will be
	#	width ** length, if width >= 1 and length >= 1

	dst = []
	ls = []
	for i in range(width):
	    ls.append([dst])
	ls = [dst] * width
	for i in range(length-1):
	    xs = []
	    for j in range(width):
		ys = []
		xs.append(ys)
		for k in range(width):
		    ys.append(ls[k])
	    ls = xs
	src = ls
	return src, dst

    def makegraph(self, width, length):
	# Generate a structure which will yield a high number
	# of shortest paths.
	# Returns a pair src, dst which are connected via a noncyclic graph
	# with many edges.
	# The length of each path (all shortest), number of edges will be length
	# The number of nodes will be 2 + width * (length - 1)
	# The number of paths will be
	#	width ** length, if width >= 1 and length >= 1

	dst = []
	ls = []
	for i in range(width):
	    ls.append([dst])
	ls = [dst] * width
	for i in range(length-1):
	    xs = []
	    for j in range(width):
		ys = []
		xs.append(ys)
		for k in range(width):
		    ys.append(ls[k])
	    ls = xs
	src = ls
	return src, dst

    def rp(self, dst, src, **kwds):
	iso = self.iso
	if src is not None:
	    src = iso(src)
	rp = iso(dst).get_rp(src=src, **kwds)
	rp.mod.UniSet.summary_str.str_address = lambda a: '<address>'
	return rp


class RefPatCase(TestCase):
    def test_basic_methods(self):
	# Test basic methods: iteration, indexing, length, tree addressing via attribute access

	# Test iteration

	dst = src = []
	lists = [dst]
	for i in range(5):
	    src = [src]
	    lists.append(src)
	    
	    
	rp = self.rp(dst, src,depth=10)
	for i, x in enumerate(rp):
	    if i < len(lists):
		self.asis(lists[i], x.theone)
	    

	# Test indexing

	# First case, when already iterated over

	self.asis( rp[0].theone, lists[0] )
	self.asis( rp[-2].theone, lists[-1])


	# Second case, when not iterated over before

	rp = self.rp(dst, src,depth=10)

	self.asis( rp[0].theone, lists[0] )
	self.asis( rp[-2].theone, lists[-1])

	# Test length

	self.aseq( len(rp), len(lists) + 1)
	rp = self.rp(dst, src,depth=10)
	self.aseq( len(rp), len(lists) + 1)

	# Test attribute access

	self.asis(rp._.theone, lists[0])
	self.asis(rp.a.theone, lists[1])

	# Test attribute access, when not iterated over before

	rp = self.rp(dst, src,depth=10)
	self.asis(rp.a2.theone, lists[2])
	self.asis(rp.a.theone, lists[1])

	# Make sure attribute access is cached:
	# so it doesn't change when struct is changed

	lists[2].append(lists[0])
	rp.View.clear_retainers()
	rp.View.update_referrers(self.iso(lists[0]))
	self.asis(rp.a.theone, lists[1])

	# Test with recursive structure

	dst = []
	dst.append(dst)
	src = [dst]
	rp = self.rp(dst, src)
	self.asis(rp._.theone, dst)
	self.aseq(rp.a, self.iso(dst, src))
	self.aseq(rp.a, rp.a2)
	self.aseq(rp.a, rp[1])

    def test_presentation(self):

	output = StringIO.StringIO()

	src = []

	def write(x):
	    print >>output, x

	R = self.RefPat
	def test_pp(dst, src, result=None, **kwds):

	    rp = self.rp(dst, src, **kwds)
	    write( repr(rp) )
	    return rp

	dst = []
	src.append(dst)
	#print R.refpat(dst=dst)

	test_pp(dst, src)

	for i in range(5):
	    x = dst
	    dst = []
	    x.append(dst)
	test_pp(dst, src)

	src, dst = self.makegraph(5,7)

	test_pp(dst, src, depth=10)

	# Test that pp() prints limited number of lines
	
	src, dst = self.makegraph(5,17)

	rp = test_pp(dst, src, depth=17)
	
	write( repr(rp.more) )

	# Test more of more

	src, dst = self.makegraph(1,30)

	rp = test_pp(dst, src, depth=35)

	m = rp.more

	write( repr(m) )
	write( repr(m.more) )
	m1 = m.more
	write( repr(m1) )
	m2 = m.more
	write( repr(m2.more) )
	write( str(m1.more) ) # Test also that str() is the same as repr()

	# Test that we get back to start by .top

	write( m1.top )

	# Test that we get back to previous by .prev

	write( m1.prev )

	if 0:
	    # I don't know if I really want this, after new general output handling
	
	    # Test that .top works at the top

	    write( m1.top.top )

	#pdb.set_trace()

	# Test that they won't say '...more lines...' if the # of lines is what is printed

	src, dst = self.makegraph(1,30)

	rp = test_pp(dst, src, depth=10)

	# Test how no more lines is printed

	write( rp.more)	
	write( rp.more.more)

	# Test that one more line is printed rather than '1 more line'

	src, dst = self.makegraph(1,30)

	rp = test_pp(dst, src, depth=21)
	write( rp.more)	

	# Test that we can do more without first printing

	rp = self.rp(dst, src, depth=20)
	
	write( rp.more )

	if 0:
	    print output.getvalue()
	else:
	    self.aseq(output.getvalue(), """\
Reference Pattern by <[dict of] class>.
 0: _ --- [-] 1 list: <address>*0
 1: a      [-] 1 list: <address>*1
 2: aa ---- [R] 1 tuple: <address>*1
Reference Pattern by <[dict of] class>.
 0: _ --- [-] 1 list: <address>*0
 1: a      [-] 1 list: <address>*1
 2: aa ---- [-] 1 list: <address>*1
 3: a3       [-] 1 list: <address>*1
 4: a4 ------ [-] 1 list: <address>*1
 5: a5         [-] 1 list: <address>*1
 6: a6 -------- [-] 1 list: <address>*1
 7: a7           [R] 1 tuple: <address>*1
Reference Pattern by <[dict of] class>.
 0: _ --- [-] 1 list: <address>*0
 1: a      [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 2: aa ---- [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 3: a3       [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 4: a4 ------ [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 5: a5         [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 6: a6 -------- [-] 5 list: <address>*5, <address>*5, <address>*5...
 7: a7           [-] 1 list: <address>*5
 8: a8 ---------- [R] 1 tuple: <address>*1
Reference Pattern by <[dict of] class>.
 0: _ --- [-] 1 list: <address>*0
 1: a      [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 2: aa ---- [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 3: a3       [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 4: a4 ------ [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 5: a5         [-] 5 list: <address>*5, <address>*5, <address>*5, <address>*5...
 6: a6 -------- [-] 5 list: <address>*5, <address>*5, <address>*5...
 7: a7           [-] 5 list: <address>*5, <address>*5, <address>*5...
 8: a8 ---------- [-] 5 list: <address>*5, <address>*5, <address>*5...
 9: a9             [-] 5 list: <address>*5, <address>*5, <address>*5...
<Type e.g. '_.more' for more.>
10: a10 ----------- [-] 5 list: <address>*5, <address>*5, <address>*5...
11: a11              [-] 5 list: <address>*5, <address>*5, <address>*5...
12: a12 ------------- [-] 5 list: <address>*5, <address>*5, <address>*5...
13: a13                [-] 5 list: <address>*5, <address>*5, <address>*5...
14: a14 --------------- [-] 5 list: <address>*5, <address>*5, <address>*5...
15: a15                  [-] 5 list: <address>*5, <address>*5, <address>*5...
16: a16 ----------------- [-] 5 list: <address>*5, <address>*5, <address>*5...
17: a17                    [+] 1 list: <address>*5
Reference Pattern by <[dict of] class>.
 0: _ --- [-] 1 list: <address>*0
 1: a      [-] 1 list: <address>*1
 2: aa ---- [-] 1 list: <address>*1
 3: a3       [-] 1 list: <address>*1
 4: a4 ------ [-] 1 list: <address>*1
 5: a5         [-] 1 list: <address>*1
 6: a6 -------- [-] 1 list: <address>*1
 7: a7           [-] 1 list: <address>*1
 8: a8 ---------- [-] 1 list: <address>*1
 9: a9             [-] 1 list: <address>*1
<Type e.g. '_.more' for more.>
10: a10 ----------- [-] 1 list: <address>*1
11: a11              [-] 1 list: <address>*1
12: a12 ------------- [-] 1 list: <address>*1
13: a13                [-] 1 list: <address>*1
14: a14 --------------- [-] 1 list: <address>*1
15: a15                  [-] 1 list: <address>*1
16: a16 ----------------- [-] 1 list: <address>*1
17: a17                    [-] 1 list: <address>*1
18: a18 ------------------- [-] 1 list: <address>*1
19: a19                      [-] 1 list: <address>*1
<Type e.g. '_.more' for more.>
20: a20 --------------------- [-] 1 list: <address>*1
21: a21                        [-] 1 list: <address>*1
22: a22 ----------------------- [-] 1 list: <address>*1
23: a23                          [-] 1 list: <address>*1
24: a24 ------------------------- [-] 1 list: <address>*1
25: a25                            [-] 1 list: <address>*1
26: a26 --------------------------- [-] 1 list: <address>*1
27: a27                              [-] 1 list: <address>*1
28: a28 ----------------------------- [-] 1 list: <address>*1
29: a29                                [-] 1 list: <address>*1
<Type e.g. '_.more' for more.>
20: a20 --------------------- [-] 1 list: <address>*1
21: a21                        [-] 1 list: <address>*1
22: a22 ----------------------- [-] 1 list: <address>*1
23: a23                          [-] 1 list: <address>*1
24: a24 ------------------------- [-] 1 list: <address>*1
25: a25                            [-] 1 list: <address>*1
26: a26 --------------------------- [-] 1 list: <address>*1
27: a27                              [-] 1 list: <address>*1
28: a28 ----------------------------- [-] 1 list: <address>*1
29: a29                                [-] 1 list: <address>*1
<Type e.g. '_.more' for more.>
30: a30 ------------------------------- [-] 1 list: <address>*1
31: a31                                  [R] 1 tuple: <address>*1
30: a30 ------------------------------- [-] 1 list: <address>*1
31: a31                                  [R] 1 tuple: <address>*1
Reference Pattern by <[dict of] class>.
 0: _ --- [-] 1 list: <address>*0
 1: a      [-] 1 list: <address>*1
 2: aa ---- [-] 1 list: <address>*1
 3: a3       [-] 1 list: <address>*1
 4: a4 ------ [-] 1 list: <address>*1
 5: a5         [-] 1 list: <address>*1
 6: a6 -------- [-] 1 list: <address>*1
 7: a7           [-] 1 list: <address>*1
 8: a8 ---------- [-] 1 list: <address>*1
 9: a9             [-] 1 list: <address>*1
<22 more lines. Type e.g. '_.more' for more.>
10: a10 ----------- [-] 1 list: <address>*1
11: a11              [-] 1 list: <address>*1
12: a12 ------------- [-] 1 list: <address>*1
13: a13                [-] 1 list: <address>*1
14: a14 --------------- [-] 1 list: <address>*1
15: a15                  [-] 1 list: <address>*1
16: a16 ----------------- [-] 1 list: <address>*1
17: a17                    [-] 1 list: <address>*1
18: a18 ------------------- [-] 1 list: <address>*1
19: a19                      [-] 1 list: <address>*1
<12 more lines. Type e.g. '_.more' for more.>
Reference Pattern by <[dict of] class>.
 0: _ --- [-] 1 list: <address>*0
 1: a      [-] 1 list: <address>*1
 2: aa ---- [-] 1 list: <address>*1
 3: a3       [-] 1 list: <address>*1
 4: a4 ------ [-] 1 list: <address>*1
 5: a5         [-] 1 list: <address>*1
 6: a6 -------- [-] 1 list: <address>*1
 7: a7           [-] 1 list: <address>*1
 8: a8 ---------- [-] 1 list: <address>*1
 9: a9             [-] 1 list: <address>*1
10: a10 ----------- [+] 1 list: <address>*1


Reference Pattern by <[dict of] class>.
 0: _ --- [-] 1 list: <address>*0
 1: a      [-] 1 list: <address>*1
 2: aa ---- [-] 1 list: <address>*1
 3: a3       [-] 1 list: <address>*1
 4: a4 ------ [-] 1 list: <address>*1
 5: a5         [-] 1 list: <address>*1
 6: a6 -------- [-] 1 list: <address>*1
 7: a7           [-] 1 list: <address>*1
 8: a8 ---------- [-] 1 list: <address>*1
 9: a9             [-] 1 list: <address>*1
<Type e.g. '_.more' for more.>
10: a10 ----------- [-] 1 list: <address>*1
11: a11              [-] 1 list: <address>*1
12: a12 ------------- [-] 1 list: <address>*1
13: a13                [-] 1 list: <address>*1
14: a14 --------------- [-] 1 list: <address>*1
15: a15                  [-] 1 list: <address>*1
16: a16 ----------------- [-] 1 list: <address>*1
17: a17                    [-] 1 list: <address>*1
18: a18 ------------------- [-] 1 list: <address>*1
19: a19                      [-] 1 list: <address>*1
<Type e.g. '_.more' for more.>
10: a10 ----------- [-] 1 list: <address>*1
11: a11              [-] 1 list: <address>*1
12: a12 ------------- [-] 1 list: <address>*1
13: a13                [-] 1 list: <address>*1
14: a14 --------------- [-] 1 list: <address>*1
15: a15                  [-] 1 list: <address>*1
16: a16 ----------------- [-] 1 list: <address>*1
17: a17                    [-] 1 list: <address>*1
18: a18 ------------------- [-] 1 list: <address>*1
19: a19                      [-] 1 list: <address>*1
20: a20 --------------------- [+] 1 list: <address>*1
""")
	
    def test_referrer_registration(self):
	import gc

	# The reference pattern should register itself as referrer target
	# so that after a gc, the rp target will still be included in the referrer target
	# Since the target is passed to referrers and update, it will still find the
	# referrers. It is an optimization issue: it should cover the referrers.
	# We test this by having two different-typed referrers
	# Accessing a referrer of the first one, then gc collecting, then checking that
	# the second one can be accessed without update: it was created automatically.
	# The test failed when not registering, but succeeded when registering was added.
	# It succeeds any case if no GC collection is made.

	dst = []
	a = [dst]
	aa = [a]
	b = (dst,)
	ba = [b]
	src = [aa, ba]
	rp = self.rp(dst, src)

	self.asis(rp._.theone, dst)
	gc.collect()
	self.asis(rp.aa.theone, aa)
	self.asis(rp.View.rg[b][0], ba)
    

    def test_some_more_advanced_usages(self):
	import gc

	# Test immediate dominators

	dst = []
	src = [dst]
	src.append([dst])
	rp = self.rp(dst, src, depth=10, imdom=1)
	self.asis(rp._.theone, dst)
	self.asis(rp.a.theone, src)

	# Test with mixed types

	# In particular, dict owned by an instance

	dst = []
	class A:
	    pass
	a = A()
	a.dst = dst
	b = {'dst':dst}

	src = (a, b)

	gc.collect()
	rp = self.rp(dst, src, depth=10)
	rp.er.classifier.is_clear_drg_enabled = 0 # Note Apr 19 2005
	self.asis(rp.a.theone, b)
	self.asis(rp.b.theone, a.__dict__)

	# Test that the dict is eventually automatically removed from dictowners - 
	# First test that dictowners is nonzero

	ln = len(rp.mod.View.dict_ownership)
	self.assert_(ln > 0)

	del src
	del a
	mod = rp.mod
	rp.er.classifier.is_clear_drg_enabled = 1
	del rp
	# It is cleared after GC

	gc.collect()
	lnnow = len(mod.View.dict_ownership)
	self.assert_(lnnow == 0)

class NewCase(TestCase):
    # Some new tests as they come up


    def test_reset(self):
	# Test the .reset() method

	dst = []
	a = [dst]
	b = [dst]
	src = [a,b]
	rp = self.rp(dst, src)
	self.aseq( rp.a, self.iso(a, b) )

	b.pop()
	rp.reset()
	self.aseq( rp.a, self.iso(a) )


    def test_paths(self):
	# Test the .paths() method

	dst = []
	a = [dst]+[None]*40	# Make order well-defined. Note May 2 2005.
	b = [dst]
	src = [a,b]
	rp = self.rp(dst, src)

	expected = """\
Paths from source 'a3' to target '_'.
 0: a3 [0] @ [0]
 1: aa [0]  @ [0]
 2: a  [0]   @ [0]
 3: _  [0]    = <1 list: <address>*0>
 4: aa [0]  @ [1]
 5: a  [1]   @ [0] -> #3"""

	self.aseq( str(rp.paths('a3')), expected)

	expected = expected[:expected.index('\n 4:')]

 	# Test the andsets argument, given as a dict

	self.aseq( str(rp.paths('a3', andsets={'a':self.iso(a)})), expected)

 	# Test the andsets argument, given as a list

	self.aseq( str(rp.paths('a3', andsets=[None, None, self.iso(a)])), expected)


def test_main(debug=0):
    support.run_unittest(RefPatCase,debug)
    support.run_unittest(NewCase,debug)

def test_leak():
    # Runs the tests in a loop and prints memory statistics,
    # to see if there are underlying low-level memory problems.
    # Requires Python to be compiled with debug support.
    from guppy.heapy.heapyc import xmemstats
    import gc, sys, time
    i = 0
    xmemstats()
    while 1:
	print '[%d]'%i, time.asctime()
	i += 1
	test_main()
	gc.collect()
	xmemstats()

if __name__ == "__main__":
    test_main()
