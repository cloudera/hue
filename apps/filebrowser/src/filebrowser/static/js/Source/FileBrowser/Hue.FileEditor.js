/*
---

description: File Editor
provides: [Hue.FileEditor]
requires: [JFrame/JFrame.Browser, clientcide/PostEditor, /Hue.FileBrowser]
script: Hue.FileEditor.js

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

ART.Sheet.define('window.browser.fileeditor', {
	'min-width': 620,
	'min-height': 310
});

Hue.FileEditor = new Class({

	Extends: Hue.JBrowser,

	options: {
		className: 'art browser fileeditor logo_header',
		displayHistory: false,
		  prefix: "/filebrowser/edit",
		  filesystem: "filebrowser"
	 },

	 getDirPath: function() {
		  return this.jframe.currentPath.replace(this.options.prefix, '');
	 },

	initialize: function (path, options) {
		this.parent(path || '/filebrowser/', options);
		this.jframe.addRenderers({
			'saveAsPrompt_popup': function (content) {
				var saveAs = content.elements.filter('.saveAsPrompt_popup')[0];
				if(!saveAs) return;
				var path = this.getDirPath();
				var file = path.split('/').getLast();
				var pathNoFile = this.getDirPath().replace('/' + file, '');
				Hue.saveFile(this, file, pathNoFile, "Save As", function(data) {
					var form = saveAs.getElement("form");
					this.jframe.applyFilter('formRequest', saveAs);
					this.jframe.applyBehavior('FormRequest', form);
					var request = form.retrieve('form.request');
					saveAs.getElement('input[name=path]').set('value', data.path);
					request.send();
				}.bind(this), {
						filesystem: this.options.filesystem,
						filter: 'dir'
				});
				return true;
			}.bind(this) 
		});
		this.jframe.addEvents({
			beforeRenderer: function (content) {
				var toolbar = content.elements.filter('div.toolbar')[0];
				if (!toolbar) return;
				var buttons = toolbar.getElement('.fe-buttons');
				if (!buttons) return;
				['saveAs', 'save'].each(function(button) {
					var link = new Element("a", {
						'class': 'fe-' + button + 'Button',
						'data-filters': 'ArtButton',
						'data-icon-styles': "{'width': 16, 'height': 16}",
						'events': {
							'click': function (e) {
								e.preventDefault();
								var form = $(this.jframe).getElement(".fe-editForm");
								var request = form.retrieve('form.request');
								request.setOptions({
									extraData: {
										'save': button
									}
								});
								request.send();
							}.bind(this)
						},
						'html': button.hyphenate().replace("-", " ").capitalize()
					}).inject(buttons, 'top');
				}, this);
			}.bind(this)
		});
		this.addEvents({
			load: function(){
				$(this.jframe).setStyle('overflow', 'hidden');
			}.bind(this)
		});
		
	}
});
