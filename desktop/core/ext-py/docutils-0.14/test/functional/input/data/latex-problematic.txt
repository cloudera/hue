Problematic Cases for the LaTeX Writer
======================================

These tests contain unusual combinations of syntax elements which may cause
trouble for the LaTeX writer but do not need to be tested with other writers
(e.g. the HTML writer).

The file `latex-problematic.txt` contains the cases with non unsatisfying
results. It is only used to control the visual appearance of the output, not
by any automated test

Sidebars
--------

This paragraph precedes the sidebar.  This is some text.  This is some
text.  This is some text.  This is some text.  This is some text.
This is some text.  This is some text.  This is some text.

.. sidebar:: Sidebar Title

   These are the sidebar contents.  These are the sidebar contents.

   These are the sidebar contents.  These are the sidebar contents.

   These are the sidebar contents.  These are the sidebar contents.
   These are the sidebar contents.  These are the sidebar contents.

This paragraph follows the sidebar.  This is some text.  This is some
text.  This is some text.

This is some text.  This is some text.  This is some text.  This is
some text.  This is some text.  This is some text.  This is some text.


Next Section
------------

This section comes after the sidebar, and this text should float
around the sidebar as well.  This is some text.  This is some text.
This is some text.  This is some text.  This is some text.  This is
some text.  This is some text.  This is some text.  This is some text.
This is some text.  This is some text.  This is some text.  This is
some text.  This is some text.

This is some text.  This is some text.  This is some text.  This is
some text.  This is some text.  This is some text.  This is some text.
This is some text.  This is some text.  This is some text.

Nested Elements
---------------

:Field list: | Line
             | Block
:Field 2: * Bullet
          * list
:Another (longer) field: * Bullet
                         * list
:Yet another long field:
          * .. comment

            Bullet

            .. comment

          * .. comment

            list

            .. comment

:Field: * This

          is

          a

        * bullet

          list

:Field: * | This is
          | a bullet
        * | list with
          | line blocks
:Last field: Last field.

Too deeply nested lists fail. TODO: generate an error or provide a workaround.

.. * * * * * * * * Deeply nested list.

.. 1. 2. 3. 4. 5. 6. 7. 8. Deeply nested list.

+-----------------+
| | Line block    |
|                 |
| * Bullet list   |
|                 |
| ::              |
|                 |
|     Literal     |
|     block       |
+-----------------+
| :Field 1:       |
|  Text.          |
| :Field 2:       |
|  More text.     |
+-----------------+
| +-------+-----+ |
| | A     |* foo| |
| | nested|     | |
| | table.|* bar| |
| +-------+-----+ |
+-----------------+
| This is a       |
| paragraph.      |
|                 |
| +-------+-----+ |
| | A     |* foo| |
| | nested|     | |
| | table.|* bar| |
| +-------+-----+ |
|                 |
| Another longer  |
| paragraph.      |
+-----------------+
| * A list.       |
| * A list.       |
|                 |
| +-------+-----+ |
| | A     |* foo| |
| | nested|     | |
| | table.|* bar| |
| +-------+-----+ |
|                 |
| * Another list. |
| * Another list. |
+-----------------+
| Foo             |
|                 |
| Bar             |
+-----------------+
| * Foo           |
|                 |
| * Bar           |
+-----------------+
| * This is a     |
|   paragraph.    |
|                 |
|   This is a     |
|   paragraph.    |
|                 |
| * This is a     |
|   paragraph.    |
|                 |
|   This is a     |
|   paragraph.    |
+-----------------+

Vertical alignment of inline images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. |top| image:: ../../../../docs/user/rst/images/biohazard.png
   :align: top
   :width: 3em

.. |middle| image:: ../../../../docs/user/rst/images/biohazard.png
   :align: middle
   :width: 2em

.. |bottom| image:: ../../../../docs/user/rst/images/biohazard.png
   :align: bottom
   :width: 2.5em

A paragraph with top |top|, middle |middle|, and bottom |bottom|
aligned images.

A paragraph with top |top| aligned image.

A paragraph with middle |middle| aligned image.

A paragraph with bottom |bottom| aligned image.


