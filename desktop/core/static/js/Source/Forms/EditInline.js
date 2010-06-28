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
description: EditInline
provides: [EditInline]
requires: [Core/Class.Extras, More/Class.Binds, More/Class.Occlude, Core/Element.Event,
  More/Element.Shortcuts]
script: EditInline.js

...
*/

//positions an input over an object to edit it inline
var EditInline = new Class({
	Implements: [Options, Class.Occlude, Events],
	Binds: ['edit', 'mouseenter', 'mouseleave', 'handleDocKey', 'handleDocClick'],
	options: {
		//onEnter: $empty,
		//onEdit: $empty(input),
		tag: 'input',
		hoverClass: 'edit_highlight',
		activeClass: 'edit_activated',
		props: {
			styles: {}
		},
		injectWhere: 'after',
		onEdit: $empty,
		positionOptions: {},
		preventDefault: false,
		editEvent: 'click',
		selectBegin: null,
		selectEnd: null,
		applySize: true,
		applyPosition: true,
		value: false, //value or function, if true, uses innerHTML of element
		/** if true, clicking out of the edit box acts like cancel. If false, acts like enter
		 TODO(nutron) can I make this default false, plz? kthxbye -todd */
		clickOutCancels: true
	},
	property: 'EditInline',
	initialize: function(container, options){
		this.container = $(container);
		if (this.occlude(this.property, this.container)) return this.occluded;
		this.setOptions(options);
		this.attach();
	},
	toElement: function(){
		return this.element;
	},
	attach: function(attach) {
		var method = $pick(attach, true) ? 'addEvents' : 'removeEvents';
		//mouseover/out behavior to allow for highlight invitation
		var events = {
			mouseenter: this.mouseenter,
			mouseleave: this.mouseleave
		};
		//if we're attaching an edit event (like "click") attach it
		if (this.options.editEvent) events[this.options.editEvent] = this.edit;
		this.container[method](events);
		//add document listener for out-clicks and esc key
		document[method]({
			keyup: this.handleDocKey,
			click: this.handleDocClick
		});
	},
	detach: function(){
		this.attach(false);
	},

	// If the user hits escape, abort the edit
	handleDocKey: function(e) {
		if (e.key == "esc") {
			this.close();
		}
	},

	//if user clicks out, close or commit depending on the options
	handleDocClick: function(e) {
		if (!this.activating && this.active && e.type == "click" && e.target != this.element) {
			if (this.options.clickOutCancels) {
				this.close();
			} else {
				this.enter();
			}
		}
	},

	/** "commit" the value that the user has entered */
	enter: function() {
		this.close();
		this.fireEvent('enter', this.element.get('value'));
	},

	mouseenter: function(){
		this.container.addClass(this.options.hoverClass);
	},
	mouseleave: function(){
		this.container.removeClass(this.options.hoverClass);
	},
	//shows input with the given value defaulted and selected
	edit: function(value, begin, end){
		if (this.activating || this.active) return;
		this.activating = true;
		//if this was used as an event listener, reset the value
		if ($type(value) == "event") value = null;
		if (!this.element) {
			//make the input; if the user hits enter, fire the enter event
			this.element = new Element(this.options.tag, this.options.props);
			this.element.addEvent('keydown', function(e) {
				if (this.active && !this.activating && e.key == "enter") this.enter();
			}.bind(this)).store(this.property, this);
		}
		var input = this.element;
		//inject it after the element we're editing
		input.hide().inject(this.container, this.options.injectWhere);
		value = value || this.options.value;
		if (value) input.set('value', $type(value) == "boolean" ? this.container.get('html') : $lambda(value)());
		//position it
		var dim = this.container.getComputedSize();
		if (this.options.applySize) {
			input.setStyles({
				width: this.options.props.styles.width||(this.container.getScrollSize().x),
				height: this.options.props.styles.height||(this.container.getScrollSize().y)
			});
		}
		if (this.options.applyPosition) {
			input.position(
				$merge(this.options.positionOptions, {
					relativeTo: this.container,
					position: 'upperLeft'
				})
			);
		}
	
		begin = (typeof begin == "number") ? begin : (typeof this.options.selectBegin == "number") ? this.options.selectBegin : 0;
		end = (typeof end == "number") ? end : (typeof this.options.selectEnd == "number") ? this.options.selectEnd : value.length;
	
		this.active = true;
		this.fireEvent('edit', input);
		input.show();
		if (input.createTextRange) {
		  var range = input.createTextRange();
		  range.collapse(true);
		  range.moveEnd('character', end);
		  range.moveStart('character', begin);
		  range.select();
		} else if (input.setSelectionRange) {
		  input.focus();
		  input.setSelectionRange(begin, end);
		} else {
		  input.select();
		}
		(function(){
			this.activating = false;
		}).delay(30, this);
	},
	close: function(){
		if (!this.active) return;
		this.element.hide();
		this.active = false;
		this.fireEvent('hide');
	}
});
