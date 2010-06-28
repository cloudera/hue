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
MultiInput - allows users to generate additional clones of an input.

arguments:

* container - a DOM element or its id of an element containing the input, add, and delete buttons.
* options - an object with key/value pairs of options

options

* onAdd - (function) event callback for when a new item is added; passed the copy of the container
* onRemove - (funciton) event callback for when an item is removed; passed the container of the item to be removed. Defaults to removing that element from the DOM with an effect (element.nix()).
* addButton - (string) a selector that is relative to the container for selecting the button for cloning an input
* delButton - (string) a selector that is relative to the container for selecting the button for removing a container
* hideFirstDel - (boolean) if *true* (the default) the delete button on the first input is hidden, preventing the original input from being removed.

*/

var MultiInput = new Class({

	Implements: [Options, Events, Class.Occlude],

	Binds: ['addInput', 'removeInput'],

	options: {
		/*
		onAdd: $empty(container),
		*/
		onRemove: function(container){
			container.nix();
			if (this.inputs.length) this.inputs.getLast().getElement(this.options.addButton).show(this.options.buttonDisplayStyle);
		},
		addButton: '.add',
		delButton: '.del',
		buttonDisplayStyle: 'inline',
		containerDisplayStyle: 'list-item',
		hideFirstDel: true
	},
	// <ul id="myUl">
	//   <li><input name="foo" type="text"/> <a class="del">Delete</a> <a class="add">Add</a></li>
	// </ul>
	
	property: 'MultiInput',

	//var myMultiInput = new MultiInput($('myUl').getElement('li'), {...})
	initialize: function(container, options){
		this.element = $(container);
		if (this.occlude()) return this.occluded;
		this.inputs.include(this.element);
		this.setOptions(options);
		if (this.options.hideFirstDel) this.element.getElement(this.options.delButton).hide();
		this.attach();
	},
	attach: function(container, attach){
		var method = $pick(attach, true) ? 'addEvents' : 'removeEvents';
		container = container || this.element;
		container.getElement(this.options.addButton);
		container.getElement(this.options.addButton)[method]({
			click: this.addInput
		});
		container.getElement(this.options.delButton)[method]({
			click: this.removeInput
		});
	},
	inputs: [],
	addInput: function(e, useFx) {
		if (e && e.preventDefault) e.preventDefault();
		var last = this.inputs.getLast();
		var copy = last.clone().inject(last, 'after').hide();
		this.attach(copy);
		this.inputs.include(copy);
		last.getElement(this.options.addButton).hide();
		copy.getElement(this.options.delButton).show(this.options.buttonDisplayStyle);
		if ($pick(useFx, true)) copy.reveal({display: this.options.containerDisplayStyle});
		else copy.show();
		this.fireEvent('add', copy);
	},
	removeInput: function(e) {
		var container;
		if (e && e.preventDefault) {
			e.preventDefault();
			this.inputs.each(function(input){
				if (input == e.target || input.hasChild(e.target)) container = input;
			});
		} else if ($type(e) == 'element') {
			container = e;
		}
		this.inputs.erase(container);
		this.fireEvent('remove', container);
	}
});
