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
description: Adds a tab interface (TabSwapper instance) for elements with .css-tab_ui. Matched with tab elements that are .tabs and sections that are .tab_sections.
provides: [Behavior.Tabs]
requires: [Widgets/Behavior, clientcide/TabSwapper]
script: Behavior.Tabs.js

...
*/

Behavior.addGlobalFilters({

	Tabs: function(element, methods) {
		var tabs = element.getElements(element.get('data', 'tabs-selector') || '.tabs>li');
		var sections = element.getElements(element.get('data', 'sections-selector') || '.tab_sections>li');
		if (tabs.length != sections.length || tabs.length == 0) {
			methods.error('warning; sections and sections are not of equal number. tabs: %o, sections: %o', tabs, sections);
			return;
		}
		var ts = new TabSwapper({
			tabs: tabs,
			sections: sections,
			smooth: true,
			smoothSize: true
		});
		element.store('TabSwapper', ts);
	}

});
