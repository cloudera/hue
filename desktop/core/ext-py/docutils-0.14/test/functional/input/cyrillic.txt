Заголовок
---------

первый пример: "Здравствуй, мир!"

Title
-----

.. class:: language-en

first example: "Hello world".

Notes
-----

.. class:: language-en

This example tests rendering of Latin and Cyrillic characters by the LaTeX
and XeTeX writers. Check the compiled PDF for garbage characters in text and
bookmarks.

.. class:: language-en

To work around a problem with Cyrillic in PDF-bookmarks in `hyperref`
versions older than v6.79g 2009/11/20, the test caller ``latex_cyrillic.py``
sets ``hyperref_options`` to ``'unicode=true'`` while ``xetex_cyrillic.py``
sets it to ``'unicode=false'``. The recommended option for current
(2011-08-24) hyperref versions is ``'pdfencoding=auto'``.




