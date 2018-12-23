import contextlib

try:
    from eventlet.green import zmq
except ImportError:
    zmq = {}    # for systems lacking zmq, skips tests instead of barfing
else:
    RECV_ON_CLOSED_SOCKET_ERRNOS = (zmq.ENOTSUP, zmq.ENOTSOCK)

import eventlet
import tests


def zmq_supported(_):
    try:
        import zmq
    except ImportError:
        return False
    return not tests.using_pyevent(_)


class TestUpstreamDownStream(tests.LimitedTestCase):
    TEST_TIMEOUT = 2

    @tests.skip_unless(zmq_supported)
    def setUp(self):
        super(TestUpstreamDownStream, self).setUp()
        self.context = zmq.Context()
        self.sockets = []

    @tests.skip_unless(zmq_supported)
    def tearDown(self):
        self.clear_up_sockets()
        super(TestUpstreamDownStream, self).tearDown()

    def create_bound_pair(self, type1, type2, interface='tcp://127.0.0.1'):
        """Create a bound socket pair using a random port."""
        s1 = self.context.socket(type1)
        port = s1.bind_to_random_port(interface)
        s2 = self.context.socket(type2)
        s2.connect('%s:%s' % (interface, port))
        self.sockets.append(s1)
        self.sockets.append(s2)
        return s1, s2, port

    def clear_up_sockets(self):
        for sock in self.sockets:
            sock.close()
        self.sockets = None
        self.context.destroy(0)

    def assertRaisesErrno(self, errnos, func, *args):
        try:
            func(*args)
        except zmq.ZMQError as e:
            if not hasattr(errnos, '__iter__'):
                errnos = (errnos,)

            if e.errno not in errnos:
                raise AssertionError(
                    "wrong error raised, expected one of ['%s'], got '%s'" % (
                        ", ".join("%s" % zmq.ZMQError(errno) for errno in errnos),
                        zmq.ZMQError(e.errno)
                    ),
                )
        else:
            self.fail("Function did not raise any error")

    @tests.skip_unless(zmq_supported)
    def test_close_linger(self):
        """Socket.close() must support linger argument.

        https://github.com/eventlet/eventlet/issues/9
        """
        sock1, sock2, _ = self.create_bound_pair(zmq.PAIR, zmq.PAIR)
        sock1.close(1)
        sock2.close(linger=0)

    @tests.skip_unless(zmq_supported)
    def test_recv_spawned_before_send_is_non_blocking(self):
        req, rep, port = self.create_bound_pair(zmq.PAIR, zmq.PAIR)
