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
description: Behavior filter to filter elements based on the value of a text box with "FilterInput" in its data-filters property, when that text box is changed.
provides: [Behavior.FilterInput]
requires: [Widgets/Behavior, Widgets/Element.Data]
script: Behavior.FilterInput.js
...
*/

Behavior.addGlobalFilters({
	/*
		data-filter-elements: css selector for group of elements to filter against
		data-filter-parent: optional, css parent selector, from element, of element to hide/display
		TODO:  Deal with other types of data to filter relationships.  (sibling, child, etc.)
	*/

	FilterInput: function(element, methods){
		var container = methods.getContentElement();
		//this method will find all the elements and check them for the value
		var selector = element.get('data', 'filter-elements');
		if (!selector) {
			dbug.warn('warning, there was no selector defined for data-filter-elements for this element: ', element);
			return;
		}
		var filterParents = element.get('data', 'filter-parents');
		var filter = function (){
			var elements = container.getElements(selector);
			if (!elements.length) {
				dbug.warn('warning, this filter element %o has data-filter-elements selector defined as %s but this selector matches no elements.', element, selector);
				return;
			}
			var value = element.get('value').toLowerCase();
			var parents = new Table();
			elements.each(function(el){
				//if the filter value is empty, or the element contains the value
				var show = !value || el.get('html').toLowerCase().contains(value);
				//then show the parent:
				//get the parent or, if there is no parent defined, show/hide the element
				var parent = filterParents ? el.getParent(filterParents) : el;
				//if we haven't defined a value for this parent yet, then set it
				if (parents.get(parent) == undefined) parents.set(parent, show);
				//else, if we're showing set it to true
				else if (show) parents.set(parent, true);
			});
			//for each parent, check its state and show it
			parents.each(function(parent, show) {
				if(show) {
					display = "block";
					switch(parent.get('tag')){
						case "tr":
							display = "table-row";
							break;
						case "td":
							display = "table-cell";
							break;
						case "table":
							display = "table";
							break;
					}
					parent.show(display);
				} else {
					parent.hide();
				}
			});
		};
		var inputValue = element.get('value');
		//if there's a predefined value on startup, run the filter
		if (inputValue) filter();

		var fitEvent = function(){
			if (inputValue != element.get('value')){
				inputValue = element.get('value');
				filter();
			}
		};

		element.addEvent('change', fitEvent);
		this.markForCleanup(element, function(){
			element.removeEvent('change', fitEvent);
		});
	}
	
});
