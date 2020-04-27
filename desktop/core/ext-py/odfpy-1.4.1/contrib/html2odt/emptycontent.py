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

chead = ['''<?xml version="1.0" encoding="UTF-8"?>\n''',
'''<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" office:version="1.0">''',
'''<office:scripts/>''',
'''<office:font-face-decls>''',
'''<style:font-face style:name="Luxi Sans1" svg:font-family="&apos;Luxi Sans&apos;" style:font-pitch="variable"/>''',
'''<style:font-face style:name="Nimbus Roman No9 L" svg:font-family="&apos;Nimbus Roman No9 L&apos;" style:font-family-generic="roman" style:font-pitch="variable"/>''',
'''<style:font-face style:name="Luxi Sans" svg:font-family="&apos;Luxi Sans&apos;" style:font-family-generic="swiss" style:font-pitch="variable"/>''',
'''</office:font-face-decls>''',
'''<office:automatic-styles/>''',
'''<office:body>''',
'''<office:text>''',
'''<office:forms form:automatic-focus="false" form:apply-design-mode="false"/>''',
'''<text:sequence-decls>''',
'''<text:sequence-decl text:display-outline-level="0" text:name="Illustration"/>''',
'''<text:sequence-decl text:display-outline-level="0" text:name="Table"/>''',
'''<text:sequence-decl text:display-outline-level="0" text:name="Text"/>''',
'''<text:sequence-decl text:display-outline-level="0" text:name="Drawing"/>''',
'''</text:sequence-decls>''']

cmiddle = [
'''<text:p text:style-name="Standard"/>''',]

cfoot = [ '''</office:text>''',
'''</office:body>''',
'''</office:document-content>''']

def content():
    return ''.join(chead + cmiddle + cfoot)

