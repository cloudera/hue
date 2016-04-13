#._cv_part guppy.heapy.test.test_Classifiers

from guppy.heapy.test import support

PORTABLE_TEST = 1	# Relax tests to be more portable

class TestCase(support.TestCase):
    def setUp(self):
	support.TestCase.setUp(self)
	self.View.is_rg_update_all = False
	
	self.US = US = self.heapy.UniSet

	self.Use = Use = self.heapy.Use
	Use.reprefix = 'hp.'
	self.do = lambda x:x.dictof

	self.un = Use.Anything.fam
	self.ty = Use.Type
	self.cl = Use.Class
	self.rc = Use.Rcs
	self.iso = Use.iso

	self.Anything = US.Anything
	self.Nothing = US.Nothing

	class C1:
	    def x(self):
		return 0
	class C2:
	    pass
	c1 = C1()

	self.C1 = C1
	self.C2 = C2
	self.c1 = c1

    def lt(self, a, b):
	self.assert_(a < b)

    def eq(self, a, b):
	self.assert_(a == b)

    def dj(self, a, b):
	# disjoint; not related by <= or >=, and not overlapping
	self.assert_(not a <= b)
	self.assert_(not b <= a)
	self.assert_(not a & b)
	self.assert_(a.disjoint(b))

    def nr(self, a, b):
	# not related by <= or >=, and overlapping
	self.assert_(not a <= b)
	self.assert_(not b <= a)
	self.assert_(a & b)
	self.assert_(not a.disjoint(b))


class NewCases(TestCase):
    # New cases that came up after all the original tests had passed,
    # according to notes at Tue Nov 23 06:40:59 MET 2004.
    # To keep original tests intact, for consistency, speed reasons.

    def test_owners(self):
	# Test the .owners attribute
	iso = self.iso
	class C:
	    pass
	class D:
	    pass
	c = C()
	d = D()
	self.aseq(iso(c.__dict__, d.__dict__, C.__dict__).owners,
		  iso(c, d, C))


