<!DOCTYPE style-sheet PUBLIC "-//James Clark//DTD DSSSL Style Sheet//EN" [
<!ENTITY walsh-style PUBLIC "-//Norman Walsh//DOCUMENT DocBook HTML Stylesheet//EN" CDATA DSSSL>
]>

<style-sheet>

<style-specification id="html" use="docbook">
<style-specification-body>

(define %root-filename% "index")        ;; name for the root html file
(define %html-ext% ".html")             ;; default extension for html output files
(define %html-prefix% "hue")            ;; prefix for all filenames generated (except root)

; Use the section id as the filename rather than
; cryptic filenames like x1547.html
(define %use-id-as-filename% #t)

(define %gentext-nav-use-tables%
          ;; Use tables to build the navigation headers and footers?
          #t)

; Repeat the section number in each section to make it easier
; when browsing the doc
(define %section-autolabel% #t)

; Use CSS to make the look of the documentation customizable
(define %stylesheet% "docbook.css")
(define %stylesheet-type% "text/css")

; === Rendering ===
(define %admon-graphics% #t)            ;; use symbols for Caution|Important|Note|Tip|Warning
(define %admon-graphics-path% "images/");; path to the admonitions graphics
(define %admon-graphics-extension% ".png");; extension for admon graphics
(define %admon-graphic-default-extension% ".png");;
(define %stock-graphics-extension% ".png");;

; === Books only ===
(define %generate-book-titlepage% #t)
(define %generate-book-toc% #t)
(define ($generate-chapter-toc$) #f)    ;; never generate a chapter TOC in books

; === Articles only ===
(define %generate-article-titlepage% #t)
(define %generate-article-toc% #t)      ;; make TOC
(define (toc-depth nd) 5)

</style-specification-body>
</style-specification>

<external-specification id="docbook" document="walsh-style">

</style-sheet>
