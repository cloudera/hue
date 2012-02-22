"""
ldif - generate and parse LDIF data (see RFC 2849)

See http://www.python-ldap.org/ for details.

$Id: ldif.py,v 1.56 2010/07/19 08:23:22 stroeder Exp $

Python compability note:
Tested with Python 2.0+, but should work with Python 1.5.2+.
"""

__version__ = '2.3.12'

__all__ = [
  # constants
  'ldif_pattern',
  # functions
  'AttrTypeandValueLDIF','CreateLDIF','ParseLDIF',
  # classes
  'LDIFWriter',
  'LDIFParser',
  'LDIFRecordList',
  'LDIFCopy',
]

import urlparse,urllib,base64,re,types

try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO

attrtype_pattern = r'[\w;.-]+(;[\w_-]+)*'
attrvalue_pattern = r'(([^,]|\\,)+|".*?")'
attrtypeandvalue_pattern = attrtype_pattern + r'[ ]*=[ ]*' + attrvalue_pattern
rdn_pattern   = attrtypeandvalue_pattern + r'([ ]*\+[ ]*' + attrtypeandvalue_pattern + r')*[ ]*'
dn_pattern   = rdn_pattern + r'([ ]*,[ ]*' + rdn_pattern + r')*[ ]*'
dn_regex   = re.compile('^%s$' % dn_pattern)

ldif_pattern = '^((dn(:|::) %(dn_pattern)s)|(%(attrtype_pattern)s(:|::) .*)$)+' % vars()

MOD_OP_INTEGER = {
  'add':0,'delete':1,'replace':2
}

MOD_OP_STR = {
  0:'add',1:'delete',2:'replace'
}

CHANGE_TYPES = ['add','delete','modify','modrdn']
valid_changetype_dict = {}
for c in CHANGE_TYPES:
  valid_changetype_dict[c]=None


def is_dn(s):
  """
  returns 1 if s is a LDAP DN
  """
  if s=='':
    return 1
  rm = dn_regex.match(s)
  return rm!=None and rm.group(0)==s


SAFE_STRING_PATTERN = '(^(\000|\n|\r| |:|<)|[\000\n\r\200-\377]+|[ ]+$)'
safe_string_re = re.compile(SAFE_STRING_PATTERN)

def list_dict(l):
  """
  return a dictionary with all items of l being the keys of the dictionary
  """
  return dict([(i,None) for i in l])


class LDIFWriter:
  """
  Write LDIF entry or change records to file object
  Copy LDIF input to a file output object containing all data retrieved
  via URLs
  """

  def __init__(self,output_file,base64_attrs=None,cols=76,line_sep='\n'):
    """
    output_file
        file object for output
    base64_attrs
        list of attribute types to be base64-encoded in any case
    cols
        Specifies how many columns a line may have before it's
        folded into many lines.
    line_sep
        String used as line separator
    """
    self._output_file = output_file
    self._base64_attrs = list_dict([a.lower() for a in (base64_attrs or [])])
    self._cols = cols
    self._line_sep = line_sep
    self.records_written = 0

  def _unfoldLDIFLine(self,line):
    """
    Write string line as one or more folded lines
    """
    # Check maximum line length
    line_len = len(line)
    if line_len<=self._cols:
      self._output_file.write(line)
      self._output_file.write(self._line_sep)
    else:
      # Fold line
      pos = self._cols
      self._output_file.write(line[0:min(line_len,self._cols)])
      self._output_file.write(self._line_sep)
      while pos<line_len:
        self._output_file.write(' ')
        self._output_file.write(line[pos:min(line_len,pos+self._cols-1)])
        self._output_file.write(self._line_sep)
        pos = pos+self._cols-1
    return # _unfoldLDIFLine()

  def _needs_base64_encoding(self,attr_type,attr_value):
    """
    returns 1 if attr_value has to be base-64 encoded because
    of special chars or because attr_type is in self._base64_attrs
    """
    return self._base64_attrs.has_key(attr_type.lower()) or \
           not safe_string_re.search(attr_value) is None

  def _unparseAttrTypeandValue(self,attr_type,attr_value):
    """
    Write a single attribute type/value pair

    attr_type
          attribute type
    attr_value
          attribute value
    """
    if self._needs_base64_encoding(attr_type,attr_value):
      # Encode with base64
      self._unfoldLDIFLine(':: '.join([attr_type,base64.encodestring(attr_value).replace('\n','')]))
    else:
      self._unfoldLDIFLine(': '.join([attr_type,attr_value]))
    return # _unparseAttrTypeandValue()

  def _unparseEntryRecord(self,entry):
    """
    entry
        dictionary holding an entry
    """
    attr_types = entry.keys()[:]
    attr_types.sort()
    for attr_type in attr_types:
      for attr_value in entry[attr_type]:
        self._unparseAttrTypeandValue(attr_type,attr_value)

  def _unparseChangeRecord(self,modlist):
    """
    modlist
        list of additions (2-tuple) or modifications (3-tuple)
    """
    mod_len = len(modlist[0])
    if mod_len==2:
      changetype = 'add'
    elif mod_len==3:
      changetype = 'modify'
    else:
      raise ValueError,"modlist item of wrong length"
    self._unparseAttrTypeandValue('changetype',changetype)
    for mod in modlist:
      if mod_len==2:
        mod_type,mod_vals = mod
      elif mod_len==3:
        mod_op,mod_type,mod_vals = mod
        self._unparseAttrTypeandValue(MOD_OP_STR[mod_op],mod_type)
      else:
        raise ValueError,"Subsequent modlist item of wrong length"
      if mod_vals:
        for mod_val in mod_vals:
          self._unparseAttrTypeandValue(mod_type,mod_val)
      if mod_len==3:
        self._output_file.write('-'+self._line_sep)

  def unparse(self,dn,record):
    """
    dn
          string-representation of distinguished name
    record
          Either a dictionary holding the LDAP entry {attrtype:record}
          or a list with a modify list like for LDAPObject.modify().
    """
    if not record:
      # Simply ignore empty records
      return
    # Start with line containing the distinguished name
    self._unparseAttrTypeandValue('dn',dn)
    # Dispatch to record type specific writers
    if isinstance(record,types.DictType):
      self._unparseEntryRecord(record)
    elif isinstance(record,types.ListType):
      self._unparseChangeRecord(record)
    else:
      raise ValueError, "Argument record must be dictionary or list"
    # Write empty line separating the records
    self._output_file.write(self._line_sep)
    # Count records written
    self.records_written = self.records_written+1
    return # unparse()


