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
description: File Browser
provides: [CCS.FileBrowser, CCS.FileChooser, CCS.FileSaver]
requires: [ccs-shared/CCS.JBrowser, fancyupload/FancyUpload3.Attach, More/URI, More/Fx.Reveal, Widgets/Element.Data]
script: CCS.FileBrowser.js

...
*/
ART.Sheet.define('window.filebrowser.browser', {
	'min-width': 620
});

ART.Sheet.define('window.filebrowser.alert content', {
	'padding': 20,
	'font-size': 14,
	'text-align': 'center'
}, 'css');

ART.Sheet.define('window.filechooser.browser.alert', {
	'header-height': 54,
	'min-height': 240,
	'min-width': 300
});
ART.Sheet.define('window.filechooser.browser.alert content', {
	'padding': 0
}, 'css');

ART.Sheet.define('window.filechooser.browser', {
	'header-height': 54,
	'min-height': 240,
	'min-width' : 300,
	'footer-height':30 
});

(function(){

	var filebrowser = {
	
		options: {
			//used for ART styling (see above styles)
			className: 'art filebrowser browser logo_header',
			//the prefixed path to the actions
			//this value is prepended with "/"
			//and is given the action as a suffix
			//for example: /filebrowser/view
			filesystem: 'filebrowser',
			//either 'view' or 'chooser'
			//'view' = the main browser; a standard table of files
			//'chooser' = the same, but customized for the file chooser
			view: 'view',
			//filter: either 'file', 'dir', or 'any'
			//used to enforce choices available in the chooser
			//ignored in the filebrowser
			filter: 'any',
			windowTitler: function(title) {
				return title + " :: File Browser";
			}
		},

		initialize: function(path, options) {
			this.parent(path, options);
			this.addEvent('load', this.setup.bind(this));
			this.setupHistory();
			this.addLinkers();
			this.removeOkEvents();
			this.addSaverInfo();
			this.addItemClickEvents();
			//when an alert is visible, hide the upload swiff
			//as it sometimes gets "stuck" to the mouse
			this.addEvents({
				alert: function(){
					if (this.uploader) this.uploader.uploader.box.hide();
				},
				endAlert: function(){
					if (this.uploader) this.uploader.uploader.box.show();
				}
			});
			
			this.jframe.addFilter('rename', function(container) {
				if (!container.get('html').contains('dest_path')) return;
				var src = container.getElement('input[name=src_path]');
				var dest = container.getElement('input[name=dest_path]');
				if (!src || !dest) return;
				dest.set('value', src.get('value').split('/').getLast());
				dest.select.delay(500, dest);
			});
		},

		//configures history for file browser
		setupHistory: function(){
			//I don't do anything by default
			//chooser doesn't have a history
			//browser does
		},

		//removes ok events for filechooser
		removeOkEvents: function(){
			//do nothing by default
			//filechooser manipulates ok events
		},

		//adds item click events
		addItemClickEvents: function(){
			//do nothing by default
			//filechooser adds delegated events
		},

		//adds fields for saver
		addSaverInfo: function(){
			//do nothing by default
			//filechooser will add fields
		},

		//add linkers to jFrame for filebrowser
		addLinkers: function(){
			this.jframe.addLinkers({
				'a.fb-move': function(e, link) {
					e.stop();
					var toMove = link.get('href').toURI().get('data', true).src_path.split('/').getLast();
					CCS.saveFile(this, toMove, this.getDirPath(), "Move " + toMove, function(data){
						var uri = link.get('href').toURI();
						var params = uri.get('data', true);
						this.jframe.load({
							requestPath: link.get('href').split('?')[0],
							method: 'post',
							data: {
								src_path: params.src_path,
								dest_path: data.path,
								next: params.next
							}
						});
					}.bind(this), {
						filesystem: this.options.filesystem,
						filter: 'dir'
					});
				}.bind(this)
			});
		},

		//shortcuts for dirlist; the only view we have (in theory)
		addFBShortcuts: function(){
			this.jframe.addShortcuts({
				'Open Selected': {
					keys: 'enter',
					shortcut: 'enter',
					handler: function(e){
						var table = $(this).getElement('[data-filters*=HtmlTable]');
						if (!table) return;
						hTable = table.retrieve('HtmlTable');
						var selected = hTable.selectedRows[0];
						if (!selected) return;
						CCS.JFrame.doubleClickHandler(this.jframe, e, selected);
					}.bind(this),
					description: 'Open the selected item.'
				},
			//TODO: Make Keyboard shortcuts more cognizant of the focus being on an input field
				'Remove Selected': {
					keys: 'keydown:backspace',
					shortcut: 'backspace',
					handler: function(e){
	    			if ($(e.target).match('input, textarea')) return;
						e.stop();
						var table = this.getDirList().retrieve('HtmlTable');
						//the view only allows one item to be selected at a time currently
						//but selectedRows is an array, so just always use the first one.
						if (table.selectedRows[0]) this.jframe.callClick(e, table.selectedRows[0].getElement('a.fb-default-rm'));
					}.bind(this),
					description: 'Remove the selected file/folder.'
				}
			});
		},

		makeUploader: function(dest){
			if (Browser.Plugins.Flash.build) {
				this.uploader = new CCS.FileBrowser.Uploader(dest, this.jframe, {
					//the DOM element where we're going to display our results
					list: $(this).getElement('.fb-upload-list'),
					listContainer: $(this).getElement('.fb-uploader'),
					button: $(this).getElement('.fb-upload'),
					uploaderOptions: {
						//call this url when we upload a file
						url: '/' + this.options.filesystem + '/upload_flash',
						container: this.toolbar
					}
				});
			} else {
				$(this).getElement('.fb-upload').set('target', '_blank');
			}
		},

		//when jframe loads, set up the content
		setup: function(view){
			if (!this._shortcutsAdded) {
				this.addFBShortcuts();
				this._shortcutsAdded = true;
			}
			//make the uploader
			(function(){
				//note we have a very short delay here; the DOM needs a moment to be there or else you sometimes
				//get the error "obj.CallFunction is not a function" which means that the JS can't communicate with
				//the swf file
				this.makeUploader($(this).getElement('.fb-upload').get('href').toURI().get('data').dest);
			}).delay(10, this);
		},

		//returns the file list element
		getDirList: function(){
			return $(this).getElement('.fb-file-list');
		},

		//returns the path relative to the current file system
		getDirPath: function(){
			return this.jframe.currentPath.split("?")[0].replace('/' + this.options.filesystem + '/' + this.options.view, '');
		}


	};
	
	/*
		the filebrowser class
		arguments
		* path - the base path from the file system; defaults to '/'
		* options - see options defined w/ notes above in the filebrowser object
	*/
	
	CCS.FileBrowser = new Class(
		$merge({
			Extends: CCS.JBrowser
		}, filebrowser, {
			//configures history for file browser
			setupHistory: function(){
				this.history.setOptions({
					editable: true,
					pathFilter: function(path) {
						return path.replace('/' + this.options.filesystem + '/' + this.options.view, '').split('?')[0];
					}.bind(this),
					showPath: false
				});
				this.history.addEvent('selectManual', function(path) {
					this.jframe.load({
						requestPath: '/filebrowser/view' + path
					});
				}.bind(this));
			}
		})
	);
	
	/*
		the file chooser class; not really meant to be used as a standalone
		see CCS.chooseFile below
		The exception is when an application requires the file chooser to launch;
		then there isn't a JBrowser instance already, so use the constructor
		
		arguments:
		* same as FileBrowser (path, options)
	*/
	ART.Sheet.define('window.art.browser.filechooser', {
		'content-border-bottom-color': hsb(0, 0, 60),
		'min-width': 600
	});
	
	var FileChooser = new Class(
		$merge({
			Extends: CCS.JBrowser.Confirm
		}, filebrowser, {
			options: {
				autosize: false,
				className: 'art filechooser filebrowser browser alert confirm'
			},
			removeOkEvents: function() {
				//remove the closeWin class; this selector is designed to close the window
				$(this.getOk()).removeClass('closeWin');
				//remove any click handlers
				this.getOk().removeEvents('press');
			},
			getOk: function() {
				return this.alertButtons[1];
			},
			getSelected: function(table) {
				var selectInfo = {'data': null, 'elem' : null};
				hTable = table.retrieve('HtmlTable');
				var selected = hTable.selectedRows[0];
				selectInfo.data = selected.get('data', 'filedata', true);
				if (!selected) return null;
				else selectInfo.elem = selected;
				return selectInfo;
			}
		})
	);

	
	CCS.FileChooser = new Class({
		Extends: FileChooser,
		options: {
			windowTitler: function() {
				return this.caption || "Choose a File";
			}
		},
		addFBShortcuts: function() {
			this.jframe.addShortcuts({
				'Select Highlighted': {
					keys: 'enter',
					shortcut: 'enter',
					handler: function(e){
						var table = $(this).getElement('[data-filters*=HtmlTable]');
						if (!table) return;
						var selectInfo = this.getSelected(table);
						if (selectInfo == null) return;
						var selectData = selectInfo.data;
						var selected = selectInfo.elem;
						if (selectData.type == 'dir') CCS.JFrame.doubleClickHandler(this.jframe, e, selected);
						else if (selectData.type == 'file') this.getOk().fireEvent('press');
					}.bind(this)
				},
				'Close': {
					keys: 'escape',
					shortcut: 'escape',
					handler: function(e) {
						Keyboard.stop(e);
						this.hide();
					}
				}
			});
		}

	});

	CCS.FileSaver = new Class({		 
		Extends: FileChooser,
		options: {
			windowTitler: function() {
				return this.caption || "Choose Where To Save This File";
			}.bind(this)
		},
		addSaverInfo: function() {
			var locationInput = new Element("input", {
				'type' : 'text',
				'class': 'fs-locationInput',
				'value': this.options.fileToMove || ""
			});
			var locationDiv = new Element("div", {
				'class': 'fs-location',
				'html' : 'File Name:'
			});
			locationInput.inject(locationDiv);
			locationDiv.inject($(this.footer), 'top');
			this.locationInput = locationInput;
		},
		addItemClickEvents: function(){
			$(this).addEvent('click:relay(.fb-item-row)', function(event, clicked) {
				var targetData = clicked.get('data', 'filedata', true);
				var locationInput = $(this).getElement('.fs-locationInput');
				if (targetData.type === 'file') {
					locationInput.set('value', targetData.path.split('/').getLast());
				} else if (targetData.type === 'dir') {
					locationInput.set('value', this.options.fileToMove);
				}

			}.bind(this));
		},
		addFBShortcuts: function(){
			this.jframe.addShortcuts({
			'Select Highlighted': {
				keys: 'enter',
				shortcut: 'enter',
				handler: function(e){
					if (document.activeElement != this.locationInput) { 
						var table = $(this).getElement('[data-filters*=HtmlTable]');
						if (!table) return;
						hTable = table.retrieve('HtmlTable');
						var selected = hTable.selectedRows[0];
						if (!selected) return;
						var selectData = selected.get('data', 'filedata', true);
						if (selectData.type == 'dir') CCS.JFrame.doubleClickHandler(this.jframe, e, selected);
						//Leaving this code here for when overwrite does work.
						/*else if (selectData.type == 'file') {
							locationInput.set('value', selectData.path.split('/').getLast());
							this.jframe.confirm("Warning!", "This will overwrite " + selectData.path + ".	 Are you sure you want to do this ?",	 function() {
							this.getOk().fireEvent('press');
						}.bind(this), {});
							confirmDialog.show();
						}*/
						} else {
							this.getOk().fireEvent('press');
						}
					}.bind(this),
				description: 'Select the highlighted row or folder.'
				}
			});

		}
	});

	/*
	Brings up a file chooser for a window
	arguments:
	* fsPath - the root path from the file system; defaults to '/'
	* cap - the caption of the window; defaults to "Choose a File"
	* fn - the callback to execute when the user choose a file
	* options - options passed to CCS.FileChooser
		* plus:
		* filter: (string) either 'file', 'dir', or 'any' to limit choices the user can make
	*/
	CCS.chooseFile = function(jbrowser, fsPath, cap, fn, opt){
		return jbrowser.alert(cap, '', fn || $empty, opt, function(caption, content, callback, options) {
			$extend(options || {}, {
				caption: caption || "Choose a File",
				className: 'art filechooser filebrowser browser alert',
				resizable: true
			});
			var chooser = new CCS.FileChooser("/filebrowser/view" + fsPath, options);
			chooser.jframe.addEvent('loadComplete', function() {
				this.setCaption(chooser.getDirPath() + " :: " + caption);
			}.bind(chooser));
			chooser.getOk().addEvent('press', function(){
				var selected = $(chooser).getElement('.table-tr-selected');
				var error = function(){
					var msg = "Please choose a directory.";
					if (options.filter == "file") msg = "Please choose a file.";
					chooser.alert(caption || "Choose a File", msg);
					chooser.fireEvent('badSelection', selected);
				};
				if (selected) {
					if (selected.hasClass('not-selectable')) {
						error();
						return;
					}
					callback($(chooser).getElement('.table-tr-selected').get('data', 'filedata', true));
					chooser.hide();
				} else if (options.filter == "file") {
					error();
				} else {
					callback({
						path: chooser.getDirPath(),
						type: 'dir'
					});
					chooser.hide();
				}
				
			});
			return chooser;
		});
	};
	CCS.saveFile = function(jbrowser, toMove, fsPath, cap, fn, opt){
		return jbrowser.alert(cap, '', fn || $empty, opt, function(caption, content, callback, options) {
				$extend(options || {}, {
					caption: caption || "Choose a File",
					className: 'art filechooser filebrowser browser alert',
					resizable: true,
					fileToMove: toMove
				});
				var saver = new CCS.FileSaver("/filebrowser/view" + fsPath + "?show_upload=false", options);
				saver.jframe.addEvent('loadComplete', function() {
					this.setCaption(saver.getDirPath() + " :: " + caption);
				}.bind(saver));
				var locationInput = $(saver).getElement('.fs-locationInput');
				saver.getOk().addEvent('press', function(){
				//Get selected row of filebrowser table
				var selected = $(saver).getElement('.table-tr-selected');
				var selectedPath, isDirSelected = false;
				// If there is a row selected create a selected path based on that row
				// If not create a selected path based on the current displayed directory
				if(selected) {
					var selectedData = selected.get('data', 'filedata', true);
					isDirSelected = selectedData.type == 'dir';
					selectedPath = selectedData.path;
				} else {
					selectedPath = saver.getDirPath();
				}
				var error = function(){
					var msg = "Please choose a directory.";
					if (options.filter == "file") msg = "Please choose a file.";
					saver.alert(caption || "Choose a File", msg);
					saver.fireEvent('badSelection', selected);
				};
				//if a directory is selected, move to the selected directory
				var inputPath = (isDirSelected ? selectedPath + "/" : "") + locationInput.get('value');
				var returnPath; 
				//An input path belonging with a slash is assumed to be an absolute path.
				if (inputPath[0] == '/') returnPath = inputPath;
				else returnPath = saver.getDirPath() + '/' + inputPath;
				callback({
					path: returnPath,
					type: 'dir'
				});
				saver.hide();
				});
			return saver;
		});
	};
})();

