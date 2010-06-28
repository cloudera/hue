/*
---
description: Makes links with .css-nav_back and .ccs-nav_next navigate forward and back.
provides: [CCS.JFrame.Nav]
requires: [/CCS.JFrame]
script: CCS.JFrame.Nav.js

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
	'.ccs-nav_next': function(event, link) {
		this.getWindow().history.forward();
	},

	'.ccs-nav_back': function(event, link) {
		this.getWindow().history.back();
	}

});