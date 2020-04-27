from setuptools import setup
import textwrap

setup(name='MarkupPy',
      version='1.14',
      description='An HTML/XML generator',
      url='https://github.com/tylerbakke/MarkupPy',
      author='Daniel Nogradi',
      author_email="nogradi@gmail.com",
      long_description=textwrap.dedent("""\
        This is MarkupPy - a Python module that attempts to make it easier to generate HTML/XML from a Python program in an intuitive, lightweight, customizable and pythonic way. It works with both python 2 and 3.
    
        The code is in the public domain.

        Version: 1.14 as of August 1, 2017.

        Please send bug reports, feature requests, enhancement ideas or questions to tylerbakke@gmail.com.
 
        Installation: Run 'pip install MarkupPy" from the terminal.
    
        Documentation and further info is at https://tylerbakke.github.io/MarkupPy/
        
        (Migrated from markup.py)
        """),
      license="MIT",
      packages=['MarkupPy'],
      classifiers=[
          'Environment :: Console',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3'
      ],
      zip_safe=False)