//have to hack the FancyUpload class a little because it has a hard-coded path in it
FancyUpload3.Attach.File2 = new Class({
	Extends: FancyUpload3.Attach.File,
	render: function(){
		var result = this.parent();
		this.ui.progress.element.src = "/static/js/ThirdParty/digitarald-fancyupload/assets/progress-bar/bar.gif";
		return result;
	},

	// To handle errors, we parse out the JSON response.  The stock uploader
	// uses the HTTP status and error string, which is hard to customize 
	// in Django.
	onComplete: function() {
		response_obj = JSON.decode(this.response.text, true);
		if (response_obj && response_obj.error) {
			this.response.error = response_obj.error;
		}
		this.parent.apply(this, arguments);
	}
});


CCS.FileBrowser.Uploader = new Class({

	Implements: Options,

	options: {
		//the DOM element that is hidden that contains the result list
		//listContainer: null,

		//the DOM element where we're going to display our results
		//list,

		//the button that prompts the user to select a local file
		//button: null
		uploaderOptions: {
			//call this url when we upload a file
			//url: null,
			//container: null
			path: '/static/js/ThirdParty/digitarald-fancyupload/source/Swiff.Uploader.swf',
			//this is the key for the file in the POST params
			fieldName: 'file',
			method: 'post',
			appendCookieData: true
		}
	},

	initialize: function(dest, jframe, options){
		this.dest = dest || '/';
		this.jframe = jframe;
		this.setOptions(options);
		this.makeSwf();
		this.completedFiles = 0;
	},

	makeSwf: function(){
		/**
		 * Uploader instance
		 */
		//create an instance of uploader, attach our click behavior to the "upload" button in the toolbar
		var list = $(this.options.list);
		var button = (this.options.button);
		this.uploader = new FancyUpload3.Attach(list, button, $merge({
			data: {
				//dest is the destination path (directory) for the file
				dest: this.dest
			},
			fileClass: FancyUpload3.Attach.File2,

			//when we select an invalid file, show an error
			onSelectFail: function(files) {
				files.each(function(file) {
					new Element('li', {
						'class': 'file-invalid',
						events: {
							click: function() {
								this.destroy();
							}
						}
					}).adopt(
						new Element('span', {html: file.validationErrorMessage || file.validationError})
					).inject(this.list, 'bottom');
				}, this); 
			},

			//when we succeed, highlight the element and then, after a moment, transition it out
			//of view
			onFileSuccess: function(file) {
				file.ui.element.highlight('#e6efc2');
				(function(){
					file.ui.element.nix();
				}).delay(300);
				this.completedFiles++;
			}.bind(this),

			//when the file fails to upload, display the error and a link to retry
			onFileError: function(file) {
				file.ui.cancel.set('html', 'Retry').removeEvents().addEvent('click', function() {
					file.requeue();
					return false;
				});

				new Element('span', {
					html: file.errorMessage,
					'class': 'file-error'
				}).inject(file.ui.cancel, 'after');
				this.completedFiles++;
			}.bind(this),

			onFileRequeue: function(file) {
				file.ui.element.getElement('.file-error').destroy();

				file.ui.cancel.set('html', 'Cancel').removeEvents().addEvent('click', function() {
					file.remove();
					return false;
				});

				this.start();
			},

			//when all files are complete and there are no errors,
			//hide the upload display and refresh the file browser
			onComplete: function() {
				// onComplete might get fired before onFileError does, in which case this
				// routine will hide the uploader without ever having shown the user the
				// error message. So, we manually wait until every file has reported its
				// status.
				if (this.completedFiles < this.uploader.fileList.length) {
					this.uploader.fireEvent.delay(100, this.uploader, ['onComplete']);
					return;
				}
				// Every file we tried to upload has reported either success or failure at this point.
				if (list.getElement('span.file-error')) return;
				this.hide();
				this.jframe.refresh();
			}.bind(this),

			onStop: function(){
				this.jframe.refresh();
			}.bind(this),

			//show the file upload display when we start uploading
			onBeforeStart: this.show.bind(this)

		}, this.options.uploaderOptions));
		//when we resize jframe, reposition the upload swf
		var reposition = this.uploader.reposition.bind(this.uploader);
		this.jframe.addEvent('resize', reposition);
		this.jframe.markForCleanup(function(){
			//remove this event on unload
			this.jframe.removeEvent('resize', reposition);
		}.bind(this));
		
		$(this.jframe).getElements('.fb-cancel-upload').addEvent('click', function(e) {
			//cancel upload stops the uploader and hides the display of files uploading and refreshes
			e.stop();
			if (this.uploader) this.uploader.stop();
			this.hide();
			this.jframe.refresh();
		}.bind(this));
	},

	//display the upload indicator area
	show: function(){
		var list = $(this.options.listContainer);
		var events = {
			resize: function(x, y) {
				//when we resize, reposition the mask and the upload display
				this.uploadMask.position();
				this.uploader.position();
			}.bind(this)
		};
		this.jframe.addEvents(events);
		//if there isn't an uploadMask, create one
		if (!this.uploadMask) {
			this.uploadMask = new Mask($(this.jframe), {
				hideOnClick: true,
				onHide: function() {
					//hide the uploader display
					list.hide();
					//remove the resize monitor
					this.jframe.removeEvents(events);
				}.bind(this)
			});
		}
		//show the mask
		this.uploadMask.show();
		//show the upload list
		list.show().position({ relativeTo: $(this.jframe)});
	},

	//hide the upload display and the mask
	hide: function(){
		if (this.uploadMask) this.uploadMask.hide();
	}
});
