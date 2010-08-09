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
description: Enables smooth scrolling for in-page anchors in SplitView.
provides: [Behavior.SplitViewScroller]
requires: [Widgets/Behavior.SplitView]
script: Behavior.SplitViewScroller.js
...
*/

Behavior.addGlobalPlugin('SplitView', 'SplitViewScroller', function(element, methods) {
	var splitview = element.retrieve('SplitView');
	var el = $(splitview);
	var sides = splitview.getSides();
	var tabAnchorScroller = function(e, link){
		var name = link.get('href').split('#')[1];
		var anchor = el.getElement('[name=' + name + ']');
		if (!anchor) {
			dbug.warn('warning, link name "%s" found no corresponding anchor', name);
			return;
		}
		var scrollSide;
		for (sideName in sides) {
			if (sides[sideName].hasChild(anchor)) scrollSide = sides[sideName];
		}
		if (scrollSide){
			var scroller = scrollSide.retrieve('_scroller');
			if (!scroller) {
				scroller = new Fx.Scroll(scrollSide);
				scrollSide.store('_scroller', scroller);
			}
			scroller.toElement(anchor);
			e.stop();
		}
	};
	el.addEvent('click:relay([href*=#])', tabAnchorScroller);
	this.markForCleanup(element, function(){
		el.removeEvent('click:relay([href*=#]', tabEnchorScroller);
	});
});