#       req.connect(ipc)
#       rep.bind(ipc)
        eventlet.sleep()
        msg = dict(res=None)
        done = eventlet.Event()

        def rx():
            msg['res'] = rep.recv()
            done.send('done')

        eventlet.spawn(rx)
        req.send(b'test')
        done.wait()
        self.assertEqual(msg['res'], b'test')

    @tests.skip_unless(zmq_supported)
    def test_close_socket_raises_enotsup(self):
        req, rep, port = self.create_bound_pair(zmq.PAIR, zmq.PAIR)

        rep.close()
        req.close()
        self.assertRaisesErrno(RECV_ON_CLOSED_SOCKET_ERRNOS, rep.recv)
        self.assertRaisesErrno(RECV_ON_CLOSED_SOCKET_ERRNOS, req.send, b'test')

    @tests.skip_unless(zmq_supported)
    def test_close_xsocket_raises_enotsup(self):
        req, rep, port = self.create_bound_pair(zmq.XREQ, zmq.XREP)

        rep.close()
        req.close()
        self.assertRaisesErrno(RECV_ON_CLOSED_SOCKET_ERRNOS, rep.recv)
        self.assertRaisesErrno(RECV_ON_CLOSED_SOCKET_ERRNOS, req.send, b'test')

    @tests.skip_unless(zmq_supported)
    def test_send_1k_req_rep(self):
        req, rep, port = self.create_bound_pair(zmq.REQ, zmq.REP)
        eventlet.sleep()
        done = eventlet.Event()

        def tx():
            tx_i = 0
            req.send(str(tx_i).encode())
            while req.recv() != b'done':
                tx_i += 1
                req.send(str(tx_i).encode())
            done.send(0)

        def rx():
            while True:
                rx_i = rep.recv()
                if rx_i == b"1000":
                    rep.send(b'done')
                    break
                rep.send(b'i')
        eventlet.spawn(tx)
        eventlet.spawn(rx)
        final_i = done.wait()
        self.assertEqual(final_i, 0)

    @tests.skip_unless(zmq_supported)
    def test_send_1k_push_pull(self):
        down, up, port = self.create_bound_pair(zmq.PUSH, zmq.PULL)
        eventlet.sleep()

        done = eventlet.Event()

        def tx():
            tx_i = 0
            while tx_i <= 1000:
                tx_i += 1
                down.send(str(tx_i).encode())

        def rx():
            while True:
                rx_i = up.recv()
                if rx_i == b"1000":
                    done.send(0)
                    break
        eventlet.spawn(tx)
        eventlet.spawn(rx)
        final_i = done.wait()
        self.assertEqual(final_i, 0)

    @tests.skip_unless(zmq_supported)
    def test_send_1k_pub_sub(self):
        pub, sub_all, port = self.create_bound_pair(zmq.PUB, zmq.SUB)
        sub1 = self.context.socket(zmq.SUB)
        sub2 = self.context.socket(zmq.SUB)
        self.sockets.extend([sub1, sub2])
        addr = 'tcp://127.0.0.1:%s' % port
        sub1.connect(addr)
        sub2.connect(addr)
        sub_all.setsockopt(zmq.SUBSCRIBE, b'')
        sub1.setsockopt(zmq.SUBSCRIBE, b'sub1')
        sub2.setsockopt(zmq.SUBSCRIBE, b'sub2')

        sub_all_done = eventlet.Event()
        sub1_done = eventlet.Event()
        sub2_done = eventlet.Event()

        eventlet.sleep(0.2)

        def rx(sock, done_evt, msg_count=10000):
            count = 0
            while count < msg_count:
                msg = sock.recv()
                eventlet.sleep()
                if b'LAST' in msg:
                    break
                count += 1

            done_evt.send(count)

        def tx(sock):
            for i in range(1, 1001):
                msg = ("sub%s %s" % ([2, 1][i % 2], i)).encode()
                sock.send(msg)
                eventlet.sleep()
            sock.send(b'sub1 LAST')
            sock.send(b'sub2 LAST')

        eventlet.spawn(rx, sub_all, sub_all_done)
        eventlet.spawn(rx, sub1, sub1_done)
        eventlet.spawn(rx, sub2, sub2_done)
        eventlet.spawn(tx, pub)
        sub1_count = sub1_done.wait()
        sub2_count = sub2_done.wait()
        sub_all_count = sub_all_done.wait()
        self.assertEqual(sub1_count, 500)
        self.assertEqual(sub2_count, 500)
        self.assertEqual(sub_all_count, 1000)

    @tests.skip_unless(zmq_supported)
    def test_change_subscription(self):
        # FIXME: Extensive testing showed this particular test is the root cause
        # of sporadic failures on Travis.
        pub, sub, port = self.create_bound_pair(zmq.PUB, zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, b'test')
        eventlet.sleep(0)
        sub_ready = eventlet.Event()
        sub_last = eventlet.Event()
        sub_done = eventlet.Event()

        def rx():
            while sub.recv() != b'test BEGIN':
                eventlet.sleep(0)
            sub_ready.send()
            count = 0
            while True:
                msg = sub.recv()
                if msg == b'test BEGIN':
                    # BEGIN may come many times
                    continue
                if msg == b'test LAST':
                    sub.setsockopt(zmq.SUBSCRIBE, b'done')
                    sub.setsockopt(zmq.UNSUBSCRIBE, b'test')
                    eventlet.sleep(0)
                    # In real application you should either sync
                    # or tolerate loss of messages.
                    sub_last.send()
                if msg == b'done DONE':
                    break
                count += 1
            sub_done.send(count)

        def tx():
            # Sync receiver ready to avoid loss of first packets
            while not sub_ready.ready():
                pub.send(b'test BEGIN')
                eventlet.sleep(0.005)
            for i in range(1, 101):
                msg = 'test {0}'.format(i).encode()
                if i != 50:
                    pub.send(msg)
                else:
                    pub.send(b'test LAST')
                    sub_last.wait()
                # XXX: putting a real delay of 1ms here fixes sporadic failures on Travis
                # just yield eventlet.sleep(0) doesn't cut it
                eventlet.sleep(0.001)
            pub.send(b'done DONE')

        eventlet.spawn(rx)
        eventlet.spawn(tx)
        rx_count = sub_done.wait()
        self.assertEqual(rx_count, 50)

    @tests.skip_unless(zmq_supported)
    def test_recv_multipart_bug68(self):
        req, rep, port = self.create_bound_pair(zmq.REQ, zmq.REP)
        msg = [b'']
        req.send_multipart(msg)
        recieved_msg = rep.recv_multipart()
        self.assertEqual(recieved_msg, msg)

        # Send a message back the other way
        msg2 = [b""]
        rep.send_multipart(msg2, copy=False)
        # When receiving a copy it's a zmq.core.message.Message you get back
        recieved_msg = req.recv_multipart(copy=False)
        # So it needs to be converted to a string
        # I'm calling str(m) consciously here; Message has a .data attribute
        # but it's private __str__ appears to be the way to go
        self.assertEqual([m.bytes for m in recieved_msg], msg2)

    @tests.skip_unless(zmq_supported)
    def test_recv_noblock_bug76(self):
        req, rep, port = self.create_bound_pair(zmq.REQ, zmq.REP)
        self.assertRaisesErrno(zmq.EAGAIN, rep.recv, zmq.NOBLOCK)
        self.assertRaisesErrno(zmq.EAGAIN, rep.recv, zmq.NOBLOCK, True)

    @tests.skip_unless(zmq_supported)
    def test_send_during_recv(self):
        sender, receiver, port = self.create_bound_pair(zmq.XREQ, zmq.XREQ)
        eventlet.sleep()

        num_recvs = 30
        done_evts = [eventlet.Event() for _ in range(num_recvs)]

        def slow_rx(done, msg):
            self.assertEqual(sender.recv(), msg)
            done.send(0)

        def tx():
            tx_i = 0
            while tx_i <= 1000:
                sender.send(str(tx_i).encode())
                tx_i += 1

        def rx():
            while True:
                rx_i = receiver.recv()
                if rx_i == b"1000":
                    for i in range(num_recvs):
                        receiver.send(('done%d' % i).encode())
                    eventlet.sleep()
                    return

        for i in range(num_recvs):
            eventlet.spawn(slow_rx, done_evts[i], ("done%d" % i).encode())

        eventlet.spawn(tx)
        eventlet.spawn(rx)
        for evt in done_evts:
            self.assertEqual(evt.wait(), 0)

    @tests.skip_unless(zmq_supported)
    def test_send_during_recv_multipart(self):
        sender, receiver, port = self.create_bound_pair(zmq.XREQ, zmq.XREQ)
        eventlet.sleep()

        num_recvs = 30
        done_evts = [eventlet.Event() for _ in range(num_recvs)]

        def slow_rx(done, msg):
            self.assertEqual(sender.recv_multipart(), msg)
            done.send(0)

        def tx():
            tx_i = 0
            while tx_i <= 1000:
                sender.send_multipart([str(tx_i).encode(), b'1', b'2', b'3'])
                tx_i += 1

        def rx():
            while True:
                rx_i = receiver.recv_multipart()
                if rx_i == [b"1000", b'1', b'2', b'3']:
                    for i in range(num_recvs):
                        receiver.send_multipart([
                            ('done%d' % i).encode(), b'a', b'b', b'c'])
                    eventlet.sleep()
                    return

        for i in range(num_recvs):
            eventlet.spawn(slow_rx, done_evts[i], [
                ("done%d" % i).encode(), b'a', b'b', b'c'])

        eventlet.spawn(tx)
        eventlet.spawn(rx)
        for i in range(num_recvs):
            final_i = done_evts[i].wait()
            self.assertEqual(final_i, 0)

    # Need someway to ensure a thread is blocked on send... This isn't working
    @tests.skip_unless(zmq_supported)
    def test_recv_during_send(self):
        sender, receiver, port = self.create_bound_pair(zmq.XREQ, zmq.XREQ)
        eventlet.sleep()

        done = eventlet.Event()

        try:
            SNDHWM = zmq.SNDHWM
        except AttributeError:
            # ZeroMQ <3.0
            SNDHWM = zmq.HWM

        sender.setsockopt(SNDHWM, 10)
        sender.setsockopt(zmq.SNDBUF, 10)

        receiver.setsockopt(zmq.RCVBUF, 10)

        def tx():
            tx_i = 0
            while tx_i <= 1000:
                sender.send(str(tx_i).encode())
                tx_i += 1
            done.send(0)

        eventlet.spawn(tx)
        final_i = done.wait()
        self.assertEqual(final_i, 0)

    @tests.skip_unless(zmq_supported)
    def test_close_during_recv(self):
        sender, receiver, port = self.create_bound_pair(zmq.XREQ, zmq.XREQ)
        eventlet.sleep()
        done1 = eventlet.Event()
        done2 = eventlet.Event()

        def rx(e):
            self.assertRaisesErrno(RECV_ON_CLOSED_SOCKET_ERRNOS, receiver.recv)
            e.send()

        eventlet.spawn(rx, done1)
        eventlet.spawn(rx, done2)

        eventlet.sleep()
        receiver.close()

        done1.wait()
        done2.wait()

    @tests.skip_unless(zmq_supported)
    def test_getsockopt_events(self):
        sock1, sock2, _port = self.create_bound_pair(zmq.DEALER, zmq.DEALER)
        eventlet.sleep()
        poll_out = zmq.Poller()
        poll_out.register(sock1, zmq.POLLOUT)
        sock_map = poll_out.poll(100)
        self.assertEqual(len(sock_map), 1)
        events = sock1.getsockopt(zmq.EVENTS)
        self.assertEqual(events & zmq.POLLOUT, zmq.POLLOUT)
        sock1.send(b'')

        poll_in = zmq.Poller()
        poll_in.register(sock2, zmq.POLLIN)
        sock_map = poll_in.poll(100)
        self.assertEqual(len(sock_map), 1)
        events = sock2.getsockopt(zmq.EVENTS)
        self.assertEqual(events & zmq.POLLIN, zmq.POLLIN)

    @tests.skip_unless(zmq_supported)
    def test_cpu_usage_after_bind(self):
        """zmq eats CPU after PUB socket .bind()

        https://bitbucket.org/eventlet/eventlet/issue/128

        According to the ZeroMQ documentation, the socket file descriptor
        can be readable without any pending messages. So we need to ensure
        that Eventlet wraps around ZeroMQ sockets do not create busy loops.

        A naive way to test it is to measure resource usage. This will require
        some tuning to set appropriate acceptable limits.
        """
        sock = self.context.socket(zmq.PUB)
        self.sockets.append(sock)
        sock.bind_to_random_port("tcp://127.0.0.1")
        eventlet.sleep()
        tests.check_idle_cpu_usage(0.2, 0.1)

    @tests.skip_unless(zmq_supported)
    def test_cpu_usage_after_pub_send_or_dealer_recv(self):
        """zmq eats CPU after PUB send or DEALER recv.

        Same https://bitbucket.org/eventlet/eventlet/issue/128
        """
        pub, sub, _port = self.create_bound_pair(zmq.PUB, zmq.SUB)
        sub.setsockopt(zmq.SUBSCRIBE, b"")
        eventlet.sleep()
        pub.send(b'test_send')
        tests.check_idle_cpu_usage(0.2, 0.1)

        sender, receiver, _port = self.create_bound_pair(zmq.DEALER, zmq.DEALER)
        eventlet.sleep()
        sender.send(b'test_recv')
        msg = receiver.recv()
        self.assertEqual(msg, b'test_recv')
        tests.check_idle_cpu_usage(0.2, 0.1)


