Use cases section header adjustment
===================================

Conditions
----------

* **Pr**\e\ **f**\erences
  * **N**\o preferences
  * **P**\references exist

* **Sel**\ection
  * **N**\o adornment around point
  * **E**\xisting adornment around point
  * **R**\egion

* **Pr**\e\ **v**\ious header
  * **N**\o previous header
  * **D**\isadvised previous header (i.e. not in preferences)
  * **P**\references contain previous header

* Current header in existing **hie**\rarchy
  * **N**\o hierarchy beyond current header
  * **M**\ultiple occurrence in the middle of existing hierarchy
  * **B**\reaking single entry in the middle of existing hierarchy
  * **L**\ast in existing hierarchy for given direction
  * **O**\nce in existing hierarchy at beginning or end of hierarchy

* **Cur**\rent header in preferences
  * **D**\isadvised (i.e. not in preferences)
  * **S**\uccessor exists in preferences
  * **L**\ast in preferences

* **Dir**\ection
  * **D**\ownward
  * **U**\pward

* **Res**\ult
  * **N**\o next
  * **E**\rror
  * **P**\references give next including rotation
  * **H**\ierarchy gives next including rotation
  * **T**\op of hierarchy
  * **L**\ast of hierarchy

* **Rem**\mark

Use cases
---------

+---+---+---+-----+---+---+-+------+-------------------------------------------+
|Prf|Sel|Prv|Hie  |Cur|Dir|#|Res   |Rem                                        |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|NP |NER|NDP|NMBLO|DSL|DU |#|NEPHTL|                                           |
+===+===+===+=====+===+===+-+======+===========================================+
|N> |?  |<ND|?    |<D |?  | |<NEHTL|[No preferences]                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |N> |<N>|<N   |<! |?  | |E     |Nothing there at all                       |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |N> |<N>|<!   |<! |?  | |T     |At top use top                             |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |N> |<D>|<!   |<! |?  | |H     |New section header in existing hierarchy   |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |E  |<N>|<N   |<D |?  | |E     |One and only header                        |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |<E |<N>|<M   |<D |?  | |H     |Top header matching medium level - continue|
|   |   |   |     |   |   | |      |reorganisation by a step                   |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |<E |<N>|<L   |<D |?  | |H     |Top header matching extreme level -        |
|   |   |   |     |   |   | |      |continue reorganisation by a rotation      |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |<E |<N>|<O   |<D |D  | |T     |Top header with exclusive level downwards -|
|   |   |   |     |   |   | |      |align to top of remaining hierarchy        |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |<E |<N>|<O   |<D |U  | |L     |Top header with exclusive level upwards -  |
|   |   |   |     |   |   | |      |align to last of remaining hierarchy       |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |<E |<D |<M   |<D |?  | |H     |Standard step                              |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |<E |<D |<B   |<D |?  | |H     |Align breaking header                      |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |<E |<D |<L   |<D |?  | |H     |Step or rotate                             |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |<E |<D |<O   |<D |?  | |H     |Step or rotate                             |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|###|###|###|#####|###|###|#|######|###########################################|
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |N> |<N>|N>   |<! |?  | |P     |Only preferences exist                     |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |N> |N> |<!   |<! |D  | |T     |At top downwards use top of hierarchy      |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |N> |N> |<!   |<! |U  | |P     |At top upwards use top of preferences      |
|   |   |   |     |   |   | |      |adding a title                             |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<M   |D  |?  | |H     |Prefer hierarchy over preferences          |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<M   |S  |?  | |H     |Prefer hierarchy over preferences          |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<M   |L  |?  | |H     |Prefer hierarchy over preferences          |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<B   |D  |?  | |H     |Prefer hierarchy over preferences          |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<B   |S  |?  | |H     |Prefer hierarchy over preferences          |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<B   |L  |?  | |H     |Prefer hierarchy over preferences          |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<L   |D  |D  | |H     |Wrap to top level                          |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<L   |D  |U  | |P     |Use first from preferences                 |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<L   |S  |D  | |P     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<L   |S  |U  | |P     |Prefer preferences                         |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<L   |L  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<O   |D  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<O   |S  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |D> |<O   |L  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<M   |D  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<M   |S  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<M   |L  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<B   |D  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<B   |S  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<B   |L  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<L   |D  |?  | |P     |Prefer preferences                         |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<L   |S  |?  | |P     |Prefer preferences                         |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<L   |L  |?  | |P     |Prefer preferences                         |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<O   |D  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<O   |S  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|P  |<E |P> |<O   |L  |?  | |H     |Prefer hierarchy                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|   |   |   |     |   |   | |      |                                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|   |   |   |     |   |   | |      |                                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|   |   |   |     |   |   | |      |                                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|   |   |   |     |   |   | |      |[CONSTRAINTS]                              |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |?  |<ND|?    |<D |?  | |<NEHTL|Without preferences no header may relate to|
|   |   |   |     |   |   | |      |them                                       |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|?  |N> |?  |<N!  |<! |?  | |      |Without a selection the current header may |
|   |   |   |     |   |   | |      |not relate to anything                     |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|?  |?  |N> |<NMLO|?  |?  | |      |Without a previous header only certain     |
|   |   |   |     |   |   | |      |relations to hierarchy are possible        |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|?  |?  |D> |<MBLO|?  |?  | |      |With a disadvised previous header only     |
|   |   |   |     |   |   | |      |certain relations to hierarchy are possible|
|   |   |   |     |   |   | |      |for current header                         |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|?  |?  |<N |N>   |?  |?  | |<NPE  |Without hierarchy there can be no previous |
|   |   |   |     |   |   | |      |header and result may not come from        |
|   |   |   |     |   |   | |      |hierarchy                                  |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|?  |<E |   |MBLO>|   |   | |      |If the header has a relation than it must  |
|   |   |   |     |   |   | |      |exist                                      |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|   |   |   |     |   |   | |      |REGION                                     |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|N> |R  |<ND|     |<D |   | |      |                                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+
|   |   |   |     |   |   | |      |                                           |
+---+---+---+-----+---+---+-+------+-------------------------------------------+

* For each line in the table there should be an ert test named
  `rst-adjust-section-prf-_-sel-_-prv-_-hie-_-cur-_-dir-_` where the
  ``_`` stand for the respective cell entries

* In addition each operation should be reversible by using the
  opposite direction

  * Unless the information before reversion is lost by the first
    operation

Legend
------

* "X>" means "if X"

* "<XY" means "X or Y follow from an if"

* "-" means "irrelevant"

* "!" means "does not apply"

* "?" means "any"

* "[X]" means "header for situation group X"
