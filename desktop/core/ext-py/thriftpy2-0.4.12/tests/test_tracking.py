# -*- coding: utf-8 -*-
# flake8: disable E501

'''
Tests for contrib/tracking...

Compatibility Tests Table

============= ==================================== ======================================== ========================================
client/server native                               v2                                       v3
============= ==================================== ======================================== ========================================
native        N/A                                  test_native_client_tracked_server_v2     test_native_client_tracked_server_v3
v2            test_tracked_client_v2_native_server test_tracked_client_v2_tracked_server_v2 test_tracked_client_v2_tracked_server_v3
v3            test_tracked_client_v3_native_server test_tracked_client_v3_tracked_server_v2 regular tests
============= ==================================== ======================================== ========================================
'''  # noqa

from __future__ import absolute_import

import contextlib
import multiprocessing
import os
import pickle
import random
import socket
import tempfile
import time

import thriftpy2

try:
    import dbm
except ImportError:
    import dbm.ndbm as dbm

import pytest

from thriftpy2.contrib.tracking import TTrackedProcessor, TTrackedClient, \
    TrackerBase, track_thrift
from thriftpy2.contrib.tracking.tracker import ctx

from thriftpy2.thrift import TProcessorFactory, TClient, TProcessor
from thriftpy2.server import TThreadedServer
from thriftpy2.transport import TServerSocket, TBufferedTransportFactory, \
    TTransportException, TSocket
from thriftpy2.protocol import TBinaryProtocolFactory
from compatible.version_2.tracking import (
    TTrackedProcessor as TTrackedProcessorV2,
    TTrackedClient as TTrackedClientV2,
    TrackerBase as TrackerBaseV2,
)

try:
    from pytest_cov.embed import cleanup_on_sigterm
except ImportError:
    pass
else:
    cleanup_on_sigterm()

addressbook = thriftpy2.load(os.path.join(os.path.dirname(__file__),
                                          "addressbook.thrift"))
_, db_file = tempfile.mkstemp()


def _get_port():
    while True:
        port = 20000 + random.randint(1, 9999)
        for i in range(5):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                continue
        else:
            return port


PORT = _get_port()


class SampleTracker(TrackerBase):
    def record(self, header, exception):
        db = dbm.open(db_file, 'w')
        key = "%s:%s" % (header.request_id, header.seq)
        db[key.encode("ascii")] = pickle.dumps(header.__dict__)
        db.close()

    def handle_response_header(self, response_header):
        self.response_header = response_header

    def get_response_header(self):
        return getattr(self, 'response_header', None)


class Tracker_V2(TrackerBaseV2):
    def record(self, header, exception):
        db = dbm.open(db_file, 'w')
        key = "%s:%s" % (header.request_id, header.seq)
        db[key.encode("ascii")] = pickle.dumps(header.__dict__)
        db.close()


tracker = SampleTracker("test_client", "test_server")
tracker_v2 = Tracker_V2("test_client", "test_server")


class Dispatcher(object):
    def __init__(self):
        self.ab = addressbook.AddressBook()
        self.ab.people = {}

    def ping(self):
        test_response = {'ping': 'pong'}
        TrackerBase.add_response_meta(**test_response)
        return True

    def hello(self, name):
        # Add specially constructed response header for assertion.
        test_response = {name: name}
        TrackerBase.add_response_meta(**test_response)
        return "hello %s" % name

    def sleep(self, ms):
        return True

    def remove(self, name):
        person = addressbook.Person(name="mary")
        with client(port=PORT) as c:
            c.add(person)

        return True

    def get_phonenumbers(self, name, count):
        return [addressbook.PhoneNumber(number="sdaf"),
                addressbook.PhoneNumber(number='saf')]

    def add(self, person):
        with client(port=PORT + 1) as c:
            c.get_phonenumbers("jane", 1)

        with client(port=PORT + 1) as c:
            c.ping()
        return True

    def get(self, name):
        if not name:
            # undeclared exception
            raise ValueError('name cannot be empty')
        raise addressbook.PersonNotExistsError()


class TSampleServer(TThreadedServer):
    def __init__(self, processor_factory, trans, trans_factory, prot_factory):
        self.daemon = False
        self.processor_factory = processor_factory
        self.trans = trans

        self.itrans_factory = self.otrans_factory = trans_factory
        self.iprot_factory = self.oprot_factory = prot_factory
        self.closed = False

    def handle(self, client):
        processor = self.processor_factory.get_processor()
        itrans = self.itrans_factory.get_transport(client)
        otrans = self.otrans_factory.get_transport(client)
        iprot = self.iprot_factory.get_protocol(itrans)
        oprot = self.oprot_factory.get_protocol(otrans)
        try:
            while True:
                processor.process(iprot, oprot)
        except TTransportException:
            pass
        except Exception:
            raise
        finally:
            itrans.close()
            otrans.close()


