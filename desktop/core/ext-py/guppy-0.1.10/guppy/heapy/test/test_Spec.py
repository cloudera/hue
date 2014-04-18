from guppy.heapy.test import support
import sys, unittest

class TestCase(support.TestCase):
    pass

class FirstCase(TestCase):
    def test_1(self):
	Spec = self.heapy.Spec
	TestEnv = Spec.mkTestEnv(Spec._Specification_)
	#print SpecSpec.getstr(1000)


	TestEnv.test_contains(Spec)


if __name__ == "__main__":
    support.run_unittest(FirstCase, 1)
    
