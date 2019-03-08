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
# Developer tools - this file is only included in SDK build.

# May require download from PyPI or whereever
DEVTOOLS += \
	ipython[7.3.0] \
	ipdb[0.11] \
	nose[1.3.7] \
	coverage[4.5.2] \
	nosetty[0.4] \
	werkzeug[0.14.1] \
    astroid[2.2.5] \
    isort[4.2.5] \
    six[1.12.0]

PYPI_MIRROR ?= https://pypi.python.org/simple/

# Install/download dev tools for SDK into the virtual environment
.PHONY: $(DEVTOOLS)
$(DEVTOOLS):
	@echo "--- Installing development tool: $@"
	$(ENV_EASY_INSTALL) -i $(PYPI_MIRROR) \
	   -H *.cloudera.com,pypi.python.org,files.pythonhosted.org $(SETUPTOOLS_OPTS) $(subst ],,$(subst [,==,$@))

$(BLD_DIR):
	@mkdir -p $@

$(BLD_DIR)/.devtools: $(BLD_DIR)
	@# If $(DEVTOOLS) are the prerequisites, we\'ll end up rebuilding them everytime.
	$(MAKE) $(DEVTOOLS)
	@touch $@
