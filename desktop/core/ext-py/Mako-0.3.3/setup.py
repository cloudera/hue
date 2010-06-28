from setuptools import setup, find_packages
import os
import re
import sys

extra = {}
if sys.version_info >= (3, 0):
    extra.update(
        use_2to3=True,
    )

v = open(os.path.join(os.path.dirname(__file__), 'mako', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

setup(name='Mako',
      version=VERSION,
      description="A super-fast templating language that borrows the \
 best ideas from the existing templating languages.",
      long_description="""\
Mako is a template library written in Python. It provides a familiar, non-XML 
syntax which compiles into Python modules for maximum performance. Mako's 
syntax and API borrows from the best ideas of many others, including Django
templates, Cheetah, Myghty, and Genshi. Conceptually, Mako is an embedded 
Python (i.e. Python Server Page) language, which refines the familiar ideas
of componentized layout and inheritance to produce one of the most 
straightforward and flexible models available, while also maintaining close 
ties to Python calling and scoping semantics.

""",
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='wsgi myghty mako',
      author='Mike Bayer',
      author_email='mike@zzzcomputing.com',
      url='http://www.makotemplates.org/',
      license='MIT',
      packages=find_packages('.', exclude=['examples*', 'test*']),
      scripts=['scripts/mako-render'],
      tests_require = ['nose >= 0.11'],
      test_suite = "nose.collector",
      zip_safe=False,
      install_requires=[
          'Beaker>=1.1',
      ],
      entry_points="""
      [python.templating.engines]
      mako = mako.ext.turbogears:TGPlugin
      
      [pygments.lexers]
      mako = mako.ext.pygmentplugin:MakoLexer
      html+mako = mako.ext.pygmentplugin:MakoHtmlLexer
      xml+mako = mako.ext.pygmentplugin:MakoXmlLexer
      js+mako = mako.ext.pygmentplugin:MakoJavascriptLexer
      css+mako = mako.ext.pygmentplugin:MakoCssLexer

      [babel.extractors]
      mako = mako.ext.babelplugin:extract
      """,
)
