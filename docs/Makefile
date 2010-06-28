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

export ROOT := $(realpath ..)
include $(ROOT)/Makefile.vars.priv

.PHONY: default docs

default: docs
docs: $(BLD_DIR_DOC)

# Option for a2x
NO_TOC := --xsltproc-opts='--stringparam generate.toc ""'

#
# Being lazy/loose with the prerequsite. Include all files except sdk, which is
# handled separately below.
#
$(BLD_DIR_DOC): $(BLD_DIR_DOC)/sdk $(shell find . -name sdk -prune -o -print)
	@echo '--- Generating doc at $@'
	@mkdir -p $@

	@a2x $(NO_TOC) --icons --icons-dir=images --format=xhtml --stylesheet=docbook.css -D $@ index.txt
	@a2x --asciidoc-opts="-a toc.max.depth=4" --format=xhtml --icons --icons-dir=images --stylesheet=docbook.css -D $@ manual.txt
	@rm -f {index,manual}.xml

	@cp docbook.css $@
	@cp *.repo $@
	@# Remove intermediate file
	@rsync -a images $@/
	@cp -r release-notes $@/


$(BLD_DIR_DOC)/sdk: $(shell find sdk)
	@echo '--- Generating sdk doc at $@'
	@mkdir -p $@
	@cp sdk/*.png $@
	@cp docbook.css $@
	@# This is somewhat heinous, but works fine and avoids the need
	@# to install markdown on developer systems, or depend on building
	@# out the virtual env to build sdk docs
	@PYTHONPATH=$(DESKTOP_DIR)/core/ext-py/markdown \
	  $(DESKTOP_DIR)/core/ext-py/markdown/bin/markdown \
	  sdk/sdk.md -x toc > $@/sdk.html
	@echo "--- Generated $@/sdk.html"

clean:
	@echo '--- Removing $(BLD_DIR_DOC)'
	@rm -rf $(BLD_DIR_DOC)
