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
description: Toggles the display of a group of elements when another is clicked or changed 
provides: [CCS.JFrame.DataGroupToggle]
requires: [/CCS.JFrame, /Element.Data]
script: CCS.JFrame.DataGroupToggle.js

...
*/

CCS.JFrame.addGlobalFilters({
	dataGroupToggle : function(container){
		if(!container.get('html').contains('ccs-group_toggle')) return;
		var toggles = container.getElements('.ccs-group_toggle');
		toggles.each(function(toggle) {
			if(toggle.tagName == 'SELECT') {
				toggle.addEvent('change', function(event) {
					var selected = toggle.getSelected()[0];
					var toggleData = selected.get('data', 'group-toggle', true);
					if(!toggleData) {
						dbug.warn("data-group-toggle either not present or unparseable.");
						return;
					}
					var sections = container.getElements(toggleData.group);
					if(!sections) {
						dbug.warn("Search using data-group-toggle[group] as selector returned no elements.");
						return;
					}
					var show = container.getElements(toggleData.show);
					if(!show) {
						dbug.warn("Search using data-group-toggle[show] as selector returned no elements.");
						return;
					}
					sections.each(function(section) {
						section.setStyle('display', show.contains(section) ? 'block' : 'none');
					});
				});
			} else {
				toggle.addEvent('click', function(event) {
					var toggleData = toggle.get('data', 'group-toggle', true);
					if(!toggleData) {
						dbug.warn("data-group-toggle either not present or unparseable.");
						return;
					} 
					var sections = container.getElements(toggleData.group);
					if(!sections) {
						dbug.warn("Search using data-group-toggle[group] as selector returned no elements.");
						return;
					}
					var show = container.getElements(toggleData.show);
					if(!show) {
						dbug.warn("search using data-group-toggle[show] as selector returned no elements.");
						return;
					}
					sections.each(function(section) {
						section.setStyle('display', show.contains(section) ? 'block' : 'none');
					});
				});
			}
		});
	}

});