class SpecialCases(TestCase):
    # Special tests that catch cases that came up during development & debugging
    def test_1(self):

	un = self.un
	ty = self.ty
	cl = self.cl
	do = self.do
	rc = self.rc
	iso = self.iso
	All = self.Anything
	Nothing = self.Nothing
	C1 = self.C1
	C2 = self.C2
	c1 = self.c1

	def eq(a, b):
	    self.assert_(a == b)
	    self.assert_(str(a) == str(b))
	    
	e1 = []
	e2 = {}
	e3 = []
	e4 = ()

	a = rc(cl(C1)) & ty(type(c1))
	b = rc(cl(C1))
	eq((b - a) | a, b)
	eq(a | (b - a), b)

	a = rc(cl(C1)) & ~ty(type(c1))
	b = ty(type(c1)) & ~rc(cl(C1))

	eq(a | b, b | a)

	a = ty(int)
	b = cl(C1)
	c = All

	eq(c - (a & b), (c - a) | (c - b))

	a = cl(C1)
	b = rc(ty(dict))
	c = iso(c1)

	eq( (a | b) | c , a | (b | c))

	a = ty(int)
	b = ty(dict)
	self.assert_( ~a & ~b != Nothing)


	eq( ty(list) & iso(e1, e2, e3), iso(e1, e3))
	eq( (ty(list) | ty(dict)) & iso(e1, e2, e3, e4), iso(e1, e2, e3))
	eq( (ty(list) &~rc(cl(C1))) & iso(e1, e2, e3), iso(e1, e3))
	eq( iso(e1,e3) |  ty(list), ty(list))
	eq( ty(list) | iso(e1,e3), ty(list))

	eq( iso(e1,e3) - iso(e3), iso(e1))
	eq(  ~iso(e3) & iso(e1,e3), iso(e1))

	eq( iso(e1,e2,e3) - ty(dict), iso(e1,e3))
	eq(  ~ty(dict) & iso(e1,e2,e3), iso(e1,e3))
	eq( ty(dict) | iso(e1,e2), ty(dict) | iso(e1))
	eq( iso(e1,e2) | ty(dict), ty(dict) | iso(e1))
	eq( (ty(dict) | ty(tuple)) | iso(e1,e2), (ty(dict) | ty(tuple)) | iso(e1))
	eq( iso(e1,e2) | (ty(dict) | ty(tuple)), (ty(dict) | ty(tuple)) | iso(e1))
	eq( (ty(dict) & ~rc(cl(C1))) | iso(e1,e2), (ty(dict)  & ~rc(cl(C1))) | iso(e1))
	eq( iso(e1,e2) | (ty(dict) & ~rc(cl(C1))), (ty(dict)  & ~rc(cl(C1))) | iso(e1))
	eq( ~ty(dict) | iso(e1, e2), ~ty(dict) | iso(e2))
	eq( iso(e1, e2) | ~ty(dict), ~ty(dict) | iso(e2))
	eq( ty(dict) - iso(e1,e2), ty(dict) - iso(e2))
	eq( ~iso(e1,e2) & ty(dict), ty(dict) - iso(e2))

	eq( iso(e1,e3) ^ iso(e2), iso(e1,e2,e3))
	eq( iso(e1,e3) ^ iso(e2,e3), iso(e1,e2))
	eq( iso(e1,e3) ^ iso(e1,e3), Nothing)

	eq( iso(e1,e3) <= ty(list), True)
	eq( iso(e1,e2) <= ty(list)|ty(dict), True)
	eq( ty(list) >= iso(e1,e3), True)
	eq( ty(list)|ty(dict) >= iso(e1,e2), True)



    def test_2(self):

	un = self.un
	ty = self.ty
	cl = self.cl
	do = self.do
	rc = self.rc
	iso = self.iso
	All = self.Anything
	Nothing = self.Nothing
	C1 = self.C1
	C2 = self.C2
	c1 = self.c1

	class C3(object):
	    def x(self):
		return 1
	
	def asrt(x):
	    self.assert_(x)

	def no(x):
	    self.assert_(not x)

	eq = self.aseq

	# Tests to do with Nothing being finite - having length and iteration

	no(dict in (ty(dict) | ty(int)))
	no([] in (ty(dict) | ty(int)))
	asrt({} in (ty(dict) | ty(int)))
	asrt(dict in (ty(dict) | ty(int) | ty(type(dict))))
	asrt(list(ty(list) & iso({})) == [])

	# When creating ISO classes, we don't want to memoize them
	# which would leak the elements.

	from sys import getrefcount as grc
	import sys, types

	c = C1()
	rc = grc(c)
	x = iso(c)
	x=None
	eq(grc(c), rc)

    def test_dictowner(self):
	# Special test for dict ownership
	# motivated by: dicts that are not found in traversal, should not
	# cause repeated (unsuccessfull) updates of dict ownership
	# This is a performance question, requires special kind of testing
	# 
	# Also tests that dict & dict owners are not leaked
	import sys
	if sys.hexversion >= 0x02070000:
	    print "XXX SKIPPING test_dictowner TEST BECAUSE OF SLUGGISHNESS WITH PYTHON 2.7"	  
	    return
	import gc
	from sys import getrefcount as grc
	Use = self.Use
	C1 = self.C1
	c1 = self.c1
	iso = self.iso

	o = self.python.StringIO.StringIO()

	# Create a dict hidden from view
	d1 = self.View.immnodeset([{}])
	d3 = {}


	# Remember the initial ref counts for target objects

	gc.collect()

	rcd1 = grc(list(d1)[0])
	rcd3 = grc(d3)
	rcC1 = grc(C1)
	rcc1 = grc(c1)
	rcdc1 = grc(c1.__dict__)

	clock = self.python.time.time

	N = 5
        M = 50

	# This was the fast case, when only reachable dicts are classified
	for i in range(N):
	    print >>o, iso(d3).kind
	    print >>o, iso(c1.__dict__).kind

        # Now measure it

        while 1:
            gc.collect()
            t = clock()
            for i in range(M):
                iso(d3).kind
                iso(c1.__dict__).kind
            fast = clock()-t
            if fast >= 0.5: # Enough resolution?
                break
            else:
                M *= 2 # No, try more loops


	# This was a slow case; involving repeated classification of a unreachable dict
	# It was originally 4.97 times slower when N was 5
	# The problem occurs for successive classifications of different dicts,
	# when at least one of them is unreachable.
	
	gc.collect()
	for i in range(N):
	    print >>o, iso(*d1).kind
	    print >>o, iso(c1.__dict__).kind

	gc.collect()
        # Now measure it

	t = clock()
	for i in range(M):
	    iso(*d1).kind
	    iso(c1.__dict__).kind
	slow = clock()-t

        #print 'slow,fast',slow,fast
	self.assert_( slow <= 1.5*fast )

	# This is another slow case according to notes Nov 18 2004.
	# A succession of different unreachable dicts.

	gc.collect()
	dn = self.View.immnodeset([{} for i in range(N)])
	for i in range(N):
	    print >>o, iso(list(dn)[i]).kind

        # Now measure it
	gc.collect()
	dn = self.View.immnodeset([{} for i in range(M)])

	t = clock()
        for i in range(M):
	    iso(list(dn)[i]).kind
	slow = clock()-t

        #print 'slow,fast',slow,fast
	self.assert_( slow <= 1.5*fast )

	# Partition was likewise slow for unreachable dicts
	dn = self.View.immnodeset([{} for i in range(N)])
	gc.collect()
	print >>o, [x[0] for x in Use.Clodo.classifier.partition(dn)]

        # Now measure it
	dn = self.View.immnodeset([{} for i in range(M)])
	gc.collect()
	t = clock()
	[x[0] for x in Use.Clodo.classifier.partition(dn)]
	slow = clock()-t
        #print 'slow,fast',slow,fast
	self.assert_( slow <= 1.5*fast )
	
	# Check that ref counts for target objects are the same as initially

	gc.collect()
	gc.collect()	# Note May 17 2005

	self.aseq(grc(list(d1)[0]), rcd1)
	self.aseq(grc(d3), rcd3)
	self.aseq(grc(c1), rcc1)
	self.aseq(grc(C1), rcC1)
	self.aseq(grc(c1.__dict__), rcdc1)


	self.aseq( o.getvalue(), """\
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict of <Module>.C1
dict (no owner)
dict (no owner)
dict (no owner)
dict (no owner)
dict (no owner)
[hp.Nothing.dictof]
""".replace('<Module>', self.__module__))


    def test_retclaset(self):
	# Test (A) that referrer classifications don't leak their classes
	# and (B) that selection is not disturbed by list arguments
	# (This is removed since it doesnt always work)
	# and (C) that selection does update referrer graph correctly

	self.__module__ = '<Module>' # Make the rendering independent on our name

	from sys import getrefcount as grc
	import gc
	C1 = self.C1
	c1 = self.c1
	
	iso = self.iso
	rcC1 = grc(C1)

	o = self.python.StringIO.StringIO()
	print >>o, iso(C1).byrcs.kind

	s = iso(c1).byrcs.kind
	print >>o, s
	self.aseq(s & iso(c1), iso(c1))

	x = C1()

	# set_trace()

	if 0:
	    self.aseq( s & [c1, x], iso(c1))# (B) makes sure arg is removed from frame when converted
	else:
	    self.aseq(s & iso(c1, x), iso(c1))

	s = iso(x).byrcs.kind
	self.aseq( s & iso(c1, x), iso(x))
	x = C1()
	self.aseq( s & iso(c1, x), iso(x)) # (C) make sure referrer graph is updated by select

	s = None
	x = None
	locals().clear()
	gc.collect()
	gc.collect()			# Note May 17 2005
	self.aseq(grc(C1), rcC1)	# (A)




    def test_alt_retclaset(self):
	# Test the alternative referrer memo update
	# On low level, and the speed of selection

	import gc
	iso = self.iso
	a = []
	b = self.View.immnodeset([[]])

	x = [a, b]
	if 1:
	    hv = self.View.hv

	    rg = self.View.nodegraph()

	    gc.collect()
	    hv.update_referrers_completely(rg)
	    self.assert_( x in rg[a] )


	    self.assert_(rg[list(b)[0]] == (None,))
	    rg.clear()
	    rg=None

	# Test View functionality

	self.View.is_rg_update_all = True
	gc.collect()
	iso(a).referrers
	self.assert_( a in self.View.rg.get_domain() )
	self.assert_( list(b)[0] in self.View.rg.get_domain())

	clock = self.python.time.clock
        s = iso(a)
        N = 1000
        while 1:
            t = clock()
            for i in range(N):
                s.referrers
            fast = clock()-t
            if fast >= 0.5:
                break
            N *= 2	# CPU is too fast to get good resolution, try more loops

	t = clock()
	for i in range(N):
	    self.View.rg.domain_covers([a])
	    self.View.rg[a]
	faster = clock()-t
        s = iso(*b)
	t = clock()
	for i in range(N):
	    s.referrers
	slow = clock() - t
	#print 'slow,fast,faster',slow, fast, faster
	self.assert_(not slow > fast * 4)
	    

    def test_via(self, vlist=['v',]): # vlist is just to make v unoptimizable
	# Special tests for the via classifier

	
	from sys import getrefcount as grc
	import gc

	iso = self.iso
	hp = self.Use
	d = {}
	k = ('k',)
	v = tuple(vlist) # Make sure v is not optimized to a constant

	d[k] = v
	d[v] = v

	rck = grc(k)
	rcv = grc(v)

	s = iso(v)

	self.assert_( s.byvia.kind == hp.Via("_.f_locals['v']", "_[('k',)]", "_[('v',)]", '_.keys()[1]') or
		      s.byvia.kind == hp.Via("_.f_locals['v']", "_[('k',)]", "_[('v',)]", '_.keys()[0]'))
		      
	del s
	gc.collect()
	gc.collect()
	self.aseq(grc(k), rck)
	self.aseq(grc(v), rcv )
		  


		  


