from guppy.heapy.test import support
class TestCase(support.TestCase):
    def setUp(self):
	support.TestCase.setUp(self)
	self.types = self.heapy.UniSet.types

class FirstCase(TestCase):
    def test_cal_hiding(self):
	V = self.View
	iso = self.iso

	# Tests that our workspace nodesets are hidden. 

	a = []
	b = []
	as_ = iso(a)
	bs = iso(b)
	ab = as_ | bs
	# Make sure hiding is carried on with set operations
	self.assert_(ab.referrers.kind == self.types.FrameType)
	self.assert_((as_ | bs).referrers.kind == self.types.FrameType)
	self.assert_(V.referrers(iso(a)).kind == self.types.FrameType)
	self.assert_(V.referrers(iso(b)).kind == self.types.FrameType)

	# Test that we can still see nodesets created with other hiding_tag

	c = []
	chold = self.guppy.sets.immnodeset(
	    [c],
	    hiding_tag = []	# Make sure we see it whether or not View uses default or not
	    )
	cs = iso(c)
	del c

	self.assert_(cs.referrers.kind == type(self.guppy.sets.immnodeset()))

    def test_dominos(self):
	# Test dominos and domisize
	iso = self.iso
	x = []
	y = [x, []]
	z = [y]
	self.aseq(iso(y).dominos, iso(y, y[1]))
	self.aseq(iso(y).domisize, iso(y, y[1]).indisize)
	self.aseq(iso(z).dominos, iso(z))
	del y
	self.aseq(iso(z).dominos, iso(z, z[0], z[0][1]))

    def test_exports(self):
	# Test a few exports; the other defined in _unp_exports use the same mechanism
	iso = self.iso
	x = []
	y = [x, []]
	z = [y]
	p = iso(z).referents.indisize
	self.aseq(p, iso(y).indisize)

    def test_horizon(self):
	iso = self.iso
	h = self.View.horizon()
	x = []
	hn = h.news()
	self.aseq(hn, iso(x))
	del hn
	hn = h.news()
	self.aseq(hn, iso(x))
	del x, hn
	hn = h.news()
	self.aseq(hn, iso())

    def test_imdom(self):
	iso = self.iso
	x = []
	y = [x, []]
	z = [x, y]
	del x, y
	self.aseq(iso(z[0]).imdom, iso(z))

    def test_referents(self):
	iso = self.iso
	x = []
	y = [x, []]
	z = [y]
	self.aseq( iso(x).referents, iso())
	self.aseq( iso(y).referents, iso(x, y[1]))
	self.aseq( iso(z).referents, iso(y))
	self.aseq( iso(y, z).referents, iso(x, y, y[1]))

        


class GCCase(TestCase):
    def test_gc_mechanism(self):
	# Test the underlying GC system for having the properties that
	# support the method of automatic reclamation of nodegraphs
	# that is relied on in other tests. Failure here, dependent on
	# changed GC behaviour, would explain the other failures.

	from weakref import ref
	import gc
	class C:
	    pass

	c = C()
	cbs = []
	def cb(wr):
	    cbs.append(wr)

	wr = ref(c, cb)

	c.x = c
	gc.collect()
	strc = str(c)
	self.aseq(str(wr()), strc)
	self.asis(wr(), c)
	c=None
	self.aseq(str(wr()), strc)
	self.aseq(cbs, [])
	gc.collect()
	self.asis(wr(), None)
	self.aseq(cbs, [wr])
    
    def test_gc_hook(self):
	# Test the GC hook as implemented in View

	hos = []
	def ho():
	    hos.append(1)
	    
	import gc
	gc.collect()
	hook = self.heapy.View.gchook(ho)
	self.aseq(hos, [])
	gc.collect()
	self.aseq(hos, [1])
	hook = None
	gc.collect()
	self.aseq(hos, [1])

    def test_gc_drg(self):
	# Test automatic reclamation issues for dict owner nodegraph
	# This mechanism changed so the old test here is
	# not valid anymore
	# XXX MAKE NEW TEST
	return

	import gc
	View = self.View
	hv = View.hv
	drg = View.nodegraph()
	def clear_drg():
	    if drg.is_sorted:
		#print 'yes'
		drg.clear()
	    else:
		#print 'no'
		pass
	_clear_drg_hook = View.gchook(clear_drg)

	hv.update_dictowners(drg)
	gc.collect()
	lendrg = len(drg)
	self.assert_(lendrg > 0)    # Before any use, it will not be cleared
	# Now it is used by taking its length
	gc.collect()
	self.aseq(len(drg), 0)
	
	byclodo = hv.cli_clodo(drg, {})

	class C:
	    pass
	c=C()

	byclodo.partition([c.__dict__])
	self.assert_(len(drg) > 0)
	gc.collect()
	self.assert_(len(drg) == 0)

    def test_gc_rg(self):
	# Test automatic reclamation issues for referrer nodegraph
	iso = self.iso
	immnodeset = self.guppy.sets.immnodeset
	self.View.is_rg_update_all = False
	import gc
	
	gc.collect()

	dst = []

	gc.collect()
	self.assert_( len(self.View.rg) == 0)

	# Test that rg is automatically updated with the set target(s)
	
	a = [dst]
	b = [dst]
	c = [a, b]

	class T:
	    def __init__(self, set):
		self.set = set

	ta = T(iso(a))
	self.View.referrers_add_target(ta)
	tb = T(iso(b))
	self.View.referrers_add_target(tb)

	self.View.referrers(iso(c))
	self.assert_(c in immnodeset(self.View.rg[a]))
	self.assert_(c in immnodeset(self.View.rg[b]))

	# Test that a referrers target is automatically collected when not referenced

	tb = None
	gc.collect()
	self.View.referrers(iso(c))
	self.assert_(c in immnodeset(self.View.rg[a]))
	self.assert_(c not in immnodeset(self.View.rg[b]))
	
	# Test that adding a source automatically updates rg
	# even though domain of rg already includes its target
	# This requires gc collection

	d = [c]
	self.assert_(d not in self.View.referrers(iso(c)))
	gc.collect()
	self.assert_(d in self.View.referrers(iso(c)))


class AltHeapCase(TestCase):
    # Tests for support of alternative heap as implemented around 27 Oct 2005
    # and discussed in Notes at that time.

    def test_observation_containers(self):
	# Test the View.observation_containers method

	iso = self.iso
	idset = self.idset

	# These are to be included
	a = iso([],{})
	b = self.ImpSet.mutnodeset()
	c = self.View.observation_list()

	# These are not to be included - have another hiding tag

	excla = self.guppy.sets.mutnodeset()
	exclb = self.guppy.sets.immnodeset()

	# Get possible containers

	oc = idset(self.View.observation_containers())
	# print oc

	self.assert_( iso(a.nodes, b, c) <= oc )
	self.assert_( not (iso(excla, exclb) & oc) )


class SpecialTypesCase(TestCase):
    # Some tests for special types

    def test_array(self):
        iso = self.iso
        import array
        a=array.array('b','asdf')
        iso(a).size



def test_main(debug = 0):
    from guppy.heapy.Remote import off; off()
    support.run_unittest(FirstCase, debug)
    support.run_unittest(GCCase, debug)
    support.run_unittest(AltHeapCase, debug)
    support.run_unittest(SpecialTypesCase, debug)

if __name__ == "__main__":
    test_main()

