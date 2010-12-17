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
description: User Admin
provides: [Hue.UserAdmin]
requires: [JFrame/JFrame.Browser]
script: Hue.UserAdmin.js

...
*/

UI.Sheet.define('window.art.browser.useradmin', {
	'header-height': 70,
	'header-overflow': 'visible',
	'min-width': 700
});

ART.Sheet.define('window.useradmin history.browser', {
	'top':32,
	'padding': '0 8px 0 60px'
});

ART.Sheet.define('window.useradmin history input', {
	'left': 66
});

ART.Sheet.define('window.useradmin history input.disabled', {
	'left': 66
});


Hue.UserAdmin = new Class({

	Extends: Hue.JBrowser,

	options: {
		className: 'art browser logo_header useradmin',
		jframeOptions: {
			clickRelays: 'a, .relays'
		}
	}
});
