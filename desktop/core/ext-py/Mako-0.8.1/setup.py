from setuptools import setup, find_packages
import os
import re
import sys

v = open(os.path.join(os.path.dirname(__file__), 'mako', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

markupsafe_installs = (
            sys.version_info >= (2, 6) and sys.version_info < (3, 0)
        ) or sys.version_info >= (3, 3)

if markupsafe_installs:
    install_requires = ['MarkupSafe>=0.9.2']
else:
    install_requires = []

setup(name='Mako',
      version=VERSION,
      description="A super-fast templating language that borrows the \
 best ideas from the existing templating languages.",
      long_description=readme,
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      "Programming Language :: Python :: Implementation :: CPython",
      "Programming Language :: Python :: Implementation :: PyPy",
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='templates',
      author='Mike Bayer',
      author_email='mike@zzzcomputing.com',
      url='http://www.makotemplates.org/',
      license='MIT',
      packages=find_packages('.', exclude=['examples*', 'test*']),
      scripts=['scripts/mako-render'],
      tests_require=['nose >= 0.11'],
      test_suite="nose.collector",
      zip_safe=False,
      install_requires=install_requires,
      extras_require={'beaker': ['Beaker>=1.1']},
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
      """
)
