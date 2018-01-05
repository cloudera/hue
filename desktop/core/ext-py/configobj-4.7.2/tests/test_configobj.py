# configobj_test.py
# doctests for ConfigObj
# A config file reader/writer that supports nested sections in config files.
# Copyright (C) 2005-2010 Michael Foord, Nicola Larosa
# E-mail: fuzzyman AT voidspace DOT org DOT uk
#         nico AT tekNico DOT net

# ConfigObj 4
# http://www.voidspace.org.uk/python/configobj.html

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
# For information about bugfixes, updates and support, please join the
# ConfigObj mailing list:
# http://lists.sourceforge.net/lists/listinfo/configobj-develop
# Comments, suggestions and bug reports welcome.


from __future__ import generators
from StringIO import StringIO

import os
import sys
INTP_VER = sys.version_info[:2]
if INTP_VER < (2, 2):
    raise RuntimeError("Python v.2.2 or later needed")

try:
    from codecs import BOM_UTF8
except ImportError:
    # Python 2.2 does not have this
    # UTF-8
    BOM_UTF8 = '\xef\xbb\xbf'

from configobj import *
from validate import Validator, VdtValueTooSmallError


"""
    >>> z = ConfigObj()
    >>> z['a'] = 'a'
    >>> z['sect'] = {
    ...    'subsect': {
    ...         'a': 'fish',
    ...         'b': 'wobble',
    ...     },
    ...     'member': 'value',
    ... }
    >>> x = ConfigObj(z.write())
    >>> z == x
    1
"""


def _error_test():
    """
    Testing the error classes.
    
    >>> raise ConfigObjError
    Traceback (most recent call last):
    ConfigObjError

    >>> raise NestingError
    Traceback (most recent call last):
    NestingError
    
    >>> raise ParseError
    Traceback (most recent call last):
    ParseError
    
    >>> raise DuplicateError
    Traceback (most recent call last):
    DuplicateError
    
    >>> raise ConfigspecError
    Traceback (most recent call last):
    ConfigspecError
    
    >>> raise InterpolationLoopError('yoda')
    Traceback (most recent call last):
    InterpolationLoopError: interpolation loop detected in value "yoda".
    
    >>> raise RepeatSectionError
    Traceback (most recent call last):
    RepeatSectionError
    
    >>> raise MissingInterpolationOption('yoda')
    Traceback (most recent call last):
    MissingInterpolationOption: missing option "yoda" in interpolation.
    
    
    >>> raise ReloadError()
    Traceback (most recent call last):
    ReloadError: reload failed, filename is not set.
    >>> try:
    ...     raise ReloadError()
    ... except IOError:
    ...     pass
    ... else:
    ...     raise Exception('We should catch a ReloadError as an IOError')
    >>>
    
    """


def _section_test():
    """
    Tests from Section methods.
    
    >>> n = a.dict()
    >>> n == a
    1
    >>> n is a
    0
        
    >>> a = '''[section1]
    ...     option1 = True
    ...     [[subsection]]
    ...     more_options = False
    ...     # end of file'''.splitlines()
    >>> b = '''# File is user.ini
    ...     [section1]
    ...     option1 = False
    ...     # end of file'''.splitlines()
    >>> c1 = ConfigObj(b)
    >>> c2 = ConfigObj(a)
    >>> c2.merge(c1)
    >>> c2
    ConfigObj({'section1': {'option1': 'False', 'subsection': {'more_options': 'False'}}})
    
    >>> config = '''[XXXXsection]
    ... XXXXkey = XXXXvalue'''.splitlines()
    >>> cfg = ConfigObj(config)
    >>> cfg
    ConfigObj({'XXXXsection': {'XXXXkey': 'XXXXvalue'}})
    >>> def transform(section, key):
    ...     val = section[key]
    ...     newkey = key.replace('XXXX', 'CLIENT1')
    ...     section.rename(key, newkey)
    ...     if isinstance(val, (tuple, list, dict)):
    ...         pass
    ...     else:
    ...         val = val.replace('XXXX', 'CLIENT1')
    ...         section[newkey] = val
    >>> cfg.walk(transform, call_on_sections=True)
    {'CLIENT1section': {'CLIENT1key': None}}
    >>> cfg
    ConfigObj({'CLIENT1section': {'CLIENT1key': 'CLIENT1value'}})
    """


def _test_reset():
    """
    >>> something = object()
    >>> c = ConfigObj()
    >>> c['something'] = something
    >>> c['section'] = {'something': something}
    >>> c.filename = 'fish'
    >>> c.raise_errors = something
    >>> c.list_values = something
    >>> c.create_empty = something
    >>> c.file_error = something
    >>> c.stringify = something
    >>> c.indent_type = something
    >>> c.encoding = something
    >>> c.default_encoding = something
    >>> c.BOM = something
    >>> c.newlines = something
    >>> c.write_empty_values = something
    >>> c.unrepr = something
    >>> c.initial_comment = something
    >>> c.final_comment = something
    >>> c.configspec = something
    >>> c.inline_comments = something
    >>> c.comments = something
    >>> c.defaults = something
    >>> c.default_values = something
    >>> c.reset()
    >>> 
    >>> c.filename
    >>> c.raise_errors
    False
    >>> c.list_values
    True
    >>> c.create_empty
    False
    >>> c.file_error
    False
    >>> c.interpolation
    True
    >>> c.configspec
    >>> c.stringify
    True
    >>> c.indent_type
    >>> c.encoding
    >>> c.default_encoding
    >>> c.unrepr
    False
    >>> c.write_empty_values
    False
    >>> c.inline_comments
    {}
    >>> c.comments
    {}
    >>> c.defaults
    []
    >>> c.default_values
    {}
    >>> c == ConfigObj()
    True
    >>> c
    ConfigObj({})
    """


def _test_reload():
    """
    >>> c = ConfigObj(StringIO())
    >>> c.reload()
    Traceback (most recent call last):
    ReloadError: reload failed, filename is not set.
    >>> c = ConfigObj()
    >>> c.reload()
    Traceback (most recent call last):
    ReloadError: reload failed, filename is not set.
    >>> c = ConfigObj([])
    >>> c.reload()
    Traceback (most recent call last):
    ReloadError: reload failed, filename is not set.
    
    We need to use a real file as reload is only for files loaded from
    the filesystem.
    >>> h = open('temp', 'w')
    >>> h.write('''
    ...     test1=40
    ...     test2=hello
    ...     test3=3
    ...     test4=5.0
    ...     [section]
    ...         test1=40
    ...         test2=hello
    ...         test3=3
    ...         test4=5.0
    ...         [[sub section]]
    ...             test1=40
    ...             test2=hello
    ...             test3=3
    ...             test4=5.0
    ...     [section2]
    ...         test1=40
    ...         test2=hello
    ...         test3=3
    ...         test4=5.0
    ... ''')
    >>> h.close()
    >>> configspec = '''
    ...     test1= integer(30,50)
    ...     test2= string
    ...     test3=integer
    ...     test4=float(4.5)
    ...     [section]
    ...         test1=integer(30,50)
    ...         test2=string
    ...         test3=integer
    ...         test4=float(4.5)
    ...         [[sub section]]
    ...             test1=integer(30,50)
    ...             test2=string
    ...             test3=integer
    ...             test4=float(4.5)
    ...     [section2]
    ...         test1=integer(30,50)
    ...         test2=string
    ...         test3=integer
    ...         test4=float(4.5)
    ...     '''.split('\\n')
    >>> c = ConfigObj('temp', configspec=configspec)
    >>> c.configspec['test1'] = 'integer(50,60)'
    >>> backup = ConfigObj('temp')
    >>> del c['section']
    >>> del c['test1']
    >>> c['extra'] = '3'
    >>> c['section2']['extra'] = '3'
    >>> c.reload()
    >>> c == backup
    True
    >>> c.validate(Validator())
    True
    >>> os.remove('temp')
    """


