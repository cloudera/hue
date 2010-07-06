// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/*
---
description: Automatically fits text to fit an element adding an elipse to the text using the FitText plugin for any elements with the .ccs-truncate class.
provides: [CCS.JFrame.FitText]
requires: [/CCS.JFrame, FitText/FitText, More/Array.Extras]
script: CCS.JFrame.FitText.js

...
*/

CCS.JFrame.addGlobalFilters({

	/*
		truncates text automatically for elements with the class .ccs-truncate
		elements cannot have child elements (only text)
	*/
	truncate: function(container) {
		if (!container.get('html').contains('ccs-truncate')) return;
		container.getElements('.ccs-truncate').each(function(el){
			dbug.warn('you are using a deprecated JFrame filter (truncate) on %o, use the FitText data-filter instead.', el);
			el.addDataFilter('FitText');
		}, this);
	},

	/*
		finds all elements wth data-fit-text properties - these properties must be selectors
		for the elements to apply the FitText class to.
	*/
	truncateChildren: function(container){
		if (!container.get('html').contains('data-fit-text')) return;
		container.getElements('[data-fit-text]').each(function(fitParent){
			if (!fitParent.hasDataFilter('FitText-Children')) {
				dbug.warn('you are using a deprecated JFrame filter (data-fit-text) on %o without the data-filter "FitText-Children".', fitParent);
				fitParent.addDataFilter('FitText-Children');
			}
		}, this);
	}

});
