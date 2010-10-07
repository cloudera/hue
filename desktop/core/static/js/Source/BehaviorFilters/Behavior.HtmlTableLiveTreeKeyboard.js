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
description: Adds keyboard support for live loading trees - integrates key navigation with the livepath linker.
provides: [Behavior.HtmlTableLiveTreeKeyboard]
requires: [Widgets/Behavior.HtmlTable]
script: Behavior.HtmlTableLiveTreeKeyboard.js
...
*/
(function(){

var checkLinkerForLivePath = function(anchor, methods){
	['[data-livepath-toggle]', '[data-livepath-add]', '[data-livepath-replace]'].some(function(selector){
		if (anchor.match(selector)) {
			methods.invokeLinker(selector, anchor, { stop: $empty, preventDefault: $empty, stopPropagation: $empty});
			return true;
		}
	});
};

Behavior.addGlobalPlugin('HtmlTable', 'HtmlTableLiveTreeKeyboard', function(element, methods){
	if (!element.hasClass('treeView')) return;
	var table = element.retrieve('HtmlTable');
	table.addEvent('onHideRow', function(row){
		if (row.get('data-partial-line-id')) row.destroy();
	});
	table.addEvent('expandSection', function(row){
		var anchor = row.getElement('.expand');
		if (anchor) methods.callClick({ stop: $empty, preventDefault: $empty, stopPropagation: $empty}, anchor, true);
	}.bind(this));
	table.addEvent('closeSection', function(row){
		var anchor = row.getElement('.expand');
		if (anchor) checkLinkerForLivePath(anchor, methods);
	});
	$(table).addEvent('click:relay(.expand)', function(event, link){
		event.stop();
	});
});

})();