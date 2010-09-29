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
description: Provides functionality for links that load content into a target element via ajax.
provides: [CCS.JFrame.AjaxLoad]
requires: [/CCS.JFrame]
script: CCS.JFrame.AjaxLoad.js
...
*/

(function(){

	/*
		loads the contents of a link into a specific target
		* event - the event object from the link click
		* link - the link clicked
		
		notes:
		* links have properties for one of data-ajax-append, data-ajax-replace, and data-ajax-target
		* replace means destroy the target and replace it entirely with the response.
		* append means leave everything in place and inject the response after the target.
		* target means empty the target and fill it with the response
		* links with a "data-ajax-filter" property will inject only the elements that match the selector it specifies.
		  For example, if you have a table that you want to add rows to, and your request returns an HTML document that
		  includes an entire table, you would specify data-ajax-filter="table tbody tr" to only inject the rows from
		  the body in the response.
	*/

	var linkers = {};

	['append', 'replace', 'target', 'after', 'before'].each(function(action){

		linkers['[data-ajax-' + action + ']'] = function(event, link){
			var target = $(this).getElement(link.get('data', 'ajax-' + action));
			if (!target) {
				link.erase('data-ajax-' + action);
				dbug.log('could not ' + action + ' the target element with response; element matching selector %s was not found', link.get('data', 'ajax-' + action));
				this.callClick(event, link, true);
				return;
			}

			var requestTarget = target;
			if (action != 'target') requestTarget = new Element('div');

			var options = {
				filter: link.get('data', 'ajax-filter'),
				requestPath: link.get('href'),
				spinnerTarget: target,
				target: requestTarget,
				onlyProcessPartials: true,
				ignoreAutoRefresh: true,
				suppressLoadComplete: true,
				fullFrameLoad: false,
				retainPath: true,
				callback: function(data){
					switch(action){
						case 'replace':
							//reverse the elements and inject them
							//reversal is required since it injects each after the target
							//pushing down the previously added element
							data.elements.reverse().injectAfter(target);
							target.destroy();
							break;
						case 'append':
						case 'after':
							//see note above in 'replace' case as to why we use reverse here
							data.elements.reverse().injectAfter(target);
							break;
						case 'before':
							data.elements.reverse().injectBefore(target);
						//do nothing for update, as Request.HTML already does it for you
					}
					var state = {
						event: event,
						link: link,
						target: target,
						action: action
					};
					//pass along the data that came back from JFrame's response handler as well as the state of this ajax load.
					this.fireEvent('ajaxLoad', [data, state]);
					this.behavior.fireEvent('update', [data, state]);
				}.bind(this)
			};
			var spinnerTarget = link.get('data', 'spinner-target');
			if (spinnerTarget) {
				spinnerTarget = $(this).getElement(spinnerTarget);
				options.spinnerTarget = spinnerTarget;
			}

			this.load(options);
		};
	});
	CCS.JFrame.addGlobalLinkers(linkers);

})();