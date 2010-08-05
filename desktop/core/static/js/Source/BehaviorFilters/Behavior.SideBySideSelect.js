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
description: Automatically turns multi select inputs into an instance of ART.SideBySideSelect.
provides: [Behavior.SideBySideSelect]
requires: [Widgets/Behavior, /ART.SideBySideSelect]
script: Behavior.SideBySideSelect.js
...
*/

Behavior.addGlobalFilters({

	SideBySideSelect: function(element, events) {
		if (element.get('tag') != 'select' && element.get('multiple')){
			dbug.warn("Side_by_side_select element %o does not contain multiple=true.", element);
			return;
		}
		var parent = element.get('parentWidget');
		var sbs = new ART.SideBySideSelect(element);

		//inject our new widget into the DOM and the widget tree (if there is a parent widget)
		if (parent) sbs.inject(parent, element, 'after');
		else widget.inject(element, element, 'after');

		this.markForCleanup(element, function(){
			sbs.destroy();
		});
	}

});
