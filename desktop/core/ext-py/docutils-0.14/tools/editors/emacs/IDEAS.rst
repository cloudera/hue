The following is a list of ideas of functionality which would be nice
to have in `rst.el`. In the examples a ``@`` stands for the cursor.

Convert to id
=============

* Convert the region to an HTML id

  * For instance "Eine Überschrift" to "eine-berschrift"

  * According the same rules as reST does this

Jump to internal target
=======================

* A command to jump to the internal target the point is on

* A target may be

  * A section title

  * Footnotes / citations

  * Inline internal targets

  * Hyperlink target definition

  * Substitution definition

* See hunk #26 in `rst_el-emacs_V23_1_patch1_1_2` vs. `emacs_V23_1`
  for some ideas

Completion for directive options
================================

* Imagine ::

    .. list-table::
       :@

  with the cursor at the asterisk

* There should be a command which offers all the possible options for
  this particular directive as completion

* May be `skeleton.el` can also be useful

Completion for directives
=========================

* Imagine ::

    .. @

* There should be a command which offers all directives as completion

* May be this should work for other keywords as well

* May be this could work even at the beginning of the line

* Completion must be bound to M-TAB

  * Already existing binding must be chained

  * May be `expand.el` can help (look in package finder)?

  * May be `hippie` is good here

  * Check `(info)autotype`

Completion for user-defined elements
====================================

