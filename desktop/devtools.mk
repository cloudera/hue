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
	ipdb[0.1dev-r1716] \
	ipython[0.10] \
	nose[0.11.3] \
	coverage[3.7.1] \
	nosetty[0.4] \
	werkzeug[0.6] \
	windmill[1.3] \
	pylint[0.28.0]

# Install/download dev tools for SDK into the virtual environment
.PHONY: $(DEVTOOLS)
$(DEVTOOLS):
	@echo "--- Installing development tool: $@"
	$(ENV_EASY_INSTALL) -f http://archive.cloudera.com/desktop-sdk-python-packages/ \
	   -H pypi.python.org,archive.cloudera.com $(SETUPTOOLS_OPTS) $(subst ],,$(subst [,==,$@))

$(BLD_DIR):
	@mkdir -p $@

$(BLD_DIR)/.devtools: $(BLD_DIR)
	@# If $(DEVTOOLS) are the prerequisites, we\'ll end up rebuilding them everytime.
	$(MAKE) $(DEVTOOLS)
	@touch $@
