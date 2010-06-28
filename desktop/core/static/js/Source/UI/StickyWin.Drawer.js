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
description: Drawer for StickyWin
provides: [StickyWin.Drawer]
requires: [Core/Fx.Tween, clientcide/StickyWin.UI]
script: StickyWin.Drawer.js

...
*/
StickyWin.UI.implement({
	options: {
		drawer: {
			content: '',
			side: 'right',
			styles: {
				width: 200,
				minHeight: 100,
				padding: 10,
				background: '#fff',
				position: 'absolute',
				background: 'url(/static/art/drawer.png) no-repeat'
			},
			fxOptions: {
				duration: 700,
				transition: 'expo:out'
			}
		}
	},
	fillDrawer: function(content){
		if (!this.drawer) return this.makeDrawer(content);
		if ($(content) || $type(content) == "array") this.drawer_content.empty().adopt(content);
		else this.drawer_content.set('html', content);
		return this;
	},
	makeDrawer: function(content){
		content = content || this.options.drawer.content;
		this.drawer = new Element('div', {
			'class':'sw_drawer'
		}).setStyles(this.options.drawer.styles).inject(this.element).set('tween', this.options.drawer.fxOptions);
		this.drawer_content = new Element('div', {
			'class':'sw_drawer_content'
		}).inject(this.drawer);
		this.drawer_footer = new Element('div', {
			'class':'sw_drawer_footer'
		}).setStyles(this.options.drawer.styles).setStyle('height', 20);
		this.fillDrawer(content);
		this.drawer_footer.inject(this.drawer);
		switch(this.options.drawer.side) {
			case 'right':
				this.drawer.setStyles({
					right: 14, //-this.options.drawer.styles.width - 14,
					top: 15,
					zIndex: -1,
					backgroundPosition: (-775 + this.options.drawer.styles.width) + 'px 0'
				});
				this.drawer_footer.setStyles({
					bottom: -30,
					left: 0,
					minHeight: 10,
					height: 10,
					backgroundPosition: (-775 + this.options.drawer.styles.width) + 'px -782px'
				});
		}
		return this;
	},
	toggleDrawer: function() {
		this[this.drawerVisible ? 'hideDrawer' : 'showDrawer']();
		return this;
	},
	showDrawer: function(){
		if (!this.drawer) this.makeDrawer();
		this.drawer.tween('right', -this.options.drawer.styles.width - 13);
		this.drawerVisible = true;
		return this;
	},
	hideDrawer: function(){
		if (this.drawer) this.drawer.tween('right', 13);
		this.drawerVisible = false;
		return this;
	}
});

StickyWin.implement({
	getUI: function(){
		var div = this.element.getElement('.DefaultStickyWin');
		return div ? div.retrieve('StickyWinUI') : null;
	},
	fillDrawer: function(content) {
		var ui = this.getUI();
		if (ui) ui.fillDrawer(content);
		return this;
	},
	toggleDrawer: function(show){
		var ui = this.getUI();
		if (ui) {
			if (show) ui.showDrawer();
			else if (show != undefined) ui.hideDrawer();
			else ui.toggleDrawer();
		}
		return this;
	},
	hideDrawer: function(){
		return this.toggleDrawer(false);
	},
	showDrawer: function(){
		return this.toggleDrawer(true);
	}
});
