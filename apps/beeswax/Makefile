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

APP_NAME = hue-beeswax
include $(ROOT)/Makefile.sdk

###################################
# Build beeswax
###################################

BEESWAX_ROOT := $(realpath .)
BLD_DIR_BEESWAX=$(BEESWAX_ROOT)/java/target
BEESWAX_JAVA_LIB := $(BEESWAX_ROOT)/java-lib
BEESWAX_HIVE_LIB := $(BEESWAX_ROOT)/hive/lib

BEESWAX := $(BEESWAX_JAVA_LIB)/BeeswaxServer.jar
BEESWAX_JAVA_DIR := $(BEESWAX_ROOT)/java

HAVE_JAVA_SRC=$(wildcard $(BEESWAX_JAVA_DIR))


compile: $(BEESWAX)

ifneq (,$(HAVE_JAVA_SRC))

# If we have the source, remove the java-lib
clean::
	rm -Rf $(BEESWAX_JAVA_LIB)
	cd $(BEESWAX_JAVA_DIR) && mvn clean $(MAVEN_OPTIONS) || :

$(BEESWAX): $(shell find $(BEESWAX_JAVA_DIR) -type f)
	@echo "--- Building Desktop beeswax"
	cd $(BEESWAX_JAVA_DIR) && mvn clean install -DskipTests $(MAVEN_OPTIONS)
	@mkdir -p $(BEESWAX_JAVA_LIB)
	@cp $(BLD_DIR_BEESWAX)/beeswax-server-$(MAVEN_VERSION).jar $@

else
$(BEESWAX):
	$(error Cannot build beeswax jars without source)
endif

#
# Tell the `bdist' target to exclude our java source.
#
BDIST_EXCLUDES += \
	--exclude=java \
	--exclude=thrift

SDIST_EXCLUDES += \
	--exclude=java-lib \
	--exclude=thrift
