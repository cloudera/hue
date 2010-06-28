"""
filterldif - example for implementing a LDIF filter class

Written by Michael Stroeder <michael@stroeder.com>

$Id: $

This example translates the naming context of data read from
input, sanitizes some attributes, maps/removes object classes,
maps/removes attributes., etc. It's far from being complete though.

Python compability note:
Runs on Python 2.0+
"""

##################################################################
# Configuration
##################################################################

import sys

source_namingcontext = 'O=MICHAELS'

target_namingcontext = 'dc=stroeder,dc=de'

infile = sys.stdin

outfile = sys.stdout

infile_charset = 'utf-8'
outfile_charset = 'utf-8'

##################################################################
# Nothing to configure below this line
##################################################################

import re,ldap,ldif

from ldap.cidict import cidict

german_syntax_re = re.compile(r'^0[1-9]+[0-9]+[\s]*/[0-9 -]+$')
german_syntax2_re = re.compile(r'^0[1-9]+[0-9]+[\s]*-[0-9 -]+$')
german_countrycode_re = re.compile(r'^[+]+[\s-]*49[\s-]*\(0\)[\w]+[0-9/-]+$')
us_syntax_re = re.compile(
  r'^([1-9]+|\([1-9]+\))+[\s-]*[0-9]+[\s]*-[\s]*[0-9x -]+$'
)

german_mobile_dict = {
  '0160':'D1','0161':'D1','0170':'D1','0171':'D1','0175':'D1',
  '0162':'D2','0172':'D2','0173':'D2','0174':'D2',
  '0177':'E-Plus','0178':'E-Plus',
  '0176':'E2','0179':'E2',
}

def sanitize_phonenumber(s):
  if not s: return ''
  old = s
  s = s.strip()
  if german_countrycode_re.match(s):
    s = s.replace('(0)','')
  elif us_syntax_re.match(s):
    s = '+1 '+ s
  else:
    if german_syntax_re.match(s):
      sep = '/'
    elif german_syntax2_re.match(s):
      sep = '-'
    else:
      sep = None
    if sep:
      area_code,rest = s.split(sep)
      if german_mobile_dict.has_key(area_code):
        # German mobile are not structured => remove spaces
        rest = rest.replace(' ','').replace('-','')
      s = ' '.join(['+49',area_code.strip()[1:],rest])
  for i,j in [
    (' - ',' '),('-',' '),('++','+'),('(',''),(')',''),('  ',' ')
  ]:
    s = s.replace(i,j)
  s = s.strip()
  return s

def normalize_dn(dn):
  result = ldap.explode_dn(dn)
  return ','.join(result)

def list_dict(l):
  d={}
  for i in l:
    d[i.lower()] = None
  return d

class LDIFFilter(ldif.LDIFCopy):

  def __init__(
    self,
    input_file,
    output_file,
    source_namingcontext,
    target_namingcontext,
    source_charset = 'utf-8',
    target_charset = 'utf-8',
    dn_attr_types=[],
    delete_object_classes=[],
    object_class_map={},
    delete_attr_types=[],
    attr_type_map={}
  ):
    ldif.LDIFCopy.__init__(self,input_file,output_file)
    self.source_charset = source_charset
    self.target_charset = target_charset
    self.source_namingcontext = unicode(
      normalize_dn(source_namingcontext),
      source_charset
    ).lower()
    self.source_namingcontext_len = len(self.source_namingcontext)
    self.target_namingcontext = unicode(
      normalize_dn(target_namingcontext),
      target_charset
    )
    self._dn_attr_types=cidict(list_dict(dn_attr_types))
    self._delete_object_classes=cidict(list_dict(delete_object_classes))
    self._object_class_map = cidict(object_class_map)
    self._delete_attr_types=cidict(list_dict(delete_attr_types))
    self._attr_type_map = cidict(attr_type_map)
    self._phonenumber_syntax=list_dict([
      'telephoneNumber','facsimileTelephoneNumber','fax',
      'homePhone','homeTelephoneNumber','mobile','mobileTelephoneNumber',
      'pager','pagerTelephoneNumber',
    ])

  def _transform_dn(self,dn):
    dn = unicode(normalize_dn(dn),self.source_charset)
    dn_len = len(dn)
    if dn_len<self.source_namingcontext_len:
      return dn.encode(self.target_charset)
    elif dn[-self.source_namingcontext_len:].lower()==self.source_namingcontext:
      dn = dn[:dn_len-self.source_namingcontext_len]+self.target_namingcontext
      return dn.encode(self.target_charset)
    else:
      return dn.encode(self.target_charset)
    
  def handle(self,dn,entry):

    new_entry = cidict(entry)

    objectClass_attrvalue = cidict()
    for oc in new_entry['objectClass']:
      if self._delete_object_classes.has_key(oc.lower()):
        continue
      if self._object_class_map.has_key(oc):
        for oc_new in self._object_class_map[oc]:
          objectClass_attrvalue[oc_new] = None
      else:
        objectClass_attrvalue[oc] = None
    new_entry['objectClass'] = objectClass_attrvalue.keys()

    # Sanitize new_entry's attributes
    for attr_type in new_entry.keys():
      # Attributes to be deleted
      if self._delete_attr_types.has_key(attr_type):
        del new_entry[attr_type]
        continue
      if self._phonenumber_syntax.has_key(attr_type):
        new_entry[attr_type] = map(sanitize_phonenumber,new_entry[attr_type])
      # Transform attributes holding DNs
      if self._dn_attr_types.has_key(attr_type):
        new_entry[attr_type] = map(self._transform_dn,new_entry[attr_type])
      # Transform attribute type names
      if self._attr_type_map.has_key(attr_type):
        mapped_attr_type = self._attr_type_map[attr_type]
        if new_entry.has_key(mapped_attr_type):
          new_entry[mapped_attr_type].extend(new_entry[attr_type])
        else:
          new_entry[mapped_attr_type] = new_entry[attr_type]
        del new_entry[attr_type]

    entry = {}
    entry.update(new_entry)    

    ldif.LDIFCopy.handle(self,self._transform_dn(dn),entry)


##################################################################
# Main
##################################################################

ldif_filter = LDIFFilter(
  infile,
  outfile,
  source_namingcontext,
  target_namingcontext,
  dn_attr_types=[
    'modifiersname','creatorsname','seealso',
    'manager','secretary','documentAuthor',
    'aliasedObjectName','associatedName',
  ],
  delete_object_classes=[
    'restaurant','pkiUser'
  ],
  object_class_map={
    'inetOrgPerson':['inetOrgPerson','globalPerson'],
    'labeledURLObject':['labeledURIObject'],
    'bankArrangement':['germanBankArrangement'],
  },
  delete_attr_types=[
    'destinationIndicator',
    'owner','member',
    'modifiersname','modifytimestamp',
    'creatorsname','createtimestamp','userpassword',
    'shortname'
  ],
  attr_type_map={
    'usersmimecertificate;binary':'userSMIMECertificate',
    'usercertificate;binary':'userCertificate',
    'labeledurl':'labeledURI',
    'bankarrangementinfo':'germanBankAccountInfo',
    'bankaccount':'germanBankAccountNumber',
    'bankcodenumber':'germanBankCode',
    'bankname':'germanBankName',
    'band':'musicalOrchestra',
  },
)

ldif_filter.parse()

