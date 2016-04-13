import os

from distutils.command.install import INSTALL_SCHEMES

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib'] 

from distutils.core import setup, Extension

setsc = Extension("guppy.sets.setsc",
                  [
                      "src/sets/sets.c",
                      "src/sets/bitset.c",
                      "src/sets/nodeset.c"
                      ]
                  )

heapyc = Extension("guppy.heapy.heapyc",
                   [
        	       'src/heapy/heapyc.c',
                       'src/heapy/stdtypes.c'
                       ]
                   )

def doit():
    setup(name="guppy",
          version="0.1.10",
          description="Guppy-PE -- A Python Programming Environment",
          long_description="""
Guppy-PE is a library and programming environment for Python,
currently providing in particular the Heapy subsystem, which supports
object and heap memory sizing, profiling and debugging. It also
includes a prototypical specification language, the Guppy
Specification Language (GSL), which can be used to formally specify
aspects of Python programs and generate tests and documentation from a
common source.

The guppy top-level package contains the following subpackages:

doc
       Documentation files. These are in a package so they get installed
       at a well-defined place, especially to support interactive help.

etc
       Support modules. Contains especially the Glue protocol module.

gsl
       The Guppy Specification Language implementation. This can
       be used to create documents and tests from a common source.

heapy
       The heap analysis toolset. It can be used to find information
       about the objects in the heap and display the information
       in various ways.

sets 
       Bitsets and 'nodesets' implemented in C.
""",
          author="Sverker Nilsson",
          author_email="sn@sncs.se",
          url="http://guppy-pe.sourceforge.net",
          license='MIT',
          packages=[
            "guppy",
            "guppy.doc",
            "guppy.etc",
            "guppy.gsl",
            "guppy.heapy",
            "guppy.heapy.test",
            "guppy.sets",
            ],
          package_data={"guppy.doc" : ["*.html","*.jpg"]},
          ext_modules=[setsc, heapyc]
          )

doit()

