# $Id: local_dummy_lang.py 7504 2012-08-27 07:55:20Z grubert $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

# New language mappings are welcome.  Before doing a new translation, please
# read <http://docutils.sf.net/docs/howto/i18n.html>.  Two files must be
# translated for each language: one in docutils/languages, the other in
# docutils/parsers/rst/languages.

"""
English-language mappings for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'

labels = {
      # fixed: language-dependent
      'author': 'dummy Author',
      'authors': 'dummy Authors',
      'organization': 'dummy Organization',
      'address': 'dummy Address',
      'contact': 'dummy Contact',
      'version': 'dummy Version',
      'revision': 'dummy Revision',
      'status': 'dummy Status',
      'date': 'dummy Date',
      'copyright': 'dummy Copyright',
      'dedication': 'dummy Dedication',
      'abstract': 'dummy Abstract',
      'attention': 'dummy Attention!',
      'caution': 'dummy Caution!',
      'danger': 'dummy !DANGER!',
      'error': 'dummy Error',
      'hint': 'dummy Hint',
      'important': 'dummy Important',
      'note': 'dummy Note',
      'tip': 'dummy Tip',
      'warning': 'dummy Warning',
      'contents': 'dummy Contents'}
"""Mapping of node class name to label text."""

bibliographic_fields = {
      # language-dependent: fixed
      'dummy author': 'author',
      'dummy authors': 'authors',
      'dummy organization': 'organization',
      'dummy address': 'address',
      'dummy contact': 'contact',
      'dummy version': 'version',
      'dummy revision': 'revision',
      'dummy status': 'status',
      'dummy date': 'date',
      'dummy copyright': 'copyright',
      'dummy dedication': 'dedication',
      'dummy abstract': 'abstract'}
"""English (lowcased) to canonical name mapping for bibliographic fields."""

author_separators = [';', ',']
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""

directives = {
      # language-dependent: fixed
      'dummy attention': 'attention',
      'dummy caution': 'caution',
      'dummy code': 'code',
      'dummy code-block': 'code',
      'dummy sourcecode': 'code',
      'dummy danger': 'danger',
      'dummy error': 'error',
      'dummy hint': 'hint',
      'dummy important': 'important',
      'dummy note': 'note',
      'dummy tip': 'tip',
      'dummy warning': 'warning',
      'dummy admonition': 'admonition',
      'dummy sidebar': 'sidebar',
      'dummy topic': 'topic',
      'dummy line-block': 'line-block',
      'dummy parsed-literal': 'parsed-literal',
      'dummy rubric': 'rubric',
      'dummy epigraph': 'epigraph',
      'dummy highlights': 'highlights',
      'dummy pull-quote': 'pull-quote',
      'dummy compound': 'compound',
      'dummy container': 'container',
      #'dummy questions': 'questions',
      'dummy table': 'table',
      'dummy csv-table': 'csv-table',
      'dummy list-table': 'list-table',
      #'dummy qa': 'questions',
      #'dummy faq': 'questions',
      'dummy meta': 'meta',
      'dummy math': 'math',
      #'dummy imagemap': 'imagemap',
      'dummy image': 'image',
      'dummy figure': 'figure',
      'dummy include': 'include',
      'dummy raw': 'raw',
      'dummy replace': 'replace',
      'dummy unicode': 'unicode',
      'dummy date': 'date',
      'dummy class': 'class',
      'dummy role': 'role',
      'dummy default-role': 'default-role',
      'dummy title': 'title',
      'dummy contents': 'contents',
      'dummy sectnum': 'sectnum',
      'dummy section-numbering': 'sectnum',
      'dummy header': 'header',
      'dummy footer': 'footer',
      #'dummy footnotes': 'footnotes',
      #'dummy citations': 'citations',
      'dummy target-notes': 'target-notes',
      'dummy restructuredtext-test-directive': 'restructuredtext-test-directive'}
"""English name to registered (in directives/__init__.py) directive name
mapping."""

roles = {
    # language-dependent: fixed
    'dummy abbreviation': 'abbreviation',
    'dummy ab': 'abbreviation',
    'dummy acronym': 'acronym',
    'dummy ac': 'acronym',
    'dummy code': 'code',
    'dummy index': 'index',
    'dummy i': 'index',
    'dummy subscript': 'subscript',
    'dummy sub': 'subscript',
    'dummy superscript': 'superscript',
    'dummy sup': 'superscript',
    'dummy title-reference': 'title-reference',
    'dummy title': 'title-reference',
    'dummy t': 'title-reference',
    'dummy pep-reference': 'pep-reference',
    'dummy pep': 'pep-reference',
    'dummy rfc-reference': 'rfc-reference',
    'dummy rfc': 'rfc-reference',
    'dummy emphasis': 'emphasis',
    'dummy strong': 'strong',
    'dummy literal': 'literal',
    'dummy math': 'math',
    'dummy named-reference': 'named-reference',
    'dummy anonymous-reference': 'anonymous-reference',
    'dummy footnote-reference': 'footnote-reference',
    'dummy citation-reference': 'citation-reference',
    'dummy substitution-reference': 'substitution-reference',
    'dummy target': 'target',
    'dummy uri-reference': 'uri-reference',
    'dummy uri': 'uri-reference',
    'dummy url': 'uri-reference',
    'dummy raw': 'raw',}
"""Mapping of English role names to canonical role names for interpreted text.
"""
