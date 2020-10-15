import copy
import os
import socket
import unittest

import six
import should_be.all  # noqa

import gssapi.raw as gb
import gssapi.raw.misc as gbmisc
import k5test.unit as ktu
import k5test as kt

if six.PY2:
    from collections import Set
else:
    from collections.abc import Set


TARGET_SERVICE_NAME = b'host'
FQDN = socket.getfqdn().encode('utf-8')
SERVICE_PRINCIPAL = TARGET_SERVICE_NAME + b'/' + FQDN


class _GSSAPIKerberosTestCase(kt.KerberosTestCase):
    @classmethod
    def setUpClass(cls):
        super(_GSSAPIKerberosTestCase, cls).setUpClass()
        svc_princ = SERVICE_PRINCIPAL.decode("UTF-8")

        cls.realm.kinit(svc_princ, flags=['-k'])

        cls._init_env()

        cls.USER_PRINC = cls.realm.user_princ.split('@')[0].encode("UTF-8")
        cls.ADMIN_PRINC = cls.realm.admin_princ.split('@')[0].encode("UTF-8")

    @classmethod
    def _init_env(cls):
        cls._saved_env = copy.deepcopy(os.environ)
        for k, v in cls.realm.env.items():
            os.environ[k] = v

    @classmethod
    def _restore_env(cls):
        for k in copy.deepcopy(os.environ):
            if k in cls._saved_env:
                os.environ[k] = cls._saved_env[k]
            else:
                del os.environ[k]

        cls._saved_env = None

    @classmethod
    def tearDownClass(cls):
        super(_GSSAPIKerberosTestCase, cls).tearDownClass()
        cls._restore_env()


