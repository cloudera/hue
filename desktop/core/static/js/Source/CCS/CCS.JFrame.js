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
description: JFrame--Configurable "container" for simple HTML pages, within the CCS framework.
provides: [CCS.JFrame]
requires: 
 - Core/Request
 - More/Element.Delegation
 - More/Elements.From
 - More/Fx.Scroll
 - More/String.Extras
 - More/Spinner
 - clientcide/Collapsible
 - Widgets/ART.Alerts
 - Widgets/Behavior
 - Widgets/Behavior.Accordion
 - Widgets/Behavior.ArtButton
 - Widgets/Behavior.ArtInput
 - Widgets/Behavior.FormRequest
 - Widgets/Behavior.FormValidator
 - Widgets/Behavior.HtmlTable
 - Widgets/Behavior.OverText
 - Widgets/Behavior.SplitView
 - /Behavior.CollapsingElements
 - /Behavior.ContextMenu
 - /Behavior.DataGroupToggle
 - /Behavior.FilterInput
 - /Behavior.FitText
 - /Behavior.HtmlTableCheckSelected
 - /Behavior.HtmlTableChromeHack
 - /Behavior.HtmlTableKeyboard
 - /Behavior.HtmlTableLiveTreeKeyboard
 - /Behavior.HtmlTableMultiSelectMenu
 - /Behavior.HtmlTableRestore
 - /Behavior.HtmlTableUpdate
 - /Behavior.MultiChecks
 - /Behavior.PostEditor
 - /Behavior.SelectWithOther
 - /Behavior.SideBySideSelect
 - /Behavior.SizeTo
 - /Behavior.SplitViewPostFold
 - /Behavior.SplitViewScroller
 - /Behavior.SubmitOnChange
 - /Behavior.Tabs
 - /Behavior.Tips
 - /CCS

