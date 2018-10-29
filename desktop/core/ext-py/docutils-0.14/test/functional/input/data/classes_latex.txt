class handling
--------------

This section tests class handling for block level elements by the LaTeX
writer. See the input file ``classes_latex.txt`` for the raw LaTeX code used
to style the examples.

An "epigraph" directive is exported as "quote" wrapped in a "DUclass"
environment. Here, it is styled by a "DUCLASSepigraph" environment
redefining the "quote" environment as "minipage":

.. raw:: latex

   \newcommand*{\DUCLASSepigraph}{%
     \renewenvironment{quote}{\vspace{1em}
                              \footnotesize\hfill{}%
                              \begin{minipage}{0.4\columnwidth}}%
                             {\end{minipage}\vskip\baselineskip}}

.. epigraph::

   Do not play this piece fast. It is never right to play *Ragtime* fast.

   -- Scott Joplin

Raw latex is also used to style the following lists: "DUCLASSenumerateitems"
redefines "itemize" as "enumerate", "DUCLASSrules" draws horizontal lines
above and below. 

.. raw:: latex

   \newcommand*{\DUCLASSenumerateitems}{%
     \renewenvironment{itemize}{\begin{enumerate}}%
                               {\end{enumerate}}%
   }

   \newenvironment{DUCLASSrules}%
                  {\noindent\rule[0.5ex]{1\columnwidth}{1pt}}%
                  {\noindent\rule[0.5ex]{1\columnwidth}{1pt}}

An "enumerated" bullet list:

.. class::  enumerateItems

* item
* next item
* third item

A list with lines above and below:

.. class:: rules

* item
* next item
    
A normal bullet list is kept unchanged by the above redefinitions:

* item
* next item
* third item

A container wraps several elements in a common "class wrapper". Here, we use
it to set 2 paragraphs and a list in small caps:

.. raw:: latex

   \newcommand*{\DUCLASSscshape}{\scshape}

.. container:: scshape

   paragraph 1

   paragraph 2

   * bullet list
   * still bullet list


A right-aligned line-block. Alignment handling is built into the latex
writer for image, table, and line block elements.

.. class:: align-right

| Max Mustermann
| Waldstr. 22
| D 01234 Testdorf
| Tel.: 0123/456789