class TestBaseUtilities(_GSSAPIKerberosTestCase):
    def setUp(self):
        self.realm.kinit(SERVICE_PRINCIPAL.decode("UTF-8"), flags=['-k'])

    def test_indicate_mechs(self):
        mechs = gb.indicate_mechs()

        mechs.shouldnt_be_none()
        mechs.should_be_a(set)
        mechs.shouldnt_be_empty()

        mechs.should_include(gb.MechType.kerberos)

    def test_import_name(self):
        imported_name = gb.import_name(TARGET_SERVICE_NAME)

        imported_name.shouldnt_be_none()
        imported_name.should_be_a(gb.Name)

        gb.release_name(imported_name)

    def test_canonicalize_export_name(self):
        imported_name = gb.import_name(self.ADMIN_PRINC,
                                       gb.NameType.kerberos_principal)

        canonicalized_name = gb.canonicalize_name(imported_name,
                                                  gb.MechType.kerberos)

        canonicalized_name.shouldnt_be_none()
        canonicalized_name.should_be_a(gb.Name)

        exported_name = gb.export_name(canonicalized_name)

        exported_name.shouldnt_be_none()
        exported_name.should_be_a(bytes)
        exported_name.shouldnt_be_empty()

    def test_duplicate_name(self):
        orig_name = gb.import_name(TARGET_SERVICE_NAME)
        new_name = gb.duplicate_name(orig_name)

        new_name.shouldnt_be_none()
        gb.compare_name(orig_name, new_name).should_be_true()

    def test_display_name(self):
        imported_name = gb.import_name(TARGET_SERVICE_NAME,
                                       gb.NameType.hostbased_service)
        displ_resp = gb.display_name(imported_name)

        displ_resp.shouldnt_be_none()

        (displayed_name, out_type) = displ_resp

        displayed_name.shouldnt_be_none()
        displayed_name.should_be_a(bytes)
        displayed_name.should_be(TARGET_SERVICE_NAME)

        out_type.shouldnt_be_none()
        out_type.should_be(gb.NameType.hostbased_service)

    # NB(directxman12): we don't test display_name_ext because the krb5 mech
    # doesn't actually implement it

    @ktu.gssapi_extension_test('rfc6680', 'RFC 6680')
    def test_inquire_name_not_mech_name(self):
        base_name = gb.import_name(TARGET_SERVICE_NAME,
                                   gb.NameType.hostbased_service)
        inquire_res = gb.inquire_name(base_name)

        inquire_res.shouldnt_be_none()

        inquire_res.is_mech_name.should_be_false()
        inquire_res.mech.should_be_none()

    @ktu.gssapi_extension_test('rfc6680', 'RFC 6680')
    def test_inquire_name_mech_name(self):
        base_name = gb.import_name(TARGET_SERVICE_NAME,
                                   gb.NameType.hostbased_service)
        mech_name = gb.canonicalize_name(base_name, gb.MechType.kerberos)

        inquire_res = gb.inquire_name(mech_name)
        inquire_res.shouldnt_be_none()

        inquire_res.is_mech_name.should_be_true()
        inquire_res.mech.should_be_a(gb.OID)
        inquire_res.mech.should_be(gb.MechType.kerberos)

    @ktu.gssapi_extension_test('rfc6680', 'RFC 6680')
    @ktu.gssapi_extension_test('rfc6680_comp_oid',
                               'RFC 6680 (COMPOSITE_EXPORT OID)')
    def test_import_export_name_composite_no_attrs(self):
        base_name = gb.import_name(TARGET_SERVICE_NAME,
                                   gb.NameType.hostbased_service)

        canon_name = gb.canonicalize_name(base_name,
                                          gb.MechType.kerberos)
        exported_name = gb.export_name_composite(canon_name)

        exported_name.should_be_a(bytes)

        imported_name = gb.import_name(exported_name,
                                       gb.NameType.composite_export)

        imported_name.should_be_a(gb.Name)

    # NB(directxman12): the greet_client plugin only allows for one value

    @ktu.gssapi_extension_test('rfc6680', 'RFC 6680')
    @ktu.krb_plugin_test('authdata', 'greet_client')
    def test_inquire_name_with_attrs(self):
        base_name = gb.import_name(TARGET_SERVICE_NAME,
                                   gb.NameType.hostbased_service)
        canon_name = gb.canonicalize_name(base_name, gb.MechType.kerberos)
        gb.set_name_attribute(canon_name, b'urn:greet:greeting',
                              [b'some greeting'])

        inquire_res = gb.inquire_name(canon_name)
        inquire_res.shouldnt_be_none()

        inquire_res.attrs.should_be_a(list)
        inquire_res.attrs.should_be([b'urn:greet:greeting'])

    @ktu.gssapi_extension_test('rfc6680', 'RFC 6680')
    @ktu.krb_plugin_test('authdata', 'greet_client')
    def test_basic_get_set_delete_name_attributes_no_auth(self):
        base_name = gb.import_name(TARGET_SERVICE_NAME,
                                   gb.NameType.hostbased_service)
        canon_name = gb.canonicalize_name(base_name, gb.MechType.kerberos)

        gb.set_name_attribute(canon_name, b'urn:greet:greeting',
                              [b'some other val'], complete=True)

        get_res = gb.get_name_attribute(canon_name, b'urn:greet:greeting')
        get_res.shouldnt_be_none()

        get_res.values.should_be_a(list)
        get_res.values.should_be([b'some other val'])

        get_res.display_values.should_be_a(list)
        get_res.display_values.should_be(get_res.values)

        get_res.complete.should_be_true()
        get_res.authenticated.should_be_false()

        gb.delete_name_attribute(canon_name, b'urn:greet:greeting')

        # NB(directxman12): the code below currently segfaults due to the way
        # that krb5 and the krb5 greet plugin is written
        # gb.get_name_attribute.should_raise(
        #     gb.exceptions.OperationUnavailableError, canon_name,
        #     'urn:greet:greeting')

    @ktu.gssapi_extension_test('rfc6680', 'RFC 6680')
    @ktu.krb_plugin_test('authdata', 'greet_client')
    def test_import_export_name_composite(self):
        base_name = gb.import_name(TARGET_SERVICE_NAME,
                                   gb.NameType.hostbased_service)
        canon_name = gb.canonicalize_name(base_name, gb.MechType.kerberos)
        gb.set_name_attribute(canon_name, b'urn:greet:greeting', [b'some val'])

        exported_name = gb.export_name_composite(canon_name)

        exported_name.should_be_a(bytes)

        # TODO(directxman12): when you just import a token as composite,
        # appears as this name whose text is all garbled, since it contains
        # all of the attributes, etc, but doesn't properly have the attributes.
        # Once it's canonicalized, the attributes reappear.  However, if you
        # just import it as normal export, the attributes appear directly.
        # It is thus unclear as to what is going on

        # imported_name_raw = gb.import_name(exported_name,
        #                                    gb.NameType.composite_export)
        # imported_name = gb.canonicalize_name(imported_name_r,
        #                                      gb.MechType.kerberos)

        imported_name = gb.import_name(exported_name, gb.NameType.export)

        imported_name.should_be_a(gb.Name)

        get_res = gb.get_name_attribute(imported_name, b'urn:greet:greeting')
        get_res.values.should_be([b'some val'])

    def test_compare_name(self):
        service_name1 = gb.import_name(TARGET_SERVICE_NAME)
        service_name2 = gb.import_name(TARGET_SERVICE_NAME)
        init_name = gb.import_name(self.ADMIN_PRINC,
                                   gb.NameType.kerberos_principal)

        gb.compare_name(service_name1, service_name2).should_be_true()
        gb.compare_name(service_name2, service_name1).should_be_true()

        gb.compare_name(service_name1, init_name).should_be_false()

        gb.release_name(service_name1)
        gb.release_name(service_name2)
        gb.release_name(init_name)

    def test_display_status(self):
        status_resp = gbmisc._display_status(0, False)
        status_resp.shouldnt_be_none()

        (status, ctx, cont) = status_resp

        status.should_be_a(bytes)
        status.shouldnt_be_empty()

        ctx.should_be_an_integer()

        cont.should_be_a(bool)
        cont.should_be_false()

    def test_acquire_creds(self):
        name = gb.import_name(SERVICE_PRINCIPAL,
                              gb.NameType.kerberos_principal)
        cred_resp = gb.acquire_cred(name)
        cred_resp.shouldnt_be_none()

        (creds, actual_mechs, ttl) = cred_resp

        creds.shouldnt_be_none()
        creds.should_be_a(gb.Creds)

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        ttl.should_be_an_integer()

        gb.release_name(name)
        gb.release_cred(creds)

    @ktu.gssapi_extension_test('cred_imp_exp', 'credentials import-export')
    def test_cred_import_export(self):
        creds = gb.acquire_cred(None).creds
        token = gb.export_cred(creds)
        imported_creds = gb.import_cred(token)

        inquire_orig = gb.inquire_cred(creds, name=True)
        inquire_imp = gb.inquire_cred(imported_creds, name=True)

        gb.compare_name(inquire_orig.name, inquire_imp.name).should_be_true()

    def test_context_time(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(target_name)

        client_token1 = ctx_resp[3]
        client_ctx = ctx_resp[0]
        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name)[0]
        server_resp = gb.accept_sec_context(client_token1,
                                            acceptor_creds=server_creds)
        server_tok = server_resp[3]

        client_resp2 = gb.init_sec_context(target_name,
                                           context=client_ctx,
                                           input_token=server_tok)
        ctx = client_resp2[0]

        ttl = gb.context_time(ctx)

        ttl.should_be_an_integer()
        ttl.should_be_greater_than(0)

    def test_inquire_context(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(target_name)

        client_token1 = ctx_resp[3]
        client_ctx = ctx_resp[0]
        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name)[0]
        server_resp = gb.accept_sec_context(client_token1,
                                            acceptor_creds=server_creds)
        server_tok = server_resp[3]

        client_resp2 = gb.init_sec_context(target_name,
                                           context=client_ctx,
                                           input_token=server_tok)
        ctx = client_resp2[0]

        inq_resp = gb.inquire_context(ctx)
        inq_resp.shouldnt_be_none()

        (src_name, target_name, ttl, mech_type,
         flags, local_est, is_open) = inq_resp

        src_name.shouldnt_be_none()
        src_name.should_be_a(gb.Name)

        target_name.shouldnt_be_none()
        target_name.should_be_a(gb.Name)

        ttl.should_be_an_integer()

        mech_type.shouldnt_be_none()
        mech_type.should_be(gb.MechType.kerberos)

        flags.shouldnt_be_none()
        flags.should_be_a(Set)
        flags.shouldnt_be_empty()

        local_est.should_be_a(bool)
        local_est.should_be_true()

        is_open.should_be_a(bool)
        is_open.should_be_true()

    # NB(directxman12): We don't test `process_context_token` because
    #                   there is no clear non-deprecated way to test it

    @ktu.gssapi_extension_test('s4u', 'S4U')
    def test_add_cred_impersonate_name(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        client_ctx_resp = gb.init_sec_context(target_name)
        client_token = client_ctx_resp[3]
        del client_ctx_resp  # free all the things (except the token)!

        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name, usage='both')[0]
        server_ctx_resp = gb.accept_sec_context(client_token,
                                                acceptor_creds=server_creds)

        input_creds = gb.Creds()
        imp_resp = gb.add_cred_impersonate_name(input_creds,
                                                server_creds,
                                                server_ctx_resp[1],
                                                gb.MechType.kerberos)

        imp_resp.shouldnt_be_none()

        new_creds, actual_mechs, output_init_ttl, output_accept_ttl = imp_resp

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        output_init_ttl.should_be_a(int)
        output_accept_ttl.should_be_a(int)

        new_creds.should_be_a(gb.Creds)

    @ktu.gssapi_extension_test('s4u', 'S4U')
    def test_acquire_creds_impersonate_name(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        client_ctx_resp = gb.init_sec_context(target_name)
        client_token = client_ctx_resp[3]
        del client_ctx_resp  # free all the things (except the token)!

        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name, usage='both')[0]
        server_ctx_resp = gb.accept_sec_context(client_token,
                                                acceptor_creds=server_creds)

        imp_resp = gb.acquire_cred_impersonate_name(server_creds,
                                                    server_ctx_resp[1])

        imp_resp.shouldnt_be_none()

        imp_creds, actual_mechs, output_ttl = imp_resp

        imp_creds.shouldnt_be_none()
        imp_creds.should_be_a(gb.Creds)

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        output_ttl.should_be_a(int)
        # no need to explicitly release any more -- we can just rely on
        # __dealloc__ (b/c cython)

    @ktu.gssapi_extension_test('s4u', 'S4U')
    @ktu.krb_minversion_test('1.11',
                             'returning delegated S4U2Proxy credentials')
    def test_always_get_delegated_creds(self):
        svc_princ = SERVICE_PRINCIPAL.decode("UTF-8")
        self.realm.kinit(svc_princ, flags=['-k', '-f'])

        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)

        client_token = gb.init_sec_context(target_name).token

        # if our acceptor creds have a usage of both, we get
        # s4u2proxy delegated credentials
        server_creds = gb.acquire_cred(None, usage='both').creds
        server_ctx_resp = gb.accept_sec_context(client_token,
                                                acceptor_creds=server_creds)

        server_ctx_resp.shouldnt_be_none()
        server_ctx_resp.delegated_creds.shouldnt_be_none()
        server_ctx_resp.delegated_creds.should_be_a(gb.Creds)

    @ktu.gssapi_extension_test('rfc5588', 'RFC 5588')
    def test_store_cred_acquire_cred(self):
        # we need to acquire a forwardable ticket
        svc_princ = SERVICE_PRINCIPAL.decode("UTF-8")
        self.realm.kinit(svc_princ, flags=['-k', '-f'])

        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)

        client_creds = gb.acquire_cred(None, usage='initiate').creds
        client_ctx_resp = gb.init_sec_context(
            target_name, creds=client_creds,
            flags=gb.RequirementFlag.delegate_to_peer)

        client_token = client_ctx_resp[3]

        server_creds = gb.acquire_cred(None, usage='accept').creds
        server_ctx_resp = gb.accept_sec_context(client_token,
                                                acceptor_creds=server_creds)

        deleg_creds = server_ctx_resp.delegated_creds
        deleg_creds.shouldnt_be_none()
        store_res = gb.store_cred(deleg_creds, usage='initiate',
                                  set_default=True, overwrite=True)

        store_res.shouldnt_be_none()
        store_res.usage.should_be('initiate')
        store_res.mechs.should_include(gb.MechType.kerberos)

        deleg_name = gb.inquire_cred(deleg_creds).name
        acq_resp = gb.acquire_cred(deleg_name, usage='initiate')
        acq_resp.shouldnt_be_none()

    @ktu.gssapi_extension_test('cred_store', 'credentials store')
    def test_store_cred_into_acquire_cred(self):
        CCACHE = 'FILE:{tmpdir}/other_ccache'.format(tmpdir=self.realm.tmpdir)
        KT = '{tmpdir}/other_keytab'.format(tmpdir=self.realm.tmpdir)
        store = {b'ccache': CCACHE.encode('UTF-8'),
                 b'keytab': KT.encode('UTF-8')}

        princ_name = 'service/cs@' + self.realm.realm
        self.realm.addprinc(princ_name)
        self.realm.extract_keytab(princ_name, KT)
        self.realm.kinit(princ_name, None, ['-k', '-t', KT])

        initial_creds = gb.acquire_cred(None, usage='initiate').creds

        # NB(sross): overwrite because the ccache doesn't exist yet
        store_res = gb.store_cred_into(store, initial_creds, overwrite=True)

        store_res.mechs.shouldnt_be_none()
        store_res.usage.should_be('initiate')

        name = gb.import_name(princ_name.encode('UTF-8'))
        retrieve_res = gb.acquire_cred_from(store, name)

        retrieve_res.shouldnt_be_none()
        retrieve_res.creds.shouldnt_be_none()
        retrieve_res.creds.should_be_a(gb.Creds)

        retrieve_res.mechs.shouldnt_be_empty()
        retrieve_res.mechs.should_include(gb.MechType.kerberos)

        retrieve_res.lifetime.should_be_an_integer()

    def test_add_cred(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        client_ctx_resp = gb.init_sec_context(target_name)
        client_token = client_ctx_resp[3]
        del client_ctx_resp  # free all the things (except the token)!

        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name, usage='both')[0]
        server_ctx_resp = gb.accept_sec_context(client_token,
                                                acceptor_creds=server_creds)

        input_creds = gb.Creds()
        imp_resp = gb.add_cred(input_creds,
                               server_ctx_resp[1],
                               gb.MechType.kerberos)

        imp_resp.shouldnt_be_none()

        new_creds, actual_mechs, output_init_ttl, output_accept_ttl = imp_resp

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        output_init_ttl.should_be_a(int)
        output_accept_ttl.should_be_a(int)

        new_creds.should_be_a(gb.Creds)

    # NB(sross): we skip testing add_cred with mutate for the same reasons
    #            that testing add_cred in the high-level API is skipped

    def test_inquire_creds(self):
        name = gb.import_name(SERVICE_PRINCIPAL,
                              gb.NameType.kerberos_principal)
        cred = gb.acquire_cred(name).creds

        inq_resp = gb.inquire_cred(cred)

        inq_resp.shouldnt_be_none()

        inq_resp.name.should_be_a(gb.Name)
        assert gb.compare_name(name, inq_resp.name)

        inq_resp.lifetime.should_be_an_integer()

        inq_resp.usage.should_be('both')

        inq_resp.mechs.shouldnt_be_empty()
        inq_resp.mechs.should_include(gb.MechType.kerberos)

    def test_create_oid_from_bytes(self):
        kerberos_bytes = gb.MechType.kerberos.__bytes__()
        new_oid = gb.OID(elements=kerberos_bytes)

        new_oid.should_be(gb.MechType.kerberos)

        del new_oid  # make sure we can dealloc

    def test_error_dispatch(self):
        err_code1 = gb.ParameterReadError.CALLING_CODE
        err_code2 = gb.BadNameError.ROUTINE_CODE
        err = gb.GSSError(err_code1 | err_code2, 0)

        err.should_be_a(gb.NameReadError)
        err.maj_code.should_be(err_code1 | err_code2)

    def test_inquire_names_for_mech(self):
        res = gb.inquire_names_for_mech(gb.MechType.kerberos)

        res.shouldnt_be_none()
        res.should_include(gb.NameType.kerberos_principal)

    def test_inquire_mechs_for_name(self):
        name = gb.import_name(self.USER_PRINC,
                              gb.NameType.kerberos_principal)

        res = gb.inquire_mechs_for_name(name)

        res.shouldnt_be_none()
        res.should_include(gb.MechType.kerberos)

    @ktu.gssapi_extension_test('password', 'Password')
    def test_acquire_cred_with_password(self):
        password = self.realm.password('user')
        self.realm.kinit(self.realm.user_princ, password=password)

        name = gb.import_name(b'user', gb.NameType.kerberos_principal)

        imp_resp = gb.acquire_cred_with_password(name,
                                                 password.encode('UTF-8'))
        imp_resp.shouldnt_be_none()

        imp_creds, actual_mechs, output_ttl = imp_resp

        imp_creds.shouldnt_be_none()
        imp_creds.should_be_a(gb.Creds)

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        output_ttl.should_be_a(int)

    @ktu.gssapi_extension_test('password_add', 'Password (add)')
    def test_add_cred_with_password(self):
        password = self.realm.password('user')
        self.realm.kinit(self.realm.user_princ, password=password)

        name = gb.import_name(b'user', gb.NameType.kerberos_principal)

        input_creds = gb.Creds()
        imp_resp = gb.add_cred_with_password(input_creds, name,
                                             gb.MechType.kerberos,
                                             password.encode('UTF-8'))
        imp_resp.shouldnt_be_none()

        new_creds, actual_mechs, output_init_ttl, output_accept_ttl = imp_resp

        actual_mechs.shouldnt_be_empty()
        actual_mechs.should_include(gb.MechType.kerberos)

        output_init_ttl.should_be_a(int)
        output_accept_ttl.should_be_a(int)

        new_creds.should_be_a(gb.Creds)

    @ktu.gssapi_extension_test('rfc5587', 'RFC 5587')
    def test_rfc5587(self):
        mechs = gb.indicate_mechs_by_attrs(None, None, None)

        mechs.should_be_a(set)
        mechs.shouldnt_be_empty()

        # We need last_attr to be an attribute on last_mech.
        # Since mechs is of type set and thus not indexable, these
        # are used to track the last visited mech for testing
        # purposes, and saves a call to inquire_attrs_for_mech().
        last_attr = None
        last_mech = None

        for mech in mechs:
            mech.shouldnt_be_none()
            mech.should_be_a(gb.OID)
            last_mech = mech

            inquire_out = gb.inquire_attrs_for_mech(mech)
            mech_attrs = inquire_out.mech_attrs
            known_mech_attrs = inquire_out.known_mech_attrs

            mech_attrs.should_be_a(set)

            known_mech_attrs.should_be_a(set)

            # Verify that we get data for every available
            # attribute. Testing the contents of a few known
            # attributes is done in test_display_mech_attr().
            for mech_attr in mech_attrs:
                mech_attr.shouldnt_be_none()
                mech_attr.should_be_a(gb.OID)

                display_out = gb.display_mech_attr(mech_attr)
                display_out.name.shouldnt_be_none()
                display_out.short_desc.shouldnt_be_none()
                display_out.long_desc.shouldnt_be_none()
                display_out.name.should_be_a(bytes)
                display_out.short_desc.should_be_a(bytes)
                display_out.long_desc.should_be_a(bytes)

                last_attr = mech_attr

            for mech_attr in known_mech_attrs:
                mech_attr.shouldnt_be_none()
                mech_attr.should_be_a(gb.OID)

                display_out = gb.display_mech_attr(mech_attr)
                display_out.name.shouldnt_be_none()
                display_out.short_desc.shouldnt_be_none()
                display_out.long_desc.shouldnt_be_none()
                display_out.name.should_be_a(bytes)
                display_out.short_desc.should_be_a(bytes)
                display_out.long_desc.should_be_a(bytes)

        attrs = set([last_attr])

        mechs = gb.indicate_mechs_by_attrs(attrs, None, None)
        mechs.shouldnt_be_empty()
        mechs.should_include(last_mech)

        mechs = gb.indicate_mechs_by_attrs(None, attrs, None)
        mechs.shouldnt_include(last_mech)

        mechs = gb.indicate_mechs_by_attrs(None, None, attrs)
        mechs.shouldnt_be_empty()
        mechs.should_include(last_mech)

    @ktu.gssapi_extension_test('rfc5587', 'RFC 5587')
    def test_display_mech_attr(self):
        test_attrs = [
            # oid, name, short_desc, long_desc
            # Taken from krb5/src/tests/gssapi/t_saslname
            [gb.OID.from_int_seq("1.3.6.1.5.5.13.24"), b"GSS_C_MA_CBINDINGS",
             b"channel-bindings", b"Mechanism supports channel bindings."],
            [gb.OID.from_int_seq("1.3.6.1.5.5.13.1"),
             b"GSS_C_MA_MECH_CONCRETE", b"concrete-mech",
             b"Mechanism is neither a pseudo-mechanism nor a composite "
             b"mechanism."]
        ]

        for attr in test_attrs:
            display_out = gb.display_mech_attr(attr[0])
            display_out.name.should_be(attr[1])
            display_out.short_desc.should_be(attr[2])
            display_out.long_desc.should_be(attr[3])

    @ktu.gssapi_extension_test('rfc5801', 'SASL Names')
    def test_sasl_names(self):
        mechs = gb.indicate_mechs()

        for mech in mechs:
            out = gb.inquire_saslname_for_mech(mech)

            out_smn = out.sasl_mech_name
            out_smn.shouldnt_be_none()
            out_smn.should_be_a(bytes)
            out_smn.shouldnt_be_empty()

            out_mn = out.mech_name
            out_mn.shouldnt_be_none()
            out_mn.should_be_a(bytes)

            out_md = out.mech_description
            out_md.shouldnt_be_none()
            out_md.should_be_a(bytes)

            cmp_mech = gb.inquire_mech_for_saslname(out_smn)
            cmp_mech.shouldnt_be_none()
            cmp_mech.should_be(mech)

    @ktu.gssapi_extension_test('ggf', 'Global Grid Forum')
    @ktu.gssapi_extension_test('s4u', 'S4U')
    @ktu.krb_minversion_test('1.16',
                             'querying impersonator name of krb5 GSS '
                             'Credential using the '
                             'GSS_KRB5_GET_CRED_IMPERSONATOR OID')
    def test_inquire_cred_by_oid_impersonator(self):
        svc_princ = SERVICE_PRINCIPAL.decode("UTF-8")
        self.realm.kinit(svc_princ, flags=['-k', '-f'])

        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)

        client_token = gb.init_sec_context(target_name).token

        # if our acceptor creds have a usage of both, we get
        # s4u2proxy delegated credentials
        server_creds = gb.acquire_cred(None, usage='both').creds
        server_ctx_resp = gb.accept_sec_context(client_token,
                                                acceptor_creds=server_creds)

        server_ctx_resp.shouldnt_be_none()
        server_ctx_resp.delegated_creds.shouldnt_be_none()
        server_ctx_resp.delegated_creds.should_be_a(gb.Creds)

        # GSS_KRB5_GET_CRED_IMPERSONATOR
        oid = gb.OID.from_int_seq("1.2.840.113554.1.2.2.5.14")
        info = gb.inquire_cred_by_oid(server_ctx_resp.delegated_creds, oid)

        info.should_be_a(list)
        info.shouldnt_be_empty()
        info[0].should_be_a(bytes)
        info[0].should_be(b"%s@%s" % (SERVICE_PRINCIPAL,
                                      self.realm.realm.encode('utf-8')))

    @ktu.gssapi_extension_test('ggf', 'Global Grid Forum')
    def test_inquire_sec_context_by_oid(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        ctx_resp1 = gb.init_sec_context(target_name)

        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name)[0]
        server_resp = gb.accept_sec_context(ctx_resp1[3],
                                            acceptor_creds=server_creds)
        server_ctx = server_resp[0]
        server_tok = server_resp[3]

        client_resp2 = gb.init_sec_context(target_name,
                                           context=ctx_resp1[0],
                                           input_token=server_tok)
        client_ctx = client_resp2[0]

        # GSS_C_INQ_SSPI_SESSION_KEY
        session_key_oid = gb.OID.from_int_seq("1.2.840.113554.1.2.2.5.5")

        client_key = gb.inquire_sec_context_by_oid(client_ctx, session_key_oid)
        server_key = gb.inquire_sec_context_by_oid(server_ctx, session_key_oid)

        client_key.should_be_a(list)
        client_key.shouldnt_be_empty()
        server_key.should_be_a(list)
        server_key.shouldnt_be_empty()
        client_key.should_have_same_items_as(server_key)

    @ktu.gssapi_extension_test('ggf', 'Global Grid Forum')
    def test_inquire_sec_context_by_oid_should_raise_error(self):
        target_name = gb.import_name(TARGET_SERVICE_NAME,
                                     gb.NameType.hostbased_service)
        ctx_resp1 = gb.init_sec_context(target_name)

        server_name = gb.import_name(SERVICE_PRINCIPAL,
                                     gb.NameType.kerberos_principal)
        server_creds = gb.acquire_cred(server_name)[0]
        server_resp = gb.accept_sec_context(ctx_resp1[3],
                                            acceptor_creds=server_creds)

        client_resp2 = gb.init_sec_context(target_name,
                                           context=ctx_resp1[0],
                                           input_token=server_resp[3])
        client_ctx = client_resp2[0]

        invalid_oid = gb.OID.from_int_seq("1.2.3.4.5.6.7.8.9")
        gb.inquire_sec_context_by_oid.should_raise(gb.GSSError, client_ctx,
                                                   invalid_oid)

    @ktu.gssapi_extension_test('ggf', 'Global Grid Forum')
    @ktu.gssapi_extension_test('password', 'Add Credential with Password')
    def test_set_sec_context_option(self):
        ntlm_mech = gb.OID.from_int_seq("1.3.6.1.4.1.311.2.2.10")
        username = gb.import_name(name=b"user",
                                  name_type=gb.NameType.user)
        try:
            cred = gb.acquire_cred_with_password(name=username,
                                                 password=b"password",
                                                 mechs=[ntlm_mech])
        except gb.GSSError:
            self.skipTest('You do not have the GSSAPI gss-ntlmssp mech '
                          'installed')

        server = gb.import_name(name=b"server",
                                name_type=gb.NameType.hostbased_service)
        orig_context = gb.init_sec_context(server, creds=cred.creds,
                                           mech=ntlm_mech)[0]

        # GSS_NTLMSSP_RESET_CRYPTO_OID_STRING
        reset_mech = gb.OID.from_int_seq("1.3.6.1.4.1.7165.655.1.3")
        out_context = gb.set_sec_context_option(reset_mech,
                                                context=orig_context,
                                                value=b"\x00" * 4)
        out_context.should_be_a(gb.SecurityContext)

    @ktu.gssapi_extension_test('ggf', 'Global Grid Forum')
    @ktu.gssapi_extension_test('password', 'Add Credential with Password')
    def test_set_sec_context_option_fail(self):
        ntlm_mech = gb.OID.from_int_seq("1.3.6.1.4.1.311.2.2.10")
        username = gb.import_name(name=b"user",
                                  name_type=gb.NameType.user)
        try:
            cred = gb.acquire_cred_with_password(name=username,
                                                 password=b"password",
                                                 mechs=[ntlm_mech])
        except gb.GSSError:
            self.skipTest('You do not have the GSSAPI gss-ntlmssp mech '
                          'installed')

        server = gb.import_name(name=b"server",
                                name_type=gb.NameType.hostbased_service)
        context = gb.init_sec_context(server, creds=cred.creds,
                                      mech=ntlm_mech)[0]

        # GSS_NTLMSSP_RESET_CRYPTO_OID_STRING
        reset_mech = gb.OID.from_int_seq("1.3.6.1.4.1.7165.655.1.3")

        # will raise a GSSError if no data was passed in
        gb.set_sec_context_option.should_raise(gb.GSSError, reset_mech,
                                               context)

    @ktu.gssapi_extension_test('set_cred_opt', 'Kitten Set Credential Option')
    @ktu.krb_minversion_test('1.14',
                             'GSS_KRB5_CRED_NO_CI_FLAGS_X was added in MIT '
                             'krb5 1.14')
    def test_set_cred_option(self):
        name = gb.import_name(SERVICE_PRINCIPAL,
                              gb.NameType.kerberos_principal)
        # GSS_KRB5_CRED_NO_CI_FLAGS_X
        no_ci_flags_x = gb.OID.from_int_seq("1.2.752.43.13.29")
        orig_cred = gb.acquire_cred(name).creds

        # nothing much we can test here apart from it doesn't fail and the
        # id of the return cred is the same as the input one
        output_cred = gb.set_cred_option(no_ci_flags_x, creds=orig_cred)
        output_cred.should_be_a(gb.Creds)

    @ktu.gssapi_extension_test('set_cred_opt', 'Kitten Set Credential Option')
    def test_set_cred_option_should_raise_error(self):
        name = gb.import_name(SERVICE_PRINCIPAL,
                              gb.NameType.kerberos_principal)
        orig_cred = gb.acquire_cred(name).creds

        # this is a fake OID and shouldn't work at all
        invalid_oid = gb.OID.from_int_seq("1.2.3.4.5.6.7.8.9")
        gb.set_cred_option.should_raise(gb.GSSError, invalid_oid, orig_cred,
                                        b"\x00")


