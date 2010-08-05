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
description: Allows users to hold down shift to select multiple check boxes.
provides: [Behavior.MultiChecks]
requires: [Widgets/Behavior]
script: Behavior.MultiChecks.js
...
*/
(function(){
	var checkInput = function(input, checked) {
		input.set('checked', checked).fireEvent('change');
	};
	
	Behavior.addGlobalFilters({

		MultiChecks: function(element, events) {
			var prev;
			//this method handles clicks to our checkboxes
			var clickHandler = function(e, input){
				//if there's a previously clicked input and the shift button is held
				if (prev && e.shift) {
					var active, check;
					//get the state of the input, if it's checked, we're selecting things
					//otherwise we're deselecting them
					check = input.get('checked');
					//get all the checkboxes in the element
					element.getElements('input[type=checkbox]').each(function(el){
						//if it's the element we checked, or it's the previous one checked
						if (el == input || el == prev) {
							//then check it and toggle our start state
							checkInput(el, check);
							active = !active;
							return;
						}
						//if we're active, check the input
						if (active) checkInput(el, check);
					});
				}
				//store the clicked element as the new one.
				prev = input;
			};
			element.addEvent('click:relay(input[type=checkbox])', clickHandler);
			this.markForCleanup(element, function(){
				element.removeEvent('click:relay(input[type=checkbox])', clickHandler);
			});
		}

	});

})();
