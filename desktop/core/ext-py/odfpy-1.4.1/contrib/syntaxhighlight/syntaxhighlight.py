#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007 Søren Roug, European Environment Agency
#
# This is free software.  You may redistribute it under the terms
# of the Apache license and the GNU General Public License Version
# 2 or at your option any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#
#
# Syntax Highlighting
# Originally from Peter Clive Wilkinson (http://www.petersblog.org/node/763)
#
import os, sys, re, getopt
from odf.opendocument import OpenDocumentText
from odf.style import FontFace, Style, TextProperties, ParagraphProperties
from odf.text import P, Span, S

class Highlight:
    """
    Do syntax highlighting.
    """

    courierfont = FontFace(name="Courier", fontfamily="Courier",
            fontadornments="Normal", fontfamilygeneric="modern", fontpitch="fixed")
    
    #--- Paragraph style --

    programliststyle = Style(name="Program Listing", family="paragraph")
    programliststyle.addElement(ParagraphProperties(border="0.002cm solid #000000", margin="0cm", padding="0.2cm"))
    programliststyle.addElement(TextProperties(fontname="Courier", fontsize="9pt", language="none", country="none"))

    #--- Text styles --
    puncstyle = Style(name="Highlighted Punctuation", family="text")
    puncstyle.addElement(TextProperties(fontweight="bold")) # Bold

    numberstyle = Style(name="Highlighted Number", family="text")
    numberstyle.addElement(TextProperties(color="#ff0000")) # Red

    keywordstyle = Style(name="Highlighted Keyword", family="text")
    keywordstyle.addElement(TextProperties(color="#b218b2", fontweight="bold")) # Blue, bold

    variablestyle = Style(name="Highlighted Magic", family="text")
    variablestyle.addElement(TextProperties(color="#0000ff")) # Blue

    tagstyle = Style(name="Highlighted Tag", family="text")
    tagstyle.addElement(TextProperties(color="#800000")) # Darkred

    attrstyle = Style(name="Highlighted Tag", family="text")
    attrstyle.addElement(TextProperties(color="#008000", fontweight="bold")) # Dark green bold

    stringstyle = Style(name="Highlighted String", family="text")
    stringstyle.addElement(TextProperties(color="#800000")) # Red

    commentstyle = Style(name="Highlighted Comment", family="text")
    commentstyle.addElement(TextProperties(color="#0000ff", fontstyle="italic")) # Blue, Italic

    preprocstyle = Style(name="Highlighted Preprocessing", family="text")
    preprocstyle.addElement(TextProperties(color="#ff00ff", fontstyle="italic")) # Magenta, Italic

    def __init__(self, strMode):
        """
        Initialise highlighter: strMode = language (PYTHON, C, CPP, PHP, HTML)
        """
         
        self.textdoc = OpenDocumentText()

        self.textdoc.fontfacedecls.addElement(self.courierfont)

        self.textdoc.styles.addElement(self.programliststyle)
        self.textdoc.styles.addElement(self.puncstyle)
        self.textdoc.styles.addElement(self.numberstyle)
        self.textdoc.styles.addElement(self.keywordstyle)
        self.textdoc.styles.addElement(self.variablestyle)
        self.textdoc.styles.addElement(self.tagstyle)
        self.textdoc.styles.addElement(self.attrstyle)
        self.textdoc.styles.addElement(self.stringstyle)
        self.textdoc.styles.addElement(self.commentstyle)
        self.textdoc.styles.addElement(self.preprocstyle)

        self.strSpanStyle = None
        self.currPara = P(stylename=self.programliststyle)
        self.textdoc.text.addElement(self.currPara)
        self.currSpan = None
        if strMode == 'CPP':
            strMode = 'C'
            self.strSuppressTokens = []
        elif strMode == 'C':
            self.strSuppressTokens = ['CPPKEYWORD']
        else:
            self.strSuppressTokens = []

        self.strMode = strMode

    def PythonHighlightToken(self, strTok, oMatch, strStyle):
        """
        Callback for python specific highlighting.
        """
        #
        # Input matches this type.
        #
        strValue = oMatch.group()

        if strTok == 'MULTILINESTRING':
            #
            # If not inside a multiline string then start one now.
            #
            self.ChangeStyle(strStyle)
            self.WriteContent(strValue)
            #
            # Remember you are in a string and remember how it was
            # started (""" vs ''')
            #
            self.strMultilineString = oMatch.group(1)
            return 'PythonMultilineString'

        elif strTok == 'ENDMULTILINESTRING':
            #
            # Multiline Token found within a multiline string
            #
            if oMatch.group(1) == self.strMultilineString:
                #
                # Token is end of multiline so stop here.
                #
                self.WriteMultiline(strValue)
                self.strMultilineString = ''
                return 'PYTHON'

        self.ChangeStyle(strStyle)
        self.WriteContent(strValue)

    def CHighlightToken(self, strTok, oMatch, strStyle):
        """
        Callback for C specific highlighting.
        """
        #
        # Input matches this type.
        #
        strValue = oMatch.group()

        #
        # Not in multiline mode so change display style as appropriate
        # and output the text.
        #
        self.ChangeStyle(strStyle)
        self.WriteContent(strValue)

    def PHPHighlightToken(self, strTok, oMatch, strStyle):
        """
        Callback for PHP specific highlighting.
        """
        #
        # Input matches this type.
        #
        strValue = oMatch.group()

        if strTok == 'MULTILINESTRING':
            #
            # If not inside a multiline string then start one now.
            #
            self.ChangeStyle(strStyle)
            self.WriteContent(strValue)
            #
            # Remember you are in a string and remember how it was
            # started (""" vs ''')
            #
            self.strMultilineString = oMatch.group(1)
            return 'PHPMultilineString'

        elif strTok == 'ENDMULTILINESTRING':
            #
            # Multiline Token found within a multiline string
            #
            if oMatch.group(1) == self.strMultilineString:
                #
                # Token is end of multiline so stop here.
                #
                self.WriteMultiline(strValue)
                self.strMultilineString = ''
                return 'PHP'

        self.ChangeStyle(strStyle)
        self.WriteContent(strValue)

        if strTok == 'GOTOHTML':
            #
            # Embedded HTML
            #
            return 'HTML'
        else:
            return None

    def HTMLHighlightToken(self, strTok, oMatch, strStyle):
        """
        Callback for HTML specific highlighting.
        """
        #
        # Input matches this type.
        #
        strValue = oMatch.group()
        self.ChangeStyle(strStyle)
        self.WriteContent(strValue)

        if strTok == 'TAG':
            #
            # Change to mode 1, 'within tag'.
            #
            return 'HTMLTag'

        elif strTok == 'ENDTAG':
            #
            # Change to mode 1, 'within tag'.
            #
            return 'HTML'

        elif strTok == 'GOTOPHP':
            #
            # Embedded PHP
            #
            return 'PHP'

        else:
            #
            # No state change.
            #
            return None

    oStyles = {
        'PYTHON': ( PythonHighlightToken,
            (
                ('PUNC', re.compile( r'[-+*!|&^~/%\=<>\[\]{}(),.:]'), puncstyle),
                ('NUMBER', re.compile( r'0x[0-9a-fA-F]+|[+-]?\d+(\.\d+)?([eE][+-]\d+)?|\d+'), numberstyle),
                ('KEYWORD', re.compile( r'(def|class|break|continue|del|exec|finally|pass|' +
                                        r'print|raise|return|try|except|global|assert|lambda|' +
                                        r'yield|for|while|if|elif|else|and|in|is|not|or|import|' +
                                        r'from|True|False)(?![a-zA-Z0-9_])'), keywordstyle),
                ('MAGIC', re.compile( r'self|None'), variablestyle),
                ('MULTILINESTRING', re.compile( r'r?u?(\'\'\'|""")'), stringstyle),
                ('STRING', re.compile( r'r?u?\'(.*?)(?<!\\)\'|"(.*?)(?<!\\)"'), stringstyle),
                ('IDENTIFIER', re.compile( r'[a-zA-Z_][a-zA-Z0-9_]*'), None),
                ('COMMENT', re.compile( r'\#.*'), commentstyle),
                ('NEWLINE', re.compile( r'\r?\n'), 'NewPara'),
                ('WHITESPACE', re.compile( r'[   ]+'), 'Keep'),
            # if all else fails...
                ('UNKNOWN', re.compile( r'.'), None)
            )),

        'PythonMultilineString': ( PythonHighlightToken,
            (
                ('ENDMULTILINESTRING', re.compile( r'.*?("""|\'\'\')', re.DOTALL), stringstyle),
                ('UNKNOWN', re.compile( r'.'), 'Keep')
            )),

        'C': ( CHighlightToken,
            (
                ('COMMENT', re.compile( r'//.*\r?\n'), commentstyle),
                ('MULTILINECOMMENT', re.compile( r'/\*.*?\*/', re.DOTALL), commentstyle),
                ('PREPROCESSOR', re.compile( r'\s*#.*?[^\\]\s*\n', re.DOTALL), preprocstyle),
                ('PUNC', re.compile( r'[-+*!&|^~/%\=<>\[\]{}(),.:]'), puncstyle),
                ('NUMBER', re.compile( r'0x[0-9a-fA-F]+|[+-]?\d+(\.\d+)?([eE][+-]\d+)?|\d+'),
                                        numberstyle),
                ('KEYWORD', re.compile( r'(sizeof|int|long|short|char|void|' +
                                        r'signed|unsigned|float|double|' +
                                        r'goto|break|return|continue|asm|' +
                                        r'case|default|if|else|switch|while|for|do|' +
                                        r'struct|union|enum|typedef|' +
                                        r'static|register|auto|volatile|extern|const)(?![a-zA-Z0-9_])'), keywordstyle),
                ( 'CPPKEYWORD', re.compile( r'(class|private|protected|public|template|new|delete|' +
                                            r'this|friend|using|inline|export|bool|throw|try|catch|' +
                                            r'operator|typeid|virtual)(?![a-zA-Z0-9_])'), keywordstyle),
                ('STRING', re.compile( r'r?u?\'(.*?)(?<!\\)\'|"(.*?)(?<!\\)"'), stringstyle),
                ('IDENTIFIER', re.compile( r'[a-zA-Z_][a-zA-Z0-9_]*'), None),
                ('NEWLINE', re.compile( r'\r?\n'), 'NewPara'),
                ('WHITESPACE', re.compile( r'[   ]+'), 'Keep'),
                ('UNKNOWN', re.compile( r'.'), None)
            )),

        'PHP': ( PHPHighlightToken,
            (
                ('COMMENT', re.compile( r'//.*\r?\n'), commentstyle),
                ('MULTILINECOMMENT', re.compile( r'/\*.*?\*/', re.DOTALL), commentstyle),
                ('MULTILINESTRING', re.compile( r'<<<\s*([a-zA-Z0-9_]+)'), stringstyle),
                ('GOTOPHP', re.compile( r'<\?php'), stringstyle),
                ('PUNC', re.compile( r'[-+*!&|^~/%\=<>\[\]{}(),.:]'), puncstyle),
                ('NUMBER', re.compile( r'0x[0-9a-fA-F]+|[+-]?\d+(\.\d+)?([eE][+-]\d+)?|\d+'),
                                        numberstyle),
                ('KEYWORD', re.compile( r'(declare|else|enddeclare|endswitch|elseif|endif|if|switch|' +
                                        r'as|do|endfor|endforeach|endwhile|for|foreach|while|' +
                                        r'case|default|switch|function|return|break|continue|exit|' +
                                        r'var|const|boolean|bool|integer|int|real|double|float|string|' +
                                        r'array|object|NULL|extends|implements|instanceof|parent|self|' +
                                        r'include|require|include_once|require_once|new|true|false)(?![a-zA-Z0-9_])'), keywordstyle),

                ('STRING', re.compile( r'r?u?\'(.*?)(?<!\\)\'|"(.*?)(?<!\\)"'), stringstyle),
                ('VARIABLE', re.compile( r'\$[a-zA-Z_][a-zA-Z0-9_]*'), variablestyle),
                ('IDENTIFIER', re.compile( r'[a-zA-Z_][a-zA-Z0-9_]*'), None),
                ('WHITESPACE', re.compile( r'[   \r\n]+'), 'Keep'),
                ('GOTOHTML', re.compile( r'\?>'), stringstyle),
                ('UNKNOWN', re.compile( r'.'), None)
            )),

        'PHPMultilineString': ( PHPHighlightToken,
            (
                ('ENDMULTILINESTRING', re.compile( r'.*?\n([a-zA-Z0-9_]+)', re.DOTALL), stringstyle),
                ('UNKNOWN', re.compile( r'.*?(?!\n)'), 'Keep')
            )),

        'HTML': ( HTMLHighlightToken,
            # Mode 0: just look for tags
            (
                ('COMMENT', re.compile( r'<!--[^>]*-->|<!>'), commentstyle),
                ('XMLCRAP', re.compile( r'<![^>]*>'), preprocstyle),
                ('SCRIPT', re.compile( r'<script .*?</script>', re.IGNORECASE + re.DOTALL), tagstyle),
                ('TAG', re.compile( r'</?\s*[a-zA-Z0-9]+'), tagstyle),
                ('GOTOPHP', re.compile( r'<\?php'), stringstyle),
                ('NEWLINE', re.compile( r'\r?\n'), 'NewPara'),
                ('UNKNOWN', re.compile( r'[^<]*'), None)
            )),
            # Mode 1: within tags,
        'HTMLTag': ( HTMLHighlightToken,
            (
                ('ENDTAG', re.compile( r'>'), tagstyle),
                ('ATTRIBUTE', re.compile( r'[a-zA-Z][a-zA-Z0-9:]*='), attrstyle),
                ('VALUE', re.compile( r'"[^"]*"'), stringstyle),
                ('NEWLINE', re.compile( r'\r?\n'), 'NewPara'),
                ('WHITESPACE', re.compile( r'[ \t\f\v]+'), None),
                ('UNKNOWN', re.compile( r'.'), None)
            ))
    }

    def generatedoc(self, strData):
        """
        Syntax highlight some python code.
        Returns html version of code.
        """
        i = 0

        strMode = self.strMode

        #
        # While input is not exhausted...
        #
        while i < len(strData):
            #
            # Compare current position with all possible display types.
            #
            try:
                for strTok, oRE, strStyle in Highlight.oStyles[strMode][1]:
                    if not strTok in self.strSuppressTokens:
                        oMatch = oRE.match(strData, i)
                        if oMatch:
                            strNewMode = Highlight.oStyles[strMode][0](self, strTok, oMatch, strStyle)
                            if strNewMode != None:
                                strMode = strNewMode

                            i += len(oMatch.group())
                            break
                else:
                    #
                    # Token not found so dump out raw text. This doesn't have to be bullet proof.
                    #
                    self.ChangeStyle(None)
                    self.WriteContent(strData[i])
                    i += 1
            except:
                raise
        #
        # Terminate any styles in use.
        #
        self.ChangeStyle(None)

        #
        # Expand tabs to 4 spaces.
        # Doesn't matter if this number is wrong, the indentation will be butt ugly anyhow.
        #
        return self.textdoc

    def WriteSingleline(self, parent, data):
        ls = len(data)
        cnt = 0
        textstart = 0
        i = -1
        for i in xrange(ls):
            if data[i] == ' ':
                if cnt == 0:
                    # We found the first space. Now print the text before
                    parent.addText(data[textstart:i])
                    cnt = 0
                    textstart = i
                cnt = cnt+1
            else:
            # We didn't see a space
            # If there are unprinted spaces, print them now, if there are, then we're at text-start
                if cnt > 0:
                    parent.addText(' ')
                if cnt > 1:
                    parent.addElement(S(c=cnt-1))
                if cnt > 0:
                    cnt = 0
                    textstart = i
        if cnt > 0:
            parent.addText(' ')
        if cnt > 1:
            parent.addElement(S(c=cnt-1))
        elif i != -1:
            parent.addText(data[textstart:i+1])


    def WriteMultiline(self, data):
        lines = data.split('\n')
        self.currPara.addText(lines[0])
        for line in lines[1:]:
            self.currPara = P(stylename=self.programliststyle)
            self.textdoc.text.addElement(self.currPara)
            self.currSpan = Span(stylename=self.strSpanStyle)
            self.WriteSingleline(self.currSpan, line)
            self.currPara.addElement(self.currSpan)

    def WriteContent(self, data):
        """
        Write the content, but convert spaces to <text:s> first
        """