class TestIntEnumFlagSet(unittest.TestCase):
    def test_create_from_int(self):
        int_val = (gb.RequirementFlag.integrity |
                   gb.RequirementFlag.confidentiality)
        fset = gb.IntEnumFlagSet(gb.RequirementFlag, int_val)

        int(fset).should_be(int_val)

    def test_create_from_other_set(self):
        int_val = (gb.RequirementFlag.integrity |
                   gb.RequirementFlag.confidentiality)
        fset1 = gb.IntEnumFlagSet(gb.RequirementFlag, int_val)
        fset2 = gb.IntEnumFlagSet(gb.RequirementFlag, fset1)

        fset1.should_be(fset2)

    def test_create_from_list(self):
        lst = [gb.RequirementFlag.integrity,
               gb.RequirementFlag.confidentiality]
        fset = gb.IntEnumFlagSet(gb.RequirementFlag, lst)

        list(fset).should_have_same_items_as(lst)

    def test_create_empty(self):
        fset = gb.IntEnumFlagSet(gb.RequirementFlag)
        fset.should_be_empty()

    def _create_fset(self):
        lst = [gb.RequirementFlag.integrity,
               gb.RequirementFlag.confidentiality]
        return gb.IntEnumFlagSet(gb.RequirementFlag, lst)

    def test_contains(self):
        fset = self._create_fset()
        fset.should_include(gb.RequirementFlag.integrity)
        fset.shouldnt_include(gb.RequirementFlag.protection_ready)

    def test_len(self):
        self._create_fset().should_have_length(2)

    def test_add(self):
        fset = self._create_fset()
        fset.should_have_length(2)

        fset.add(gb.RequirementFlag.protection_ready)
        fset.should_have_length(3)
        fset.should_include(gb.RequirementFlag.protection_ready)

    def test_discard(self):
        fset = self._create_fset()
        fset.should_have_length(2)

        fset.discard(gb.RequirementFlag.protection_ready)
        fset.should_have_length(2)

        fset.discard(gb.RequirementFlag.integrity)
        fset.should_have_length(1)
        fset.shouldnt_include(gb.RequirementFlag.integrity)

    def test_and_enum(self):
        fset = self._create_fset()
        (fset & gb.RequirementFlag.integrity).should_be_true()
        (fset & gb.RequirementFlag.protection_ready).should_be_false()

    def test_and_int(self):
        fset = self._create_fset()
        int_val = int(gb.RequirementFlag.integrity)

        (fset & int_val).should_be(int_val)

    def test_and_set(self):
        fset1 = self._create_fset()
        fset2 = self._create_fset()
        fset3 = self._create_fset()

        fset1.add(gb.RequirementFlag.protection_ready)
        fset2.add(gb.RequirementFlag.out_of_sequence_detection)

        (fset1 & fset2).should_be(fset3)

    def test_or_enum(self):
        fset1 = self._create_fset()
        fset2 = fset1 | gb.RequirementFlag.protection_ready

        (fset1 < fset2).should_be_true()
        fset2.should_include(gb.RequirementFlag.protection_ready)

    def test_or_int(self):
        fset = self._create_fset()
        int_val = int(gb.RequirementFlag.integrity)

        (fset | int_val).should_be(int(fset))

    def test_or_set(self):
        fset1 = self._create_fset()
        fset2 = self._create_fset()
        fset3 = self._create_fset()

        fset1.add(gb.RequirementFlag.protection_ready)
        fset2.add(gb.RequirementFlag.out_of_sequence_detection)
        fset3.add(gb.RequirementFlag.protection_ready)
        fset3.add(gb.RequirementFlag.out_of_sequence_detection)

        (fset1 | fset2).should_be(fset3)

    def test_xor_enum(self):
        fset1 = self._create_fset()

        fset2 = fset1 ^ gb.RequirementFlag.protection_ready
        fset3 = fset1 ^ gb.RequirementFlag.integrity

        fset2.should_have_length(3)
        fset2.should_include(gb.RequirementFlag.protection_ready)

        fset3.should_have_length(1)
        fset3.shouldnt_include(gb.RequirementFlag.integrity)

    def test_xor_int(self):
        fset = self._create_fset()

        (fset ^ int(gb.RequirementFlag.protection_ready)).should_be(
            int(fset) ^ gb.RequirementFlag.protection_ready)

        (fset ^ int(gb.RequirementFlag.integrity)).should_be(
            int(fset) ^ gb.RequirementFlag.integrity)

    def test_xor_set(self):
        fset1 = self._create_fset()
        fset2 = self._create_fset()

        fset1.add(gb.RequirementFlag.protection_ready)
        fset2.add(gb.RequirementFlag.out_of_sequence_detection)

        fset3 = fset1 ^ fset2
        fset3.should_have_length(2)
        fset3.shouldnt_include(gb.RequirementFlag.integrity)
        fset3.shouldnt_include(gb.RequirementFlag.confidentiality)
        fset3.should_include(gb.RequirementFlag.protection_ready)
        fset3.should_include(gb.RequirementFlag.out_of_sequence_detection)


