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


# The default RSYNC_OPT copies unsafe links. We don't want that because
# the symlink targets are always installed (separately). See HUE-565.
RSYNC_OPT := -a
include $(ROOT)/Makefile.sdk

default::
	@echo '  env-install    : Install into virtual-env'
	@echo 'desktop/core/Makefile default EXT_ENV_INSTALL: $(EXT_ENV_INSTALL)'

#
# env-install
# 	Install app into the virtual environment.
#
.PHONY: env-install
env-install: $(EXT_ENV_INSTALL) compile
	@echo '--- Installing $(APP_NAME) into virtual-env'
	@echo '--- env-install: EXT_ENV_INSTALL: $(EXT_ENV_INSTALL)'
	@$(ENV_PYTHON) -m pip install -e .
