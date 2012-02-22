import ldap,ldap.async

class DeleteLeafs(ldap.async.AsyncSearchHandler):
  """
  Class for deleting entries which are results of a search.
  
  DNs of Non-leaf entries are collected in DeleteLeafs.nonLeafEntries.
  """
  _entryResultTypes = ldap.async._entryResultTypes

  def __init__(self,l):
    ldap.async.AsyncSearchHandler.__init__(self,l)
    self.nonLeafEntries = []
    self.deletedEntries = 0

  def startSearch(self,searchRoot,searchScope):
    if not searchScope in [ldap.SCOPE_ONELEVEL,ldap.SCOPE_SUBTREE]:
      raise ValueError, "Parameter searchScope must be either ldap.SCOPE_ONELEVEL or ldap.SCOPE_SUBTREE."
    self.nonLeafEntries = []
    self.deletedEntries = 0
    ldap.async.AsyncSearchHandler.startSearch(
      self,
      searchRoot,
      searchScope,
      filterStr='(objectClass=*)',
      attrList=['hasSubordinates','numSubordinates'],
      attrsOnly=0,
    )

  def _processSingleResult(self,resultType,resultItem):
    if self._entryResultTypes.has_key(resultType):
      # Don't process search references
      dn,entry = resultItem
      hasSubordinates = entry.get(
        'hasSubordinates',
        entry.get('hassubordinates',['FALSE']
        )
      )[0]
      numSubordinates = entry.get(
        'numSubordinates',
        entry.get('numsubordinates',['0'])
      )[0]
      if hasSubordinates=='TRUE' or int(numSubordinates):
        self.nonLeafEntries.append(dn)
      else:
        try:
          self._l.delete_s(dn)
        except ldap.NOT_ALLOWED_ON_NONLEAF,e:
          self.nonLeafEntries.append(dn)
        else:
          self.deletedEntries = self.deletedEntries+1


def DelTree(l,dn,scope=ldap.SCOPE_ONELEVEL):
  """
  Recursively delete entries below or including entry with name dn.
  """
  leafs_deleter = DeleteLeafs(l)
  leafs_deleter.startSearch(dn,scope)
  leafs_deleter.processResults()
  deleted_entries = leafs_deleter.deletedEntries
  non_leaf_entries = leafs_deleter.nonLeafEntries[:]
  while non_leaf_entries:
    dn = non_leaf_entries.pop()
    print deleted_entries,len(non_leaf_entries),dn
    leafs_deleter.startSearch(dn,ldap.SCOPE_SUBTREE)
    leafs_deleter.processResults()
    deleted_entries = deleted_entries+leafs_deleter.deletedEntries
    non_leaf_entries.extend(leafs_deleter.nonLeafEntries)
  return # DelTree()


# Create LDAPObject instance
l = ldap.initialize('ldap://localhost:1390')

# Try a bind to provoke failure if protocol version is not supported
l.simple_bind_s('cn=Directory Manager,dc=IMC,dc=org','controller')

# Delete all entries *below* the entry dc=Delete,dc=IMC,dc=org
DelTree(l,'dc=Delete,dc=IMC,dc=org',ldap.SCOPE_ONELEVEL)
