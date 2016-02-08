from distutils.core import setup
import readdir2_build

setup(
    name="readdir2",
    version="0.1",
    py_modules=["readdir2"],
    ext_modules=[readdir2_build.ffi.distutils_extension('build')],
)
