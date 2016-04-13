#._cv_part guppy.heapy.test.test_Path

from guppy.heapy.test import support
import sys, unittest

class TestCase(support.TestCase):
    def setUp(self):
	support.TestCase.setUp(self)
	self.Path = self.heapy.Path

    def chkrel(self, src, dst, relstr=None, clas=None):
	rel = self.relation(src, dst)
	if clas is not None:
	    self.assert_(isinstance(rel, clas))
	if relstr is None:
	    print rel
	else:
            sr = str(rel)
            if sr.startswith('<') and not relstr.startswith('<'):
                self.assert_( sr.endswith('>') )
                sr = sr[1:-1].split(',')
                self.assert_(relstr in sr)
            else:
                self.aseq(sr, relstr)
	
    def chkrelattr(self, src, *attrs):
	for attr in attrs:
	    self.chkrel(src, getattr(src, attr), '%s.'+attr)

    def chkpath(self, src, dst, expect=None):
	rel = self.shpaths(dst, src)
	if expect is None:
	    print rel
	else:
	    li = rel.aslist()
	    if len(li) == 1: li = li[0]
	    self.aseq(str(li), str(expect), -1)

    def relation(self, src, dst):
	return self.Path.relation(src, dst)

    def shpaths(self, dst, src=None, *args, **kwds):
	#return self.Path.shpaths(dst, src, *args, **kwds)

	dst = self.iso(dst)
	if src is not None:
	    src = self.iso(src)
	return dst.get_shpaths(src, *args, **kwds)

class RelationTestCase(TestCase):
    # Test relations from standard types and some simple paths

    def test_list_relation(self):
	v1 = 'v1'
	v2 = 'v2'
	v3 = range(100, 200)
	x = [v1, v2, v3]
        # xxx Why are these commented out?
        # It works when I remove the first comment...
        # Didn't it work in some other arch?
	#self.chkrel(x, v1, '%s[0]')
	#self.chkrel(x, v2, '%s[1]')
	#self.chkrel(x, v3, '%s[2]')

    def test_cell_relation(self):
	cellvalue = []
	def f():
	    return cellvalue
	self.chkrel(f.func_closure[0], cellvalue, '%s->ob_ref')

    def test_class_relation(self):
	# Test old-style classes
	class T:
	    tvar = []
	class U:
	    uvar = []
	class V(U,T):
	    vvar = []
	self.chkrelattr(V, '__name__', '__dict__', '__bases__', 'vvar')
	# The relation method doesn't look in base classes -
	# I suppose it doesn't need to. This would be a test in that case:
	# 	self.chkrel(V, V.uvar, '%s.uvar')
	# Currently, only the path is found:
	self.chkpath(V, V.uvar, "%s.__bases__[0].__dict__['uvar']")
	self.chkpath(V, V.tvar, "%s.__bases__[1].__dict__['tvar']")
	self.chkpath(V, V.vvar, "%s.__dict__['vvar']")

    def test_code_relation(self):
	def f():
	    a = 3
	    return self, a
	co = f.func_code
	self.chkpath(co, 3, '%s.co_consts[1]')  # xxx brittle test but catches a bug
						# commented in notes Sep 27 2004
	self.chkrelattr(co, 'co_code', 'co_consts', 'co_names', 'co_varnames',
			'co_freevars', 'co_cellvars', 'co_filename', 'co_name',
			'co_lnotab')