def gen_server(port, tracker=tracker, processor=TTrackedProcessor):
    args = [processor, addressbook.AddressBookService, Dispatcher()]
    if tracker:
        args.insert(1, tracker)
    processor = TProcessorFactory(*args)
    server_socket = TServerSocket(host="localhost", port=port)
    server = TSampleServer(processor, server_socket,
                           prot_factory=TBinaryProtocolFactory(),
                           trans_factory=TBufferedTransportFactory())
    ps = multiprocessing.Process(target=server.serve)
    ps.start()
    return ps, server


@pytest.fixture(scope="module")
def server(request):
    ps, ser = gen_server(PORT)
    time.sleep(0.15)

    def fin():
        if ps.is_alive():
            ps.terminate()
            ps.join()

    request.addfinalizer(fin)
    return ser


@pytest.fixture(scope="module")
def server1(request):
    ps, ser = gen_server(PORT + 1)
    time.sleep(0.15)

    def fin():
        if ps.is_alive():
            ps.terminate()
            ps.join()

    request.addfinalizer(fin)
    return ser


@pytest.fixture(scope="module")
def server2(request):
    ps, ser = gen_server(PORT + 2)
    time.sleep(0.15)

    def fin():
        if ps.is_alive():
            ps.terminate()
            ps.join()

    request.addfinalizer(fin)
    return ser


@pytest.fixture(scope="module")
def native_server(request):
    ps, ser = gen_server(PORT + 3, tracker=None, processor=TProcessor)
    time.sleep(0.15)

    def fin():
        if ps.is_alive():
            ps.terminate()
            ps.join()

    request.addfinalizer(fin)
    return ser


@pytest.fixture(scope="module")
def tracked_server_v2(request):
    ps, ser = gen_server(PORT + 4, tracker=tracker_v2,
                         processor=TTrackedProcessorV2)
    time.sleep(0.15)

    def fin():
        if ps.is_alive():
            ps.terminate()
            ps.join()

    request.addfinalizer(fin)
    return ser


@contextlib.contextmanager
def client(client_class=TTrackedClient, port=PORT):
    socket = TSocket("localhost", port)

    try:
        trans = TBufferedTransportFactory().get_transport(socket)
        proto = TBinaryProtocolFactory().get_protocol(trans)
        trans.open()
        args = [addressbook.AddressBookService, proto]
        if client_class.__name__ == TTrackedClient.__name__:
            args.insert(0, SampleTracker("test_client", "test_server"))
        yield client_class(*args)
    finally:
        trans.close()


@pytest.fixture
def dbm_db(request):
    db = dbm.open(db_file, 'n')
    db.close()

    def fin():
        try:
            os.remove(db_file)
        except OSError:
            pass

    request.addfinalizer(fin)


@pytest.fixture
def tracker_ctx(request):
    def fin():
        if hasattr(ctx, "header"):
            del ctx.header
        if hasattr(ctx, "counter"):
            del ctx.counter
        if hasattr(ctx, "response_header"):
            del ctx.response_header

    request.addfinalizer(fin)


def test_negotiation(server):
    with client() as c:
        assert c.is_upgraded is True


def test_response_tracker(server, dbm_db, tracker_ctx):
    with client() as c:
        c.hello('you')
        assert c.tracker.response_header.meta == {'you': 'you'}
        c.hello('me')
        assert c.tracker.response_header.meta == {'me': 'me'}


def test_tracker(server, dbm_db, tracker_ctx):
    with client() as c:
        c.hello('you')
        assert c.tracker.response_header.meta == {'you': 'you'}

    time.sleep(0.2)

    db = dbm.open(db_file, 'r')
    headers = list(db.keys())
    assert len(headers) == 1

    request_id = headers[0]
    data = pickle.loads(db[request_id])

    assert "start" in data and "end" in data
    data.pop("start")
    data.pop("end")
    assert data == {
        "request_id": request_id.decode("ascii").split(':')[0],
        "seq": '1',
        "client": "test_client",
        "server": "test_server",
        "api": "hello",
        "status": True,
        "annotation": {},
        "meta": {},
    }


def test_tracker_chain(server, server1, server2, dbm_db, tracker_ctx):
    test_meta = {'test': 'test_meta'}
    with client() as c:
        with SampleTracker.add_meta(**test_meta):
            c.remove("jane")
            c.hello("yes")

    time.sleep(0.2)

    db = dbm.open(db_file, 'r')
    headers = list(db.keys())
    assert len(headers) == 5

    headers = [pickle.loads(db[i]) for i in headers]
    headers.sort(key=lambda x: x["seq"])

    assert len(set([i["request_id"] for i in headers])) == 2

    seqs = [i["seq"] for i in headers]
    metas = [i["meta"] for i in headers]
    assert seqs == ['1', '1.1', '1.1.1', '1.1.2', '2']
    assert metas == [test_meta] * 5


def test_exception(server, dbm_db, tracker_ctx):
    with pytest.raises(addressbook.PersonNotExistsError):
        with client() as c:
            c.get("jane")

    db = dbm.open(db_file, 'r')
    headers = list(db.keys())
    assert len(headers) == 1

    header = pickle.loads(db[headers[0]])
    assert header["status"] is False


def test_undeclared_exception(server, dbm_db, tracker_ctx):
    with pytest.raises(TTransportException):
        with client() as c:
            c.get('')