def CreateLDIF(dn,record,base64_attrs=None,cols=76):
  """
  Create LDIF single formatted record including trailing empty line.
  This is a compability function. Use is deprecated!

  dn
        string-representation of distinguished name
  record
        Either a dictionary holding the LDAP entry {attrtype:record}
        or a list with a modify list like for LDAPObject.modify().
  base64_attrs
        list of attribute types to be base64-encoded in any case
  cols
        Specifies how many columns a line may have before it's
        folded into many lines.
  """
  f = StringIO()
  ldif_writer = LDIFWriter(f,base64_attrs,cols,'\n')
  ldif_writer.unparse(dn,record)
  s = f.getvalue()
  f.close()
  return s


class LDIFParser:
  """
  Base class for a LDIF parser. Applications should sub-class this
  class and override method handle() to implement something meaningful.

  Public class attributes:
  records_read
        Counter for records processed so far
  """

  def _stripLineSep(self,s):
    """
    Strip trailing line separators from s, but no other whitespaces
    """
    if s[-2:]=='\r\n':
      return s[:-2]
    elif s[-1:]=='\n':
      return s[:-1]
    else:
      return s

  def __init__(
    self,
    input_file,
    ignored_attr_types=None,
    max_entries=0,
    process_url_schemes=None,
    line_sep='\n'
  ):
    """
    Parameters:
    input_file
        File-object to read the LDIF input from
    ignored_attr_types
        Attributes with these attribute type names will be ignored.
    max_entries
        If non-zero specifies the maximum number of entries to be
        read from f.
    process_url_schemes
        List containing strings with URLs schemes to process with urllib.
        An empty list turns off all URL processing and the attribute
        is ignored completely.
    line_sep
        String used as line separator
    """
    self._input_file = input_file
    self._max_entries = max_entries
    self._process_url_schemes = list_dict([s.lower() for s in (process_url_schemes or [])])
    self._ignored_attr_types = list_dict([a.lower() for a in (ignored_attr_types or [])])
    self._line_sep = line_sep
    self.records_read = 0

  def handle(self,dn,entry):
    """
    Process a single content LDIF record. This method should be
    implemented by applications using LDIFParser.
    """

  def _unfoldLDIFLine(self):
    """
    Unfold several folded lines with trailing space into one line
    """
    unfolded_lines = [ self._stripLineSep(self._line) ]
    self._line = self._input_file.readline()
    while self._line and self._line[0]==' ':
      unfolded_lines.append(self._stripLineSep(self._line[1:]))
      self._line = self._input_file.readline()
    return ''.join(unfolded_lines)

  def _parseAttrTypeandValue(self):
    """
    Parse a single attribute type and value pair from one or
    more lines of LDIF data
    """
    # Reading new attribute line
    unfolded_line = self._unfoldLDIFLine()
    # Ignore comments which can also be folded
    while unfolded_line and unfolded_line[0]=='#':
      unfolded_line = self._unfoldLDIFLine()
    if not unfolded_line or unfolded_line=='\n' or unfolded_line=='\r\n':
      return None,None
    try:
      colon_pos = unfolded_line.index(':')
    except ValueError:
      # Treat malformed lines without colon as non-existent
      return None,None
    attr_type = unfolded_line[0:colon_pos]
    # if needed attribute value is BASE64 decoded
    value_spec = unfolded_line[colon_pos:colon_pos+2]
    if value_spec=='::':
      # attribute value needs base64-decoding
      attr_value = base64.decodestring(unfolded_line[colon_pos+2:])
    elif value_spec==':<':
      # fetch attribute value from URL
      url = unfolded_line[colon_pos+2:].strip()
      attr_value = None
      if self._process_url_schemes:
        u = urlparse.urlparse(url)
        if self._process_url_schemes.has_key(u[0]):
          attr_value = urllib.urlopen(url).read()
    elif value_spec==':\r\n' or value_spec=='\n':
      attr_value = ''
    else:
      attr_value = unfolded_line[colon_pos+2:].lstrip()
    return attr_type,attr_value

  def parse(self):
    """
    Continously read and parse LDIF records
    """
    self._line = self._input_file.readline()

    while self._line and \
          (not self._max_entries or self.records_read<self._max_entries):

      # Reset record
      version = None; dn = None; changetype = None; modop = None; entry = {}

      attr_type,attr_value = self._parseAttrTypeandValue()

      while attr_type!=None and attr_value!=None:
        if attr_type=='dn':
          # attr type and value pair was DN of LDIF record
          if dn!=None:
            raise ValueError, 'Two lines starting with dn: in one record.'
          if not is_dn(attr_value):
            raise ValueError, 'No valid string-representation of distinguished name %s.' % (repr(attr_value))
          dn = attr_value
        elif attr_type=='version' and dn is None:
          version = 1
        elif attr_type=='changetype':
          # attr type and value pair was DN of LDIF record
          if dn is None:
            raise ValueError, 'Read changetype: before getting valid dn: line.'
          if changetype!=None:
            raise ValueError, 'Two lines starting with changetype: in one record.'
          if not valid_changetype_dict.has_key(attr_value):
            raise ValueError, 'changetype value %s is invalid.' % (repr(attr_value))
          changetype = attr_value
        elif attr_value!=None and \
             not self._ignored_attr_types.has_key(attr_type.lower()):
          # Add the attribute to the entry if not ignored attribute
          if entry.has_key(attr_type):
            entry[attr_type].append(attr_value)
          else:
            entry[attr_type]=[attr_value]

        # Read the next line within an entry
        attr_type,attr_value = self._parseAttrTypeandValue()

      if entry:
        # append entry to result list
        self.handle(dn,entry)
        self.records_read = self.records_read+1

    return # parse()


