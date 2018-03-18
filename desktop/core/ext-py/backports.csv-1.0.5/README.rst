================================================
backports.csv: Backport of Python 3's csv module
================================================

.. image:: https://img.shields.io/pypi/v/backports.csv.svg
   :target: https://pypi.python.org/pypi/backports.csv
   :alt: Latest Version

.. image:: https://travis-ci.org/ryanhiebert/backports.csv.svg?branch=master
   :target: https://travis-ci.org/ryanhiebert/backports.csv

.. image:: https://badges.gitter.im/ryanhiebert/backports.csv.svg
   :alt: Join the chat at https://gitter.im/ryanhiebert/backports.csv
   :target: https://gitter.im/ryanhiebert/backports.csv?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://requires.io/github/ryanhiebert/backports.csv/requirements.svg?branch=master
   :target: https://requires.io/github/ryanhiebert/backports.csv/requirements/?branch=master
   :alt: Requirements Status

The API of the csv module in Python 2 is drastically different from
the csv module in Python 3. This is due, for the most part, to the
difference between str in Python 2 and Python 3.

The semantics of Python 3's version are more useful because they support
unicode natively, while Python 2's csv does not.

Installation
============

.. code-block:: sh

    pip install backports.csv

Usage
=====

First make sure you're starting your file off right:

.. code-block:: python

    from backports import csv


Then be careful with your files to handle the encoding.
If you're working with a binary file-like object,
``io.TextIOWrapper`` can be very helpful.
If you're dealing with a file, you can just use ``io.open``
instead of Python 2's ``open`` builtin, and it works
just like Python 3's builtin ``open``.

.. code-block:: python

    from backports import csv
    import io

    def read_csv(filename):
        with io.open(filename, newline='', encoding='utf-8') as f:
            for row in csv.reader(f):
                yield row

    def write_csv(filename, rows):
        with io.open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

Note: It should always be safe to specify ``newline=''``,
since the csv module does its own (universal) newline handling.
