import gc
import importlib
import uuid

from mock import patch, call, Mock
import pytest
from objgraph import count as count_refs_by_type

from kazoo.testing import KazooTestHarness
from kazoo.exceptions import KazooException
from kazoo.recipe.cache import TreeCache, TreeNode, TreeEvent


class KazooAdaptiveHandlerTestCase(KazooTestHarness):
    HANDLERS = (
        ('kazoo.handlers.gevent', 'SequentialGeventHandler'),
        ('kazoo.handlers.eventlet', 'SequentialEventletHandler'),
        ('kazoo.handlers.threading', 'SequentialThreadingHandler'),
    )

    def setUp(self):
        self.handler = self.choose_an_installed_handler()
        self.setup_zookeeper(handler=self.handler)

    def tearDown(self):
        self.handler = None
        self.teardown_zookeeper()

    def choose_an_installed_handler(self):
        for handler_module, handler_class in self.HANDLERS:
            try:
                mod = importlib.import_module(handler_module)
                cls = getattr(mod, handler_class)
            except ImportError:
                continue
            else:
                return cls()
        raise ImportError('No available handler')


class KazooTreeCacheTests(KazooAdaptiveHandlerTestCase):
    def setUp(self):
        super(KazooTreeCacheTests, self).setUp()
        self._event_queue = self.client.handler.queue_impl()
        self._error_queue = self.client.handler.queue_impl()
        self.path = None
        self.cache = None

    def tearDown(self):
        if not self._error_queue.empty():
            try:
                raise self._error_queue.get()
            except FakeException:
                pass
        if self.cache is not None:
            self.cache.close()
            self.cache = None
        super(KazooTreeCacheTests, self).tearDown()

    def make_cache(self):
        if self.cache is None:
            self.path = '/' + uuid.uuid4().hex
            self.cache = TreeCache(self.client, self.path)
            self.cache.listen(lambda event: self._event_queue.put(event))
            self.cache.listen_fault(lambda error: self._error_queue.put(error))
            self.cache.start()
        return self.cache

    def wait_cache(self, expect=None, since=None, timeout=10):
        started = since is None
        while True:
            event = self._event_queue.get(timeout=timeout)
            if started:
                if expect is not None:
                    assert event.event_type == expect
                return event
            if event.event_type == since:
                started = True
                if expect is None:
                    return

    def spy_client(self, method_name):
        method = getattr(self.client, method_name)
        return patch.object(self.client, method_name, wraps=method)

    def _wait_gc(self):
        # trigger switching on some coroutine handlers
        self.client.handler.sleep_func(0.1)

        completion_queue = getattr(self.handler, 'completion_queue', None)
        if completion_queue is not None:
            while not self.client.handler.completion_queue.empty():
                self.client.handler.sleep_func(0.1)

        for gen in range(3):
            gc.collect(gen)

    def count_tree_node(self):
        # inspect GC and count tree nodes for checking memory leak
        for retry in range(10):
            result = set()
            for _ in range(5):
                self._wait_gc()
                result.add(count_refs_by_type('TreeNode'))
            if len(result) == 1:
                return list(result)[0]
        raise RuntimeError('could not count refs exactly')

    def test_start(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        stat = self.client.exists(self.path)
        assert stat.version == 0

        assert self.cache._state == TreeCache.STATE_STARTED
        assert self.cache._root._state == TreeNode.STATE_LIVE

    def test_start_started(self):
        self.make_cache()
        with pytest.raises(KazooException):
            self.cache.start()

    def test_start_closed(self):
        self.make_cache()
        self.cache.close()
        with pytest.raises(KazooException):
            self.cache.start()

    def test_close(self):
        assert self.count_tree_node() == 0

        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)
        self.client.create(self.path + '/foo/bar/baz', makepath=True)
        for _ in range(3):
            self.wait_cache(TreeEvent.NODE_ADDED)

        # setup stub watchers which are outside of tree cache
        stub_data_watcher = Mock(spec=lambda event: None)
        stub_child_watcher = Mock(spec=lambda event: None)
        self.client.get(self.path + '/foo', stub_data_watcher)
        self.client.get_children(self.path + '/foo', stub_child_watcher)

        # watchers inside tree cache should be here
        root_path = self.client.chroot + self.path
        assert len(self.client._data_watchers[root_path + '/foo']) == 2
        assert len(self.client._data_watchers[root_path + '/foo/bar']) == 1
        assert len(self.client._data_watchers[root_path + '/foo/bar/baz']) == 1
        assert len(self.client._child_watchers[root_path + '/foo']) == 2
        assert len(self.client._child_watchers[root_path + '/foo/bar']) == 1
        assert (
            len(self.client._child_watchers[root_path + '/foo/bar/baz']) == 1
        )

        self.cache.close()

        # nothing should be published since tree closed
        assert self._event_queue.empty()

        # tree should be empty
        assert self.cache._root._children == {}
        assert self.cache._root._data is None
        assert self.cache._state == TreeCache.STATE_CLOSED

        # node state should not be changed
        assert self.cache._root._state != TreeNode.STATE_DEAD

        # watchers should be reset
        assert len(self.client._data_watchers[root_path + '/foo']) == 1
        assert len(self.client._data_watchers[root_path + '/foo/bar']) == 0
        assert len(self.client._data_watchers[root_path + '/foo/bar/baz']) == 0
        assert len(self.client._child_watchers[root_path + '/foo']) == 1
        assert len(self.client._child_watchers[root_path + '/foo/bar']) == 0
        assert (
            len(self.client._child_watchers[root_path + '/foo/bar/baz']) == 0
        )

        # outside watchers should not be deleted
        assert (
            list(self.client._data_watchers[root_path + '/foo'])[0]
            == stub_data_watcher
        )
        assert (
            list(self.client._child_watchers[root_path + '/foo'])[0]
            == stub_child_watcher
        )

        # should not be any leaked memory (tree node) here
        self.cache = None
        assert self.count_tree_node() == 0

    def test_delete_operation(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        assert self.count_tree_node() == 1

        self.client.create(self.path + '/foo/bar/baz', makepath=True)
        for _ in range(3):
            self.wait_cache(TreeEvent.NODE_ADDED)

        self.client.delete(self.path + '/foo', recursive=True)
        for _ in range(3):
            self.wait_cache(TreeEvent.NODE_REMOVED)

        # tree should be empty
        assert self.cache._root._children == {}

        # watchers should be reset
        root_path = self.client.chroot + self.path
        assert self.client._data_watchers[root_path + '/foo'] == set()
        assert self.client._data_watchers[root_path + '/foo/bar'] == set()
        assert self.client._data_watchers[root_path + '/foo/bar/baz'] == set()
        assert self.client._child_watchers[root_path + '/foo'] == set()
        assert self.client._child_watchers[root_path + '/foo/bar'] == set()
        assert self.client._child_watchers[root_path + '/foo/bar/baz'] == set()

        # should not be any leaked memory (tree node) here
        assert self.count_tree_node() == 1

    def test_children_operation(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        self.client.create(self.path + '/test_children', b'test_children_1')
        event = self.wait_cache(TreeEvent.NODE_ADDED)
        assert event.event_type == TreeEvent.NODE_ADDED
        assert event.event_data.path == self.path + '/test_children'
        assert event.event_data.data == b'test_children_1'
        assert event.event_data.stat.version == 0

        self.client.set(self.path + '/test_children', b'test_children_2')
        event = self.wait_cache(TreeEvent.NODE_UPDATED)
        assert event.event_type == TreeEvent.NODE_UPDATED
        assert event.event_data.path == self.path + '/test_children'
        assert event.event_data.data == b'test_children_2'
        assert event.event_data.stat.version == 1

        self.client.delete(self.path + '/test_children')
        event = self.wait_cache(TreeEvent.NODE_REMOVED)
        assert event.event_type == TreeEvent.NODE_REMOVED
        assert event.event_data.path == self.path + '/test_children'
        assert event.event_data.data == b'test_children_2'
        assert event.event_data.stat.version == 1

    def test_subtree_operation(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        self.client.create(self.path + '/foo/bar/baz', makepath=True)
        for relative_path in ('/foo', '/foo/bar', '/foo/bar/baz'):
            event = self.wait_cache(TreeEvent.NODE_ADDED)
            assert event.event_type == TreeEvent.NODE_ADDED
            assert event.event_data.path == self.path + relative_path
            assert event.event_data.data == b''
            assert event.event_data.stat.version == 0

        self.client.delete(self.path + '/foo', recursive=True)
        for relative_path in ('/foo/bar/baz', '/foo/bar', '/foo'):
            event = self.wait_cache(TreeEvent.NODE_REMOVED)
            assert event.event_type == TreeEvent.NODE_REMOVED
            assert event.event_data.path == self.path + relative_path

    def test_get_data(self):
        cache = self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)
        self.client.create(self.path + '/foo/bar/baz', b'@', makepath=True)
        self.wait_cache(TreeEvent.NODE_ADDED)
        self.wait_cache(TreeEvent.NODE_ADDED)
        self.wait_cache(TreeEvent.NODE_ADDED)

        with patch.object(cache, '_client'):  # disable any remote operation
            assert cache.get_data(self.path).data == b''
            assert cache.get_data(self.path).stat.version == 0

            assert cache.get_data(self.path + '/foo').data == b''
            assert cache.get_data(self.path + '/foo').stat.version == 0

            assert cache.get_data(self.path + '/foo/bar').data == b''
            assert cache.get_data(self.path + '/foo/bar').stat.version == 0

            assert cache.get_data(self.path + '/foo/bar/baz').data == b'@'
            assert cache.get_data(self.path + '/foo/bar/baz').stat.version == 0

    def test_get_children(self):
        cache = self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)
        self.client.create(self.path + '/foo/bar/baz', b'@', makepath=True)
        self.wait_cache(TreeEvent.NODE_ADDED)
        self.wait_cache(TreeEvent.NODE_ADDED)
        self.wait_cache(TreeEvent.NODE_ADDED)

        with patch.object(cache, '_client'):  # disable any remote operation
            assert (
                cache.get_children(self.path + '/foo/bar/baz') == frozenset()
            )
            assert (
                cache.get_children(self.path + '/foo/bar')
                == frozenset(['baz'])
            )
            assert cache.get_children(self.path + '/foo') == frozenset(['bar'])
            assert cache.get_children(self.path) == frozenset(['foo'])

    def test_get_data_out_of_tree(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)
        with pytest.raises(ValueError):
            self.cache.get_data('/out_of_tree')

    def test_get_children_out_of_tree(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)
        with pytest.raises(ValueError):
            self.cache.get_children('/out_of_tree')

    def test_get_data_no_node(self):
        cache = self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        with patch.object(cache, '_client'):  # disable any remote operation
            assert cache.get_data(self.path + '/non_exists') is None

    def test_get_children_no_node(self):
        cache = self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        with patch.object(cache, '_client'):  # disable any remote operation
            assert cache.get_children(self.path + '/non_exists') is None

    def test_session_reconnected(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        self.client.create(self.path + '/foo')
        event = self.wait_cache(TreeEvent.NODE_ADDED)
        assert event.event_data.path == self.path + '/foo'

        with self.spy_client('get_async') as get_data:
            with self.spy_client('get_children_async') as get_children:
                # session suspended
                self.lose_connection(self.client.handler.event_object)
                self.wait_cache(TreeEvent.CONNECTION_SUSPENDED)

                # There are a serial refreshing operation here. But NODE_ADDED
                # events will not be raised because the zxid of nodes are the
                # same during reconnecting.

                # connection restore
                self.wait_cache(TreeEvent.CONNECTION_RECONNECTED)

                # wait for outstanding operations
                while self.cache._outstanding_ops > 0:
                    self.client.handler.sleep_func(0.1)

                # inspect in-memory nodes
                _node_root = self.cache._root
                _node_foo = self.cache._root._children['foo']

                # make sure that all nodes are refreshed
                get_data.assert_has_calls(
                    [
                        call(self.path, watch=_node_root._process_watch),
                        call(
                            self.path + '/foo', watch=_node_foo._process_watch
                        ),
                    ],
                    any_order=True,
                )
                get_children.assert_has_calls(
                    [
                        call(self.path, watch=_node_root._process_watch),
                        call(
                            self.path + '/foo', watch=_node_foo._process_watch
                        ),
                    ],
                    any_order=True,
                )

    def test_root_recreated(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        # remove root node
        self.client.delete(self.path)
        event = self.wait_cache(TreeEvent.NODE_REMOVED)
        assert event.event_type == TreeEvent.NODE_REMOVED
        assert event.event_data.data == b''
        assert event.event_data.path == self.path
        assert event.event_data.stat.version == 0

        # re-create root node
        self.client.ensure_path(self.path)
        event = self.wait_cache(TreeEvent.NODE_ADDED)
        assert event.event_type == TreeEvent.NODE_ADDED
        assert event.event_data.data == b''
        assert event.event_data.path == self.path
        assert event.event_data.stat.version == 0

        assert self.cache._outstanding_ops >= 0, (
            'unexpected outstanding ops %r' % self.cache._outstanding_ops
        )

    def test_exception_handler(self):
        error_value = FakeException()
        error_handler = Mock()

        with patch.object(TreeNode, 'on_deleted') as on_deleted:
            on_deleted.side_effect = [error_value]

            self.make_cache()
            self.cache.listen_fault(error_handler)

            self.cache.close()
            error_handler.assert_called_once_with(error_value)

    def test_exception_suppressed(self):
        self.make_cache()
        self.wait_cache(since=TreeEvent.INITIALIZED)

        # stoke up ConnectionClosedError
        self.client.stop()
        self.client.close()
        self.client.handler.start()  # keep the async completion
        self.wait_cache(since=TreeEvent.CONNECTION_LOST)

        with patch.object(TreeNode, 'on_created') as on_created:
            self.cache._root._call_client('exists', '/')
            self.cache._root._call_client('get', '/')
            self.cache._root._call_client('get_children', '/')

            self.wait_cache(since=TreeEvent.INITIALIZED)
            on_created.assert_not_called()
            assert self.cache._outstanding_ops == 0


class FakeException(Exception):
    pass
