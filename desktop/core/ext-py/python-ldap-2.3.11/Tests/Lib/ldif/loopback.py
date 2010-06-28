import sys,ldif,StringIO

test_entry_records = [
  (
    'cn=Michael Str\303\266der,dc=stroeder,dc=com',
    {
      'objectClass':['person','organizationalPerson','inetOrgPerson'],
      'cn;lang-de':['Michael Str\303\266der'],
      'cn;lang-en':['Michael Stroeder'],
      'bin':['\000\001\002'*3000],
      'leadingspace':[' this strings contains a leading space'],
      'trailingspace':['this strings contains a trailing space '],
      'emptyvalue':['',''],
      'singlespace':[' '],
    },
  )
]

test_entry_ldif = """dn:
emptyvalue:
emptyvalue: 
emptyvalue:  

"""

ldif_parser = ldif.LDIFRecordList(StringIO.StringIO(test_entry_ldif))
ldif_parser.parse()
test_entry_records.extend(ldif_parser.all_records)

for test_dn,test_entry in test_entry_records:
  ldif_lines = ldif.CreateLDIF(
    test_dn,test_entry,['bin']
  )
  sys.stdout.write(ldif_lines)
  ldif_parser = ldif.LDIFRecordList(StringIO.StringIO(ldif_lines))
  ldif_parser.parse()
  result_entry = ldif_parser.all_records[0][1]
#  print test_entry
  for a in test_entry.keys():
    test_entry[a].sort();result_entry[a].sort()
    if test_entry[a]!=result_entry[a]:
      print 'Error in attribute %s: "%s"!="%s"' % (
        a,repr(test_entry[a]),repr(result_entry[a])
      )

