"""
ldap.schema.subentry -  subschema subentry handling

See http://www.python-ldap.org/ for details.

\$Id: subentry.py,v 1.25 2010/04/30 08:39:38 stroeder Exp $
"""

import ldap.cidict,ldap.schema

from ldap.schema.models import *

from UserDict import UserDict

SCHEMA_CLASS_MAPPING = ldap.cidict.cidict()
SCHEMA_ATTR_MAPPING = {}

for _name in dir():
  o = eval(_name)
  if hasattr(o,'schema_attribute'):
    SCHEMA_CLASS_MAPPING[o.schema_attribute] = o
    SCHEMA_ATTR_MAPPING[o] = o.schema_attribute

SCHEMA_ATTRS = SCHEMA_CLASS_MAPPING.keys()


class SubSchema:
    
  def __init__(self,sub_schema_sub_entry):
      """
      sub_schema_sub_entry
          Dictionary containing the sub schema sub entry
      """
      # Initialize all dictionaries
      self.name2oid = {}
      self.sed = {}
      for c in SCHEMA_CLASS_MAPPING.values():
        self.name2oid[c] = ldap.cidict.cidict()
        self.sed[c] = {}

      e = ldap.cidict.cidict(sub_schema_sub_entry)

      # Build the schema registry
      for attr_type in SCHEMA_ATTRS:
        if not e.has_key(attr_type) or \
           not e[attr_type]:
          continue
        for attr_value in filter(None,e[attr_type]):
          se_class = SCHEMA_CLASS_MAPPING[attr_type]
          se_instance = se_class(attr_value)
          self.sed[se_class][se_instance.get_id()] = se_instance
          if hasattr(se_instance,'names'):
            for name in se_instance.names:
              self.name2oid[se_class][name] = se_instance.get_id()
      return # subSchema.__init__()

  def ldap_entry(self):
    """
    Returns a dictionary containing the sub schema sub entry
    """
    # Initialize the dictionary with empty lists
    entry = {}
    # Collect the schema elements and store them in
    # entry's attributes
    for se_class in self.sed.keys():
      for se in self.sed[se_class].values():
        se_str = str(se)
        try:
          entry[SCHEMA_ATTR_MAPPING[se_class]].append(se_str)
        except KeyError:
          entry[SCHEMA_ATTR_MAPPING[se_class]] = [ se_str ]
    return entry

  def listall(self,schema_element_class,schema_element_filters=None):
    """
    Returns a list of OIDs of all available schema
    elements of a given schema element class.
    """
    avail_se = self.sed[schema_element_class]
    if schema_element_filters:
      result = []
      for se_key in avail_se.keys():
        se = avail_se[se_key]
        for fk,fv in schema_element_filters:
          try:
            if getattr(se,fk) in fv:
              result.append(se_key)
          except AttributeError:
            pass
    else:
      result = avail_se.keys()
    return result
    

  def tree(self,schema_element_class,schema_element_filters=None):
    """
    Returns a ldap.cidict.cidict dictionary representing the
    tree structure of the schema elements.
    """
    assert schema_element_class in [ObjectClass,AttributeType]
    avail_se = self.listall(schema_element_class,schema_element_filters)
    top_node = '_'
    tree = ldap.cidict.cidict({top_node:[]})
    # 1. Pass: Register all nodes
    for se in avail_se:
      tree[se] = []
    # 2. Pass: Register all sup references
    for se_oid in avail_se:
      se_obj = self.get_obj(schema_element_class,se_oid,None)
      if se_obj.__class__!=schema_element_class:
        # Ignore schema elements not matching schema_element_class.
        # This helps with falsely assigned OIDs.
        continue
      assert se_obj.__class__==schema_element_class, \
        "Schema element referenced by %s must be of class %s but was %s" % (
          se_oid,schema_element_class.__name__,se_obj.__class__
        )
      for s in se_obj.sup or ('_',):
        sup_oid = self.name2oid[schema_element_class].get(s,s)
        try:
          tree[sup_oid].append(se_oid)
        except:
          pass
    return tree


  def getoid(self,se_class,nameoroid):
    """
    Get an OID by name or OID
    """
    se_oid = nameoroid.split(';')[0].strip()
    return self.name2oid[se_class].get(se_oid,se_oid)


  def get_inheritedattr(self,se_class,nameoroid,name):
    """
    Get a possibly inherited attribute specified by name
    of a schema element specified by nameoroid.
    Returns None if class attribute is not set at all.
    
    Raises KeyError if no schema element is found by nameoroid.
    """
    se = self.sed[se_class][self.getoid(se_class,nameoroid)]
    try:
      result = getattr(se,name)
    except AttributeError:
      result = None
    if result is None and se.sup:
      result = self.get_inheritedattr(se_class,se.sup[0],name)
    return result


  def get_obj(self,se_class,nameoroid,default=None):
    """
    Get a schema element by name or OID
    """
    return self.sed[se_class].get(self.getoid(se_class,nameoroid),default)


  def get_inheritedobj(self,se_class,nameoroid,inherited=None):
    """
    Get a schema element by name or OID with all class attributes
    set including inherited class attributes
    """
    import copy
    inherited = inherited or []
    se = copy.copy(self.sed[se_class].get(self.getoid(se_class,nameoroid)))
    if se and hasattr(se,'sup'):
      for class_attr_name in inherited:
        setattr(se,class_attr_name,self.get_inheritedattr(se_class,nameoroid,class_attr_name))
    return se


  def get_syntax(self,nameoroid):
    """
    Get the syntax of an attribute type specified by name or OID
    """
    at_oid = self.getoid(AttributeType,nameoroid)
    try:
      at_obj = self.get_inheritedobj(AttributeType,at_oid)
    except KeyError:
      return None
    else:
      return at_obj.syntax


  def get_structural_oc(self,oc_list):
    """
    Returns OID of structural object class in object_class_list
    if any is present. Returns None else.
    """
    # Get tree of all STRUCTURAL object classes
    oc_tree = self.tree(ObjectClass,[('kind',[0])])
    # Filter all STRUCTURAL object classes
    struct_ocs = {}
    for oc_nameoroid in oc_list:
      oc_se = self.get_obj(ObjectClass,oc_nameoroid,None)
      if oc_se and oc_se.kind==0:
        struct_ocs[oc_se.oid] = None
    result = None
    struct_oc_list = struct_ocs.keys()
    while struct_oc_list:
      oid = struct_oc_list.pop()
      for child_oid in oc_tree[oid]:
        if struct_ocs.has_key(self.getoid(ObjectClass,child_oid)):
          break
      else:
        result = oid
    return result


  def get_applicable_aux_classes(self,nameoroid):
    """
    Return a list of the applicable AUXILIARY object classes
    for a STRUCTURAL object class specified by 'nameoroid'
    if the object class is governed by a DIT content rule.
    If there's no DIT content rule all available AUXILIARY
    object classes are returned.
    """
    content_rule = self.get_obj(DITContentRule,nameoroid)
    if content_rule:
      # Return AUXILIARY object classes from DITContentRule instance
      return content_rule.aux
    else:
      # list all AUXILIARY object classes
      return self.listall(ObjectClass,[('kind',[2])])

  def attribute_types(
    self,object_class_list,attr_type_filter=None,raise_keyerror=1,ignore_dit_content_rule=0
  ):
    """
    Returns a 2-tuple of all must and may attributes including
    all inherited attributes of superior object classes
    by walking up classes along the SUP attribute.

    The attributes are stored in a ldap.cidict.cidict dictionary.

    object_class_list
        list of strings specifying object class names or OIDs
    attr_type_filter
        list of 2-tuples containing lists of class attributes
        which has to be matched
    raise_keyerror
        All KeyError exceptions for non-existent schema elements
	are ignored
    ignore_dit_content_rule
	A DIT content rule governing the structural object class
	is ignored
    """
    AttributeType = ldap.schema.AttributeType
    ObjectClass = ldap.schema.ObjectClass

    # Map object_class_list to object_class_oids (list of OIDs)
    object_class_oids = [
      self.name2oid[ObjectClass].get(o,o)
      for o in object_class_list
    ]
    # Initialize
    oid_cache = {}

    r_must,r_may = ldap.cidict.cidict(),ldap.cidict.cidict()
    if '1.3.6.1.4.1.1466.101.120.111' in object_class_oids:
      # Object class 'extensibleObject' MAY carry every attribute type
      for at_obj in self.sed[AttributeType].values():
        r_may[at_obj.oid] = at_obj

    # Loop over OIDs of all given object classes
    while object_class_oids:
      object_class_oid = object_class_oids.pop(0)
      # Check whether the objectClass with this OID
      # has already been processed
      if oid_cache.has_key(object_class_oid):
        continue
      # Cache this OID as already being processed
      oid_cache[object_class_oid] = None
      try:
        object_class = self.sed[ObjectClass][object_class_oid]
      except KeyError:
        if raise_keyerror:
          raise
        # Ignore this object class
        continue
      assert isinstance(object_class,ObjectClass)
      assert hasattr(object_class,'must'),ValueError(object_class_oid)
      assert hasattr(object_class,'may'),ValueError(object_class_oid)
      for a in object_class.must:
        try:
          at_obj = self.sed[AttributeType][self.name2oid[AttributeType].get(a,a)]
        except KeyError:
          if raise_keyerror:
            raise
          else:
            r_must[a] = None
        else:
          r_must[at_obj.oid] = at_obj
      for a in object_class.may:
        try:
          at_obj = self.sed[AttributeType][self.name2oid[AttributeType].get(a,a)]
        except KeyError:
          if raise_keyerror:
            raise
          else:
            r_may[a] = None
        else:
          r_may[at_obj.oid] = at_obj

      object_class_oids.extend([
        self.name2oid[ObjectClass].get(o,o)
        for o in object_class.sup
      ])

    # Removed all mandantory attribute types from
    # optional attribute type list
    for a in r_may.keys():
      if r_must.has_key(a):
        del r_may[a]

    # Process DIT content rules
    if not ignore_dit_content_rule:
      structural_oc = self.get_structural_oc(object_class_list)
      if structural_oc:
        # Process applicable DIT content rule
        dit_content_rule = self.get_obj(DITContentRule,structural_oc)
        if dit_content_rule:
          for a in dit_content_rule.must:
            try:
              at_obj = self.sed[AttributeType][self.name2oid[AttributeType].get(a,a)]
            except KeyError:
              if raise_keyerror:
                raise
              else:
                r_must[a] = None
            else:
              r_must[at_obj.oid] = at_obj
          for a in dit_content_rule.may:
            try:
              at_obj = self.sed[AttributeType][self.name2oid[AttributeType].get(a,a)]
            except KeyError:
              if raise_keyerror:
                raise
              else:
                r_may[a] = None
            else:
              r_may[at_obj.oid] = at_obj
          for a in dit_content_rule.nots:
            a_oid = self.name2oid[AttributeType].get(a,a)
            if not r_must.has_key(a_oid):
              try:
                at_obj = self.sed[AttributeType][a_oid]
              except KeyError:
                if raise_keyerror:
                  raise
              else:
                try:
                  del r_must[at_obj.oid]
                except KeyError:
                  pass
                try:
                  del r_may[at_obj.oid]
                except KeyError:
                  pass

    # Apply attr_type_filter to results
    if attr_type_filter:
      for l in [r_must,r_may]:
        for a in l.keys():
          for afk,afv in attr_type_filter:
            try:
              schema_attr_type = self.sed[AttributeType][a]
            except KeyError:
              if raise_keyerror:
                raise KeyError,'No attribute type found in sub schema by name %s' % (a)
              # If there's no schema element for this attribute type
              # but still KeyError is to be ignored we filter it away
              del l[a]
              break
            else:
              if not getattr(schema_attr_type,afk) in afv:
                del l[a]
                break

    return r_must,r_may # attribute_types()


