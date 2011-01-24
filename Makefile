#
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# <<<< DEV ONLY
#
# Hue Build Process Overview
# =======================================
# This build process handles different types of builds:
#
#   - The production release build, the main task of which is to install
#     Desktop in the local system. The main build products are:
#
#     * build/env 		- The virtual environment, where Desktop core
#     				  and various apps install into.
#
#   - The development build, which includes test and debugging tools. It
#     generates the production release, which boils down to a tarball that is
#     downloaded and installed. Additional build products include:
#
#     * build/release/prod 	- The production tarball.
#     * build/docs 		- General Desktop and SDK docs.
#
# We achieve this by selecting the parts to be distributed, and by stripping
# the Makefile's. Lines enclosed by the "DEV ONLY" marks are stripped for the
# general release. Targets are split/expanded using multiple rules and
# double-colon rules. The idea is to use almost identical build logic for the
# different flavours.
#
# Logic Flow
# ==========
# Here we summarize the flow of the build logic. Lines represent dependency.
#
#   virtual-bootstrap.py
#             |                       ext/thirdparty/js (crepo sync)
#   virtual-env (./env)                           |
#             |                                   |
#             '--------+----------+---------------'
#                      |          |
#                      |          V
#                      |       desktop  <--- recursive make in /desktop
#                      |          |
#                      |          V
#                      |         apps   <--- recursive make in /apps
#                      |
#                      V
#                 prod tarball   <-- selective copying into /build/release/...
#
#
# Application Build
# =================
# An app typically includes $(ROOT)/Makefile.sdk, which provides the standard
# targets and facilities. ROOT, which points to the Hue installation root, is
# always passed in.
#
# The application may also choose to not use the Hue build facilities. In that
# case, its Makefile still receives $(ROOT), and needs to provide several
# targets as specified in Makefile.sdk.
#
# END DEV ONLY >>>>

###################################
# Global variables
###################################
ROOT := $(realpath .)

include $(ROOT)/Makefile.vars.priv

###################################
# Error checking
###################################

# <<<< DEV ONLY
CREPO ?= $(shell which crepo 2> /dev/null)
ifeq ($(CREPO),)
  $(error "Error: Need crepo. See <http://github.com/cloudera/crepo>.")
endif

ifneq ($(shell test -e $(HADOOP_HOME)/hadoop-core-0.20*.jar -o -e $(HADOOP_HOME)/hadoop*0.20*core.jar && echo $$?),0)
  $(error "Error: No Hadoop 0.20 installation at $(HADOOP_HOME). Please set $$HADOOP_HOME.")
endif
# END DEV ONLY >>>>


.PHONY: default
default:
	@echo 'The build targets for Hue $(DESKTOP_VERSION) are:'
	@echo '  install     : Install at $$PREFIX ($(INSTALL_DIR)); need desktop'
	@echo '  apps        : Build and register all desktop apps; need desktop'
	@echo '  desktop     : Build desktop core only'
	@echo '  clean       : Remove desktop build products'
	@echo '  distclean   : Remove desktop and thirdparty build products'
# <<<< DEV ONLY
	@echo '  docs        : Build documentation'
	@echo '  crepo       : Update crepo'
	@echo '  prod        : Generate a tar file for production distribution'
# END DEV ONLY >>>>

.PHONY: all
all: default

# <<<< DEV ONLY
include Makefile.tarball

###################################
# Build docs
###################################
.PHONY: docs
docs:
	@$(MAKE) -C docs

###################################
# Crepo
###################################

# Development use crepo to fetch thirdparty dependencies.

