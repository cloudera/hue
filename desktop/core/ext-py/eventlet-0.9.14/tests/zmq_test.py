from eventlet import event, spawn, sleep, patcher
from eventlet.hubs import get_hub, _threadlocal, use_hub
from nose.tools import *
from tests import mock, LimitedTestCase, skip_unless_zmq
from unittest import TestCase

from threading import Thread
try:
    from eventlet.green import zmq
    from eventlet.hubs.zeromq import Hub
except ImportError:
    zmq = None
    Hub = None


class TestUpstreamDownStream(LimitedTestCase):

    sockets = []

    def tearDown(self):
        self.clear_up_sockets()
        super(TestUpstreamDownStream, self).tearDown()

    def create_bound_pair(self, type1, type2, interface='tcp://127.0.0.1'):
        """Create a bound socket pair using a random port."""
        self.context = context = zmq.Context()
        s1 = context.socket(type1)
        port = s1.bind_to_random_port(interface)
        s2 = context.socket(type2)
        s2.connect('%s:%s' % (interface, port))
        self.sockets = [s1, s2]
        return s1, s2, port

    def clear_up_sockets(self):
        for sock in self.sockets:
            sock.close()

    def assertRaisesErrno(self, errno, func, *args):
        try:
            func(*args)
        except zmq.ZMQError, e:
            self.assertEqual(e.errno, errno, "wrong error raised, expected '%s' \
got '%s'" % (zmq.ZMQError(errno), zmq.ZMQError(e.errno)))
        else:
            self.fail("Function did not raise any error")

    @skip_unless_zmq
    def test_recv_spawned_before_send_is_non_blocking(self):
        req, rep, port = self.create_bound_pair(zmq.PAIR, zmq.PAIR)
#        req.connect(ipc)
#        rep.bind(ipc)
        sleep()
        msg = dict(res=None)
        done = event.Event()

        def rx():
            msg['res'] = rep.recv()
            done.send('done')

        spawn(rx)
        req.send('test')
        done.wait()
        self.assertEqual(msg['res'], 'test')

    @skip_unless_zmq
    def test_close_socket_raises_enotsup(self):
        req, rep, port = self.create_bound_pair(zmq.PAIR, zmq.PAIR)

        rep.close()
        req.close()
        self.assertRaisesErrno(zmq.ENOTSUP, rep.recv)
        self.assertRaisesErrno(zmq.ENOTSUP, req.send, 'test')

    @skip_unless_zmq
    def test_send_1k_req_rep(self):
        req, rep, port = self.create_bound_pair(zmq.REQ, zmq.REP)
        sleep()
        done = event.Event()

        def tx():
            tx_i = 0
            req.send(str(tx_i))
            while req.recv() != 'done':
                tx_i += 1
                req.send(str(tx_i))

        def rx():
            while True:
                rx_i = rep.recv()
                if rx_i == "1000":
                    rep.send('done')
                    sleep()
                    done.send(0)
                    break
                rep.send('i')
        spawn(tx)
        spawn(rx)
        final_i = done.wait()
        self.assertEqual(final_i, 0)

    @skip_unless_zmq
    def test_send_1k_push_pull(self):
        down, up, port = self.create_bound_pair(zmq.PUSH, zmq.PULL)
        sleep()

        done = event.Event()

        def tx():
            tx_i = 0
            while tx_i <= 1000:
                tx_i += 1
                down.send(str(tx_i))

        def rx():
            while True:
                rx_i = up.recv()
                if rx_i == "1000":
                    done.send(0)
                    break
        spawn(tx)
        spawn(rx)
        final_i = done.wait()
        self.assertEqual(final_i, 0)

    @skip_unless_zmq
    def test_send_1k_pub_sub(self):
        pub, sub_all, port = self.create_bound_pair(zmq.PUB, zmq.SUB)
        sub1 = self.context.socket(zmq.SUB)
        sub2 = self.context.socket(zmq.SUB)
        self.sockets.extend([sub1, sub2])
        addr = 'tcp://127.0.0.1:%s' % port
        sub1.connect(addr)
        sub2.connect(addr)
        sub_all.setsockopt(zmq.SUBSCRIBE, '')
        sub1.setsockopt(zmq.SUBSCRIBE, 'sub1')
        sub2.setsockopt(zmq.SUBSCRIBE, 'sub2')

        sub_all_done = event.Event()
        sub1_done = event.Event()
        sub2_done = event.Event()

        sleep(0.2)

        def rx(sock, done_evt, msg_count=10000):
            count = 0
            while count < msg_count:
                msg = sock.recv()
                sleep()
                if 'LAST' in msg:
                    break
                count += 1

            done_evt.send(count)

        def tx(sock):
            for i in range(1, 1001):
                msg = "sub%s %s" % ([2,1][i % 2], i)
                sock.send(msg)
                sleep()
            sock.send('sub1 LAST')
            sock.send('sub2 LAST')

        spawn(rx, sub_all, sub_all_done)
        spawn(rx, sub1, sub1_done)
        spawn(rx, sub2, sub2_done)
        spawn(tx, pub)
        sub1_count = sub1_done.wait()
        sub2_count = sub2_done.wait()
        sub_all_count = sub_all_done.wait()
        self.assertEqual(sub1_count, 500)
        self.assertEqual(sub2_count, 500)
        self.assertEqual(sub_all_count, 1000)

    @skip_unless_zmq
    def test_change_subscription(self):
        pub, sub, port = self.create_bound_pair(zmq.PUB, zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, 'test')

        sleep(0.2)
        sub_done = event.Event()

        def rx(sock, done_evt):
            count = 0
            sub = 'test'
            while True:
                msg = sock.recv()
                sleep()
                if 'DONE' in msg:
                    break
                if 'LAST' in msg and sub == 'test':
                    sock.setsockopt(zmq.UNSUBSCRIBE, 'test')
                    sock.setsockopt(zmq.SUBSCRIBE, 'done')
                    sub = 'done'
                count += 1
            done_evt.send(count)

        def tx(sock):
            for i in range(1, 101):
                msg = "test %s" % i
                if i != 50:
                    sock.send(msg)
                else:
                    sock.send('test LAST')
                sleep()
            sock.send('done DONE')

        spawn(rx, sub, sub_done)
        spawn(tx, pub)

        rx_count = sub_done.wait()
        self.assertEqual(rx_count, 50)

    @skip_unless_zmq
    def test_recv_multipart_bug68(self):
        req, rep, port = self.create_bound_pair(zmq.REQ, zmq.REP)
        msg = ['']
        req.send_multipart(msg)
        recieved_msg = rep.recv_multipart()
        self.assertEqual(recieved_msg, msg)

        # Send a message back the other way
        msg2 = [""]
        rep.send_multipart(msg2, copy=False)
        # When receiving a copy it's a zmq.core.message.Message you get back
        recieved_msg = req.recv_multipart(copy=False)
        # So it needs to be converted to a string
        # I'm calling str(m) consciously here; Message has a .data attribute
        # but it's private __str__ appears to be the way to go
        self.assertEqual([str(m) for m in recieved_msg], msg2)