def urlfetch(uri,trace_level=0):
  """
  Fetches a parsed schema entry by uri.
  
  If uri is a LDAP URL the LDAP server is queried directly.
  Otherwise uri is assumed to point to a LDIF file which
  is loaded with urllib.
  """
  uri = uri.strip()
  if uri.startswith('ldap:') or uri.startswith('ldaps:') or uri.startswith('ldapi:'):
    import ldapurl
    ldap_url = ldapurl.LDAPUrl(uri)
    l=ldap.initialize(ldap_url.initializeUrl(),trace_level)
    l.protocol_version = ldap.VERSION3
    l.simple_bind_s(ldap_url.who or '', ldap_url.cred or '')
    subschemasubentry_dn = l.search_subschemasubentry_s(ldap_url.dn)
    if subschemasubentry_dn is None:
      subschemasubentry_entry = None
    else:
      if ldap_url.attrs is None:
        schema_attrs = SCHEMA_ATTRS
      else:
        schema_attrs = ldap_url.attrs
      subschemasubentry_entry = l.read_subschemasubentry_s(
        subschemasubentry_dn,attrs=schema_attrs
      )
    l.unbind_s()
    del l
  else:
    import urllib,ldif
    ldif_file = urllib.urlopen(uri)
    ldif_parser = ldif.LDIFRecordList(ldif_file,max_entries=1)
    ldif_parser.parse()
    subschemasubentry_dn,subschemasubentry_entry = ldif_parser.all_records[0]
  if subschemasubentry_dn!=None:
    parsed_sub_schema = ldap.schema.SubSchema(subschemasubentry_entry)
  else:
    parsed_sub_schema = None
  return subschemasubentry_dn, parsed_sub_schema
