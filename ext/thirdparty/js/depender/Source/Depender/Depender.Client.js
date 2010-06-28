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
description: A dependency loader for the MooTools library that integrates with <a
  href="http://github.com/anutron/mootools-depender/tree/">the server side Depender
  library</a>.
provides: [Depender.Client]
requires: [Core/Class.Extras, Core/Element.Event]
script: Depender.Client.js
authors: [Aaron Newton]

...
*/

var Depender = {

	options: {
		/* 
		onRequire: $empty(options),
		onRequirementLoaded: $empty([scripts, options]),
		target: null,
		builder: '/depender/build.php'
		*/
	},
	
	loadedSources: [],

	loaded: [],
	
	required: [],

	finished: [],
	
	lastLoaded: 0,

	require: function(options){
		if (!this.options.builder) return;
		this.fireEvent('require', options);

		var finish = function(script){
			this.finished.push(script);
			if (options.callback) {
				if (options.domready) window.addEvent('domready', options.callback.pass(options));
				else options.callback(options);
			}
			this.fireEvent('scriptLoaded', {
				script: this.loaded.join(', '),
				totalLoaded: (this.finished.length / this.required.length * 100).round(),
				currentLoaded: ((this.finished.length - this.lastLoaded) / (this.required.length - this.lastLoaded) * 100).round(),
				loaded: this.loaded
			});
			if (this.required.length == this.finished.length) this.lastLoaded = this.finished.length;
			this.fireEvent('requirementLoaded', [this.loaded, options]);
		}.bind(this);

		var src = [this.options.builder + '?client=true'];

		if (options.scripts) {
			var scripts = $splat(options.scripts).filter(function(script) {
				return !this.loaded.contains(script);
			}, this);
			if (scripts.length) src.push('require=' + scripts.join(','));
		}

		if (options.sources) {
			var sources = $splat(options.sources).filter(function(source){
				return !this.loadedSources.contains(source);
			}, this);
			if (sources.length) src.push('requireLibs=' + $splat(sources).join(','));
		}

		if (src.length == 1) {
			finish();
			return this;
		}

		if (this.loaded.length) {
			src.push('exclude=' + this.loaded.join(','));
		}
		var finished;
		var script = new Element('script', {
			src: src.join('&'),
			events: {
				//IE doesn't fire a load event for scripts, so we monitor the ready state
				readystatechange: function(){
					if (['loaded', 'complete'].contains(this.readyState) && !finished) {
						finished = true;
						finish(script);
					}
				},
				load: function(){
					if (!finished) {
						finished = true;
						finish(script);
					}
				}
			}
		}).inject(this.options.target || document.head);

		this.required.push(script);

		return this;

	}

};

//make it easy to switch between the server side and the client side versions of this library.
['enableLog', 'disableLog', 'include'].each(function(fn) {
	Depender[fn] = $lambda(Depender);
});

$extend(Depender, new Events);
$extend(Depender, new Options);



(function(){
	if (!Browser.Engine.trident) return;
	/*
		I am going to hell for this.
		
		Override Mootool's $ method and its Element.implement method for IE.
		
		Override $ to disable the caching elements whenever Element.implement is called.
		
		This hack exists because we load dependencies on the fly with Depender and IE does not
		expose the element prototype. Thus, if we extend an element (through $) once, and then
		subsequently implement new properties onto the Element prototype, we need to re-apply
		them to any element instances fetched with MooTools.
		
		Like I said, I'm going to hell for this.
		
	*/
	
	var impl = Element.implement;
	//keep track of the "version" that the element has been implemented
	var version = 0;
	Element.implement = function() {
		version++;
		impl.apply(Element, arguments);
	};
	var old$ = document.id;
	document.id = (function(){

		return function(el, nocash, doc){
			el = old$(el, nocash, doc);
			//if the version of this element is behind the current
			//Element implementation, re-process it
			if (el && el.$version != version
			    && el.$family
			    //mootools doesn't extend window, document, whitespace, or textnode
			    //in the same way as it does Element; we exclude them here
			    && el.$family.name != 'window'
			    && el.$family.name != 'document'
			    && el.$family.name != 'whitespace'
			    && el.$family.name != 'textnode') {
				el.$family = null;
				el = old$(el);
				el.$version = version;
			}
			return el;
		};

	})();

})();