class RenderCase(TestCase):

    def test_rendering(self):
	import sys, types
	iso = self.iso
	C1 = self.C1
	c1 = self.c1
	class C3(object):
	    def x(self):
		return 1

	e1 = []
	e2 = {}
	e3 = []

	o = self.python.StringIO.StringIO()
	# str'ing of homogenous & inhoumogenous values

	self.US.summary_str.str_address = lambda x:'<address>'

	def ps(x):
	    print >>o, x.brief

	ps( iso(1,2) )
	ps( iso(1,2.0, 3.0) )
	ps( iso(e1) )
	ps( iso(e1, e2) )
	ps( iso(e1, e3) )

	ps( iso(self.python.exceptions.TypeError()) )
	ps( iso(None) )
	ps( iso(sys, support, types) )
	ps( iso(int, types.ClassType, C3) )
	ps( iso(C1()) )
	ps( iso(C3()) )
	ps( iso(C1) )
	ps( iso(C3) )
	ps( iso(len) )
	ps( iso(self.setUp) )
	ps( iso(C1.x) )
	ps( iso(C1.x.im_func) )
	ps( iso(C1().x) )
	ps( iso(C3.x) )
	ps( iso(C3().x) )

	ps( iso({}) )
	ps( iso(c1.__dict__) )
	ps( iso(types.__dict__) )

	try:
	    1/0
	except:
	    typ, value, traceback = sys.exc_info()

	ps( iso(traceback) )
	ps( iso(traceback.tb_frame) )


        expected = """\
<2 int: 1, 2>
<3 (float | int): <2 float: 2.0, 3.0> | <1 int: 1>>
<1 list: <address>*0>
<2 (dict (no owner) | list): <1 dict (no owner): <address>*0> | <1 list: <ad...>
<2 list: <address>*0, <address>*0>
<1 exceptions.TypeError: <address>>
<1 types.NoneType: None>
<3 module: guppy.heapy.test.support, sys, types>
<3 type: class, <Module>.C3, int>
<1 <Module>.C1: <address>>
<1 <Module>.C3: <address>>
<1 class: <Module>.C1>
<1 type: <Module>.C3>
<1 types.BuiltinFunctionType: len>
<1 types.MethodType: <<Module>.RenderCase at <addre...>
<1 types.MethodType: <Module>.C1.x>
<1 function: <Module>.x>
<1 types.MethodType: <<Module>.C1 at <address>>.x>
<1 types.MethodType: <Module>.C3.x>
<1 types.MethodType: <<Module>.C3 at <address>>.x>
<1 dict (no owner): <address>*0>
<1 dict of <Module>.C1: <address>>
<1 dict of module: types>
<1 types.TracebackType: <in frame <test_rendering at <address>> at <address>>>
<1 types.FrameType: <test_rendering at <address>>>
""".replace('<Module>', self.__module__)
        self.aseq(o.getvalue(), expected)

        if PORTABLE_TEST:
            return

	o = self.python.StringIO.StringIO()

        # The following is nonportable, sizes may change
        # In particular, the list size changed from 2.3 to 2.4
        # The following test is only for 2.3 in 32-bit python

	# pp'ing prints in a nice form
	# This tests all types currently defined in Classifiers.Summary_str
	# and then some
	# Except: frametype; its size varies from time to time!
	
	x = iso(len, C1, 1.0+3j, {1:2,3:4}, 1.25, C1.x.im_func, 1, ['list'],
	   100000000000l, None, C1.x, C1().x, C3.x, C3().x, sys, support,
	   'string', ('tuple',), C3, int, type(None), 
	   # and some types not defined
	   C1(), C3(), c1.__dict__

	   )
	
	print >>o, x
	print >>o, x.more

	# Test instancetype; we need to replace the classifier with bytype

	x = iso(C1()).bytype
	print >>o, x

	if 0:
	    print o.getvalue()
	else:
	    expected = """\
Partition of a set of 24 objects. Total size = 2128 bytes.
 Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
     0      3  12     1272  60      1272  60 type
     1      4  17      144   7      1416  67 types.MethodType
     2      1   4      136   6      1552  73 dict (no owner)
     3      1   4      136   6      1688  79 dict of <Module>.C1
     4      1   4       60   3      1748  82 list
     5      1   4       56   3      1804  85 function
     6      2   8       48   2      1852  87 module
     7      1   4       44   2      1896  89 class
     8      1   4       32   2      1928  91 <Module>.C1
     9      1   4       32   2      1960  92 str
<8 more rows. Type e.g. '_.more' to view.>
 Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
    10      1   4       32   2      1992  94 types.BuiltinFunctionType
    11      1   4       28   1      2020  95 <Module>.C3
    12      1   4       28   1      2048  96 tuple
    13      1   4       24   1      2072  97 complex
    14      1   4       20   1      2092  98 long
    15      1   4       16   1      2108  99 float
    16      1   4       12   1      2120 100 int
    17      1   4        8   0      2128 100 types.NoneType
Partition of a set of 1 object. Total size = 32 bytes.
 Index  Count   %     Size   % Cumulative  % Type
     0      1 100       32 100        32 100 types.InstanceType
""".replace('<Module>', self.__module__)
	    self.aseq(o.getvalue(), expected)


