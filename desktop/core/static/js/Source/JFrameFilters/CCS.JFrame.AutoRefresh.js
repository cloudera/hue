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
description: An auto refresh filter for Jframe keyed on the meta-refresh tag.
provides: [CCS.JFrame.AutoRefresh]
requires: [/CCS.JFrame, More/Date, More/Table]
script: CCS.JFrame.AutoRefresh.js

...
*/

(function(){
var urlRE = /^url=/;

CCS.JFrame.addGlobalFilters({

	autorefresh: function(container, content){
		$clear(refreshTable.get(this));
		//get the first input.autorefresh and use its value as the duration before
		//it auto refreshes the input. if span.sec_to_autorefresh is present, fill its
		//contents with the number of seconds until a refresh.
		var ignoreAutoRefresh = content && content.options && content.options.ignoreAutoRefresh;
		if (!ignoreAutoRefresh && content && content.meta) setupAutoRefresh.call(this, content);
	}

});

//given the content object from the filter handler, set up an auto refresher if the meta tag
//for it is present
var setupAutoRefresh = function(content) {
	var sec, url;
	//get the meta tags from the content and check them for a refresh tag
	content.meta.each(function(meta) {
		var parts = meta.get('content').split(';');
		if(meta.get('http-equiv') == "refresh") {
			sec = parts[0].toInt();
			if (parts[1]) url = unescape(parts[1].replace(urlRE, ''));
		}
	}, this);
	//if there's no refresh variable, exit
	if (!sec) return;
	//determin the timestamp for when we should refresh
	var end = new Date().increment('second', sec);
	var until, diff, span;
	//this method updates the DOM when the counter decrements
	var update = function() {
		span = $(this).getElement('span.sec_to_autorefresh');
		diff = ((end - new Date()) / Date.units['second']());
		until = diff.toInt();
		if (span) span.set('html', until);
	}.bind(this);
	update();

	//this method compares to urls to see if they match
	var compareURI = function(one, two) {
		return new URI(one).toString() == new URI(two).toString();
	};

	//this method checks a request to see if it's been spoiled
	//with the ajax linkers and the live url, it's possible that
	//the user clicked a link that updated the url for this frame
	//while a request was running
	var requestChecker = function(text, request, options) {
		var valid = compareURI(options.url, url ? url : this.currentPath);
		if (!valid) load();
		return valid;
	}.bind(this);

	//this method refreshs the frame either with the url from the meta
	//tag or from the current path
	var load = function(){
		if (url && url != unescape(this.currentPath)) {
			this.load({
				requestPath: url,
				autorefreshed: true,
				requestChecker: requestChecker
			});
		} else {
			this.refresh({ autorefreshed: true, requestChecker: requestChecker });
		}
	}.bind(this);

	//this timer goes off ever .25 seconds and checks to see if we've reached our
	//target refresh time
	var timer = (function(){
		if (diff < 1) {
			if (span) span.set('html', 0);
			load();
			$clear(timer);
		} else {
			update();
		}
	}).periodical(250, this);

	//this stores the timer in a universal table object.
	refreshTable.set(this, timer);

	//when a new request is generated (i.e. the user clicks a link, or refresh, or autorefresh)
	//check to see if the options for the request have the fullFrameLoad flag set to true; if not
	//restart our counter. For example, if a user does an AJAX request to update a dom (as we do
	//in the AjaxLoad jframe linker), that's still a request, but it's not a request for the entire
	//page so has no refresh handling of its own
	var clearer = function(requestPath, userData, options){
		if (!options.fullFrameLoad) {
			setupAutoRefresh.call(this, content);
		} else {
			$clear(timer);
			this.removeEvent('request', clearer);
		}
	};

	this.addEvent('request', clearer);
	this.markForCleanup(function(){
		$clear(timer);
	});
};

var refreshTable = new Table();

})();