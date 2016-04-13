#
# Makefile to generate epydoc documentation for the NDG HTTPS Client Package
#
# @author P J Kershaw 17/01/12
#

# @copyright: (C) 2012 STFC
#
# @license: BSD - see LICENSE file for details
#
# $Id$

# Generate HTML from embedded epydoc text in source code.
EPYDOC=epydoc
EPYDOC_INDIR=../ndg
EPYDOC_OUTDIR=.
EPYDOC_NAME='NDG HTTPS Client'
EPYDOC_LOGFILE=epydoc.log
EPYDOC_OPTS=--no-frames --include-log --graph=all -v --debug
ZIP=zip
ZIP_OUTFILE=./documentation.zip
ZIP_INFILES=./*.*

epydoc:
	${EPYDOC} ${EPYDOC_INDIR} -o ${EPYDOC_OUTDIR} --name ${EPYDOC_NAME} \
	${EPYDOC_OPTS} > ${EPYDOC_LOGFILE}
    
zip:
	${ZIP} ${ZIP_OUTFILE} ${ZIP_INFILES}    

clean:
	rm -f *.txt *.html *.gif *.css *.js *.png *.log
