"""
dsml - generate and parse DSMLv1 data
(see http://www.oasis-open.org/committees/dsml/)

See http://www.python-ldap.org/ for details.

$Id: dsml.py,v 1.16 2010/05/07 08:15:47 stroeder Exp $

Python compability note:
Tested with Python 2.0+.
"""

__version__ = '2.3.12'

import string,base64

def list_dict(l):
  """
  return a dictionary with all items of l being the keys of the dictionary
  """
  d = {}
  for i in l:
    d[i]=None
  return d


special_entities = (
  ('&','&amp;'),
  ('<','&lt;'),
  ('"','&quot;'),
  ("'",'&apos;'),
)

def replace_char(s):
  for char,entity in special_entities:
    s = string.replace(s,char,entity)
  return s

class DSMLWriter:

  def __init__(
    self,f,base64_attrs=[],dsml_comment='',indent='    '
  ):
    """
    Parameters:
    f
          File object for output.
    base64_attrs
          Attribute types to be base64-encoded.
    dsml_comment
          Text placed in comment lines behind <dsml:dsml>.
    indent
          String used for indentiation of next nested level.
    """
    self._output_file = f
    self._base64_attrs = list_dict(map(string.lower,base64_attrs))
    self._dsml_comment = dsml_comment
    self._indent = indent

  def _needs_base64_encoding(self,attr_type,attr_value):
    if self._base64_attrs:
      return self._base64_attrs.has_key(string.lower(attr_type))
    else:
      try:
        unicode(attr_value,'utf-8')
      except UnicodeError:
        return 1
      else:
        return 0

  def writeHeader(self):
    """
    Write the header
    """
    self._output_file.write('\n'.join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE root PUBLIC "dsml.dtd" "http://www.dsml.org/1.0/dsml.dtd">',
        '<dsml:dsml xmlns:dsml="http://www.dsml.org/DSML">',
        '%s<dsml:directory-entries>\n' % (self._indent),
      ])
    )
    if self._dsml_comment:
      self._output_file.write('%s<!--\n' % (self._indent))
      self._output_file.write('%s%s\n' % (self._indent,self._dsml_comment))
      self._output_file.write('%s-->\n' % (self._indent))

  def writeFooter(self):
    """
    Write the footer
    """
    self._output_file.write('%s</dsml:directory-entries>\n' % (self._indent))
    self._output_file.write('</dsml:dsml>\n')
    
  def unparse(self,dn,entry):
    return self.writeRecord(dn,entry)

  def writeRecord(self,dn,entry):
    """
    dn
          string-representation of distinguished name
    entry
          dictionary holding the LDAP entry {attr:data}
    """

    # Write line dn: first
    self._output_file.write(
      '%s<dsml:entry dn="%s">\n' % (
        self._indent*2,replace_char(dn)
      )
    )

    objectclasses = entry.get('objectclass',entry.get('objectClass',[]))

    self._output_file.write('%s<dsml:objectclass>\n' % (self._indent*3))
    for oc in objectclasses:
      self._output_file.write('%s<dsml:oc-value>%s</dsml:oc-value>\n' % (self._indent*4,oc))
    self._output_file.write('%s</dsml:objectclass>\n' % (self._indent*3))

    attr_types = entry.keys()[:]
    try:
      attr_types.remove('objectclass')
      attr_types.remove('objectClass')
    except ValueError:
      pass
    attr_types.sort()
    for attr_type in attr_types:
      self._output_file.write('%s<dsml:attr name="%s">\n' % (self._indent*3,attr_type))
      for attr_value_item in entry[attr_type]:
        needs_base64_encoding = self._needs_base64_encoding(
          attr_type,attr_value_item
        )
        if needs_base64_encoding:
          attr_value_item = base64.encodestring(attr_value_item)
        else:
          attr_value_item = replace_char(attr_value_item)
        self._output_file.write('%s<dsml:value%s>\n' % (
            self._indent*4,
            ' encoding="base64"'*needs_base64_encoding
          )
        )
        self._output_file.write('%s%s\n' % (
            self._indent*5,
            attr_value_item
          )
        )
        self._output_file.write('%s</dsml:value>\n' % (
            self._indent*4,
          )
        )
      self._output_file.write('%s</dsml:attr>\n' % (self._indent*3))
    self._output_file.write('%s</dsml:entry>\n' % (self._indent*2))
    return


