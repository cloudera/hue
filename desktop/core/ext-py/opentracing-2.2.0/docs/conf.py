import sphinx_rtd_theme


project = 'opentracing-python'
copyright = 'The OpenTracing Authors'
author = 'The OpenTracing Authors'
version = '1.2.3.dev0'
release = '1.2'

needs_sphinx = '1.0'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']
templates_path = []
source_suffix = '.rst'
source_encoding = 'utf-8'
master_doc = 'index'

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = []
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    'python': ('https://docs.python.org/', None),
}

