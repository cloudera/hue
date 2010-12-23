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
description: Configures every form to use the Form.Request behavior.
provides: [CCS.JFrame.FormRequest]
requires: [/CCS.JFrame, More/Form.Request]
script: CCS.JFrame.FormRequest.js

...
*/

CCS.JFrame.addGlobalFilters({

	//this runs BEFORE Behavior.FormRequest
	formRequest: function(container){
		//get all forms in the response
		container.getElements('form').each(function(form){
			//set their action url and add the FormRequest filter
			if(form.get('action')){
				form.set('action', new URI(form.get('action'), {base: this.currentPath}));
			} else {
				form.set('action', new URI(this.currentPath));
				form.set('data', 'live-path', true);
			}
			form.addDataFilter("FormRequest");
		}, this);
	}

});

//this runs AFTER Behavior.FormRequest
Behavior.addGlobalPlugin('FormRequest', 'JFrameFormRequest', function(element, methods){
	//get the Form.Request instance
	var formRequest = element.get('formRequest');
	//tell it not to update anything
	formRequest.request.options.update = null;
	var options = {};
	['append', 'replace', 'target', 'after', 'before'].each(function(action){
		var selector = element.get('data', 'ajax-' + action);
		if (selector) {
			var target = methods.getContentElement().getElement(selector);
			if (target) {
				$extend(options, {
					target: target,
					spinnerTarget: target,
					noScroll: true,
					onlyProcessPartials: true,
					ignoreAutoRefresh: true,
					suppressLoadComplete: true,
					fullFrameLoad: false,
					retainPath: true
				});
			}
		}
	});
	//configure its request to use JFrame's response handler
	methods.configureRequest(formRequest.request, options);
	//if the element does not initially have an action, update its action to the new path, on livePathUpdate
	var pathUpdate = function(uri) {
		element.set('action', uri);
	};
	if (element.get('data', 'live-path')){
		methods.addEvent('livePathUpdate', pathUpdate);
	}
	formRequest.addEvent('send', function(form, query){
		formRequest.request.setOptions({
			formAction: form.get('action'),
			formData: query
		});
	});
	this.markForCleanup(element, function() {
		methods.removeEvent('livePathUpdate', pathUpdate);
	});
});