def _doctest():
    """
    Dummy function to hold some of the doctests.
    
    >>> a.depth
    0
    >>> a == {
    ...     'key2': 'val',
    ...     'key1': 'val',
    ...     'lev1c': {
    ...         'lev2c': {
    ...             'lev3c': {
    ...                 'key1': 'val',
    ...             },
    ...         },
    ...     },
    ...     'lev1b': {
    ...         'key2': 'val',
    ...         'key1': 'val',
    ...         'lev2ba': {
    ...             'key1': 'val',
    ...         },
    ...         'lev2bb': {
    ...             'key1': 'val',
    ...         },
    ...     },
    ...     'lev1a': {
    ...         'key2': 'val',
    ...         'key1': 'val',
    ...     },
    ... }
    1
    >>> b.depth
    0
    >>> b == {
    ...     'key3': 'val3',
    ...     'key2': 'val2',
    ...     'key1': 'val1',
    ...     'section 1': {
    ...         'keys11': 'val1',
    ...         'keys13': 'val3',
    ...         'keys12': 'val2',
    ...     },
    ...     'section 2': {
    ...         'section 2 sub 1': {
    ...             'fish': '3',
    ...     },
    ...     'keys21': 'val1',
    ...     'keys22': 'val2',
    ...     'keys23': 'val3',
    ...     },
    ... }
    1
    >>> t = '''
    ... 'a' = b # !"$%^&*(),::;'@~#= 33
    ... "b" = b #= 6, 33
    ... ''' .split('\\n')
    >>> t2 = ConfigObj(t)
    >>> assert t2 == {'a': 'b', 'b': 'b'}
    >>> t2.inline_comments['b'] = ''
    >>> del t2['a']
    >>> assert t2.write() == ['','b = b', '']
    
    # Test ``list_values=False`` stuff
    >>> c = '''
    ...     key1 = no quotes
    ...     key2 = 'single quotes'
    ...     key3 = "double quotes"
    ...     key4 = "list", 'with', several, "quotes"
    ...     '''
    >>> cfg = ConfigObj(c.splitlines(), list_values=False)
    >>> cfg == {'key1': 'no quotes', 'key2': "'single quotes'", 
    ... 'key3': '"double quotes"', 
    ... 'key4': '"list", \\'with\\', several, "quotes"'
    ... }
    1
    >>> cfg = ConfigObj(list_values=False)
    >>> cfg['key1'] = 'Multiline\\nValue'
    >>> cfg['key2'] = '''"Value" with 'quotes' !'''
    >>> cfg.write()
    ["key1 = '''Multiline\\nValue'''", 'key2 = "Value" with \\'quotes\\' !']
    >>> cfg.list_values = True
    >>> cfg.write() == ["key1 = '''Multiline\\nValue'''",
    ... 'key2 = \\'\\'\\'"Value" with \\'quotes\\' !\\'\\'\\'']
    1
    
    Test flatten_errors:
    
    >>> config = '''
    ...     test1=40
    ...     test2=hello
    ...     test3=3
    ...     test4=5.0
    ...     [section]
    ...         test1=40
    ...         test2=hello
    ...         test3=3
    ...         test4=5.0
    ...         [[sub section]]
    ...             test1=40
    ...             test2=hello
    ...             test3=3
    ...             test4=5.0
    ... '''.split('\\n')
    >>> configspec = '''
    ...     test1= integer(30,50)
    ...     test2= string
    ...     test3=integer
    ...     test4=float(6.0)
    ...     [section]
    ...         test1=integer(30,50)
    ...         test2=string
    ...         test3=integer
    ...         test4=float(6.0)
    ...         [[sub section]]
    ...             test1=integer(30,50)
    ...             test2=string
    ...             test3=integer
    ...             test4=float(6.0)
    ...     '''.split('\\n')
    >>> val = Validator()
    >>> c1 = ConfigObj(config, configspec=configspec)
    >>> res = c1.validate(val)
    >>> flatten_errors(c1, res) == [([], 'test4', False), (['section', 
    ...     'sub section'], 'test4', False), (['section'], 'test4', False)]
    True
    >>> res = c1.validate(val, preserve_errors=True)
    >>> check = flatten_errors(c1, res)
    >>> check[0][:2]
    ([], 'test4')
    >>> check[1][:2]
    (['section', 'sub section'], 'test4')
    >>> check[2][:2]
    (['section'], 'test4')
    >>> for entry in check:
    ...     isinstance(entry[2], VdtValueTooSmallError)
    ...     print str(entry[2])
    True
    the value "5.0" is too small.
    True
    the value "5.0" is too small.
    True
    the value "5.0" is too small.
    
    Test unicode handling, BOM, write witha file like object and line endings :
    >>> u_base = '''
    ... # initial comment
    ...     # inital comment 2
    ... 
    ... test1 = some value
    ... # comment
    ... test2 = another value    # inline comment
    ... # section comment
    ... [section]    # inline comment
    ...     test = test    # another inline comment
    ...     test2 = test2
    ... 
    ... # final comment
    ... # final comment2
    ... '''
    >>> u = u_base.encode('utf_8').splitlines(True)
    >>> u[0] = BOM_UTF8 + u[0]
    >>> uc = ConfigObj(u)
    >>> uc.encoding = None
    >>> uc.BOM == True
    1
    >>> uc == {'test1': 'some value', 'test2': 'another value',
    ... 'section': {'test': 'test', 'test2': 'test2'}}
    1
    >>> uc = ConfigObj(u, encoding='utf_8', default_encoding='latin-1')
    >>> uc.BOM
    1
    >>> isinstance(uc['test1'], unicode)
    1
    >>> uc.encoding
    'utf_8'
    >>> uc.newlines
    '\\n'
    >>> uc['latin1'] = "This costs lot's of "
    >>> a_list = uc.write()
    >>> len(a_list)
    15
    >>> isinstance(a_list[0], str)
    1
    >>> a_list[0].startswith(BOM_UTF8)
    1
    >>> u = u_base.replace('\\n', '\\r\\n').encode('utf_8').splitlines(True)
    >>> uc = ConfigObj(u)
    >>> uc.newlines
    '\\r\\n'
    >>> uc.newlines = '\\r'
    >>> file_like = StringIO()
    >>> uc.write(file_like)
    >>> file_like.seek(0)
    >>> uc2 = ConfigObj(file_like)
    >>> uc2 == uc
    1
    >>> uc2.filename == None
    1
    >>> uc2.newlines == '\\r'
    1
    
    Test validate in copy mode
    >>> a = '''
    ... # Initial Comment
    ... 
    ... key1 = string(default=Hello)
    ... 
    ... # section comment
    ... [section] # inline comment
    ... # key1 comment
    ... key1 = integer(default=6)
    ... # key2 comment
    ... key2 = boolean(default=True)
    ... 
    ...     # subsection comment
    ...     [[sub-section]] # inline comment
    ...     # another key1 comment
    ...     key1 = float(default=3.0)'''.splitlines()
    >>> b = ConfigObj(configspec=a)
    >>> b.validate(val, copy=True)
    1
    >>> b.write() == ['',
    ... '# Initial Comment',
    ... '',
    ... 'key1 = Hello',
    ... '',
    ... '# section comment',
    ... '[section]    # inline comment',
    ... '    # key1 comment',
    ... '    key1 = 6',
    ... '    # key2 comment',
    ... '    key2 = True',
    ... '    ',
    ... '    # subsection comment',
    ... '    [[sub-section]]    # inline comment',
    ... '        # another key1 comment',
    ... '        key1 = 3.0']
    1
    
    Test Writing Empty Values
    >>> a = '''
    ...     key1 =
    ...     key2 =# a comment''' 
    >>> b = ConfigObj(a.splitlines())
    >>> b.write()
    ['', 'key1 = ""', 'key2 = ""    # a comment']
    >>> b.write_empty_values = True
    >>> b.write()
    ['', 'key1 = ', 'key2 =     # a comment']
    
    Test unrepr when reading
    >>> a = '''
    ...     key1 = (1, 2, 3)    # comment
    ...     key2 = True
    ...     key3 = 'a string'
    ...     key4 = [1, 2, 3, 'a mixed list']
    ... '''.splitlines()
    >>> b = ConfigObj(a, unrepr=True)
    >>> b == {'key1': (1, 2, 3),
    ... 'key2': True,
    ... 'key3': 'a string',
    ... 'key4': [1, 2, 3, 'a mixed list']}
    1
    
    Test unrepr when writing
    >>> c = ConfigObj(b.write(), unrepr=True)
    >>> c == b
    1
    
    Test unrepr with multiline values
    >>> a = '''k = \"""{
    ... 'k1': 3,
    ... 'k2': 6.0}\"""
    ... '''.splitlines()
    >>> c = ConfigObj(a, unrepr=True)
    >>> c == {'k': {'k1': 3, 'k2': 6.0}}
    1
    
    Test unrepr with a dictionary
    >>> a = 'k = {"a": 1}'.splitlines()
    >>> c = ConfigObj(a, unrepr=True)
    >>> type(c['k']) == dict
    1
        
    >>> a = ConfigObj()
    >>> a['a'] = 'fish'
    >>> a.as_bool('a')
    Traceback (most recent call last):
    ValueError: Value "fish" is neither True nor False
    >>> a['b'] = 'True'
    >>> a.as_bool('b')
    1
    >>> a['b'] = 'off'
    >>> a.as_bool('b')
    0
        
    >>> a = ConfigObj()
    >>> a['a'] = 'fish'
    >>> try:
    ...     a.as_int('a') #doctest: +ELLIPSIS
    ... except ValueError, e:
    ...     err_mess = str(e)
    >>> err_mess.startswith('invalid literal for int()')
    1
    >>> a['b'] = '1'
    >>> a.as_int('b')
    1
    >>> a['b'] = '3.2'
    >>> try:
    ...     a.as_int('b') #doctest: +ELLIPSIS
    ... except ValueError, e:
    ...     err_mess = str(e)
    >>> err_mess.startswith('invalid literal for int()')
    1
        
    >>> a = ConfigObj()
    >>> a['a'] = 'fish'
    >>> a.as_float('a')
    Traceback (most recent call last):
    ValueError: invalid literal for float(): fish
    >>> a['b'] = '1'
    >>> a.as_float('b')
    1.0
    >>> a['b'] = '3.2'
    >>> a.as_float('b')
    3.2000000000000002
    
     Test # with unrepr
     >>> a = '''
     ...     key1 = (1, 2, 3)    # comment
     ...     key2 = True
     ...     key3 = 'a string'
     ...     key4 = [1, 2, 3, 'a mixed list#']
     ... '''.splitlines()
     >>> b = ConfigObj(a, unrepr=True)
     >>> b == {'key1': (1, 2, 3),
     ... 'key2': True,
     ... 'key3': 'a string',
     ... 'key4': [1, 2, 3, 'a mixed list#']}
     1
    """
    
    # Comments are no longer parsed from values in configspecs 
    # so the following test fails and is disabled
    untested = """
    Test validate in copy mode
    >>> a = '''
    ... # Initial Comment
    ... 
    ... key1 = string(default=Hello)    # comment 1
    ... 
    ... # section comment
    ... [section] # inline comment
    ... # key1 comment
    ... key1 = integer(default=6) # an integer value
    ... # key2 comment
    ... key2 = boolean(default=True) # a boolean
    ... 
    ...     # subsection comment
    ...     [[sub-section]] # inline comment
    ...     # another key1 comment
    ...     key1 = float(default=3.0) # a float'''.splitlines()
    >>> b = ConfigObj(configspec=a)
    >>> b.validate(val, copy=True)
    1
    >>> b.write()
    >>> b.write() == ['',
    ... '# Initial Comment',
    ... '',
    ... 'key1 = Hello    # comment 1',
    ... '',
    ... '# section comment',
    ... '[section]    # inline comment',
    ... '    # key1 comment',
    ... '    key1 = 6    # an integer value',
    ... '    # key2 comment',
    ... '    key2 = True    # a boolean',
    ... '    ',
    ... '    # subsection comment',
    ... '    [[sub-section]]    # inline comment',
    ... '        # another key1 comment',
    ... '        key1 = 3.0    # a float']
    1
    """


