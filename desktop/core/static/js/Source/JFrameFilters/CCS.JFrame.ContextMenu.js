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
description: Adds context menu support for any element with a data-context-menu-actions property. See the CCS.ContextMenu class for details on usage.
provides: [CCS.JFrame.ContextMenu]
requires: [/CCS.JFrame, /CCS.ContextMenu]
script: CCS.JFrame.ContextMenu.js

...
*/

(function(){

//subclass CCS.ContextMenu to create one that knows about JFrame

var JframeContextMenu = new Class({
	Extends: CCS.ContextMenu,
	options: {
		//jframe: null,
		adjustLocation: false
	},
	initialize: function(){
		//create a placeholder for when we pop menus out of the jframe (so we can put them back)
		this._placeHolder = new Element('div').hide();
		this.parent.apply(this, arguments);
		//pointer to the jframe; it's wrapped in function to prevent a recurssion issue - 
		//when you run a class instance through $merge (which setOptions does) you get one...
		this._jframe = $lambda(this.options.jframe)();
	},
	show: function(x, y){
		//when the menu is shown, put the place holder after the menu
		this._placeHolder.inject(this.activeMenu, 'after');
		//move the menu into the container
		this.activeMenu.inject(this.options.container);
		//apply click delegates to it since it's likely no longer in the jframe (where the delegates start)
		this._jframe.applyDelegates(this.activeMenu);
		this.parent(x, y);
	},
	hide: function(){
		//when we hide the menu, put the menu back where it was and pop the placeholder out of the DOM
		this.activeMenu.inject(this._placeHolder, 'after');
		this._placeHolder.dispose();
		this.parent();
	}
});

CCS.JFrame.addGlobalFilters({

	//intercept right click behaviors
	contextMenu: function(container){
		//get the elements that capture right click events for context menus
		var delegates = container.getElements('[data-context-menu-actions]');
		if (!delegates.length) return;
		
		//get a pointer to the content contaner of the window; this is the jbrowser container
		//that contains the jframe
		var contents = this.getWindow().contents;
		
		//create an instance of CCS.Context menu for each delegate
		var menus = delegates.map(function(delegate) {
			return new JframeContextMenu(delegate, {
				jframe: $lambda(this), //pass a function that wraps this jframe instance
				container: contents //inject the menu into the container outside the jframe
			});
		}, this);
		//detatch these whenever we unload jframe
		this.markForCleanup(function(){
			menus.each(function(menu){
				menu.detach();
			});
		});
	}

});

})();
