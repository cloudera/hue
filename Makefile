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
#                  virtual-bootstrap.py
#                            |
#                  virtual-env (./env)
#                            |
#                      +----------+
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
PPC64LE := $(shell uname -m)

include $(ROOT)/Makefile.vars.priv


###################################
# Error checking
###################################


.PHONY: default
default:
	@echo 'The build targets for Hue $(DESKTOP_VERSION) are:'
	@echo '  install     : Install at $$PREFIX ($(INSTALL_DIR)); need desktop'
	@echo '  apps        : Build and register all desktop apps; need desktop'
	@echo '  desktop     : Build desktop core only'
	@echo '  clean       : Remove desktop build products'
	@echo '  distclean   : Remove desktop and thirdparty build products'
# <<<< DEV ONLY
	@echo '  doc 	     : Build documentation'
	@echo '  prod        : Generate a tar file for production distribution'
	@echo '  locales     : Extract strings and update dictionary of each locale'
	@echo '  ace         : Builds the Ace Editor tool'
# END DEV ONLY >>>>

.PHONY: all
all: default

# <<<< DEV ONLY
include Makefile.tarball

###################################
# Build docs (unused)
###################################
test_prep:
	@$(ENV_PYTHON) -m pip install -r $(REQUIREMENT_TEST_FILE)

###################################
# Build docs (unused)
###################################
.PHONY: docs
docs:
	@$(MAKE) -C docs
# END DEV ONLY >>>>

###################################
# Install parent POM
###################################
.PHONY: parent-pom
parent-pom:
ifneq (,$(BUILD_DB_PROXY))
	cd $(ROOT)/maven && mvn install $(MAVEN_OPTIONS)
endif

$(info "PYTHON_VER is $(PYTHON_VER)")
$(info "SYS_PYTHON is $(SYS_PYTHON)")
$(info "ENV_PYTHON is $(ENV_PYTHON)")
$(info "SYS_PIP is $(SYS_PIP)")
$(info "ENV_PIP is $(ENV_PIP)")
$(info "PYTHON_INCLUDE_DIR is $(PYTHON_INCLUDE_DIR)")
$(info "PYTHON_H is $(PYTHON_H)")
$(info "PIP_VERSION is $(PIP_VERSION)")
$(info "VIRTUAL_ENV_VERSION is $(VIRTUAL_ENV_VERSION)")
$(info "RELOCATABLE is $(RELOCATABLE)")
$(info "LOCAL_PY_BIN is $(LOCAL_PY_BIN)")
$(info "BLD_DIR_ENV is $(BLD_DIR_ENV)")
$(info "REQUIREMENT_FILE is $(REQUIREMENT_FILE)")
$(info "INSTALL_DIR is $(INSTALL_DIR)")
$(info "INST_DIR_ENV is $(INST_DIR_ENV)")
$(info "PPC64LE is $(PPC64LE)")
###################################
# virtual-env
# Enhanced to support building and packaging Hue for multiple Python versions.
# Adds per-Python virtual environment creation, improved logging and diagnostics,
# Test push
###################################
virtual-env: $(BLD_DIR_ENV)/bin/python
$(BLD_DIR_ENV)/bin/python:
	@echo "--- Creating virtual environment for $(PYTHON_VER) ---"
	@mkdir -p $(BLD_DIR_ENV)
	@$(SYS_PYTHON) -m pip install --upgrade pip==$(PIP_VERSION)
	@$(SYS_PYTHON) -m pip install virtualenv==$(VIRTUAL_ENV_VERSION) virtualenv-make-relocatable==$(VIRTUAL_ENV_RELOCATABLE_VERSION)
	@$(SYS_PYTHON) -m virtualenv --copies -p $(PYTHON_VER) $(BLD_DIR_ENV)
	@$(ENV_PYTHON) -m pip install virtualenv==$(VIRTUAL_ENV_VERSION) virtualenv-make-relocatable==$(VIRTUAL_ENV_RELOCATABLE_VERSION)
	@$(eval RELOCATABLE := $(shell which virtualenv-make-relocatable))
	@echo "REQUIREMENT_FILE is $(REQUIREMENT_FILE)"
	@$(ENV_PIP) install -r $(REQUIREMENT_FILE)
	@echo "--- Virtual environment setup complete for $(PYTHON_VER) ---"
	@$(ENV_PIP) install $(NAVOPTAPI_WHL)
	@echo "--- Finished installing $(NAVOPTAPI_WHL) into virtual-env ---"
###################################
# Build desktop
###################################
.PHONY: desktop

# <<<< DEV ONLY
desktop: parent-pom
# END DEV ONLY >>>>
desktop: virtual-env
	@$(MAKE) -C desktop

###################################
# relocatable-env
# Enhanced to support relocatable .pth files.
###################################
relocatable-env:
	@$(MAKE) virtual-env
	@echo "--- Running $(SYS_PYTHON) $(RELOCATABLE) $(BLD_DIR_ENV)"
	@$(ENV_PYTHON) $(RELOCATABLE) $(BLD_DIR_ENV)
	@echo "--- Setting up pth files $(ENV_PYTHON) $(ROOT)/tools/relocatable.py"
	@$(ENV_PYTHON) $(ROOT)/tools/relocatable.py

###################################
# Build apps
###################################
.PHONY: apps
apps: desktop
	@$(MAKE) npm-install
	@$(MAKE) -C $(APPS_DIR) env-install
	@$(MAKE) create-static

###################################
# Install binary dist
###################################
INSTALL_CORE_FILES = \
	Makefile* $(wildcard *.mk) \
	ext \
	tools/app_reg \
	$(INSTALL_DIR) \
	VERS* LICENSE* README*