#B

    def test_dict_relation(self):
	k1 = 'k1'
	k2 = 'k2'
	v1 = 'v1'
	v2 = 'v2'
	k3 = tuple(range(100))
	v3 = tuple(range(100, 200))
	x = {k1:v1, k2:v2, k3:v3}
	self.chkrel(x, v1, "%s['k1']")
	self.chkrel(x, v2, "%s['k2']")
	self.chkrel(x, v3, "%s[(0, 1, 2, 3, 4, 5, ...)]")
	ks = [str(self.relation(x, k1)),
	      str(self.relation(x, k2)),
	      str(self.relation(x, k3))]
	ks.sort()
	self.aseq(ks, ['%s.keys()[0]', '%s.keys()[1]', '%s.keys()[2]'])
	
    def test_dictproxy_relation(self):
	v1 = 'v1'
	class T(object):
	    k1 = v1
	x = T.__dict__
	self.chkpath(x, v1, "%s->dict['k1']")
	self.chkrel(x, v1, "%s['k1']")

    def test_frame_relation(self):
	try:
	    1/0
	except:
	    type, value, traceback = sys.exc_info()
	    f = traceback.tb_frame
	f.f_trace = lambda : None
	f.f_exc_type = []
	f.f_exc_value = []
	f.f_exc_traceback = []
	self.chkrelattr(f,'f_back', 'f_code', 'f_builtins', 'f_globals',
			'f_trace', 'f_exc_type', 'f_exc_value', 'f_exc_traceback',
			'f_locals')
	
	a = []
	# The representation of local variables is how they may be accessed
	# - not how they are really stored.
	# xxx this may be confusing/lack information?
	# The information is available in the relation object class,
	# it is just not represented with str()...
	self.chkrel(f, a, "%s.f_locals['a']", clas=self.Path.R_LOCAL_VAR)

	x = []
	z = []

	def func(x, y=3):
	    try:
		1/0
	    except:
		type, value, traceback = sys.exc_info()
		frame = traceback.tb_frame
	    return self, frame, z
	_, frame, __ = func(0)
	del _, __
	self.chkrel(frame, self, "%s.f_locals ['self']", clas=self.Path.R_CELL)

	self.chkrel(f, x, "%s.f_locals['x']", clas=self.Path.R_LOCAL_VAR)
	self.chkrel(f, z, "%s.f_locals ['z']", clas=self.Path.R_CELL)
	# self becomes both a local var and a cell var, since it is an argument.
	self.chkrel(f, self, "<%s.f_locals['self'],%s.f_locals ['self']>")

	# Stack variables doesn't work (Because ceval.c doesn't update
	# the f_stacktop index.) so the corresponding part of frame_relate is not tested.


#B

    def test_function_relation(self):
	def f(x, y=3):
	    return self
	f.a = []

	self.chkrelattr(f, 'func_code', 'func_globals', 'func_defaults',
			'func_closure', 'func_doc', 'func_name', 'func_dict',
			'a')

    def test_instance_relation(self):
	# Test 'traditional' class instance
	class T:
	    tvar = []
	t = T()
	self.chkrelattr(t, '__class__', '__dict__')
	t.a = []
	self.chkrelattr(t, 'a')
	# No direct relation for class variables - as noted in test_object_relation
	self.chkpath(t, t.tvar, "%s.__class__.__dict__['tvar']")
	
	class U:
	    uvar = []

	class V(U, T):
	    vvar = []

	v = V()
	self.chkpath(v, v.uvar, "%s.__class__.__bases__[0].__dict__['uvar']")
	self.chkpath(v, v.tvar, "%s.__class__.__bases__[1].__dict__['tvar']")
	self.chkpath(v, v.vvar, "%s.__class__.__dict__['vvar']")


    def test_instancemethod_relation(self):
	class T:
	    def f(x):
		pass
	self.chkrelattr(T.f, 'im_func', 'im_class')
	t = T()
	self.chkrelattr(t.f, 'im_func', 'im_class', 'im_self')

    def test_list_relation(self):
	v1 = 'v1'
	v2 = 'v2'
	v3 = range(100, 200)
	x = [v1, v2, v3]
	self.chkrel(x, v1, '%s[0]')
	self.chkrel(x, v2, '%s[1]')
	self.chkrel(x, v3, '%s[2]')
	    
