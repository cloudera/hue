Test input for test_dependencies.

Docutils can write a list of files required to generate the output like
included files or embedded stylesheets. This is particularly useful in
conjunction with programs like ``make``.

Included files are recorded:

.. include:: include.txt

.. raw:: HTML
   :file: raw.txt

Dependencies are recorded only once:

.. include:: include.txt

Image files are only recorded, if actually accessed
(to extract the size or if embedded in the output document):

.. image:: test.jpg

.. figure:: ../docs/user/rst/images/title.png
   :figwidth: image

Scaled images without given size are recorded by the html writer:

.. image:: ../docs/user/rst/images/biohazard.png
   :scale: 50 %

TODO: Paths in included files should be rewritten relative to the base
      document.

      * when loading images,
      * when recording dependencies.

.. include: subdir/dependencies-included.txt
