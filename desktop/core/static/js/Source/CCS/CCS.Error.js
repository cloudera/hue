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
description: Error Dialog box
provides: [CCS.Error]
requires: [/CCS, Widgets/ART.Alerts]
script: CCS.Error.js

...
*/
CCS.error = function(caption, message){
	message = message || "unknown";
	if (['element', 'string'].contains($type(message))) {
		var alerter =  ART.alert(caption || 'Woops!', message || 'Something has gone horribly, horribly wrong.', function(){
			alerter.keyboard.relinquish();
		}, {
				width: 400,
				height: 150,
				mask: true
		}).inject(document.body);
		return alerter;
	} else {
		dbug.log('not alerting message, as it\'s not a string or element', caption, message);
	}
};
