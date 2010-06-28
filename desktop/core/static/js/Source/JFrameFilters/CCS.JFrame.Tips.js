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
description: Shows or hides the history component from the widget.
provides: [CCS.JFrame.Tips]
requires: [/CCS.JFrame, clientcide/Tips.Pointy]
script: CCS.JFrame.Tips.js

...
*/

CCS.JFrame.addGlobalFilters({

	tips: function(container){
		if (!container.get('html').match(/ccs\-pointy_tip/)) return;
		var points = {};
		container.getElements('.ccs-pointy_tip').each(function(el){
			var point = el.get('data', 'tip-direction', false, 12);
			points[point] = points[point] || [];
			points[point].push(el);
		}, this);
		//for each point, create a new instance of Tips.Pointy (clientcide plugin)
		$each(points, function(links, point) {
			var tips = new Tips.Pointy(links, {
				pointyTipOptions: {
					destroyOnClose: false,
					width: 250,
					point: point.toInt()
				}
			});
			//destroy the tips on cleanup
			this.markForCleanup(function(){
				tips.destroy();
			});
		}, this);
	},
	//display help tips for users
	help_tips: function(container) {
		if (!container.get('html').match(/[ccs\-help_text][ccs\-info_text]/)) return;
		//hide all the help text in the document
		var helps = container.getElements('.ccs-help_text, .ccs-info_text').hide();
		var points = {};
		//create a link for each help text we found
		helps.each(function(help) {
			var isHelp = help.hasClass('ccs-help_text');
			var link = new Element('a', {
				'class': 'ccs-inline ' + (isHelp ? 'ccs-help_link' : 'ccs-info_link'),
				'html': isHelp ? '?' : 'i'
			}).inject(help, 'after').store('tip:text', help.get('html'));
			//see where that text is supposed to have its pointer and group them by point
			var point = help.get('data', 'help-direction', false, 1);
			points[point] = points[point] || [];
			points[point].push(link);
		});
		//for each point, create a new instance of Tips.Pointy (clientcide plugin)
		$each(points, function(links, point) {
			var tips = new Tips.Pointy(links, {
				pointyTipOptions: {
					destroyOnClose: false,
					width: 250,
					point: point.toInt()
				}
			});
			//destroy the tips on cleanup
			this.markForCleanup(function(){
				tips.destroy();
			});
		}, this);
	}

});
