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
description: Refreshes the current URL (including any GET parameters) with additional get parameters as specified.
provides: [CCS.JFrame.RefreshWithParams]
requires: [/CCS.JFrame]
script: CCS.JFrame.RefreshWithParams.js

...
*/

CCS.JFrame.addGlobalLinkers({
	/*
		submit the form that the element is in.
	*/
	'.ccs-refresh_with_params': function(event, link) {
		this.load({
			requestPath: new URI(this.currentPath).setData(String.parseQueryString(link.getData('refresh-params')), true).toString()
		});
	}

});