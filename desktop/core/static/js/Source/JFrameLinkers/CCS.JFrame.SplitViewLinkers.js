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
description: Handles the resize linkers for the SplitView behavior.
provides: [CCS.JFrame.SplitViewLinkers]
requires: [/CCS.JFrame]
script: CCS.JFrame.SplitViewLinkers.js

...
*/

(function(){

var getWidget = function(link) {
	var splitview = link.getParent('.splitview');
	if (!splitview) return;
	return splitview.get('widget');
};
CCS.JFrame.addGlobalLinkers({

	'[data-splitview-resize]': function(e, link){
		if ($(e.target).get('tag') == 'a') e.preventDefault();
		var widget = getWidget(link);
		if (!widget) return;
		var resize = link.get('data', 'splitview-resize', true);
		if (!resize) return;
		var side;
		var sides = ['left', 'right', 'top', 'bottom'];
		for (key in resize) {
			if (sides.contains(key)) side = key;
		}
		widget.fold(side, resize[side], resize.hideSplitter).chain(partialPostFold.bind(this, [resize, e, link]));
	},

	'[data-splitview-toggle]': function(e, link){
		if ($(e.target).get('tag') == 'a') e.preventDefault();
		var widget = getWidget(link);
		if (!widget) return;
		var resize = link.get('data', 'splitview-toggle', true);
		if (!resize) return;
		widget.toggle(resize.side, resize.hideSplitter).chain(partialPostFold.bind(this, [resize, e, link]));
	}

});

var partialPostFold = function(data, event, link){
	if (!$(document.body).hasChild(link)) return;
	if (data.partialRefresh) {
		if ($type(data.partialRefresh) == "string") link = new Element('a', { href: data.partialRefresh });
		this.invokeLinker('.ccs-fake_refresh', link, event);
	}
};

})();