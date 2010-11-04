/*
---
description: Any JFrame response that has a root-level child element with the class .partial_refresh will find all elements that have a property defined for data-partial-id that is unique to the response and only update them. If there is a mismatch in the response such that the number of and ids of partials in the previous state do not match the return state, an alert will be shown the user that the entire view will be updated that they can cancel, if they so choose.
provides: [PartialUpdate]
requires: [Core/Element.Dimensions, Core/Options, Core/Events, Behavior/DashSelectors]
script: PartialUpdate.js

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

;(function(){

	this.PartialUpdate = new Class({

		Implements: [Options, Events],

		options: {
			// onFailure: function(){},
			// onNoUpdate: function(){},
			// onBeforeUpdate: function(){},
			// initialPartials: null,

			sorted: true,
			clone: false,
			ejectToUpdate: true,
			updateClass: 'partial-refresh-updated partial-refresh-transitionable',
			updateClassToRemove: 'partial-refresh-updated',
			flagRemovalDelay: 1000,
			partialIdProperty: 'data-partial-id',
			partialLineIdProperty: 'data-partial-line-id',
			updateStateOnStartup: true
		},

		initialize: function(container, options){
			this.container = document.id(container);
			this.setOptions(options);
			if (this.options.updateStateOnStartup) this.updateState(this.container);
		},

		//update the current state from the container (the "live" DOM)
		updateState: function(container){
			var partials = this._getPartials(container);
			if (partials) {
				//if there are partials already, merge the result
				if (this.partials) {
					for (id in partials) {
						this._validateId(id);
						this.partials[id] = partials[id];
					}
				//else there were no partials in the previous response; so assign these.
				} else {
					this.partials = partials;
				}
			}
		},

		/*
			takes the given container and updates the live DOM with the state of the given
			container. This container must contain immediate children that either have partials
			or partial lines.
		*/
		update: function(container){
			//dbug.time('partial update completed');
			var restore = this._eject();
			//keep an un-altered version of the response to use for sorting
			var untouched = this.options.sorted && container.clone(true, true);
			//get the partials from the container
			var partials = this._getPartials(container);
			if (partials) {
				//check the partials for changes
				var checked = this._checkPartials(partials);
				if (!checked) {
					//if there aren't any partials in the response, then clean any in the DOM
					this._cleanRemainingPartials(partials);
					//put the container back in place
					restore();
					//exit
					return false;
				}
				//if we're cloning, fire our event for jframe to run its filters
				if (this.options.clone) {
					//dbug.time('fireEvent: beforeUpdate');
					this.fireEvent('beforeUpdate', checked);
					//dbug.timeEnd('fireEvent: beforeUpdate');
					//restore the clones to the response container
					this._restorePartials(checked, partials);
				}
				//inject the response updates into the DOM
				this._injectPartials(partials, checked);
				//clean any partials that don't belong
				this._cleanRemainingPartials(partials);
				//sort if necessary
				if (this.options.sorted) this._sortPartials(untouched);
			} else {
				//clean any partials that don't belong
				this._cleanRemainingPartials(partials);
			}
			//return the container to the DOM
			restore();
			//clean up the "updated" flag after a delay
			if (this.options.updateClassToRemove) this._cleanUpdateFlag.delay(this.options.flagRemovalDelay, this);
			//dbug.timeEnd('partial update completed');
			return true;
		},

		toElement: function(){
			return this.container;
		},

		// ejects the container from the DOM, returning a function that puts it back
		_eject: function(){
			//dbug.time('eject');
			if (this.container.parentNode && this.options.ejectToUpdate){
				var scroll = this.container.getParent().getScroll();
				var s = new Element('span').inject(this.container, 'after');
				this.container.dispose();
				return function(){
					//dbug.time('restore');
					s.parentNode.replaceChild(this.container, s);
					this.container.getParent().scrollTo(scroll.x, scroll.y);
					//dbug.timeEnd('restore');
				}.bind(this);
			} else {
				return function(){};
			}
			//dbug.timeEnd('eject');
		},

		//find all elements marked as updated and remove the updated class name
		_cleanUpdateFlag: function(){
			var els = this.container.getElements('.' + this.options.updateClassToRemove);
			for (var i = 0; i < els.length; i++){
				els[i].removeClass(this.options.updateClassToRemove);
			}
		},

		/*
			gets the partials from the given container
			returns a map of partial ids to objects with
			pointers to the element and the html of that element
			e.g. data[id] = {element: partialElement, html: partialElement.innerHTML}

			if the container has no partial elements, it returns the boolean false
		*/

		_getPartials: function(container) {
			//dbug.time('get partials');
			var data = {};
			//if there are no partial elements, return now
			if (!container.innerHTML.contains(this.options.partialIdProperty)) return false;
			//get all the elements with a partial id
			var partial, id,
			    els = container.getElements('[' + this.options.partialIdProperty + ']');
			for (var i = 0; i < els.length; i++){
				partial = els[i];
				id = partial.getAttribute(this.options.partialIdProperty);
				//store a pointer to that element to return it
				data[id] = {
					element: partial,
					html: partial.innerHTML
				};
			}
			//dbug.timeEnd('get partials');
			return data;
		},

		/*
			given a list of partial objects ({element:el, html:html[, line:line]})
			go through and find which ones require updating. if options.clone is true
			clone these into a target.
		*/
		_checkPartials: function(partials){
			//dbug.time('check partials');
			var data = {
				updates: {},
				target: new Element('div')
			};
			//loop through the partials and figure out which ones need updating so that we can
			//run only those through the filters
			var checked = false;
			for (id in partials){
				var partial = partials[id];
				//get the corresponding element in the dom
				var before = this.partials && this.partials[id];
				//if there isn't one, or thier raw html don't match, we'll update it, so we must render it
				if (!before || before.html != partial.html) {
					//we must preserve the DOM structure to be able to find partial containers and partial lines
					//so clone the partial for rendering
					if (this.options.clone){
						var clone = document.id(partial.element.cloneNode(true));
						data.target.appendChild(clone);
						//we also need a key/value map of all the updates for quick lookups
						data.updates[id] = clone;
					} else {
						data.updates[id] = partial.element;
					}
					checked = true;
				}
			}
			//dbug.timeEnd('check partials');
			return checked ? data : false;
		},

		//given a partial, attempts to find the line it is in
		//example: for a td that is a partial, it may have the tr as its line
		_getPartialLine: function(partial, forceUpdate){
			if (!partial.line || forceUpdate) partial.line = partial.element.getParent('[' + this.options.partialLineIdProperty + ']');
			return partial.line;
		},

		//this method destroys a partial given its partial id
		_destroyPartial: function(id){
			//get the element
			var element = this.partials[id].element;

			this._clean(element);
			//delete it from the state
			delete this.partials[id];
		},

		//this method takes a group of cloned partials (that have been passed through filters)
		//and puts them back into the DOM from which they came, replacing the elements they
		//were cloned from. This allows us to retain the DOM structure of the response, while
		//only running through the filters the elements that need it.
		_restorePartials: function(checked, partials){
			//dbug.time('restore partials');
			for (id in checked.updates) {
				var clone = checked.updates[id],
				    partial = partials[id];
				partial.element.parentNode.replaceChild(clone, partial.element);
				partial.element = clone;
			}
			//dbug.timeEnd('restore partials');
		},

		_injectPartials: function(partials, checked) {
			//dbug.time('inject partials');
			var insertedPartials = {},
			    partial,
			    prevId;
			//iterate over all the partials to inject them into the live DOM
			for (id in partials) {
				partial = partials[id];
				//if it's in a line that's been injected, skip it
				//if it was passed through the renderers, it means that it needs an update or insertion
				if (checked.updates[id] && !insertedPartials[id]) {
					//get the corresponding partial in the DOM
					var before = this.partials && this.partials[id];
					//if there's a corresponding partial already in the DOM, replace it
					if (before) {
						if (this.options.updateClass) partial.element.addClass(this.options.updateClass);
						partial.element.replaces(before.element);
						this._clean(before.element);
					} else {
						//else it's not in the DOM
						//look to see if this partial is in a line item (for example, the tr for a td that is a partial)
						var line = partial.line || this._getPartialLine(partial);
						//if there is no line, inject it into the DOM in the container
						if (line) this._injectPartialLine(partial, insertedPartials);
						else this._injectPartial(partial, prevId);
					}
				}
				if (!this.partials) this.partials = {};
				if (checked.updates[id]) this.partials[id] = partial;
				prevId = id;
			}
			//dbug.timeEnd('inject partials');
		},

		_cleanRemainingPartials: function(partials){
			//dbug.time('clean partials');
			var linesToDestroy = {}, partial;
			//for any partials that were in the DOM but not in the response, remove them
			for (id in this.partials) {
				partial = this.partials[id];
				//if the partial is in the DOM but not the response
				if (!partials || !partials[id]) {
					//get its line; assume that we have to remove that, too
					var line = partial.line || this._getPartialLine(partial);
					if (line) linesToDestroy[line.getAttribute(this.options.partialLineIdProperty)] = line;
					//destroy the partial
					this._destroyPartial(id);
				}
			}
			for (id in linesToDestroy) {
				this.fireEvent('elementDestroy', line);
				line.destroy();
			}
			//dbug.timeEnd('clean partials');
		},

		//inject a partial into the container; prevId is the previous partial's id, used
		//to inject the partial in the proper place
		_injectPartial: function(partial, prevId){
			this._validateId(partial.get(this.options.partialIdProperty));
			var previousPartial = this.partials[prevId];
			if (previousPartial) {
				//if this isn't the first one, inject it after the previous id
				partial.element.inject(previousPartial.element, 'after');
			} else {
				partial.inject(this.container, 'top');
			}
		},

		//inject a partial line into the container; insertedPartials is a map of partial ids to
		//partials that have been injected; used to ensure partials aren't injected twice when
		//a line that contains several is injected into the DOM
		_injectPartialLine: function(partial, insertedPartials){
			//there is a line, so we inject it instead of the partial.
			//get the previous line (from the response)
			var line = partial.line || this._getPartialLine(partial);
			var prevLine = line.getPrevious('[' + this.options.partialLineIdProperty + ']'),
			    prevLineInDOM;
			this._validateId(line.get(this.options.partialLineIdProperty));

			//now find it's counterpart in the live DOM
			var injected = false;
			if (!this.options.sorted) {
				if (prevLine) prevLineInDOM = this.container.getElement('[' + this.options.partialLineIdProperty + '=' + prevLine.getAttribute(this.options.partialLineIdProperty) + ']');
				//if it's there, inject this line after it
				if (prevLineInDOM) {
					line.inject(prevLineInDOM, 'after');
				} else {
					line.inject(this.container, 'top');
				}
				injected = true;
			}
			if (!injected) line.inject(this.container);
			//store the fact that we just injected all the partials in this line
			var linePartials = line.getElements('[' + this.options.partialIdProperty + ']');
			for (var p = 0; p < linePartials.length; p++) {
				this._validateId(linePartials[p].get(this.options.partialIdProperty));
				if (this.options.updateClass) linePartials[p].addClass(this.options.updateClass);
				insertedPartials[linePartials[p].getAttribute(this.options.partialIdProperty)] = true;
			};
		},

		_sortPartials: function(responseContainer) {
			//dbug.time('sort partials');
			this._sortCount = 0;
			//get all the children of the update container that are partially updatable
			var kids = responseContainer.getChildren('[' + this.options.partialIdProperty + ']');
			//for each kid, inject it into this container
			for (var kid = 0; kid < kids.length; kid++){
				var id = kids[kid].getAttribute(this.options.partialIdProperty);
				this.partials[id].element.inject(this.container);
			}
			//get all the lines that are children of the update container
			var lines = responseContainer.getChildren('[' + this.options.partialLineIdProperty + ']');
			if (lines.length){
				//get the lines in this.container
				var liveLines = this.container.getChildren('[' + this.options.partialLineIdProperty + ']');
				var liveLineMap = {}, liveLineOrder = [];
				//create a map of all the live lines to their ids
				for (var liveLine = 0; liveLine < liveLines.length; liveLine++) {
					var liveLineId = liveLines[liveLine].getAttribute(this.options.partialLineIdProperty);
					liveLineMap[liveLineId] = liveLines[liveLine];
					liveLineOrder.push(liveLineId);
				}
				//loop through all the lines in the response
				var prev;
				for (var line = 0; line < lines.length; line++){
					//get the id of the response line
					var lineId = lines[line].getAttribute(this.options.partialLineIdProperty);
					if (lineId != liveLineOrder[line]) {
						//inject the live line into that location
						if (!prev) liveLineMap[lineId].inject(this.container, 'top');
						else liveLineMap[lineId].inject(prev, 'after');
						var index = liveLineOrder.indexOf(lineId);
						liveLineOrder.splice(index, 1);
						liveLineOrder.splice(line, 0, lineId);
						this._sortCount++;
					}
					prev = liveLineMap[lineId];
				}
			}
			//dbug.log('items: %s, sorted: %s', lines.length, this._sortCount);
			//dbug.timeEnd('sort partials');
		},

		_toGC: [],

		_clean: function(element){
			this.fireEvent('elementDestroy', element);
			if (!this._gcTimer) this._gcTimer = this._gc.periodical(100, this);
			this._toGC.push({
				element: element
			});
		},

		//this is a "threadsafe" garbage collection routine
		//if we call element.destroy on, say, 1000 nodes, the MooTools gc goes through
		//all of them at once. This version does them in batches, releasing the thread
		//as it goes.
		_gc: function(){
			if (this._toGC.length) {
				var i = 0;
				while (this._toGC.length && i < Math.max(100, this._toGC.length/100)) {
					var data = this._toGC.shift();
					//destroy the element
					this._destroy(data.element);
					i++;
				}
				if (i == 0) clearInterval(this._gcTimer);
			}
		},

		//implementing a custom destroy method; this is slightly faster than the MooTools version
		//but doesn't do some of it's less-important garbage collection
		_destroy: function(el){
			for (var i = 0; i < el.childNodes.length; i++) {
				this._destroy(el.childNodes[i]);
			}
			if (el.removeEvents) el.removeEvents();
		},

		//ids must be alpha-numeric
		_validateId: function(id){
			if (id.test(validIdRE)) throw ('invalid partial id: "' + id + '"');
		}

	});

	var validIdRE = /[^a-zA-Z0-9_\-]/;

	PartialUpdate.Single = new Class({

		Extends: PartialUpdate,

		initialize: function(element, options){
			this.element = document.id(element);
			this.html = this.element.innerHTML;
			this.setOptions(options);
			this.partialId = this.element.get(this.options.partialIdProperty);
			this._validateId(this.partialId);
		},

		update: function(container){
			var partial = container.getElement('[' + this.options.partialIdProperty + '=' + this.partialId + ']');
			var html = partial && partial.innerHTML;
			if (partial && html != this.element.innerHTML) {
				this.fireEvent('beforeUpdate', partial);
				if (this.options.updateClass) partial.addClass(this.options.updateClass);
				partial.replaces(this.element);
				var element = this.element;
				this.element = partial;
				this.html = html;
				this._clean(element);
				this._cleanUpdateFlag.delay(this.options.flagRemovalDelay, this);
			}
		},

		updateState: function(container){
			var partial = container.getElement('[' + this.options.partialIdProperty + '=' + this.partialId + ']');
			var html = partial && partial.innerHTML;
			this.html = html;
		},

		_cleanUpdateFlag: function(){
			this.element.removeClass(this.options.updateClassToRemove);
		}

	});

})();
