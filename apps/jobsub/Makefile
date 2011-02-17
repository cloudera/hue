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

APP_NAME = hue-jobsub
include $(ROOT)/Makefile.sdk

#############################
# Jobsub specific
#############################

BLD_DIR_JOBSUB := $(BUILD_DIR)/java
JOBSUB_JAVA_LIB := $(APP_ROOT)/java-lib

JOBSUB := $(JOBSUB_JAVA_LIB)/trace.jar
JOBSUB_JAVA_DIR := $(APP_ROOT)/src/jobsub/java

#
# Compile jobsub
#
compile: $(JOBSUB)

clean::
	rm -Rf $(JOBSUB_JAVA_LIB)

ifneq (,$(wildcard $(JOBSUB_JAVA_DIR)))
JOBSUB_OPTS := -Daspectj.dir=$(ASPECTJ_DIR) \
	       -Dbuild.dir=$(BLD_DIR_JOBSUB) \
	       -Dhadoop.home=$(HADOOP_HOME)
$(JOBSUB): $(shell find $(JOBSUB_JAVA_DIR))
	@echo "--- Building Desktop jobsub"
	cd $(JOBSUB_JAVA_DIR) && ant $(ANT_OPTS) $(JOBSUB_OPTS) jar
	@mkdir -p $(JOBSUB_JAVA_LIB)
	@cp $(BLD_DIR_JOBSUB)/*.jar $@
else
$(JOBSUB):
	$(error Cannot build jobsub java without java source)
endif

#
# Tell the `bdist' target to exclude our java source.
#
BDIST_EXCLUDES += \
	--exclude=src/jobsub/java
