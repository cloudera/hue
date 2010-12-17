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
description: Dock UI Component for Desktop
provides: [Hue.Dock]
requires: [/Hue, clientcide/StickyWin.PointyTip, /Hue.User]
script: Hue.Dock.js

...
*/
Hue.Dock = {
	initialize: function(){
		this.element = $('hue-dock');
		this.statusContent = $('hue-dock-status-content');
		//show/hide tips when mousing over dock icons; launch the app when clicked
		this.icons = $('hue-dock-icons').addEvents({
			'mouseover:relay(a)': this.showAppTip.bind(this),
			'mouseout:relay(a)': this.hideAppTip.bind(this),
			'click:relay(a)': this.launchApp.bind(this),
			'dblclick:relay(a)': function(e, a){
				this.launchApp(e, a, true);
			}.bind(this)
		});
		//an instance of PointyTip for the application names
		this.tip = new StickyWin.PointyTip({
			point: 6,
			destroyOnClose: false,
			showNow: false,
			pointyOptions: {
				closeButton: false
			},
			offset: {
				y: -17
			}
		});
		$(this.tip).addClass('dock-tip');
	},
	/*
		shows the tip popup when an application is moused over
		e - the mouseover event
		a - the link to the app
	*/
	showAppTip: function(e, a){
		var component = a.retrieve('Hue-app');
		if (!component) return;
		var name = Hue.Desktop.getBootstrap(component).name;
		this.tip.pointy.setContent(name);
		this.tip.show();
		this.tip.position({
			relativeTo: a
		});
	},
	/*
		hides the app tip
		e - the mouseout event
		a - the link to the app
	*/
	hideAppTip: function(e, a){
		this.tip.hide();
	},
	apps: {},
	/*
		registers an app on the doc; builds its icon
		component - (string) the application name
		appData - (object) the metadata from the bootstrap
	*/
	addApp: function(component){
		var appData = Hue.Desktop.getBootstrap(component);
		if (!appData.menu || !appData.menu.img) return;
		var lnk = new Element('a', {
			id: appData.menu.id
		});
		var img = new Element('img', appData.menu.img).addClass('hue-icon').inject(lnk);
		var dock = $('hue-dock-icons');
		lnk.inject(dock);
		// Sort the menu.
		var sortkey = function(a_left, a_right) {
			var left = a_left.get('id');
			var right = a_right.get('id');
			return (left == right) ? 0 : (left < right) ? -1 : 1;
		};
		dock.getChildren().sort(sortkey).inject(dock);
		lnk.store('Hue-app', component);
	},
	/*
		launches an app; if the app is open already, brings its windows to the foreground
		TODO: manage creating new windows for an existing open app
		e - (event) the click event
		a - (element) the app link
		launchAnother - (boolean) if true (defaults to false), launch another copy of the app even if one is open
	*/
	launchApp: function(e, a, launchAnother) {
		e.preventDefault();
		//get the component from the link
		var component = a.retrieve('Hue-app');
		//if we're in the middle of launching that app *from the dock*, stop
		if (this.launching.contains(component)) return;
		//get the instances for this app and focus them
		var instances = Hue.Desktop.focusComponent(component);
		//if there are no instances, or if we're explicitly launching another one (double click), launch it
		if (!instances.length || launchAnother) {
			//store that we're launching this
			this.launching.push(component);
			var launched;
			//add a timeout in case we fail to get a callback
			(function(){
				//if we haven't launched after 10 sec, drop the reference so the user can try again
				if (!launched) {
					this.launching.erase(component);
					dbug.log('removing dock launcher reference counter for %s launch request; no answer in 10 seconds', component);
				}
			}).delay(10000, this);
			//launch it
			Hue.Desktop.launch(component, a.get('href'), function(){
				//flag that this succeeded (even if the app failed to display, we can drop our reference counter)
				launched = true;
				//remove that we're storing this
				this.launching.erase(component);
			}.bind(this));
		}
	},
	launching: []
};
