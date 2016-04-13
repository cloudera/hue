from guppy.heapy.test import support

class IdentityCase(support.TestCase):
    def test_1(self):
	import random
	vs = range(100)
	random.shuffle(vs)
	vs = [float(i) for i in vs]
	x = self.iso(*vs).byid
	if self.allocation_behaves_as_originally:
	    self.aseq(str(x)+'\n'+str(x.more)+'\n', """\
Set of 100 <float> objects. Total size = 1600 bytes.
 Index     Size   %   Cumulative  %   Value
     0       16   1.0        16   1.0 0.0
     1       16   1.0        32   2.0 1.0
     2       16   1.0        48   3.0 2.0
     3       16   1.0        64   4.0 3.0
     4       16   1.0        80   5.0 4.0
     5       16   1.0        96   6.0 5.0
     6       16   1.0       112   7.0 6.0
     7       16   1.0       128   8.0 7.0
     8       16   1.0       144   9.0 8.0
     9       16   1.0       160  10.0 9.0
<90 more rows. Type e.g. '_.more' to view.>
 Index     Size   %   Cumulative  %   Value
    10       16   1.0       176  11.0 10.0
    11       16   1.0       192  12.0 11.0
    12       16   1.0       208  13.0 12.0
    13       16   1.0       224  14.0 13.0
    14       16   1.0       240  15.0 14.0
    15       16   1.0       256  16.0 15.0
    16       16   1.0       272  17.0 16.0
    17       16   1.0       288  18.0 17.0
    18       16   1.0       304  19.0 18.0
    19       16   1.0       320  20.0 19.0
<80 more rows. Type e.g. '_.more' to view.>
""")	

    def test_2(self):
	# Slicing
	ss = []
	for i in range(100):
	    for c in 'abc':
		ss.append(c*i)
	x = self.iso(*ss).byid

	def ae(x):
	    lines = str(x).split('\n')
	    datapos = lines[1].index('Representation')
	    s = lines [2:]
	    if s[-1].startswith('<'):
		s.pop()
	    s = [line[datapos:] for line in s]
	    #print s
	    return s

	def aeq(x, y):
	    self.aseq(ae(x), ae(y))

	#print x
	#print x[100:]
	#print x[100:].byid
	for i in range(0, 300, 60):
	    b = x[i:]
	    aeq(b, b.byid)
	
	# (B) in  Notes Aug 26 2005
		       
	self.aseq( x.bysize[2].kind, x.bysize[2].bysize.kind )

    def test_3(self):
	# Some indexing cases.
	# Came up Sep 29 2005.
	# The kind of the result of indexing is to be
	# the result of the er of the partition.

	hp = self.Use

	x=hp.iso([],[],*range(20)).byid

	eq = [x[-10], x[-10:-9], x[12], x[12:13],
	      x.parts[-10], x.parts[12]]
	k = x[-10].byid.kind
	for i in range(len(eq)):
	    self.aseq(eq[i], eq[(i + 1) %len(eq)])
	    self.aseq(eq[i].kind, eq[(i + 1)%len(eq)].kind)
	    self.aseq(eq[i].kind, k)

class MixedCase(support.TestCase):
    def test_1(self):
        import sys
	x = self.iso(1, 2, 1.0, 2.0, '1', '2')
	if self.allocation_behaves_as_originally:
            if sys.version < '2.7':
                self.aseq(str(x), """\
Partition of a set of 6 objects. Total size = 112 bytes.
 Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
     0      2  33       56  50        56  50 str
     1      2  33       32  29        88  79 float
     2      2  33       24  21       112 100 int""")
            else:
                self.aseq(str(x), """\
Partition of a set of 6 objects. Total size = 104 bytes.
 Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
     0      2  33       48  46        48  46 str
     1      2  33       32  31        80  77 float
     2      2  33       24  23       104 100 int""")
                
	for row in x.partition.get_rows():
	    self.assert_(row.set <= row.kind)
	 

class StatCase(support.TestCase):
    def test_1(self):
	hp = self.Use

	class C:
	    pass
	c0 = C()
	class C:
	    pass
	c1 = C()
	x = hp.iso(c0, c1)
	y = hp.iso(c1)

	d = x.diff(y)
	self.aseq(d.count, 1)
	self.aseq(d[0].count, 1)
	#print d
	d = y.diff(x)
	self.aseq(d.count, -1)
	self.aseq(d[0].count, -1)
	#print d

	d = x.diff(hp.iso())
	self.aseq(d.count, 2)
	self.aseq(d[0].count, 2)
	#print d

	d = hp.iso().diff(x)
	self.aseq(d.count, -2)
	self.aseq(d[0].count, -2)
	#print d


def test_main(debug = 0):
    support.run_unittest(StatCase, debug)
    support.run_unittest(IdentityCase, debug)
    support.run_unittest(MixedCase, debug)


if __name__ == "__main__":
    test_main()
