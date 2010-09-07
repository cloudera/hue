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
description: Toggles the display of a group of elements when an element with DataGroupToggle in its data-filters property is clicked or changed 
provides: [Behavior.DataGroupToggle]
requires: [Widgets/Behavior, Widgets/Element.Data]
script: Behavior.DataGroupToggle.js

...
*/

Behavior.addGlobalFilters({
	DataGroupToggle: function(element, methods){
		container = methods.getContentElement();
		var selectHandler = function(event) {
			var selected = element.getSelected()[0];
			var toggleData = selected.get('data', 'group-toggle', true);
			if(!toggleData) {
				dbug.warn("data-group-toggle either not present or unparseable.");
				return;
			}
			var sections = container.getElements(toggleData.group);
			if(!sections.length) {
				dbug.warn("Search using data-group-toggle[group] as selector returned no elements.");
				return;
			}
			//If toggleData.show is undefined, then display none of the sections.
			var show = [];
			if(toggleData.show) show = container.getElements(toggleData.show);
			if(toggleData.show && !show.length) {
				dbug.warn("Search using data-group-toggle[show] as selector returned no elements.");
				return;
			}
			sections.each(function(section) {
				if(!show.contains(section)) {
					section.hide();
				} else if (!section.isDisplayed()) {
					section.show();
				}
			});
		};
		var linkHandler = function(event) {
			var toggleData = element.get('data', 'group-toggle', true);
			if(!toggleData) {
				dbug.warn("data-group-toggle either not present or unparseable.");
				return;
			} 
			var sections = container.getElements(toggleData.group);
			if(!sections.length) {
				dbug.warn("Search using data-group-toggle[group] as selector returned no elements.");
				return;
			}
			var show = container.getElements(toggleData.show);
			if(!show.length) {
				dbug.warn("search using data-group-toggle[show] as selector returned no elements.");
				return;
			}
			sections.each(function(section) {
				if(!show.contains(section)) {
					section.hide();
				} else if (!section.isDisplayed()) {
					section.show();
				}
			});
		};
		if(element.tagName == 'SELECT') {
			element.addEvent('change', selectHandler);
			selectHandler();
			this.markForCleanup(element, function(){
				element.removeEvent('change', selectHandler);
			});
		} else {
			element.addEvent('click', linkHandler);
			this.markForCleanup(element, function(){
				element.removeEvent('click', linkHandler);
			}); 
		}
	}

});