class TestQueueLock(tests.LimitedTestCase):
    @tests.skip_unless(zmq_supported)
    def test_queue_lock_order(self):
        q = zmq._QueueLock()
        s = eventlet.Semaphore(0)
        results = []

        def lock(x):
            with q:
                results.append(x)
            s.release()

        q.acquire()

        eventlet.spawn(lock, 1)
        eventlet.sleep()
        eventlet.spawn(lock, 2)
        eventlet.sleep()
        eventlet.spawn(lock, 3)
        eventlet.sleep()

        self.assertEqual(results, [])
        q.release()
        s.acquire()
        s.acquire()
        s.acquire()
        self.assertEqual(results, [1, 2, 3])

    @tests.skip_unless(zmq_supported)
    def test_count(self):
        q = zmq._QueueLock()
        self.assertFalse(q)
        q.acquire()
        self.assertTrue(q)
        q.release()
        self.assertFalse(q)

        with q:
            self.assertTrue(q)
        self.assertFalse(q)

    @tests.skip_unless(zmq_supported)
    def test_errors(self):
        q = zmq._QueueLock()

        self.assertRaises(zmq.LockReleaseError, q.release)

        q.acquire()
        q.release()

        self.assertRaises(zmq.LockReleaseError, q.release)

    @tests.skip_unless(zmq_supported)
    def test_nested_acquire(self):
        q = zmq._QueueLock()
        self.assertFalse(q)
        q.acquire()
        q.acquire()

        s = eventlet.Semaphore(0)
        results = []

        def lock(x):
            with q:
                results.append(x)
            s.release()

        eventlet.spawn(lock, 1)
        eventlet.sleep()
        self.assertEqual(results, [])
        q.release()
        eventlet.sleep()
        self.assertEqual(results, [])
        self.assertTrue(q)
        q.release()

        s.acquire()
        self.assertEqual(results, [1])


