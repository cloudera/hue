# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

from babel.core import *

from django.conf import settings
settings.configure(USE_I18N=True)
from django.template import Lexer, TOKEN_TEXT, TOKEN_VAR, TOKEN_BLOCK
from django.utils.translation.trans_real import inline_re, block_re, \
                                                endblock_re, plural_re, \
                                                constant_re

def extract_django(fileobj, keywords, comment_tags, options):
    """Extract messages from Django template files.

    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: a list of keywords (i.e. function names) that should
                     be recognized as translation functions
    :param comment_tags: a list of translator tags to search for and
                         include in the results
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """
    intrans = False
    inplural = False
    singular = []
    plural = []
    lineno = 1
    for t in Lexer(fileobj.read(), None).tokenize():
        lineno += t.contents.count('\n')
        if intrans:
            if t.token_type == TOKEN_BLOCK:
                endbmatch = endblock_re.match(t.contents)
                pluralmatch = plural_re.match(t.contents)
                if endbmatch:
                    if inplural:
                        yield lineno, 'ngettext', (unicode(''.join(singular)),
                                                   unicode(''.join(plural))), []
                    else:
                        yield lineno, None, unicode(''.join(singular)), []
                    intrans = False
                    inplural = False
                    singular = []
                    plural = []
                elif pluralmatch:
                    inplural = True
                else:
                    raise SyntaxError('Translation blocks must not include '
                                      'other block tags: %s' % t.contents)
            elif t.token_type == TOKEN_VAR:
                if inplural:
                    plural.append('%%(%s)s' % t.contents)
                else:
                    singular.append('%%(%s)s' % t.contents)
            elif t.token_type == TOKEN_TEXT:
                if inplural:
                    plural.append(t.contents)
                else:
                    singular.append(t.contents)
        else:
            if t.token_type == TOKEN_BLOCK:
                imatch = inline_re.match(t.contents)
                bmatch = block_re.match(t.contents)
                cmatches = constant_re.findall(t.contents)
                if imatch:
                    g = imatch.group(1)
                    if g[0] == '"':
                        g = g.strip('"')
                    elif g[0] == "'":
                        g = g.strip("'")
                    yield lineno, None, unicode(g), []
                elif bmatch:
                    for fmatch in constant_re.findall(t.contents):
                        yield lineno, None, unicode(fmatch), []
                    intrans = True
                    inplural = False
                    singular = []
                    plural = []
                elif cmatches:
                    for cmatch in cmatches:
                        yield lineno, None, unicode(cmatch), []
            elif t.token_type == TOKEN_VAR:
                parts = t.contents.split('|')
                cmatch = constant_re.match(parts[0])
                if cmatch:
                    yield lineno, None, unicode(cmatch.group(1)), []
                for p in parts[1:]:
                    if p.find(':_(') >= 0:
                        p1 = p.split(':',1)[1]
                        if p1[0] == '_':
                            p1 = p1[1:]
                        if p1[0] == '(':
                            p1 = p1.strip('()')
                        if p1[0] == "'":
                            p1 = p1.strip("'")
                        elif p1[0] == '"':
                            p1 = p1.strip('"')
                        yield lineno, None, unicode(p1), []
