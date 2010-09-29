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

		/*
			Partials are comprised of instructions in HTML responses that mark areas of the document that should be
			compaired against previous responses. These areas's raw HTML (the HTML returned from the server, not the
			current DOM state, which may have classes or style attributes or even new DOM elements in place) is compared
			to the previous response. When there's a mis-match in the response, only those elements that have changed
			are run through the JFrame filters to configure them for display and then replace their expired counterparts.

			Each area that may have elements that should be checked is identified with the class "partial_refresh" on some
			container; often a div wrapping the entire response.

			Each individual item that might be refreshed must be marked with a data-partial-id property that is unique
			to the JFrame (i.e. multiple app windows can have id overlap).

			If you need to support the loading of additional content after the fact, such as with loading additional Ajax
			elements within the frame or if the response may return more or fewer items than the previous response, then
			you must add some additional instrumentation to your HTML. Specifically, you *must* define a container where
			new elements are injected. This is typically the immediate parent of the partials, like so:

			Example w/ just partials and container
			<div data-partial-container-id="div1">
				<p data-partial-id="p1">foo</p>
				<p data-partial-id="p2">bar</p>
			</div>

			In some cases, such as with tables, you may wish to add "lines" between the partials and the container. A good
			example here is a table which has partials for individual td elements, but new tr elements may come and go.

			Example w/ partials, container, and lines
			<tbody data-partial-container-id="tbody1">
				<tr data-partial-line-id="tr1">
					<td data-partial-id="id1"></td>
					<td data-partial-id="id2"></td>
				</tr>
			</tbody>

			When the above markup is used, new partials may appear (the tds) and the parent element with the data-partial-line-id
			will be used for injection instead. Note that this id, and the container id, must also be unique to the frame.

			Both lines and partials will be injected in their relative position; i.e. if in the above example our response returned
			a new tr line afer tr1, the new row would be found in the response, the reponse's DOM tree would be inspected and
			the previous row would be found there. It's id is "tr1". The *live* DOM tree - the one the user sees - would be searched
			for an element with that line-id. The new line would be injected after it.

			When using ajax to load in new content (such as with the AjaxLoad linker) you'll likely load new content in ouside
			the scope of this refresh handler. I.e. you'll handle the response and inject the new items yourself. In this case
			partial refresh needs only to store the original request state for future checksums. To accomplish this, set the
			options of the request to have the onlyProcessPartials flag set to true. This will run the ajax response through
			this renderer, find the new partial elements, and store their initial state for checking later.

		*/

		partialRefresh: function(content){
			var options = content.options || {};
			//if the request options include the ignorePartialRequest flag, exit
			if (options.ignorePartialRefresh) return;
			//when we load content via ajax, we don't want the response being parsed for partials
			var jState = getJState(this);
			//get the partial containers; containers that have elements in them to be partially refreshed
			var partialContainers = new Element('div').adopt(content.elements).getElements('.partial_refresh');

			//for requests that want to handle the element injection themselves (ajaxload, for example)
			//they can instruct this filter to process the partials in the response and then exit
			if (options.onlyProcessPartials) {
				processPartials(content, jState);
				return;
			}
			//store the previous path to be the current one
			jState.prevPath = options ? options.responsePath : null;

			if (!partialContainers.length) {
				if (enableLog) dbug.log('no partials to refresh, exiting');
				//no partial containers, reset and fall through to other renderers
				jState.partials = null;
				this.enableSpinnerUsage();
				return;
			}
			//get the partials in the containers
			var partials = getPartials(new Element('div').adopt(partialContainers), true);
			//if the options aren't defined or if we didn't auto refresh, reset and
			//return (fall through to other renderers)
			if (!options || !(options.autorefreshed || options.forcePartial)) {
				//...then store the state and render as usual (fall through to other renderers)
				if (enableLog) dbug.log('not auto refreshed (%s), or new path (%s != %s) and not forced (%s), existing partial refresh after setup', !options.autorefreshed, jState.prevPath, options.responsePath, options.forcePartial);
				jState.partials = partials;
				this.disableSpinnerUsage();
				return;
			}

			if (new URI(options.requestPath).toString() != new URI(options.responsePath).toString()) {
				if (enableLog) dbug.warn('detected partial refresh on a possible redirect (the request path (%s) != the response path (%s)), continuing with partial refresh', new URI(options.requestPath).toString(), new URI(options.responsePath).toString());
			}

			//don't show the spinner for partial refreshes
			this.disableSpinnerUsage();

			/*******************************
			FORM HERE ON OUT
			this filter will handle the response; we return true and other renderers are excluded
			UNLESS there is a partial returned that we cannot find the proper place to put it
			(i.e. it has no partial-container).
			*******************************/
			if (enableLog) dbug.log('proceeding with partial refresh');
			//store the path as the current one
			this.currentPath = options.responsePath || this.currentPath;

			var checkedPartials = checkPartials(partials, jState);

			//render the content
			if (!checkedPartials.renderedPartials.length) {
				if (enableLog) dbug.log('no partials for render; exiting quietly');
				//if we aren't updating anything, that's cool, but still call the autorefresh filter
				//to ensure that the frame keeps refreshing
				this.applyFilter('autorefresh', new Element('div'), content);
				//if there is no new content, return true (so no other renderers are called)
				return true;
			}

			//apply all the jframe magic to our filtered content
			if (enableLog) dbug.log('applying filters');
			//filters expect to be handed an object (content) that has various properties of the
			//response; the meta tags, the script tags, and elements that were in the body, etc.
			//because we want to run the elements we're updating through the filters, we overwrite
			//the elements that were passed in to this renderer with only the elements we want
			//updated and then apply the filters.
			content.elements = checkedPartials.renderedPartials;
			this.applyFilters(checkedPartials.target, content);

			//now loop through the partials again and inject them into the DOM structure from the response
			//replacing the original partial with the cloned one
			restorePartials(checkedPartials.partialClones, partials);

			var success = injectPartials(partials, jState, checkedPartials.renderedIds, this.behavior, $(this));
			if (!success) return;

			cleanRemainingParitals(partials, jState, this.behavior);

			//we've updated the display, so tell filters that are waiting that they may need to update their display, too
			this.behavior.fireEvent('show');
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
		return $H(partials);
	};

	var processPartials = function(content, jState){
		var toProcess = getPartials(new Element('div').adopt(content.elements), true);
		//if there are partials already, merge the result
		if (jState.partials) {
			toProcess.each(function(partial, id){
				jState.partials[id] = partial;
			});
		//else there were no partials in the previous response; so assign these.
		} else {
			jState.partials = toProcess;
		}
	};

	var checkPartials = function(partials, jState){
		var data = {
			renderedIds: {},
			renderedPartials: new Elements(),
			partialClones: {},
			target: new Element('div')
		};
		//loop through the partials and figure out which ones need updating so that we can 
		//run only those through the filters
		partials.each(function(partial, id) {
			if (enableLog) dbug.log('considering %s for update', id);
			//get the corresponding element in the dom
			var before = jState.partials[id];
			//if there isn't one, or thier raw html don't match, we'll update it, so we must render it
			if (!before || !compare(before, partial)) {
				if (enableLog) dbug.log('preparing %s for update', id);
				//we must preserve the DOM structure to be able to find partial containers and partial lines
				//so clone the partial for rendering
				var clone = partial.clone(true, true);
				data.target.adopt(clone);
				//we need an array of these elements for when we call applyFilters below, which expects
				//content.elements to be an array of the elements returned in the response
				data.renderedPartials.push(clone);
				data.renderedIds[id] = true;
				//we also need a key/value map of all the clones for quick lookups when we put them back
				//into the response DOM
				data.partialClones[id] = clone;
			}
		});
		return data;
	};

	//given a partial, attempts to find the line it is in
	//example: for a td that is a partial, it may have the tr as its line
	var getPartialLine = function(partial){
		return partial.getParent('[data-partial-line-id]');
	};
	//given a partial, attempts to find the container it is in
	//for example, for a td that is a partial, it may have the tr as its line and the table as its container
	var getPartialContainers = function(partial, container){
		var containers = {
			container: partial.getParent('[data-partial-container-id]')
		};
		if (containers.container) {
			containers.DOMcontainer = container.getElement('[data-partial-container-id=' + 
			  containers.container.get('data', 'partial-container-id') + ']');
		}
		return containers;
	};

	//given two partials, compares their raw HTML before they were parsed by filters
	var compare = function(before, after){
		return before.retrieve('partialRefresh:unaltered') == after.retrieve('partialRefresh:unaltered');
	};

	//this method destroys a partial given its partial id
	var destroyPartial = function(id, jState, behavior){
		//get the element
		var element = jState.partials[id];
		//clean up its behaviors
		behavior.cleanup(element);
		//destroy the element
		element.destroy();
		//delete it from the jState
		delete jState.partials[id];
	};

	//this method takes a group of cloned partials (that have been passed through filters)
	//and puts them back into the DOM from which they came, replacing the elements they
	//were cloned from. This allows us to retain the DOM structure of the response, while
	//only running through the filters the elements that need it.
	var restorePartials = function(clones, partials){
		for (id in clones) {
			if (enableLog) dbug.log('replacing target with clone: ', id);
			var clone = clones[id],
			    partial = partials[id];
			//because we're replacing, we need to copy over thier original HTML state for the checksum
			clone.store('partialRefresh:unaltered', partial.retrieve('partialRefresh:unaltered'));
			clone.replaces(partial);
			//and then update the pointer as the clone is now the rendered partial
			partials[id] = clone;
		}
	};

	var injectPartials = function(partials, jState, rendered, behavior, container) {
		var insertedPartials = {},
		    prevId;
		if (enableLog) dbug.log('iterating over partials for injection');
		//iterate over all the partials to inject them into the live DOM
		return partials.every(function(partial, id){
			if (enableLog) dbug.log('considering %s for injection', id);
			//if it's in a line that's been injected, skip it
			//if it was passed through the renderers, it means that it needs an update or insertion
			if (rendered[id] && !insertedPartials[id]) {
				//get the corresponding partial in the DOM
				var before = jState.partials[id];
				//if there's a corresponding partial already in the DOM, replace it
				if (before) {
					if (enableLog) dbug.log('performing update for %s', id);
					partial.replaces(before);
					destroyPartial(id, jState, behavior);
				} else {
					//else it's not in the DOM
					//look to see if this partial is in a line item (for example, the tr for a td that is a partial)
					var line = getPartialLine(partial);
					//if there is no line, inject it into the DOM in the container
					var success = line ? injectPartialLine(partial, line, container, insertedPartials)
					    : injectPartial(partial, jState.partials[prevId], container);
					if (!success) return false;
				}
			}
			if (rendered[id]) jState.partials[id] = partial;
			prevId = id;
			return true;
		}, this);
	};

	//given a line, destroy it
	var destroyLine = function(line, behavior){
		if (enableLog) dbug.log('destroying line:', line);
		behavior.cleanup(line);
		line.destroy();
	};

	var cleanRemainingParitals = function(partials, jState, behavior){
		var linesToDestroy = {};
		//for any partials that were in the DOM but not in the response, remove them
		jState.partials.each(function(partial, id){
			//if the partial is in the DOM but not the response
			if (!partials[id]) {
				//get its line; assume that we have to remove that, too
				var line = getPartialLine(partial);
				if (enableLog) dbug.log('destroying %s', id, line);
				//destroy the partial
				destroyPartial(id, jState, behavior);
				linesToDestroy[line.get('data', 'partial-line-id')] = line;
			}
		});
		for (id in linesToDestroy) {
			destroyLine(linesToDestroy[id], behavior);
		}
	};

	var injectPartial = function(partial, previousPartial, container){
		if (prevId) {
			if (enableLog) dbug.log('injecting line for %s after previous item (%s)', id, prevId);
			//if this isn't the first one, inject it after the previous id
			partial.inject(jState.partials[prevId], 'after');
		} else {
			//find the container and inject it as the first item there
			var containers = getPartialContainers(partial, container);
			if (containers.DOMcontainer) {
				if (enableLog) dbug.log('injecting %s into top of container (%o)', id, containers.DOMcontainer);
				partial.inject(containers.DOMcontainer, 'top');
			} else {
				//else, we don't know where to inject it
				dbug.warn('Could not inject partial (%o); no container or previous item found.', partial);
				return false;
			}
		}
		return true;
	};

	var injectPartialLine = function(partial, line, container, insertedPartials){
		if (enableLog) dbug.log('preparing line for injection');
		//there is a line, so we inject it instead of the partial.
		//get the previous line (from the response)
		var prevLine = line.getPrevious('[data-partial-line-id]'),
		    prevLineInDOM;
		//now find it's counterpart in the live DOM
		if (prevLine) prevLineInDOM = container.getElement('[data-partial-line-id=' + prevLine.get('data', 'partial-line-id') + ']');
		//if it's there, inject this line after it
		if (prevLineInDOM) {
			if (enableLog) dbug.log('injecting line (%o) after previous line (%o)', line, prevLine);
			line.inject(prevLineInDOM, 'after');
		} else {
			//else this is the first line, so inject it at the top of the container
			var lineContainers = getPartialContainers(partial, container);
			if (lineContainers.DOMcontainer) {
				if (enableLog) dbug.log('injecting line (%o) into top of container (%o)', line, lineContainers.DOMcontainer);
				line.inject(lineContainers.DOMcontainer, 'top');
			} else {
				//else, we don't know where to inject it
				dbug.warn('Could not inject partial (%o) in line (%o); no container or previous item found.', partial, line);
				return false;
			}
		}
		//store the fact that we just injected all the partials in this line
		line.getElements('[data-partial-id]').each(function(partial){
			insertedPartials[partial.get('data', 'partial-id')] = true;
		});
		return true;
	};

})();