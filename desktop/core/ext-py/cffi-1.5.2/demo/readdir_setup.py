from setuptools import setup

setup(
    name="example",
    version="0.1",
    py_modules=["readdir"],
    setup_requires=["cffi>=1.0.dev0"],
    cffi_modules=["readdir_build.py:ffi"],
    install_requires=["cffi>=1.0.dev0"],
    zip_safe=False,
)