#
    def test_meth_relation(self):
	x = []
	#self.chkrel(x.append, x, '%s->m_self')
	self.chkrel(x.append, x, '%s.__self__')

    def test_module_relation(self):
	self.chkrelattr(unittest, '__dict__', 'TestCase')

    def test_nodegraph_relation(self):
	a = 0
	b = 1
	rl = [a, b]
	rg = self.heapy.heapyc.NodeGraph([(a, rl), (b, rl)])
	self.chkrel(rg, a, '%s->edges[0].src')
	self.chkrel(rg, b, '%s->edges[1].src')
	self.chkrel(rg, rl, '<%s->edges[0].tgt,%s->edges[1].tgt>')
	self.chkpath(rg, a, '%s->edges[0].src')
	self.chkpath(rg, rl, ['%s->edges[0].tgt', '%s->edges[1].tgt'])
	
    def test_nodeset_relation(self):
	from guppy.sets import immnodeset, mutnodeset
        if 0:
            # This is hard to get to work accross different architectures
            # Noted Jan 17 2006
            x = [0, 1, 'a', 'b']
            x.sort(lambda a, b: cmp(id(a), id(b)))
        else:
            # This is a relaxed variant, still tests SOME thing!
            x = ['a']
	for s in (immnodeset(x), mutnodeset(x)):
	    for i in range(len(x)):
		self.chkrel(s, x[i], 'list(%%s)[%s]'%i)
		     

    def test_object_relation(self):
	class T(object):
	    __slots__ = 'a', 'b'
	t = T()
	a = []
	t.a = a
	b = []
	t.b = b
	#self.chkrel(t, T, 'type(%s)')
	self.chkrel(t, T, '%s->ob_type')
	self.chkrelattr(t, 'a', 'b')
	# We shouldn't have a __dict__ here - just make sure this is the case
	self.failUnlessRaises(AttributeError, lambda:t.__dict__)

	class U(T):
	    pass
	u = U()
	u.a = a
	self.chkpath(u, T, "%s->ob_type.__base__")
	self.chkrel(u, a, '%s.a')

	c = []
	u.c = c
	self.chkrel(u, c, '%s.c')
	self.chkrel(u, u.__dict__, '%s.__dict__')

	class V(U):
	    pass
	v = V()
	v.c = c
	self.chkrelattr(v, '__dict__')

	class W(V):
	    __slots__ = 'c', 'd', 'b'
	    pass
	w = W()
	w.a = a
	w.b = b
	w.c = c
	w.d = []
	w.e = []
	self.chkrelattr(w, '__dict__', 'a', 'b', 'c', 'd', 'e')
	self.chkpath(w, w.a, '%s.a')
	self.chkpath(w, w.b, '%s.b')
	self.chkpath(w, w.c, '%s.c')
	self.chkpath(w, w.d, '%s.d')
	self.chkpath(w, w.e, "%s.__dict__['e']")

	class R(object):
	    rvar = []
	class S(R, T):
	    svar = []
	    
	s = S()
	s.a = a
	s.b = b
	s.c = c
	self.chkrelattr(s, '__dict__', 'a', 'b', 'c')
	self.chkpath(s, s.a, '%s.a')
	self.chkpath(s, s.b, '%s.b')
	self.chkpath(s, s.c, "%s.__dict__['c']")

	# Class variables are not directly related- should they be that?
	# Possibly, but the compression could as well be done in Python.
	# We just check that we can get the path.
	self.chkpath(s, s.svar, "%s->ob_type.__dict__['svar']")
	self.chkpath(s, s.rvar, ["%s->ob_type.__bases__[0].__dict__['rvar']",
				 "%s->ob_type.__mro__[1].__dict__['rvar']"])
	self.chkpath(s, s.__slots__, "%s->ob_type.__base__.__dict__['__slots__']")


    def test_traceback_relation(self):
	try:
	    def g():
		1/0
	    g()
	except:
	    type, value, traceback = sys.exc_info()
	self.chkrelattr(traceback, 'tb_next', 'tb_frame')

    def test_tuple_relation(self):
	v1 = 'v1'
	v2 = 'v2'
	v3 = range(100, 200)
	x = (v1, v2, v3)
	self.chkrel(x, v1, '%s[0]')
	self.chkrel(x, v2, '%s[1]')
	self.chkrel(x, v3, '%s[2]')

    def test_type_relation(self):
	name = 'T'
	base = object
	bases = (base,)
	dict = {'__slots__':('a','b')}
	T = type(name, bases, dict)
	# tp_dict can't be directly tested since .__dict__ returns a proxy
	# and the dict passed is not used directly.
	# We test it indirectly by getting a path through it.
	self.chkpath(T, T.a, "%s.__dict__['a']")
	# The C-struct __slots__ field can't be tested directly
	# This just tests the ordinary attribute
	self.chkpath(T, T.__slots__, "%s.__dict__['__slots__']")
	self.chkrelattr(T, '__mro__', '__base__', '__bases__')
	# tp_cache and tp_subclasses can also not be tested directly

	# We could try use referrers if it worked
	# print V.referents(T).reprobj.select('TOC=="dict"')
	
	# Inheritance is tested via test_object_relation()

	    
