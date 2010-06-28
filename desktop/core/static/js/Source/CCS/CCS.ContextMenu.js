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
description: Right-click context menu for CCS.JFrame
provides: [CCS.ContextMenu]
requires: [More/Element.Shortcuts, Core/Element.Event, Core/Class.Extras, /Element.Data,
  Core/Element.Dimensions, Core/Selectors]
script: CCS.ContextMenu.js

...
*/

(function(){

	var eventStopper = $lambda(false);
	/*
		ContextMenu class adds right-click style menus to a jframe environment
		arguments:
			delegate - (element) the parent element that one right-clicks to show the context menu and also, usually, contains the menu element.
		
		note:
			delegate also has an object defined in it's css value; a JSON decodable set of properties like so:
			<div data-context-menu-actions="[{'events':['contextmenu','click:relay(.fb-item-options)'],'menu':'ul.context-menu'}]">
			
			where the data is structured like so:
			
				[ //array of actions; this allows support for more than one context menu in a single parent
					{
						'events':['contextmenu','click:relay(.fb-item-options)'], //when the user right clicks, or clicks a .fb-item-options element
						'menu':'ul.context-menu' //it shows this menu
					}
				]
	*/
	document.addEvents({
		mousedown: function(e) {
			//if there is a menu visible, hide it on any click
			var active = $(CCS.ContextMenu.active);
			if (active && e.target != active && !active.hasChild(e.target)) CCS.ContextMenu.active.hide();
		}.bind(this),
		keyup: function(e) {
			//or if the user hits escape
			if (e.key == "esc" && CCS.ContextMenu.active) CCS.ContextMenu.active.hide();
		}.bind(this)
	});
	CCS.ContextMenu = new Class({
		Implements: [Options, Events],
		options: {
			//onShow: $empty(menu),
			//onHide: $empty(menu)
		},
		initialize: function(delegate, options){
			this.setOptions(options);
			this.delegate = $(delegate);
			this.attach();
		},
		detachers: [],
		attach: function(){
			//get the menu data in the css property
			var menudata = this.delegate.get('data', 'context-menu-actions', true);
			if (menudata) {
				//for each menu item defined
				menudata.each(function(data){
					var events = {};
					//get the menu
					var menu = this.delegate.getElement(data.menu);
					if (!menu) {
						//if there is no menu, but there was data, we want to kill right-click support
						//on this element; we assume that the right-click behavior is still intended,
						//but there's simply no menu
						this.delegate.addEvent('contextmenu', eventStopper);
						this.detachers.push(function(){
							this.delegate.removeEvent('contextmenu', eventStopper);
						}.bind(this));
						return;
					}
					menu.addEvents({
						//prevent the menu item itself from having default right click actions displayed
						contextmenu: eventStopper,
						//hide the menu when a value is selected
						click: this.hide.bind(this)
					});
					this.detachers.push(function(){
						menu.removeEvent('contextmenu', eventStopper);
					});
					//for each event defined in the data, delegate that event to the container
					//contextmenu, click:relay(selector), etc
					data.events.each(function(event) {
						events[event] = function(e){
							e.preventDefault();
							//let's only show one menu like this at a time
							this.activeMenu = menu;
							//put the menu on the mouse
							this.show(e.page.x, e.page.y);
						}.bind(this);
					}, this);
					this.delegate.addEvents(events);
					this.detachers.push(function(){
						this.delegate.removeEvents(events);
					}.bind(this));
				}, this);
			}
		},
		//removes all the bound functions from the DOM
		detach: function(){
			this.detachers.each(function(fn){
				fn();
			});
		},
		toElement: function(){
			return this.activeMenu;
		},
		//shows the menu at the given x/y position
		show: function(x, y){
			//if there is a menu visible, hide it on any click
			if (CCS.ContextMenu.active && CCS.ContextMenu.active != this) CCS.ContextMenu.active.hide();
			
			if (this.activeMenu) {
				this.activeMenu.show();
				this.position(x, y);
				CCS.ContextMenu.active = this;
				this.fireEvent('show', [x, y, this.activeMenu]);
			}
		},
		position: function(x, y){
			relativeTo = this.activeMenu.getOffsetParent();
			var relpos = relativeTo.getPosition();
			//position the menu next to the cursor so that the menu is to the right and below it
			var newpos = {
				left: x - relpos.x,
				top: y - relpos.y
			};
			//now do a bunch of math to figure out if the menu is out of view
			var wSize = window.getSize();
			var mSize = this.activeMenu.getSize();
			var bottomRight = {
				x: x + mSize.x,
				y: y + mSize.y
			};
			if (bottomRight.x > wSize.x) newpos.left = newpos.left - mSize.x - 5;
			if (bottomRight.y > wSize.y) newpos.top = newpos.top - mSize.y - 5;
			
			this.activeMenu.setStyles(newpos);
		},
		//hides the active menu
		hide: function(){
			var menu = this.activeMenu;
			if (menu) menu.hide();
			this.activeMenu = null;
			if (CCS.ContextMenu.active == this) CCS.ContextMenu.active = null;
			this.fireEvent('hide', menu);
		}
	});

})();
