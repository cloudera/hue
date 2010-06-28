#!/usr/bin/python

# Convert the reStructuredText docs to LaTeX for use in Python docs

# This script is a hacked version taken from the Optik SVN repository.

import sys, os
import re
import rfc822
from distutils.dep_util import newer_group, newer
from docutils.core import Publisher
from docutils.readers.standalone import Reader as StandaloneReader
from docutils.transforms import Transform
from docutils.writers.latex2e import Writer as LaTeXWriter, LaTeXTranslator
from docutils import nodes

class OptikReader(StandaloneReader):
    #default_transforms = (StandaloneReader.default_transforms +
    #                      (ReplacementTransform,))
    pass

# python 2.3
if not hasattr(__builtins__,"set"):
    import sets
    set = sets.Set
if not hasattr(__builtins__,"sorted"):
    def sorted(list):
        if hasattr(list,"sort"):
            return list.sort()
        # maybe it is sorted
        return list

from markup import codemarkup
missing = set()

class PyLaTeXWriter(LaTeXWriter):
    def __init__(self):
        LaTeXWriter.__init__(self)
        self.translator_class = PyLaTeXTranslator

class PyLaTeXTranslator(LaTeXTranslator):
    remap_title = {
        }
    roman = (None,None,"ii","iii","iv","v")

    refuri_override = {
        "reference" : "reference-guide",
        "callbacks" : "option-callbacks",
        }

    def __init__(self, document):
        LaTeXTranslator.__init__(self, document)
        self.label_prefix = ""
        self.docinfo = {}
        self.head_prefix = []
        self.head = []
        self.body_prefix = []
        self.in_title = False
        self.in_anydesc = False  # _title is different if it is a funcdesc
        self.admonition_stack = []

        # Disable a bunch of methods from the base class.
        empty_method = lambda self: None
        for nodetype in ('field_argument',
                         'field_body',
                         'field_list',
                         'field_name'):
            setattr(self, 'visit_' + nodetype, empty_method)
            setattr(self, 'depart_' + nodetype, empty_method)
        self.head_prefix = []
        # definitions must be guarded if multiple modules are included
        self.definitions = [
                "\\ifx\\locallinewidth\\undefined\\newlength{\\locallinewidth}\\fi\n"
                "\\setlength{\\locallinewidth}{\\linewidth}\n"
            ]
    def astext(self):
        return ''.join(self.definitions +
                       self.head_prefix +
                       self.head +
                       self.body_prefix +
                       self.body +
                       self.body_suffix)

    def set_label_prefix(self, text):
        self.label_prefix = text.replace(" ","-")

    def generate_section_label(self, title):
        title = title.lower()
        title = re.sub(r'\([^\)]*\)', '', title)
        title = re.sub(r'[^\w\s\-]', '', title)
        title = re.sub(r'\b(the|an?|and|your|are)\b', '', title)
        title = re.sub(r'(example \d+).*', r'\1', title)
        return self.label_prefix + "-" + "-".join(title.split())

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

    def visit_docinfo(self, node):
        pass

    def depart_docinfo(self, node):
        # module and summary are mandatory
        self.body.append(
                "\\section{\\module{%(module)s} --- %(summary)s}\n"
                % self.docinfo )
        if self.docinfo.has_key("moduletype"):
            self.body.append(
                    "\\declaremodule{%(moduletype)s}{%(module)s}\n"
                    % self.docinfo )
        if self.docinfo.has_key("moduleauthor"):
            self.body.append(
                    "\\moduleauthor{%(moduleauthor)s}{%(moduleauthoremail)s}\n"
                    % self.docinfo )
        if self.docinfo.has_key("synopsis"):
            self.body.append(
                    "\\modulesynopsis{%(synopsis)s}\n"
                    % self.docinfo )
        if self.docinfo.has_key("release"):
            self.body.append( "\\release{%(release)s}\n" % self.docinfo )
        if self.docinfo.has_key("shortversion"):
            self.body.append( "\\setshortversion{%(shortversion)s}\n" 
                              % self.docinfo )
        if self.docinfo.has_key("sectionauthor"):
            self.body.append(
                    "\\sectionauthor{%(sectionauthor)s}{%(sectionauthoremail)s}\n"
                    % self.docinfo )
        if self.docinfo.has_key("versionadded"):
            self.body.append(
                    "\\versionadded{%(versionadded)s}\n"
                    % self.docinfo )

    def visit_docinfo_item(self, node, name):
        if name == "author":
            (ename, email) = rfc822.parseaddr(node.astext())
            self.docinfo["moduleauthor"] = ename
            self.docinfo["moduleauthoremail"] = email
            raise nodes.SkipNode

    def depart_docinfo_item(self, node):
        pass

    def visit_field(self, node):
        if isinstance(node.parent, nodes.docinfo):
            name = node[0].astext().lower().replace(" ","")
            if name == "moduleauthor":
                (ename, email) = rfc822.parseaddr(node[1].astext())
                self.docinfo["moduleauthor"] = ename
                self.docinfo["moduleauthoremail"] = email
            elif name in ("author", "sectionauthor") :
                (ename, email) = rfc822.parseaddr(node[1].astext())
                self.docinfo["sectionauthor"] = ename
                self.docinfo["sectionauthoremail"] = email
            else:
                if name == "module":
                    self.set_label_prefix(node[1].astext())
                self.docinfo[name] = node[1].astext()
            raise nodes.SkipNode
        
    _quoted_string_re = re.compile(r'\"[^\"]*\"')
    _short_opt_string_re = re.compile(r'-[a-zA-Z]')
    _long_opt_string_re = re.compile(r'--[a-zA-Z-]+')
    _identifier_re = re.compile(r'[a-zA-Z_][a-zA-Z_0-9]*'
                                r'(\.[a-zA-Z_][a-zA-Z_0-9]*)*'
                                r'(\(\))?$')

    def visit_literal(self, node):
        assert isinstance(node[0], nodes.Text)
        text = node[0].data
        if self.in_title:
            cmd = None
        elif self._quoted_string_re.match(text):
            cmd = 'code'
        elif self._short_opt_string_re.match(text):
            cmd = 'programopt'
        elif self._long_opt_string_re.match(text):
            cmd = 'longprogramopt'
            text = text[2:]
        elif self._identifier_re.match(text):
            cmd = codemarkup.get(text)
            if cmd is None:
