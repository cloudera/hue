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
description: Attaches Tips.Pointy objects to elements with PointyTip in their data-filters property and turns elements with HelpTip or InfoTip in their data-filters property into elements which show a Tips.Pointy object which contains their content, on rollover.
provides: [Behavior.Tips]
requires: [Widgets/Behavior, clientcide/Tips.Pointy]
script: Behavior.Tips.js
...
*/

(function() {

var createLink = function(element) {
	var isHelp = element.hasDataFilter('HelpTip');
	var link = new Element('a', {
		'class': element.get('class'),
		'data-filters': (isHelp ? 'HelpTip' : 'InfoTip'),
		'html': isHelp ? '?' : 'i'
	}).inject(element, 'after').store('tip:text', element.get('html'));
	//see where that text is supposed to have its pointer and group them by point
	var point = element.get('data', 'help-direction', false, 1);
	return {point: point, link: link};
};

var createTip = function(link, point) {
	var tip = new Tips.Pointy(link, {
		pointyTipOptions: {
			destroyOnClose: false,
			width: 250,
			point: point.toInt()
		}
	});
	return tip;
};

Behavior.addGlobalFilters({

	PointyTip: function(element, methods){
		var point = element.get('data', 'tip-direction', false, 12);
		var tip = createTip(element, point);
		//destroy the tips on cleanup
		this.markForCleanup(element, function(){
			tip.destroy();
		});
	},

	//display help tips for users
	HelpTip: function(element, methods) {
		var help = element.hide();
		var link = createLink(help);
		//for each point, create a new instance of Tips.Pointy (clientcide plugin)
		var tip = createTip(link.link, link.point); 
		//destroy the tips on cleanup
		this.markForCleanup(element, function(){
			tip.destroy();
		});
	},

	InfoTip: function(element, methods) {
		var info = element.hide();
		var link = createLink(info);
		var tip = createTip(link.link, link.point);
		this.markForCleanup(element, function(){
			tip.destroy();
		});
	}

});

})();
