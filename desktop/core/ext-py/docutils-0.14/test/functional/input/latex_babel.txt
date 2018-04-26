The babel_ package introduces the concept of "shorthands": additional
characters that introduce a latex macro. Most common is the active double
quote ("). Problematic is the tilde character (~) which is regularely used
for no-break spaces but redefined by some language definition files:

English: 'an' "active"-quote, ^circumflex, and no-break spaces

.. class:: language-eu

Basque: 'an' "active"-quote, ^circumflex, and no-break spaces

.. class:: language-eo

Esperanto: 'an' "active"-quote, ^circumflex, and no-break spaces

.. class:: language-et

Estonian: 'an' "active"-quote, ^circumflex, and no-break spaces

.. class:: language-gl

Galician: 'an' "active"-quote, ^circumflex, and no-break spaces

.. class:: language-de

German: 'an' "active"-quote, ^circumflex, and no-break spaces

Spanish: option clash with Galician!

..
   .. class:: language-es

   Spanish: 'an' "active"-quote, ^circumflex, and no-break spaces


.. _babel: http://www.ctan.org/packages/babel
