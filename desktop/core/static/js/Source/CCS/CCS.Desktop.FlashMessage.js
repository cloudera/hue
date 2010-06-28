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
requires: [/CCS.Desktop, Core/Fx.Tween, Core/Fx.Transitions]
script: CCS.Desktop.FlashMessage.js

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
CCS.Desktop.flashMessages = [];
CCS.Desktop.flashMessage = function(message, duration, noCleanup){
	var b = 100; // offset for get satifaction 
	
	var growls = $$('.growl');
	if(growls.length){ // if growls already exist
		var bottom = growls[growls.length-1].getStyle('bottom').toInt();
		b = bottom + growls[growls.length-1].getSize().y + 12;
	}
	//store the message as displayed so we don't show dupes
	CCS.Desktop.flashMessages.push(message);
	var el, cleaned, cleanupCallbackCalledAlready, okToClean, timeout;
	//create a timeout for a minimum amount of time for a message to be displayed
	//if the cleanup method is called before this timeout, wait until the timer expires
	//to hide the message
	(function(){ 
		okToClean = true;
		if (cleanupCallbackCalledAlready) cleanup();
	}).delay(2000);
	//this function removes the message
	var cleanup = function(clicked){
		//if the user clicked the message, or the timer has expired,
		//then it's ok to clean up the message, otherwise defer to the timer
		if (!okToClean && !clicked) {
			cleanupCallbackCalledAlready = true;
			return;
		}
		//if we've already called this, break
		if (cleaned) return;
		cleaned = true;
		$clear(timeout);
		//slide the element out to the right, then destroy it and remove the message from the stack
		el.tween('right', -300).get('tween').chain(function(){
			CCS.Desktop.flashMessages.erase(message);
			el.destroy();
		});
	};
	//create the element and inject it into the DOM
	el = new Element('div',{
		'class': 'growl', 
		html: message,
		tween: {
			transition: 'back:in'
		},
		events: {
			click: cleanup
		},
		styles: {
			right : 0,
			bottom: b
		}
	}).inject(this.options.append);
	//set a timeout to hide the message
	timeout = cleanup.delay(duration || 4500);
	//return the cleanup function so that the code that called this method can optionally
	//clean it before the timeout.
	return cleanup;
};
CCS.Desktop.checkForFlashMessage = function(message) {
	return CCS.Desktop.flashMessages.contains(message);
};