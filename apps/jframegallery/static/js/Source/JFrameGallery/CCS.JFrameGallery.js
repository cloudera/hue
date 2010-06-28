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
description: JFrame Gallery window
provides: [CCS.JFrameGallery]
requires: [ccs-shared/CCS.JBrowser, ccs-shared/CCS.JFrame.Chooser]
script: CCS.JFrameGallery.js

...
*/

CCS.JFrameGallery = new Class({

	Extends: CCS.JBrowser,

	options: {
		className: 'art jframe-gallery browser logo_header',
		jframeOptions: {
			clickRelays: 'a, .relays'
		}
	},

	initialize: function(path, options){
		this.addEvent('load', function(){
			this.toolbar.adopt(
				new Element('a', {
					href: '/jframegallery/',
					'class': 'jf-logo'
				})
			);
		}.bind(this));
		this.parent(path || '/jframegallery/', options);
	}

});
