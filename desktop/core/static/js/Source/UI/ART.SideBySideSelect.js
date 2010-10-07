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
requires: [Widgets/ART.Widget, Widgets/ART.Keyboard, More/HtmlTable.Zebra, Core/Fx.Tween, Core/Selectors]
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
				'data-filters': 'HtmlTable',
				'class':'noKeyboard'
			},
			headers: ['Deselected']
		},
		selectedOptions: {
			properties: {
				'data-filters': 'HtmlTable',
				'class':'noKeyboard'
			},
			headers: ['Selected']
		},
		makeContent: function(name, selected){
			return new Element('span', { html: name });
		}
	},
	
	initialize: function(select, options){
		this.select = $(select).setStyle('display', 'none');
		this.parent(options);
		this._build();
		this.element.setStyle('display', 'block');
		this.select.store('SideBySideSelect', this);
		new ART.Keyboard(this);
		this._attachKeys();
	},
	
	// creates the DOM elements for the UI
	_build: function(){
		this.deselectedContainer = new Element('div', { 'class':'deselected' });
		this.deselected = new HtmlTable(this.options.deselectedOptions);
		this.deselectedContainer.adopt(this.deselected);
		
		this.spacer = new Element('div', {
			'class': 'spacer'
		});
		this.moveRight = new Element('a', {
			text: 'select',
			'class': 'moveRight',
			events: {
				click: this.moveSelection.bind(this, 'right')
			}
		}).inject(this.spacer);
		this.moveLeft = new Element('a', {
			text: 'select',
			'class': 'moveLeft',
			events: {
				click: this.moveSelection.bind(this, 'left')
			}
		}).inject(this.spacer);
		
		this.selectedContainer = new Element('div', { 'class':'selected' });
		this.selected = new HtmlTable(this.options.selectedOptions);
		this.selectedContainer.adopt(this.selected);

		this.element.adopt(this.deselectedContainer);
		this.element.adopt(this.spacer);
		this.element.adopt(this.selectedContainer);

		this.makeRows();

		//click a row, select it; double click, move it
		this.element.addEvent('click:relay(tbody tr)', this.clickRow.bind(this));
		this.element.addEvent('dblclick:relay(tbody tr)', function(e, tr){
			e.stop();
			this.moveRow(tr);
		}.bind(this));
	},
	
	makeRows: function(){
		this.selected.body.empty();
		this.deselected.body.empty();
		this.select.getElements('option').each(function(option){
			var name = option.get('text') || option.get('value');
			this._options[name] = option;
			var row = this._makeRow(name, option.get('selected') ? 'selected' : 'deselected');
		}, this);
	},
	
	_attachKeys: function(){
		//selects all rows in the focused table
		var selectAll = function(e){
			e.preventDefault();
			var trs;
			if (this._rangeStart) trs = this._rangeStart.getSiblings('tr');
			else if (this._focusedRow) trs = this._focusedRow.getSiblings('tr');
			else trs = $(this.deselected).getElements('tbody tr');
			trs.each(function(tr) {
				this.selectRow(tr, true);
			}, this);
		}.bind(this);
		//returns the focused row or our best guess as to which one is our starting point
		//defaults to the left side's first row if nothing else matches
		var getCurrentRow = function(){
			if (this._focusedRow) return this._focusedRow;
			if (this._rangeStart) return this._rangeStart;
			else return $(this.deselected).getElement('tbody tr');
		}.bind(this);
		//return the sibling rows for a given row
		var getSiblings = function(row){
			return row.getParent('tbody').getChildren('tr');
		};
		//selects the next row from the current focused row
		var selectNext = function(e){
			e.preventDefault();
			var row = getCurrentRow();
			var rows = getSiblings(row);
			var next = rows[rows.indexOf(row) + 1];
			if (!next) return;
			//if shift is held, don't clear the selection; add to it
			if (!e.shift) this.clearSelection(rows);
			if (!next.hasClass('selected')) this.selectRow(next, true);
			else this.deselectRow(row, true);
			this._focusedRow = next;
		}.bind(this);
		//same as selectNext, only the other way
		var selectPrev = function(e){
			e.preventDefault();
			var row = getCurrentRow();
			var rows = getSiblings(row);
			var prev = rows[rows.indexOf(row) - 1];
			if (!prev) return;
			if (!e.shift) this.clearSelection(rows);
			if (!prev.hasClass('selected')) this.selectRow(prev, true);
			else this.deselectRow(row, true);
			this._focusedRow = prev;
		}.bind(this);
		//move selected rows to the left
		var moveLeft = function(e){
			e.preventDefault();
			$(this.selected).getElements('tr.selected').each(function(row){
				this.moveRow(row);
			}, this);
		}.bind(this);
		//move selected rows to the right
		var moveRight = function(e){
			e.preventDefault();
			$(this.deselected).getElements('tr.selected').each(function(row){
				this.moveRow(row);
			}, this);
		}.bind(this);
		//add keyboard entries for the above actions
		this.addShortcuts({
			'Select All': {
				keys: 'ctrl+a',
				shortcut: 'control/command + a',
				handler: selectAll,
				description: 'Select the previous row in the table.'
			},
			'Select Previous Row': {
				keys: 'up',
				shortcut: 'up arrow',
				handler: selectPrev,
				description: 'Select the previous row in the table.'
			},
			'Select Next Row': {
				keys: 'down',
				shortcut: 'down arrow',
				handler: selectNext,
				description: 'Select the next row in the table.'
			},
			'Move Row(s) Right': {
				keys: 'right',
				shortcut: 'right arrow',
				handler: moveRight,
				description: 'Select the next row in the table.'
			},
			'Move Row(s) Left': {
				keys: 'left',
				shortcut: 'left arrow',
				handler: moveLeft,
				description: 'Select the next row in the table.'
			}
		});
		
		this.attachKeys({
			'meta+a': selectAll,
			'shift+up': selectPrev,
			'shift+down': selectNext,
			'shift+right': moveRight,
			'shift+left': moveLeft
		});
	},
	
	_options: {},
	_rows: {},
	
	//return a row given the name (the text of the option the row correlates to)
	_getRow: function(name){
		return this._rows[name];
	},
	
	//given a row, return the name (the option text)
	_getName: function(row){
		return row.retrieve('_sideBySide:name');
	},
	
	//given an option name, get the value of it.
	getValue: function(name){
		return this._options[name].get('value') || this._options[name].get('text');
	},
	
	//remove a row from the layout; pass in noEffect (boolean) as *true* to do this instantly
	_destroyRow: function(row, noEffect){
		if (noEffect) {
			row.destroy();
		} else {
			row.fade('out', { duration: 500 }).get('tween').chain(function(){
				row.destroy();
			});
		}
	},
	
	//select a given row; pass *true* for noMove to leave it where it is, otherwise move it to the opposite side
	selectRow: function(row, noMove){
		if (noMove) {
			row.addClass('selected');
		} else {
			this.moveRow(row, 'selected');
			row.setStyle('opacity', 0).fade('in');
		}
		return row;
	},

	//same as selectRow, only the other direction
	deselectRow: function(row, noMove){
		if (noMove) {
			row.removeClass('selected');
		} else {
			this.moveRow(row, 'deselected');
			row.setStyle('opacity', 0).fade('in');
		}
		return row;
	},

	//given a name, create a row in the specified table; either 'selected' or 'deselected'
	_makeRow: function(name, where){
		var row = this[where].push([this.options.makeContent.call(this, name, where)]).tr.store('_sideBySide:name', name);
		this._options[name].set('selected', where == 'selected');
		this._rows[name] = row;
		return row;
	},

	//move a row to the specified table ('selected' or 'deselected');
	//if no *where* value is defined, move it to whatever table it isn't in.
	moveRow: function(row, where){
		var name = this._getName(row);
		if (!where) where = $(this.selected).hasChild(row) ? 'deselected' : 'selected';
		this[where].push(row);
		this[where + 'Container'].scrollTo(0, 999999);
		this._options[name].set('selected', where == 'selected');
		this.fireEvent(where == 'selected' ? 'select' : 'deselect', [name, row]);
		this._rangeStart = null;
		return row;
	},
	
	//given a click event, determine if the user intended to select/move a row.
	//allows for rows to contain elements like links or checkboxes, for example.
	ignore: function(event, row){
		var target = $(event.target);
		var valid = !['a', 'input'].every(function(str){
			return !target.match(str);
		});
		//if the row doesn't have a stored name, then it is the header or something so ignore it
		if (valid && this._getName(row)) return true;
		return false;
	},
	
	//select or deselect a row depending on its current state.
	toggleSelect: function(row){
		if (row.hasClass('selected')) this.deselectRow(row, true);
		else this.selectRow(row, true);
	},
	
	//select a range of rows. pass in a row element; if a start row is defined,
	//this row will be used as the end of the selection, otherwise stored as the start.
	selectRange: function(row){
		if (!this._rangeStart) {
			this._rangeStart = row;
		} else {
			var start = this._rangeStart;
			//see if the start of the selection is a child of the selected table
			var startSelected = $(this.selected).hasChild(start);
			var end = row;
			//see if the end is a child of the selected table
			var endSelected = $(this.selected).hasChild(end);
			//if both are in the same table, select the range
			if (startSelected == endSelected) {
				var rows;
				//get the selected rows
				if (startSelected) {
					rows = $(this.selected).getElements('tr');
					$(this.deselected).getElements('.selected').removeClass('selected');
				} else {
					rows = $(this.deselected).getElements('tr');
					$(this.selected).getElements('.selected').removeClass('selected');
				}
				var toToggle = [], started;
				//go through each row in the respective table and find the rows to mark and mark them
				rows.each(function(row) {
					if (row == start || row == end) started = !started;
					if (started || row == start || row == end) row.addClass('selected');
					else row.removeClass('selected');
				}, this);
			} else {
				//here the selected row wasn't in the same table as the previous marker, so we clear
				//the selection and reset the start.
				this.clearSelection();
				this._rangeStart = row;
			}
		}
	},

	//clear the selection state
	//if you pass in a collection of rows, remove their selected class.
	clearSelection: function(rows){
		this._rangeStart = null;
		if (rows) rows.removeClass('selected');
	},

	//handles a row being clicked
	clickRow: function(event, row){
		//check if we should ignore this click
		if (this.ignore(event, row)) return;
		//store the new focus point
		this._focusedRow = row;
		//if the user is holding shift, select the row and then the range
		if (event.shift) {
			this.toggleSelect(row);
			this.selectRange(row);
		//if meta/control, then toggle but don't clear the selection
		} else if (event.meta || event.control) {
			this.toggleSelect(row);
		} else {
			//else it's a naked click; clear the selection and select only the clicked row
			this.clearSelection($(this).getElements('tr'));
			this.toggleSelect(row);
			this._rangeStart = row;
		}
		return this;
	},
	
	//moves all selected rows from one side to the other
	//direction = 'left' or 'right'
	moveSelection: function(direction){
		var selected = $(this.selected).getElements('tr.selected');
		var deselected = $(this.deselected).getElements('tr.selected');
		var source = direction == 'left' ? selected : deselected;
		source.each(function(row){
			var name = this._getName(row);
			this.moveRow(row, direction == 'left' ? 'deselected' : 'selected');
		}, this);
	},
	
	//destroys this widget
	destroy: function(){
		this.element.destroy();
		this.fireEvent('destroy');
		this.eject();
		return this;
	}

});