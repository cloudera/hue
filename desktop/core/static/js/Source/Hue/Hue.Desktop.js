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
description: Core Hue.Desktop Functionality.
provides: [Hue.Desktop, CCS.Desktop]
requires: [/Hue, depender_client/Depender.Client, Core/Request, /Hue.Dock,
  More/Elements.From, More/URI]
script: Hue.Desktop.js

...
*/
Hue.Desktop = CCS.Desktop = {

	options: {
	//	onBeforeLoad: $empty(componentName)
	//	onComponentLoaded: $empty(componentName)
	//	onBeforeLaunch: $empty(componentName)
	//	onAfterLaunch: $empty(componentName)
	//	loginUrl: 'login.html', TODO(nutron)
		append: 'hue-desktop'
	},

	initialize: function(options){
		this.setOptions(options);
		this.addEvent('desktopReady', this.pollSession.bind(this));
		this.addEvent('componentLoaded', function(component){
			this.loadedComponents[component] = true;
		}.bind(this));
		Hue.Dock.initialize();
	},

	loaders: {},
	launchers: {},
	loadedComponents: {},
	stateUrl: "prefs/state",
	prefsUrl: "prefs/",

	/******************
	 * PUBLIC METHODS
	 ******************/

	//registers an object of key/value components
	/* example:
	Hue.Desktop.register({
		Help: {											//app name
			name: "Document Viewer", //name to show the user
			autolaunch: true/false, //if true, the app launches at registration time (startup)
			css: '/path/to/css/file.css',
			require: ['packagename/DV.Viewer'],								//required js files
			launch: function(path){								//function to execute whenever app is launched
				return new DV.Viewer(dv, path);
			},
			menu: {												//menu item (optional)
				id: 'hue-help-menu',						//id of the item
				img: {											//img properties (optional)
					src: '/help/static/art/help.png',
				}
			},
			help: '/help/help' //url to help document
		}
	}); */
	register: function(components){
		$each(components, function(val, key){
			this.add(key, val);
		}, this);
		return this;
	},

	/*
		Register several plugins. See addPlugin for details.
		Example:
		Hue.Desktop.addPlugins({
			FileBrowser: {...plugin details},
			FileEditor: {...plugin details}
		});
	*/

	addPlugins: function(components){
		$each(components, function(val, key){
			this.addPlugin(key, val);
		}, this);
	},

	plugins: {},

	/*
		Register a plugin for an application (component).
		Pass in an object with JavaScript and CSS dependencies and an optional launch method.
		The launch method, if defined, will be passed the instance that is being launched as well as the arguments passed to it at its invocation. You can add numerous plugins to the same app.

		Example:
		Hue.Desktop.addPlugin('SomeApp', {
			requires: ['More/Fx.Reveal', 'hue-shared/Foo'],
			css: '/plugindir/static/css/plugin.css',
			launch: function(instance, args){
				instance.foo();
			}
		});
	*/
	addPlugin: function(component, options){
		if (!this.plugins[component]) this.plugins[component] = [];
		this.plugins[component].push(options);
	},

	bootstraps: {},

	getBootstrap: function(componentOrInstance){
		var component = $type(componentOrInstance) == "string" ? componentOrInstance : this.getAppComponentName(componentOrInstance);
		return this.bootstraps[component];
	},

	//adds a single component (string - the app name) and its options (object)
	//see register example above
	add: function(component, options){
		if (!options || this.loaders[component]) return this;
		this.bootstraps[component] = options;
		//if there is a custom launch method, set the launcher
		if (options.launch) this.setLauncher(component, options.launch);
		this.loaders[component] = function(callback){
			var plugins = this.plugins[component];
			var loadCSS = function(url){
				if (!$$('link').get('href').contains(url)) {
					new Element('link', {
						rel: 'stylesheet',
						media: 'screen',
						type: 'text/css',
						href: new URI(url).setData('noCache', new Date().toString())
					}).inject(document.head);
				}
			};
			//if there is a css link, inject it
			if (options.css) loadCSS(options.css);
			var requiredScripts = [];
			if (plugins) {
				plugins.each(function(plugin){
					if (plugin.css) loadCSS(plugin.css);
					if (plugin.require) requiredScripts.combine(plugin.require);
				});
			}
			//if there is an oncomplete method in the options, execute it when the files are loaded
			var ready = function(){
				this.fireEvent('componentLoaded', component);
				if (callback) callback();
				if (options.onComplete) options.onComplete();
				//reset the loader to be this method going forward (as it's already loaded);
				this.loaders[component] = ready;
			}.bind(this);
			//if there are dependencies, load them
			if (options.require) requiredScripts.combine(options.require);
			if (requiredScripts.length) {
				Depender.require({
					scripts: requiredScripts,
					callback: ready
				});
			} else {
				ready();
			}
		}.bind(this);

		if (options.menu) Hue.Dock.addApp(component, options);
		//if this app is to autolaunch
		if (options.autolaunch) this.autolaunchers.push(this.launch.bind(this, component));
		return this;
	},

	autolaunchers: [],

	hasApp: function(component){
		return !!this.loaders[component];
	},

	//configures a launcher (function) for a given component(string)
	setLauncher: function(component, launcher){
		this.launchers[component] = launcher;
	},

	instances: {},

	/*
		adds an instance for z-index / focus management
		component - (string) the application name
		instance - (object) the instance of that application
	*/
	addInstance: function(component, instance){
		instance._hueComponent = component;
		if (!this.instances[component]) this.instances[component] = [];
		this.instances[component].include(instance);
		//on destroy, remove the instance from the list of instances
		//add Hue-<COMPONENT> - mostly just used for selecting apps in windmill.
		instance.addEvent('destroy', this.removeInstance.bind(this, [component, instance]));
		$(instance).addClass('Hue-'+component.toUpperCase());
		instance.inject($('hue-desktop'));
	},

	/*
		given an instance of a widget, returns the component name for that widget ("FileBrowser", "JobBrowser", etc)
	*/
	getAppComponentName: function(instance){
		return instance._hueComponent;
	},

	/*
		given the component name of a widget ("FileBrowser"), return the nice name ("File Browser")
	*/
	getAppName: function(component){
		var appData = this.bootstraps[component];
		if (!appData) return null;
		return this.bootstraps[component].name || component;
	},

	/*
		removes an instance from z-index / focus managment
		component - (string) the application name
		instance - (object) the instance of that application
	*/
	removeInstance: function(component, instance){
		this.instances[component].erase(instance);
		return this;
	},
	/*
		brings all the windows of a specified application to the foreground
		component - (string) the application name
	*/
	focusComponent: function(component){
		var instances = this.instances[component];
		if (!instances || !instances.length) return instances || [];
		if (instances.length == 1) {
			instances[0].focus();
		} else {
			var sorted = instances.sort(function(left, right){
				var zl = $(left).getStyle('z-index').toInt();
				var zr = $(right).getStyle('z-index').toInt();
				return (zl == zr) ? 0 : (zl < zr) ? -1 : 1;
			});
			sorted.each(function(win, i){
				if (i == sorted.length - 1) win.focus(true);
				else win.bringToFront(true);
			});
		}
		return instances;
	},

	/*
		launches a given component
		component - (string) the name of the component
		args - (object) arguments to pass to its launcher
		callback - (function; optional) an optional callback passed a pointer to the instance created; passed nothing if the launch was not sucessful.
	*/

	launch: function(component, args, callback){
		callback = callback || $empty;
		if (!this.hasApp(component)) {
			if (component != '_blank') {
				Hue.error('Could Not Launch App', 'Sorry, we couldn\'t find an app named ' + component + '. Launching a new window instead.');
			}
			callback();
			return window.open(args[0], component);
		}

		args = args ? $splat(args) : [];
		//if the component has a launcher configured
		var launch = function(){
			this.fireEvent('beforeLaunch', component);
			var launcher = this.launchers[component];
			//throw errors if we're debugging
			var attempt = function(){
				var launched = launcher.apply(this, args);
				if (this.plugins[component]) {
					this.plugins[component].each(function(plugin){
						if (plugin.launch) plugin.launch(launched, args);
					});
				}
				this.addInstance(component, launched);
				var after = function(){
					this.fireEvent('afterLaunch', component);
					launched.removeEvent('afterLaunch', after);
				}.bind(this);
				launched.addEvent('load', after);
				callback(launched);
				return launched;
			}.bind(this);

			return dbug.conditional(attempt, function(e){
				callback();
				alert('Sorry, there was an error launching ' + component + '.\n Try again, or contact us for help.');
			});
		}.bind(this);
		if (this.hasLoaded(component)) {
			return launch();
		} else {
			//add an event so it launches after it loads
			var loaded;
			this.addEvent('componentLoaded', function(comp){
				if (loaded) return;
				if (comp == component) {
					loaded = true;
					return launch();
				}
			}.bind(this));
		}
		this.load(component, $empty, true);
		return this;
	},

	//load a component, e.g.
	//this.load("FileBrowser")
	//callback - (function) method to execute when the component loads
	//_showMessage - (boolean) show a loading message; internal - messages are only showed when the app is launched
	load: function(component, callback, _showMessage){
		dbug.conditional(function(){
			callback = callback || $empty;
			if (!this.hasLoaded(component)) {
				if (_showMessage) this.fireEvent('beforeLoad', component);
				this.loaders[component](callback);
			} else {
				this.fireEvent('componentLoaded', component);
				callback();
			}
		}.bind(this), function(e){
			dbug.warn('could not launch %s', component);
		});
		return this;
	},

	hasLoaded: function(component){
		return !!this.loadedComponents[component];
	},

	//iterates over all the open windows and serializes their state for restoration
	//returns: an object of component, size, position, url, and options for each open window
	serialize: function(){
		var state = {};
		//loop through all the components for which there are instances
		$each(this.instances, function(instances, component){
			if (!state[component]) state[component] = [];
			//loop through each instance for the component (all the windows)
			instances.each(function(instance){
				//if it has a serialize method and it's not destroyed
				//store its serialization
				if (instance.serialize && !instance.isDestroyed()) state[component].push(instance.serialize());
			});
		});
		//return the object of all the states
		return state;
	},

	//restores a state to the desktop
	//states - (object) the state of all the open apps (returned by .serialize())
	restore: function(states){
		this.states = $H(JSON.decode(unescape(states)));
		var loaded_component;
		if (this.states.getLength()) {
			var hidden, msg;
			//hider obscures the desktop while it loads apps
			var hider = function(){
				//if the msg is already displayed/present, then exit
				if (msg) return;
				hidden = true;
				//hide the desktop
				//IE has rendering issues when the opacity of the desktop is zero
				//so don't do this for IE.
				if (!Browser.Engine.trident) $('hue-desktop').setStyle('opacity', 0);
				//create a holder for the messaging, inject it, and center it
				msg = new Element('div', {
					'class':'loadingmsg',
					html: '<p>Restoring your session...</p>'
				}).inject(document.body).adopt(new Element('a', {
					text: 'Clear your session',
					events: {
						click: function(){
							this.resetAndRefresh();
						}.bind(this)
					}
				})).position();
			}.bind(this);
			//fades the message out and restores the desktop
			var fader = function(){
				msg.fade('out').get('tween').chain(function(){
					msg.destroy();
				});
				$('hue-desktop').fade('in');
				ART.Popup.DefaultManager.focusTop();
			};
			//reference count the number of components we're going to load
			var components_to_load = 0;
			//iterate over all the components
			this.states.each(function(componentStates, component){
				if (!this.hasApp(component)) {
					dbug.warn('could not find application: %s', component);
					return;
				}
				//if there are no states in this app (component) to load, exit
				if (!componentStates.length) return;
				loaded_component = true;

				//hide the desktop
				hider();
				//increment the component counter
				components_to_load++;

				//define a launcher function for this particular component
				var launcher = function(){
					//update the message to the user
					msg.set('html', 'Restoring ' + this.getBootstrap(component).name + '...');
					//decrement the reference counter
					components_to_load = components_to_load - 1;
					//for each app that was open, launch it
					componentStates.each(function(state){
						dbug.conditional(function(){
							var instance = this.launch(component, [state.path, state.options]);
							if (instance) instance.restore(state);
						}.bind(this), function(e){
							dbug.warn('could not launch %s', component);
						});
					}, this);
					//if there are no more components, fade in the desktop
					if (components_to_load == 0) {
						this.fireEvent('desktopReady');
						fader.delay(500);
					}
				}.bind(this);

				//if the component is already loaded, call the launcher
				if (this.hasLoaded(component)) {
					launcher();
				} else {
					//else add an event to call the launcher when the component is loaded
					var launched;
					this.addEvent('componentLoaded', function(comp){
						if (comp == component && !launched) {
							launched = true;
							launcher();
						}
					});
					//load the component
					this.load(component);
				}
			}, this);
		}
		if (!loaded_component) this.fireEvent('desktopReady');
	},

	//returns true if there is a state to restore
	isClearSession: function(){
		return new URI().getData('clearSession') == "true";
	},

	//stores the current desktop state
	store: function(){
		if (this.noSession) return;
		var hashString = escape(JSON.encode(this.serialize()));
		var jsonRequest = new Request.JSON({
				url: this.stateUrl,
				method: "post",
				onFailure:function(){
					$clear(Hue.Desktop.store_periodical);
				}
		});
		jsonRequest.send("set=" + hashString);
	},

	//delete the user session
	resetSession: function(){
		var jsonRequest = new Request.JSON({
			url: this.stateUrl,
			method:"post",
			async: false
		});
		jsonRequest.send("delete");
	},

	resetAndRefresh: function(){
		this.resetSession();
		document.body.hide();
		this.noSession = true;
		window.location.href = "/";
	},

	/*
		if the window location has a launch instruction, launch the apps per the instruction
		instruction is a query string value for "launch" with comma separated values of app
		names and optional **encoded** urls. Examples:

		http://desktop/?launch=FileBrowser,Health
		http://desktop/?launch=FileBrowser:/some/path,Heath:/some/other/path%3Fwith%3Dstuff

		The prefered usage is to put the same query string values after the hash:

		http://desktop/#launch=FileBrowser,Health
		http://desktop/#launch=FileBrowser:/some/path,Heath:/some/other/path%3Fwith%3Dstuff

		If both are specified (a query string AND a hash query string) then the hash version will win.

		An additional parameter can be specified to prevent session restoration:

		http://desktop/?launch=FileBrowser,Health&noSession=true
		http://desktop/#launch=FileBrowser,Health&noSession=true

		otherwise the previous session is restored and the linked apps are launched with them.

	*/
	launchLinked: function(){
		//grab the current window location data
		var uri = new URI();
		//get the query string data and from the hash as well
		var data = uri.getData('launch') || {};
		var fragData = uri.get('fragment').parseQueryString();
		//look for the launch argument in both
		var launch = fragData.launch || data.launch;
		//if there's fragment data, clear it (so that it's not there if the user hits reload or bookmarks)
		if (fragData) window.location.hash = "";
		//look for the noSession value and, if it's not present, restore the session
		var noSession = fragData.noSession || data.noSession;
		var launched;
		if (launch){
			//loop through all the launch instructions
			launch.split(',').each(function(toLaunch){
				var split = toLaunch.trim().split(':');
				//split on : - example: FileBrowser:/some/path
				var component = split[0];
				var url = split[1];
				//launch the app
				if (this.hasApp(component)) {
					if (!launched && noSession != "true") Hue.Desktop.restoreDesktop();
					else this.fireEvent('desktopReady');
					//TODO don't fire ready until these other apps are launched
					this.launch(component, url && unescape(url));
					launched = true;
				}
			}, this);
		}
		return launched;
	},

	//restores the desktop
	//returns true if any state was found (including an empty one)
	restoreDesktop: function(){
		if (this.isClearSession()) {
			this.resetAndRefresh();
			return;
		}
		this.prefs = this.getState();
		if (this.prefs) this.restore(this.prefs.state);
		return !!this.prefs && this.prefs.state;
	},

	//This request is synchronous because this method determines whether or not there is a session to restore.  It is a decision point, at which the app continues in one of two ways.
	//Either restoration, or be initializing the default desktop.  In order to do this synchronously we would need to use callbacks.
	getState: function(){
		//only get this once; it's syncronous
		if (this._fetchedState) return this._fetchedState;
		var result;
		var jsonRequest = new Request.JSON({
			url: this.prefsUrl,
			async: false,
			method: "get",
			onSuccess: function(data){
				result = data;
			}
		});
		jsonRequest.send();
		this._fetchedState = result;
		return result;
	},

	pollSession: function(){
		//store the state of the desktop every 10 seconds
		Hue.User.withUser(function(){
			Hue.Desktop.store_periodical = Hue.Desktop.store.periodical(30000, Hue.Desktop);
		});
	},

	showHelp: function(componentOrInstance, url){
		var data = this.getBootstrap(componentOrInstance) || {};
		if (this.healthInstance && !this.healthInstance.isDestroyed() && (url || data.help)) {
			this.healthInstance.load({ requestPath: url || data.help }).focus();
		} else {
			Hue.Desktop.launch('Help', data.help, function(instance){
				if (instance) this.healthInstance = instance;
			}.bind(this));
		}
	}

};

//store the state of the desktop on unload
window.addEvent('unload', function(){
	Hue.Desktop.store();
});

$extend(Hue.Desktop, new Events);
$extend(Hue.Desktop, new Options);
