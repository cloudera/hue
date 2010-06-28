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
description: Sets up all inputs with the css class .overtext to have an OverText instance for inline labeling. The OverText label element inherits all the classes assigned to the input (at run time) with an "OverText-" prefix, allowing you to style OverText labels on a per-input basis.
provides: [CCS.JFrame.OverText]
requires: [/CCS.JFrame, More/OverText]
script: CCS.JFrame.OverText.js

...
*/

CCS.JFrame.addGlobalFilters({

	overText: function(container){
		//get all input.overtext elements and make an OverText for them.
		var ots = container.getElements('input.overtext, textarea.overtext').map(function(input){
			var ot = new OverText(input);
			input.get('class').split(' ').each(function(cls) {
				ot.text.addClass('OverText-'+cls);
			});
			return ot;
		});
		var updater = function(){
			(function(){
				ots.each(function(ot) {
					ot.reposition();
				});
			}).delay(10);
		};
		this.addEvent('loadComplete', updater);
		var win = this.getWindow();
		if (win) win.addEvent('unshade', updater);
		this.markForCleanup(function(){
			this.removeEvent('loadComplete', updater);
			if (win) win.removeEvent('unshade', updater);
		}.bind(this));
	}

});