class RootTestCase(TestCase):

    def test_1(self):
	import sys, __builtin__
	root = self.View.root
	# Interpreter attributes

	rel = str(self.relation(root, sys.modules))

	self.assert_(eval(rel % 'root') is sys.modules)
	self.aseq(rel, '%s.i0_modules')

	rel = str(self.relation(root, sys.__dict__))
	self.assert_(eval(rel % 'root') is sys.__dict__)
	self.aseq(rel, '%s.i0_sysdict')

	rel = str(self.relation(root, __builtin__.__dict__))
	self.assert_(eval(rel % 'root') is __builtin__.__dict__)
	self.aseq(rel, '%s.i0_builtins')

	if sys.version >= "2.3.3": # The version I saw them; they may have come earlier
	    for name in "codec_search_path", "codec_search_cache", "codec_error_registry":
		attr = "i0_%s"%name
		rel = str(self.relation(root, getattr(root, attr)))
		self.aseq(rel, '%%s.%s'%attr)


	# Thread attributes

	try:
	    1/0
	except:
	    exc_type, exc_value, exc_traceback = sys.exc_info()
	    for name in 'exc_type', 'exc_value', 'exc_traceback':
		rel = str(self.relation(root, eval(name)))
		self.asis(eval(rel % 'root') , eval(name))
		
	    # There are more, untested, attributes, but the code is farily regular...
	    # More complication is to do with frames which I concentrate on for now.
		
	    # We need to find out what level we are at - count to lowest frame
	    level = 0
	    frame = exc_traceback.tb_frame
	    #print self.relation(root, frame)
	    #print self.relation(root, exc_type)


	    while frame.f_back:
		frame = frame.f_back
		level += 1
	    rel = str(self.relation(root, frame))
	    self.assert_(rel.endswith('_f0'))
	    rel = str(self.relation(root, exc_traceback.tb_frame))
	    import re
	    self.asis( eval(rel%'root'), exc_traceback.tb_frame)
	    self.assert_(rel.endswith('_f%d'%level))
	
	
    def test_thread(self):
	try:
	    import thread
	except ImportError:
	    print 'threading not enabled - skipping test'
	    return

	root = self.View.root
	
	def task(self):
	    try:
		1/0
	    except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
	    self.exc_traceback = exc_traceback
	    self.sync = 1
	    while self.sync:
		pass
	    self.sync = 1
	    
	self.sync = 0
	thread.start_new_thread(task, (self,))
	while not self.sync:
	    pass
	exc_traceback = self.exc_traceback
	rel = str(self.relation(root, exc_traceback))
	self.asis(eval(rel%'root'), exc_traceback)
	self.sync = 0
	while not self.sync:
	    pass
	    
	def task(self):
	    self.test_1()
	    self.sync = 1
	self.sync = 0
	thread.start_new_thread(task, (self,))
	while not self.sync:
	    pass

    def _test_secondary_interpreter(self):
	try:
	    import thread
	except ImportError:
	    print 'threading not enabled - skipping test'
	    return

	import_remote = """\
import sys
import thread
import time
def task():
    time.sleep(0.5)
thread.start_new_thread(task, ())

self.sysdict = sys.__dict__
self.sync = 1
while self.sync:
    pass
# print 'done'

"""


	self.sync = 0
	thid = self.heapy.heapyc.interpreter(import_remote, {'self':self})
	
	root = self.View.root

	import sys
	sysdict = sys.__dict__
	rel = str(self.relation(root, sysdict))
	self.aseq(rel, '%s.i0_sysdict')

	while not self.sync:
	    pass

	rel = str(self.relation(root, self.sysdict))
	self.aseq(rel, '%s.i1_sysdict')

	self.sync = 0

    def test_rootframe(self):
	# assert 0 # to do
	pass

