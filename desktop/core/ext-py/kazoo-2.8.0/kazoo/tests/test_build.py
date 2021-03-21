import os

import pytest

from kazoo.testing import KazooTestCase


class TestBuildEnvironment(KazooTestCase):
    def setUp(self):
        KazooTestCase.setUp(self)
        if not os.environ.get('TRAVIS'):
            pytest.skip('Only run build config tests on Travis.')

    def test_zookeeper_version(self):
        server_version = self.client.server_version()
        server_version = '.'.join([str(i) for i in server_version])
        env_version = os.environ.get('ZOOKEEPER_VERSION')
        if env_version:
            if '-' in env_version:
                # Ignore pre-release markers like -alpha
                env_version = env_version.split('-')[0]
            assert env_version == server_version