class TestThreadedContextAccess(TestCase):
    """zmq's Context must be unique within a hub

    The zeromq API documentation states:
    All zmq sockets passed to the zmq_poll() function must share the same zmq
    context and must belong to the thread calling zmq_poll()

    As zmq_poll is what's eventually being called then we need to ensure that
    all sockets that are going to be passed to zmq_poll (via hub.do_poll) are
    in the same context
    """
    if zmq:  # don't call decorators if zmq module unavailable
        @skip_unless_zmq
        @mock.patch('eventlet.green.zmq.get_hub_name_from_instance')
        @mock.patch('eventlet.green.zmq.get_hub', spec=Hub)
        def test_context_factory_funtion(self, get_hub_mock, hub_name_mock):
            hub_name_mock.return_value = 'zeromq'
            ctx = zmq.Context()
            self.assertTrue(get_hub_mock().get_context.called)

        @skip_unless_zmq
        def test_threadlocal_context(self):
            hub = get_hub()
            context = zmq.Context()
            self.assertEqual(context, _threadlocal.context)
            next_context = hub.get_context()
            self.assertTrue(context is next_context)

        @skip_unless_zmq
        def test_different_context_in_different_thread(self):
            context = zmq.Context()
            test_result = []
            def assert_different(ctx):
                hub = get_hub()
                try:
                    this_thread_context = zmq.Context()
                except:
                    test_result.append('fail')
                    raise
                test_result.append(ctx is this_thread_context)
            Thread(target=assert_different, args=(context,)).start()
            while not test_result:
                sleep(0.1)
            self.assertFalse(test_result[0])


class TestCheckingForZMQHub(TestCase):

    @skip_unless_zmq
    def setUp(self):
        self.orig_hub = zmq.get_hub_name_from_instance(get_hub())
        use_hub('selects')

    def tearDown(self):
        use_hub(self.orig_hub)

    def test_assertionerror_raise_by_context(self):
        self.assertRaises(RuntimeError, zmq.Context)





