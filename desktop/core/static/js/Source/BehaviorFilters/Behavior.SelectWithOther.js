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
                //get the 'other' input
                var other = element.getElement('input').set('alt', 'Enter a custom value').addClass('required').addDataFilter('OverText').hide();
                //create hint text
                var ot = new OverText(other);
                //get the select input
                var sel = element.getElement('select');
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
                                other.addClass('ignoreValidation').dissolve();
                        }
                });
                this.markForCleanup(element, function(){
                        ot.destroy();
                });
	}
});