.PHONY: install
install: virtual-env install-check install-core-structure install-desktop install-apps install-env

.PHONY: install-check
install-check:
	@if [ -n '$(wildcard $(INST_DIR_ENV)/*)' ] ; then \
	  echo "ERROR: $(INST_DIR_ENV) is not empty. Contents:" ; \
	  ls -la "$(INST_DIR_ENV)" ; \
	  echo 'ERROR: $(INST_DIR_ENV) not empty. Cowardly refusing to continue.' ; \
	  false ; \
	fi

.PHONY: install-core-structure
install-core-structure:
	@echo --- Installing core source structure in $(INSTALL_DIR)...
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
	@echo --- Setting up Frontend assets
	cp $(ROOT)/package.json $(INSTALL_DIR)
	cp $(ROOT)/package-lock.json $(INSTALL_DIR)
	cp $(ROOT)/webpack.config*.js $(INSTALL_DIR)
	cp $(ROOT)/babel.config.js $(INSTALL_DIR)
	cp $(ROOT)/tsconfig.json $(INSTALL_DIR)
	$(MAKE) -C $(INSTALL_DIR) npm-install
	$(MAKE) -C $(INSTALL_DIR) create-static


###################################
# Frontend and static assets
###################################

.PHONY: npm-install
npm-install: .npm-install-lock
.npm-install-lock:
	npm --version
	node --version
	npm install
	npm run webpack
	npm run webpack-login
	npm run webpack-workers
	node_modules/.bin/removeNPMAbsolutePaths .
	rm -rf node_modules
	touch .npm-install-lock

.PHONY: create-static
create-static:
	$(ENV_PYTHON) $(BLD_DIR_BIN)/hue collectstatic --noinput

# <<<< DEV ONLY
.PHONY: doc
doc:
	hugo --source docs/docs-site
# END DEV ONLY >>>>


###################################
# Internationalization
###################################

# <<<< DEV ONLY
.PHONY: locales
locales:
	@$(MAKE) -C desktop compile-locales
	@$(MAKE) -C apps compile-locales
# END DEV ONLY >>>>


###################################
# Ace Editor
###################################

# <<<< DEV ONLY
.PHONY: ace
ace:
	@cd tools/ace-editor && ./hue-ace.sh
# END DEV ONLY >>>>


###################################
# JISON Parser Generators
###################################

# <<<< DEV ONLY
.PHONY: global-search-parser
global-search-parser:
	@pushd tools/jison/ && npm install && node generateParsers.js globalSearchParser && popd

.PHONY: solr-all-parsers
solr-all-parsers:
	@pushd tools/jison/ && npm install  && node generateParsers.js solrQueryParser solrFormulaParser && popd

.PHONY: solr-query-parser
solr-query-parser:
	@pushd tools/jison/ && npm install  && node generateParsers.js solrQueryParser && popd

.PHONY: solr-formula-parser
solr-formula-parser:
	@pushd tools/jison/ && npm install  && node generateParsers.js solrFormulaParser && popd

.PHONY: sql-all-parsers
sql-all-parsers:
	@pushd tools/jison/ && npm install  && node generateParsers.js generic hive impala && popd

.PHONY: sql-autocomplete-parser
sql-autocomplete-parser:
	@pushd tools/jison/ && npm install  && node generateParsers.js genericAutocomp hiveAutocomp impalaAutocomp && popd

.PHONY: sql-statement-parser
sql-statement-parser:
	@pushd tools/jison/ && npm install  && node generateParsers.js sqlStatementsParser && popd

.PHONY: sql-syntax-parser
sql-syntax-parser:
	@pushd tools/jison/ && npm install  && node generateParsers.js genericSyntax hiveSyntax impalaSyntax && popd
# END DEV ONLY >>>>

###################################
# Cleanup
###################################

.PHONY: clean
clean:
	@$(MAKE) -C desktop clean
	@$(MAKE) -C apps clean
# <<<< DEV ONLY
	@$(MAKE) -C docs clean
# END DEV ONLY >>>>
	@rm -rf $(BLD_DIR_ENV)
	@rm -rf $(STATIC_DIR)

#
# Note: It is important for clean targets to *ONLY* clean products of the
#       build, and not misc runtime generated files. Don't abuse Makefile.
#
.PHONY: distclean
distclean: clean
	@# Remove the other directories in build/
	@$(MAKE) -C desktop distclean
	@$(MAKE) -C apps distclean
	@rm -rf $(BLD_DIR)

.PHONY: ext-clean
ext-clean:
	@$(MAKE) -C desktop ext-clean
	@$(MAKE) -C apps ext-clean

# <<<< DEV ONLY
###############################################
# Misc (some used by automated test scripts)
###############################################

huecheck:
	@echo "Checking for release..."
	DESKTOP_DEBUG=1 $(ENV_PYTHON) $(BLD_DIR_BIN)/hue check

test:
	DESKTOP_DEBUG=1 $(ENV_PYTHON) $(BLD_DIR_BIN)/hue test fast --with-xunit

test-slow:
	DESKTOP_DEBUG=1 $(ENV_PYTHON) $(BLD_DIR_BIN)/hue test all --with-xunit --with-cover
	$(BLD_DIR_BIN)/coverage xml -i

start-dev:
	DESKTOP_DEBUG=1 $(ENV_PYTHON) $(BLD_DIR_BIN)/hue runserver_plus

devinstall:
	npm run devinstall

css:
	npm run less
# END DEV ONLY >>>>
