import sys, os


from setup import include_dirs, sources, libraries, define_macros
from setup import library_dirs, extra_compile_args, extra_link_args


if __name__ == '__main__':
    from distutils.core import setup
    from distutils.extension import Extension
    standard = '__pypy__' not in sys.builtin_module_names
    setup(packages=['cffi'],
          requires=['pycparser'],
          ext_modules=[Extension(name = '_cffi_backend',
                                 include_dirs=include_dirs,
                                 sources=sources,
                                 libraries=libraries,
                                 define_macros=define_macros,
                                 library_dirs=library_dirs,
                                 extra_compile_args=extra_compile_args,
                                 extra_link_args=extra_link_args,
                                 )] * standard)
