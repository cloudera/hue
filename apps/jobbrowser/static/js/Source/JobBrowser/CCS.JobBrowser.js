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
description: Job Browser core
provides: [CCS.JobBrowser]
requires: [ccs-shared/CCS.JBrowser, ccs-shared/CCS.JFrame.Tabs]
script: CCS.JobBrowser.js

...
*/
ART.Sheet.define('window.browser.jobbrowser', {
	'min-width': 620,
	'min-height': 108
});

CCS.JobBrowser = new Class({

	Extends: CCS.JBrowser,

	options: {
		className: 'art browser jobbrowser logo_header',
		height: 350
	},

	initialize: function(url, options){
		this.parent(url || '/jobbrowser/jobs/', options);
	}

});