def _test_configobj():
    """
    Testing ConfigObj
    Testing with duplicate keys and sections.
    
    >>> c = '''
    ... [hello]
    ... member = value
    ... [hello again]
    ... member = value
    ... [ "hello" ]
    ... member = value
    ... '''
    >>> ConfigObj(c.split('\\n'), raise_errors = True)
    Traceback (most recent call last):
    DuplicateError: Duplicate section name at line 6.
    
    >>> d = '''
    ... [hello]
    ... member = value
    ... [hello again]
    ... member1 = value
    ... member2 = value
    ... 'member1' = value
    ... [ "and again" ]
    ... member = value
    ... '''
    >>> ConfigObj(d.split('\\n'), raise_errors = True)
    Traceback (most recent call last):
    DuplicateError: Duplicate keyword name at line 7.

    Testing ConfigParser-style interpolation
    
    >>> c = ConfigObj()
    >>> c['DEFAULT'] = {
    ...     'b': 'goodbye',
    ...     'userdir': 'c:\\\\home',
    ...     'c': '%(d)s',
    ...     'd': '%(c)s'
    ... }
    >>> c['section'] = {
    ...     'a': '%(datadir)s\\\\some path\\\\file.py',
    ...     'b': '%(userdir)s\\\\some path\\\\file.py',
    ...     'c': 'Yo %(a)s',
    ...     'd': '%(not_here)s',
    ...     'e': '%(e)s',
    ... }
    >>> c['section']['DEFAULT'] = {
    ...     'datadir': 'c:\\\\silly_test',
    ...     'a': 'hello - %(b)s',
    ... }
    >>> c['section']['a'] == 'c:\\\\silly_test\\\\some path\\\\file.py'
    1
    >>> c['section']['b'] == 'c:\\\\home\\\\some path\\\\file.py'
    1
    >>> c['section']['c'] == 'Yo c:\\\\silly_test\\\\some path\\\\file.py'
    1
    
    Switching Interpolation Off
    
    >>> c.interpolation = False
    >>> c['section']['a'] == '%(datadir)s\\\\some path\\\\file.py'
    1
    >>> c['section']['b'] == '%(userdir)s\\\\some path\\\\file.py'
    1
    >>> c['section']['c'] == 'Yo %(a)s'
    1
    
    Testing the interpolation errors.
    
    >>> c.interpolation = True
    >>> c['section']['d']
    Traceback (most recent call last):
    MissingInterpolationOption: missing option "not_here" in interpolation.
    >>> c['section']['e']
    Traceback (most recent call last):
    InterpolationLoopError: interpolation loop detected in value "e".
    
    Testing Template-style interpolation
    
    >>> interp_cfg = '''
    ... [DEFAULT]
    ... keyword1 = value1
    ... 'keyword 2' = 'value 2'
    ... reference = ${keyword1}
    ... foo = 123
    ... 
    ... [ section ]
    ... templatebare = $keyword1/foo
    ... bar = $$foo
    ... dollar = $$300.00
    ... stophere = $$notinterpolated
    ... with_braces = ${keyword1}s (plural)
    ... with_spaces = ${keyword 2}!!!
    ... with_several = $keyword1/$reference/$keyword1
    ... configparsersample = %(keyword 2)sconfig
    ... deep = ${reference}
    ... 
    ...     [[DEFAULT]]
    ...     baz = $foo
    ... 
    ...     [[ sub-section ]]
    ...     quux = '$baz + $bar + $foo'
    ... 
    ...         [[[ sub-sub-section ]]]
    ...         convoluted = "$bar + $baz + $quux + $bar"
    ... '''
    >>> c = ConfigObj(interp_cfg.split('\\n'), interpolation='Template')
    >>> c['section']['templatebare']
    'value1/foo'
    >>> c['section']['dollar']
    '$300.00'
    >>> c['section']['stophere']
    '$notinterpolated'
    >>> c['section']['with_braces']
    'value1s (plural)'
    >>> c['section']['with_spaces']
    'value 2!!!'
    >>> c['section']['with_several']
    'value1/value1/value1'
    >>> c['section']['configparsersample']
    '%(keyword 2)sconfig'
    >>> c['section']['deep']
    'value1'
    >>> c['section']['sub-section']['quux']
    '123 + $foo + 123'
    >>> c['section']['sub-section']['sub-sub-section']['convoluted']
    '$foo + 123 + 123 + $foo + 123 + $foo'
    
    Testing our quoting.
    
    >>> i._quote('\"""\\'\\'\\'')
    Traceback (most recent call last):
    ConfigObjError: Value \"\"""'''" cannot be safely quoted.
    >>> try:
    ...     i._quote('\\n', multiline=False)
    ... except ConfigObjError, e:
    ...    e.msg
    'Value "\\n" cannot be safely quoted.'
    >>> i._quote(' "\\' ', multiline=False)
    Traceback (most recent call last):
    ConfigObjError: Value " "' " cannot be safely quoted.
    
    Testing with "stringify" off.
    >>> c.stringify = False
    >>> c['test'] = 1
    Traceback (most recent call last):
    TypeError: Value is not a string "1".
    
    Testing Empty values.
    >>> cfg_with_empty = '''
    ... k =
    ... k2 =# comment test
    ... val = test
    ... val2 = ,
    ... val3 = 1,
    ... val4 = 1, 2
    ... val5 = 1, 2, \'''.splitlines()
    >>> cwe = ConfigObj(cfg_with_empty)
    >>> cwe == {'k': '', 'k2': '', 'val': 'test', 'val2': [],
    ...  'val3': ['1'], 'val4': ['1', '2'], 'val5': ['1', '2']}
    1
    >>> cwe = ConfigObj(cfg_with_empty, list_values=False)
    >>> cwe == {'k': '', 'k2': '', 'val': 'test', 'val2': ',',
    ...  'val3': '1,', 'val4': '1, 2', 'val5': '1, 2,'}
    1
    
    Testing list values.
    >>> testconfig3 = \'''
    ... a = ,
    ... b = test,
    ... c = test1, test2   , test3
    ... d = test1, test2, test3,
    ... \'''
    >>> d = ConfigObj(testconfig3.split('\\n'), raise_errors=True)
    >>> d['a'] == []
    1
    >>> d['b'] == ['test']
    1
    >>> d['c'] == ['test1', 'test2', 'test3']
    1
    >>> d['d'] == ['test1', 'test2', 'test3']
    1
    
    Testing with list values off.
    
    >>> e = ConfigObj(
    ...     testconfig3.split('\\n'),
    ...     raise_errors=True,
    ...     list_values=False)
    >>> e['a'] == ','
    1
    >>> e['b'] == 'test,'
    1
    >>> e['c'] == 'test1, test2   , test3'
    1
    >>> e['d'] == 'test1, test2, test3,'
    1
    
    Testing creating from a dictionary.
    
    >>> f = {
    ...     'key1': 'val1',
    ...     'key2': 'val2',
    ...     'section 1': {
    ...         'key1': 'val1',
    ...         'key2': 'val2',
    ...         'section 1b': {
    ...             'key1': 'val1',
    ...             'key2': 'val2',
    ...         },
    ...     },
    ...     'section 2': {
    ...         'key1': 'val1',
    ...         'key2': 'val2',
    ...         'section 2b': {
    ...             'key1': 'val1',
    ...             'key2': 'val2',
    ...         },
    ...     },
    ...      'key3': 'val3',
    ... }
    >>> g = ConfigObj(f)
    >>> f == g
    1
    
    Testing we correctly detect badly built list values (4 of them).
    
    >>> testconfig4 = '''
    ... config = 3,4,,
    ... test = 3,,4
    ... fish = ,,
    ... dummy = ,,hello, goodbye
    ... '''
    >>> try:
    ...     ConfigObj(testconfig4.split('\\n'))
    ... except ConfigObjError, e:
    ...     len(e.errors)
    4
    
    Testing we correctly detect badly quoted values (4 of them).
    
    >>> testconfig5 = '''
    ... config = "hello   # comment
    ... test = 'goodbye
    ... fish = 'goodbye   # comment
    ... dummy = "hello again
    ... '''
    >>> try:
    ...     ConfigObj(testconfig5.split('\\n'))
    ... except ConfigObjError, e:
    ...     len(e.errors)
    4
    
    Test Multiline Comments
    >>> i == {
    ...     'name4': ' another single line value ',
    ...     'multi section': {
    ...         'name4': '\\n        Well, this is a\\n        multiline '
    ...             'value\\n        ',
    ...         'name2': '\\n        Well, this is a\\n        multiline '
    ...             'value\\n        ',
    ...         'name3': '\\n        Well, this is a\\n        multiline '
    ...             'value\\n        ',
    ...         'name1': '\\n        Well, this is a\\n        multiline '
    ...             'value\\n        ',
    ...     },
    ...     'name2': ' another single line value ',
    ...     'name3': ' a single line value ',
    ...     'name1': ' a single line value ',
    ... }
    1
     
    >>> filename = a.filename
    >>> a.filename = None
    >>> values = a.write()
    >>> index = 0
    >>> while index < 23:
    ...     index += 1
    ...     line = values[index-1]
    ...     assert line.endswith('# comment ' + str(index))
    >>> a.filename = filename
    
    >>> start_comment = ['# Initial Comment', '', '#']
    >>> end_comment = ['', '#', '# Final Comment']
    >>> newconfig = start_comment + testconfig1.split('\\n') + end_comment
    >>> nc = ConfigObj(newconfig)
    >>> nc.initial_comment
    ['# Initial Comment', '', '#']
    >>> nc.final_comment
    ['', '#', '# Final Comment']
    >>> nc.initial_comment == start_comment
    1
    >>> nc.final_comment == end_comment
    1
    
    Test the _handle_comment method
    
    >>> c = ConfigObj()
    >>> c['foo'] = 'bar'
    >>> c.inline_comments['foo'] = 'Nice bar'
    >>> c.write()
    ['foo = bar # Nice bar']
    
    tekNico: FIXME: use StringIO instead of real files
    
    >>> filename = a.filename
    >>> a.filename = 'test.ini'
    >>> a.write()
    >>> a.filename = filename
    >>> a == ConfigObj('test.ini', raise_errors=True)
    1
    >>> os.remove('test.ini')
    >>> b.filename = 'test.ini'
    >>> b.write()
    >>> b == ConfigObj('test.ini', raise_errors=True)
    1
    >>> os.remove('test.ini')
    >>> i.filename = 'test.ini'
    >>> i.write()
    >>> i == ConfigObj('test.ini', raise_errors=True)
    1
    >>> os.remove('test.ini')
    >>> a = ConfigObj()
    >>> a['DEFAULT'] = {'a' : 'fish'}
    >>> a['a'] = '%(a)s'
    >>> a.write()
    ['a = %(a)s', '[DEFAULT]', 'a = fish']
    
    Test indentation handling
    
    >>> ConfigObj({'sect': {'sect': {'foo': 'bar'}}}).write()
    ['[sect]', '    [[sect]]', '        foo = bar']
    >>> cfg = ['[sect]', '[[sect]]', 'foo = bar']
    >>> ConfigObj(cfg).write() == cfg
    1
    >>> cfg = ['[sect]', '  [[sect]]', '    foo = bar']
    >>> ConfigObj(cfg).write() == cfg
    1
    >>> cfg = ['[sect]', '    [[sect]]', '        foo = bar']
    >>> ConfigObj(cfg).write() == cfg
    1
    >>> ConfigObj(oneTabCfg).write() == oneTabCfg
    1
    >>> ConfigObj(twoTabsCfg).write() == twoTabsCfg
    1
    >>> ConfigObj(tabsAndSpacesCfg).write() == tabsAndSpacesCfg
    1
    >>> ConfigObj(cfg, indent_type=chr(9)).write() == oneTabCfg
    1
    >>> ConfigObj(oneTabCfg, indent_type='    ').write() == cfg
    1
    """