try:

  import xml.sax,xml.sax.handler

except ImportError:
  pass

else:

  class DSMLv1Handler(xml.sax.handler.ContentHandler):
    """
    Content handler class for DSMLv1
    """

    def __init__(self,parser_instance):
      self._parser_instance = parser_instance
      xml.sax.handler.ContentHandler.__init__(self)

    def startDocument(self):
      pass

    def endDocument(self):
      pass

    def startElement(self,raw_name,attrs):
      assert raw_name.startswith(''),'Illegal name'
      name = raw_name[5:]
      if name=='dsml':
        pass
      elif name=='directory-entries':
        self._parsing_entries = 1
      elif name=='entry':
        self._dn = attrs['dn']
        self._entry = {}
      elif name=='attr':
        self._attr_type = attrs['name'].encode('utf-8')
        self._attr_values = []
      elif name=='value':
        self._attr_value = ''
        self._base64_encoding = attrs.get('encoding','').lower()=='base64'
      # Handle object class tags
      elif name=='objectclass':
        self._object_classes = []
      elif name=='oc-value':
        self._oc_value = ''
      # Unhandled tags
      else:
        raise ValueError,'Unknown tag %s' % (raw_name)

    def endElement(self,raw_name):
      assert raw_name.startswith('dsml:'),'Illegal name'
      name = raw_name[5:]
      if name=='dsml':
        pass
      elif name=='directory-entries':
        self._parsing_entries = 0
      elif name=='entry':
        self._parser_instance.handle(self._dn,self._entry)
        del self._dn
        del self._entry
      elif name=='attr':
        self._entry[self._attr_type] = self._attr_values
        del self._attr_type
        del self._attr_values
      elif name=='value':
        if self._base64_encoding:
          attr_value = base64.decodestring(self._attr_value.strip())
        else:
          attr_value = self._attr_value.strip().encode('utf-8')
        self._attr_values.append(attr_value)
        del attr_value
        del self._attr_value
        del self._base64_encoding
      # Handle object class tags
      elif name=='objectclass':
        self._entry['objectClass'] = self._object_classes
        del self._object_classes
      elif name=='oc-value':
        self._object_classes.append(self._oc_value.strip().encode('utf-8'))
        del self._oc_value
      # Unhandled tags
      else:
        raise ValueError,'Unknown tag %s' % (raw_name)

    def characters(self,ch):
      if self.__dict__.has_key('_oc_value'):
        self._oc_value = self._oc_value + ch
      elif self.__dict__.has_key('_attr_value'):
        self._attr_value = self._attr_value + ch
      else:
        pass


  class DSMLParser:
    """
    Base class for a DSMLv1 parser. Applications should sub-class this
    class and override method handle() to implement something meaningful.

    Public class attributes:
    records_read
          Counter for records processed so far
    """

    def __init__(
      self,
      input_file,
      ContentHandlerClass,
      ignored_attr_types=None,
      max_entries=0,
    ):
      """
      Parameters:
      input_file
          File-object to read the DSMLv1 input from
      ignored_attr_types
          Attributes with these attribute type names will be ignored.
      max_entries
          If non-zero specifies the maximum number of entries to be
          read from f.
      line_sep
          String used as line separator
      """
      self._input_file = input_file
      self._max_entries = max_entries
      self._ignored_attr_types = list_dict(map(string.lower,(ignored_attr_types or [])))
      self._current_record = None,None
      self.records_read = 0
      self._parser = xml.sax.make_parser()
      self._parser.setFeature(xml.sax.handler.feature_namespaces,0)
      content_handler = ContentHandlerClass(self)
      self._parser.setContentHandler(content_handler)

    def handle(self,*args,**kwargs):
      """
      Process a single content DSMLv1 record. This method should be
      implemented by applications using DSMLParser.
      """
      import pprint
      pprint.pprint(args)
      pprint.pprint(kwargs)

    def parse(self):
      """
      Continously read and parse DSML records
      """
      self._parser.parse(self._input_file)

