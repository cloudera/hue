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

script: ${app_name_camel}.js

description: Defines ${app_name_camel}; a Hue application that extends Hue.JBrowser.

authors:
- Unknown

requires:
- JFrame/JFrame.Browser

provides: [${app_name_camel}]

...
*/
ART.Sheet.define('window.art.browser.${app_name}', {
	'min-width': 620
});

var ${app_name_camel} = new Class({

	Extends: Hue.JBrowser,

	options: {
		className: 'art browser logo_header ${app_name}'
	},

	initialize: function(path, options){
		this.parent(path || '/${app_name}/', options);
	}

});
