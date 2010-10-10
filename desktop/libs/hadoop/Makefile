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


ifeq ($(ROOT),)
  $(error "Error: Expect the environment variable $$ROOT to point to the Desktop installation")
endif

include $(ROOT)/Makefile.sdk

default::
	@echo '  env-install    : Install into virtual-env'

#
# env-install
# 	Install app into the virtual environment.
#
.PHONY: env-install
env-install: compile ext-env-install
	@echo '--- Installing $(APP_NAME) into virtual-env'
	@$(ENV_PYTHON) setup.py develop -N -q

###################################
# Build Hadoop plugins
###################################

PLUGIN_DIR := $(realpath .)
PLUGIN_JAVA_LIB := $(PLUGIN_DIR)/java-lib
PLUGIN_JAVA_DIR := $(PLUGIN_DIR)/java
PLUGIN := $(PLUGIN_JAVA_LIB)/hue-plugins-$(DESKTOP_VERSION).jar
BLD_DIR_PLUGINS := $(PLUGIN_DIR)/build/java

STATIC_GROUP_MAPPING_DIR := $(realpath .)/static-group-mapping
STATIC_GROUP_MAPPING_SRC := $(STATIC_GROUP_MAPPING_DIR)/src
STATIC_GROUP_MAPPING_BUILD := $(STATIC_GROUP_MAPPING_DIR)/build
STATIC_GROUP_MAPPING_LIB := $(STATIC_GROUP_MAPPING_DIR)/java-lib
STATIC_GROUP_MAPPING := $(STATIC_GROUP_MAPPING_LIB)/static-group-mapping-$(DESKTOP_VERSION).jar

SUDO_SHELL_DIR := $(realpath .)/sudo-shell
SUDO_SHELL_SRC := $(SUDO_SHELL_DIR)/src
SUDO_SHELL_BUILD := $(SUDO_SHELL_DIR)/build
SUDO_SHELL_LIB := $(SUDO_SHELL_DIR)/java-lib
SUDO_SHELL := $(SUDO_SHELL_LIB)/sudo-shell-$(DESKTOP_VERSION).jar

compile: $(PLUGIN) $(STATIC_GROUP_MAPPING) $(SUDO_SHELL)

clean::
	rm -Rf $(PLUGIN_JAVA_LIB) $(STATIC_GROUP_MAPPING_LIB) $(SUDO_SHELL_LIB)

ifneq (,$(wildcard $(PLUGIN_JAVA_DIR)))
PLUGIN_OPTS := -Dbuild.dir=$(BLD_DIR_PLUGINS) \
	       -Dhadoop.home=$(HADOOP_HOME) \
	       -Dplugins.version=$(DESKTOP_VERSION)

$(PLUGIN): $(shell find $(PLUGIN_JAVA_DIR) )
	mkdir -p $(PLUGIN_JAVA_LIB)
	@echo "--- Building Hadoop plugins"
	cd $(PLUGIN_JAVA_DIR) && ant $(ANT_OPTS) $(PLUGIN_OPTS) jar
	cp $(BLD_DIR_PLUGINS)/$(notdir $(PLUGIN)) $(PLUGIN)
else
$(PLUGIN):
	$(error Cannot build hadoop plugin without source)
endif

STATIC_GROUP_MAPPING_OPTS := -Dbuild.dir=$(STATIC_GROUP_MAPPING_BUILD) \
         -Dhadoop.home=$(HADOOP_HOME) \
         -Dstatic-group-mapping.version=$(DESKTOP_VERSION)

$(STATIC_GROUP_MAPPING): $(shell find $(STATIC_GROUP_MAPPING_SRC))
	mkdir -p $(STATIC_GROUP_MAPPING_LIB)
	@echo "--- Building static UserGroupMappingService"
	cd $(STATIC_GROUP_MAPPING_DIR) && ant $(ANT_OPTS) $(STATIC_GROUP_MAPPING_OPTS) jar
	cp $(STATIC_GROUP_MAPPING_BUILD)/$(notdir $(STATIC_GROUP_MAPPING)) $(STATIC_GROUP_MAPPING)

SUDO_SHELL_OPTS := -Dbuild.dir=$(SUDO_SHELL_BUILD) \
         -Dhadoop.home=$(HADOOP_HOME) \
         -Dsudo-shell.version=$(DESKTOP_VERSION)

$(SUDO_SHELL): $(shell find $(SUDO_SHELL_SRC))
	mkdir -p $(SUDO_SHELL_LIB)
	@echo "--- Building sudo fsshell tool"
	cd $(SUDO_SHELL_DIR) && ant $(ANT_OPTS) $(SUDO_SHELL_OPTS) jar
	cp $(SUDO_SHELL_BUILD)/$(notdir $(SUDO_SHELL)) $(SUDO_SHELL)
#
# Tell the `bdist' target to exclude our java source.
#
BDIST_EXCLUDES += \
	--exclude=java \
	--exclude=regenerate-thrift.sh