class BaseCase(TestCase):

    def test_minmax(self):
	s = self.guppy.sets.immbitset
	min = self.US.minimals
	max = self.US.maximals

	self.aseq( min([]), [])
	self.aseq( min([1]), [1])
	self.aseq( min([1,1]), [1])
	self.aseq( min([1,2]), [1])
	self.aseq( min([[],[]]), [[]])

	self.aseq( min([s([1]),s([1,2])]), [s([1])])
	self.aseq( min([s([1]),s([1,2]),s([3])]), [s([1]),s([3])])

	self.aseq( max([]), [])
	self.aseq( max([1]), [1])
	self.aseq( max([1,1]), [1])
	self.aseq( max([1,2]), [2])
	self.aseq( max([[],[]]), [[]])

	self.aseq( max([s([1]),s([1,2])]), [s([1,2])])
	self.aseq( max([s([1]),s([1,2]),s([3])]), [s([1,2]), s([3])])

    def test_base_classes(self):
	un = self.un
	ty = self.ty
	cl = self.cl
	do = self.do
	rc = self.rc
	iso = self.iso
	All = self.Anything
	Nothing = self.Nothing
	C1 = self.C1
	C2 = self.C2
	c1 = self.c1
	lt = self.lt
	eq = self.eq
	dj = self.dj
	nr = self.nr

	data = [
	    (All,	eq,	All),


	    (ty(int),	eq,	ty(int)),
	    (ty(int),	dj,	ty(dict)),
	    (ty(int),	lt,	All),

	    (cl(C1),	eq,	cl(C1)),
	    (cl(C1),	dj,	cl(C2)),
	    (cl(C1),	lt,	ty(type(C1()))),
	    (cl(C1),	dj,	ty(int)),
	    (cl(C1),	lt,	All),

	    (do(cl(C1)), eq,	do(cl(C1))),
	    (do(cl(C1)), lt,	All),
	    (do(cl(C1)), dj,	do(cl(C2))),
	    (do(cl(C1)), dj,	cl(C1)),
	    (do(cl(C1)), dj,	ty(int)),
	    (do(cl(C1)), dj,	do(ty(type(C1())))),
	    (do(cl(C1)), lt,	ty(dict)),
	    (do(cl(C1)), dj,	do(rc(ty(dict)))),

	    (rc(ty(dict)),eq,	rc(ty(dict))),
	    (rc(ty(dict)),lt,	All),
	    (rc(ty(dict)),dj,	rc(ty(list))),
	    (rc(cl(C1)), dj,	rc(ty(type(C1())))),
	    (rc(cl(C1)), nr,	ty(type(C1()))),
	    (rc(cl(C1)), nr,	cl(C1)),
	    # (rc(cl(C1)), dj,	rc(rc(cl(C1)))), # Not allowed form anymore / Nov 4 2005
	    (rc(cl(C1)), dj,	rc(do(cl(C1)))),
	    
	    (iso(1),	eq,	iso(1)),
	    (iso(1),	lt,	All),
	    (iso(1),	dj,	iso(2)),
	    (iso(1),	lt,	ty(int)),
	    (iso(1),	dj,	ty(dict)),
	    (iso(1),	dj,	cl(C1)),
	    (iso(c1),	lt,	cl(C1)),
	    (iso(c1.__dict__),lt,do(cl(C1))),
	    (iso(1),	dj,	do(cl(C1))),
	    (iso(1),	dj,	rc(cl(C1))),


	    (Nothing,	eq,	Nothing),
	    (Nothing,	lt,	ty(int)),
	    (Nothing,	lt,	iso(1)),
	    ]

	# Test relation of base classifications
	for a, cmp, b in data:
	    cmp(a, b)
	    # Test the four set-operations: & | - ^
	    # depending on the asserted argument relation
	    if cmp is eq:
		eq(b, a)
	    elif cmp is lt:
		self.assert_(b > a)
		eq(b ^ a, b - a)	# Simple transformation
		eq(a ^ b, b - a)	# -=-, indep. of type
		lt(a, b)
	    elif cmp is dj:
		dj(b, a) # check that the dj relation is symmetric
		eq(a & b, Nothing)
		eq(b & a, Nothing)
		eq(a | b, b | a)
		eq(a - b, a)
		eq((a | b) - b, a)
		eq(a ^ b, a | b)
		eq(b ^ a, a | b)
		lt(a, a | b)
		lt(b, a | b)
	    elif cmp is nr:
		nr(b, a)	 # symmetric as well
		eq(a & b, b & a)
		eq(a & b & b, a & b)
		eq((a & b) - b, Nothing)
		eq((a | b) - b, a - b)
		eq(a | b, b | a)
		lt(Nothing, a & b)
		lt(Nothing, b & a)
		lt(a & b, a)
		lt(a & b, b)
		lt(a - b, a)
		dj(a - b, b)
		lt(a ^ b, a | b)
		lt(a, a | b)
		lt(b, a | b)


    def test_invalid_operations(self):
	US = self.US
	US.auto_convert_iter = False
	US.auto_convert_type = False
	US.auto_convert_class = False

	cl = self.cl
	ty = self.ty
	c1 = self.c1

	self.failUnlessRaises(TypeError, lambda : cl(c1))
	self.failUnlessRaises(TypeError, lambda : ty(c1))
	self.failUnlessRaises(TypeError, lambda:ty(int) <= None)
	self.failUnlessRaises(TypeError, lambda:None >= ty(int))
	self.failUnlessRaises(TypeError, lambda:None <= ty(int))
	
	self.failUnlessRaises(TypeError, lambda:list(ty(int)))
	self.failUnlessRaises(TypeError, lambda:len(ty(int)))

	self.failUnlessRaises(TypeError, lambda:ty(int) & None)
	self.failUnlessRaises(TypeError, lambda:None & ty(int))
	self.failUnlessRaises(TypeError, lambda:ty(int) | None)
	self.failUnlessRaises(TypeError, lambda:None | ty(int))
	self.failUnlessRaises(TypeError, lambda:ty(int) - None)
	self.failUnlessRaises(TypeError, lambda:None - ty(int))
	self.failUnlessRaises(TypeError, lambda:ty(int) ^ None)
	self.failUnlessRaises(TypeError, lambda:None ^ ty(int))

	self.failUnlessRaises(TypeError, lambda: ty(int) | [14])
	self.failUnlessRaises(TypeError, lambda: ty(int) | dict)
	self.failUnlessRaises(TypeError, lambda: ty(int) | self.C1)

    def test_fancy_list_args(self):
	# Test the, normally disabled, possibility to use iterables as
	# right and left arguments in set expressions.
	# This option can cause problems as noted 22/11 2004.

	self.US.auto_convert_iter = True

	eq = self.eq
	iso = self.iso
	ty = self.ty

	e1 = []
	e2 = {}
	e3 = []
	e4 = ()

	eq( ty(list) & [e1, e2, e3], iso(e1,e3))
	eq( [e1, e2, e3] & ty(list) , iso(e1,e3)) 	# Requires __rand__
	eq( [e1,e2,e4] & (ty(dict)|ty(list)) == [e1,e2], True)
	eq( [e1,e2] & (ty(dict)|ty(list)) == [e1,e2], True)
	eq( iso(e1,e2) & (ty(dict)|ty(list)) == [e1,e2], True)
	eq( iso(e1,e2) & [e1, e3], iso(e1))
	eq( iso(e1,e2) | [e1, e3], iso(e1,e2,e3))
	eq( [e1, e3] | iso(e1,e2), iso(e1,e2,e3))		# Requires __ror__
	eq( iso(e1,e3) - [e3], iso(e1))
	eq( [e1,e3] - iso(e3), iso(e1))			# Requires __rsub__
	eq( [e1,e2,e3] - ty(dict), iso(e1,e3))
	eq(  ~ty(dict) & [e1,e2,e3], iso(e1,e3))
	eq( iso(e1,e3) ^ [e2], iso(e1,e2,e3))
	eq( [e2] ^ iso(e1,e3), iso(e1,e2,e3))		# Requires __rxor__
	eq( [e1,e2] <= iso(e1,e2,e3), True)
	eq( [e1,e2] <= ty(list)|ty(dict), True)
	eq( (ty(list)|ty(dict)) >= [e1,e2], True)
	eq( [e1,e2] <= ty(list), False)
	eq( [e1,e2] <= iso(e1), False)
	eq( [e1,e2] >= iso(e1,e2,e3), False)
	eq( [e1,e2] >= iso(e1,e2), True)
	eq( iso(e1,e2,e3) <= [e1,e2], False)
	eq( iso(e1,e2) <= [e1,e2], True)
	eq( iso(e1,e2,e3) >= [e1,e2], True)
	eq( iso(e1,e2) >= [e1,e2,e3], False)


    def test_fancy_type_conversions(self):
	# Test the, perhaps optional, possibility to use types and classes
	# in classification set expressions.

	self.US.auto_convert_type = True
	self.US.auto_convert_class = True

	un = self.un
	ty = self.ty
	cl = self.cl
	do = self.do
	rc = self.rc
	iso = self.iso
	All = self.Anything
	Nothing = self.Nothing
	C1 = self.C1
	C2 = self.C2
	c1 = self.c1

	def eq(a, b):
	    self.assert_(a == b)
	    
	e1 = []
	e2 = {}
	e3 = []
	e4 = ()

	eq( ty(dict), dict)
	eq( cl(C1), C1)
	eq( iso(e1,e2) & dict, iso(e2))
	eq( dict & iso(e1,e2), iso(e2))
	eq( iso(e1,e2) | dict, iso(e1) | ty(dict))
	eq( dict | iso(e1,e2), iso(e1) | ty(dict))
	eq( iso(e1,e2) - dict, iso(e1))
	eq( dict - iso(e1,e2), ty(dict) - iso(e2))
	eq( iso(e1,e2, e3) ^ dict, (ty(dict)-iso(e2))|iso(e1,e3))