class TestBlockedThread(tests.LimitedTestCase):
    @tests.skip_unless(zmq_supported)
    def test_block(self):
        e = zmq._BlockedThread()
        done = eventlet.Event()
        self.assertFalse(e)

        def block():
            e.block()
            done.send(1)

        eventlet.spawn(block)
        eventlet.sleep()

        self.assertFalse(done.has_result())
        e.wake()
        done.wait()


@contextlib.contextmanager
def clean_context():
    ctx = zmq.Context()
    eventlet.sleep()
    yield ctx
    ctx.destroy()


@contextlib.contextmanager
def clean_pair(type1, type2, interface='tcp://127.0.0.1'):
    with clean_context() as ctx:
        s1 = ctx.socket(type1)
        port = s1.bind_to_random_port(interface)
        s2 = ctx.socket(type2)
        s2.connect('{0}:{1}'.format(interface, port))
        eventlet.sleep()
        yield (s1, s2, port)
        s1.close()
        s2.close()


@tests.skip_unless(zmq_supported)
def test_recv_json_no_args():
    # https://github.com/eventlet/eventlet/issues/376
    with clean_pair(zmq.REQ, zmq.REP) as (s1, s2, _):
        eventlet.spawn(s1.send_json, {})
        s2.recv_json()


@tests.skip_unless(zmq_supported)
def test_recv_timeout():
    # https://github.com/eventlet/eventlet/issues/282
    with clean_pair(zmq.PUB, zmq.SUB) as (_, sub, _):
        sub.setsockopt(zmq.RCVTIMEO, 100)
        try:
            with eventlet.Timeout(1, False):
                sub.recv()
            assert False
        except zmq.ZMQError as e:
            assert eventlet.is_timeout(e)
