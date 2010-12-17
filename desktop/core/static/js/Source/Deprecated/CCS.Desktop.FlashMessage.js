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
description: Flash Messaging (notifications) for Desktop
provides: [CCS.Desktop.FlashMessage]
requires: [/Hue.Desktop, Core/Fx.Tween, Core/Fx.Transitions, JFrame/FlashMessage]
script: Hue.Desktop.FlashMessage.js

...
*/
/*
	flashMessage - displays a "growl" message for the user to read and dismiss
	message - (string) message to display to the user. can be html.
	duration - (integer) ms to delay hiding the message; defaults to 4500, cannot be less than 2000
	noCleanup - (boolean) don't clean the message up; relies on the caller to do with the returned function
	
	returns: a function that will hide the message when called. There is no consequence to calling it if the message
	  has already been cleaned (or calling it more than once).
*/
Hue.Desktop.flashMessage = function(message, duration, noCleanup){
	return FlashMessage.flash({
		message: message,
		duration: duration,
		noCleanup: noCleanup
	});
};
