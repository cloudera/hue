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
description: Turns a mutli-select input into two side-by-side areas that items move between when selected/deselected.
provides: [ART.SideBySideSelect]
requires: [Widgets/ART.Widget, More/HtmlTable.Zebra, Core/Fx.Tween, Core/Selectors]
script: ART.SideBySideSelect.js
...
*/

ART.SideBySideSelect = new Class({
	
	Extends: ART.Widget,
	
	Implements: [Options, Events],
	
	options: {
		// onSelect: $empty(name, row),
		// onDeselect: $empty(name, row),
		className: 'sideBySideSelect clearfix',
		deselectedOptions: {
			properties: {
				'class': 'ccs-data_table'
			},
			headers: ['Deselected']
		},
		selectedOptions: {
			properties: {
				'class': 'ccs-data_table'
			},
			headers: ['Selected']
		},
		makeContent: function(name, selected) {
			return new Element('span', { html: name });
		}
	},
	
	initialize: function(select, options) {
		this.select = $(select);
		this.parent(options);
		this._build();
		this.element.setStyle('display', 'block');
		this.select.store('SideBySideSelect', this);
	},
	
	_build: function() {
		this.deselectedContainer = new Element('div', { 'class':'deselected' });
		this.deselected = new HtmlTable(this.options.deselectedOptions);
		this.deselectedContainer.adopt(this.deselected);
		
		this.spacer = new Element('div', {'class': 'spacer'});
		
		this.selectedContainer = new Element('div', { 'class':'selected' });
		this.selected = new HtmlTable(this.options.selectedOptions);
		this.selectedContainer.adopt(this.selected);

		this.element.adopt(this.deselectedContainer);
		this.element.adopt(this.spacer);
		this.element.adopt(this.selectedContainer);
		
		this.select.getElements('option').each(function(option){
			var name = [option.get('text') || option.get('value')];
			this._options[name] = option;
			if (option.get('selected')) this.selectRow(name);
			else this.deselectRow(name);
		}, this);
		
		this.element.addEvent('click:relay(tr)', this.swap.bind(this));
	},
	
	_options: {},
	_rows: {},
	
	_destroyRow: function(name) {
		var row = this._rows[name];
		if (row) {
			row.fade('out', { duration: 500 }).get('tween').chain(function(){
				row.destroy();
			});
		}
	},
	
	getValue: function(name) {
		return this._options[name].get('value');
	},
	
	selectRow: function(name) {
		this._destroyRow(name);
		var row = this.selected.push([this.options.makeContent(name, true)]).tr;
		row.setStyle('opacity', 0).fade('in').store('_sideBySide:name', name);
		this._rows[name] = row;
		this._options[name].set('selected', true);
		this.fireEvent('select', [name, row]);
		return row;
	},
	
	deselectRow: function(name) {
		this._destroyRow(name);
		var row = this.deselected.push([this.options.makeContent(name)]).tr;
		row.setStyle('opacity', 0).fade('in').store('_sideBySide:name', name);
		this._rows[name] = row;
		this._options[name].set('selected', false);
		this.fireEvent('deselect', [name, row]);
		return row;
	},
	
	ignore: function(event, row) {
		var target = $(event.target);
		return !['a', 'input'].every(function(str){
			return !target.match(str);
		});
	},
	
	swap: function(event, row) {
		if (this.ignore(event, row)) return;
		var name = row.retrieve('_sideBySide:name');
		if (!name) return;
		if ($(this.selected).hasChild(row)) this.deselectRow(name);
		else if ($(this.deselected).hasChild(row)) this.selectRow(name);
		return this;
	},
	
	destroy: function(){
		this.element.destroy();
		this.fireEvent('destroy');
		return this;
	}

});