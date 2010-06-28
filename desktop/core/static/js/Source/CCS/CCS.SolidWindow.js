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
description: SolidWindow
provides: [CCS.SolidWindow]
requires: [ccs-shared/CCS, ccs-shared/StickyWin.UI.Solid]
script: CCS.SolidWindow.js

...
*/
CCS.SolidWindow = new Class({

	Extends: StickyWin,

	Implements: Options,

	options: {/*
		uiOptions: {}, 
		*/
		width: 200
	},

	initialize: function(options){
		this.setOptions(options);
		if (this.options.content) {
			this.options.content = new StickyWin.UI.Solid(this.options.content, $merge({
				width: this.options.width
			}, this.options.uiOptions));
			this.options.width = false;
		}
		this.parent(this.options);
	}

});
