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

# Application installation
# ========================
# The apps/ directory contains all the opensource apps. The standard build
# process installs all of them. You can use the `app_reg' tool for more
# fine-grain control.
#

export ROOT := $(realpath ..)
include $(ROOT)/Makefile.vars.priv

default: env-install

.PHONY: clean default distclean install

APPS := $(shell find . -maxdepth 2 -name "src" -type d|cut -d"/" -f2|sort)

################################################
# Install all applications into the Desktop environment
# Updates all recursive targets to pass through PYTHON_VER, ENV_PYTHON, and VIRTUAL_ENV
# to ensure application builds and installs work per Python version.
################################################
EGG_INFO_TARGETS := $(APPS:%=.recursive-egg-info/%)
.recursive-egg-info/%:
	@$(MAKE) -C $* egg-info ext-eggs

.PHONY: env-install
env-install: $(EGG_INFO_TARGETS)
	ENV_PYTHON=$(ENV_PYTHON) PYTHON_VER=$(PYTHON_VER) VIRTUAL_ENV=$(BLD_DIR_ENV) $(APP_REG) --install $(APPS) --relative-paths


################################################
# Distribution
################################################
INSTALL_BDIST_TARGETS := $(APPS:%=.recursive-install-bdist/%)
.recursive-install-bdist/%: %
	INSTALL_DIR=$(INSTALL_DIR)/apps/$< PYTHON_VER=$(PYTHON_VER) ENV_PYTHON=$(ENV_PYTHON) VIRTUAL_ENV=$(BLD_DIR_ENV) $(MAKE) -C $< install-bdist

.PHONY: install
install: install-source-parts $(INSTALL_BDIST_TARGETS)

#
# install-source-parts:
#     Installs the non-app parts into the INSTALL_DIR
#
SOURCE_PARTS = Makefile

.PHONY: install-source-parts
install-source-parts:
	mkdir -p $(INSTALL_DIR)/apps
	tar cf - $(SOURCE_PARTS) | tar -C $(INSTALL_DIR)/apps -xf -


################################################
# Clean all the apps
################################################
CLEAN_TARGETS := $(APPS:%=.recursive-clean/%)
DISTCLEAN_TARGETS := $(APPS:%=.recursive-distclean/%)
EXT_CLEAN_TARGETS := $(APPS:%=.recursive-ext-clean/%)

clean: $(CLEAN_TARGETS)
.recursive-clean/%:
	@PYTHON_VER=$(PYTHON_VER) ENV_PYTHON=$(ENV_PYTHON) VIRTUAL_ENV=$(BLD_DIR_ENV) $(MAKE) -C $* clean
	@$(APP_REG) --remove $* ||:

distclean: $(DISTCLEAN_TARGETS)
.recursive-distclean/%:
	@PYTHON_VER=$(PYTHON_VER) ENV_PYTHON=$(ENV_PYTHON) VIRTUAL_ENV=$(BLD_DIR_ENV) $(MAKE) -C $* distclean
	@$(APP_REG) --remove $* ||:

ext-clean: $(EXT_CLEAN_TARGETS)
.recursive-ext-clean/%:
	@PYTHON_VER=$(PYTHON_VER) ENV_PYTHON=$(ENV_PYTHON) VIRTUAL_ENV=$(BLD_DIR_ENV) $(MAKE) -C $* ext-clean


################################################
# Internationalization
################################################
I18N_APPS := about \
  beeswax \
  metastore \
  filebrowser \
  jobbrowser \
  jobsub \
  useradmin \
  oozie \
  impala \
  pig \
  search \
  hbase \
  sqoop \
  zookeeper \
  rdbms \
  spark \
  hive

COMPILE_LOCALE_TARGETS := $(I18N_APPS:%=.recursive-compile-locales/%)
compile-locales: $(COMPILE_LOCALE_TARGETS)
.recursive-compile-locales/%:
	-@PYTHON_VER=$(PYTHON_VER) ENV_PYTHON=$(ENV_PYTHON) VIRTUAL_ENV=$(BLD_DIR_ENV) $(MAKE) -C $* compile-locale