class PathTestCase(TestCase):


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

    def chkgraph(self, width, length, expect=None):
	src, dst = self.makegraph(width, length)
	self.chkpath(src, dst, expect)

    def test_path(self):
	dst = 'dst'
	self.chkpath([dst], dst, '%s[0]')
	self.chkpath([[], dst], dst, '%s[1]')
	self.chkpath([dst, dst], dst, "['%s[0]', '%s[1]']")
	self.chkpath([[dst,0], dst, [dst,2]], dst, "%s[1]")
	self.chkpath([[dst,0], [dst,2]], dst, "['%s[0][0]', '%s[1][0]']")


	src, dst = self.makegraph(1, 1)

	self.chkgraph(1, 1, '%s[0]')
	self.chkgraph(1, 2, '%s[0][0]')
	self.chkgraph(2, 1, ['%s[0]', '%s[1]'])
	self.chkgraph(3, 2, ['%s[0][0]', '%s[0][1]',	 '%s[0][2]',
			     '%s[1][0]', '%s[1][1]',	 '%s[1][2]',
			     '%s[2][0]', '%s[2][1]',	 '%s[2][2]'])

    def test_numpaths(self):
	for (width, length) in [(2, 1), (7, 3), (3, 7), (10, 20)]:
	    src, dst = self.makegraph(width, length)
	    p = self.shpaths(dst, src)
	    self.aseq( p.numpaths, width**length)

    def test_iter(self):
	src, dst = self.makegraph(2, 2)
	p = self.shpaths(dst, src)
	it = iter(p)
	ss = []
	for i in it:
	    ss.append(str(i))
	ss.sort()
	self.aseq(ss, ['%s[0][0]', '%s[0][1]', '%s[1][0]', '%s[1][1]'])

	# Check that we can get some of the first values from the iterator
	# of a graph with an astronomical number of paths.

	width = 11
	length = 13
	numpaths = 20
	src, dst = self.makegraph(width, length)
	p = self.shpaths(dst, src)
	it = iter(p)
	for i in range(numpaths):
	    path =  it.next()
	    sp = str(path)
	    div, mod = divmod(i, width)
	    self.aseq(sp, '%s'+'[0]'*(length-2)+'[%d][%d]'%(div, mod))

	# Check that the iterator works even if the graph initially
	# would yield astronomical numbers of dead ends.
	# (The initial algorithm took astronomically long time.)

	osrc = src
	#osrc = [[],[]]

	src, dst = self.makegraph(width, length)
	src[0] = osrc
	p = self.shpaths(dst, src)
	it = iter(p)
	for i in range(numpaths):
	    path =  it.next()
	    sp = str(path)
	    div, mod = divmod(i, width)
	    self.aseq(sp, '%s[1]'+'[0]'*(length-3)+'[%d][%d]'%(div, mod))
	    #print sp

	# Test iterating with a negative start and a large positive start

	numfromend = width / 2
	for it in [p.iter(-numfromend), p.iter(p.numpaths-numfromend)]:
	    for i, path in enumerate(it):
		sp = str(path)
		self.aseq(sp, '%s'+('[%d]'%(width-1))*(length-1)+'[%d]'%(width-numfromend+i))

	# Test iterating with start and stop

	start = 5
	stop = 25
	i = start
	for path in p.iter(start, stop):
	    sp = str(path)
	    div, mod = divmod(i, width)
	    self.aseq(sp, '%s[1]'+'[0]'*(length-3)+'[%d][%d]'%(div, mod))
	    self.aseq(path.index, i)
	    i += 1
	self.aseq(i, stop)


    def test_str(self):
	# Make sure large number of paths will yield reasonable representations
	width = 11
	length = 4
	src, dst = self.makegraph(width, length)
	p = self.shpaths(dst, src)
	p.maxpaths = 1
	self.aseq(str(p), " 0: Src[0][0][0][0]\n<... 14640 more paths ...>")
	p.maxpaths = 2
	self.aseq(str(p), " 0: Src[0][0][0][0]\n 1: Src[0][0][0][1]\n<... 14639 more paths ...>")

    def test_printing(self):
	# Test the pretty-printing and moreing methods
	from StringIO import StringIO
	output = StringIO()
	self.Path.output = output
	width = 11
	length = 4
	src, dst = self.makegraph(width, length)
	p = self.shpaths(dst, src)
	p.maxpaths = 2
	p.pp()
	p.more()
	self.aseq( output.getvalue(),"""\
 0: Src[0][0][0][0]
 1: Src[0][0][0][1]
<... 14639 more paths ...>
 2: Src[0][0][0][2]
 3: Src[0][0][0][3]
<... 14637 more paths ...>
"""	)

    def test_subscript(self):
	# Test subscripting
	width = 3
	length = 40
	src, dst = self.makegraph(width, length)
	p = self.shpaths(dst, src)
	np = width**length
	self.aseq(np, p.numpaths)
	#p[0].pp(p.output)
	self.aseq(str(p[0]), '%s'+'[0]'*length)
	self.aseq(str(p[-np]), '%s'+'[0]'*length)
	self.aseq(str(p[width-1]), '%s'+'[0]'*(length-1) + '[%d]'%(width-1))
	self.aseq(str(p[width]), '%s'+'[0]'*(length-2) + '[1][0]')
	self.aseq(str(p[width+1]), '%s'+'[0]'*(length-2) + '[1][1]')
	self.aseq(str(p[np-1]), '%s'+('[%d]'%(width-1))*length)
	self.aseq(str(p[-1]), '%s'+('[%d]'%(width-1))*length)
	self.failUnlessRaises(IndexError, lambda:p[np])
	self.failUnlessRaises(IndexError, lambda:p[-np-1])