class LawsCase(TestCase):
    def test_laws(self):
	un = self.un
	ty = self.ty
	cl = self.cl
	do = self.do
	rc = self.rc
	iso = self.iso
	All = self.Anything
	Nothing = self.Nothing
	C1 = self.C1
	C2 = self.C2
	c1 = self.c1
	lt = self.lt
	eq = self.eq

	t = self.guppy.sets.test

	absorption = t.absorption
	associative = t.associative
	commutative = t.commutative
	deMorgan = t.deMorgan
	distributive = t.distributive
	idempotence = t.idempotence
	inclusion = t.inclusion

	def ltr(a, b, level=3):
	    lt(a, b)
	    eq(a & b, a)
	    eq(b & a, a)
	    eq(a | b, b)
	    eq(b | a, b)
	    eq(a - b, Nothing)
	    eqr(b - a, b - a)
	    eq((b - a) | a, b)
	    eq(a | (b - a), b)
	    eq(a & (b - a), Nothing)
	    eq((b - a) & a, Nothing)
	    eq((b - a) - a, (b - a))
	    eq(a - (b - a), a)	#  note Nov 3 2004
	    if level > 0:
		if a is Nothing:
		    eq(b - a, b)
		else:
		    ltr(b - a, b, level-1)
	    
	def eqr(a, b, level = 1):
	    eq(a, b)
	    eq(a & b, a)
	    eq(a | b, a)
	    eq(a - b, Nothing)
	    eq(a ^ b, Nothing)
	    if level:
		eqr(b, a, level - 1)

	classes = [All, ty(int), ty(type(c1)), cl(C1), do(cl(C1)), rc(ty(dict)), iso(c1), Nothing]

	for a in classes:
	    idempotence(a)
	    for b  in classes:
		if a <= b:
		    if b <= a:
			eqr(a, b)
		    else:
			ltr(a, b)
		elif b <= a:
		    ltr(b, a)

		absorption(a, b)
		commutative(a, b)

		inclusion(a, b)
		deMorgan(a, b)
		for c in classes:
		    associative(a, b, c)
		    deMorgan(a, b, c)
		    distributive(a, b, c)
			

