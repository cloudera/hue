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
description: Displays an input field when the user chooses "other" in a select input in an element with "SelectWithOther" in its data-filters property.
provides: [Behavior.SelectWithOther]
requires: [Widgets/Behavior,More/Fx.Reveal,More/OverText]
script: Behavior.SelectWithOther.js
...
*/

Behavior.addGlobalFilters({
	SelectWithOther: function(element, methods) {
		//get the 'other' input / container
		var other = element.getElement(element.get('data', 'other-input') || 'input');
		var input = other;
		var otherOptions = element.getElements(element.get('data', 'other-options') || 'option[value=__other__]');
		//if the "other" element is not an input, it must be a container that contains one
		if (!['input', 'select', 'textarea'].contains(other.get('tag'))) input = other.getElement('input, textarea');
		other.hide();
		//get the select input
		var sel = element.getElement('select');
		//when the select changes, if the user chooses "other"
		//reveal the input, enable the overtext
		sel.addEvent('change', function() {
			var ot = input.retrieve('OverText');
			if (otherOptions.contains(sel.getSelected()[0])) {
				input.removeClass('ignoreValidation');
				if (ot) {
					other.get('reveal').chain(function(){
						ot.enable();
					});
				}
				other.reveal();
			//else hide and disable the input
			} else {
				if (ot) ot.disable();
				input.addClass('ignoreValidation');
				other.dissolve();
			}
		});
		if (ot) {
			this.markForCleanup(element, function(){
				ot.destroy();
			});
		}
	}
});
