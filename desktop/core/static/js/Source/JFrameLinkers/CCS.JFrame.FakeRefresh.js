/*
---
description: Loads a new url into the view but tells JFrame it's a refresh action rather than a normal load. This is only useful for forcing a partial refresh to a different url than the original.
provides: [CCS.JFrame.FakeRefresh]
requires: [/CCS.JFrame]
script: CCS.JFrame.FakeRefresh.js

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
	'.ccs-fake_refresh': function(event, link) {
		this.fireEvent('refresh');
		this.load({
			requestPath: new URI(link.get('href'), {base: this.currentPath}).toString(),
			autorefreshed: true,
			forcePartial: true
		});
	}

});
