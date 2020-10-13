import uuid

from kazoo.testing import KazooTestCase


class KazooPartyTests(KazooTestCase):
    def setUp(self):
        super(KazooPartyTests, self).setUp()
        self.path = "/" + uuid.uuid4().hex

    def test_party(self):
        parties = [self.client.Party(self.path, "p%s" % i)
                   for i in range(5)]

        one_party = parties[0]

        assert list(one_party) == []
        assert len(one_party) == 0

        participants = set()
        for party in parties:
            party.join()
            participants.add(party.data.decode('utf-8'))

            assert set(party) == participants
            assert len(party) == len(participants)

        for party in parties:
            party.leave()
            participants.remove(party.data.decode('utf-8'))

            assert set(party) == participants
            assert len(party) == len(participants)

    def test_party_reuse_node(self):
        party = self.client.Party(self.path, "p1")
        self.client.ensure_path(self.path)
        self.client.create(party.create_path)
        party.join()
        assert party.participating is True
        party.leave()
        assert party.participating is False
        assert len(party) == 0

    def test_party_vanishing_node(self):
        party = self.client.Party(self.path, "p1")
        party.join()
        assert party.participating is True
        self.client.delete(party.create_path)
        party.leave()
        assert party.participating is False
        assert len(party) == 0


class KazooShallowPartyTests(KazooTestCase):
    def setUp(self):
        super(KazooShallowPartyTests, self).setUp()
        self.path = "/" + uuid.uuid4().hex

    def test_party(self):
        parties = [self.client.ShallowParty(self.path, "p%s" % i)
                   for i in range(5)]

        one_party = parties[0]

        assert list(one_party) == []
        assert len(one_party) == 0

        participants = set()
        for party in parties:
            party.join()
            participants.add(party.data.decode('utf-8'))

            assert set(party) == participants
            assert len(party) == len(participants)

        for party in parties:
            party.leave()
            participants.remove(party.data.decode('utf-8'))

            assert set(party) == participants
            assert len(party) == len(participants)
