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
description: Displays an input field when the user chooses "other" in a select input.
provides: [CCS.JFrame.SelectWithOther]
requires: [/CCS.JFrame,More/Fx.Reveal,More/OverText]
script: CCS.JFrame.SelectWithOther.js
...
*/

CCS.JFrame.addGlobalFilters({
	select_with_other: function(container) {
		if (!container.get('html').contains('ccs-select-with-other')) return;
		container.getElements('.ccs-select-with-other').each(function(el) {
			//get the 'other' input
			var other = el.getElement('input').set('alt', 'Enter a custom value').addClass('overtext required');
			//create hint text
			var ot = new OverText(other);
			//get the select input
			var sel = el.getElement('select');
			//when the select changes, if the user chooses "other"
			//reveal the input, enable the overtext
			sel.addEvent('change', function() {
				if (sel.getSelected()[0].get('value') == '__other__') {
					other.removeClass('ignoreValidation').reveal().get('reveal').chain(function(){
						ot.enable();
					});
				//else hide and disable the input
				} else {
					ot.disable();
				}
			});
		});
	},
});
