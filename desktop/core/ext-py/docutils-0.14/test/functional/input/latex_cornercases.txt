Some Tests for the LaTeX Writer
===============================

These tests contain unusual combinations of syntax elements which may cause
trouble for the LaTeX writer but do not need to be tested with other writers.

Block Quotes
------------

    This block quote comes directly after the section heading and is
    followed by a paragraph.

    This is the second paragraph of the block quote and it contains
    some more text filling up some space which would otherwise be
    empty.

    -- Attribution

This is a paragraph.

    This block quote does not have an attribution.

This is another paragraph.

    Another block quote at the end of the section.


More Block Quotes
-----------------

    Block quote followed by a transition.

----------

    Another block quote.


Images
------

Image with 20% width:

.. image:: ../../../docs/user/rst/images/title.png
   :width: 20%

Image with 100% width:

.. image:: ../../../docs/user/rst/images/title.png
   :width: 100%


Rowspanning tables
------------------

Several rowspanning cells in a table.

Problem:

In LaTeX, "overwritten" cells need to be defined as empty cells.

Docutils (similarily to HTML) uses is the "Exchange Table Model" (also known
as CALS tables, see docs/ref/soextblx.dtd) which defines only the remaining
cells in a row "affected" by multirow cells.

Therefore, visit_entry() is only called for the remaining cells and the
LaTeX writer needs bookkeeping to write out the required number of extra
'&'s.

+-----+----------+----------+------+
| 11  |       12 |       13 |  14  |
+-----+----------+----------+------+
| 21  | 2/3 2    |          |  24  |
+-----+          |          +------+
| 31  |          | 2…4 3    |  34  |
+-----+----------+          +------+
| 41  |       42 |          |  14  |
+-----+----------+----------+------+

+-------+-------+----+
| 11    |    12 | 13 |
+-------+-------+----+
| 2/3 1 |       | 23 |
|       |       +----+
|       | 2/3 2 | 33 |
+-------+-------+----+

+-------+----+
| 11    | 12 |
+-------+----+
| 2/3 1 | 22 |
|       +----+
|       | 32 |
+-------+----+

+----+--------+----+
| 11 |    12  | 13 |
+----+--------+----+
| 21 | 2/3 2  | 23 |
+----+        +----+
| 31 |        | 33 |
+----+--------+----+

+----+--------+
| 11 | 12     |
+----+--------+
| 21 | 2/3 1  |
+----+        |
| 31 |        |
+----+--------+


+----+--------+
| 11 | 1/2 1  |
+----+        |
| 21 |        |
+----+--------+
| 31 | 32     |
+----+--------+

+----+------------+--------+
| 11 | 1/2 2      |        |
+----+            | 1/2 3  |
| 21 |            |        |
+----+------------+--------+

+-------+----+--------+
|       | 12 | 1/2 3  |
| 1/2 3 +----+        |
|       | 22 |        |
+-------+----+--------+

+-------+----+
|       | 12 |
| 1/2 3 +----+
|       | 22 |
+-------+----+
| 31    | 32 |
+-------+----+
