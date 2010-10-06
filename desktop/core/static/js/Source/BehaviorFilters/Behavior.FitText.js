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
description: Automatically sizes text to fit an element adding an elipse to the text using the FitText plugin for any elements with the FitText data-filter.
provides: [Behavior.FitText]
requires: [Widgets/Behavior, FitText/FitText]
script: Behavior.FitText.js

...
*/

(function(){
	if (Browser.Engine.trident) return; //disable this for now as it's broken IE; bug #
	/*
		implements the FitText filter on an element; attaches to Behavior for events on resize
		filter - the Behavior filter instance
		element - the element to instantiate FitText against
		methods - the Behavior methods object passed into the filter
		garbageElement - (optional) if the element passed to the filter is not the one having 
		     FitText applied, pass in the filter element for garbage collection marking
	*/
	var fitIt = function(filter, element, methods, garbageElement){
		if (element.get('tag') == 'td' || element.getParent('table')) {
			fixTable(element.getParent('table'));
			if (element.get('tag') == 'td') element.setStyles(tdStyles);
			else element.getParent('td').setStyles(tdStyles);
		}
		
		if (element.getChildren().length > 0) {
			dbug.warn('attempting to truncate an element (%o) that has child elements; this is not permitted.', element);
			return;
		}
		var text = element.get('text');
		var span = new Element('span', {
			text: text,
			styles: {
				'white-space': 'nowrap'
			}
		}).inject(element.empty());

		//because FitText requires element measurement, don't create an instance
		//until after the element is visible.
		var fitter = function(){
			if (!element.isVisible()) {
				//not ready; call again when the thread is released
				fitter.delay(1);
			} else {
				var options = {};
				var offset = element.get('data', 'fit-text-offset', true);
				if (offset != null) options.offset = offset;
				var fitText = new FitText(element, span, options);
				//detach the window resize events that FitText attaches itself
				fitText.detach();
				fitText.fit();
				element.store('FitText', fitText).set('title', text);
				var fitTextFit = fitText.fit.bind(fitText);
				//rerun this after a while, as some filters muck about w/ the DOM
				//I'm not crazy about this solution, but it'll have to do for now
				fitTextFit.delay(10); 
				methods.addEvent('show', fitTextFit);
				filter.markForCleanup(garbageElement || element, function(){
					methods.removeEvent('show', fitTextFit);
				});
			}
		};
		fitter();
	};

	var tdStyles = {
		'max-width': 200, //this number doesn't seem to matter, really
		'overflow': 'hidden'
	};

	var fixTable = function(table) {
		if (!table || table.retrieve('fittext:fixed')) return;
		table.store('fittext:fixed', true);
		table.getElements('tbody td').setStyles(tdStyles);
	};
	

	Behavior.addGlobalFilters({

		/*
			truncates text automatically for elements with the class .ccs-truncate
			elements cannot have child elements (only text)
		*/

		FitText: function(element, methods) {
			fitIt(this, element, methods);
		},

		/*
			finds all elements wth data-fit-text properties - these properties must be selectors
			for the elements to apply the FitText class to.
		*/
		'FitText-Children': function(element, methods){
			var selector = element.get('data', 'fit-text');
			element.getElements(selector).each(function(el){
				fitIt(this, el, methods, element);
			}, this);
		}

	});

	Behavior.addGlobalPlugin('HtmlTable', 'FitTextResize', function(element, methods) {
		if(element.hasClass('resizable')) {
			htmlTable = element.retrieve('HtmlTable');
			htmlTable.addEvent('columnResize', function() {
				if(element.hasDataFilter('FitText-Children')) {
					var selector = element.get('data', 'fit-text');
					element.getElements(selector).each(function(el){
						el.retrieve('FitText').fit();
					}, this);
				}
				element.getElements('[data-filters*=FitText]').each(function(el) {
					el.retrieve('FitText').fit();
				});
			});
		}
	});

})();
