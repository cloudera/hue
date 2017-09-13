from saml2.eptid import Eptid, EptidShelve

__author__ = 'rolandh'


def test_eptid():
    edb = Eptid("secret")
    e1 = edb.get("idp_entity_id", "sp_entity_id", "user_id", "some other data")
    print(e1)
    assert e1.startswith("idp_entity_id!sp_entity_id!")
    e2 = edb.get("idp_entity_id", "sp_entity_id", "user_id", "some other data")
    assert e1 == e2

    e3 = edb.get("idp_entity_id", "sp_entity_id", "user_2", "some other data")
    print(e3)
    assert e1 != e3

    e4 = edb.get("idp_entity_id", "sp_entity_id2", "user_id", "some other data")
    assert e4 != e1
    assert e4 != e3


def test_eptid_shelve():
    edb = EptidShelve("secret", "eptid.db")
    e1 = edb.get("idp_entity_id", "sp_entity_id", "user_id", "some other data")
    print(e1)
    assert e1.startswith("idp_entity_id!sp_entity_id!")
    e2 = edb.get("idp_entity_id", "sp_entity_id", "user_id", "some other data")
    assert e1 == e2

    e3 = edb.get("idp_entity_id", "sp_entity_id", "user_2", "some other data")
    print(e3)
    assert e1 != e3

    e4 = edb.get("idp_entity_id", "sp_entity_id2", "user_id", "some other data")
    assert e4 != e1
    assert e4 != e3


if __name__ == "__main__":
    test_eptid_shelve()
