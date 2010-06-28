import sys,pprint,ldap,ldap.schema

schema_attrs = ldap.schema.SCHEMA_ATTRS

ldap.set_option(ldap.OPT_DEBUG_LEVEL,0)

ldap._trace_level = 0

subschemasubentry_dn,schema = ldap.schema.urlfetch(sys.argv[-1])

if subschemasubentry_dn is None:
  print 'No sub schema sub entry found!'
  sys.exit(1)

oc_list = [
  'person',
  'organizationalPerson',
  'inetOrgPerson',
]
struct_oc = schema.get_structural_oc(oc_list)
#print str(schema.get_obj(ldap.schema.ObjectClass,struct_oc))
pprint.pprint(schema.get_applicable_aux_classes(struct_oc))
pprint.pprint(schema.attribute_types(oc_list))
