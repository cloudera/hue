import os
import subprocess
import time

import pytest

from kazoo.testing import KazooTestHarness
from kazoo.exceptions import (
    AuthFailedError,
    NoAuthError,
)
from kazoo.tests.util import TRAVIS_ZK_VERSION


class TestLegacySASLDigestAuthentication(KazooTestHarness):
    def setUp(self):
        try:
            import puresasl  # NOQA
        except ImportError:
            pytest.skip("PureSASL not available.")

        os.environ["ZOOKEEPER_JAAS_AUTH"] = "digest"
        self.setup_zookeeper()

        if TRAVIS_ZK_VERSION:
            version = TRAVIS_ZK_VERSION
        else:
            version = self.client.server_version()
        if not version or version < (3, 4):
            pytest.skip("Must use Zookeeper 3.4 or above")

    def tearDown(self):
        self.teardown_zookeeper()

    def test_connect_sasl_auth(self):
        from kazoo.security import make_acl

        username = "jaasuser"
        password = "jaas_password"

        acl = make_acl("sasl", credential=username, all=True)

        sasl_auth = "%s:%s" % (username, password)
        client = self._get_client(auth_data=[("sasl", sasl_auth)])

        client.start()
        try:
            client.create("/1", acl=(acl,))
            # give ZK a chance to copy data to other node
            time.sleep(0.1)
            with pytest.raises(NoAuthError):
                self.client.get("/1")
        finally:
            client.delete("/1")
            client.stop()
            client.close()

    def test_invalid_sasl_auth(self):
        client = self._get_client(auth_data=[("sasl", "baduser:badpassword")])
        with pytest.raises(AuthFailedError):
            client.start()


class TestSASLDigestAuthentication(KazooTestHarness):
    def setUp(self):
        try:
            import puresasl  # NOQA
        except ImportError:
            pytest.skip("PureSASL not available.")

        os.environ["ZOOKEEPER_JAAS_AUTH"] = "digest"
        self.setup_zookeeper()

        if TRAVIS_ZK_VERSION:
            version = TRAVIS_ZK_VERSION
        else:
            version = self.client.server_version()
        if not version or version < (3, 4):
            pytest.skip("Must use Zookeeper 3.4 or above")

    def tearDown(self):
        self.teardown_zookeeper()

    def test_connect_sasl_auth(self):
        from kazoo.security import make_acl

        username = "jaasuser"
        password = "jaas_password"

        acl = make_acl("sasl", credential=username, all=True)

        client = self._get_client(
            sasl_options={
                "mechanism": "DIGEST-MD5",
                "username": username,
                "password": password,
            }
        )
        client.start()
        try:
            client.create("/1", acl=(acl,))
            # give ZK a chance to copy data to other node
            time.sleep(0.1)
            with pytest.raises(NoAuthError):
                self.client.get("/1")
        finally:
            client.delete("/1")
            client.stop()
            client.close()

    def test_invalid_sasl_auth(self):
        client = self._get_client(
            sasl_options={
                "mechanism": "DIGEST-MD5",
                "username": "baduser",
                "password": "badpassword",
            }
        )
        with pytest.raises(AuthFailedError):
            client.start()


class TestSASLGSSAPIAuthentication(KazooTestHarness):
    def setUp(self):
        try:
            import puresasl  # NOQA
        except ImportError:
            pytest.skip("PureSASL not available.")
        try:
            import kerberos  # NOQA
        except ImportError:
            pytest.skip("Kerberos support not available.")
        if not os.environ.get("KRB5_TEST_ENV"):
            pytest.skip("Test Kerberos environ not setup.")

        os.environ["ZOOKEEPER_JAAS_AUTH"] = "gssapi"
        self.setup_zookeeper()

        if TRAVIS_ZK_VERSION:
            version = TRAVIS_ZK_VERSION
        else:
            version = self.client.server_version()
        if not version or version < (3, 4):
            pytest.skip("Must use Zookeeper 3.4 or above")

    def tearDown(self):
        self.teardown_zookeeper()

    def test_connect_gssapi_auth(self):
        from kazoo.security import make_acl

        # Ensure we have a client ticket
        subprocess.check_call(
            [
                "kinit",
                "-kt",
                os.path.expandvars("${KRB5_TEST_ENV}/client.keytab"),
                "client",
            ]
        )

        acl = make_acl("sasl", credential="client@KAZOOTEST.ORG", all=True)

        client = self._get_client(sasl_options={"mechanism": "GSSAPI"})
        client.start()
        try:
            client.create("/1", acl=(acl,))
            # give ZK a chance to copy data to other node
            time.sleep(0.1)
            with pytest.raises(NoAuthError):
                self.client.get("/1")
        finally:
            client.delete("/1")
            client.stop()
            client.close()

    def test_invalid_gssapi_auth(self):
        # Request a post-datated ticket, so that it is currently invalid.
        subprocess.check_call(
            [
                "kinit",
                "-kt",
                os.path.expandvars("${KRB5_TEST_ENV}/client.keytab"),
                "-s",
                "30min",
                "client",
            ]
        )

        client = self._get_client(sasl_options={"mechanism": "GSSAPI"})
        with pytest.raises(AuthFailedError):
            client.start()
