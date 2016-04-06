from setuptools import setup

setup(
    name="example",
    version="0.1",
    py_modules=["bsdopendirtype"],
    setup_requires=["cffi>=1.0.dev0"],
    cffi_modules=[
        "bsdopendirtype_build.py:ffi",
    ],
    install_requires=["cffi>=1.0.dev0"],   # should maybe be "cffi-backend" only?
    zip_safe=False,
)
