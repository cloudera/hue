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
description: Automatically fits text to fit an element adding an elipse to the text using the FitText plugin for any elements with the .ccs-truncate class.
provides: [CCS.JFrame.FitText]
requires: [/CCS.JFrame, FitText/FitText, More/Array.Extras]
script: CCS.JFrame.FitText.js

...
*/

(function(){
	//implements the FitText filter on an element; attaches to the jframe for events on resize
	var fitIt = function(element, jframe){
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
		var win = jframe.getWindow();
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
				fitText.fit();
				element.store('FitText', fitText).set('title', text);
				if (win) {
					var fitTextFit = fitText.fit.bind(fitText);
					//rerun this after a while, as some filters muck about w/ the DOM
					//I'm not crazy about this solution, but it'll have to do for now
					fitTextFit.delay(10); 
					win.addEvent('unshade', fitTextFit);
					jframe.markForCleanup(function(){
						win.removeEvent('unshade', fitTextFit);
					});
				}
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
	

	CCS.JFrame.addGlobalFilters({

		/*
			truncates text automatically for elements with the class .ccs-truncate
			elements cannot have child elements (only text)
		*/
		truncate: function(container) {
			if (!container.get('html').contains('ccs-truncate')) return;
			var tables = container.getElements('table');
			var tds = [];
			tables.each(function(table){
				var tdsToTruncate = table.getElements('td.ccs-truncate');
				if (tdsToTruncate.length) fixTable(table);
				tdsToTruncate.each(function(td){
					fitIt(td, this);
					tds.push(td);
				}, this);
			}, this);
			
			container.getElements('.ccs-truncate').each(function(el){
				if (!tds.contains(el)) {
					//this is for partial refresh
					//we're assuming this td element, which is not in a table
					//because it would have been found in the block above,
					//is already in a table that's been fixed
					//so we just apply the td styles to it alone
					if (el.get('tag') == 'td') el.setStyles(tdStyles); 
					fitIt(el, this);
				}
			}, this);
		},

		/*
			finds all elements wth data-fit-text properties - these properties must be selectors
			for the elements to apply the FitText class to.
		*/
		truncateChildren: function(container){
			if (!container.get('html').contains('data-fit-text')) return;
			container.getElements('[data-fit-text]').each(function(fitParent){
				var selector = fitParent.get('data', 'fit-text');
				var table = fitParent.get('tag') == 'table';
				if (table) fixTable(fitParent);
				fitParent.getElements(selector).each(function(el){
					fitIt(el, this);
				}, this);
			}, this);
		}

	});

})();