def _test_validate():
    """
    >>> config = '''
    ... test1=40
    ... test2=hello
    ... test3=3
    ... test4=5.0
    ... [section]
    ...     test1=40
    ...     test2=hello
    ...     test3=3
    ...     test4=5.0
    ...     [[sub section]]
    ...         test1=40
    ...         test2=hello
    ...         test3=3
    ...         test4=5.0
    ... '''.split('\\n')
    >>> configspec = '''
    ... test1= integer(30,50)
    ... test2= string
    ... test3=integer
    ... test4=float(6.0)
    ... [section ]
    ...     test1=integer(30,50)
    ...     test2=string
    ...     test3=integer
    ...     test4=float(6.0)
    ...     [[sub section]]
    ...         test1=integer(30,50)
    ...         test2=string
    ...         test3=integer
    ...         test4=float(6.0)
    ... '''.split('\\n')
    >>> val = Validator()
    >>> c1 = ConfigObj(config, configspec=configspec)
    >>> test = c1.validate(val)
    >>> test == {
    ...         'test1': True,
    ...         'test2': True,
    ...         'test3': True,
    ...         'test4': False,
    ...         'section': {
    ...             'test1': True,
    ...             'test2': True,
    ...             'test3': True,
    ...             'test4': False,
    ...             'sub section': {
    ...                 'test1': True,
    ...                 'test2': True,
    ...                 'test3': True,
    ...                 'test4': False,
    ...             },
    ...         },
    ...     }
    1
    >>> val.check(c1.configspec['test4'], c1['test4'])
    Traceback (most recent call last):
    VdtValueTooSmallError: the value "5.0" is too small.
    
    >>> val_test_config = '''
    ...     key = 0
    ...     key2 = 1.1
    ...     [section]
    ...     key = some text
    ...     key2 = 1.1, 3.0, 17, 6.8
    ...         [[sub-section]]
    ...         key = option1
    ...         key2 = True'''.split('\\n')
    >>> val_test_configspec = '''
    ...     key = integer
    ...     key2 = float
    ...     [section]
    ...     key = string
    ...     key2 = float_list(4)
    ...        [[sub-section]]
    ...        key = option(option1, option2)
    ...        key2 = boolean'''.split('\\n')
    >>> val_test = ConfigObj(val_test_config, configspec=val_test_configspec)
    >>> val_test.validate(val)
    1
    >>> val_test['key'] = 'text not a digit'
    >>> val_res = val_test.validate(val)
    >>> val_res == {'key2': True, 'section': True, 'key': False}
    1
    >>> configspec = '''
    ...     test1=integer(30,50, default=40)
    ...     test2=string(default="hello")
    ...     test3=integer(default=3)
    ...     test4=float(6.0, default=6.0)
    ...     [section ]
    ...         test1=integer(30,50, default=40)
    ...         test2=string(default="hello")
    ...         test3=integer(default=3)
    ...         test4=float(6.0, default=6.0)
    ...         [[sub section]]
    ...             test1=integer(30,50, default=40)
    ...             test2=string(default="hello")
    ...             test3=integer(default=3)
    ...             test4=float(6.0, default=6.0)
    ...     '''.split('\\n')
    >>> default_test = ConfigObj(['test1=30'], configspec=configspec)
    >>> default_test
    ConfigObj({'test1': '30'})
    >>> default_test.defaults
    []
    >>> default_test.default_values
    {}
    >>> default_test.validate(val)
    1
    >>> default_test == {
    ...     'test1': 30,
    ...     'test2': 'hello',
    ...     'test3': 3,
    ...     'test4': 6.0,
    ...     'section': {
    ...         'test1': 40,
    ...         'test2': 'hello',
    ...         'test3': 3,
    ...         'test4': 6.0,
    ...         'sub section': {
    ...             'test1': 40,
    ...             'test3': 3,
    ...             'test2': 'hello',
    ...             'test4': 6.0,
    ...         },
    ...     },
    ... }
    1
    >>> default_test.defaults
    ['test2', 'test3', 'test4']
    >>> default_test.default_values == {'test1': 40, 'test2': 'hello',
    ... 'test3': 3, 'test4': 6.0}
    1
    >>> default_test.restore_default('test1')
    40
    >>> default_test['test1']
    40
    >>> 'test1' in default_test.defaults
    1
    >>> def change(section, key): 
    ...     section[key] = 3
    >>> _ = default_test.walk(change)
    >>> default_test['section']['sub section']['test4']
    3
    >>> default_test.restore_defaults()
    >>> default_test == {
    ...     'test1': 40,
    ...     'test2': "hello",
    ...     'test3': 3,
    ...     'test4': 6.0,
    ...     'section': {
    ...         'test1': 40,
    ...         'test2': "hello",
    ...         'test3': 3,
    ...         'test4': 6.0,
    ...         'sub section': {
    ...             'test1': 40,
    ...             'test2': "hello",
    ...             'test3': 3,
    ...             'test4': 6.0
    ... }}}
    1
    >>> a = ['foo = fish']
    >>> b = ['foo = integer(default=3)']
    >>> c = ConfigObj(a, configspec=b)
    >>> c
    ConfigObj({'foo': 'fish'})
    >>> from validate import Validator
    >>> v = Validator()
    >>> c.validate(v)
    0
    >>> c.default_values
    {'foo': 3}
    >>> c.restore_default('foo')
    3

    Now testing with repeated sections : BIG TEST
    
    >>> repeated_1 = '''
    ... [dogs]
    ...     [[__many__]] # spec for a dog
    ...         fleas = boolean(default=True)
    ...         tail = option(long, short, default=long)
    ...         name = string(default=rover)
    ...         [[[__many__]]]  # spec for a puppy
    ...             name = string(default="son of rover")
    ...             age = float(default=0.0)
    ... [cats]
    ...     [[__many__]] # spec for a cat
    ...         fleas = boolean(default=True)
    ...         tail = option(long, short, default=short)
    ...         name = string(default=pussy)
    ...         [[[__many__]]] # spec for a kitten
    ...             name = string(default="son of pussy")
    ...             age = float(default=0.0)
    ...         '''.split('\\n')
    >>> repeated_2 = '''
    ... [dogs]
    ... 
    ...     # blank dogs with puppies
    ...     # should be filled in by the configspec
    ...     [[dog1]]
    ...         [[[puppy1]]]
    ...         [[[puppy2]]]
    ...         [[[puppy3]]]
    ...     [[dog2]]
    ...         [[[puppy1]]]
    ...         [[[puppy2]]]
    ...         [[[puppy3]]]
    ...     [[dog3]]
    ...         [[[puppy1]]]
    ...         [[[puppy2]]]
    ...         [[[puppy3]]]
    ... [cats]
    ... 
    ...     # blank cats with kittens
    ...     # should be filled in by the configspec
    ...     [[cat1]]
    ...         [[[kitten1]]]
    ...         [[[kitten2]]]
    ...         [[[kitten3]]]
    ...     [[cat2]]
    ...         [[[kitten1]]]
    ...         [[[kitten2]]]
    ...         [[[kitten3]]]
    ...     [[cat3]]
    ...         [[[kitten1]]]
    ...         [[[kitten2]]]
    ...         [[[kitten3]]]
    ... '''.split('\\n')
    >>> repeated_3 = '''
    ... [dogs]
    ... 
    ...     [[dog1]]
    ...     [[dog2]]
    ...     [[dog3]]
    ... [cats]
    ... 
    ...     [[cat1]]
    ...     [[cat2]]
    ...     [[cat3]]
    ... '''.split('\\n')
    >>> repeated_4 = '''
    ... [__many__]
    ... 
    ...     name = string(default=Michael)
    ...     age = float(default=0.0)
    ...     sex = option(m, f, default=m)
    ... '''.split('\\n')
    >>> repeated_5 = '''
    ... [cats]
    ... [[__many__]]
    ...     fleas = boolean(default=True)
    ...     tail = option(long, short, default=short)
    ...     name = string(default=pussy)
    ...     [[[description]]]
    ...         height = float(default=3.3)
    ...         weight = float(default=6)
    ...         [[[[coat]]]]
    ...             fur = option(black, grey, brown, "tortoise shell", default=black)
    ...             condition = integer(0,10, default=5)
    ... '''.split('\\n')
    >>> val= Validator()
    >>> repeater = ConfigObj(repeated_2, configspec=repeated_1)
    >>> repeater.validate(val)
    1
    >>> repeater == {
    ...     'dogs': {
    ...         'dog1': {
    ...             'fleas': True,
    ...             'tail': 'long',
    ...             'name': 'rover',
    ...             'puppy1': {'name': 'son of rover', 'age': 0.0},
    ...             'puppy2': {'name': 'son of rover', 'age': 0.0},
    ...             'puppy3': {'name': 'son of rover', 'age': 0.0},
    ...         },
    ...         'dog2': {
    ...             'fleas': True,
    ...             'tail': 'long',
    ...             'name': 'rover',
    ...             'puppy1': {'name': 'son of rover', 'age': 0.0},
    ...             'puppy2': {'name': 'son of rover', 'age': 0.0},
    ...             'puppy3': {'name': 'son of rover', 'age': 0.0},
    ...         },
    ...         'dog3': {
    ...             'fleas': True,
    ...             'tail': 'long',
    ...             'name': 'rover',
    ...             'puppy1': {'name': 'son of rover', 'age': 0.0},
    ...             'puppy2': {'name': 'son of rover', 'age': 0.0},
    ...             'puppy3': {'name': 'son of rover', 'age': 0.0},
    ...         },
    ...     },
    ...     'cats': {
    ...         'cat1': {
    ...             'fleas': True,
    ...             'tail': 'short',
    ...             'name': 'pussy',
    ...             'kitten1': {'name': 'son of pussy', 'age': 0.0},
    ...             'kitten2': {'name': 'son of pussy', 'age': 0.0},
    ...             'kitten3': {'name': 'son of pussy', 'age': 0.0},
    ...         },
    ...         'cat2': {
    ...             'fleas': True,
    ...             'tail': 'short',
    ...             'name': 'pussy',
    ...             'kitten1': {'name': 'son of pussy', 'age': 0.0},
    ...             'kitten2': {'name': 'son of pussy', 'age': 0.0},
    ...             'kitten3': {'name': 'son of pussy', 'age': 0.0},
    ...         },
    ...         'cat3': {
    ...             'fleas': True,
    ...             'tail': 'short',
    ...             'name': 'pussy',
    ...             'kitten1': {'name': 'son of pussy', 'age': 0.0},
    ...             'kitten2': {'name': 'son of pussy', 'age': 0.0},
    ...             'kitten3': {'name': 'son of pussy', 'age': 0.0},
    ...         },
    ...     },
    ... }
    1
    >>> repeater = ConfigObj(repeated_3, configspec=repeated_1)
    >>> repeater.validate(val)
    1
    >>> repeater == {
    ...     'cats': {
    ...         'cat1': {'fleas': True, 'tail': 'short', 'name': 'pussy'},
    ...         'cat2': {'fleas': True, 'tail': 'short', 'name': 'pussy'},
    ...         'cat3': {'fleas': True, 'tail': 'short', 'name': 'pussy'},
    ...     },
    ...     'dogs': {
    ...         'dog1': {'fleas': True, 'tail': 'long', 'name': 'rover'},
    ...         'dog2': {'fleas': True, 'tail': 'long', 'name': 'rover'},
    ...         'dog3': {'fleas': True, 'tail': 'long', 'name': 'rover'},
    ...     },
    ... }
    1
    >>> repeater = ConfigObj(configspec=repeated_4)
    >>> repeater['Michael'] = {}
    >>> repeater.validate(val)
    1
    >>> repeater == {
    ...     'Michael': {'age': 0.0, 'name': 'Michael', 'sex': 'm'},
    ... }
    1
    >>> repeater = ConfigObj(repeated_3, configspec=repeated_5)
    >>> repeater == {
    ...     'dogs': {'dog1': {}, 'dog2': {}, 'dog3': {}},
    ...     'cats': {'cat1': {}, 'cat2': {}, 'cat3': {}},
    ... }
    1
    >>> repeater.validate(val)
    1
    >>> repeater == {
    ...     'dogs': {'dog1': {}, 'dog2': {}, 'dog3': {}},
    ...     'cats': {
    ...         'cat1': {
    ...             'fleas': True,
    ...             'tail': 'short',
    ...             'name': 'pussy',
    ...             'description': {
    ...                 'weight': 6.0,
    ...                 'height': 3.2999999999999998,
    ...                 'coat': {'fur': 'black', 'condition': 5},
    ...             },
    ...         },
    ...         'cat2': {
    ...             'fleas': True,
    ...             'tail': 'short',
    ...             'name': 'pussy',
    ...             'description': {
    ...                 'weight': 6.0,
    ...                 'height': 3.2999999999999998,
    ...                 'coat': {'fur': 'black', 'condition': 5},
    ...             },
    ...         },
    ...         'cat3': {
    ...             'fleas': True,
    ...             'tail': 'short',
    ...             'name': 'pussy',
    ...             'description': {
    ...                 'weight': 6.0,
    ...                 'height': 3.2999999999999998,
    ...                 'coat': {'fur': 'black', 'condition': 5},
    ...             },
    ...         },
    ...     },
    ... }
    1
    
    Test that interpolation is preserved for validated string values.
    Also check that interpolation works in configspecs.
    >>> t = ConfigObj(configspec=['test = string'])
    >>> t['DEFAULT'] = {}
    >>> t['DEFAULT']['def_test'] = 'a'
    >>> t['test'] = '%(def_test)s'
    >>> t['test']
    'a'
    >>> v = Validator()
    >>> t.validate(v)
    1
    >>> t.interpolation = False
    >>> t
    ConfigObj({'test': '%(def_test)s', 'DEFAULT': {'def_test': 'a'}})
    >>> specs = [
    ...    'interpolated string  = string(default="fuzzy-%(man)s")',
    ...    '[DEFAULT]',
    ...    'man = wuzzy',
    ...    ]
    >>> c = ConfigObj(configspec=specs)
    >>> c.validate(v)
    1
    >>> c['interpolated string']
    'fuzzy-wuzzy'

    Test SimpleVal
    >>> val = SimpleVal()
    >>> config = '''
    ... test1=40
    ... test2=hello
    ... test3=3
    ... test4=5.0
    ... [section]
    ... test1=40
    ... test2=hello
    ... test3=3
    ... test4=5.0
    ...     [[sub section]]
    ...     test1=40
    ...     test2=hello
    ...     test3=3
    ...     test4=5.0
    ... '''.split('\\n')
    >>> configspec = '''
    ... test1=''
    ... test2=''
    ... test3=''
    ... test4=''
    ... [section]
    ... test1=''
    ... test2=''
    ... test3=''
    ... test4=''
    ...     [[sub section]]
    ...     test1=''
    ...     test2=''
    ...     test3=''
    ...     test4=''
    ... '''.split('\\n')
    >>> o = ConfigObj(config, configspec=configspec)
    >>> o.validate(val)
    1
    >>> o = ConfigObj(configspec=configspec)
    >>> o.validate(val)
    0
    
    Test Flatten Errors
    >>> vtor = Validator()
    >>> my_ini = '''
    ...     option1 = True
    ...     [section1]
    ...     option1 = True
    ...     [section2]
    ...     another_option = Probably
    ...     [section3]
    ...     another_option = True
    ...     [[section3b]]
    ...     value = 3
    ...     value2 = a
    ...     value3 = 11
    ...     '''
    >>> my_cfg = '''
    ...     option1 = boolean()
    ...     option2 = boolean()
    ...     option3 = boolean(default=Bad_value)
    ...     [section1]
    ...     option1 = boolean()
    ...     option2 = boolean()
    ...     option3 = boolean(default=Bad_value)
    ...     [section2]
    ...     another_option = boolean()
    ...     [section3]
    ...     another_option = boolean()
    ...     [[section3b]]
    ...     value = integer
    ...     value2 = integer
    ...     value3 = integer(0, 10)
    ...         [[[section3b-sub]]]
    ...         value = string
    ...     [section4]
    ...     another_option = boolean()
    ...     '''
    >>> cs = my_cfg.split('\\n')
    >>> ini = my_ini.split('\\n')
    >>> cfg = ConfigObj(ini, configspec=cs)
    >>> res = cfg.validate(vtor, preserve_errors=True)
    >>> errors = []
    >>> for entry in flatten_errors(cfg, res):
    ...     section_list, key, error = entry
    ...     section_list.insert(0, '[root]')
    ...     if key is not None:
    ...         section_list.append(key)
    ...     section_string = ', '.join(section_list)
    ...     errors.append('%s%s%s' % (section_string, ' = ', error or 'missing'))
    >>> errors.sort()
    >>> for entry in errors:
    ...     print entry
    [root], option2 = missing
    [root], option3 = the value "Bad_value" is of the wrong type.
    [root], section1, option2 = missing
    [root], section1, option3 = the value "Bad_value" is of the wrong type.
    [root], section2, another_option = the value "Probably" is of the wrong type.
    [root], section3, section3b, section3b-sub = missing
    [root], section3, section3b, value2 = the value "a" is of the wrong type.
    [root], section3, section3b, value3 = the value "11" is too big.
    [root], section4 = missing
    """


