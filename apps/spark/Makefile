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

APP_NAME = spark
include $(ROOT)/Makefile.sdk

SPARK_ROOT := $(realpath .)
JAVA_LIB = $(SPARK_ROOT)/java-lib

LIVY_DIR = $(SPARK_ROOT)/java
LIVY_TARGET_DIR = $(LIVY_DIR)/livy-assembly/target/scala-2.10
LIVY_ASSEMBLY_JAR = livy-assembly-$(MAVEN_VERSION).jar
LIVY_JAR = $(JAVA_LIB)/$(LIVY_ASSEMBLY)

HAVE_JAVA_SRC = $(wildcard $(LIVY_DIR))

compile: $(LIVY_JAR)

ifneq (,$(wildcard $(LIVY_DIR)))
$(LIVY_JAR): $(shell find $(LIVY_DIR) -type f)
	mkdir -p $(JAVA_LIB)
	@echo "--- Building Desktop spark"
	cd $(LIVY_DIR) && mvn clean install -DskipTests $(MAVEN_OPTIONS)
	cp $(LIVY_TARGET_DIR)/$(LIVY_ASSEMBLY_JAR) $(LIVY_JAR)

clean::
	rm -Rf $(JAVA_LIB)
	cd $(LIVY_DIR) && mvn clean $(MAVEN_OPTIONS) || :
else
$(LIVY_JAR):
	$(error Cannot build spark jars without source)
endif

BDIST_EXCLUDES += \
	--exclude=java

SDIST_EXCLUDES += \
	--exclude=java-lib
