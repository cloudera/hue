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
description: Job Designer (nee "JobSub")
provides: [Hue.JobSub]
requires: [JFrame/JFrame.Browser]
script: Hue.JobSub.js

...
*/
ART.Sheet.define('window.jobsub', {
	'min-width': 720
});

ART.Sheet.define('window.jobsub splitview', {
	'fixed-width': 180,
	'splitter-width': 1
});

Hue.JobSub = new Class({

	Extends: Hue.JBrowser,

	options: {
		className: 'art jobsub browser logo_header',
		displayHistory: false
	},

	initialize: function(path, options){
		this.parent(path || '/jobsub/list/', options);
	}

});
