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
BLD_DIR_PLUGINS := $(PLUGIN_DIR)/java/target

STATIC_GROUP_MAPPING_DIR := $(realpath .)/static-group-mapping
STATIC_GROUP_MAPPING_SRC := $(STATIC_GROUP_MAPPING_DIR)/src
STATIC_GROUP_MAPPING_BUILD := $(STATIC_GROUP_MAPPING_DIR)/target
STATIC_GROUP_MAPPING_LIB := $(STATIC_GROUP_MAPPING_DIR)/java-lib
STATIC_GROUP_MAPPING := $(STATIC_GROUP_MAPPING_LIB)/static-group-mapping-$(DESKTOP_VERSION).jar

SUDO_SHELL_DIR := $(realpath .)/sudo-shell
SUDO_SHELL_SRC := $(SUDO_SHELL_DIR)/src
SUDO_SHELL_BUILD := $(SUDO_SHELL_DIR)/target
SUDO_SHELL_LIB := $(SUDO_SHELL_DIR)/java-lib
SUDO_SHELL := $(SUDO_SHELL_LIB)/sudo-shell-$(DESKTOP_VERSION).jar

CREDENTIALS_MERGER_DIR := $(realpath .)/credentials-merger
CREDENTIALS_MERGER_SRC := $(CREDENTIALS_MERGER_DIR)/src
CREDENTIALS_MERGER_BUILD := $(CREDENTIALS_MERGER_DIR)/target
CREDENTIALS_MERGER_LIB := $(CREDENTIALS_MERGER_DIR)/java-lib
CREDENTIALS_MERGER := $(CREDENTIALS_MERGER_LIB)/credentials-merger-$(DESKTOP_VERSION).jar

compile: $(DESKTOP_PLUGIN_JAR) $(STATIC_GROUP_MAPPING) $(SUDO_SHELL) $(CREDENTIALS_MERGER)

# Build the plugin jar iff the source is present
ifneq (,$(wildcard $(PLUGIN_JAVA_DIR)))
$(DESKTOP_PLUGIN_JAR): $(shell find $(PLUGIN_JAVA_DIR) -type f)
	mkdir -p $(PLUGIN_JAVA_LIB)
	@echo "--- Building Hadoop plugins"
	cd $(PLUGIN_JAVA_DIR) && mvn clean install -DskipTests $(MAVEN_OPTIONS)
	cp $(BLD_DIR_PLUGINS)/hue-plugins-$(MAVEN_VERSION).jar $(DESKTOP_PLUGIN_JAR)

clean::
	rm -rf $(PLUGIN_JAVA_LIB)
	cd $(PLUGIN_JAVA_DIR) && mvn clean $(MAVEN_OPTIONS) ||:
else
$(DESKTOP_PLUGIN_JAR):
	$(error Cannot build hadoop plugin without source)
endif

# Build the static group mapping jar iff the source is present
ifneq (,$(wildcard $(STATIC_GROUP_MAPPING_SRC)))
$(STATIC_GROUP_MAPPING): $(shell find $(STATIC_GROUP_MAPPING_SRC) -type f)
	mkdir -p $(STATIC_GROUP_MAPPING_LIB)
	@echo "--- Building static UserGroupMappingService"
	cd $(STATIC_GROUP_MAPPING_DIR) && mvn clean install -DskipTests $(MAVEN_OPTIONS)
	cp $(STATIC_GROUP_MAPPING_BUILD)/static-group-mapping-$(MAVEN_VERSION).jar $(STATIC_GROUP_MAPPING)

clean::
	rm -rf $(STATIC_GROUP_MAPPING_LIB)
	cd $(STATIC_GROUP_MAPPING_DIR) && mvn clean $(MAVEN_OPTIONS) ||:
else
$(STATIC_GROUP_MAPPING):
	$(error Cannot build static-group-mapping jar without source)
endif

# Build the sudo shell jar iff the source is present
ifneq (,$(wildcard $(SUDO_SHELL_SRC)))
$(SUDO_SHELL): $(shell find $(SUDO_SHELL_SRC) -type f)
	mkdir -p $(SUDO_SHELL_LIB)
	@echo "--- Building sudo fsshell tool"
	cd $(SUDO_SHELL_DIR) && mvn clean install -DskipTests $(MAVEN_OPTIONS)
	cp $(SUDO_SHELL_BUILD)/sudo-shell-$(MAVEN_VERSION).jar $(SUDO_SHELL)

clean::
	rm -rf $(SUDO_SHELL_LIB)
	cd $(SUDO_SHELL_DIR) && mvn clean $(MAVEN_OPTIONS) ||:
else
$(SUDO_SHELL):
	$(error cannot build sudo-shell jar without source)
endif

# Build the credentials merger jar iff the source is present
ifneq (,$(wildcard $(CREDENTIALS_MERGER_SRC)))
$(CREDENTIALS_MERGER): $(shell find $(CREDENTIALS_MERGER_SRC) -type f)
	mkdir -p $(CREDENTIALS_MERGER_LIB)
	@echo "--- Building credentials merger tool"
	cd $(CREDENTIALS_MERGER_DIR) && mvn clean install -DskipTests $(MAVEN_OPTIONS)
	cp $(CREDENTIALS_MERGER_BUILD)/credentials-merger-$(MAVEN_VERSION).jar $(CREDENTIALS_MERGER)

clean::
	rm -rf $(CREDENTIALS_MERGER_LIB)
	cd $(CREDENTIALS_MERGER_DIR) && mvn clean $(MAVEN_OPTIONS) ||:
else
$(CREDENTAILS_MERGER):
	$(error cannot build credentials merger jar without source)
endif

#
# Tell the `bdist' target to exclude our java source.
#
BDIST_EXCLUDES += \
	--exclude=java \
	--exclude=static-group-mapping/src \
	--exclude=sudo-shell/src \
	--exclude=regenerate-thrift.sh
