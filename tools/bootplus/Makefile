BOOTPLUS = ../../desktop/core/static/ext/css/bootplus.css
BOOTPLUS_LESS = ./less/bootplus/bootplus.less
BOOTPLUS_RESPONSIVE = ../../desktop/core/static/ext/css/bootplus-responsive.css
BOOTPLUS_RESPONSIVE_LESS = ./less/bootplus/responsive.less
DATE=$(shell date +%I:%M%p)
CHECK=\033[32m✔ Done\033[39m
HR=\033[37m--------------------------------------------------\033[39m
PATH := ./node_modules/.bin:$(PATH)


#
# BUILD DOCS
#

build:
	@echo "\n${HR}"
	@echo "Building Bootplus..."
	@echo "${HR}\n"
	@printf "Compiling LESS with Recess..."
	@recess --compress ${BOOTPLUS_LESS} > ${BOOTPLUS}
	@recess --compress ${BOOTPLUS_RESPONSIVE_LESS} > ${BOOTPLUS_RESPONSIVE}
	@echo "             ${CHECK}"
	@echo "\n${HR}"
	@echo "Bootplus successfully built at ${DATE}."
	@echo "${HR}\n"
	@echo "Thanks for using Bootplus"

#
# BUILD SIMPLE BOOTPLUS DIRECTORY
# recess & uglifyjs are required
#

bootplus: bootplus-css

#
# CSS COMPILE
#

bootplus-css: bootplus/css/*.css

bootplus/css/*.css: less/*.less
	mkdir -p bootplus/css
	./node_modules/.bin/recess --compile ${BOOTPLUS_LESS} > bootplus/css/bootplus.css
	./node_modules/.bin/recess --compress ${BOOTPLUS_LESS} > bootplus/css/bootplus.min.css
	./node_modules/.bin/recess --compile ${BOOTPLUS_RESPONSIVE_LESS} > bootplus/css/bootplus-responsive.css
	./node_modules/.bin/recess --compress ${BOOTPLUS_RESPONSIVE_LESS} > bootplus/css/bootplus-responsive.min.css
	mkdir -p bootplus/font
	cp -R docs/assets/font/*.* bootplus/font


#
# WATCH LESS FILES
#

watch:
	echo "Watching less files..."; \
	watchr -e "watch('less/.*\.less') { system 'make' }"


.PHONY: watch bootplus-css