##                print "warning: unrecognized code word %r" % text
                missing.add(text)
                cmd = 'code'
        else:
            cmd = 'code'

        self.literal = 1
        node[0].data = text
        if cmd is not None:
            self.body.append('\\%s{' % cmd)

    # use topics for special environments
    def visit_topic(self, node):
        classes = node.get('classes', ['topic', ])
        if classes[0] in ('datadesc', 'datadescni', 'excdesc', 'classdesc*',
                        'csimplemacrodesc', 'ctypedesc', 'memberdesc',
                        'memberdescni', 'cvardesc', 'excclassdesc',
                        'funcdesc', 'funcdescni', 'methoddesc', 
                        'methoddescni', 'cmemberdesc', 'classdesc',
                        'cfuncdesc'):
            self.body.append('\n\\begin{%s}' % classes[0])
            self.context.append('\\end{%s}\n' % classes[0])
            self.in_anydesc = classes[0]
        else:
            self.context.append('')

    def depart_topic(self, node):
        self.in_anydesc = False
        self.body.append(self.context.pop())

    # use definition lists for special environments
    #
    # definition_list
    #   defintion_list_item
    #     term
    #     classifier
    #     definition
    #       paragraph ?
    def visit_definition_list(self, node):
        pass

    def depart_definition_list(self, node):
        pass

    def visit_definition_list_item(self, node):
        self._dl_term = []

    def depart_definition_list_item(self, node):
        try:
            self.body.append(self.context.pop())
        except:
            self.body.append("% WARN definition list without classifier\n")
            

    def visit_term(self, node):
        self._dl_term.append(node.astext())
        raise nodes.SkipNode

    def depart_term(self, node):
        pass
    
    def visit_classifier(self, node):
        # TODO here it should be decided if it is latex or python
        classifier = node.astext()
        
        if classifier in ('datadesc', 'datadescni', 'excdesc', 'classdesc*',
                        'csimplemacrodesc', 'ctypedesc', 'memberdesc',
                        'memberdescni', 'cvardesc', 'excclassdesc',
                        'funcdesc', 'funcdescni', 'methoddesc', 
                        'methoddescni', 'cmemberdesc', 'classdesc',
                        'cfuncdesc'):
            pass
        else:
            classifier = 'datadescni'
        self.body.append('\n\\begin{%s}' % classifier)
        self.in_anydesc = classifier
        self.body.append(self.anydesc_title(self._dl_term.pop()))
        self.context.append('\\end{%s}\n' % classifier)
        self.in_anydesc = None
        raise nodes.SkipNode

    def depart_classifier(self, node):
        pass

    def visit_definition(self, node):
        if len(self._dl_term)>0:
            # no classifier, fake it (maybe make a plain latex description).
            classifier = 'datadescni'
            self.body.append('\n\\begin{%s}' % classifier)
            self.in_anydesc = classifier
            self.body.append(self.anydesc_title(self._dl_term.pop()))
            self.context.append('\\end{%s}\n' % classifier)
            self.in_anydesc = None

    def depart_definition(self, node):
        pass


    def depart_literal(self, node):
        if not self.in_title:
            self.body.append('}')
        self.literal = 0

    def visit_literal_block(self, node):
        self.body.append("\\begin{verbatim}\n")
        self.verbatim = 1

    def depart_literal_block(self, node):
        self.verbatim = 0
        self.body.append("\n\\end{verbatim}\n")

    def anydesc_title(self, title):
        """Returns the title for xxxdesc environments."""
        def markup_optional_parameters(s):
            return s.replace('[','\\optional{').replace(']','}')
        def with_params(s):
            return markup_optional_parameters(
                        '{%s}' % s.replace('(','}{').replace(')',''))
        def with_tag_or_typename(s, braces):
            # "name", "tag name", "name(params)", "type name(params)"
            param_pos = s.find("(")
            blank_pos = s.find(" ")
            if ((blank_pos>0 and param_pos<0)
            or (blank_pos>0 and blank_pos<param_pos)):
                (tag,rest) = s.split(None,1)
                return braces[0] + tag + braces[1] + with_params(rest)
            return with_params(s)
        # 
        if self.in_anydesc in ('datadesc','datadescni','excdesc','classdesc*',
                                'csimplemacrodesc'):
            # \begin{xdesc}{name}
            return '{%s}' % title
        elif self.in_anydesc in ('ctypedesc','memberdesc','memberdescni',):
            # \begin{ctypedesc} [tag]{name}
            return with_tag_or_typename(title, '[]')
        elif self.in_anydesc in ('classdesc', 'cvardesc','excclassdesc',
                                'funcdesc','funcdescni'):
            # "funcname(arguments)" to "{funcname}{arguments}"
            # "funcname([arguments])" to "{funcname}{\optional{arguments}}"
            return with_params(title)
        elif self.in_anydesc in ('methoddesc','methoddescni'):
            # \begin{methoddesc} [type name]{name}{parameters}
            return with_tag_or_typename(title, '[]')
        elif self.in_anydesc in ('cmemberdesc','cfuncdesc'):
            # \begin{cmemberdesc} {container}{type}{name}
            return with_tag_or_typename(title, '{}')
        # fallback
        return "{%s}" % title

    def visit_title(self, node):
        title = node.astext()
        if self.in_anydesc:
            self.body.append(self.anydesc_title(title))
            raise nodes.SkipNode
        title = self.remap_title.get(title, title)
        # TODO label_prefix might not be set yet.
        label = self.generate_section_label(title)
        section_name = self.d_class.section(self.section_level + 1)
        self.body.append("\n\n\\%s{" % section_name)
        self.context.append("\\label{%s}}\n" % label)
        self.in_title = True

    def depart_title(self, node):
        self.in_title = False
        self.body.append(self.context.pop())
        
    def visit_target(self, node):
        pass

    def depart_target(self, node):
        pass

    def visit_admonition(self, node, name=''):
        self.admonition_stack.append(name)
        if name in ('note', 'warning'):
            self.body.append('\\begin{notice}[%s]' % name)
        else:
            LaTeXTranslator.visit_admonition(self, node, name)
    def depart_admonition(self, node=None):
        name = self.admonition_stack.pop()
        if name=="note":
            self.body.append('\\end{notice}\n')
        else:
            LaTeXTranslator.depart_admonition(self, node)

    def bookmark(self, node):
        pass

    def visit_reference(self, node):
        if node.has_key('refuri'):
            refuri = node['refuri']
            basename = os.path.splitext(refuri)[0]
            label = self.label_prefix + "-" + self.refuri_override.get(basename, basename)
            print "got refuri=%r, label=%r" % (refuri, label)
        elif node.has_key('refid'):
            label = self.generate_section_label(node['refid'])
            print "got refid=%r, label=%r" % (node['refid'], label)
        else:
            print "warning: unhandled reference: node=%r" % node
            LaTeXTranslator.visit_reference(self, node)          

        self.body.append("section~\\ref{%s}, " % label)
        raise nodes.SkipDeparture

    _quoted_phrase_re = re.compile(r'"([^"]+)"')
    _em_dash_re = re.compile(r'\s+\-\-\s+')

    def visit_Text(self, node):
        text = node.astext()
        if self.in_title:
            text = self.remap_title.get(text, text)

        if not (self.literal or self.verbatim):
            text = self._em_dash_re.sub(u"\u2014", text)
            text = self._quoted_phrase_re.sub(u"\u201C\\1\u201D", text)
            text = re.sub(r'\bdocument\b', "section", text)
        text = self.encode(text)

        # A couple of transformations are easiest if they go direct
        # to LaTeX, so do them *after* encode().
        text = text.replace("UNIX", "\\UNIX{}")

        self.body.append(text)

    def depart_Text(self, node):
        pass

    # table handling
    # TODO move table handling into latex2e writer Table class.
    def visit_table(self, node):
        self.active_table.open()
    def depart_table(self, node):
        self.body.append('\\end{table%s}\n' %
                        (self.roman[len(self.active_table._col_specs)]) )
        # TODO use roman to map name ? only i ... iv is supported
        self.active_table.close()
    def visit_thead(self, node):
        self.body.append('\\begin{table%s}{l%s}{textrm}\n' %
                        (self.roman[len(self.active_table._col_specs)],
                         '|l'*(len(self.active_table._col_specs)-1)
                        ) )
        self.active_table.set('preamble written',1)
    def depart_thead(self, node):
        pass
    def visit_row(self, node):
        if not isinstance(node.parent, nodes.thead):
            self.body.append('\\line%s' %
                        (self.roman[len(self.active_table._col_specs)], )
                                )
    def depart_row(self, node):
        # CAUTION: latex2html stuffs content outside of {} into paragraphs
        # before the table.
        pass
    def visit_entry(self, node):
        if node.has_key('morerows') or node.has_key('morecols'):
            raise NotImplementedError('Cells spanning rows or columns are not'
                                    ' supported.')
        # CAUTION: latex2html needs ``\lineii{`` the brace must follow
        # immediately
        self.body.append('{')
    def depart_entry(self, node):
        self.body.append('}\n')


def convert(infilename, outfilename):
    print "converting %s to %s" % (infilename, outfilename)
    pub = Publisher()
    pub.set_components('standalone',        # reader
                       'restructuredtext',  # parser
                       'latex')             # writer (arg, will be discarded)
    pub.reader = OptikReader()
    pub.writer = PyLaTeXWriter()
    pub.process_programmatic_settings(None, None, None)
    pub.set_source(source_path=infilename)
    pub.set_destination(destination_path=outfilename)
    pub.publish()

def main():
    convert(sys.argv[1], sys.argv[2])
    if missing:
        mod = open("missing.py", "w")
        mod.write("# possible markups:\n")
        mod.write("# module, code, method, class, function, member, var.  Are there more?\n")
        mod.write("codemarkup = {\n")
        keys = sorted(missing)
        for name in keys:
            mod.write("    '%s': 'code',\n" % name)
        mod.write("}\n")
        mod.close()

main()
