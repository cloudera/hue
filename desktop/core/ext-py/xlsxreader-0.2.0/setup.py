import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xlsxreader",
    version="0.2.0",
    author="Michael Brine",
    author_email="mbrine0@gmail.com",
    description="reads .xlsx files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.infra.cloudera.com/michaelbrine/xlsx_to_delim",
    project_urls={
        "Bug Tracker": "https://github.infra.cloudera.com/michaelbrine/xlsx_to_delim",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=2.7",
)
