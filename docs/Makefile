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
# Being lazy/loose with the prerequisite. Include all files except sdk and
# release notes, which are handled separately below.
#
DOC_FILES := $(shell find . -name sdk -prune -o -name release-notes -name user-guide -name admin-manual -o -print)
$(BLD_DIR_DOC): sdk release-notes user-guide admin-manual $(DOC_FILES)
	@echo '--- Generating doc at $@'
	@mkdir -p $@

	@a2x $(NO_TOC) --icons --icons-dir=images --format=xhtml --stylesheet=css/docbook.css -D $@ index.txt
	@rm -f index.xml

	@cp images/favicon.ico $@
	@# Remove intermediate file
	@rsync -a images $@/
	@rsync -a js $@/
	@rsync -a css $@/
	@rsync -a fonts $@/


.PHONY: release-notes
release-notes: $(BLD_DIR_DOC)/release-notes
$(BLD_DIR_DOC)/release-notes: $(wildcard release-notes/*.txt)
	@echo '--- Generating release notes at $@'
	@mkdir -p $@
	@cp css/docbook.css release-notes/
	@for i in $? ; do \
	  a2x $(NO_TOC) --format=xhtml --stylesheet=docbook.css $$i ; \
	  rm -f $$i.xml ; \
	done;
	@mv release-notes/docbook.css $@/
	@mv release-notes/*.html $@/
	@echo "--- Generated $@"


.PHONY: admin-manual
admin-manual: $(BLD_DIR_DOC)/admin-manual
$(BLD_DIR_DOC)/admin-manual: $(wildcard admin-manual/*.md)
	@echo '--- Generating admin-manual doc at $@'
	@mkdir -p $@
	@PYTHONPATH=$(DESKTOP_DIR)/core/ext-py/markdown:$(DESKTOP_DIR)/core/ext-py/elementtree \
	  $(DESKTOP_DIR)/core/ext-py/markdown/bin/markdown \
	  admin-manual/manual.md -x toc > $@/manual.html
	@echo "--- Generated $@"


.PHONY: user-guide
user-guide: $(BLD_DIR_DOC)/user-guide
$(BLD_DIR_DOC)/user-guide: $(wildcard user-guide/*.md)
	@echo '--- Generating user-guide doc at $@'
	@mkdir -p $@
	@cp -r user-guide/images $@
	@for x in $? ; do PYTHONPATH=$(DESKTOP_DIR)/core/ext-py/markdown:$(DESKTOP_DIR)/core/ext-py/elementtree \
	  $(DESKTOP_DIR)/core/ext-py/markdown/bin/markdown \
	  $$x > $(BLD_DIR_DOC)/$$x -x toc ; done
	@(cd $@; for file in *.md; do mv $${file} $${file/\.md/.html}; done)
	@echo "--- Generated $@"


.PHONY: sdk
sdk: $(BLD_DIR_DOC)/sdk/sdk.html
$(BLD_DIR_DOC)/sdk/sdk.html: $(shell find sdk -type f)
	@echo '--- Generating sdk doc at $@'
	@mkdir -p $(@D)
	@cp sdk/*.png $(@D)
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
