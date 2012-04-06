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
# Being lazy/loose with the prerequsite. Include all files except sdk and
# release notes, which are handled separately below.
#
DOC_FILES := $(shell find . -name sdk -prune -o -name release-notes -o -print)
$(BLD_DIR_DOC): sdk release-notes $(DOC_FILES)
	@echo '--- Generating doc at $@'
	@mkdir -p $@

	@a2x $(NO_TOC) --icons --icons-dir=images --format=xhtml --stylesheet=docbook.css -D $@ index.txt
	@a2x --asciidoc-opts="-a toc.max.depth=4" --format=xhtml --icons --icons-dir=images --stylesheet=docbook.css -D $@ manual.txt
	@rm -f {index,manual}.xml

	@cp docbook.css $@
	@cp *.repo $@
	@# Remove intermediate file
	@rsync -a images $@/


.PHONY: release-notes
release-notes: $(BLD_DIR_DOC)/release-notes
$(BLD_DIR_DOC)/release-notes: $(wildcard release-notes/*.txt)
	@echo '--- Generating release notes at $@'
	@mkdir -p $@
	@for i in $? ; do asciidoc $$i ; done
	@mv release-notes/*.html $@/
	@echo "--- Generated $@"


.PHONY: sdk
sdk: $(BLD_DIR_DOC)/sdk/sdk.html
$(BLD_DIR_DOC)/sdk/sdk.html: $(shell find sdk -type f)
	@echo '--- Generating sdk doc at $@'
	@mkdir -p $(@D)
	@cp sdk/*.png $(@D)
	@cp docbook.css $(@D)
	@# This is somewhat heinous, but works fine and avoids the need
	@# to install markdown on developer systems, or depend on building
	@# out the virtual env to build sdk docs
	@PYTHONPATH=$(DESKTOP_DIR)/core/ext-py/markdown:$(DESKTOP_DIR)/core/ext-py/elementtree \
	  $(DESKTOP_DIR)/core/ext-py/markdown/bin/markdown \
	  sdk/sdk.md -x toc > $@
	@echo "--- Generated $@"


clean:
	@echo '--- Removing $(BLD_DIR_DOC)'
	@rm -rf $(BLD_DIR_DOC)
