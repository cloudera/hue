/*
---
description: Any JFrame response that has a root-level child element with the class .partial_refresh will find all elements that have a property defined for data-partial-id that is unique to the response and only update them. If there is a mismatch in the response such that the number of and ids of partials in the previous state do not match the return state, an alert will be shown the user that the entire view will be updated that they can cancel, if they so choose. 
provides: [CCS.JFrame.PartialRefresh]
requires: [/CCS.JFrame, Widgets/ART.Alerts, More/Table, Widgets/Element.Data]
script: CCS.JFrame.PartialRefresh.js

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
(function(){

	var enableLog; //set to true if you want to log messages; left here for convenience.

	CCS.JFrame.addGlobalRenderers({

		partialRefresh: function(content){
			var options = content.options;
			//when we load content via ajax, we don't want the response being parsed for partials
			if (options && options.ignorePartialRefresh) return;
			var jState = getJState(this);
			//get the partial containers; containers that have elements in them to be partially refreshed
			var partialContainers = content.elements.filter('.partial_refresh');
			var setPrevPath = function(){
				jState.prevPath = options ? options.responsePath : null;
			};
			if (!partialContainers.length) {
				if (enableLog) dbug.log('no partials to refresh, exiting');
				//no partial containers, reset and fall through to other renderers
				setPrevPath();
				jState.partials = null;
				this.enableSpinnerUsage();
				return;
			}
			//get the partials in the containers
			var partials = getPartials(new Element('div').adopt(partialContainers), true);
			//if the options aren't defined or if we didn't auto refresh, reset and
			//return (fall through to other renderers)
			if (!options || !options.autorefreshed || 
					//or if the last time we loaded we stored partials but the url has changed
					//(i.e. a new page is loaded, this one also having partials)
					(jState.prevPath != options.responsePath && !options.forcePartial)) {
				//...then store the state and render as usual (fall through to other renderers)
				if (enableLog) dbug.log('not auto refreshed (%s), or new path (%s != %s) and not forced (%s), existing partial refresh after setup', !options.autorefreshed, jState.prevPath, options.responsePath, options.forcePartial);
				setPrevPath();
				jState.partials = partials;
				this.disableSpinnerUsage();
				return;
			}
			
			if (new URI(options.requestPath).toString() != new URI(options.responsePath).toString()) {
				if (enableLog) dbug.warn('detected partial refresh on a possible redirect (the request path != the response path), continuing with partial refresh');
			}
			setPrevPath();

			//don't show the spinner for partial refreshes
			this.disableSpinnerUsage();

			//check that the old partials are present in the new ones
			//and that all the new ones are present in the old ones
			//if not, store the new state and fall through to other renderers
			var checked = checkPartials(jState.partials, partials);
			if (checked.spoiled) {
				if (enableLog) dbug.log('checked partials spoiled, setup and return');
				//TODO tell the user that their state has spoiled and then update
				jState.partials = partials;
				//fall through to other renderers
				return;
			}
			
			/*******************************
			FORM HERE ON OUT
			this filter will handle the response; we return true and other renderers are excluded
			*******************************/
			
			//store the path as the current one
			this.currentPath = options.responsePath || this.currentPath;
			
			//if there's something to update...
			if (checked.update.length > 0) {
				//apply the JFrame filters to the response
				//but only to the elements require updating
				//this requires some foresight on how you apply the partials
				//if your partial contains a filter and that filter expects
				//the rest of the response to be around it, it's not going to be
				//only the children of each section marked as a partial can be relied upon
				//to be in this DOM structure when we apply the filters.
				var pElements = new Elements(checked.update.map(function(id){ return partials[id]; }));
				var target = new Element('div').adopt(pElements);
				content.elements = pElements;
				this.applyFilters(target, content);
				//get the partials from the target now that they've been set up with the filters
				partials = getPartials(target);
				//update the items that require it
				if (enableLog) dbug.log('updating partial refresh items (%s)', checked.update.length);
				checked.update.each(function(id){
					//replace the element
					partials[id].replaces(jState.partials[id]);
					//destroy the old one from memory (garbage collection)
					jState.partials[id].destroy();
					//update the pointer to the new one
					jState.partials[id] = partials[id];
				}, this);
			} else {
				//if we aren't updating anything, that's cool, but still call the autorefresh filter
				//to ensure that the frame keeps refreshing
				this.applyFilter('autorefresh', new Element('div'), content);
			}
			//prevent other renderers from handling the response
			return true;
		}

	});

	var jframeStates = new Table();

	//gets the state for the given jframe
	var getJState = function(jframe) {
		var jState = jframeStates.get(jframe);
		if (!jState) {
			jState = {};
			jframeStates.set(jframe, jState);
		}
		return jState;
	};

	//gets all the partial elements to refresh from the specified container
	//if *store* == true, then store this state on each element as the original,
	//unaltered response
	var getPartials = function(container, store) {
		if (!container.innerHTML.contains('data-partial-id')) return {};
		var partials = {};
		//get all the elements with a partial id
		container.getElements('[data-partial-id]').each(function(partial){
			//store a pointer to that element to return it
			partials[partial.get('data', 'partial-id')] = partial;
			//if instructed to, store the original state of the response before it was altered by any filter
			if (store) partial.store('partialRefresh:unaltered', partial.innerHTML);
		});
		return partials;
	};

	//checks two collections of partials to see if they are equal
	//that each group has the same number of partials
	//that the ids match up and, in addition, that the content 
	//returned has updated or not
	var checkPartials = function(partials1, partials2) {
		var keys = $H(partials1).getKeys();
		keys.combine($H(partials2).getKeys());
		
		var result = {
			update: [],
			spoiled: false
		};
	
		keys.every(function(key) {
			//get the partial from both sets
			var p1 = partials1[key],
					p2 = partials2[key];
			//if they are present
			if (p1 && p2) {
				//and their *original* html doesn't match, then mark it for update
				if (p1.retrieve('partialRefresh:unaltered') != p2.retrieve('partialRefresh:unaltered')) result.update.push(key);
				//continue looping
				return true;
			} else {
				//mismatch, the batch is spoiled, we reload the whole view
				result.spoiled = true;
				//break looping
				return false;
			}
		});
		return result;
	};

})();