def _test_errors():
    """
    Test the error messages and objects, in normal mode and unrepr mode.
    >>> bad_syntax = '''
    ... key = "value"
    ... key2 = "value
    ... '''.splitlines()
    >>> c = ConfigObj(bad_syntax)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 3.
    >>> c = ConfigObj(bad_syntax, raise_errors=True)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 3.
    >>> c = ConfigObj(bad_syntax, raise_errors=True, unrepr=True)
    Traceback (most recent call last):
    UnreprError: Parse error in value at line 3.
    >>> try:
    ...     c = ConfigObj(bad_syntax)
    ... except Exception, e:
    ...     pass
    >>> assert(isinstance(e, ConfigObjError))
    >>> print e
    Parse error in value at line 3.
    >>> len(e.errors) == 1
    1
    >>> try:
    ...     c = ConfigObj(bad_syntax, unrepr=True)
    ... except Exception, e:
    ...     pass
    >>> assert(isinstance(e, ConfigObjError))
    >>> print e
    Parse error in value at line 3.
    >>> len(e.errors) == 1
    1
    >>> the_error = e.errors[0]
    >>> assert(isinstance(the_error, UnreprError))
    
    >>> multiple_bad_syntax = '''
    ... key = "value"
    ... key2 = "value
    ... key3 = "value2
    ... '''.splitlines()
    >>> try:
    ...     c = ConfigObj(multiple_bad_syntax)
    ... except ConfigObjError, e:
    ...     str(e)
    'Parsing failed with several errors.\\nFirst error at line 3.'
    >>> c = ConfigObj(multiple_bad_syntax, raise_errors=True)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 3.
    >>> c = ConfigObj(multiple_bad_syntax, raise_errors=True, unrepr=True)
    Traceback (most recent call last):
    UnreprError: Parse error in value at line 3.
    >>> try:
    ...     c = ConfigObj(multiple_bad_syntax)
    ... except Exception, e:
    ...     pass
    >>> assert(isinstance(e, ConfigObjError))
    >>> print e
    Parsing failed with several errors.
    First error at line 3.
    >>> len(e.errors) == 2
    1
    >>> try:
    ...     c = ConfigObj(multiple_bad_syntax, unrepr=True)
    ... except Exception, e:
    ...     pass
    >>> assert(isinstance(e, ConfigObjError))
    >>> print e
    Parsing failed with several errors.
    First error at line 3.
    >>> len(e.errors) == 2
    1
    >>> the_error = e.errors[1]
    >>> assert(isinstance(the_error, UnreprError))
    
    >>> unknown_name = '''
    ... key = "value"
    ... key2 = value
    ... '''.splitlines()
    >>> c = ConfigObj(unknown_name)
    >>> c = ConfigObj(unknown_name, unrepr=True)
    Traceback (most recent call last):
    UnreprError: Unknown name or type in value at line 3.
    >>> c = ConfigObj(unknown_name, raise_errors=True, unrepr=True)
    Traceback (most recent call last):
    UnreprError: Unknown name or type in value at line 3.
    """


