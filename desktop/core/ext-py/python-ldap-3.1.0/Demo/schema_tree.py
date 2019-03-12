"""
Outputs the object class tree read from LDAPv3 schema
of a given server

Usage: schema_oc_tree.py [--html] [LDAP URL]
"""
from __future__ import print_function

import sys,getopt,ldap,ldap.schema


ldap.trace_level = 1

def PrintSchemaTree(schema,se_class,se_tree,se_oid,level):
  """ASCII text output for console"""
  se_obj = schema.get_obj(se_class,se_oid)
  if se_obj!=None:
    print('|    '*(level-1)+'+---'*(level>0), \)
          ', '.join(se_obj.names), \
          '(%s)' % se_obj.oid
  for sub_se_oid in se_tree[se_oid]:
    print('|    '*(level+1))
    PrintSchemaTree(schema,se_class,se_tree,sub_se_oid,level+1)


def HTMLSchemaTree(schema,se_class,se_tree,se_oid,level):
  """HTML output for browser"""
  se_obj = schema.get_obj(se_class,se_oid)
  if se_obj!=None:
    print("""
    <dt><strong>%s (%s)</strong></dt>
    <dd>
      %s
    """ % (', '.join(se_obj.names),se_obj.oid,se_obj.desc))
  if se_tree[se_oid]:
    print('<dl>')
    for sub_se_oid in se_tree[se_oid]:
      HTMLSchemaTree(schema,se_class,se_tree,sub_se_oid,level+1)
    print('</dl>')
  print('</dd>')


ldap.set_option(ldap.OPT_DEBUG_LEVEL,0)

ldap._trace_level = 0

subschemasubentry_dn,schema = ldap.schema.urlfetch(sys.argv[-1],ldap.trace_level)

if subschemasubentry_dn is None:
  print('No sub schema sub entry found!')
  sys.exit(1)

try:
  options,args=getopt.getopt(sys.argv[1:],'',['html'])
except getopt.error:
  print('Error: %s\nUsage: schema_oc_tree.py [--html] [LDAP URL]')

html_output = options and options[0][0]=='--html'

oc_tree = schema.tree(ldap.schema.ObjectClass)
at_tree = schema.tree(ldap.schema.AttributeType)

#for k,v in oc_tree.items():
#  print(k,'->',v)
#for k,v in at_tree.items():
#  print(k,'->',v)

if html_output:

  print("""<html>
<head>
  <title>Object class tree</title>
</head>
<body bgcolor="#ffffff">
<h1>Object class tree</h1>
<dl>
""")
  HTMLSchemaTree(schema,ldap.schema.ObjectClass,oc_tree,'2.5.6.0',0)
  print("""</dl>
<h1>Attribute type tree</h1>
<dl>
""")
  for a in schema.listall(ldap.schema.AttributeType):
    if at_tree[a]:
      HTMLSchemaTree(schema,ldap.schema.AttributeType,at_tree,a,0)
      print

  print("""</dl>
</body>
</html>
""")

else:

  print('*** Object class tree ***\n')
  print
  PrintSchemaTree(schema,ldap.schema.ObjectClass,oc_tree,'2.5.6.0',0)

  print('\n*** Attribute types tree ***\n')
  PrintSchemaTree(schema,ldap.schema.AttributeType,at_tree,'_',0)
