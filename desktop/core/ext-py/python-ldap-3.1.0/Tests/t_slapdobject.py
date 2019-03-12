import unittest

import slapdtest


class TestSlapdObject(unittest.TestCase):
    def test_context_manager(self):
        with slapdtest.SlapdObject() as server:
            self.assertIsNotNone(server._proc)
        self.assertIsNone(server._proc)

    def test_context_manager_after_start(self):
        server = slapdtest.SlapdObject()
        server.start()
        self.assertIsNotNone(server._proc)
        with server:
            self.assertIsNotNone(server._proc)
        self.assertIsNone(server._proc)
