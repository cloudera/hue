More Tables
-----------

A table with multi-paragraph multicolumn cells:

+----------+--------------+---------------------------------+-----------+
| test     | **bold hd**  | multicolumn 1                   | *emph hd* |
|          |              |                                 |           |
|          |              | With a second paragraph         |           |
+----------+--------------+--------------+--------+---------+-----------+
| multicolumn 2           | cell         | cell   | cell    | cell      |
|                         |              |        |         |           |
| With a second paragraph |              |        |         |           |
+----------+--------------+--------------+--------+---------+-----------+
| cell     | multicolumn 3 (one line,    | cell   | cell    | cell      |
|          | but very very very very     |        |         |           |
|          | very looooong)              |        |         |           |
+----------+--------------+--------------+--------+---------+-----------+
| cell     | cell         | cell         | Short multicolumn 4          |
+----------+--------------+--------------+------------------------------+

Tables with multi-paragraph multirow cells currently fail due to a LaTeX
limitation (see https://sourceforge.net/p/docutils/bugs/225/).

A table with multirow header and column-widths set by LaTeX:

.. table::
   :widths: auto

   +------------+-------------------+
   | XXX        | Variable Summary  |
   |            +-------------------+
   |            | Description       |
   +============+===================+
   | multicollumn cell              |
   +--------------------------------+

In a table with column-widths set by LaTeX, each cell has just one line.
Paragraphs are merged (a warning is given).

.. table::
   :widths: auto

   +------------+-------------------+
   | 11         | first paragraph   |
   |            |                   |
   |            | second paragraph  |
   |            |                   |
   |            | third paragraph   |
   +------------+-------------------+
   | 21         | 22                |
   +------------+-------------------+
