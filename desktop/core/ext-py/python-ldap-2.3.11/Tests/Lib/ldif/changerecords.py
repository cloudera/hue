import sys,StringIO,ldap,ldif

test_records = (
  (
    'cn=Michael Str\303\266der,dc=stroeder,dc=com',
    [
      ('objectClass',['person','organizationalPerson','inetOrgPerson']),
      ('cn;lang-de',['Michael Str\303\266der']),
      ('cn;lang-en',['Michael Stroeder']),
      ('bin',['\000\001\002'*200]),
      ('leadingspace',[' this strings contains a leading space']),
      ('trailingspace',['this strings contains a trailing space (']),
    ],
  ),
  (
    'cn=Michael Str\303\266der,dc=stroeder,dc=com',
    [
      ('objectClass',['person','pilotPerson']),
      ('cn',['Michael Str\303\266der','Michael Stroeder']),
      ('sn',['Str\303\266der']),
    ]
  ),
  (
    'cn=Michael Str\303\266der,dc=stroeder,dc=com',
    [
      (ldif.MOD_OP_INTEGER['replace'],'objectClass',['person','pilotPerson']),
      (ldif.MOD_OP_INTEGER['add'],'cn',['Michael Str\303\266deqr','Michael Stroeder']),
      (ldif.MOD_OP_INTEGER['delete'],'sn',['Str\303\266der']),
      (ldif.MOD_OP_INTEGER['delete'],'sn',None),
    ]
  ),
)

f = StringIO.StringIO()
ldif_writer = ldif.LDIFWriter(f)
ldif_writer_debug = ldif.LDIFWriter(sys.stdout)
for dn,record in test_records:
  ldif_writer.unparse(dn,record)
  ldif_writer_debug.unparse(dn,record)
test_entry_ldif = f.getvalue()
f.close()

ldif_parser = ldif.LDIFRecordList(StringIO.StringIO(test_entry_ldif))
ldif_parser.parse()

import pprint

pprint.pprint(ldif_parser.all_records)