class ClassificationCase(TestCase):

    def test_classification(self):
	# Test classification by the standard classifiers
	self.View.is_rg_update_all = True # Tricky details Note Apr 22 2005
	Use = self.Use
	iso = self.iso
	nodeset = self.heapy.UniSet.immnodeset
	class A:
	    pass
	class B(object):
	    pass
	a = A()
	b = B()
	li = [1, [], {}, a, b, a.__dict__, b.__dict__]
	for o in li:
	    self.asis(iso(o).bytype.kind.arg, type(o))
	for o in li:
	    kind = type(o)
	    if kind == type(a):
		kind = o.__class__
	    self.asis(iso(o).byclass.kind.arg, kind)
	for o in li:
	    if o is a.__dict__:
		kind = iso(a).kind
	    elif o is b.__dict__:
		kind = iso(b).kind
	    elif type(o) is dict:
		kind = Use.Nothing
	    elif o is a:
		kind = a.__class__
	    else:
		kind = type(o)
	    self.aseq(iso(o).kind.arg, kind)
	cla = iso(()).byunity.kind
	self.asis(cla.arg, None)
	for o in li:
	    self.aseq(iso(o).byunity.kind, cla)
	for o in li:
	    self.aseq(iso(o).byid.kind, Use.Id(id(o)))
	#self.View.update_referrers(nodeset(li))
	for i, o in enumerate(li):
	    cl = iso(o).byrcs.kind
	    if 1 <= i <= 2:
		self.aseq(cl, Use.Clodo.sokind(list).refdby)
	    if i == 5:
		self.aseq(cl, Use.Clodo.sokind(A)(list).refdby)
	    if i == 6:
		self.aseq(cl, Use.Clodo.sokind(B)(list).refdby)

    def test_selection(self):
	# Test classifications operations via selection invariant

	Use = self.Use

	class A:
	    pass
	class B(object):
	    pass
	a = A()
	b = B()
	li = Use.iso(135l, [], {}, a, b, a.__dict__, b.__dict__)

	allers = (Use.Unity, Use.Type, Use.Class, Use.Clodo,
		  Use.Rcs, Use.Via) #, Use.Id
	ps = {}
	for er in allers:
	    # p = er.classifier.partition(li.nodes)
            p = [(av.kind, av) for av in li.by(er).partition]
	    for ak, av in p:
		if ak in ps:
		    self.aseq( ps[ak],  av)
		else:
		    ps[ak] = av

	for ak, av in ps.items():
	    self.aseq ( ak & li, av )
	    for bk, bv in ps.items():
		# Test set operations by selection definition
		self.aseq ( (ak & bk) & li, av & bv)
		self.aseq ( (ak | bk) & li, av | bv)
		self.aseq ( (ak - bk) & li, av - bv)
		self.aseq ( (bk - ak) & li, bv - av)
		self.aseq ( (ak ^ bk) & li, av ^ bv)

def test_main(testrender=1, debug=0):

    if 0 or not debug:
	support.run_unittest(BaseCase, debug)

    if 1 or not debug:
	support.run_unittest(ClassificationCase, debug)

    if 0 or not debug:
	support.run_unittest(LawsCase, debug)

    if 0 or not debug:
	support.run_unittest(NewCases, debug)

    if 0 or (testrender and not debug):
	support.run_unittest(RenderCase, debug)

    if 0 or not debug:
	support.run_unittest(SpecialCases, debug)

if 0 and __name__ == "__main__":
    # It doesn't like to be run under name __main__,
    # needs to have its actual module name.
    import guppy.heapy.test.test_Classifiers as x
    if 1:
	reload(x)
    x.test_main()
