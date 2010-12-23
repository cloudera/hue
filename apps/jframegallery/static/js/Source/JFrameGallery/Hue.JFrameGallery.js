// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.	See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.	Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.	You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/*
---
description: JFrame Gallery window
provides: [Hue.JFrameGallery]
requires: [JFrame/JFrame.Browser, hue-shared/Hue.JFrame.Chooser]
script: Hue.JFrameGallery.js

...
*/

ART.Sheet.define('window.art.jframe-gallery', {
	'footer-height': 28
});

Hue.JFrameGallery = new Class({

	Extends: Hue.JBrowser,

	options: {
		className: 'art jframe-gallery browser logo_header',
		jframeOptions: {
			clickRelays: 'a, .relays'
		}
	},

	initialize: function(path, options){
		this.parent(path || '/jframegallery/', options);

		this.addEvent('load', function(view){
			this.toolbar.adopt(
				new Element('a', {
					href: '/jframegallery/',
					'class': 'jf-logo'
				})
			);

			/* Inject demo/source button bar */
			var currentPath = this.jframe.currentPath,
			    path;

			if (currentPath.indexOf('/jframegallery/gallery') === 0) {
				/* This is the view of a demo */
				path = currentPath.replace('/jframegallery/gallery', '/jframegallery/source');
			} else if (currentPath.indexOf('/jframegallery/source') === 0) {
				/* This is the view of a demo source */
				path = currentPath.replace('/jframegallery/source', '/jframegallery/gallery');
			}

			if (path) {
				var button = new Element('a', {
					href: path,
					'class': 'jf-button',
					'data-filters': 'ArtButton',
					'text': view == "source" ? "View Demo" : "View Source"
				});
				var buttonBar = new Element('ul', {
					'class': 'jf-buttonbar',
					'data-filters': 'ArtButtonBar'
				}).adopt(new Element('li').adopt(button));
				this.footerText.adopt(buttonBar);
				this.jframe.behavior.apply(this.footerText);
			}
		}.bind(this));
	}

});
