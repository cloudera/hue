from guppy.heapy.test import support

class FirstCase(support.TestCase):
    def setUp(self):
	support.TestCase.setUp(self)
	self.OH = self.heapy.OutputHandling
    
    def test_1(self):
	class T:
	    def __init__(self, test, numlines, get_num_lines=None, get_more_msg=None):
		mod = test.OH

		def get_line_iter():
		    for i in range(numlines):
			yield '%d'%i

		self.mod = mod
		self.more = mod.more_printer(
		    self,
		    get_line_iter = get_line_iter,
		    max_top_lines = 4,
		    max_more_lines = 3,
		    get_num_lines = get_num_lines,
		    get_more_msg=get_more_msg)

	    def __str__(self):
		return self.more._oh_printer.get_str_of_top()

	self.aseq(str( T(self, 4) ), '0\n1\n2\n3')

	t = T(self,6, lambda :6)

	self.aseq(str(t), "0\n1\n2\n3\n<Lines 0..3 of 6. Type e.g. '_.more' for more.>")
	x = t.more
	self.aseq(str(x), '4\n5')
	self.aseq(str(x.top), "0\n1\n2\n3\n<Lines 0..3 of 6. Type e.g. '_.more' for more.>")

	t = T(self,6, get_more_msg = lambda f, t: '<%d more rows>'%(6-t))
	self.aseq(str(t), '0\n1\n2\n3\n<3 more rows>')


def test_main(debug = 0):
    support.run_unittest(FirstCase, debug)

if __name__ == "__main__":
    test_main()
