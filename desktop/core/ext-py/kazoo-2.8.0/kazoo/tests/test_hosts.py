from unittest import TestCase

from kazoo.hosts import collect_hosts


class HostsTestCase(TestCase):

    def test_ipv4(self):
        hosts, chroot = collect_hosts('127.0.0.1:2181, 192.168.1.2:2181, \
                                       132.254.111.10:2181')
        assert hosts == [('127.0.0.1', 2181),
                         ('192.168.1.2', 2181),
                         ('132.254.111.10', 2181)]
        assert chroot is None

        hosts, chroot = collect_hosts(['127.0.0.1:2181',
                                       '192.168.1.2:2181',
                                       '132.254.111.10:2181'])
        assert hosts == [('127.0.0.1', 2181),
                         ('192.168.1.2', 2181),
                         ('132.254.111.10', 2181)]
        assert chroot is None

    def test_ipv6(self):
        hosts, chroot = collect_hosts('[fe80::200:5aee:feaa:20a2]:2181')
        assert hosts == [('fe80::200:5aee:feaa:20a2', 2181)]
        assert chroot is None

        hosts, chroot = collect_hosts(['[fe80::200:5aee:feaa:20a2]:2181'])
        assert hosts == [('fe80::200:5aee:feaa:20a2', 2181)]
        assert chroot is None

    def test_hosts_list(self):

        hosts, chroot = collect_hosts('zk01:2181, zk02:2181, zk03:2181')
        expected1 = [('zk01', 2181), ('zk02', 2181), ('zk03', 2181)]
        assert hosts == expected1
        assert chroot is None

        hosts, chroot = collect_hosts(['zk01:2181', 'zk02:2181', 'zk03:2181'])
        assert hosts == expected1
        assert chroot is None

        expected2 = '/test'
        hosts, chroot = collect_hosts('zk01:2181, zk02:2181, zk03:2181/test')
        assert hosts == expected1
        assert chroot == expected2

        hosts, chroot = collect_hosts(['zk01:2181',
                                       'zk02:2181',
                                       'zk03:2181', '/test'])
        assert hosts == expected1
        assert chroot == expected2
