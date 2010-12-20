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

		this.addEvent('load', function(){
			this.toolbar.adopt(
				new Element('a', {
					href: '/jframegallery/',
					'class': 'jf-logo'
				})
			);

			/* Inject demo/source button bar */
			var path = this.jframe.currentPath;
			var do_inject = false;
			var demopath;
			var sourcepath;

			if (path.indexOf('/jframegallery/gallery') === 0) {
				/* This is the view of a demo */
				demopath = path;
				sourcepath = path.replace('/jframegallery/gallery', '/jframegallery/source');
				do_inject = true;
			} else if (path.indexOf('/jframegallery/source') === 0) {
				/* This is the view of a demo source */
				demopath = path.replace('/jframegallery/source', '/jframegallery/gallery');
				sourcepath = path;
				do_inject = true;
			}

			if (do_inject) {
				var buttonBar = new Element('ul', {
					'class': 'jf-buttonbar',
					'data-filters': 'ArtButtonBar'
				});

				var demoLink = new Element('a', {
					href: demopath,
					'class': 'jf-button',
					'data-filters': 'ArtButton',
					'text': "View Demo"
				});

				var sourceLink = new Element('a', {
					href: sourcepath,
					'class': 'jf-button',
					'data-filters': 'ArtButton',
					'text': "View Source"
				});

				buttonBar.adopt(new Element('li').adopt(demoLink));
				buttonBar.adopt(new Element('li').adopt(sourceLink));
				this.toolbar.adopt(buttonBar);
				this.jframe.behavior.apply(this.toolbar);
			}
			sourcepath = "foo";
		}.bind(this));
	}

});
