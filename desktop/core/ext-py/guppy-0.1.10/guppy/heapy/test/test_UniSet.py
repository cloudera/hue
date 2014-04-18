from guppy.heapy.test import support
class FirstCase(support.TestCase):
    def setUp(self):
	support.TestCase.setUp(self)

    def test_1(self):
	asrt = self.assert_
	a = []
	b = []
	c = self.iso(a, b)
	asrt( len(c.nodes) == 2)
	asrt( a in c )
	asrt( b in c )
	asrt( [] not in c )
	asrt( c not in c )

	d = self.idset(c.nodes)

	asrt( c.nodes == d.nodes )

	asrt( c == d )

    def test_2(self):
	# Test standard set operations
	H = self.idset
	e1 = []
	e2 = {}
	e3 = ()
	la = [], [e1], [e1, e2], [e1, e2, e3], [e2], [e2, e3], [e3]
	self.guppy.sets.test.test_set_operations(
	    [H(x) for x in la], [H(x) for x in la], [H(x) for x in la])

    def test_3(self):
	# Test out-reaching
	
	iso = self.iso

	a = []
	b = [a]
	c = [b]
	self.View.root =  c 

	x = iso(b)

	self.assert_( x.referrers == iso(c))
	self.aseq( x.referents,  iso(a))
	self.aseq( x.referents.referrers,  x)
	self.aseq( x.dominos, iso(a, b))



def test_main(debug=False):
    support.run_unittest(FirstCase,debug)

if __name__ == "__main__":
    test_main()
    
