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


ifneq ($(PYTHON_VER),python2.7)
  # MAKEFILE_SDK = $(shell echo "")
  COMPILE = $(shell echo "")
  EXT_ENV_INSTALL = $(shell echo "")
else
  COMPILE = compile
  EXT_ENV_INSTALL = ext-env-install
endif

# The default RSYNC_OPT copies unsafe links. We don't want that because
# the symlink targets are always installed (separately). See HUE-565.
RSYNC_OPT := -a
include $(ROOT)/Makefile.sdk

default::
	@echo '  env-install    : Install into virtual-env'

#
# env-install
# 	Install app into the virtual environment.
#
.PHONY: env-install
env-install: $(COMPILE) $(EXT_ENV_INSTALL)
	@echo ">>>-----> env-install: $(APP_NAME)"
	@if [ "${PYTHON_VER}" != "python2.7" ]; then \
	    echo '--- Installing requirement.txt into virtual-env' via $(ENV_PIP) command. \
	    $(ENV_PIP) install -r requirements_py3.txt ;\
	    echo '--- Finished requirement.txt into virtual-env' \
	else \
	    echo '--- Installing $(APP_NAME) into virtual-env' \
	    $(ENV_PYTHON) setup.py develop -N -q ; \
	fi

