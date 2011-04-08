from twisted.internet import reactor
from twisted.names.srvconnect import SRVConnector
from gnutls.interfaces.twisted import X509Credentials

from eventlet.twistedutil.protocol import GreenClientCreator
from eventlet.twistedutil.protocols.basic import LineOnlyReceiverTransport

class NoisySRVConnector(SRVConnector):

    def pickServer(self):
        host, port = SRVConnector.pickServer(self)
        print 'Resolved _%s._%s.%s --> %s:%s' % (self.service, self.protocol, self.domain, host, port)
        return host, port

cred = X509Credentials(None, None)
creator = GreenClientCreator(reactor, LineOnlyReceiverTransport)
conn = creator.connectSRV('msrps', 'ag-projects.com',
                          connectFuncName='connectTLS', connectFuncArgs=(cred,),
                          ConnectorClass=NoisySRVConnector)

request = """MSRP 49fh AUTH
To-Path: msrps://alice@intra.example.com;tcp
From-Path: msrps://alice.example.com:9892/98cjs;tcp
-------49fh$
""".replace('\n', '\r\n')

print 'Sending:\n%s' % request
conn.write(request)
print 'Received:'
for x in conn:
    print repr(x)
    if '-------' in x:
        break