def _test_unrepr_comments():
    """
    >>> config = '''
    ... # initial comments
    ... # with two lines
    ... key = "value"
    ... # section comment
    ... [section] # inline section comment
    ... # key comment
    ... key = "value"
    ... # final comment
    ... # with two lines
    ... '''.splitlines()
    >>> c = ConfigObj(config, unrepr=True)
    >>> c == { 'key': 'value',
    ... 'section': { 'key': 'value'}}
    1
    >>> c.initial_comment == ['', '# initial comments', '# with two lines']
    1
    >>> c.comments == {'section': ['# section comment'], 'key': []}
    1
    >>> c.inline_comments == {'section': '# inline section comment', 'key': ''}
    1
    >>> c['section'].comments == { 'key': ['# key comment']}
    1
    >>> c.final_comment == ['# final comment', '# with two lines']
    1
    """


def _test_newline_terminated():
    """
    >>> c = ConfigObj()
    >>> c.newlines = '\\n'
    >>> c['a'] = 'b'
    >>> collector = StringIO()
    >>> c.write(collector)
    >>> collector.getvalue()
    'a = b\\n'
    """
    
    
def _test_hash_escaping():
    """
    >>> c = ConfigObj()
    >>> c.newlines = '\\n'
    >>> c['#a'] = 'b # something'
    >>> collector = StringIO()
    >>> c.write(collector)
    >>> collector.getvalue()
    '"#a" = "b # something"\\n'
    
    >>> c = ConfigObj()
    >>> c.newlines = '\\n'
    >>> c['a'] = 'b # something', 'c # something'
    >>> collector = StringIO()
    >>> c.write(collector)
    >>> collector.getvalue()
    'a = "b # something", "c # something"\\n'
    """