#       re.compile( r'( )\1+(.+)')
        if self.currSpan is None:
            self.WriteSingleline(self.currPara, data)
        else:
            self.WriteSingleline(self.currSpan, data)
        
    def ChangeStyle(self, strStyle):
        """
        Generate output to change from existing style to another style only.
        """
        #
        # Output minimal formatting code: only output anything if the style has
        # actually  changed.
        #
        if self.strSpanStyle != strStyle:
            if strStyle == 'NewPara':
                self.currPara = P(stylename=self.programliststyle)
                self.textdoc.text.addElement(self.currPara)
                self.currSpan = None
                self.strSpanStyle = None
            elif strStyle != 'Keep':
                if strStyle is None:
                    self.currSpan = None
                else:
                    self.currSpan = Span(stylename=strStyle)
                    self.currPara.addElement(self.currSpan)
                self.strSpanStyle = strStyle

def usage():
   sys.stderr.write("Usage: %s [-l language] [-e encoding] inputfile outputfile\n" % sys.argv[0])

try:
    opts, args = getopt.getopt(sys.argv[1:], "l:e:", ["language=", "encoding="])

except getopt.GetoptError:
    usage()
    sys.exit(2)

language = None
encoding = 'utf-8'
for o, a in opts:
    if o in ("-l", "--language"):
        language = a.upper()
    if o in ("-e", "--encoding"):
        encoding = a

if len(args) != 2:
    usage()
    sys.exit(2)

suffixes = {
    '.py': 'PYTHON',
    '.xhtml': 'HTML',
    '.html': 'HTML',
    '.htm': 'HTML',
    '.c': 'C',
    '.c++': 'CPP',
    '.php': 'PHP'
}

inputfile = args[0]
outputfile = args[1]
if language is None:
    try:
        suffix = inputfile.lower().rindex('.')
        language = suffixes[inputfile[suffix:]]
    except:
        usage()
        sys.exit(2)

data = unicode(open(inputfile).read(),encoding)
Highlighted = Highlight(language).generatedoc(data)

Highlighted.save(args[1])


