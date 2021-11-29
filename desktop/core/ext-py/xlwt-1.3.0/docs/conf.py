import datetime
import os, pkginfo

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
pkg_info = pkginfo.Develop(os.path.join(os.path.dirname(__file__), os.pardir))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']
source_suffix = '.rst'
master_doc = 'index'
project = u'xlwt'
copyright = '2002-%s xlwt contributors' % datetime.datetime.now().year
version = release = pkg_info.version
exclude_patterns = ['_build']
pygments_style = 'sphinx'

if on_rtd:
    html_theme = 'default'
else:
    html_theme = 'classic'

htmlhelp_basename = project+'doc'
intersphinx_mapping = {'python': ('https://docs.python.org', None)}
