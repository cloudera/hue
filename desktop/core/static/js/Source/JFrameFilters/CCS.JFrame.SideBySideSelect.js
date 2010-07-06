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
description: Configures ART.SideBySideSelect instances for JFrame content.
provides: [CCS.JFrame.SideBySideSelect]
requires: [/CCS.JFrame, /ART.SideBySideSelect]
script: CCS.JFrame.SideBySideSelect.js

...
*/

CCS.JFrame.addGlobalFilters({

	side_by_side_select: function(container) {
		if (!container.get('html').contains('side_by_side_select')) return;
		//get the side by side containers
		return container.getElements('.side_by_side_select').map(function(select) {
			//if the element with the side_by_side class is the container of the select, get the 
			//select element within it.
			if (select && select.get('tag') != "select") select = select.getElement('select');
			dbug.warn('you are using a deprecated JFrame filter (side_by_side_select) on %o, use the SideBySideSelect data-filter instead.', select);
			select.addDataFilter('SideBySideSelect');
		}, this);
	}

});
