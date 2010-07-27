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
description: Allows an element to be sized to the dimensions of the jframe portion of the window.
provides: [Behavior.SizeTo]
requires: [Widgets/Element.Data]
script: Behavior.SizeTo.js

...
*/

Behavior.addGlobalFilters({

	/*
		elements are given data properties for data-size-to-height or data-size-to-width
		these values are offsets. So, for example:
		
			<div data-filters="SizeTo" data-size-to-height="-100"></div>
		
		will size that div to the height of the window -100 pixels. The value must always
		be a number. Use zero for 100% height/width.
	*/
	SizeTo: function(element, methods) {
		var sizeTo = {
			x: element.get('data', 'size-to-width'),
			y: element.get('data', 'size-to-height')
		};
		if (!sizeTo.x && !sizeTo.y) {
			dbug.log('this element has the SizeTo filter, but no sizes defined for size-to-height/width: ', element);
			return;
		}
		resize = function(x, y){
			if (sizeTo.x) element.setStyle('width', x + sizeTo.x.toInt());
			if (sizeTo.y) element.setStyle('height', y + sizeTo.y.toInt());
		};
		size = methods.getContainerSize();
		resize(size.x, size.y);
		methods.addEvent('resize', resize);
		this.markForCleanup(element, function(){
			methods.removeEvent('resize', resize);
		});
	}

});