def test_request_id_func():
    ctx.__dict__.clear()

    header = track_thrift.RequestHeader()
    header.request_id = "hello"
    header.seq = 0

    tracker = TrackerBase()
    tracker.handle(header)

    header2 = track_thrift.RequestHeader()
    tracker.gen_header(header2)
    assert header2.request_id == "hello"


def test_annotation(server, dbm_db, tracker_ctx):
    with client() as c:
        with SampleTracker.annotate(ann="value"):
            c.ping()

        with SampleTracker.annotate() as ann:
            ann.update({"sig": "c.hello()", "user_id": "125"})
            c.hello('you')

    time.sleep(0.2)

    db = dbm.open(db_file, 'r')
    headers = list(db.keys())

    data = [pickle.loads(db[i]) for i in headers]
    data.sort(key=lambda x: x["seq"])

    assert data[0]["annotation"] == {"ann": "value"} and \
        data[1]["annotation"] == {"sig": "c.hello()", "user_id": "125"}


def test_counter(server, dbm_db, tracker_ctx):
    with client() as c:
        c.get_phonenumbers("hello", 1)

        with SampleTracker.counter():
            c.ping()
            c.hello("counter")

        c.sleep(8)

    time.sleep(0.2)

    db = dbm.open(db_file, 'r')
    headers = list(db.keys())

    data = [pickle.loads(db[i]) for i in headers]
    data.sort(key=lambda x: x["api"])
    get, hello, ping, sleep = data

    assert get["api"] == "get_phonenumbers" and get["seq"] == '1'
    assert ping["api"] == "ping" and ping["seq"] == '1'
    assert hello["api"] == "hello" and hello["seq"] == '2'
    assert sleep["api"] == "sleep" and sleep["seq"] == '2'


def test_native_client_tracked_server_v3(server):
    with client(TClient) as c:
        c.ping()
        c.hello("world")


def test_native_client_tracked_server_v2(tracked_server_v2):
    with client(TClient, port=PORT + 4) as c:
        c.ping()
        c.hello("world")


def test_tracked_client_v2_native_server(native_server):
    with client(TTrackedClientV2, PORT + 3) as c:
        assert c._upgraded is False
        c.ping()
        c.hello("cat")
        a = c.get_phonenumbers("hello", 54)
        assert len(a) == 2
        assert a[0].number == 'sdaf' and a[1].number == 'saf'


def test_tracked_client_v2_tracked_server_v2(
        tracked_server_v2, dbm_db, tracker_ctx):
    with client(TTrackedClientV2, PORT + 4) as c:
        assert c._upgraded is True

        c.ping()
        time.sleep(0.2)

        db = dbm.open(db_file, 'r')
        headers = list(db.keys())
        assert len(headers) == 1

        request_id = headers[0]
        data = pickle.loads(db[request_id])

        assert "start" in data and "end" in data
        data.pop("start")
        data.pop("end")
        assert data == {
            "request_id": request_id.decode("ascii").split(':')[0],
            "seq": '1',
            "client": "test_client",
            "server": "test_server",
            "api": "ping",
            "status": True,
            "annotation": {},
            "meta": {},
        }


def test_tracked_client_v2_tracked_server_v3(server, dbm_db, tracker_ctx):
    with client(TTrackedClientV2) as c:
        assert c._upgraded is True

        c.ping()
        time.sleep(0.2)

        db = dbm.open(db_file, 'r')
        headers = list(db.keys())
        assert len(headers) == 1

        request_id = headers[0]
        data = pickle.loads(db[request_id])

        assert "start" in data and "end" in data
        data.pop("start")
        data.pop("end")
        assert data == {
            "request_id": request_id.decode("ascii").split(':')[0],
            "seq": '1',
            "client": "test_client",
            "server": "test_server",
            "api": "ping",
            "status": True,
            "annotation": {},
            "meta": {},
        }

        assert not hasattr(ctx, 'response_header')


def test_tracked_client_v3_native_server(native_server):
    with client(port=PORT + 3) as c:
        assert c.is_upgraded is False
        c.ping()
        assert not hasattr(ctx, "response_header")

        c.hello("cat")
        a = c.get_phonenumbers("hello", 54)
        assert len(a) == 2
        assert a[0].number == 'sdaf' and a[1].number == 'saf'


def test_tracked_client_v3_tracked_server_v2(
        tracked_server_v2, dbm_db, tracker_ctx):
    with client(port=PORT + 4) as c:
        assert c.is_upgraded is True

        c.ping()
        assert not hasattr(ctx, "response_header")
        assert c.tracker.get_response_header() is None

        time.sleep(0.2)

        db = dbm.open(db_file, 'r')
        headers = list(db.keys())
        assert len(headers) == 1

        request_id = headers[0]
        data = pickle.loads(db[request_id])

        assert "start" in data and "end" in data
        data.pop("start")
        data.pop("end")
        assert data == {
            "request_id": request_id.decode("ascii").split(':')[0],
            "seq": '1',
            "client": "test_client",
            "server": "test_server",
            "api": "ping",
            "status": True,
            "annotation": {},
            "meta": {},
        }