.PHONY: crepo
crepo: $(THIRDPARTY_JS_DIR)/manifest.json $(THIRDPARTY_JS_DIR)/*.hash parent-pom
	@echo "--- Synchronizing external dependencies with crepo"
	@mkdir -p $(BLD_DIR)
	@cd $(THIRDPARTY_JS_DIR) && $(CREPO) sync && \
	  ($(CREPO) dump-refs > $(ROOT)/VERSION_DATA || true)
# END DEV ONLY >>>>

###################################
# Install parent POM
###################################
parent-pom:
	cd $(ROOT)/maven && mvn install

.PHONY: parent-pom

###################################
# virtual-env
###################################
virtual-env: $(BLD_DIR_ENV)/stamp
$(BLD_DIR_ENV)/stamp:
	@echo "--- Creating virtual environment at $(BLD_DIR_ENV)"
	$(SYS_PYTHON) $(VIRTUAL_BOOTSTRAP) \
		$(VIRTUALENV_OPTS) --no-site-packages $(BLD_DIR_ENV)
	@touch $@
	@echo "--- $(BLD_DIR_ENV) ready"

.PHONY: virtual-env

###################################
# Build desktop
###################################
.PHONY: desktop

# <<<< DEV ONLY
desktop: crepo
# END DEV ONLY >>>>
desktop: virtual-env
	@$(MAKE) -C desktop

###################################
# Build apps
###################################
.PHONY: apps
apps: desktop
	@$(MAKE) -C $(APPS_DIR) env-install

###################################
# Install binary dist
###################################
INSTALL_CORE_FILES = \
	Makefile* $(wildcard *.mk) \
	example* \
	ext \
	tools/app_reg \
	tools/virtual-bootstrap \
	VERS* LICENSE* README*

.PHONY: install
install: virtual-env install-check install-core-structure install-desktop install-apps install-env

.PHONY: install-check
install-check:
	@if [ -n '$(wildcard $(INSTALL_DIR)/*)' ] ; then \
	  echo 'ERROR: $(INSTALL_DIR) not empty. Cowardly refusing to continue.' ; \
	  false ; \
	fi

.PHONY: install-core-structure
install-core-structure:
	@echo --- Installing core source structure...
	@mkdir -p $(INSTALL_DIR)
	@tar cf - $(INSTALL_CORE_FILES) | tar -C $(INSTALL_DIR) -xf -
	@# Add some variables to Makefile to make sure that our virtualenv
	@# in the install root is the same one we built from - this also
	@# disables the check for python-devel packages which are no longer
	@# needed
	@echo "SYS_PYTHON=$(ENV_PYTHON_VERSION)" > $(INSTALL_DIR)/Makefile.buildvars
	@echo "SKIP_PYTHONDEV_CHECK=1" >> $(INSTALL_DIR)/Makefile.buildvars

.PHONY: install-desktop
install-desktop:
	@echo --- Installing Desktop core...
	INSTALL_DIR=$(realpath $(INSTALL_DIR)) $(MAKE) -C desktop install

.PHONY: install-apps
install-apps:
	@echo '--- Installing Applications...'
	INSTALL_DIR=$(realpath $(INSTALL_DIR)) $(MAKE) -C apps install

.PHONY: install-env
install-env:
	@echo --- Creating new virtual environment
	$(MAKE) -C $(INSTALL_DIR) virtual-env
	@echo --- Setting up Desktop core
	$(MAKE) -C $(INSTALL_DIR)/desktop env-install
	@echo --- Setting up Applications
	$(MAKE) -C $(INSTALL_DIR)/apps env-install
	@echo --- Setting up Desktop database
	$(MAKE) -C $(INSTALL_DIR)/desktop syncdb


###################################
# Cleanup
###################################

.PHONY: clean
clean:
	@rm -rf $(BLD_DIR_ENV)
	@$(MAKE) -C desktop clean
	@$(MAKE) -C apps clean
# <<<< DEV ONLY
	@$(MAKE) -C docs clean
	@echo "Removing dependencies managed by crepo"
	@cd $(THIRDPARTY_JS_DIR) && $(CREPO) do-all -x clean -f -x -d
	@rm -f VERSION_DATA
# END DEV ONLY >>>>

#
# Note: It is important for clean targets to *ONLY* clean products of the
#       build, and not misc runtime generated files. Don't abuse Makefile.
#
.PHONY: distclean
distclean: clean
	@# Remove the other directories in build/
	@rm -rf $(BLD_DIR)
	@$(MAKE) -C desktop distclean
	@$(MAKE) -C apps distclean

# <<<< DEV ONLY
###############################################
# Misc (some used by automated test scripts)
###############################################
test:
	DESKTOP_DEBUG=1 $(BLD_DIR_BIN)/hue test fast --with-xunit

test-slow:
	DESKTOP_DEBUG=1 $(BLD_DIR_BIN)/hue test all --with-xunit --with-cover
	$(BLD_DIR_BIN)/coverage xml

start-dev:
	DESKTOP_DEBUG=1 $(BLD_DIR_BIN)/hue runserver_plus
# END DEV ONLY >>>>