class LDIFRecordList(LDIFParser):
  """
  Collect all records of LDIF input into a single list.
  of 2-tuples (dn,entry). It can be a memory hog!
  """

  def __init__(
    self,
    input_file,
    ignored_attr_types=None,max_entries=0,process_url_schemes=None
  ):
    """
    See LDIFParser.__init__()

    Additional Parameters:
    all_records
        List instance for storing parsed records
    """
    LDIFParser.__init__(self,input_file,ignored_attr_types,max_entries,process_url_schemes)
    self.all_records = []

  def handle(self,dn,entry):
    """
    Append single record to dictionary of all records.
    """
    self.all_records.append((dn,entry))


class LDIFCopy(LDIFParser):
  """
  Copy LDIF input to LDIF output containing all data retrieved
  via URLs
  """

  def __init__(
    self,
    input_file,output_file,
    ignored_attr_types=None,max_entries=0,process_url_schemes=None,
    base64_attrs=None,cols=76,line_sep='\n'
  ):
    """
    See LDIFParser.__init__() and LDIFWriter.__init__()
    """
    LDIFParser.__init__(self,input_file,ignored_attr_types,max_entries,process_url_schemes)
    self._output_ldif = LDIFWriter(output_file,base64_attrs,cols,line_sep)

  def handle(self,dn,entry):
    """
    Write single LDIF record to output file.
    """
    self._output_ldif.unparse(dn,entry)


def ParseLDIF(f,ignore_attrs=None,maxentries=0):
  """
  Parse LDIF records read from file.
  This is a compability function. Use is deprecated!
  """
  ldif_parser = LDIFRecordList(
    f,ignored_attr_types=ignore_attrs,max_entries=maxentries,process_url_schemes=0
  )
  ldif_parser.parse()
  return ldif_parser.all_records