def _test_lineendings():
    """
    NOTE: Need to use a real file because this code is only
          exercised when reading from the filesystem.
          
    >>> h = open('temp', 'wb')
    >>> h.write('\\r\\n')
    >>> h.close()
    >>> c = ConfigObj('temp')
    >>> c.newlines
    '\\r\\n'
    >>> h = open('temp', 'wb')
    >>> h.write('\\n')
    >>> h.close()
    >>> c = ConfigObj('temp')
    >>> c.newlines
    '\\n'
    >>> os.remove('temp')
    """


def _test_validate_with_copy_and_many():
    """
    >>> spec = '''
    ... [section]
    ... [[__many__]]
    ... value = string(default='nothing')
    ... '''
    >>> config = '''
    ... [section]
    ... [[something]]
    ... '''
    >>> c = ConfigObj(StringIO(config), configspec=StringIO(spec))
    >>> v = Validator()
    >>> r = c.validate(v, copy=True)
    >>> c['section']['something']['value']
    'nothing'
    """
    
def _test_configspec_with_hash():
    """
    >>> spec = ['stuff = string(default="#ff00dd")']
    >>> c = ConfigObj(spec, _inspec=True)
    >>> c['stuff']
    'string(default="#ff00dd")'
    >>> c = ConfigObj(configspec=spec)
    >>> v = Validator()
    >>> c.validate(v)
    1
    >>> c['stuff']
    '#ff00dd'
    
    
    >>> spec = ['stuff = string(default="fish") # wooble']
    >>> c = ConfigObj(spec, _inspec=True)
    >>> c['stuff']
    'string(default="fish") # wooble'
    """

def _test_many_check():
    """
    >>> spec = ['__many__ = integer()']
    >>> config = ['a = 6', 'b = 7']
    >>> c = ConfigObj(config, configspec=spec)
    >>> v = Validator()
    >>> c.validate(v)
    1
    >>> type(c['a'])
    <type 'int'>
    >>> type(c['b'])
    <type 'int'>
    
    
    >>> spec = ['[name]', '__many__ = integer()']
    >>> config = ['[name]', 'a = 6', 'b = 7']
    >>> c = ConfigObj(config, configspec=spec)
    >>> v = Validator()
    >>> c.validate(v)
    1
    >>> type(c['name']['a'])
    <type 'int'>
    >>> type(c['name']['b'])
    <type 'int'>
    
    
    >>> spec = ['[__many__]', '__many__ = integer()']
    >>> config = ['[name]', 'hello = 7', '[thing]', 'fish = 0']
    >>> c = ConfigObj(config, configspec=spec)
    >>> v = Validator()
    >>> c.validate(v)
    1
    >>> type(c['name']['hello'])
    <type 'int'>
    >>> type(c['thing']['fish'])
    <type 'int'>
    
    
    >>> spec = '''
    ... ___many___ = integer
    ... [__many__]
    ... ___many___ = boolean
    ... [[__many__]]
    ... __many__ = float
    ... '''.splitlines()
    >>> config = '''
    ... fish = 8
    ... buggle = 4
    ... [hi]
    ... one = true
    ... two = false
    ... [[bye]]
    ... odd = 3
    ... whoops = 9.0
    ... [bye]
    ... one = true
    ... two = true
    ... [[lots]]
    ... odd = 3
    ... whoops = 9.0
    ... '''.splitlines()
    >>> c = ConfigObj(config, configspec=spec)
    >>> v = Validator()
    >>> c.validate(v)
    1
    >>> type(c['fish'])
    <type 'int'>
    >>> type(c['buggle'])
    <type 'int'>
    >>> c['hi']['one']
    1
    >>> c['hi']['two']
    0
    >>> type(c['hi']['bye']['odd'])
    <type 'float'>
    >>> type(c['hi']['bye']['whoops'])
    <type 'float'>
    >>> c['bye']['one']
    1
    >>> c['bye']['two']
    1
    >>> type(c['bye']['lots']['odd'])
    <type 'float'>
    >>> type(c['bye']['lots']['whoops'])
    <type 'float'>
    
    
    >>> spec = ['___many___ = integer()']
    >>> config = ['a = 6', 'b = 7']
    >>> c = ConfigObj(config, configspec=spec)
    >>> v = Validator()
    >>> c.validate(v)
    1
    >>> type(c['a'])
    <type 'int'>
    >>> type(c['b'])
    <type 'int'>

    
    >>> spec = '''
    ... [__many__]
    ... [[__many__]]
    ... __many__ = float
    ... '''.splitlines()
    >>> config = '''
    ... [hi]
    ... [[bye]]
    ... odd = 3
    ... whoops = 9.0
    ... [bye]
    ... [[lots]]
    ... odd = 3
    ... whoops = 9.0
    ... '''.splitlines()
    >>> c = ConfigObj(config, configspec=spec)
    >>> v = Validator()
    >>> c.validate(v)
    1
    >>> type(c['hi']['bye']['odd'])
    <type 'float'>
    >>> type(c['hi']['bye']['whoops'])
    <type 'float'>
    >>> type(c['bye']['lots']['odd'])
    <type 'float'>
    >>> type(c['bye']['lots']['whoops'])
    <type 'float'>
    
    >>> s = ['[dog]', '[[cow]]', 'something = boolean', '[[__many__]]', 
    ...      'fish = integer']
    >>> c = ['[dog]', '[[cow]]', 'something = true', '[[ob]]', 
    ...      'fish = 3', '[[bo]]', 'fish = 6']
    >>> ini = ConfigObj(c, configspec=s)
    >>> v = Validator()
    >>> ini.validate(v)
    1
    >>> ini['dog']['cow']['something']
    1
    >>> ini['dog']['ob']['fish']
    3
    >>> ini['dog']['bo']['fish']
    6
    
    
    >>> s = ['[cow]', 'something = boolean', '[__many__]', 
    ...      'fish = integer']
    >>> c = ['[cow]', 'something = true', '[ob]', 
    ...      'fish = 3', '[bo]', 'fish = 6']
    >>> ini = ConfigObj(c, configspec=s)
    >>> v = Validator()
    >>> ini.validate(v)
    1
    >>> ini['cow']['something']
    1
    >>> ini['ob']['fish']
    3
    >>> ini['bo']['fish']
    6
    """

    