class TestInitContext(_GSSAPIKerberosTestCase):
    def setUp(self):
        self.target_name = gb.import_name(TARGET_SERVICE_NAME,
                                          gb.NameType.hostbased_service)

    def tearDown(self):
        gb.release_name(self.target_name)

    def test_basic_init_default_ctx(self):
        ctx_resp = gb.init_sec_context(self.target_name)
        ctx_resp.shouldnt_be_none()

        (ctx, out_mech_type,
         out_req_flags, out_token, out_ttl, cont_needed) = ctx_resp

        ctx.shouldnt_be_none()
        ctx.should_be_a(gb.SecurityContext)

        out_mech_type.should_be(gb.MechType.kerberos)

        out_req_flags.should_be_a(Set)
        out_req_flags.should_be_at_least_length(2)

        out_token.shouldnt_be_empty()

        out_ttl.should_be_greater_than(0)

        cont_needed.should_be_a(bool)

        gb.delete_sec_context(ctx)


class TestAcceptContext(_GSSAPIKerberosTestCase):

    def setUp(self):
        self.target_name = gb.import_name(TARGET_SERVICE_NAME,
                                          gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(self.target_name)

        self.client_token = ctx_resp[3]
        self.client_ctx = ctx_resp[0]
        self.client_ctx.shouldnt_be_none()

        self.server_name = gb.import_name(SERVICE_PRINCIPAL,
                                          gb.NameType.kerberos_principal)
        self.server_creds = gb.acquire_cred(self.server_name)[0]

        self.server_ctx = None

    def tearDown(self):
        gb.release_name(self.target_name)
        gb.release_name(self.server_name)
        gb.release_cred(self.server_creds)
        gb.delete_sec_context(self.client_ctx)

        if self.server_ctx is not None:
            gb.delete_sec_context(self.server_ctx)

    def test_basic_accept_context_no_acceptor_creds(self):
        server_resp = gb.accept_sec_context(self.client_token)
        server_resp.shouldnt_be_none()

        (self.server_ctx, name, mech_type, out_token,
         out_req_flags, out_ttl, delegated_cred, cont_needed) = server_resp

        self.server_ctx.shouldnt_be_none()
        self.server_ctx.should_be_a(gb.SecurityContext)

        name.shouldnt_be_none()
        name.should_be_a(gb.Name)

        mech_type.should_be(gb.MechType.kerberos)

        out_token.shouldnt_be_empty()

        out_req_flags.should_be_a(Set)
        out_req_flags.should_be_at_least_length(2)

        out_ttl.should_be_greater_than(0)

        if delegated_cred is not None:
            delegated_cred.should_be_a(gb.Creds)

        cont_needed.should_be_a(bool)

    def test_basic_accept_context(self):
        server_resp = gb.accept_sec_context(self.client_token,
                                            acceptor_creds=self.server_creds)
        server_resp.shouldnt_be_none()

        (self.server_ctx, name, mech_type, out_token,
         out_req_flags, out_ttl, delegated_cred, cont_needed) = server_resp

        self.server_ctx.shouldnt_be_none()
        self.server_ctx.should_be_a(gb.SecurityContext)

        name.shouldnt_be_none()
        name.should_be_a(gb.Name)

        mech_type.should_be(gb.MechType.kerberos)

        out_token.shouldnt_be_empty()

        out_req_flags.should_be_a(Set)
        out_req_flags.should_be_at_least_length(2)

        out_ttl.should_be_greater_than(0)

        if delegated_cred is not None:
            delegated_cred.should_be_a(gb.Creds)

        cont_needed.should_be_a(bool)

    def test_channel_bindings(self):
        bdgs = gb.ChannelBindings(application_data=b'abcxyz',
                                  initiator_address_type=gb.AddressType.ip,
                                  initiator_address=b'127.0.0.1',
                                  acceptor_address_type=gb.AddressType.ip,
                                  acceptor_address=b'127.0.0.1')
        self.target_name = gb.import_name(TARGET_SERVICE_NAME,
                                          gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(self.target_name,
                                       channel_bindings=bdgs)

        self.client_token = ctx_resp[3]
        self.client_ctx = ctx_resp[0]
        self.client_ctx.shouldnt_be_none()

        self.server_name = gb.import_name(SERVICE_PRINCIPAL,
                                          gb.NameType.kerberos_principal)
        self.server_creds = gb.acquire_cred(self.server_name)[0]

        server_resp = gb.accept_sec_context(self.client_token,
                                            acceptor_creds=self.server_creds,
                                            channel_bindings=bdgs)
        server_resp.shouldnt_be_none
        self.server_ctx = server_resp.context

    def test_bad_channel_binding_raises_error(self):
        bdgs = gb.ChannelBindings(application_data=b'abcxyz',
                                  initiator_address_type=gb.AddressType.ip,
                                  initiator_address=b'127.0.0.1',
                                  acceptor_address_type=gb.AddressType.ip,
                                  acceptor_address=b'127.0.0.1')
        self.target_name = gb.import_name(TARGET_SERVICE_NAME,
                                          gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(self.target_name,
                                       channel_bindings=bdgs)

        self.client_token = ctx_resp[3]
        self.client_ctx = ctx_resp[0]
        self.client_ctx.shouldnt_be_none()

        self.server_name = gb.import_name(SERVICE_PRINCIPAL,
                                          gb.NameType.kerberos_principal)
        self.server_creds = gb.acquire_cred(self.server_name)[0]

        bdgs.acceptor_address = b'127.0.1.0'
        gb.accept_sec_context.should_raise(gb.GSSError, self.client_token,
                                           acceptor_creds=self.server_creds,
                                           channel_bindings=bdgs)


class TestWrapUnwrap(_GSSAPIKerberosTestCase):
    def setUp(self):
        self.target_name = gb.import_name(TARGET_SERVICE_NAME,
                                          gb.NameType.hostbased_service)
        ctx_resp = gb.init_sec_context(self.target_name)

        self.client_token1 = ctx_resp[3]
        self.client_ctx = ctx_resp[0]
        self.server_name = gb.import_name(SERVICE_PRINCIPAL,
                                          gb.NameType.kerberos_principal)
        self.server_creds = gb.acquire_cred(self.server_name)[0]
        server_resp = gb.accept_sec_context(self.client_token1,
                                            acceptor_creds=self.server_creds)
        self.server_ctx = server_resp[0]
        self.server_tok = server_resp[3]

        client_resp2 = gb.init_sec_context(self.target_name,
                                           context=self.client_ctx,
                                           input_token=self.server_tok)
        self.client_token2 = client_resp2[3]
        self.client_ctx = client_resp2[0]

    def tearDown(self):
        gb.release_name(self.target_name)
        gb.release_name(self.server_name)
        gb.release_cred(self.server_creds)
        gb.delete_sec_context(self.client_ctx)
        gb.delete_sec_context(self.server_ctx)

    def test_import_export_sec_context(self):
        tok = gb.export_sec_context(self.client_ctx)

        tok.shouldnt_be_none()
        tok.should_be_a(bytes)
        tok.shouldnt_be_empty()

        imported_ctx = gb.import_sec_context(tok)
        imported_ctx.shouldnt_be_none()
        imported_ctx.should_be_a(gb.SecurityContext)

        self.client_ctx = imported_ctx  # ensure that it gets deleted

    def test_get_mic(self):
        mic_token = gb.get_mic(self.client_ctx, b"some message")

        mic_token.shouldnt_be_none()
        mic_token.should_be_a(bytes)
        mic_token.shouldnt_be_empty()

    def test_basic_verify_mic(self):
        mic_token = gb.get_mic(self.client_ctx, b"some message")

        qop_used = gb.verify_mic(self.server_ctx, b"some message", mic_token)

        qop_used.should_be_an_integer()

        # test a bad MIC
        gb.verify_mic.should_raise(gb.GSSError, self.server_ctx,
                                   b"some other message", b"some invalid mic")

    def test_wrap_size_limit(self):
        with_conf = gb.wrap_size_limit(self.client_ctx, 100)
        without_conf = gb.wrap_size_limit(self.client_ctx, 100,
                                          confidential=False)

        with_conf.should_be_an_integer()
        without_conf.should_be_an_integer()

        without_conf.should_be_less_than(100)
        with_conf.should_be_less_than(100)

    def test_basic_wrap_unwrap(self):
        (wrapped_message, conf) = gb.wrap(self.client_ctx, b'test message')

        conf.should_be_a(bool)
        conf.should_be_true()

        wrapped_message.should_be_a(bytes)
        wrapped_message.shouldnt_be_empty()
        wrapped_message.should_be_longer_than('test message')

        (unwrapped_message, conf, qop) = gb.unwrap(self.server_ctx,
                                                   wrapped_message)
        conf.should_be_a(bool)
        conf.should_be_true()

        qop.should_be_an_integer()
        qop.should_be_at_least(0)

        unwrapped_message.should_be_a(bytes)
        unwrapped_message.shouldnt_be_empty()
        unwrapped_message.should_be(b'test message')

    @ktu.gssapi_extension_test('dce', 'DCE (IOV/AEAD)')
    def test_basic_iov_wrap_unwrap_prealloc(self):
        init_data = b'some encrypted data'
        init_other_data = b'some other encrypted data'
        init_signed_info = b'some sig data'
        init_message = gb.IOV((gb.IOVBufferType.sign_only, init_signed_info),
                              init_data, init_other_data, auto_alloc=False)

        init_message[0].allocate.should_be_false()
        init_message[4].allocate.should_be_false()
        init_message[5].allocate.should_be_false()

        conf = gb.wrap_iov_length(self.client_ctx, init_message)

        conf.should_be_a(bool)
        conf.should_be_true()

        init_message[0].should_be_at_least_size(1)
        init_message[5].should_be_at_least_size(1)

        conf = gb.wrap_iov(self.client_ctx, init_message)

        conf.should_be_a(bool)
        conf.should_be_true()

        # make sure we didn't strings used
        init_data.should_be(b'some encrypted data')
        init_other_data.should_be(b'some other encrypted data')
        init_signed_info.should_be(b'some sig data')

        init_message[2].value.shouldnt_be(b'some encrypted data')
        init_message[3].value.shouldnt_be(b'some other encrypted data')

        (conf, qop) = gb.unwrap_iov(self.server_ctx, init_message)

        conf.should_be_a(bool)
        conf.should_be_true()

        qop.should_be_a(int)

        init_message[1].value.should_be(init_signed_info)
        init_message[2].value.should_be(init_data)
        init_message[3].value.should_be(init_other_data)

    @ktu.gssapi_extension_test('dce', 'DCE (IOV/AEAD)')
    def test_basic_iov_wrap_unwrap_autoalloc(self):
        init_data = b'some encrypted data'
        init_other_data = b'some other encrypted data'
        init_signed_info = b'some sig data'
        init_message = gb.IOV((gb.IOVBufferType.sign_only, init_signed_info),
                              init_data, init_other_data)

        conf = gb.wrap_iov(self.client_ctx, init_message)

        conf.should_be_a(bool)
        conf.should_be_true()

        # make sure we didn't strings used
        init_data.should_be(b'some encrypted data')
        init_other_data.should_be(b'some other encrypted data')
        init_signed_info.should_be(b'some sig data')

        init_message[2].value.shouldnt_be(b'some encrypted data')
        init_message[3].value.shouldnt_be(b'some other encrypted data')

        (conf, qop) = gb.unwrap_iov(self.server_ctx, init_message)

        conf.should_be_a(bool)
        conf.should_be_true()

        qop.should_be_a(int)

        init_message[1].value.should_be(init_signed_info)
        init_message[2].value.should_be(init_data)
        init_message[3].value.should_be(init_other_data)

    @ktu.gssapi_extension_test('dce', 'DCE (IOV/AEAD)')
    def test_basic_aead_wrap_unwrap(self):
        assoc_data = b'some sig data'
        (wrapped_message, conf) = gb.wrap_aead(self.client_ctx,
                                               b'test message', assoc_data)

        conf.should_be_a(bool)
        conf.should_be_true()

        wrapped_message.should_be_a(bytes)
        wrapped_message.shouldnt_be_empty()
        wrapped_message.should_be_longer_than('test message')

        (unwrapped_message, conf, qop) = gb.unwrap_aead(self.server_ctx,
                                                        wrapped_message,
                                                        assoc_data)
        conf.should_be_a(bool)
        conf.should_be_true()

        qop.should_be_an_integer()
        qop.should_be_at_least(0)

        unwrapped_message.should_be_a(bytes)
        unwrapped_message.shouldnt_be_empty()
        unwrapped_message.should_be(b'test message')

    @ktu.gssapi_extension_test('dce', 'DCE (IOV/AEAD)')
    def test_basic_aead_wrap_unwrap_no_assoc(self):
        (wrapped_message, conf) = gb.wrap_aead(self.client_ctx,
                                               b'test message')

        conf.should_be_a(bool)
        conf.should_be_true()

        wrapped_message.should_be_a(bytes)
        wrapped_message.shouldnt_be_empty()
        wrapped_message.should_be_longer_than('test message')

        (unwrapped_message, conf, qop) = gb.unwrap_aead(self.server_ctx,
                                                        wrapped_message)
        conf.should_be_a(bool)
        conf.should_be_true()

        qop.should_be_an_integer()
        qop.should_be_at_least(0)

        unwrapped_message.should_be_a(bytes)
        unwrapped_message.shouldnt_be_empty()
        unwrapped_message.should_be(b'test message')

    @ktu.gssapi_extension_test('dce', 'DCE (IOV/AEAD)')
    def test_basic_aead_wrap_unwrap_bad_assoc_raises_error(self):
        assoc_data = b'some sig data'
        (wrapped_message, conf) = gb.wrap_aead(self.client_ctx,
                                               b'test message', assoc_data)

        conf.should_be_a(bool)
        conf.should_be_true()

        wrapped_message.should_be_a(bytes)
        wrapped_message.shouldnt_be_empty()
        wrapped_message.should_be_longer_than('test message')

        gb.unwrap_aead.should_raise(gb.BadMICError, self.server_ctx,
                                    wrapped_message, b'some other sig data')

    @ktu.gssapi_extension_test('iov_mic', 'IOV MIC')
    def test_get_mic_iov(self):
        init_message = gb.IOV(b'some data',
                              (gb.IOVBufferType.sign_only, b'some sig data'),
                              gb.IOVBufferType.mic_token, std_layout=False)

        gb.get_mic_iov(self.client_ctx, init_message)

        init_message[2].type.should_be(gb.IOVBufferType.mic_token)
        init_message[2].value.shouldnt_be_empty()

    @ktu.gssapi_extension_test('iov_mic', 'IOV MIC')
    def test_basic_verify_mic_iov(self):
        init_message = gb.IOV(b'some data',
                              (gb.IOVBufferType.sign_only, b'some sig data'),
                              gb.IOVBufferType.mic_token, std_layout=False)

        gb.get_mic_iov(self.client_ctx, init_message)

        init_message[2].type.should_be(gb.IOVBufferType.mic_token)
        init_message[2].value.shouldnt_be_empty()

        qop_used = gb.verify_mic_iov(self.server_ctx, init_message)

        qop_used.should_be_an_integer()

    @ktu.gssapi_extension_test('iov_mic', 'IOV MIC')
    def test_verify_mic_iov_bad_mic_raises_error(self):
        init_message = gb.IOV(b'some data',
                              (gb.IOVBufferType.sign_only, b'some sig data'),
                              (gb.IOVBufferType.mic_token, 'abaava'),
                              std_layout=False)

        # test a bad MIC
        gb.verify_mic_iov.should_raise(gb.GSSError, self.server_ctx,
                                       init_message)

    @ktu.gssapi_extension_test('iov_mic', 'IOV MIC')
    def test_get_mic_iov_length(self):
        init_message = gb.IOV(b'some data',
                              (gb.IOVBufferType.sign_only, b'some sig data'),
                              gb.IOVBufferType.mic_token, std_layout=False,
                              auto_alloc=False)

        gb.get_mic_iov_length(self.client_ctx, init_message)

        init_message[2].type.should_be(gb.IOVBufferType.mic_token)
        init_message[2].value.shouldnt_be_empty()


TEST_OIDS = {'SPNEGO': {'bytes': b'\053\006\001\005\005\002',
                        'string': '1.3.6.1.5.5.2'},
             'KRB5': {'bytes': b'\052\206\110\206\367\022\001\002\002',
                      'string': '1.2.840.113554.1.2.2'},
             'KRB5_OLD': {'bytes': b'\053\005\001\005\002',
                          'string': '1.3.5.1.5.2'},
             'KRB5_WRONG': {'bytes': b'\052\206\110\202\367\022\001\002\002',
                            'string': '1.2.840.48018.1.2.2'},
             'IAKERB': {'bytes': b'\053\006\001\005\002\005',
                        'string': '1.3.6.1.5.2.5'}}


class TestOIDTransforms(unittest.TestCase):
    def test_decode_from_bytes(self):
        for oid in TEST_OIDS.values():
            o = gb.OID(elements=oid['bytes'])
            text = repr(o)
            text.should_be("<OID {0}>".format(oid['string']))

    def test_encode_from_string(self):
        for oid in TEST_OIDS.values():
            o = gb.OID.from_int_seq(oid['string'])
            o.__bytes__().should_be(oid['bytes'])

    def test_encode_from_int_seq(self):
        for oid in TEST_OIDS.values():
            int_seq = oid['string'].split('.')
            o = gb.OID.from_int_seq(int_seq)
            o.__bytes__().should_be(oid['bytes'])

    def test_comparisons(self):
        krb5 = gb.OID.from_int_seq(TEST_OIDS['KRB5']['string'])
        krb5_other = gb.OID.from_int_seq(TEST_OIDS['KRB5']['string'])
        spnego = gb.OID.from_int_seq(TEST_OIDS['SPNEGO']['string'])

        (krb5 == krb5_other).should_be(True)
        (krb5 == spnego).should_be(False)
        (krb5 != krb5_other).should_be(False)
        (krb5 != spnego).should_be(True)