script: CCS.JFrame.js
...
*/
CCS.JFrame = new Class({

	Extends: ART.Widget,

	Implements: [ART.WindowTools, ART.Window.AlertTools],

	ns: 'hue',

	name: 'jframe',

	options: {
		/**
		//EVENTS:
		//all the events in ART.Widget, plus:
		onRequest: $empty(requestPath, userData),
		onBeforeRenderer: $empty(content, options), //see _applyRenderers method for details
		afterRenderer: $empty(content, options) //ditto
		onLoadComplete: $empty(data),
		onLoadError: $empty(error), //the jframe failed to load. An error alert has already displayed.
		onRedirect: empty(redirectedTo, originalRequestedURL), //the response was redirected (before content has been rendered)
		redirectAfterRender: empty(redirectedTo, originalRequestedURL), //after content is rendered
		size: {
			width: ,
			height: 
		},

		**/
		//evaluateJs: if true, script tags are evaluated when content is loaded
		evaluateJs: false,
		//includeLinkTags: if true, css <link> tags are injected into the DOM
		includeLinkTags: false,
		//useSpinner: if true, the content of the jFrame is masked when loading
		useSpinner: true,
		//linkers: a key/value set of linkers (see the addLinker method for docs)
		linkers: {},
		//filters: a key/value set of JFrame filters
		filters: {},
		//behaviors: a key/value set of behavior filters passed along to Behavior.addFilters
		behaviors: {},
		//the selector to match clicks against for delegation; defaults to only links
		clickRelays: 'a',
		//given the response and response text, this method determines if there's been a serverside error
		errorDetector: function(requestInstance, responseText) {
			//flag this as an error
			return responseText.contains('ccs-error-popup');
		},
		getScroller: function(){
			return this.element;
		},
		//passed the options that generated the request; see renderContent's options
		spinnerCondition: function(options){
			if (!this.loadedOnce) return false;
			if (options.autorefreshed && this._noSpinnerOnAutoRefresh) return false;
			return this.options.useSpinner;
		}
	},

	// path: initial page to load
	initialize: function(path, options){
		this.parent(options);
		new ART.Keyboard(this, this.keyboardOptions);
		this.addLinkers(this.options.linkers);
		this.addFilters(this.options.filters);
		this.behavior = new Behavior(this.element, {
			onError: function(){
				dbug.warn.apply(dbug, arguments);
			}
		});
		if(this.options.size) this.behavior.resize(this.options.size.width, this.options.size.height);
		['attachKeys', 'detachKeys', 'addShortcut', 'addShortcuts', 'removeShortcut', 'removeShortcuts',
		 'applyDelegates', 'getScroller', 'getContentElement', 'invokeLinker', 'configureRequest', 'getBehaviorState'].each(function(method){
			this.behavior.passMethod(method, this[method].bind(this));
		}, this);
		this.behavior.passMethods({
			getContainerSize: this.getCurrentSize.bind(this),
			registerKeyboard: function(keyboard){
				this.keyboard.manage(keyboard);
			}.bind(this),
			unregisterKeyboard: function(keyboard){
				this.keyboard.drop(keyboard);
			}.bind(this),
			callClick: function(){
				this.callClick.apply(this, arguments);
			}.bind(this)
		});
		this.addEvent('resize', this.behavior.resize.bind(this.behavior));
		this.addBehaviors(this.options.behaviors);

		this.element.addClass('jframe_wrapper').addClass('ccs-shared');
		this.scroller = new Fx.Scroll(this.options.getScroller.call(this));
		this.content = new Element('div', {
			'class': 'jframe_contents'
		}).inject(this.element);

		if (this.options.size) this.resize(this.options.size.width, this.options.size.height);
		this.load({requestPath: path});
	},
	
	/*
		configureRequest - configures a passed in request to be have its response rendered within JFrame..
		request - (* request object *) request object to be configured
	*/
	configureRequest: function(request){
		this._setRequestOptions(request, {
			onSuccess: function(nodes, elements, text){
				this._requestSuccessHandler(request, text);
			}.bind(this)
		});
	},


	toElement: function(){
		return this.element;
	},

	_createElement: function(){
		this.element = this.element || new Element('div').setStyles({display: 'block', position: 'relative', outline: 'none'}).store('widget', this);
	},

	delegatedTo: [],

/*
	
	the JFrame callClick event invokes the click handler for links/elements, matching against any JFrameLinkers and, 
	if none are found, running the default click handler (which is to load the link's href, if defined, into the JFrame).
	event - (*object*) the event object that was fired; a click, usually
	link - (*element*) typically an anchor tag, though that's not a requirement
	force - (*boolean*) forces the link to be activated even if it has the css class .disabled or .jframe_ignore
	callClick: function(event, link, force) {
		//this function is defined in the applyDelegates function below;
		//this commented out version added here for visibility's sake
	},

*/
	/*
		applies the default link handling delegates to a specific target, allowing you to attach link handling to any container
		target - (*element*) the element to which you wish to attach delegates
	*/
	applyDelegates: function(target){
		target = document.id(target) || this.content;
		//make sure we only apply this once per target
		if (this.delegatedTo.contains(target)) return;
		this.delegatedTo.push(target);
		
		var handler = function(e, elem, url, options){
			if (elem.get('tag') == 'a') e.preventDefault();
			if (!this._checkLinkers(e, elem)) {
				// If it's an anchor link, do scrolling
				if (url && url.get('fragment')) {
					// hrefs are url-encoded, but the "name" for the links isn't
					target = this.content.getElement('a[name=' + unescape(url.get('fragment')) + ']');
					if (target) {
						this.scroller.toElement(target);
						return;
					}
				}
				var path = url ? url.toString() : '';
				if (!path) return;

				options = $merge({
					requestPath: path
				}, options);
				var spinnerTarget = elem.get('data', 'spinner-target');
				if (spinnerTarget) spinnerTarget = $(this).getElement(spinnerTarget);
				options.spinnerTarget = spinnerTarget;
				this.load(options);

			}
		}.bind(this);
		this.callClick = function(e, elem, force, options){
			//allow links to force jframe to nerf them
			//this is required for doubleclick support
			//as otherwise there's no way to prevent this default jframe handler per link
			if (!force && (elem.hasClass('jframe_ignore') || elem.hasClass('disabled'))) return e.preventDefault();
			// Fix relative links
			if (elem.get('href')) {
				var url = new URI(elem.get('href'), {base: this.currentPath});
				if (url) elem.set('href', url.toString());
				var me = new URI();
				// If it's an external link
				if (url.get('scheme') != me.get('scheme') ||
						url.get('host') != me.get('host') ||
						url.get('port') != me.get('port')) {
					// Open external URLs in a new window.
					// TODO(todd) should also check that the URL begins with
					// whatever our prefix is, but "prefix" isn't really known
					// by this class with the current design.
					elem.set('target', '_blank');
				} else {
					handler(e, elem, url, options);
				}
			} else {
				handler(e, elem, false, options);
			}
		}.bind(this);
		target.addEvent('click:relay(' + this.options.clickRelays + ')', this.callClick);
	},

	/**
	 * Cause the content of this JFrame to load a particular URL.
	 *   options: see renderContent's options
	 */
	load: function(options){
		options = $merge({
			//by default, requests reload the entire jframe
			fullFrameLoad: true
		}, options);
		this.fireEvent('request', [options.requestPath, options.userData, options]);
		var req = new Request();
		this._setRequestOptions(req, 
			$merge(options, {
				method: options.method || 'get',
				url: new URI(options.requestPath).toString()
			})
		);
		req.send();
	},

	disableSpinnerUsage: function(){
		this._noSpinnerOnAutoRefresh = true;
	},

	enableSpinnerUsage: function(){
		this._noSpinnerOnAutoRefresh = false;
	},

	/** refresh the current content */
	refresh: function(options){
		this.fireEvent('refresh');
		this.load(
			$merge(options, {
				noScroll: true,
				requestPath: this.currentPath
			})
		);
	},

	getBehaviorState: function() {
		if(!this.options.behaviorState) this.options.behaviorState = {};
		return this.options.behaviorState;
	},

	/*
	options:
		content: content to render (html, dom element, or $$ collection of dom elements), 
		responsePath: the path to this content, 
		title: the title for the frame for this content, 
		userData: data to be passed along to the loadComplete event,
		target: dom element or id to fill with content; defaults to this.content
		suppressLoadComplete: (boolean) if true, the loadComplete event is not fired
		callback: a callback to execute after rendering; passed an object with content, responsePath, title, and target
		error: the server has returned an error
		autorefreshed: (boolean) whether or not this refresh was user initiated
		blankWindowWithError: the window is empty (and will remain so)

	notes:
		the loadComplete and callback methods are passed an object with the following attributes:
		content: the content returned from the server, unaltered
		elements: an array of DOM elements rendered from that response, excluding the script, style, and meta tags
		scripts: the inline js in the response (any text in a script tag)
		styles: all the link and style tags
		meta: all the meta tags in teh response
		responsePath: the path of what was returned (url),
		title: the title, stripped from the content as the inner text of the *title* tag, or the inner text of the first *h1*, or the path
		userData: any data passed in to the request (used for login)
		view: the view (string; see below)
		viewElement: the view element (DOM element, see below)
		target: the target where the content was loaded
		toolbar: the toolbar elements (see below),
		footer: the footer elements (see below)
		everything else: used to pass along options to filters, renderers, etc.
		
	views:
		The content of a JFrame request is searched for the first element with the class "view". 
		If found, the id of this element is treated as the current view. This id is stripped (all
		Desktop apps do not use ids, as there may be more than one of them). The data object passed
		to the loadComplete event and the callback in the options contains this view (the value of
		the id of the element) as well as the viewElement. This allows your code to attach logic
		based on the view (a 'controler'). Just wrap your response in a div with the class "view" and
		an id and you can switch on that in the event handler you attach.
		
		example html response:
		<div id="jobbrowser_job_list" class="view">
			<!-- the html for your view -->
		</div>
		
		in your script:
		myJframe.addEvent('loadComplete', function(data) {
			if (data.view == 'jobbrowser_job_list') new CCS.JobBrowser.JobView(data.viewElement);
		})
	
	toolbars:
		The content of a JFrame request is searched for elements with the class "toolbar" and "footer".
		These elements are referenced in the data passed to the loadComplete callback as the toolbar and footer
		for the current view. This allows you to do special things to the navigation. By default, JBrowser
		injects the contents of this toolbar into the area above the content and the footer content into
		the footer. By simply putting links and other elements into a div with the class "toolbar" it 
		will be added to the header (and the same for the footer).
		You must include the toolbar / footer in every response for it to remain there.
	*/
	renderContent: function(options){
		var content = {};
		var filter = function(elements, selector){
			if (!elements.length) return elements;
			var first = elements[0];
			var holder = new Element('div').adopt(elements);
			return first.getParent().getElements(selector);
		};
		if ($(options.content)) {
			//if the content is an element, cast it into an Elements array
			content.elements = $$($(options.content));
		} else if ($type(options.content) == "string") {
			//if it's a string, parse it
			content = this._parseContent(options.content);
		} else {
			//the only other valid option is that it's an array of elements, 
			//cast it into an Elements array in case it's just a vanilla array
			content.elements = $$(options.content);
		}
		if (options.filter) content.elements = filter(content.elements, options.filter);
		//determine view and view element
		var view,
		    viewElement = content.elements.filter('.view')[0] || content.elements.getElement('.view')[0];
		if (viewElement) {
			view = viewElement.get('id');
			viewElement.set('id', '');
			content.view = view;
			content.viewElement = viewElement;
		}
		content.options = options;
		this._applyRenderers(content);
	},

	/*
		fill: fills a given target with the appropriate content
		target - (*element*) the target to fill with content
		content - (*object*) an object with the following properties:
			options - (*object*) the options object that created the request; see renderContent
			js - (*string*) any the inline javascript to evalutate,
			links - (*elements array*) css links to be injected into the target
			elements - (*elements array*) elements to inject into the target (i.e. the actual content)
			title - (*string*) the title of the content
			view - (*string*; optional) if defined, the view of the content
			viewElement - (*element*; optional) if defined, the element for the view
			behavior - (*behavior object*; optional) if defined, the behavior instance to use
		
	*/

	fill: function(target, content, behavior){
		target.empty().adopt(content.elements);
		if (content.links && content.links.length && this.options.includeLinkTags) target.adopt(content.links);
		if (this.options.evaluateJs && content.js) $exec(content.js);
		this.applyDelegates(target);
		this.applyFilters(target, content, behavior || this.behavior);
		if (Browser.Engine.webkit) {
				var width = target.style.width;
				target.setStyle('width', '99%');
				(function() {
					target.style.width = width;
				}).delay(1);
		}
	},

	resize: function(x, y){
		this.element.setStyles({
			width: 'auto',
			height: y
		});
		this.currentSize = {
			x: x,
			y: y
		};
		this.fireEvent('resize', [x, y]);
	},
	
	getCurrentSize: function(){
		return this.currentSize;
	},

	getContentElement: function(){
		return this.getWindow().contents;
	},

	getScroller: function(){
		return this.scroller;
	},

	filters: {},

	/*
		addFilter:
		name - (*string*) the unique name of the filter
		fn - (*function*) callback executed
	*/

	addFilter: function(name, fn){
		this.filters[name] = fn;
		return this;
	},

	/*
		addFilters
		obj - (*object*) a key/value set of filters to add
	*/
	addFilters: function(obj){
		for (var name in obj) {
			this.addFilter(name, obj[name]);
		}
		return this;
	},

	/*
		add a new behavior filter
		name - (*string*) the name fo the behavior (no spaces or commas; preferably CamelCase)
		fn - (*function*) the function for the behavior filter.
		overwrite - (*boolean*) if true, will overwrite any pre-existing filter if one is present
	*/
	addBehavior: function(name, fn, overwrite){
		this.behavior.addFilter(name, fn, overwrite);
	},
	
	/*
		add a group of behavior filters
		obj - (*object*) an object of key/value pairs of name/functions for filters (see addBehavior)
		overwrite - (*boolean*) if true, will overwrite any pre-existing filter if one is present
	*/
	addBehaviors: function(obj, overwrite){
		this.behavior.addFilters(obj, overwrite);
	},
	/*
		add a new behavior plugin
		filterName - (*string*) the name of the filter this plugin is for (no spaces or commas; preferably CamelCase)
		name - (*string*) the name of the plugin (no spaces or commas; preferably CamelCase)
		fn - (*string*) the attachment function for the plugin
		overwrite - (*boolean*) if true, will overwite any pre-existing filter if one is present
	*/

	addBehaviorPlugin: function(filterName, name, fn, overwrite) {
		this.behavior.addPlugin(filterName, name, fn, overwrite);
	},
	/*
		add a group of behavior plugins
		obj - (*object*) an object containing objects containing the filter name, the plugin name, and the attachment function for the plugin
		overwrite - (*boolean*) if true, will overwrite any pre-existing filter if one is present
	*/

	addBehaviorPlugins: function(obj, overwrite){
		this.behavior.addPlugins(obj, overwrite);
	},

	/*
		apply a specific behavior to an element
		name - (*string*) the name fo the behavior (no spaces or commas; preferably CamelCase)
		element - (*element*) the DOM element to apply the behavior to
		force - (*boolean*) forces the behavior to reapply, even if it has already been applied; defaults to *false*.
	*/
	applyBehavior: function(name, element, force){
		var behavior = this.behavior.getBehavior(name);
		this.behavior.applyBehavior(element, behavior, force);
	},

	//Applies all the behavior filters for an element.
	//element - (element) an element to apply the filters registered with this Behavior instance to.
	//behavior - (behavior object) behavior instance to use 
	//force - (boolean; optional) passed through to applyBehavior (see it for docs)
	applyBehaviors: function(element, behavior, force){
		behavior.apply(element, force);
	},

	//garbage collects all applied filters for the specified element
	collectElement: function(element){
		this.behavior.cleanup(element);
	},

	/*
		applyFilters:
		container - (*element*) applies all the filters on this instance of jFrame to the contents of the container.
		content - (*object*) optional object containing various metadata about the content; js tags, meta tags, title, view, etc. See the "notes" section of the renderContent method comments in this file.
		behavior - (*behavior object*) optional behavior instance to be used for application of behaviors
			
	*/

	applyFilters: function(container, content, behavior){
		for (var name in this.filters) {
			this.applyFilter(name, container, content);
		}
		this.applyBehaviors(container, behavior || this.behavior);
	},


	/*
		applyFilter:
		name - (*string*) the name of the JFrame filter to apply
		container - (*element*) applies all the filters on this instance of jFrame to the contents of the container.
		content - (*object*) optional object containing various metadata about the content; js tags, meta tags, title, view, etc. See the "notes" section of the renderContent method comments in this file.
	*/
	applyFilter: function(name, container, content){
		dbug.conditional(this.filters[name].bind(this, [container, content]), function(e) {
			dbug.error('filter failed, name %s, error: ', name, e);
		});
	},

	marked: [],

	/*
		marks a function to execute when the jFrame is unloaded (before new content is loaded)
		fn - (*function*) the function to mark. Executed only once.
	*/
	markForCleanup: function(fn) {
		this.marked.push(fn);
	},

	/*
		linkers are custom event handlers for links that match a specific selector. Ideally, the selector is just a classname.
		When any link in a jFrame is clicked, it is checked against all registered linkers. If no matches are found, the link 
		is handled by jFrame and loads new content. If there is a match, the matcher's function handles the event.
		selector - (*string*) a css selector that the link is tested against.
		fn - (*function*) callback that handles links that match the selector
		
		example:
		
		//when any link with the class .alert is clicked, alert its href:
		myjFrame.addLinker('.alert', function(event, link) {
			event.preventDefault();
			alert(link.get('href'));
		});
	*/
	addLinker: function(selector, fn){
		this.linkers[selector] = fn;
		return this;
	},

	/*
		addLinkers:
		add a group of linkers
		obj - (*object*) a key/value set of linkers
	*/
	addLinkers: function(obj){
		$each(obj, function(fn, selector){
			this.addLinker(selector, fn);
		}, this);
		return this;
	},


	/*
		invokeLinker:
		invokes a specific linker to handle an event (allows you to manually fire a click for a specific linker)
		selector - (*string*) a css selector that maps to the linker
		element - (*element*) the element that will have fired the event
		event - (*event; optional*) the event object to pass along
	*/

	invokeLinker: function(selector, element, event){
		dbug.conditional(this.linkers[selector].bind(this, [event, element]), function(e) {
			dbug.error('linker failed, selector %s, error: ', selector, e);
		});
	},

	/*
		addRenderer: adds an renderer to this instance
		name - (*string*) a unique name for this renderer
		fn - (*function*) method, passed the contents (see renderer method above), that may handle those contents if it chooses
		
		To remove an renderer, overwrite it thusly:
		
		myJFrame.addRenderer('rendererToRemove', $empty);
	*/

	addRenderer: function(name, fn) {
		this._renderers[name] = fn;
	},

	/*
		addRenderers: adds a group of renderers
		obj - (*object*) a key/value set of renderers.
	*/

	addRenderers: function(obj) {
		$each(obj, function(fn, name) {
			this.addRenderer(name, fn);
		}, this);
	},

	/*
		destroy: removes the jframe element and cleans up any events that may be attached
	*/

	destroy: function(){
		this._sweep(this.element);
	},

/****************************************************************************************
	PRIVATE METHODS BELOW
*****************************************************************************************/

	/*
		_parseContent
		html - (*string*) given a string of html, return the js, css links, and body>elements, etc based on the content parsers.
	*/

	_parseContent: function(html) {
		var data = {
			html: html
		};
		for(parser in this._contentParsers) {
			this._contentParsers[parser].call(this, data);
		}
		return data;
	},

	_contentParsers: {
		scripts: function(data) {
			//get the inline scripts, take their js out, and remove them from the html
			var js;
			data.html = data.html.stripScripts(function(script){
				js += script;
			});
			data.js = js;
		},
		styles: function(data) {
			//get all the link and style tags, remove them from the html
			data.links = Elements.from(data.html.getTags('links').join(' '));
			data.links = data.links.filter('[rel=stylesheet]');
			data.links.concat(Elements.from(data.html.getTags('style').join(' ')));
			data.html = data.html.stripTags('links');
		},
		title: function(data) {
			//grab the title value
			data.title = this._getTitleFromHTML(data.html);
		},
		meta: function(data) {
			//grab any meta tags and remove them from the html
			data.meta = Elements.from(data.html.getTags('meta').join(' ').replace(/(<|<\/)meta/g, '$1span'));
			data.html = data.html.stripTags('meta');
		},
		elements: function(data) {
			//grab the contents of the body tag
			data.elements = Elements.from(data.html.getTags('body', true)[0] || data.html);
		}
	},

	/*
		options:
			see renderContent
	*/
	_setRequestOptions: function(request, options) {
		/*
			By default, there's only ever one request running per-jframe.
			The linkers involved all create a new instance of request every time
			they are invoked. However, Form.Request re-uses its instance. To prevent
			that request instance from being "set up" twice, exit if there's already
			a request and it's already been set up.
		*/
		if (request._jframeConfigured) return;
		request._jframeConfigured = true;
		request.setOptions($merge({
			//determine if this request should be appearent to the user
			useSpinner: this.options.spinnerCondition.apply(this, [options]),
			//where to put the spinner
			spinnerTarget: this.options.spinnerTarget || this.element,
			//any options specific to spinner
			spinnerOptions: { fxOptions: {duration: 200} },
			//when there's an exception, invoke an error handler
			onFailure: this.error.bind(this),
			//do not eval scripts in the response; in theory this should never been overridden
			evalScripts: false,
			onRequest: function(){
				/*
					Here we cancel any running request if we kick off a new one.
					The exception here is when we are re-using the running request.
					FormRequest, for instance, reuses a Request instance. So we check
					that the current request is not the one we're sending; if it is
					the one we're sending, don't cancel it; only cancel if it's a different
					one.
				*/
				if (this._request && this._request != request) this._request.cancel();
				this._request = request;
			}.bind(this),
			onSuccess: function(requestTxt){
				//if there's a method called requestChecker defined in the options, run our response through it
				//if it returns false, then throw out the response.
				if (!options.requestChecker || options.requestChecker(requestTxt, request, options)) {
					this._requestSuccessHandler(request, requestTxt, options);
				}
				//we're done with this request
				this._request = null;
			}.bind(this),
			onCcsErrorPopup: function(alert){
				//when the request shows a popup error because there's been an exception of some sort
				//attach some logic to that popup so that when the user closes the alert the app window,
				//if it's never been displayed and is still hidden, is destroyed.
				alert.addEvent('destroy', function(){
					if (!this.loadedOnce) {
						var win = this.getWindow();
						if (win) win.hide();
					}
				}.bind(this));
			}.bind(this)
		}, options));
		//whenever the request completes, destroy it's spinner
		request.addEvent('complete', function(){
			if (this.spinner) {
				this.spinner.destroy();
				this.spinner = null;
			}
		}.bind(request));
		//custom header for Hue
		request.setHeader('X-Hue-JFrame', 'true');
	},

	_checkForEmptyErrorState: function(request, html){
		return this.options.errorDetector(request, html) || false;
	},

	_requestSuccessHandler: function(request, html, options) {
		var error, blankWindowWithError, previousPath;
		previousPath = this.currentPath;
		if (this._checkForEmptyErrorState(request, html)) {
			error = true;
			if (!this.loadedOnce) blankWindowWithError = true;
		}
		var responsePath = request.getHeader('X-Hue-JFrame-Path');
		var redirected = responsePath && responsePath != this.currentPath;

		if (redirected) this.fireEvent('redirect', [this.currentPath, responsePath]);
		
		this.renderContent($merge({
			content: html,
			responsePath: responsePath || request.options.url,
			error: error,
			blankWindowWithError: blankWindowWithError
		}, options || {}));
		var flash = request.getHeader('X-Hue-Flash-Messages');
		if (flash) {
			var data = eval(flash);
			data.each(function(msg) {
				CCS.Desktop.flashMessage(msg);
			});
		}
		if (redirected) this.fireEvent('redirectAfterRender', [this.currentPath, responsePath]);
		var loadOptions = $merge({
			content: html,
			responsePath: responsePath || request.options.url,
			error: error,
			blankWindowWithError: blankWindowWithError,
			previousPath: previousPath
		}, options || {}); 
		this.behavior.fireEvent('load', loadOptions); 
	},

	/*
		given an HTML string, find the contents of the <title> tag or the first <h1>
	*/

	_getTitleFromHTML: function(html){
		var title = html.getTags('title', true);
		if (!title.length) title = html.getTags('h1', true);
		if (title.length) return title[0].stripTags();
		return '';
	},

	/*
		checks the link clicked to see if it matches the selectors in any linkers.
		returns true if any were found. This allows for custom link handling; by default
		links load their contents into the jFrame (unless their link hrefs are not on the
		same domain; in that case, they are loaded in a new tab/window).
	*/
	_checkLinkers: function(event, link){
		var linked;
		for (selector in this.linkers) {
			if (link.match(selector)) {
				linked = true;
				this.invokeLinker(selector, link, event);
			}
		}
		return linked;
	},
	
	/*
		default error handler for jframe; passes to CCS.error...
	*/
	
	error: function(message){
		//TODO(nutron) insert some sort of logging report when this happens
		this.fireEvent('loadError');
	},

	/*
		filters:
		Filters are functions that are called every time the contents of the jFrame is updated. 
		The method defined is passed the container and can then apply its own logic to the contents
		of that container. The name specified is not used, except that you can overwrite a filter
		by using the same name.
		
		example: images links with class "alert" shall allert their source url:
		
			myjFrame.addFilter('alerts', function(container){
				var alerter = function(){
					alert(img.get('alt'));
				};
				var imgs = container.getElements('img');
				imgs.addEvent('click', alerter);
				//this could be accomplished with delegation too of course; just an example
				
				//you can mark a function for execution when the jframe contents are cleaned up when new content is loaded:
				this.markForCleanup(function(){
					imgs.removeEvent('click', alerter);
				});
			});
	*/

	/*
		sweeps all marked functions.
		target - (*element*) the element to garbage collect;
	*/
	_sweep: function(target){
		this.marked.each(function(fn) {
			dbug.conditional(fn.bind(this), function(e) {
				dbug.error('sweeper failed, error: ', e);
			});
		});
		this.marked.empty();
		this.behavior.cleanup(target);
		//if there are any child widgets that were not destroyed, destroy them
		if (this._childWidgets.length) this._childWidgets.each(function(w) { w.eject(); });
	},

	/*
		_applyRenderers: renders content into the target
		content - (*object*) an object with the following props:
			options - (*object*) the object that created the request
			html - (*string*) the source html, if it was present
			js - (*string*) any the inline javascript to evalutate,
			links - (*elements array*) css links and style tags to be injected into the target
			elements - (*elements array*) elements to inject into the target (i.e. the actual content)
			meta - (*elements array*) any meta tags from the content
			title - (*string*) the title of the content
			view - (*string*; optional) if defined, the view of the content
			viewElement - (*element*; optional) if defined, the element for the view
		
		Iterates over all the renderers for this instance (including global renderers on the JFrame prototype, which
		includes the default renderer). Each renderer may inspect the content and elect to handle it instead of the 
		default handler. If it handles it and wishes to prevent the default handler, the renderer returns *true*, 
		otherwise, if it returns *false* (or nothing) the default handler will fill the contents and set up events
		and filters, linkers, etc. as usual.
	*/

	_applyRenderers: function(content){
		var rendered;
		this.fireEvent('beforeRenderer', [content, content.options]);
		//loop through all the renderers
		for (name in this._renderers) {
			var renderer = this._renderers[name];
			dbug.conditional(function(){
				rendered = renderer.call(this, content);
			}.bind(this), function(e) {
				dbug.error('renderer failed: name %s, error: ', e);
			});
			if (rendered) break;
		}
		//if no renderers returned true, then call the default one
		if (!rendered) this._defaultRenderer(content);
		this.fireEvent('afterRenderer', [content, content.options]);
	},

	/*
		renderers:
		a key/value set of renderers; see _applyRenderers above
	*/
	_renderers: {},
	
	/*
		the default renderer, if no other renderers apply
		this is the default behavior for jframe which fills the content of the window and updates 
		the history (if history is enabled). It also picks out the view if there is one defined
		as well as assigns the toolbar to the callback object for JBrowser to do with it what it will.
		Finally, it calls the callback in the options (if specified) and fires the loadComplete event.
	*/
	_defaultRenderer: function(content){
		var options = content.options;
		//store the path as the current one
		if (!options.retainPath) this.currentPath = options.responsePath || this.currentPath;
		//grab the target
		var target = options.target ? $$(options.target)[0] || this.content : this.content;
		this._resetOverflow(target);

		//if we're injecting into the main content body, cleanup and scrollto the top
		if (target == this.content && !options.noScroll) {
			this.scroller.toTop();
			this._sweep(target);
		}

		//if we're injecting into the main content body apply the view classes and remove the old one
		if (target == this.content) {
			if (this.view) this.content.removeClass(this.view.view);
			if (content.viewElement) {
				this.view = {
					view: content.view,
					element: content.viewElement,
					target: target
				};
				target.addClass(content.view);
			}
		}

		this.loadedOnce = true;
		//fill the target
		this.fill(target, content);

		//see if the content has a toolbar in it
		var toolbar = target.getElements('.toolbar');
		var footer = target.getElements('.footer');

		//define the callback data
		var data = {
			content: options.content,
			elements: content.elements,
			requestOptions: content.options,
			responsePath: options.responsePath,
			title: content.title || options.title || options.responsePath,
			userData: options.userData,
			view: content.view,
			viewElement: content.viewElement,
			target: target,
			toolbar: toolbar,
			footer: footer,
			suppressHistory: options.suppressHistory
		};

		// Let observers know
		if (!options.suppressLoadComplete) this.fireEvent('loadComplete', data);
		if (options.callback) options.callback(data);
	},

	_resetOverflow: function(target) {
		//reset the overflow style for those filters which alter the content
		//such as splitview, etc.:
		target.setStyle('overflow', '');
	}

});

/****************************************************************************************
	PUBLIC STATIC METHODS BELOW
*****************************************************************************************/

/*
	Static method: CCS.JFrame.addGlobalLinkers
	Adds a group of linkers to all instances of JFrame.
	linkers - (*object*) a key/value set of linkers
*/
CCS.JFrame.addGlobalLinkers = function(linkers) {
	CCS.JFrame.implement({
		linkers: linkers
	});
};
/*
	Static method: CCS.JFrame.addGlobalFilters
	Adds a group of filters to all instances of JFrame.
	filters - (*object*) a key/value set of filters
*/
CCS.JFrame.addGlobalFilters = function(filters) {
	CCS.JFrame.implement({
		filters: filters
	});
};

/*
	Static method: CCS.JFrame.addGlobalRenderers
	Adds a group of renderers to all instances of JFrame.
	renderers - (*object*) a key/value set of renderers
*/
CCS.JFrame.addGlobalRenderers = function(renderers) {
	CCS.JFrame.implement({
		_renderers: renderers
	});
};
