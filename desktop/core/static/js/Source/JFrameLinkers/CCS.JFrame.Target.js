/*
---
description: Takes any link with a target specified and, if that target matches an app name, launches that app with the link's url as the argument, otherwise it opens a new window/tab with that url.
provides: [CCS.JFrame.Target]
requires: [/CCS.JFrame]
script: CCS.JFrame.Target.js

...
*/
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
CCS.JFrame.addGlobalLinkers({

	//any link with a target value launches the app named as the target if there is one
	//else opens new browser window/tab
	'a[target]': function(event, link) {
		var target = link.get('target');
		if (target != "_blank" && CCS.Desktop.hasApp(target)) CCS.Desktop.launch(target, link.get('href'));
		else window.open(link.get('href'), target);
	}

});