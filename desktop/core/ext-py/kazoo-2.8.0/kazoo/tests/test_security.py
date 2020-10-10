import unittest

from kazoo.security import Permissions


class TestACL(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from kazoo.security import make_acl

        return make_acl(*args, **kwargs)

    def test_read_acl(self):
        acl = self._makeOne("digest", ":", read=True)
        assert acl.perms & Permissions.READ == Permissions.READ

    def test_all_perms(self):
        acl = self._makeOne("digest", ":", read=True, write=True,
                            create=True, delete=True, admin=True)
        for perm in [Permissions.READ, Permissions.CREATE, Permissions.WRITE,
                     Permissions.DELETE, Permissions.ADMIN]:
            assert acl.perms & perm == perm

    def test_perm_listing(self):
        from kazoo.security import ACL

        f = ACL(15, 'fred')
        assert 'READ' in f.acl_list
        assert 'WRITE' in f.acl_list
        assert 'CREATE' in f.acl_list
        assert 'DELETE' in f.acl_list

        f = ACL(16, 'fred')
        assert 'ADMIN' in f.acl_list

        f = ACL(31, 'george')
        assert 'ALL' in f.acl_list

    def test_perm_repr(self):
        from kazoo.security import ACL

        f = ACL(16, 'fred')
        assert "ACL(perms=16, acl_list=['ADMIN']" in repr(f)
