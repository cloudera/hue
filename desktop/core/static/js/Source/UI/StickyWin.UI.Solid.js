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
description: StickyWin.UI.Solid
provides: [StickyWin.UI.Solid]
requires: [clientcide/StickyWin.UI, Core/Class.Extras]
script: StickyWin.UI.Solid.js

...
*/
StickyWin.UI.Solid = new Class({

	Extends: StickyWin.UI,
	
	options: {
		width: 300,
		cssId: 'defaultSolidWinStyle',
		cssClassName: 'solid-win'
	},

	initialize: function(){

		var args = this.getArgs(arguments);
		this.setOptions(args.options);
		this.build();
		this.setContent(args.body);
	},

	build: function(){
		var opt = this.options;
		
		var container = new Element('div', {
			'class': opt.cssClassName,
			styles: {
				width: opt.width + 20
			}
		});
		this.element = container;
		this.element.store('StickyWinUI', this);

		this.body = new Element('div', {
			'class':'body',
			styles: {
				width: opt.width
			}
		});


		//body
		container.adopt(new Element('div').addClass('body-left').adopt(this.body));

		//footer
		container.adopt(
			new Element('div').addClass('bottom').adopt(
					new Element('div', {
						'class':'bottom_lr',
						styles: {
							width: opt.width
						}
					})
			)
		);
		return this;

	},

	setContent: function(content) {
		if ($(content)) this.body.empty().adopt(content);
		else this.body.set('html', content);
		return this;
	}

});
