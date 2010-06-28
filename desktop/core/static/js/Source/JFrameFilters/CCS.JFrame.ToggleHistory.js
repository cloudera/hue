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
description: Shows or hides the history component from the widget.
provides: [CCS.JFrame.ToggleHistory]
requires: [/CCS.JFrame, Widgets/ART.History]
script: CCS.JFrame.ToggleHistory.js

...
*/

CCS.JFrame.addGlobalFilters({

	toggleHistory: function(container) {
		var win = this.getWindow();
		if (!win.history) return;
		var defaultState = this.getWindow().options.displayHistory;
		var history = win.history;
		var hiding = container.get('html').contains('ccs-hide_history');
		var showing = container.get('html').contains('ccs-show_history');
		if (showing || (defaultState && !hiding)) win.showHistory();
		else win.hideHistory();
	}

});