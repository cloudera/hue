from tests import requires_twisted
import unittest
try:
    from twisted.internet import reactor
    from twisted.internet.error import DNSLookupError
    from twisted.internet import defer
    from twisted.python.failure import Failure
    from eventlet.twistedutil import block_on
except ImportError:
    pass

class Test(unittest.TestCase):
    @requires_twisted
    def test_block_on_success(self):
        from twisted.internet import reactor
        d = reactor.resolver.getHostByName('www.google.com')
        ip = block_on(d)
        assert len(ip.split('.'))==4, ip
        ip2 = block_on(d)
        assert ip == ip2, (ip, ip2)

    @requires_twisted 
    def test_block_on_fail(self):
        from twisted.internet import reactor
        d = reactor.resolver.getHostByName('xxx')
        self.assertRaises(DNSLookupError, block_on, d)

    @requires_twisted 
    def test_block_on_already_succeed(self):
        d = defer.succeed('hey corotwine')
        res = block_on(d)
        assert res == 'hey corotwine', repr(res)

    @requires_twisted
    def test_block_on_already_failed(self):
        d = defer.fail(Failure(ZeroDivisionError()))
        self.assertRaises(ZeroDivisionError, block_on, d)

if __name__=='__main__':
    unittest.main()