* Imagine ::

    |@

  or ::

    [@

  or ::

    _@

* There should be a command which offers all defined substitutions /
  footnotes / links as completion

Insertion of link alias
=======================

* Imagine ::

    Aspect of something
    ===================

    This is about the `aspect of something`_@

* There should be a command which asks you for an alias for the link,
  add the alias and change the link ::

    .. _aspects of something:

    Aspect of something
    ===================

    This is about the `aspects of something`_@

Smart use of `iimage-mode`
==========================

* There is `iimage-mode` which shows ``.. image::``\s in Emacs

* May be we can add a binding to toggle it

TOC in speedbar
===============

* If the TOC is displayed in the speedbar this could be used for
  permanent navigation

  * Probably `imenu` functionality can be used for this

    * See `imenu` documentation and `speedbar-use-imenu-flag`

  * See `speedbar`

toc-mode without markup
=======================

* The markup which may be contained in a section title is not useful
  in toc-mode and should be suppressed

Sophisticated navigation in sections
====================================

* Navigation in sections similar to navigation in other structured data

  * Like XML, Lisp

  * C-M-u für Up

  * C-M-d für Down

  * C-M-f / C-M-b für Forward / Backward

Display of current location
===========================

* Display the "section path" to the current point

* Like in XML: In which element is the point?

toc-mode only to a certain level
================================

* If a TOC buffer is created a prefix argument should limit the depth
  of the listing to the given level

Imenu support or similar
========================

* Imenu could be supported

  * See `(elisp)Imenu`

* `etags` could be supported

  * See `(emacs)Tags` and `etags.el`

  * May be this can be used for generating HTML local tags somehow?

    * As requested by `Convert to id`_

    * Could use `complete-tag`

Outline support
===============

* Support for `outline-mode` / `allout-mode` would be nice

  * Should consider section titles

    * May be item lists can also be included

  * Using `allout-mode` is difficult

    * It's not customizable enough for the complex syntax of
      reStructuredText

    * However, some commands make sense

      * Motion commands

      * Exposure commands

      * Some alteration commands

    * Should be reimplemented

      * Key bindings need to be reused

	* However, care must be taken if a file uses `allout-mode` for
	  instance by comment strings

	* In this case key bindings must not be overridden

  * A command adding / updating `allout-mode` tags could be a solution

Sophisticated filling
=====================

* These things must be filled special:

  * Definitions

  * Filling of ::

      * VeryLongWordSuchAsAnURLVeryLongWordSuchAsAnURLVeryLongWordSuchAsAnURLVeryLongWordSuchAsAnURLVeryLongWordSuchAsAnURL

    should work as expected by *not* breaking the line

  * May be `fill-nobreak-predicate` can help here

* These things may not be filled at all

  * Literal blocks

  * Tables

  * Link definitions

  * May be `fill-nobreak-predicate` can help here, too

* May be defining an own `auto-fill-function` may be useful

  * Might prevent auto-filling of literal text

* Filling of a re-indented item doesn't work as expected::

    * Something just indented once more by the user
    though continuation line is not indented already

  * Alternatively indentation could indent the whole item

    * See `Sophisticated indentation`_

* See also `Filling of section headers`_

Sophisticated indentation
=========================

* It should be generally possible to shift one more to the right

  * This makes indentation for quotes possible

  * But not for literal blocks

* For item lists the best tab should be on the same level as the last
  item::

    * bla

    @

  * The second best tab should be where text starts::

      * bla

	@

* <backtab> should be used to indent in the other direction

  * Or may be C-u <tab> but this has a different meaning

* <tab> could obsolete C-c C-r <tab>

  * For this the indentation needs to be determined at the start
    instead of per line

    * <tab> over list works::

	Text

	  * GGGGGG
	  * SSSSSSSSSSSSSSS
	  * TTTTTTTT
	  * ZZZZZZZZ

    * <tab> over list doesn't work::

	Text

	* GGGGGG
	* SSSSSSSSSSSSSSS
	* TTTTTTTT
	* ZZZZZZZZ

* An indenting tab on the head of a list item should indent the whole
  list item instead of only the first line

  * Alternatively `fill-paragraph` could do so

    * See `Sophisticated filling`_

* May be `refill-mode` can be useful

List to sections
================

* A command would be nice which

  * transforms the first level of a nested list in a region into a
    header

  * removes one level of indentation from the rest of the list

Change section level by more than one step
==========================================

* It would be nice if <C-h> `rst-adjust` could rotate a section
  adornment more than one level

* A modification of the semantic of the prefix arguments could do this

  * Non-zero numeric prefix arg n rotates n step in the given direction

  * Prefix arg 0 toggles overline / underline

    * This would be different from current setup

Compiling for syntax check
==========================

* Compiling with results going to `/dev/null` would be useful

  * This would just do a syntax check with no files lying around

* Toolset choice for <C-c C-c C-c> `rst-compile` must be by
  customizable if at all necessary

  * Customization group must be used

Renumber an exisiting enumeration
=================================

* Renumbering an exisiting enumeration is not possible yet

Command to move across blocks
=============================

* A command moving forward / backward across the content blocks of the
  current block would be nice

  * For instance: Move across all blocks contained in an item or field

  * This would move to the start of the sibling of the current block

  * Would allow to jump to the next item on the same level in a list

* <C-M-f> `forward-sexp` could be a nice binding

rst-toc-insert features
=======================

* The `contents::` options could be parsed to figure out how deep to
  render the inserted TOC

* On load, detect any existing TOCs and set the properties for links

* TOC insertion should have an option to add empty lines

* TOC insertion should deal with multiple lines

* Automatically detect if we have a `section-numbering::` in the
  corresponding section, to render the toc.

Automatic handling of `.txt` files
==================================

It would be nice to differentiate between text files using
reStructuredText and other general text files. If we had a function to
automatically guess whether a `.txt` file is following the
reStructuredText conventions, we could trigger `rst-mode` without
having to hard-code this in every text file, nor forcing the user to
add a local mode variable at the top of the file. We could perform
this guessing by searching for a valid adornment at the top of the
document or searching for reStructuredText directives further on.

Entry level for rst-straighten-adornments
=========================================

* `rst-straighten-adornments` should have an entry level to start at a
  lower than the top level

  * I for one prefer a verbose style for top level titles which is not
    appropriate for documents without titles

  * Should be done by a prefix argument

Support for ispell
==================

* `ispell` may skip certain things

  * Using `ispell-skip-region-alist`

    * ``Code`` should be skipped

    * Literal text after ``::`` should be skipped

  * A customization should switch this on so users are not surprised

Marriage with `forms-mode`
==========================

* Like I married `forms-mode` with `sdf-mode`

* Would allow editing a number of records with a fixed layout

* The base reStructuredText file should be either

  * a list consisting of field lists

    * The separator needs to be defined, however

    * A section header or transition may be a useful separator

  * a `list-table`

  * a CSV file

    * That would call for a general support for CSV support for forms

    * May be `orgtbl-to-csv` in `org/org-table.el` could be useful for
      this

Marriage with `org-mode`
========================

* May be Org mode can be utilized instead of `forms-mode`

  * See `orgtbl-mode` 

  * See `orgstruct-mode`

    * Though this looks more like `allout-mode`

Intelligent quote insertion
===========================

* Use or develop something like `insert-pair`

  * Main use for forgotten quoting

    * Thus may rather quote preceding word than following one

  * If `forward-sexp` could be overridden `insert-pair` might me
    usable directly

* Also add something like `delete-pair`

Sophisticated alignment
=======================

* May be aligning can be used to get results like this

  :Some:             Field

  :Longer name:      Aligned

  :Even longer name: More aligned

  * See `align.el`

toc-mode per buffer
===================

* At the moment there can only be globally one TOC

  * A TOC could be separate for each buffer

toc-mode could generate reST
============================

* The format of the generated TOC could be reStructuredText

  * For instance as a bullet list

  * So it could be copied and basted into a reStructuredText document

  * Conversion could be done in toc-mode buffer

* An alternative could be that `rst-bullet-list-region` handles
  indented text properly

Improvements for comments
=========================

* `comment-use-syntax` should be set to nil locally

* `comment-forward` should work so `comment-dwim` recognizes a
  commented region

  * Then it could uncomment it automatically and use of prefix
    argument is no longer neccessary

Context sensitive M-q
=====================

* M-q / `fill-paragraph` should check whether point is in section
  header and call `rst-adjust` in this case

  * This would unify handling of changes in section headers and normal
    paragraphs

Switch to using `cl-lib`
========================

* Options to use `cl-lib`

    There are various options, and you'll have to judge for yourself which
    is best for your particular case:
    - live with the warnings.
    - switch to cl-lib and ask users of older Emacsen to install cl-lib
      (available in GNU ELPA).
    - add things like (unless (fboundp 'cl-letf) (defalias 'cl-letf 'letf)).
    - change the code to use something else (e.g. for flet, you can switch
      to using either defadvice or (let ((f1 (lambda ..))) ...).
    - ...

    -- Stefan Monnier

* Remove own implementations then

Filling of section headers
==========================

* Filling should recognize section headers and adjust the adornment

  * Then a fill operation for a region wouldn't break the section
    header adornment

  * In addition a fill operation could be used instead of adjusting a
    section header

Cursor after adjusting adornment
================================

* Adjusting a section header should move the cursor to the end of the
  adornment

  * Then a following C-j / Return opens a new line instead of breaking
    the adornment just created

Copying literal blocks
======================

* Copying literal blocks should eat up the block indentation

  * This way code fragments can be copied without removing the block
    indentation by hand

Structural operations for toc-mode
==================================

* Structrual operations for toc-mode

  * Raise or lower sections

  * Move sections around

Inhibit auto-fill in literal blocks
===================================

* In a literal block a space should not do auto-fill

  * May be variable `normal-auto-fill-function` can be set mode
    specific

    * Is normally `do-auto-fill`

toc-mode should leave mark
==========================

* When you jump to a different point in the document by using toc-mode
  the mark should be set at the point of departure

  * This aligns with the semantic of other far jumps in the document
    such as `beginning-of-buffer`

Remembering last location per section
=====================================

* Remembering the last location per section would make it possible to
  jump back to this location

  * This is useful if several sections are worked on in parallel

* The jump into the section could happen from toc-mode

  * Instead of to the section header

  * May be by a special key

* Other section based jump commands could do similar

  * For instance navigating by sections

* This calls for a general modifier for jumps

Multiple steps for `rst-adjust`
===============================

* Sometimes it's useful to adjust more than one step in the given
  direction

  * For instance to follow a 2= title by 1= normal header skipping the
    usual 2- level

* Therefore using a counter may be useful

Enhance compilation support
===========================

* Compilation to ODT should be supported

* Arbitrary compilations should be supported using customization

  * Key must be configurable

  * Command must be configurable

* May be the whole toolset stuff needs to be replaced?

Support for longlines mode
==========================

* `longlines-mode` should use correct indentation for broken lines

  * This is actually an enhancement of `longlines-mode`

  * `longlines-mode` modifies the buffer

    * This is needed to use all the standard functionality like
      `move-to-column`

    * Using property `display` for inserting indentation does not work
      properly because of this

  * Indentation must be inserted in the buffer

    * However, it needs to have the property `intangible` so it can
      not be modified

      * See `Emacs Lisp => 32.19 Text Properties => Special
	Properties`

    * It would be nice to also have a visible indication for being
      automatic insertion

  * Such indentation must be removed by `longlines-encode-*`

    * Probably it should be marked by a special property such as
      `longlines-indentation`

  * `longlines-wrap-line` needs a hook called after replacing the
    blank by a soft newline

  * May be `longlines-*search-*` needs to be adapted as well?

Indent correctly
================

* `rst-shift-region` should have a mode to indent correctly

  * I.e.: Indent the region according to the tab given by the line
    above

* But see also `Copying literal blocks`_

Jumps leaving mark
==================

* All jumps across a wider distance should push the mark on the local
  mark ring

  * See C-u C-SPC documentation

  * Jumps to section titles

    * That would result in jumping back to TOC which is especially
      useful for an internal TOC

  * But not jumps to paragraphs

  * Jumps with C-M-a / C-M-e?

TOC controlling sliding window
==============================

* `toc-mode` must have a mode where cursor entering a new line moves
  to the respective section in another window

  * So one can browse through a buffer by using the TOC

Jump to list entry on same level
================================

* If on a list entry of some sort there should be a way to navigate to
  a sibling

  * Forward and backward

* May be also up and down

`rst-shift-region` shifts as needed
===================================

* `rst-shift-region` should have an option to "do the right thing"

* In particular it should shift as needed by the text above

  * This makes indentation of an inserted block easier because you
    don't need to know the correct number of tabs

  * There should be an option to "align under", "align same" and
    "align less"

  * May be this could be commanded by one or more C-u's
