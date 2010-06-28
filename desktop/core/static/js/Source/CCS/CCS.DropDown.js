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
description: DropDown
provides: [CCS.DropDown]
requires: [ccs-shared/CCS, clientcide/MenuSlider]
script: CCS.DropDown.js

...
*/
CCS.DropDown = new Class({

	Extends: MenuSlider,

	options: {
		useIframeShim: false,
		hoverGroupOptions: {
			start: ['click'],
			remain: ['mouseenter'],
			end: []
		},
		slideOut: true
	},

	initialize: function(menu, options) {
		var submenu = $($(menu).get('id') + '-menu').getElement('ul');
		submenu.show().setStyle('visibility', 'hidden');
		this.parent(menu, submenu, options);
		submenu.setStyle('visibility', 'visible');
		var hider = function(e) {
			if (e.target != this.menu && this.isVisible()) this.slideOut();
		}.bind(this);
		document.addEvent('click', hider);
	}

});
