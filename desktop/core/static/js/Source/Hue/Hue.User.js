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
description: Calls code with a user profile supplied.
provides: [Hue.User]
requires: [/Hue]
script: Hue.User.js

...
*/
(function(){
	// Lazily cached user profile data.
	var data = undefined;

	var outstandingRequest = undefined;
	Hue.User = {

		/**
		 * Call a callback on the user object. This is asynchronous
		 * because we may not be logged in yet, so this has to go
		 * and fetch the user profile from the server.
		 */
		withUser: function(callback) {
			if (data) {
				callback(data);
			} else {
				if (outstandingRequest) {
					outstandingRequest.addEvent('onSuccess', callback);
				} else {
					outstandingRequest = new Request.JSON({
						url: '/profile',
						onSuccess: function(user_data) {
							outstandingRequest = undefined;
							data = user_data;
							callback(data);
						}
					}).send();
				}
			}
		}
	};
})();
