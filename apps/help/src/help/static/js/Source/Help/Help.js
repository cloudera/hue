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
description: Help Application
provides: [Help]
requires: [JFrame/JFrame.Browser]
script: Help.js
...
*/
var Help = new Class({

	Extends: Hue.JBrowser,

	options: {
		className: 'art browser hue-help',
		historyOptions: {
			editable: false
		},
		windowTitler: function(title) {
			return "Help - " + title;
		}
	},

	initialize: function(path, options) {
		this.parent(path || '/help/', options);

		this.history.setOptions({
			pathFilter: function(path) {
				if (!path) return '';
				return path.replace('/help/', '');
			}
		});
		if (!Hue.Desktop.helpInstance || Hue.Desktop.helpInstance.isDestroyed()) Hue.Desktop.helpInstance = this;
	}
});