class MultiTestCase(TestCase):
    def test_pp(self):
	# Test printing of multi relations
	self.Path.output = self.Path._root.StringIO.StringIO()
	iso = self.iso
	dst = [[],[]]
	src = iso(dst[:]*2)
	dst = [iso(x) for x in dst]
	p = self.Path.shpgraph(dst, src)
	p.pp()
	p = self.Path.shpgraph(dst, src, srcname='A',dstname='B')
	p.pp()
    
	self.aseq(self.Path.output.getvalue(), """\
--- Dst[0] ---
 0: Src[0]
 1: Src[2]
--- Dst[1] ---
 0: Src[1]
 1: Src[3]
--- B[0] ---
 0: A[0]
 1: A[2]
--- B[1] ---
 0: A[1]
 1: A[3]
""")	
	

class AvoidTestCase(TestCase):
    def test_1(self):
	# Test that we can find new paths by avoiding edges
	# selected from previously found paths.
	# First we generate a graph with paths of various lengths...

	src = ['src']
	a = src
	for i in range(3):
	    b = ['b%d'%i]
	    c = ['c%d'%i,b]
	    a.append(b)
	    a.append(c)
	    a = b
	dst = a
	p = self.shpaths(dst, src)

	for avoid, result in [
	    ([],	'%s[1][1][1]'),
	    ([0],	'%s[2][1][1][1]'),
	    ([1],	'%s[1][2][1][1]'),
	    ([2],	'%s[1][1][2][1]'),
	    ([0, 1],	'%s[2][1][2][1][1]'),
	    ([1, 2],	'%s[1][2][1][2][1]'),
#	    ([1, -1],	'%s[1][2][1][2][1]'),
	    ([0, 2],	'%s[2][1][1][2][1]'),
	    ([0, 1, 2],	'%s[2][1][2][1][2][1]'),
	    ([2, 1, 0],	'%s[2][1][2][1][2][1]'),

	    ]:
	    result = result%' 0: Src'
	    # Find new path by avoiding edges from the original path
	    q = self.shpaths(dst, src, avoid_edges=p.edges_at(*avoid))
	    self.aseq(str(q), result)
	    # Find the same path but via a direct method
	    q = p.copy_but_avoid_edges_at_levels(*avoid)
	    self.aseq(str(q), result)
	    # The same, but via a shorter method name
	    q = p.avoided(*avoid)
	    self.aseq(str(q), result)

	# Test that the avoided set is carried on to copies

	q = p.avoided(0).avoided(2)
	self.aseq(str(q), ' 0: Src[2][1][2][1][1]')

