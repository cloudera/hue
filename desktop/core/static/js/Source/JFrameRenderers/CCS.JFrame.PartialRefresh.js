/*
---
description: Any JFrame response that has elements that have a property defined for data-partial-id will have each auto-refresh response only update them.
provides: [CCS.JFrame.PartialRefresh]
requires: [/CCS.JFrame, Widgets/ART.Alerts, More/Table, Widgets/Element.Data, /PartialUpdate]
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

	CCS.JFrame.addGlobalRenderers({

		/*
			Partials are comprised of instructions in HTML responses that mark areas of the document that should be
			compaired against previous responses. These areas's raw HTML (the HTML returned from the server, not the
			current DOM state, which may have classes or style attributes or even new DOM elements in place) is compared
			to the previous response. When there's a mis-match in the response, only those elements that have changed
			are run through the JFrame filters to configure them for display and then replace their expired counterparts.

			Each individual item that might be refreshed must be marked with a data-single-partial-id property that is unique
			to the JFrame (i.e. multiple app windows can have id overlap) OR have a data-partial-id property and be the
			child of a container with app-unique data-partial-container-id.

			If you need to support the loading of additional content after the fact, such as with loading additional Ajax
			elements within the frame or if the response may return more or fewer items than the previous response, then
			you must add some additional instrumentation to your HTML. Specifically, you *must* define a container where
			new elements are injected. This MUST be the immediate parent of the partials, like so:

			Example w/ just partials and container
			<div data-partial-container-id="div1">
				<p data-partial-id="p1">foo</p>
				<p data-partial-id="p2">bar</p>
			</div>

			The only exception to this requirement, such as with tables, you may wish to add "lines" between
			the partials and the container. A good example here is a table which has partials for individual
			td elements, but new tr elements may come and go. In this case the "lines" must be immediate children
			of the parent, but the individual partials need not be immediate children of the lines.

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

			It is possible to support the possibility of the server returning a new sort order. This is a little more expensive
			so it must be "turned on" by giving the container the class name "ordered_partial_refresh".

			Example w/ partials, container, and lines that will obey sort order.
			<tbody data-partial-container-id="tbody1" class="ordered_partial_refresh">
				<tr data-partial-line-id="tr1">
					<td data-partial-id="id1"></td>
					<td data-partial-id="id2"></td>
				</tr>
				<tr data-partial-line-id="tr2">
					<td data-partial-id="id3"></td>
					<td data-partial-id="id4"></td>
				</tr>
			</tbody>

			In the above example, if the server replied with tr2 preceding tr1, the order would update in the view because
			of the "ordered_partial_refresh" class.

			When using ajax to load in new content (such as with the AjaxLoad linker) you'll likely load new content in ouside
			the scope of this refresh handler. I.e. you'll handle the response and inject the new items yourself. In this case
			partial refresh needs only to store the original request state for future checksums. To accomplish this, set the
			options of the request to have the onlyProcessPartials flag set to true. This will run the ajax response through
			this renderer, find the new partial elements, and store their initial state for checking later.

		*/

		partialRefresh: function(content){
			dbug.timeEnd('partial refresh');
			dbug.time('partial refresh');
			var options = content.options || {};
			//if the request options include the ignorePartialRequest flag, exit
			if (options.ignorePartialRefresh) return;
			//when we load content via ajax, we don't want the response being parsed for partials
			var jState = getJState(this);
			//get the partial containers; containers that have elements in them to be partially refreshed
			var elements = new Element('div').adopt(content.elements);
			//find all the containers in the response that have data-partial-container-id
			var partialContainers = elements.getElements('[data-partial-container-id]');

			dbug.time('create');
			//and either fetch or create instances of PartialUpdate for them
			var updaters = partialContainers.map(function(container){
				return {
					updater: getUpdater(container, jState, {
						//when an element is destroyed, call jframe's garbage collection method
						onElementDestroy: function(el){
							this.collectElement(el);
						}.bind(this),
						//before individual elements are inserted in the DOM, run them through the jframe filters
						onBeforeUpdate: function(checked){
							dbug.time('update:filters');
							this.applyFilters(checked.target);
							dbug.timeEnd('update:filters');
						}.bind(this)
					}),
					responseContainer: container
				};
			}, this);
			dbug.timeEnd('create');

			//find stand-alone partials; these have no containers
			var standAlones = elements.getElements('[data-single-partial-id]'),
			    tmpTarget = new Element('div');
			dbug.time('stand alone');
			
			for (var i = 0; i < standAlones.length; i++){
				var element = standAlones[i];
				var id = element.get('data-single-partial-id');
				if (!jState.standAlones[id]){
					//create an instance of the single partial updater for each of these
					jState.standAlones[id] = new PartialUpdate.Single(element, {
						onElementDestroy: function(el){
							this.collectElement(el);
						}.bind(this),
						partialIdProperty: 'data-single-partial-id',
						updateStateOnStartup: false,
						onBeforeUpdate: function(element){
							dbug.time('update:filters');
							this.applyFilters(tmpTarget.adopt(element));
							dbug.timeEnd('update:filters');
						}.bind(this)
					});
				}
				updaters.push({
					updater: jState.standAlones[id],
					responseContainer: elements
				});
			}
			dbug.timeEnd('stand alone');

			//this method just updates the state of each updater to match that of the response
			var updateState = function(){
				dbug.time('update state');
				updaters.each(function(updaterObj){
					updaterObj.updater.updateState(updaterObj.responseContainer);
				});
				dbug.timeEnd('update state');
			};

			//for requests that want to handle the element injection themselves (ajaxload, for example)
			//they can instruct this filter to process the partials in the response and then exit
			if (options.onlyProcessPartials) {
				updateState();
				return;
			}
			//store the previous path to be the current one
			jState.prevPath = options ? options.responsePath : null;

			if (!updaters.length) {
				//no partial containers, reset and fall through to other renderers
				jState.updaters = {};
				jState.standAlones = {};
				this.enableSpinnerUsage();
				return;
			}

			//disable spinner for the next autorefresh
			this.disableSpinnerUsage();

			//if the options aren't defined or if we didn't auto refresh fall through to other renderers
			if (!options || !(options.autorefreshed || options.forcePartial)) {
				//...then store the state and render as usual (fall through to other renderers)
				updateState();
				return;
			}

			/*******************************
			FORM HERE ON OUT
			this filter will handle the response; we return true and other renderers are excluded
			UNLESS there is a partial returned that we cannot find the proper place to put it
			(i.e. it has no partial-container).
			*******************************/
			//store the path as the current one
			this.currentPath = options.responsePath || this.currentPath;

			dbug.time('update');
			updaters.each(function(updaterObj){
				updaterObj.updater.update(updaterObj.responseContainer);
			});
			dbug.timeEnd('update');
			dbug.time('apply filters to content');
			this.applyFilters(new Element('div'), content);
			dbug.timeEnd('apply filters to content');

			//we've updated the display, so tell filters that are waiting that they may need to update their display, too
			this.behavior.fireEvent('show');
			//prevent other renderers from handling the response
			dbug.timeEnd('partial refresh');
			return true;
		}

	});

	var jframeStates = new Table();

	//gets the state for the given jframe
	var getJState = function(jframe) {
		var jState = jframeStates.get(jframe);
		if (!jState) {
			jState = {
				updaters: {},
				standAlones: {}
			};
			jframeStates.set(jframe, jState);
		}
		return jState;
	};

	var getUpdater = function(container, jState, options){
		var id = container.get('data-partial-container-id');
		if (!jState.updaters[id]) {
			jState.updaters[id] = new PartialUpdate(container, $merge({
				sorted: container.hasClass('ordered_partial_refresh'),
				clone: container.get('html').contains('data-filter'),
				updateStateOnStartup: false
			}, options));
		}
		return jState.updaters[id];
	};

})();