/*
---
description: File Viewer
provides: [CCS.FileViewer]
requires: [ccs-shared/CCS.JBrowser]
script: CCS.FileViewer.js

...
*/

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
ART.Sheet.define('window.browser.fileviewer', {
	'min-width': 820 
});

ART.Sheet.define('window.browser.fileviewer splitview', {
	'fixed-width': 200,
	'right-background-color': '#ddd'
});


CCS.FileViewer = new Class({

	Extends: CCS.JBrowser,

	options: {
		className: 'art browser fileviewer logo_header',
		displayHistory: false
	},

	initialize: function(path, options){
		this.parent(path || '/filebrowser/', options);
		this.addEvents({
			load: function(){
				//Set width of input fields to width of biggest value that could be required, using totalBytes span as guide
				$(this).getElements("input[data-filter*=OverText]").setStyle('width', $(this).getElement('.totalBytes').getWidth());
				//Set events on anchors to edit and cancel changes to byte values
				$(this).getElement('.fv-editBytes').addEvent('click', function() {
					$(this).getElement('.fv-navChange').show();
					OverText.update();
					$(this).getElement('.fv-navStatus').hide();
				}.bind(this));
				$(this).getElements('.fv-cancelChangeBytes').addEvent('click', function() {
					$(this).getElement('.fv-navChange').hide();
					$(this).getElement('.fv-navStatus').show();
				}.bind(this));
				$(this).getElement('.fv-changeBytes').addEvent('click', function(e) {
					e.preventDefault();
					var form = $(this).getElement('.fv-changeBytesForm');
					form.formUpdate();
				}.bind(this));

			}
		});
		this.jframe.addShortcuts({
			'Go To Next Block': {
				keys: 'v+right',
				shortcut: 'v + right',
				handler: function(e) {
					this._simulateAnchorClick('.fv-nextBlock');
				}.bind(this),
				description: 'Navigate to the next block of content.'
			},
			'Go To Previous Block': {
				keys: 'v+left',
				shortcut: 'v + left',
				handler: function(e) {
					this._simulateAnchorClick('.fv-prevBlock');
				}.bind(this),
				description: 'Navigate to the previous block of content.'
			},
			'Go To First Block': {
				keys: 'v+up',
				shortcut: 'v + up',
				handler: function(e) {
					this._simulateAnchorClick('.fv-firstBlock');
				}.bind(this),
				description: 'Navigate to first block of content.'
			},
			'Go To Last Block': {
				keys: 'v+down',
				shortcut: 'v + down',
				handler: function(e) {
					this._simulateAnchorClick('.fv-lastBlock');
				}.bind(this),
				description: 'Navigate to last block of content.'
			}
		});
	},

	_simulateAnchorClick: function(anchorSelector) {
		var href = $(this).getElement(anchorSelector).get('href');
		if(href) this.load({requestPath: href});
	}

	

});
