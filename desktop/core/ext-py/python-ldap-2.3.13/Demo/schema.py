import sys,ldap,ldap.schema

schema_attrs = ldap.schema.SCHEMA_ATTRS

ldap.set_option(ldap.OPT_DEBUG_LEVEL,0)

ldap._trace_level = 0

subschemasubentry_dn,schema = ldap.schema.urlfetch(sys.argv[-1])

schema_reverse = ldap.schema.SubSchema(schema.ldap_entry())

if subschemasubentry_dn is None:
  print 'No sub schema sub entry found!'
  sys.exit(1)

print '*** Schema from',repr(subschemasubentry_dn)

# Display schema
for attr_type,schema_class in ldap.schema.SCHEMA_CLASS_MAPPING.items():
  print '*'*20,attr_type,'*'*20
  for element_id in schema.listall(schema_class):
    se_orig = schema.get_obj(schema_class,element_id)
    se_reverse = schema_reverse.get_obj(schema_class,element_id)
#    assert str(se_orig)==str(se_reverse)
    print attr_type,str(se_orig)
print '*** Testing object class inetOrgPerson ***'

inetOrgPerson = schema.get_obj(ldap.schema.ObjectClass,'inetOrgPerson')
if not inetOrgPerson is None:
  print inetOrgPerson.must,inetOrgPerson.may

print '*** person,organizationalPerson,inetOrgPerson ***'
try:
  print schema.attribute_types(
    ['person','organizationalPerson','inetOrgPerson']
  )
  print schema.attribute_types(
    ['person','organizationalPerson','inetOrgPerson'],
    attr_type_filter = [
      ('no_user_mod',[0]),
      ('usage',range(2)),
    ]  
  )
except KeyError,e:
  print '***KeyError',str(e)

drink = schema.get_obj(ldap.schema.AttributeType,'favouriteDrink')
if not drink is None:
  print '*** drink ***'
  print 'drink.names',repr(drink.names)
  print 'drink.collective',repr(drink.collective)


schema.ldap_entry()

print str(schema.get_obj(ldap.schema.MatchingRule,'2.5.13.0'))
print str(schema.get_obj(ldap.schema.MatchingRuleUse,'2.5.13.0'))

print str(schema.get_obj(ldap.schema.AttributeType,'name'))
print str(schema.get_inheritedobj(ldap.schema.AttributeType,'cn',['syntax','equality','substr','ordering']))