def _unexpected_validation_errors():
    """
    Although the input is nonsensical we should not crash but correctly 
    report the failure to validate
    
    # section specified, got scalar
    >>> from validate import ValidateError 
    >>> s = ['[cow]', 'something = boolean']
    >>> c = ['cow = true']
    >>> ini = ConfigObj(c, configspec=s)
    >>> v = Validator()
    >>> ini.validate(v)
    0

    >>> ini = ConfigObj(c, configspec=s)
    >>> res = ini.validate(v, preserve_errors=True)
    >>> check = flatten_errors(ini, res)
    >>> for entry in check:
    ...     isinstance(entry[2], ValidateError)
    ...     print str(entry[2])
    True
    Section 'cow' was provided as a single value
    

    # scalar specified, got section
    >>> s = ['something = boolean']
    >>> c = ['[something]', 'cow = true']
    >>> ini = ConfigObj(c, configspec=s)
    >>> v = Validator()
    >>> ini.validate(v)
    0
    
    >>> ini = ConfigObj(c, configspec=s)
    >>> res = ini.validate(v, preserve_errors=True)
    >>> check = flatten_errors(ini, res)
    >>> for entry in check:
    ...     isinstance(entry[2], ValidateError)
    ...     print str(entry[2])
    True
    Value 'something' was provided as a section
    
    # unexpected section
    >>> s = []
    >>> c = ['[cow]', 'dog = true']
    >>> ini = ConfigObj(c, configspec=s)
    >>> v = Validator()
    >>> ini.validate(v)
    1
    
    
    >>> s = ['[cow]', 'dog = boolean']
    >>> c = ['[cow]', 'dog = true']
    >>> ini = ConfigObj(c, configspec=s)
    >>> v = Validator()
    >>> ini.validate(v, preserve_errors=True)
    1
    """
    
def _test_pickle():
    """
    >>> import pickle
    >>> s = ['[cow]', 'dog = boolean']
    >>> c = ['[cow]', 'dog = true']
    >>> ini = ConfigObj(c, configspec=s)
    >>> v = Validator()
    >>> string = pickle.dumps(ini)
    >>> new = pickle.loads(string)
    >>> new.validate(v)
    1
    """

def _test_as_list():
    """
    >>> a = ConfigObj()
    >>> a['a'] = 1
    >>> a.as_list('a')
    [1]
    >>> a['a'] = (1,)
    >>> a.as_list('a')
    [1]
    >>> a['a'] = [1]
    >>> a.as_list('a')
    [1]
    """

def _test_list_interpolation():
    """
    >>> c = ConfigObj()
    >>> c['x'] = 'foo'
    >>> c['list'] = ['%(x)s', 3]
    >>> c['list']
    ['foo', 3]
    """

def _test_extra_values():
    """
    >>> spec = ['[section]']
    >>> infile = ['bar = 3', '[something]', 'foo = fish', '[section]', 'foo=boo']
    >>> c = ConfigObj(infile, configspec=spec)
    >>> c.extra_values
    []
    >>> c.extra_values = ['bar', 'gosh', 'what']
    >>> c.validate(Validator())
    1
    >>> c.extra_values
    ['bar', 'something']
    >>> c['section'].extra_values
    ['foo']
    >>> c['something'].extra_values
    []
    """

def _test_reset_and_clear_more():
    """
    >>> c = ConfigObj()
    >>> c.extra_values = ['foo']
    >>> c.defaults = ['bar']
    >>> c.default_values = {'bar': 'baz'}
    >>> c.clear()
    >>> c.defaults
    []
    >>> c.extra_values
    []
    >>> c.default_values
    {'bar': 'baz'}
    >>> c.extra_values = ['foo']
    >>> c.defaults = ['bar']
    >>> c.reset()
    >>> c.defaults
    []
    >>> c.extra_values
    []
    >>> c.default_values
    {}
    """

def _test_invalid_lists():
    """
    >>> v = ['string = val, val2, , val3']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    >>> v = ['string = val, val2,, val3']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    >>> v = ['string = val, val2,,']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    >>> v = ['string = val, ,']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    >>> v = ['string = val, ,  ']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    >>> v = ['string = ,,']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    >>> v = ['string = ,, ']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    >>> v = ['string = ,foo']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    >>> v = ['string = foo, ']
    >>> c = ConfigObj(v)
    >>> c['string']
    ['foo']
    >>> v = ['string = foo, "']
    >>> c = ConfigObj(v)
    Traceback (most recent call last):
    ParseError: Parse error in value at line 1.
    """

def _test_validation_with_preserve_errors():
    """
    >>> v = Validator()
    >>> spec = ['[section]', 'foo = integer']
    >>> c = ConfigObj(configspec=spec)
    >>> c.validate(v, preserve_errors=True)
    {'section': False}
    >>> c = ConfigObj(['[section]'], configspec=spec)
    >>> c.validate(v)
    False
    >>> c.validate(v, preserve_errors=True)
    {'section': {'foo': False}}
    """


# test _created on Section

# TODO: Test BOM handling
# TODO: Test error code for badly built multiline values
# TODO: Test handling of StringIO
# TODO: Test interpolation with writing


if __name__ == '__main__':
    # run the code tests in doctest format
    #
    testconfig1 = """\
    key1= val    # comment 1
    key2= val    # comment 2
    # comment 3
    [lev1a]     # comment 4
    key1= val    # comment 5
    key2= val    # comment 6
    # comment 7
    [lev1b]    # comment 8
    key1= val    # comment 9
    key2= val    # comment 10
    # comment 11
        [[lev2ba]]    # comment 12
        key1= val    # comment 13
        # comment 14
        [[lev2bb]]    # comment 15
        key1= val    # comment 16
    # comment 17
    [lev1c]    # comment 18
    # comment 19
        [[lev2c]]    # comment 20
        # comment 21
            [[[lev3c]]]    # comment 22
            key1 = val    # comment 23"""
    #
    testconfig2 = """\
                        key1 = 'val1'
                        key2 =   "val2"
                        key3 = val3
                        ["section 1"] # comment
                        keys11 = val1
                        keys12 = val2
                        keys13 = val3
                        [section 2]
                        keys21 = val1
                        keys22 = val2
                        keys23 = val3
                        
                            [['section 2 sub 1']]
                            fish = 3
    """
    #
    testconfig6 = '''
    name1 = """ a single line value """ # comment
    name2 = \''' another single line value \''' # comment
    name3 = """ a single line value """
    name4 = \''' another single line value \'''
        [ "multi section" ]
        name1 = """
        Well, this is a
        multiline value
        """
        name2 = \'''
        Well, this is a
        multiline value
        \'''
        name3 = """
        Well, this is a
        multiline value
        """     # a comment
        name4 = \'''
        Well, this is a
        multiline value
        \'''  # I guess this is a comment too
    '''
    #
    # these cannot be put among the doctests, because the doctest module
    # does a string.expandtabs() on all of them, sigh
    oneTabCfg = ['[sect]', '\t[[sect]]', '\t\tfoo = bar']
    twoTabsCfg = ['[sect]', '\t\t[[sect]]', '\t\t\t\tfoo = bar']
    tabsAndSpacesCfg = ['[sect]', '\t \t [[sect]]', '\t \t \t \t foo = bar']
    #
    import doctest
    m = sys.modules.get('__main__')
    globs = m.__dict__.copy()
    a = ConfigObj(testconfig1.split('\n'), raise_errors=True)
    b = ConfigObj(testconfig2.split('\n'), raise_errors=True)
    i = ConfigObj(testconfig6.split('\n'), raise_errors=True)
    globs.update({'INTP_VER': INTP_VER, 'a': a, 'b': b, 'i': i,
        'oneTabCfg': oneTabCfg, 'twoTabsCfg': twoTabsCfg,
        'tabsAndSpacesCfg': tabsAndSpacesCfg})
    doctest.testmod(m, globs=globs)
    
    import configobj
    doctest.testmod(configobj, globs=globs)


# Man alive I prefer unittest ;-)