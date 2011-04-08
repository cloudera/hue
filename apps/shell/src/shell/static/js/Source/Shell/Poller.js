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
description: I/O functionality shared between instances of the Shell app.
provides: [Poller]
requires: [hue-shared/Hue.Request]
script: Poller.js

...
*/

var hueInstanceID = function() {
	var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
	var lastIndex = chars.length - 1;
	var stringLength = 128;
	var randomString = "";
	for (var i = 0; i < stringLength; i++) {
		var randomIndex = $random(0, lastIndex);
		randomString += chars.substring(randomIndex, randomIndex+1);
	}
	return randomString;
}();

Poller = {
	initialize: function() {
		this.outputReq = new Request.JSON({
			method: 'post',
			url: '/shell/retrieve_output',
			onSuccess: this.outputReceived.bind(this),
			onFailure: this.outputRequestFailed.bind(this),
			headers: { "Hue-Instance-ID" : hueInstanceID }
		});
		this.addToOutputReq = new Request.JSON({
			method: 'post',
			url: '/shell/add_to_output',
			onSuccess: this.addToOutputCompleted.bind(this),
			onFailure: this.addToOutputFailed.bind(this),
			headers: { "Hue-Instance-ID" : hueInstanceID }
		});
		this.numAdditionalReqsSent = 0;
		this.additionalReqs = [];
		this.addToOutputReqOpen = false;
		this.requestOpen = false;
		this.initialized = true;
		this.requestsStopped = true;
		this.dispatchInfo = {};
		this.backoffTime = 1;
	},

	listenForShell: function(shellId, offset, callback) {
		// One-time initialization
		if (!this.initialized) {
			this.initialize();
		}

		// Register the dispatch information for this shell ID.
		this.dispatchInfo[shellId] = {callback:callback, offset:offset};

		// If an output request is already open, use the secondary channel to add the new shell and
		// offset to the existing output request.
		if (this.requestOpen) {
			this.addToOutputChannel(shellId, offset);
		}
		
		// We might be between openOutputChannel calls, so check to see if we've stopped
		// the requests or if we're just in between calls. If we've stopped, restart them.
		if (this.requestsStopped) {
			this.requestsStopped = false;
			this.openOutputChannel();
		}
	},
	
	// Remove the dispatch info for the given shell id. We don't have to do a request.cancel() since
	// either there's only 1 shell and we won't reissue once the request completes, or there are 
	// multiple and we might want to reissue.
	stopShellListener: function(shellId) {
		this.dispatchInfo[shellId] = null;
	},
	
	// Convert the information stored in this.dispatchInfo into the form that the backend speaks.
	serializeShellData: function() {
		var serializedShells = {};
		var numShells = 0;
		for (var shellId in this.dispatchInfo) {
			var shellInfo = this.dispatchInfo[shellId];
			if (shellInfo) {
				numShells++;
				serializedShells['shellId'+numShells] = shellId;
				serializedShells['offset'+numShells] = shellInfo.offset;
			}
		}
		serializedShells["numPairs"] = numShells;
		return serializedShells;
	},
	
	openOutputChannel: function() {
		this.requestOpen = true;
		var serializedData = this.serializeShellData();
		this.outputReq.send({ data: serializedData });
	},

	outputRequestFailed: function() {
		this.requestOpen = false;
		setTimeout(this.openOutputChannel.bind(this), this.backoffTime);
		this.backoffTime *= 2;
	},
	
	outputReceived: function(json, text) {
		this.requestOpen = false;
		this.backoffTime = 1;

		var closeOutputChannel = true; // Used to determine if we should issue a new output request.
		if (json.periodicResponse) {
			closeOutputChannel = false; // If it's just a "keep-alive", we should reissue.
		}
		
		// The object we got back has a dictionary for every shell ID. We loop through the keys in the object.
		for (var shellId in json) {
			var shellInfo = this.dispatchInfo[shellId];
			// For each key, see if we have any callbacks that are interested in that key. If not, then it
			// either isn't a shell ID (so it's something like "periodicResponse") or it's a shell ID that 
			// we no longer care about. That can occur when the user closes the instance of the shell app that
			// we made this output request for.
			if (shellInfo) {
				// Let's pull out the data for this shell.
				var result = json[shellId];
				// If it's alive, or it has exited, we might have to reissue an output request. We might reissue
				// if it's exited because there might be more output available.
				if (result.alive || result.exited) {
					//Let's update how far into the output stream we are.
					shellInfo.offset = result.nextOffset;
					// If it's not alive and no more output is available, then we stop listening for this shell.
					if (!(result.alive || result.moreOutputAvailable)) {
						this.stopShellListener(shellId);
					}
				} else {
					//If it's neither alive nor exited, then we're in some error state, so we definitely stop
					//listening for this shell
					this.stopShellListener(shellId);
				}
				// Since there was output this one time, let's call the callback with the result for this shell.
				shellInfo.callback(result);
			}
			
			// Now let's check if we still care about this shell. If not, we'll have called
			// stopShellListener on it and this.dispatchInfo[shellId] will be null.
			if (this.dispatchInfo[shellId]) { 
				closeOutputChannel = false; // We care still, so let's reissue an output req.
			}
		}

		if (closeOutputChannel) {
			//None of the shells in the response are still listening. Check to see if any other is.
			for (var shellId in this.dispatchInfo) {
				if (this.dispatchInfo[shellId]) {
					closeOutputChannel = false; // >=1 shells are listening, so let's reissue
				}
			}
		}

		if (!closeOutputChannel) {
			//can't use openOutputChannel.delay(0, this) here because it causes buggy behavior in Firefox.
			setTimeout(this.openOutputChannel.bind(this), 0);
		} else {
			// Let's set this flag to true so that we can reopen the channel on the next listener.
			this.requestsStopped = true;
		}
	},
	
	addToOutputChannel: function(shellId, offset) {
		// First let's store the info
		this.additionalReqs.push({shellId: shellId, offset: offset});
		this.sendAdditionalReq();
	},
	
	serializeAdditionalReqs: function() {
		// Convert the additional things we need to register into our output channel into the
		// same format as used for output requests.
		var serializedData = {}
		for (var i = 0; i < this.additionalReqs.length; i++) {
			serializedData["shellId" + (i+1)] = this.additionalReqs[i].shellId;
			serializedData["offset" + (i+1)] = this.additionalReqs[i].offset;
		}
		serializedData["numPairs"] = this.additionalReqs.length;
		return serializedData;
	},
	
	sendAdditionalReq: function() {
		this.addToOutputReqOpen = true;
		var serializedData = this.serializeAdditionalReqs();
		this.numAdditionalReqsSent = this.additionalReqs.length;
		this.addToOutputReq.send({ data: serializedData });
	},
	
	addToOutputCompleted: function(json, text) {
		this.backoffTime = 1;
		this.addToOutputReqOpen = false;
		if (json.success) {
			this.additionalReqs.splice(0, this.numAdditionalReqsSent);
			this.numAdditionalReqsSent = 0;
			if (this.additionalReqs.length) {
				this.sendAdditionalReq.delay(0, this);
				setTimeout(this.sendAdditionalReq.bind(this), 0);
			}
		} else if (json.restartHue) {
			alert("Your version of Hue is not up to date. Please restart your browser.");
		} else if (json.notRunningSpawning) {
			alert("The server is not running Spawning and cannot support the Shell app.");
		} else {
			this.numAdditionalReqsSent = 0;
			setTimeout(this.sendAdditionalReq.bind(this), 0);
		}
	},
	
	addToOutputFailed: function() {
		this.addToOutputReqOpen = false;
		this.numAdditionalReqsSent = 0;
		setTimeout(this.sendAdditionalReq.bind(this), this.backoffTime);
		this.backoffTime *= 2;
	}
};
