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

description: Makes any form with the data-filter SubmitOnChange submit itself whenever any input is changed.
provides: [Behavior.SubmitOnChange]
requires: [Widgets/Behavior]
script: Behavior.SubmitOnChange.js

...
*/

(function(){

var setupInput = function(input, form, cleanupElement){
	var events = {
		change: function(e){
			if (e) form.fireEvent('submit', e);
			else form.fireEvent('submit');
		},
		keydown: function(e) {
			if (e.key == 'enter' && document.id(e.target).get('tag') != 'textarea') form.fireEvent('submit', e);
		}
	};
	input.addEvents(events);
	this.markForCleanup(cleanupElement, function(){
		input.removeEvents(events);
	});
};

Behavior.addGlobalFilters({
	
	/*
		Notes:
		This filter doesn't really work as it should because the event delegation functionality in MooTools
		doesn't currently support events that don't bubble (change, submit, blur, focus, etc). Consequently
		this filter must select all the inputs and apply event listeners to them individually. This breaks
		the rule of behavior filters (which are supposed to alter the element the filter is applied to).
		The alternative is to add the SubmitOnChange filter to every input which I think is too onerous.
		The consequence here is that elements retired on the fly (inputs) won't have this behavior,
		but that's a terrible idea anyway (what if I'm filling out the form?). I'm going to leave it here for
		now.
	*/

	SubmitOnChange: function(element, methods) {
		if (['input', 'select', 'textarea'].contains(element.get('tag'))) {
			setupInput.call(this, element, element.getParent('form'), element);
		} else {
			element.getElements('input, select, textarea').each(function(el){
				setupInput.call(this, el, element, element);
			}, this);
		}
	}

});

})();