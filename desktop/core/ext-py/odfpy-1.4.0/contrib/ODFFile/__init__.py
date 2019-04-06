# -*- coding: utf-8 -*-
# Copyright (C) 2007-2008 Søren Roug, European Environment Agency
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


#Zope imports
from ODFFile import ODFFile, manage_addODFFileForm, manage_addODFFile
from AccessControl.Permissions import add_documents_images_and_files
#from App.ImageFile import ImageFile


def initialize(context):
    """ initialize the ODFFile component """

    #register classes
    context.registerClass(
        ODFFile,
        permission=add_documents_images_and_files,
        constructors = (manage_addODFFileForm, manage_addODFFile),
        icon = 'images/openofficeorg-oasis-text.gif'
        )

    context.registerHelp()
    context.registerHelpTitle('ODFFile')

#misc_ = {
#  'text':ImageFile('images/openofficeorg-oasis-text.gif', globals()),
#  'presentation':ImageFile('images/openofficeorg-oasis-presentation.gif', globals()),
#  'spreadsheet':ImageFile('images/openofficeorg-oasis-spreadsheet.gif', globals())
#    }
