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
description: Instantiates a Collapsible class for all matched elements with .collapser and .collapsible css classes.
provides: [CCS.JFrame.Collapsible]
requires: [/CCS.JFrame, clientcide/Collapsible]
script: CCS.JFrame.Collapsible.js

...
*/

CCS.JFrame.addGlobalFilters({

	collapsible: function(container) {
		if (!container.get('html').contains('collapser')) return;
		//make collapsibles for each .collapser/.collapsible pair (kind of like accordion)
		var togglers = container.getElements('.collapser');
		var sections = container.getElements('.collapsible');
		if (togglers.length != sections.length) {
			dbug.warn('collapsible filter existing; togglers length (%s) != sections length (%s)', togglers.length, sections.length);
			return;
		}
		togglers.each(function(toggler, i) {
			new Collapsible(toggler, sections[i], {
				onComplete: function(){
					if (this.hidden) {
						toggler.set('html', toggler.get('html').replace('Hide', 'Show'));
					} else {
						toggler.set('html', toggler.get('html').replace('Show', 'Hide'));
						if (window.OverText) OverText.update();
					}
				}
			});
		});
	}

});