class NewTestCase(TestCase):
    def test_1(self):
	import sys
	o = self.python.StringIO.StringIO()
	iso = self.iso
	x = iso(sys.__dict__)
	print >>o, x.shpaths
	# This used to include a path via parameter avoid_edges
	# which was confusing
	print >>o, x.shpaths.avoided(0)

	# repr() used to be quite useless. I have it now defined as .pp(),
	# but without trailin newline.

	print >>o, repr(x.shpaths)
	print >>o, repr(x.shpaths)


	# The shpaths object could sometimes disturb a shpath calculation
	# because dst was free in it.

	x = []
	y = [[[x]]]

	sp = iso(x).get_shpaths(iso(y))
	print >>o, sp

	y.append(sp)
	print >>o, iso(x).get_shpaths(iso(y))


	# Test that the shortest paths to a set of objects, is the shortest
	# paths to those that can be reached by the shortest paths, only

	
	x = []
	y = [x]
	z = [y]

	print >>o, iso(x, y).get_shpaths(iso(z))

	if 0:	    # feature is dropped, for now at least. Nov 4 2005

	    # Test that the shortest path to an abstract set of objects,
	    # is the shortest paths to all the closest such objects,
	    # and that the time to calculate this doesn't need to involve
	    # an entire heap traversal to find all such objects

	    clock = self.python.time.clock
	    import gc
	    gc.collect()
	    t = clock()

	    x = str(iso(x, y).get_shpaths(iso(z)))

	    fast = clock() - t

	    gc.collect()
	    t = clock()
	    x = str((iso() | list).get_shpaths(iso(z)))
	    slow = clock() - t

	    # Originally, it was 16 times slower to use an abstract set
	    # Now, it's about 2.5;
	    # print slow/fast # has been seen printing 2.17 to 3.25
	    # we test with some margin
	    self.assert_(slow < 5 * fast)

	# Test that we can relate objects that inherits from a class and object
	# (Used to segfault)

	class C:
	    pass

	class O(C, object):
	    __slots__ = 'x',

	ob = O()
	ob.x = x
	
	print >>o, iso(x).get_shpaths(iso(ob))

	# Test that generalization to a set of sources makes some sense
	# The shortest paths are from the closest sources

	# Hack to make a constant address rendering, for test comparison.
	# This doesn't change anything permanently.
	# XXX come up with an official way to do this.
	summary_str = self.heapy.UniSet.summary_str
	str_address = lambda x:'<address>'
	str_address._idpart_header = getattr(summary_str.str_address, '_idpart_header', None)
	str_address._idpart_sortrender = getattr(summary_str.str_address, '_idpart_sortrender', None)
	summary_str.str_address = str_address

	S = iso()
	shp = iso(x).get_shpaths(iso(y, z))
	print >>o, shp
	print >>o, repr(shp)
	for p in shp:
	    S = S ^ p.src
	self.aseq(S, iso(y))

	shp = iso(x).get_shpaths(iso(ob, y, z))
	print >>o, str(shp)
	print >>o, repr(shp)
	S = iso()
	for i, p in enumerate(shp):
	    S = S ^ p.src
	    self.aseq(p.src, shp[i].src)
	self.aseq(S, iso(ob, y))

	# Test that the iter can be restarted
	# even after multiple sources handling was added

	it = iter(shp)
	a = list(it)
	it.isatend = 0
	b = list(it)
	self.aseq( str(a),str(b))

	self.aseq( o.getvalue(), """\
 0: hpy().Root.i0_sysdict
 0: Src.i0_modules['sys'].__dict__
 0: hpy().Root.i0_sysdict
 0: hpy().Root.i0_sysdict
 0: Src[0][0][0]
 0: Src[0][0][0]
 0: Src[0]
 0: Src.x
 0: <1 list: <address>*1>[0]
 0: <1 list: <address>*1>[0]
 0: <1 list: <address>*1>[0]
 1: <1 __main__.O: <address>>.x
 0: <1 list: <address>*1>[0]
 1: <1 __main__.O: <address>>.x
""".replace('__main__', self.__module__))
	
    def test_2(self):
	# To assist interactivity,
	# the more attribute is defined to return an object which
	# the repr() of gives more lines; and has a similar more attribute.
	# Testing this functionality here.

	o = self.python.StringIO.StringIO()
	iso = self.iso
	dst = []
	src = [dst]*20
	print >>o, repr(iso(dst).get_shpaths(iso(src)))
	print >>o, repr(iso(dst).get_shpaths(iso(src)).more)
	p = iso(dst).get_shpaths(iso(src))
	print >>o, repr(p.more)

	self.aseq(o.getvalue(),"""\
 0: Src[0]
 1: Src[1]
 2: Src[2]
 3: Src[3]
 4: Src[4]
 5: Src[5]
 6: Src[6]
 7: Src[7]
 8: Src[8]
 9: Src[9]
<... 10 more paths ...>
10: Src[10]
11: Src[11]
12: Src[12]
13: Src[13]
14: Src[14]
15: Src[15]
16: Src[16]
17: Src[17]
18: Src[18]
19: Src[19]
10: Src[10]
11: Src[11]
12: Src[12]
13: Src[13]
14: Src[14]
15: Src[15]
16: Src[16]
17: Src[17]
18: Src[18]
19: Src[19]
""")

    def test_empty(self):
	# Test empty paths
	iso = self.iso
	dst = []
	self.assert_( len(list(iso(dst).get_shpaths(iso()))) == 0)

	

    def test_3(self):
	# Test that Edges is not included in the shortest path

	iso = self.iso
	dst = []
	shp = iso(dst).shpaths
	del dst
	self.assert_('Edges' not in str( shp.avoided(0) ))
	#print shp.avoided(0)

	dst = []

	src = [dst]

	shp = iso(dst).get_shpaths(iso(src))

	src[0] = shp
		      
	dst = iso(dst)
	src = iso(src)

	self.assert_( dst.get_shpaths(src).numpaths == 0)

	# Test the sets attribute

	dst = []
	src = [dst]
	dst = iso(dst)
	src = iso(src)
	self.aseq( dst.get_shpaths(src).sets, (src, dst))

	# Test that srs doesn't disturb the path calculation

	class C:
	    pass

	c = C()
	cd = iso(c.__dict__)

	p = cd.shpaths
	repr(p)

	del c
	q = cd.shpaths
	self.aseq( repr(q).strip(), "")

	del p, q

	# Test that internals of ShortestPath are hidden in general
	# (via hiding_env), to consistent result when used interactively,
	# as commented on in notes.txt per Nov 30 2004.

	dst = []
	src = [[[[dst]]]]

	d = iso(dst)
	s = iso(src)

	p = d.get_shpaths(s)
	self.aseq( str(p), " 0: Src[0][0][0][0]")
	src.append(p)
	p._XX_ = dst	# A shorter path, but it should be hidden
	self.aseq( str(d.get_shpaths(s)), " 0: Src[0][0][0][0]")
	
	# Test what .more prints finally

	self.aseq( str(p.more), '<No more paths>')

	# Test that .top is idempotent

	self.asis(p.more.top.top, p)


def run_test(case, debug=0):
    support.run_unittest(case, debug)

def test_main(debug=0):
    if 1:
	run_test(NewTestCase, debug)
    if 1:
	run_test(RelationTestCase, debug)
	run_test(RootTestCase, debug)
    if 1:
	run_test(PathTestCase, debug)
    if 1:
	run_test(MultiTestCase, debug)
	run_test(AvoidTestCase, debug)

if __name__ == "__main__":
    test_main()
